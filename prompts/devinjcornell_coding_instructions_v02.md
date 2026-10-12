# Coding Guide

This provides strategies, styles, and architectural instructions that Devin J. Cornell expects coders to follow.


## Tooling

+ **Package management**: install and use UV for package management.
+ **Formatting and linting**: install and configure Ruff, which will format your code according to PEP 8.
+ **Type checking**: install and configure Pyright (Pylance).
+ **Unit tests**: use the Pytest framework.
+ **Automated actions**: Use Justfile for managing and running common routines/commands (instead of Make).



## Styles and Conventions

### Docstrings and Annotations

* Use modern Google-style docstrings for 2026. Every class, function, and method should have a docstring describing what it does.
* Modern python includes type hints, so you do not need to specify argument types in modern Python docstrings.

### Use of Exceptions

* Heavily utilize custom exceptions to provide detailed failure context.
* Fail fast and hard - do not attempt to recover from issues with input data automatically.
* When needed, use inheritance to give users flexibility in the way they handle exceptions.
* Raise these exceptions at the lowest levels possible so they can be caught in higher-level code.

For instance, use `mydict.get(key)` only when there is a good domain reason that a key does not exist. Use `mydict[key]` in most cases to add structural integrity to your program.

## Architectural Guidelines

The dominant modeling philosophy should be domain-driven design, and the following topics discuss how to construct types and architectures that support that philosophy.


There are several aspects of architectural guidelines discussed here:

* Custom types
* Custom collection types
* Architecture and design principles

### Type Definitions

* Use strong typing everywhere - custom types should be used in almost every part of an application.
* Custom types should primarily be used as data containers with extra logic for interacting with the underlying data.

Almost every custom type should be either a `dataclass` or a `pydantic` type.

* Use Pydantic at the system boundaries to parse, validate, and serialize untrusted data; use `@dataclass` in the core domain to model internal state and business logic.
* Pydantic types can have dataclass-typed attributes that work seamlessly for serialization (`model_dump`/`model_dump_json`) and schema creation (`model_json_schema`) functions.
* Note that regular dataclasses can still use `pydantic.Field` for wrapping schema metadata.



#### Type Hints

Type hints are important for both static analyzers and runtime consumers (e.g., `fastapi`, `google.genai`, or `pydantic-ai`).

This is how type hints should be written:

* Use modern typing features using `from __future__ import annotations`.
* Avoid using strings for type hint names (e.g., `list['MyType']` vs `list[MyType]`) - if these are needed, the application design is probably weak.
* Use `Self` to reference a type's own type, not the name of the class in strings or anything else.
* Use operator syntax for type hints. E.g., `|` instead of `Union`, etc.

##### Annotation With Fields

Annotations and `pydantic.Field` for dataclasses and Pydantic types:

* Type hints for attributes of pydantic types should always follow the pattern `Annotated[type, pydantic.Field(...)]`.
* When a dataclass is used as part of a larger Pydantic data structure, attributes should also follow `Annotated[type, pydantic.Field(...)]`.
* In cases where dataclasses do not need metadata for runtime consumers, annotations and `pydantic.Field` type hints may be omitted.
* When `pydantic.Field(...)` data is being included, the `Field` should at least include a useful, contextualizing description.

Using `Field` with Pydantic types adds runtime constraint validation and default values/factories to the default constructor, but adding it to a dataclass definition still provides several of the same additional benefits:

* **Schema generation**: client can use `MyType.model_json_schema()` to create detailed schema information. Packages like `fastapi`, `pydantic-ai`, and `google.genai` all use these schemas to control behavior at runtime.
* **Serialization/deserialization**: adds runtime constraint validation and default values/factories to serialization/deserialization methods.

For instance, in the following example we have a regular dataclass `UserInfo` and a pydantic type `User` with an attribute of type `UserInfo`. We use `Annotated[type, pydantic.Field(...)]` in the dataclass only because it is also being used in a Pydantic type for which we may want to use schema generation.

```python
from typing import Annotated
from dataclasses import dataclass
from pydantic import BaseModel, Field
import uuid

@dataclass(slots=True, frozen=True)
class UserInfo:
    name: Annotated[str, Field(description="Public name of the user.", default='<NAME_EMPTY>')]
    age: Annotated[int, Field(description="Age of the user (does not appear publicly).", gt=0, lt=150)]

class User(BaseModel):
    uuid: Annotated[str, Field(description="Unique identifier of the instance.")]
    mdc: UserInfo
```

We can then generate the type schema using `User.model_json_schema()`, serialize an instance to a dictionary using `user.model_dump()`, or parse a dictionary using `User.model_validate({...})`.

Adding these arguments to the `pydantic.Field` type hints in the dataclass has the following consequences:

* `UserInfo.name` has a `default` value. This default value will not be used in the default constructor, but it is added to the generated schema and allows the field to be optional when deserializing with `model_validate`.
* `UserInfo.age` has constraints `gt` and `lt`. These constraints will not be validated when the default constructor is called, but they will be specified in the generated schema (`User.model_json_schema()`) and validated against when calling `User.model_validate`.




In dataclasses, `pydantic.Field` type hints only provide metadata for schema creation and serialization/deserialization - they do not affect the behavior of the type itself like `Field` does for pydantic types. See the following example:


* **constraints**: Pydantic will use constraint information (e.g., `gt`, `lt`, etc) for validation on instantiation, while dataclasses only use this for schema generation.
* default values: x
* schema metadata.


Schema generation:

* Tools such as `fastapi`, `google.genai`, or `pydantic-ai` all generate schemas from the types using the pydantic method `MyType.model_json_schema()`.
* If present, the 



The behavior of `pydantic.Field` varies according to whether a 


`pydantic.Field` in Pydantic type definitions:

* Constraints should be added to `Field` in both dataclasses and pydantic types for runtime consumption (e.g., schema generation), though note that regular dataclasses do not use them for runtime validation.
* For dataclasses, all constraints/validation should be omitted from the `Field`.


allow for explicit field-level configuration, metadata, and constraints.


Whether a type 

* All dataclass and pydantic fields should be annotated using the `Annotated[type, pydantic.Field(...)]` pattern to allow for explicit field-level configuration, metadata, and constraints.
* `Field` instances should always have descriptions. Ideally they should also include examples or other attributes that make the meaning of the type clearer to the reader and more useful for runtime consumers.
* Field descriptions should often include references to other types to indicate to the user how they may be related.

```python
from typing import Annotated
from pydantic import BaseModel, Field

class Point(BaseModel):
    '''A single point in Cartesian space'''
    x: Annotated[float, Field(description="The x-coordinate")]
    y: Annotated[float, Field(description="The y-coordinate")]
```

##### Semantic Typing

Semantic typing with `NewType` should be used for primitives wherever relevant.

Note that `Annotated` itself does not provide type safety, but you should use `NewType` alongside `Annotated` for primitives:

* If the given type is to be used as part of a core domain concept, define the semantic type privately (e.g., `_MyNewType = NewType('_MyNewType', int)`) and then use `MyNewType = Annotated[_MyNewType, Field(..)]` to include description, examples, and any other validation logic.
* If you have strong distinction between application layer and a core domain model, use something like `UserId = NewType('UserId', int)` in the domain model and then `ValidatedUserId = Annotated[UserId, Field(gt=0)]` in the application layer.

##### Generics

* Always use generics with `TypeVar` in both type and method definitions where applicable.

##### Protocols

* Always use `typing.Protocol` where relevant - particularly for strategy patterns or APIs that accepts complex types or type definitions.
* Use `@runtime_checkable` only on API boundaries or other high-stakes interfaces; otherwise, trust static analyzers.

#### Instantiation

Custom types should often include both default and non-default static factory constructors.

Carefully consider whether to include particular features in the default constructor (especially the one created by pydantic) vs non-default static factory constructors.

In most cases, the default constructor should force the user to provide all attributes and only serve to create the instance from the provided data. Use non-default constructors when you need any of these things:

* **Default values**: place these in non-default constructors, as they are not essential to the definition of a type.
* **Parsing logic**: some parsing logic comes with general type safety.
* Validation logic that is specific to some instantiation method
* Performant


* Leave default pydantic `__init__` constructors purely for creating the container.
* Use non-default



* In most cases, avoid adding default factories and values to the pydantic type definition - instead, force the client user to provide all values when using the default constructor.


Embrace the automated validation and initialization that happens under the hood during instantiation.
* Use static factory methods (`@classmethod`) where logic or defaults are required for instantiation.

exclusively for custom type instantiation, data transformation, and validation.
* Non-default constructors should follow the naming convention `from_*` (e.g., `from_vector`)
* Do not define default parameter values in the class definition; instead, add them to the constructors (usually as a constructor parameter default).
* Use validation logic in constructors when parameters may be complicated or constructor is handling input validation.

#### Immutability

* Almost always treat custom type instances as immutable.
* Use `model_copy` to create new instances by copying old values. This is similar to `clone` in Rust. Avoid trying to re-implement this behavior with custom methods.
* You should almost always make copies of mutable collections (e.g., `list`, `dict`, and `set`) inside nondefault constructors.
* In rare cases where you need enforcement (e.g., when presenting read-only information), set the attribute `model_config = ConfigDict(frozen=True)` in your pydantic type.

#### Validation

Because instances are treated as immutable, it is usually sufficient to validate data inside nondefault constructors.

In cases where there are multiple constructors and every instance must definitionally conform to the constraint, it can be added to the definition itself as a declarative constraint.

* In most cases, set constraints in `Field(..)` instances, as it is fast and gives runtime consumers access for automatic documentation creation.
* When validation requires custom validation on a single attribute, use `field_validator`.
* When validation requires custom validation on multiple attributes, use `model_validator`.
* When writing re-usable `Annotated` types without `Field(..)` (usually outside a pydantic type definition), use `AfterValidator` or `BeforeValidator`.

##### Serialization

* Use `model_dump`/`model_dump_json` or `model_validate`/`model_validate_json` wherever possible (especially if you only need to set an `alias` in the `Field`).
* When possible, re-use `model_dump`/`model_dump_json` or `model_validate`/`model_validate_json` as part of the custom serializers/deserializers.
* If complex serialization/deserialization is required, preemptively create both serialization (`to_*`) and deserialization (`from_`) methods.
* In multi-level or recursive compositional data structures, chain custom subtype serialization/deserialization methods (`model_dump` and `model_validate` already do this).
* Use `computed_field` when you want to add attributes to the serialized object that are computed from existing properties.
* Use `AliasChoices` when deserializing data with an inconsistent format, but do not overdo it.

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

* Use strong typing principles.
* Use composition over inheritance wherever possible, even if it means more complicated data structures.

#### Domain-driven Design

Generally attempt to adhere to the engineering principles and philosophy of Domain-driven Design (DDD). There is one primary exception: when it is convenient, you may re-use Entities or Value Objects in multiple architectural layers to avoid creating duplicate objects that store almost exactly the same information. This can be especially helpful for types that are very complex with many attributes or definitional constraints. The use of compositional data structures can help reduce the risk of such an approach.

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



















## Preferred Packages

+ Tabular Data
    + When possible, use lists/dicts of dataclasses or `pydantic` types over dataframes.
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
    + When advanced Google-specific tools (such as Web Search) are needed, use the `python.genai` package.
+ SQL Databases
    + Use `sqlalchemy` Core patterns (ideally not ORM if it cannot be helped).
+ NoSQL Databases
    + Use `pymongo` with MongoDB, avoid Beanie and similar tools.
    + Ideally use custom types to represent documents.

