
# Architectural Guidelines: Data Containers and Pipelines

This document outlines the standard patterns for defining, instantiating, and transforming data in our applications. Our architecture relies on explicit data containers, strong encapsulation, strict immutability, and data pipelines constructed via sequential type transformations.

### 1. Explicit Data Containers
We rely on strongly typed, explicit data containers to pass information through the application.

* **Default to `dataclasses`:** For purely internal data structures, use Python's built-in `@dataclasses.dataclass`. 
* **Use `pydantic` at I/O Boundaries:** Reserve Pydantic models for interfaces where external validation or specific schemas are beneficial (e.g., FastAPI request/response payloads, or structured outputs for generative AI packages).
* **Immutability:** Once instantiated, the encapsulated data within these containers should be treated as strictly immutable. Any modification of data should result in the generation of a *new* object, rather than mutating an existing one in place.

### 2. Strict Instantiation via Static Factory Methods
The default constructor (`__init__`) must remain completely "dumb." It should strictly be used for assigning attributes and should **never** contain default parameters or validation logic. 

Instead, all instantiation logic, default parameter injection, and data coercion must happen within **static factory methods** (using the `@classmethod` decorator).

```python
import dataclasses
import typing

@dataclasses.dataclass
class Point:
    # No default values here.
    x: float
    y: float

    # __init__ is generated automatically by @dataclass and is kept strictly for assignment.

    @classmethod
    def from_coordinates(cls, x: float = 0.0, y: float = 0.0) -> typing.Self:
        # Defaults and any setup logic live in the factory method.
        return cls(x=float(x), y=float(y))
```

### 3. Fail-Fast Validation and Custom Exceptions
Validation must happen at the moment of instantiation within the factory methods. If data is invalid, the application should fail fast. 

We heavily utilize **Custom Exceptions** to provide exact details about what went wrong at the lowest possible level. Higher-level orchestration functions are then responsible for catching these custom exceptions and altering application behavior or surfacing the error to the user.

```python
class InvalidCoordinateError(ValueError):
    """Raised when coordinates are non-finite."""
    pass

@dataclasses.dataclass
class Point:
    x: float
    y: float

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
@dataclasses.dataclass
class RadialPoint:
    r: float
    theta: float

    @classmethod
    def from_cartesian(cls, point: Point) -> typing.Self:
        """Transforms the upstream Point type into this downstream type."""
        import math
        return cls(
            r=math.sqrt(point.x**2 + point.y**2),
            theta=math.atan2(point.y, point.x),
        )
```

### 5. Composition and Layered Encapsulation
Our custom types are organized compositionally. Complex types are built by encapsulating lower-level custom types or collections of them. 

We practice **strong encapsulation**: higher-level objects accomplish complex tasks by explicitly delegating to the methods of the lower-level objects they contain.

```python
@dataclasses.dataclass
class LineSegment:
    start: Point
    end: Point

    @classmethod
    def from_points(cls, start: Point, end: Point) -> typing.Self:
        return cls(start=start, end=end)

    def length(self) -> float:
        import math
        # The LineSegment delegates to the properties of the encapsulated Points
        return math.sqrt((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)
```

### 6. Chained Serialization Protocols
Because our architectures are deeply compositional, our serialization logic must be as well. Classes should implement standard serialization methods (typically `to_dict()` and `from_dict()`). 

When a parent object serializes itself, it must chain the serialization calls down to its child components. This explicit contract ensures that any encapsulated type can be safely swapped or refactored without breaking the parent's ability to save or load its state.

```python
@dataclasses.dataclass
class Point:
    x: float
    y: float

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict) -> typing.Self:
        return cls.from_xy(x=data["x"], y=data["y"])


@dataclasses.dataclass
class LineSegment:
    start: Point
    end: Point

    def to_dict(self) -> dict:
        # Chained serialization: Parent relies on children's serialization methods
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> typing.Self:
        # Chained deserialization
        return cls(
            start=Point.from_dict(data["start"]),
            end=Point.from_dict(data["end"])
        )
```