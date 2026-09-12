# Devin Cornell's Coding Guide

This is a compilation of different strategies, styles, and architectures that Devin Cornell likes to use when writing code.




## Styles and Conventions

### Docstrings and Annotations

* **Docstrings:** Use docstrings extensively. Every class, property, function, and method should have a docstring describing what it does. Add parameter descriptions to the docstrings only when requested explicitly.
* **Attribute Annotations:** All pydantic type attributes should use annotations like `Annotated[type, Field(description='..', ...)]` with good descriptions for both readability and so they can be used by the many packages that accept pydantic types.


### Extensive Type Hints

* **Strict Typing:** Rely heavily on comprehensive type hints to empower static analysis tools (like MyPy or Pyright) and prevent runtime errors.
* **Data Structures** Raw dictionaries should almost never be used to represent complex data structures - you might as well use defined pydantic types with composition.
* **Modern Syntax:** Exclusively use modern Python typing standards, such as the `|` operator for unions (instead of `Union`) and `typing.Self` for methods returning the object's own type.
* **Use Generics for Functions and Classes:** when applicable, use generics for both classes and functions. For Python 3.12 use `MyClass[T]` syntax and for earlier versions you can use `T = TypeVar("T")` and `MyClass(Generic[T])`.
* **Semantic Typing:** use semantic typing of some kind. The default strategy should be to use type aliases, e.g., `UserId = int` (or `type UserId = int` for Python 3.12+). If it is deemed to be far better, use nominal subtyping with `NewType` like `UserId = typing.NewType("UserId", int)`.
* **Self-referencing Hints:** When applicable, use `typing.Self` with `from __future__ import annotations` (or `from typing_extensions import Self` for Python < 3.11)
* **Attribute Annotations:** All pydantic type attributes should use annotations like `Annotated[type, Field(description='..', ...)]` with good descriptions for both readability and so they can be used by the many packages that accept pydantic types.


### Naming Conventions

* **Classes:** Use `PascalCase` for all class definitions and custom type aliases.
* **Methods & Functions:** Use `snake_case` for all functions, methods, and variables.

Use strict, predictable prefixes for your I/O and factory methods to immediately signal their behavior:

* **`from_*`**: For materialization from structured in-memory input (e.g., `from_dict`, `from_json`).
* **`read_*`**: For ingress directly from the filesystem or external storage (e.g., `read_csv`, `read_config`).
* **`to_*`**: For serialization into structured, in-memory formats (e.g., `to_dict`).
* **`write_*`**: For egress directly to the filesystem or external storage (e.g., `write_file`).


### Imports

For capitalized classes and types, it is standard and acceptable to use `from x import y` (e.g., `from fastapi import FastAPI`). Reserve `import x` for modules with overlapping function names to prevent namespace collisions. Ignore this for relative imports obviously.


## Tools for the Job

+ Tabular Data
    + When possible, I prefer to use lists/dicts of dataclasses or `pydantic` types over dataframes.
    + When dataframes really are the right solution, use Polars instead of Pandas.
+ Paths
    + Use `pathlib` for every application involving tasks that it can actually solve.
    + `Path.rglob` and `Path.glob` are much better than using `os.walk`.
    + `Path.open` is much better than using `open`.
+ Web Sites/APIs
    + Use `fastapi` for all web applications.
    + If a graphical interface is needed, write the API interface and then write an html UI that actually calls the endpoints asynchronously.
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




## Architectural Guidelines

This document outlines the standard patterns for defining, instantiating, and transforming data in our applications. The architectures rely on explicit data containers, strong encapsulation, strict immutability, and data pipelines constructed via sequential type transformations.

Here are some general principles to start with.

#### **Core Data Models**
* **Default to `pydantic`:** For all data structures, use `pydantic.BaseModel`. Pydantic provides robust typing, built-in validation, and excellent integration with external boundaries (e.g., FastAPI request/response payloads, or structured outputs for generative AI packages).
* **Attribute Annotation:** Every pydantic type should use attribute typing in the format `Annotated[type, Field(...)]` to maximize metadata included in the type. This will be used by many packages that accept pydantic types.

#### **Instantiation & Validation**
* **Enforce Immutability:** Treat all encapsulated data as immutable after creation.
* **Factory-Driven Creation:** Use static factory methods (`@classmethod`) exclusively for instantiation, data transformation, and validation.
* **Internal Constructors:** Do not override or write custom `__init__` methods. Embrace the automated validation and initialization that happens under the hood during instantiation. Do not define default parameter values in the class definition; handle them inside the factories.
* **Fail Fast:** Perform all validation inside the factory methods. 

#### **Architecture & Composition**
* **Layered Composition:** Build custom types compositionally. Higher-level objects should orchestrate tasks strictly by calling methods on their lower-level component objects.
* **Strong Encapsulation:** Treat transformations between data types as a distinct pipeline, handled almost entirely by the factory methods to keep logic isolated.
* **Exception Bubbling:** Heavily utilize custom exceptions to provide detailed failure context. Raise these exceptions at the lowest levels and catch them in higher-level orchestration functions to alter flow.

#### **Serialization**
* **Standardized Interfaces:** Use pydantic methods for converting types to/from dictionaries.



### 1. Explicit Data Containers

We rely on strongly typed, explicit data containers to pass information through the application.

* **Default to `pydantic`:** For all data structures, use `pydantic.BaseModel`. Pydantic provides robust typing, built-in validation, and excellent integration with external boundaries (e.g., FastAPI request/response payloads, or structured outputs for generative AI packages).
* **Attribute Annotation:** All fields should be annotated using the `Annotated[type, Field(...)]` pattern to allow for explicit field-level configuration, metadata, and constraints.
* **Immutability:** Once instantiated, the encapsulated data within these containers should be treated as strictly immutable. Any modification of data should result in the generation of a *new* object, rather than mutating an existing one in place.

### 2. Enforcing Strict Immutability

To natively enforce immutability in Pydantic v2, assign a `ConfigDict` with `frozen=True` to the `model_config` attribute of your models.

This configuration prevents any attribute reassignment after instantiation, raising a `ValidationError` if mutation is attempted. It also makes your models hashable, allowing them to be used safely in Python `set`s or as `dict` keys.

#### The Single Model Approach
You can apply this directly to individual models:

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

class Point(BaseModel):
    '''A single point in Cartesian space'''
    # Enforces strict immutability for this model
    model_config = ConfigDict(frozen=True)

    x: Annotated[float, Field(description="The x-coordinate")]
    y: Annotated[float, Field(description="The y-coordinate")]
```

#### The Architectural Base Class Approach
For multi-use architectural guidelines, the cleanest pattern is to define a custom base class that inherits from `BaseModel` and sets the frozen configuration. All domain models then inherit from this custom base class, guaranteeing uniform immutability across the entire data pipeline. Use this sparingly, as it increases complexity of the code.

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

class ImmutableBaseModel(BaseModel):
    """Base model that enforces immutability across the application."""
    model_config = ConfigDict(frozen=True)

class Point(ImmutableBaseModel):
    '''A single point in Cartesian space'''
    x: Annotated[float, Field(description="The x-coordinate")]
    y: Annotated[float, Field(description="The y-coordinate")]

class LineSegment(ImmutableBaseModel):
    '''A line segment specified by two points in Cartesian space.'''
    start: Annotated[Point, Field(description="Starting point for the line.")]
    end: Annotated[Point, Field(description="Ending point for the line.")]
```

#### Handling "Mutations" (Generating New Objects)
Because the architectural guidelines dictate that "Any modification of data should result in the generation of a *new* object," you can pair `frozen=True` with Pydantic's built-in `model_copy(update=...)` method. This allows you to easily generate a new immutable instance with specific fields altered, without touching the original object.

```python
p1 = Point(x=1.0, y=2.0)

# Attempting to mutate in place will fail fast:
# p1.x = 5.0  --> Raises pydantic.ValidationError

# Correct approach: Generate a new object with the updated value
p2 = p1.model_copy(update={"x": 5.0})

print(p1) # Point(x=1.0, y=2.0) -> Unchanged
print(p2) # Point(x=5.0, y=2.0) -> New object
```

### 3. Strict Instantiation via Static Factory Methods

Do not override or write custom `__init__` methods. The default constructor generated by `BaseModel` should be used, embracing the automated validation and type coercion it provides under the hood. It should **never** contain default parameters or custom logic defined by you.

Instead, all instantiation logic, default parameter injection, and data coercion must happen within **static factory methods** (using the `@classmethod` decorator).

```python
import typing
from typing import Annotated
from pydantic import BaseModel, Field

class Point(BaseModel):
    # No default values here.
    x: Annotated[float, Field(description="The x-coordinate")]
    y: Annotated[float, Field(description="The y-coordinate")]

    # __init__ is generated automatically by BaseModel and is kept strictly for assignment.

    @classmethod
    def from_coordinates(cls, x: float = 0.0, y: float = 0.0) -> typing.Self:
        # Defaults and any setup logic live in the factory method.
        return cls(x=float(x), y=float(y))

```

### 4. Fail-Fast Validation and Custom Exceptions

Validation must happen at the moment of instantiation within the factory methods rather than within pydantic validators. If data is invalid, the application should fail fast.

We heavily utilize **Custom Exceptions** to provide exact details about what went wrong at the lowest possible level. Higher-level orchestration functions are then responsible for catching these custom exceptions and altering application behavior or surfacing the error to the user.

```python
import typing
from typing import Annotated
from pydantic import BaseModel, Field

class InvalidCoordinateError(ValueError):
    """Raised when coordinates are non-finite."""
    pass

class Point(BaseModel):
    x: Annotated[float, Field(description="The x-coordinate")]
    y: Annotated[float, Field(description="The y-coordinate")]

    @classmethod
    def from_xy(cls, x: float, y: float) -> typing.Self:
        invalids = (float('inf'), float('-inf'))
        if x in invalids or y in invalids:
            raise InvalidCoordinateError(f"Coordinates must be finite. Received x={x}, y={y}")
        return cls(x=x, y=y)

```

### 5. Native Pydantic Validation

While most validation can occur in factory methods, it may sometimes be better to use Pydantic's native validation decorators (`@field_validator` and `@model_validator`) for enforcing strict data constraints directly on the model. This ensures that data is valid regardless of how the object was constructed and cleanly separates constraint logic from factory assembly.

```python
import typing
from typing import Annotated
from pydantic import BaseModel, Field, field_validator, model_validator

class BoundedPoint(BaseModel):
    x: Annotated[float, Field(description="The x-coordinate")]
    y: Annotated[float, Field(description="The y-coordinate")]

    @field_validator('x', 'y')
    @classmethod
    def check_finite(cls, v: float) -> float:
        if v in (float('inf'), float('-inf')):
            raise ValueError(f"Coordinates must be finite. Received {v}")
        return v

    @model_validator(mode='after')
    def check_first_quadrant(self) -> typing.Self:
        if self.x < 0 or self.y < 0:
            raise ValueError(f"Point must be in the first quadrant. Received x={self.x}, y={self.y}")
        return self
```

### 6. Data Pipelines as Type Transformations

The flow of data through our applications is designed as a pipeline of sequential transformations from one custom type to another.

The logic for transforming an upstream type into a downstream type should live entirely inside the **downstream type's static factory method**. This maintains weak coupling and ensures every object knows exactly how to construct itself from prior states.

```python
import math
import typing
from typing import Annotated
from pydantic import BaseModel, Field

class RadialPoint(BaseModel):
    r: Annotated[float, Field(description='Radius of the point in polar coords.')]
    theta: Annotated[float, Field(description='Angle of the point in polar coords.')]

    @classmethod
    def from_cartesian(cls, point: 'Point') -> typing.Self:
        """Transforms the upstream Point type into this downstream type."""
        return cls(
            r=math.sqrt(point.x**2 + point.y**2),
            theta=math.atan2(point.y, point.x),
        )

```

### 7. Composition and Layered Encapsulation

Our custom types are organized compositionally. Complex types are built by encapsulating lower-level custom types or collections of them.

We practice **strong encapsulation**: higher-level objects accomplish complex tasks by explicitly delegating to the methods of the lower-level objects they contain.

```python
import math
import typing
from typing import Annotated
from pydantic import BaseModel, Field

class LineSegment(BaseModel):
    start: Annotated['Point', Field()]
    end: Annotated['Point', Field()]

    @classmethod
    def from_points(cls, start: 'Point', end: 'Point') -> typing.Self:
        return cls(start=start, end=end)

    def length(self) -> float:
        # The LineSegment delegates to the properties of the encapsulated Points
        return math.sqrt((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)

```

### 8. Chained Serialization Protocols

Because our architectures are deeply compositional, our serialization logic must be as well. Do not implement custom `to_dict()` or `from_dict()` methods. Instead, rely entirely on Pydantic's native `.model_dump()` and `.model_validate()` methods.

Pydantic natively handles chained serialization. When you call `.model_dump()` on a parent model, it automatically serializes all nested Pydantic models. Similarly, `.model_validate()` automatically parses and instantiates nested models from dictionaries.

```python
import typing
from typing import Annotated
from pydantic import BaseModel, Field

class Point(BaseModel):
    x: Annotated[float, Field()]
    y: Annotated[float, Field()]


class LineSegment(BaseModel):
    start: Annotated[Point, Field()]
    end: Annotated[Point, Field()]

    # Serialization and deserialization are handled natively:
    # point = Point(x=1.0, y=2.0)
    # segment = LineSegment(start=point, end=Point(x=3.0, y=4.0))
    # data = segment.model_dump()  # {'start': {'x': 1.0, 'y': 2.0}, 'end': {'x': 3.0, 'y': 4.0}}
    # new_segment = LineSegment.model_validate(data)
```

### 9. Strongly Typed Collections via Pydantic `RootModel`

When working with groups of custom objects, it is often beneficial to create dedicated collection types rather than passing around generic `list` or `dict` objects.

**Do not subclass Python's built-in `list` or `dict`.** Subclassing C-implemented built-ins can lead to unexpected behaviors where standard operations (like slicing) bypass your custom methods.

Instead, rely on Pydantic v2's `RootModel`. This pattern natively extends our chained instantiation and serialization protocols without requiring custom factory methods for the collection itself. By defining a `RootModel`, Pydantic automatically handles parsing lists of dictionaries into lists of your custom models, and dumping them back to standard Python lists.

You can still attach custom business logic directly to the collection, and you can expose standard Python dunder methods (like `__iter__`) to make the object behave exactly like a native list.

```python
import typing
from typing import Annotated
from pydantic import BaseModel, Field, RootModel

class Point(BaseModel):
    x: Annotated[float, Field()]
    y: Annotated[float, Field()]

# Inherit from RootModel to create a strongly typed collection
class PointCloud(RootModel):
    root: list[Point]

    def __iter__(self) -> typing.Iterator[Point]:
        """Optional: Expose iteration directly so it behaves like a standard list."""
        return iter(self.root)

    def bounding_box(self) -> tuple[Point, Point]:
        """
        Custom business logic can now live directly on the collection,
        leveraging the guaranteed structure of the contained data.
        """
        if not self.root:
            raise ValueError("Cannot calculate bounding box of an empty PointCloud.")
        
        # We can iterate over self directly because we defined __iter__
        min_x = min(p.x for p in self)
        max_x = max(p.x for p in self)
        min_y = min(p.y for p in self)
        max_y = max(p.y for p in self)
        
        return Point(x=min_x, y=min_y), Point(x=max_x, y=max_y)

# Instantiation and serialization are handled entirely by Pydantic natively:
#
# raw_data = [{"x": 1.0, "y": 2.0}, {"x": 3.0, "y": 4.0}]
#
# 1. Native chained instantiation (no custom from_point_dicts needed)
# cloud = PointCloud.model_validate(raw_data)
# 
# 2. Native chained serialization (no custom to_dict_list needed)
# data_list = cloud.model_dump()

```