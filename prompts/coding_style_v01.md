

## Architectural Design

Typically I create dataclasses or pydantic types for explicit data containers, and dataclasses are preferred one. I almost exclusively use static factory methods (classmethods), aka "factory class methods" or "“"alternative/non-default constructors", to initialize these classes - the default constructor __init__ is only called from within these functions, so the dataclasses or pydantic type definitions almost never have default parameter values (defaults can be put in the static factory methods). I prefer transformations between types to happen inside the factory methods and otherwise for the encapsulated data to be treated as immutable when possible. My classes typically have serialization format methods `to_dict()` and `from_dict()` that allow them to be stored in files or databases.

My individual custom types are typically organized compositionally, where one type has an attribute containing another custom type (or collection thereof). A natural consequence is that the serialization methods are chained together - that is, the `to_json()` method of a parent class will use the `to_json()` of the child class to serialize it. Because of that, any types following that implicit protocol can be swapped out without affecting the serialization pattern.

The compositional structuring of these types typically follows a layering pattern, where methods on higher level objects often call methods of lower-level objects to accomplish tasks - a strong encapsulation philosophy is preferred even when creating hierarchical structures and considering transformations between data types. Custom Exception types used heavily and often raised in lower-level objects and caught in higher level functions to alter behavior.

If you look at the flow of data through the applications, it can often be described as a data pipeline with sequences of transformations from one custom type to another. Most of the transformation logic exists in the static factory methods, and after construction the types should typically be treated as immutable. Any validation logic should also happen at these stages as well - it is important to fail fast, and custom exceptions are a great way to provide detailed information to the user about what went wrong.

## Styles and Conventions
Also pay attention to the style and naming conventions I use here. I generally rely on these conventions:

I rely heavily on good type hints for static analysis.
I generally use modern syntax for type hints: “|” for unions, “typing.Self” to refer to the object itself.
I use pretty standard naming conventions.
PascalCase for class names.
snake_case for method and function names.
Constructor-like classmethods use semantic prefixes: `from_*` for materialization from structured input; `read_*` for file ingress; `to_*` / `write_*` for egress.

## Packages and Technologies

Take special note of which packages were used for different applications. What are the packages and how are they used within the larger architecture?

#### Imports

Rather than importing types or functions, I prefer to import entire packages. E.g., instead of using `from fastapi import FastAPI` and using `FastAPI()` within the code, I prefer to use `import fastapi` and then use `fastapi.FastAPI()` from within the code. Ignore this for relative imports obviously.


#### Custom Types

I typically prefer to use either dataclasses or pydantic for type definitions. `dataclasses` are preferred except when I'm working with packages that work particularly well with `pydantic.BaseModel`, such as `fastapi` input/output types, structured output definitions in `pydantic-ai`, or other such situations.


#### Paths

I heavily use `pathlib` to work with file paths and even to perform basic file operations. In particular, `Path.rglob` and `Path.glob` are much better than using `os.walk`, and `Path.open` is much better than using `open`.

When creating functions that accept paths as arguments, I always use parameters that accept `Path|str` values and then convert them to `Path` types internally before working with them. This takes away some ambiguity about where the conversion to `Path` types happens.

#### SQL Databases

I prefer to use `sqlalchemy` "core" compoonents for almost all my work with SQL databases - no ORM, but also no raw SQL. This way, I can use an in-memory sqlite db and then in production I can use either SQLite or PostgreSQL.

My typical approach for working with SQL databases is to create a single type that maintains the sqlalchemy engine instance (along with the connection pool) and handles all SQL transactions and database operations via the sqlalchemy interface.

+ The database type encapsulates all database operations: creating and defining tables and indexes as well as any query transaction logic.
+ The type maintains engine and metadata instances for the table so that queries can be executed through the type's methods.
When retrieving rows or aggregations from the database, I like the mthods to return custom types used to encapsulate the rows. If selecting only a subset of columns or creating aggregations, separate custom types should be defined to be very explicit about what is returned.
+ 

```
@dataclasses.dataclass
class MyDB:
    metadata: sqlalchemy.MetaData
    engine: sqlalchemy.Engine
    table1: sqlalchemy.Table
    table2: sqlalchemy.Table

    @classmethod
    def from_connection_string(cls, connection_string: str, create_if_not_exists: bool = False) -> MyDB:
        engine = sqlalchemy.create_engine(connection_string)
        metadata = sqlalchemy.MetaData()
        
        ...

        return cls(metadata=metadata, engine=engine, table1=table1, table2=table2)



```


That single type keeps the 

. I also like to define the actual SQL tables inside a method of that class so that it can be used to create the database from the static factory method when required (usually exposed as a flag). If the database schema is particularly complicated, it sometimes makes sense to have a separate type instance where I define and expose the SQL tables, then sqlalchemy core transactions can use that as an attribute of the original type (obviously, the database type would maintain a reference to that instance). The naming of that type should be clear: call it `SomethingDB`, and methods of the database-encapsulating type should roughly follow the conventions of the underlying transaction interface: `select_*` for select queries, and so on.



#### MongoDB Databases

MongoDB: I prefer to use raw pymongo without other layers such as Beanie. I define types to represent each document, and manually create serialization methods to read/write objects to the database.


#### Tabular Data

Tabular data: I prefer polars over pandas, although sometimes I use pandas. Moving forward, I would strongly prefer to use polars. Typically I avoid dataframes in favor of using polars.Series types which are assigned to attributes of a custom class.

#### Vectors and Matrices

Vectors and Matrices: I prefer numpy for this unless it requires something more like polars.

#### Web APIs

Web APIs: I mostly use API-first designs, so fastapi is my go-to framework for creating websites. Sometimes I even manually write the API interface and completely vibe-code the UI as an html template. I use the fastapi endpoints to create a definitions for the request and then can explain to the vibe-coding LLM how exactly to write the UI (but I don’t know any front-end frameworks).




