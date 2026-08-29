# Devin Cornell's Coding Guide

This is a compilation of different strategies, styles, and architectures that Devin Cornell likes to use when writing code.


## General Design Principles

### **Core Data Models**
* **Prefer `dataclasses`** for standard, explicit data containers.
* **Use `Pydantic` selectively** only when integrating with packages that require it (e.g., FastAPI, LLM structured outputs). Every pydantic type should use attribute typing in the format Annotation[type, Field(..)] to maximize metadata included in the type. This will be used by many packages that accept pydantic types.

### **Instantiation & Validation**
* **Enforce Immutability:** Treat all encapsulated data as immutable after creation.
* **Factory-Driven Creation:** Use static factory methods (`@classmethod`) exclusively for instantiation, data transformation, and validation.
* **Internal Constructors:** The default `__init__` is strictly for internal use by the factory methods. Do not define default parameter values in the class definition; handle them inside the factories.
* **Fail Fast:** Perform all validation inside the factory methods. 

### **Architecture & Composition**
* **Layered Composition:** Build custom types compositionally. Higher-level objects should orchestrate tasks strictly by calling methods on their lower-level component objects.
* **Strong Encapsulation:** Treat transformations between data types as a distinct pipeline, handled almost entirely by the factory methods to keep logic isolated.
* **Exception Bubbling:** Heavily utilize custom exceptions to provide detailed failure context. Raise these exceptions at the lowest levels and catch them in higher-level orchestration functions to alter flow.

### **Serialization**
* **Standardized Interfaces:** Use pydantic methods for converting types to/from dictionaries.


## Styles and Conventions

### Type Hinting & Static Analysis

* **Strict Typing:** Rely heavily on comprehensive type hints to empower static analysis tools (like MyPy or Pyright) and prevent runtime errors. Raw dictionaries should almost never be used.
* **Modern Syntax:** Exclusively use modern Python typing standards, such as the `|` operator for unions (instead of `Union`) and `typing.Self` for methods returning the object's own type.

### Naming Conventions

* **Classes:** Use `PascalCase` for all class definitions and custom type aliases.
* **Methods & Functions:** Use `snake_case` for all functions, methods, and variables.

### Semantic Method Prefixes

Use strict, predictable prefixes for your I/O and factory methods to immediately signal their behavior:

* **`from_*`**: For materialization from structured in-memory input (e.g., `from_dict`, `from_json`).
* **`read_*`**: For ingress directly from the filesystem or external storage (e.g., `read_csv`, `read_config`).
* **`to_*`**: For serialization into structured, in-memory formats (e.g., `to_dict`).
* **`write_*`**: For egress directly to the filesystem or external storage (e.g., `write_file`).

### Type Hints
I use type hints in every function and class signature. Basically, anywhere it is possible to use a type hint, I use it. When making generic collections, I use generics.

For Python 3.12+

    class Box[T]:
        def __init__(self, content: T):
            self.content = content

        def get_content(self) -> T:
            return self.content

    int_box = Box(10)      # Inferred as Box[int]
    str_box = Box("Hello") # Inferred as Box[str]


And for Python < 3.12:

    from typing import TypeVar, Generic

    T = TypeVar("T")

    class Box(Generic[T]):
        def __init__(self, content: T):
            self.content = content

I often use type hints for task-specific strings. For example, let's say I have a string that is actually an identifier to some resources. I would probbaly use type aliases like `SpecialID = str` for simplicity, but in some cases I might use `SpecialID = typing.NewType("SpecialID", str)`.

I tend to use the "|" operator to specify unions, e.g., `Path | str` instead of `typing.Union[Path,str]`.

I heavily use `typing.Self`, and I really, really don't like to surround type hints with quotes - it provides more flexibility, but in general I should not have those errors if my code is well-written.

### Imports

Rather than importing types or functions, I prefer to import entire packages. E.g., instead of using `from fastapi import FastAPI` and using `FastAPI()` within the code, I prefer to use `import fastapi` and then use `fastapi.FastAPI()` from within the code. Ignore this for relative imports obviously.

## Tools for the Job

+ Tabular Data
    + When possible, I prefer to use lists/dicts of dataclasses or `pydantic` types.
    + When dataframes really are the right solution, use Polars instead of Pandas.
+ Paths
    + Use `pathlib` for every application involving tasks that it can actually solve.
    + `Path.rglob` and `Path.glob` are much better than using `os.walk`.
    + `Path.open` is much better than using `open`.
+ Web Sites/APIs
    + Use `fastapi` for all web applications.
    + If a graphical interface is needed, write the API interface and then write an html UI that actually calls the endpoints.
    + Be sure to use pydantic-settings with the fastapi app.
    + Use dependency injection over middleware when possible.
    + Use FastMCP for adding MCP servers to the API.
    + Custom types should be used for both response and request objects. Ideally some of those types could come from other application logic.
+ Environment Management
    + Use `pydantic-settings` for environment management.
+ LLMs or Agents
    + Use `pydantic-ai` to make AI-powered tools.
    + when advanced Google-specific tools (such as Web Search) are needed, use the `python.genai` package.
+ SQL Databases
    + Use `sqlalchemy` Core patterns (ideally not ORM).
+ NoSQL Databases
    + Use `pymongo` with MongoDB, avoid Beanie and similar tools.
    + Ideally use custom types to represent documents.


