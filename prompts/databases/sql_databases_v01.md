# Working with SQL Databases

I use SQLAlchemy Core for nearly all SQL work: no ORM models and no raw SQL strings.

This gives me three benefits:

1. Portability across SQLite and PostgreSQL.
2. Strongly typed, composable query construction.
3. Easy local testing with an in-memory SQLite database.

My preferred structure is to keep all database behavior inside one database manager type. That type owns the engine, metadata, table definitions, and all transaction/query methods. I treat it as the single boundary between application code and SQL.

### Core Design Pattern

1. **One schema container** defines all tables, constraints, and indexes.
2. **One database manager** owns the engine and executes all queries.
3. **Public methods** express use cases using strict semantic I/O prefixes.
4. **Private helpers** contain reusable query fragments.
5. **Query results** are strictly converted into immutable Pydantic models, never returned as raw rows.

*Note on Infrastructure vs. Data:* While we strictly use Pydantic `BaseModel` for data flowing through the application (like database rows), infrastructure managers that hold stateful runtime connections (like `sqlalchemy.Engine`) should use standard classes or `@dataclasses.dataclass(frozen=True)`. Pydantic is for data validation, not runtime infrastructure.

### Example: Split Schema Definition from DB Operations

This is a good pattern for complex schemas: keep table declarations in one place, then inject them into the DB manager. We use a standard frozen dataclass here because this object manages infrastructure metadata, not application data.

```python
import dataclasses
import typing
import sqlalchemy

@dataclasses.dataclass(frozen=True)
class InventoryDBTables:
    metadata: sqlalchemy.MetaData
    products: sqlalchemy.Table
    warehouses: sqlalchemy.Table
    stock_levels: sqlalchemy.Table

    @classmethod
    def from_metadata(cls, metadata: sqlalchemy.MetaData) -> typing.Self:
        return cls(
            metadata=metadata,
            products=sqlalchemy.Table(
                "products",
                metadata,
                sqlalchemy.Column("product_id", sqlalchemy.String, primary_key=True),
                sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
                sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True), nullable=False),
            ),
            warehouses=sqlalchemy.Table(
                "warehouses",
                metadata,
                sqlalchemy.Column("warehouse_id", sqlalchemy.String, primary_key=True),
                sqlalchemy.Column("city", sqlalchemy.String, nullable=False),
                sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True), nullable=False),
            ),
            stock_levels=sqlalchemy.Table(
                "stock_levels",
                metadata,
                sqlalchemy.Column("product_id", sqlalchemy.String, nullable=False),
                sqlalchemy.Column("warehouse_id", sqlalchemy.String, nullable=False),
                sqlalchemy.Column("quantity", sqlalchemy.Integer, nullable=False),
                sqlalchemy.UniqueConstraint("product_id", "warehouse_id"),
            ),
        )

```

### Example: Single DB Manager Type

The manager itself is also a frozen dataclass holding the connection state.

```python
import dataclasses
import typing
import sqlalchemy

@dataclasses.dataclass(frozen=True)
class InventoryDB:
    engine: sqlalchemy.Engine
    metadata: sqlalchemy.MetaData
    tabs: InventoryDBTables

    @classmethod
    def from_connection_string(
        cls,
        db_connect_string: str,
        create_if_not_exists: bool = False,
    ) -> typing.Self:
        engine = sqlalchemy.create_engine(db_connect_string)
        metadata = sqlalchemy.MetaData()
        tabs = InventoryDBTables.from_metadata(metadata)

        if create_if_not_exists:
            metadata.create_all(bind=engine, tables=tabs.metadata.tables.values(), checkfirst=True)
        else:
            inspector = sqlalchemy.inspect(engine)
            # Validation logic here...

        return cls(engine=engine, metadata=metadata, tabs=tabs)

```

Two especially good choices here:

* The `create_if_not_exists` flag makes setup explicit and safe.
* Validation mode prevents accidental operation against incomplete schemas.

### Query/Transaction Conventions

I use:

* `engine.connect()` for read-only operations.
* `engine.begin()` for operations that mutate state.
* SQLAlchemy Core select/insert/update/delete expressions only.

**Semantic Method Prefixes:**
Because the database is external storage, method names must strictly align with our external I/O prefix conventions:

* **`read_*`**: For fetching data (e.g., `read_product`, `read_stock_levels`).
* **`write_*`**: For inserting, updating, or replacing data (e.g., `write_new_product`, `write_stock_adjustment`).
* **`delete_*`**: For removing records (e.g., `delete_warehouse`).

### Typed Row Objects

I strictly convert all returned rows into immutable Pydantic models. This keeps service code clean and ensures data validation happens at the absolute boundary of the application, avoiding leaked database-row details.

```python
import datetime
import typing
from typing import Annotated
import sqlalchemy
from pydantic import BaseModel, ConfigDict, Field

class ProductStock(BaseModel):
    # Enforce strict immutability per architectural guidelines
    model_config = ConfigDict(frozen=True)

    product_id: Annotated[str, Field(description="Unique identifier for the product")]
    warehouse_id: Annotated[str, Field(description="Unique identifier for the warehouse")]
    quantity: Annotated[int, Field(description="Current physical stock count")]
    updated_at: Annotated[datetime.datetime, Field(description="Timestamp of last adjustment")]

    @classmethod
    def from_row(cls, row: sqlalchemy.Row) -> typing.Self:
        """Transforms the upstream SQL row into this downstream immutable type."""
        # Pydantic natively handles the dict unpacking and type coercion
        return cls(**row._mapping)

```

### Error Handling Approach

I raise domain-specific exceptions instead of raw SQLAlchemy exceptions, catching backend errors at the lowest level inside the database manager and bubbling up custom errors.

Example categories:

* `ProductDoesNotExistError`
* `WarehouseAlreadyExistsError`
* `StockLevelMissingError`

This gives callers stable, business-level error semantics independent of backend details and perfectly aligns with the fail-fast custom exception architecture.