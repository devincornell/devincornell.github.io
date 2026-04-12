

## Architectural Design

### **Core Data Models**
* **Prefer `dataclasses`** for standard, explicit data containers.
* **Use `Pydantic` selectively** only when integrating with packages that require it (e.g., FastAPI, LLM structured outputs).

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
* **Standardized Interfaces:** Implement uniform `to_dict()` and `from_dict()` methods for database storage and file I/O.
* **Chained Serialization:** Rely on structural subtyping (duck typing). Parent classes serialize themselves by calling the `to_dict()` methods of their component children, allowing any conforming type to be safely swapped into the hierarchy.


## Styles and Conventions

### **Type Hinting & Static Analysis**
* **Strict Typing:** Rely heavily on comprehensive type hints to empower static analysis tools (like MyPy or Pyright) and prevent runtime errors.
* **Modern Syntax:** Exclusively use modern Python typing standards, such as the `|` operator for unions (instead of `Union`) and `typing.Self` for methods returning the object's own type.

### **Naming Conventions**
* **Classes:** Use `PascalCase` for all class definitions and custom type aliases.
* **Methods & Functions:** Use `snake_case` for all functions, methods, and variables.

### **Semantic Method Prefixes**
Use strict, predictable prefixes for your I/O and factory methods to immediately signal their behavior:
* **`from_*`**: For materialization from structured in-memory input (e.g., `from_dict`, `from_json`).
* **`read_*`**: For ingress directly from the filesystem or external storage (e.g., `read_csv`, `read_config`).
* **`to_*`**: For serialization into structured, in-memory formats (e.g., `to_dict`).
* **`write_*`**: For egress directly to the filesystem or external storage (e.g., `write_file`).
#### Type Hints
I use type hints in every function and class signature. Basically, anywhere it is possible to use a type hint, I use it. When making generic collections, I use generics.

For Python 3.12+


    class Box[T]:
        def __init__(self, content: T):
            self.content = content

        def get_content(self) -> T:
            return self.content

    int_box = Box(10)      # Inferred as Box[int]
    str_box = Box("Hello") # Inferred as Box[str]


And for Python < 3.12>

    from typing import TypeVar, Generic

    T = TypeVar("T")

    class Box(Generic[T]):
        def __init__(self, content: T):
            self.content = content

I often use type hints for task-specific strings. For example, let's say I have a string that is actually an identifier to some resources. I would probbaly use type aliases like `SpecialID = str` for simplicity, but in some cases I might use `SpecialID = typing.NewType("SpecialID", str)`.

I tend to use the "|" operator to specify unions, e.g., `Path | str` instead of `typing.Union[Path,str]`.

I heavily use `typing.Self`, and I really, really don't like to surround type hints with quotes - it provides more flexibility, but in general I should not have those errors if my code is well-written.

#### Imports

Rather than importing types or functions, I prefer to import entire packages. E.g., instead of using `from fastapi import FastAPI` and using `FastAPI()` within the code, I prefer to use `import fastapi` and then use `fastapi.FastAPI()` from within the code. Ignore this for relative imports obviously.

#### Paths

I heavily use `pathlib` to work with file paths and even to perform basic file operations. For instance, `Path.rglob` and `Path.glob` are much better than using `os.walk`, and `Path.open` is much better than using `open`.

When creating functions that accept paths as arguments, I always use parameters that accept `Path|str` values and then convert them to `Path` types internally before working with them. This takes away some ambiguity about where the conversion to `Path` types happens.






#### Tabular Data

Tabular data: I prefer polars over pandas, although sometimes I use pandas. Moving forward, I would strongly prefer to use polars. Typically I avoid dataframes in favor of using polars.Series types which are assigned to attributes of a custom class.



#### Web APIs

Web APIs: I mostly use API-first designs, so fastapi is my go-to framework for creating websites. Sometimes I even manually write the API interface and completely vibe-code the UI as an html template. I use the fastapi endpoints to create a definitions for the request and then can explain to the vibe-coding LLM how exactly to write the UI (but I don’t know any front-end frameworks).




