## Architectural Guidelines

This document outlines the standard patterns for defining, instantiating, and transforming data in our applications. Our architecture relies on explicit data containers, strong encapsulation, strict immutability, and data pipelines constructed via sequential type transformations.

### 1. Explicit Data Containers

We rely on strongly typed, explicit data containers to pass information through the application.

* **Default to `pydantic`:** For all data structures, use `pydantic.BaseModel`. Pydantic provides robust typing, built-in validation, and excellent integration with external boundaries (e.g., FastAPI request/response payloads, or structured outputs for generative AI packages).
* **Attribute Annotation:** All fields should be annotated using the `Annotated[type, Field(...)]` pattern to allow for explicit field-level configuration, metadata, and constraints.
* **Immutability:** Once instantiated, the encapsulated data within these containers should be treated as strictly immutable. Any modification of data should result in the generation of a *new* object, rather than mutating an existing one in place.

### 2. Strict Instantiation via Static Factory Methods

The default constructor (`__init__`) must remain completely "dumb." It should strictly be used for assigning attributes and should **never** contain default parameters or custom logic.

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

### 3. Fail-Fast Validation and Custom Exceptions

Validation must happen at the moment of instantiation within the factory methods. If data is invalid, the application should fail fast.

We heavily utilize **Custom Exceptions** to provide exact details about what went wrong at the lowest possible level. Higher-level orchestration functions are then responsible for catching these custom exceptions and altering application behavior or surfacing the error to the user.

```python
import typing
from typing import Annotated
from pydantic import BaseModel, Field

class InvalidCoordinateError(ValueError):
    """Raised when coordinates are non-finite."""
    pass

class Point(BaseModel):
    x: Annotated[float, Field()]
    y: Annotated[float, Field()]

    @classmethod
    def from_xy(cls, x: float, y: float) -> typing.Self:
        invalids = (float('inf'), float('-inf'))
        if x in invalids or y in invalids:
            raise InvalidCoordinateError(f"Coordinates must be finite. Received x={x}, y={y}")
        return cls(x=x, y=y)

```

### 4. Data Pipelines as Type Transformations

The flow of data through our applications is designed as a pipeline of sequential transformations from one custom type to another.

The logic for transforming an upstream type into a downstream type should live entirely inside the **downstream type's static factory method**. This maintains weak coupling and ensures every object knows exactly how to construct itself from prior states.

```python
import math
import typing
from typing import Annotated
from pydantic import BaseModel, Field

class RadialPoint(BaseModel):
    r: Annotated[float, Field()]
    theta: Annotated[float, Field()]

    @classmethod
    def from_cartesian(cls, point: 'Point') -> typing.Self:
        """Transforms the upstream Point type into this downstream type."""
        return cls(
            r=math.sqrt(point.x**2 + point.y**2),
            theta=math.atan2(point.y, point.x),
        )

```

### 5. Composition and Layered Encapsulation

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

### 6. Chained Serialization Protocols

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

### 7. Strongly Typed Collections via Inheritance

When working with groups of custom objects, it is often beneficial to create dedicated collection types rather than passing around generic `list` or `dict` objects. We achieve this by inheriting directly from Python's standard collection types (e.g., `list[CustomType]` or `dict[str, CustomType]`).

**Do not override the `__init__` method of built-in collections.** Overriding standard collection constructors can lead to unintended side effects or break expected behaviors. Instead, we exclusively use static factory methods to instantiate these custom collections.

This approach naturally extends our chained instantiation protocol: the collection's factory method iterates over the raw data and delegates the instantiation of individual items to the factory methods of the contained type.

```python
import typing
from typing import Annotated
from pydantic import BaseModel, Field

class Point(BaseModel):
    x: Annotated[float, Field()]
    y: Annotated[float, Field()]


# Inherit directly from list, specifying the contained type
class PointCloud(list[Point]):
    
    @classmethod
    def from_point_dicts(cls, data_list: list[dict]) -> typing.Self:
        """
        Instantiates the collection by chaining down to the contained 
        type's native validation method.
        """
        # We call the class constructor (cls) with a list comprehension
        # that utilizes the Point.model_validate method.
        return cls([Point.model_validate(item) for item in data_list])

    def to_dict_list(self) -> list[dict]:
        """Chains serialization down to the contained items."""
        return [point.model_dump() for point in self]

    def bounding_box(self) -> tuple[Point, Point]:
        """
        Custom business logic can now live directly on the collection,
        leveraging the guaranteed structure of the contained data.
        """
        if not self:
            raise ValueError("Cannot calculate bounding box of an empty PointCloud.")
        
        min_x = min(p.x for p in self)
        max_x = max(p.x for p in self)
        min_y = min(p.y for p in self)
        max_y = max(p.y for p in self)
        
        return Point(x=min_x, y=min_y), Point(x=max_x, y=max_y)

```