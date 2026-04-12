# Working with SQL Databases

I use SQLAlchemy Core for nearly all SQL work: no ORM models and no raw SQL strings.  
This gives me three benefits:

1. Portability across SQLite and PostgreSQL.
2. Strongly typed, composable query construction.
3. Easy local testing with an in-memory SQLite database.

My preferred structure is to keep all database behavior inside one database manager type. That type owns the engine, metadata, table definitions, and all transaction/query methods. I treat it as the single boundary between application code and SQL.

Core Design Pattern

1. One schema container defines all tables, constraints, and indexes.
2. One database manager owns the engine and executes all queries.
3. Public methods express use cases.
4. Private helpers contain reusable query fragments.
5. Query results are converted into explicit row types (dataclasses), never returned as raw rows.

Why this works well:
- Schema is centralized and explicit.
- Transaction boundaries are easy to reason about.
- Return types are stable and self-documenting.
- Switching backends usually requires only connection/config changes.

Example: Split Schema Definition from DB Operations

    @dataclasses.dataclass
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
                    sqlalchemy.Column("created_at", UTCDateTime, nullable=False),
                ),
                warehouses=sqlalchemy.Table(
                    "warehouses",
                    metadata,
                    sqlalchemy.Column("warehouse_id", sqlalchemy.String, primary_key=True),
                    sqlalchemy.Column("city", sqlalchemy.String, nullable=False),
                    sqlalchemy.Column("created_at", UTCDateTime, nullable=False),
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

            
This is a good pattern for complex schemas: keep table declarations in one place, then inject them into the DB manager.

Example: Single DB Manager Type

    @dataclasses.dataclass
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
                metadata.create_all(bind=engine, tables=tabs.all(), checkfirst=True)
            else:
                inspector = sqlalchemy.inspect(engine)
                ...
    
            return cls(engine=engine, metadata=metadata, tabs=tabs)

Two especially good choices here:
- The create_if_not_exists flag makes setup explicit and safe.
- Validation mode prevents accidental operation against incomplete schemas.

Query/Transaction Conventions

I use:
- engine.connect() for read-only operations.
- engine.begin() for operations that mutate state.
- SQLAlchemy Core select/insert/update/delete expressions only.

I also like naming methods by behavior:
- get_* for reads.
- add_* or create_* for inserts.
- set_* for replace semantics.
- remove_* for deletes.
- enable_*/disable_* for state toggles.

Typed Row Objects

I convert rows into explicit dataclasses:

    @dataclasses.dataclass
    class ProductStock:
        product_id: str
        warehouse_id: str
        quantity: int
        updated_at: datetime.datetime
    
        @classmethod
        def from_row(cls, row: sqlalchemy.engine.Row) -> typing.Self:
            return cls(
                product_id=row._mapping["product_id"],
                warehouse_id=row._mapping["warehouse_id"],
                quantity=row._mapping["quantity"],
                updated_at=row._mapping["updated_at"],
            )
            
This keeps service code clean and avoids leaking database-row details outside the DB layer.

Error Handling Approach

I raise domain-specific exceptions instead of raw SQLAlchemy exceptions.  

Example categories:
- ProductDoesNotExistError
- WarehouseAlreadyExistsError
- StockLevelMissingError

This gives callers stable, business-level error semantics independent of backend details.

Ultimately, this pattern provides the best of both worlds: the explicitness of SQLAlchemy Core without the heavy coupling of an ORM. By encapsulating the engine, schema, and queries inside a single manager class—and strictly returning typed dataclasses and domain-specific exceptions—your application code remains clean, highly testable, and completely agnostic to the underlying database backend.
