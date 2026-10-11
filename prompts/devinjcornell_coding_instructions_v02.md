# Coding Guide

This is a compilation of different strategies, styles, and architectures that Devin Cornell likes to use when writing code.




## Styles and Conventions

### Docstrings and Annotations

* **Docstrings:** Use docstrings extensively. Every class, property, function, and method should have a docstring describing what it does. Add parameter descriptions to the docstrings only when requested explicitly.
* **Attribute Annotations:** All pydantic type attributes should use annotations like `Annotated[type, Field(description='..', ...)]` with good descriptions for both readability and so they can be used by the many packages that accept pydantic types.


### Extensive Type Hints


* **Data Structures** Raw dictionaries should almost never be used to represent complex data structures - you might as well use defined pydantic types with composition.
* **Strict Typing:** Rely heavily on comprehensive type hints to empower static analysis tools (like MyPy or Pyright) and prevent runtime errors.
* **Modern Syntax:** Exclusively use modern Python typing standards, such as the `|` operator for unions (instead of `Union`) and `typing.Self` for methods returning the object's own type.
* **Use Generics for Functions and Classes:** when applicable, use generics for both classes and functions. For Python 3.12 use `MyClass[T]` syntax and for earlier versions you can use `T = TypeVar("T")` and `MyClass(Generic[T])`.
* **Semantic Typing:** use semantic typing of some kind. The default strategy should be to use type aliases, e.g., `UserId = int` (or `type UserId = int` for Python 3.12+). If it is deemed to be far better, use nominal subtyping with `NewType` like `UserId = typing.NewType("UserId", int)`.
* **Self-referencing Hints:** When applicable, use `typing.Self` with `from __future__ import annotations` (or `from typing_extensions import Self` for Python < 3.11)
* **Attribute Annotations:** All pydantic type attributes should use annotations like `Annotated[type, Field(description='..', ...)]` with good descriptions for both readability and so they can be used by the many packages that accept pydantic types.


---


### Naming Conventions

* **Classes:** Use `PascalCase` for all class definitions and custom type aliases.
* **Methods & Functions:** Use `snake_case` for all functions, methods, and variables.



### Imports

For capitalized classes and types, it is standard and acceptable to use `from x import y` (e.g., `from fastapi import FastAPI`). Reserve `import x` for modules with overlapping function names to prevent namespace collisions. Ignore this for relative imports obviously.

---

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



* Use custom or semantic types for almost every kind of data.
* Use strong encapsulation - only the type itself should know the implementation details.
* Avoid inheritance in favor of composition wherever possible, even if it makes some designs more complicated.




### Type Definitions

Always rely on strongly typed, explicit `pydantic` data containers to pass information through the application. 


#### Annotations

Annotations are often useful for both readers and runtime consumers (e.g., `fastapi`, `google.genai`, or `pydantic-ai` applications).

Here are some general preferences:

* Use modern typing features using `from __future__ import annotations`.
* Avoid using strings for type hint names (e.g., `list['MyType']` vs `list[MyType]`) - if these are needed, the application design is probably weak.

##### Annotation With Fields

* All pydantic class fields should be annotated using the `Annotated[type, Field(...)]` pattern to allow for explicit field-level configuration, metadata, and constraints.
* `Field` instances should always have descriptions. Ideally they should also include examples or other attributes that make the meaning of the type clearer to the reader and more useful for runtime consumers.

```python
from typing import Annotated
from pydantic import BaseModel, Field

class Point(BaseModel):
    '''A single point in Cartesian space'''
    x: Annotated[float, Field(description="The x-coordinate")]
    y: Annotated[float, Field(description="The y-coordinate")]
```

##### Semantic Typing

Semantic typing with `NewType` should be used for primatives wherever relevant.

Note that `Annotated` itself does not provide type safety, but you should use `NewType` alongside `Annotated` for primatives:

* If the given type is to be used as part of a core domain concept, define semantic type privately (e.g., `_MyNewType = NewType('_MyNewType', int)`) and then use `MyNewType = Annotated[_MyNewType, Field(..)]` to include description, examples, and any other validation logic.
* If you have strong distinction between application layer and a core domain model, use something like `UserId = NewType('UserId', int)` in the domain model and then `ValidatedUserId = Annotated[UserId, Field(gt=0)]` in the application layer.

##### Generics

* Always use generics with `TypeVar` in both type and method definitions where applicable.

##### Protocols

* Always use `typing.Protocol` where relevant - particularly for strategy patterns or APIs that accepts complex types or type definitions.
* Use `@runtime_checkable` only on API boundaries or other high-stakes interfaces; otherwise, trust static analyzers.

#### Instantiation

* Almost always use static factory methods (`@classmethod`) exclusively for custom type instantiation, data transformation, and validation.
* Non-default constructors should follow the naming convention `from_*` (e.g., `from_vector`)
* Do not override or write custom `__init__` methods. Embrace the automated validation and initialization that happens under the hood during instantiation.
* Do not define default parameter values in the class definition; instead, add them to the constructors (usually as a constructor paramter default).
* Use validation logic in constructors when parameters may be complicated or constructor is handling input validation.

#### Immutability

* Almost always treat custom type instances as immutable.
* Use `model_copy` to create new instances by copying old values. This is similar to `clone` in Rust. Avoid trying to re-implement this behavior with custom methods.
* You should almost always make copies of mutable collections (e.g., `list`, `dict`, and `set`) inside nondefault constructors.
* In rare cases where you need enforcement (e.g., when presenting read-only information), set the attribute `model_config = ConfigDict(frozen=True)` in your pydantic type.

#### Validation

Because instnaces are treated as immutable, it is usually sufficient to validate data inside nondefault constructors.

In cases where there are multiple constructors and every instance must definitionally conform to the constraint, it can be added to the definition itself as a declarative constraint.

* In most cases, set constraints in `Field(..)` instances, as it is fast and gives runtime consumers access for automatic documentation creation.
* When validation requires custom validation on a single attribute, use `field_validator`.
* When validation requires custom validation on multiple attributes, use `model_validator`.
* When writing re-usable `Annotated` types without `Field(..)` (usually outside a pydantic type definition), use `AfterValidator` or `BeforeValidator`.

##### Serialization

* Use `model_dump`/`model_dump_json` or `model_validate`/`model_validate_json` wherever possible (sepecially if you only need to set an `alias` set in the `Field`).
* When possible, re-use `model_dump`/`model_dump_json` or `model_validate`/`model_validate_json` as part of the custom serializers/deserializers.
* If complex serialization/deserialization is required, preempively create both serialization (`to_*`) and deserialization (`from_`) methods.
* In multi-level or recursive compositional data structures, chain custom subtype serialization/deserialization methods (`model_dump` and `model_validate` already do this).
* Use `computed_field` when you want to add attributes to the serialized object that are computed from existing properties.
* Use `AliasChoices` when deserializating data with an inconsistent fromat, but do not overdo it.

### Custom Collection Types

If you need functions or validations that operate on collections of specific types (including custom types or primitive semantic types), create custom collection types with `RootModel`.

* In most cases, you should define the type using syntax like `class PointList(list[Point])` instead of using a `root` attribute.
* In cases where definitional constraints/validation is required for the collection, use `RootClass.model_validator`.

```python
from typing import Annotated, NewType
from pydantic import BaseModel, Field, RootModel, model_validator

class Point(BaseModel):
    '''A single point in Cartesian space'''
    x: Annotated[float, Field(description="The x-coordinate")]
    y: Annotated[float, Field(description="The y-coordinate")]

class PointList(RootModel[list[Point]]):
    '''List of points.'''
    def mean(self) -> float:
        pass

PointName = NewType('PointName', str)

class PointMap(RootModel[dict[PointName, Point]]):
    '''Dictionary mapping point names to points.'''
    def names(self) -> list[PointName]:
        return list(self.root.keys())

    def point_list(self) -> PointList:
        return PointList(root=list(self.root.values()))

class UniqueNamesList(RootModel[list[PointName]]):
    @model_validator(mode='after')
    def check_uniqueness(self) -> None:
        if len(self.root) != len(set(self.root)):
            raise ValueError("All names in the list must be unique")
```




### Architecture and Patterns



Architecturally speaking, the best designs have strong type safety and are highly compositional.


#### Domain-driven Design

Generally attempt to adhere to the engineering principles and philosophy of Doman-driven Design (DDD). There is one primary exception: when it is convenient, you may re-use Entities or Value Objects in multiple architectural layers to avoid creating duplicate objects that store almost exactly the same information. This can be especially helpful for types that are very complex with many attributes or definitional constraints. The use of compositional data structures can help reduce the risk of such an approach.

The following are design principles of DDD:

##### Structural Architecture & Isolation

* Partition the system using a Layered Architecture to completely isolate the domain model and business logic into a single, cohesive layer.
* A layer may depend in some part on the layers beneath it, but never above; each layer provides a set of building blocks that higher layers can use.
* Eliminate all dependencies within the domain layer on infrastructure, user interfaces, or application logic.
* Decompose the code into cohesive Modules (packages) that reflect high-level domain concepts, ensuring low coupling between different parts of the system.

##### Tactical Domain Objects

* Define objects with a continuous lifecycle and unique identity as Entities.
* Define immutable characteristics, attributes, or calculations as Value Objects, ensuring all their operations are side-effect-free.
* Define significant domain processes or transformations that do not naturally belong to an Entity or Value Object as standalone Services.
* Define discrete, past activities in the domain as full-fledged, immutable Domain Events.

##### State Management & Transactional Boundaries

* Cluster related Entities and Value Objects into Aggregates to establish strict boundaries for data consistency.
* Designate a single entity as the Aggregate root to enforce all invariants and consistency rules for the cluster.
* Restrict external objects to holding references only to the Aggregate root, never to its interior elements.
* Apply consistency rules synchronously within an Aggregate boundary, and handle updates across different Aggregates asynchronously.

##### Encapsulating Object Lifecycles

* Delegate the complex assembly of entire aggregates or large value objects to Factories, enforcing creation invariants without exposing internal structures to the client.
* Delegate object storage and retrieval to Repositories, providing the application logic with the illusion of an in-memory collection of aggregate roots while encapsulating the underlying database technology.
* Restrict Repositories to only provide direct access to Aggregate roots, rather than individual interior objects.

#### Data Pipelines and Transformations

* Data transformations between types should be implemented in non-default constructors so that only the type itself needs to be privy to its own implementation.

#### Protocols and Structural Subtyping

* Structural subtyping using `Protocol` is strongly preferred over nominal subtyping.
* Use `Protocol` when implementing Observer, Adapter, and Repository (Dependency Injection) design patterns.























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

Because our architectures are deeply compositional, our serialization logic must be as well. Unless some important logic is required for serialization/deserialization, avoid implementing custom `to_dict()` or `from_dict()` methods. Instead, rely on Pydantic's native `.model_dump()` and `.model_validate()` methods when possible.

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



---

## Tools for the Job

### Preferred Packages

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
    + Use `sqlalchemy` Core patterns (ideally not ORM if it cannot be helped).
+ NoSQL Databases
    + Use `pymongo` with MongoDB, avoid Beanie and similar tools.
    + Ideally use custom types to represent documents.


### Supporting Tools
