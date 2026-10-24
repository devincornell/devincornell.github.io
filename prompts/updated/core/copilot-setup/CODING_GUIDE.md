# Team Coding Guide

## Purpose

This guide defines the default engineering standards for Python repositories. It
is intended for both developers and coding assistants.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY**
describe requirement strength:

- **MUST** rules are required unless an approved exception is documented.
- **SHOULD** rules are defaults that may be changed for a stated technical reason.
- **MAY** rules are optional practices to consider when they add value.

Repository-specific conventions take precedence when they are documented and
enforced by that repository.

This guide revises Devin J. Cornell's Coding Guide v03.

## Engineering Principles

- Prefer clear, explicit code over clever or highly abstract code.
- Use the simplest design that preserves correctness and maintainability.
- Support a deliberately narrow set of inputs and fail as early as possible when
  input falls outside it.
- Validate untrusted data at system boundaries and fail early with useful errors.
- Keep business rules independent of transport, storage, and framework details.
- Prefer immutable values and explicit state transitions.
- Use strong typing where it prevents ambiguity or invalid states.
- Automate standards through tools and CI rather than relying on memory.
- Apply architecture in proportion to the problem. Small utilities do not need
  the same structure as long-lived domain applications.

Generally follow [PEP 20 - The Zen of Python](https://peps.python.org/pep-0020/),
especially: explicit is better than implicit; errors should never pass silently;
in the face of ambiguity, refuse the temptation to guess.

## Repository Baseline

Every maintained Python repository MUST define:

- Its supported Python version in `pyproject.toml`.
- Dependencies and lock data using UV.
- Ruff formatting and linting configuration.
- Pyright type-checking configuration.
- Pytest configuration and a test directory.
- Common developer commands in a `Justfile`.
- Setup, configuration, and execution instructions in `README.md`.
- A committed `.env.example` when runtime configuration is used.
- CI checks for formatting, linting, typing, and tests.

Generated project files, virtual environments, local `.env` files, caches, and
secrets MUST be excluded from version control.

Recommended commands are:

```just
install:
    uv sync

format:
    uv run ruff format .
    uv run ruff check --fix .

check:
    uv run ruff format --check .
    uv run ruff check .
    uv run pyright
    uv run pytest
```

Repositories MAY use different command names, but the README and CI MUST use the
same supported commands developers use locally.

## Configuration and Environment Variables

Runtime configuration MUST be explicit, typed, documented, and validated at
startup. Python applications SHOULD use `pydantic-settings` as the configuration
boundary.

### Source of Truth

- A typed settings model MUST define every application-owned environment variable.
- Missing required values and invalid combinations MUST fail during startup.
- Configuration precedence MUST be documented, including command-line values,
  process environment, `.env` files, and defaults.
- Code MUST NOT call `os.getenv` throughout the application. Load configuration
  once and inject typed settings or the required values.
- Secrets MUST NOT have real defaults, appear in logs, or be committed to source
  control.
- Applications SHOULD log the effective non-secret configuration at startup.

### `.env.example`

Repositories that use environment variables MUST commit a `.env.example`. It
MUST remain synchronized with the settings model and MUST contain safe example
values rather than operational secrets.

Each variable SHOULD document:

- Purpose.
- Type and allowed values.
- Whether it is required and any default.
- Environments in which it may be used.
- Whether it is secret.
- Dependencies or conflicts with other variables.

Example:

```dotenv
# Runtime environment.
# Type: enum
# Allowed: local, test, staging, production
# Default: local
APP_ENV=local

# Authentication strategy.
# Type: enum
# Allowed: oidc, fake, disabled
# Default: oidc
# Restriction: fake and disabled are forbidden in staging and production
AUTH_MODE=oidc

# Identity used when AUTH_MODE=fake.
# Type: email
# Required when: AUTH_MODE=fake
# Secret: no
FAKE_USER_EMAIL=developer@example.com
```

Prefer one explicit mode such as `AUTH_MODE=oidc|fake|disabled` over interacting
flags such as `DISABLE_AUTH` and `FAKE_USER`. If a boolean is appropriate, accept
one documented representation consistently, preferably `true` and `false`.

Insecure development features MUST be structurally unavailable in staging and
production. The application MUST refuse to start when configuration would disable
authentication, use a fake identity, expose debug endpoints, or otherwise weaken
production safeguards.

CI SHOULD verify that:

- `.env.example` can instantiate the settings model.
- Every application-owned setting is represented in `.env.example`.
- The example contains no apparent secrets.
- Invalid or insecure setting combinations are covered by tests.

## Documentation

### Repository Documentation

`README.md` MUST enable a new contributor to install and run the project without
private verbal instructions. It MUST include:

- Project purpose and supported use cases.
- Prerequisites and installation commands.
- Local run, test, lint, type-check, and format commands.
- Configuration precedence and a link to `.env.example`.
- Common local configurations, including authentication setup.
- External service dependencies and how to obtain access.
- Deployment or operational documentation links when applicable.

Documentation MUST be updated in the same change that alters public behavior,
configuration, setup, or operational procedures.

Significant architectural decisions SHOULD be recorded as short Architecture
Decision Records describing context, decision, consequences, and alternatives.

### Code Documentation

- Public modules, classes, and functions MUST have modern Google-style docstrings
  when their purpose, contract, or failure behavior is not obvious from the API.
- Domain concepts and public extension points SHOULD always be documented.
- Trivial private helpers and self-explanatory methods do not require docstrings.
- Docstrings MUST add intent, invariants, side effects, or failure information;
  they MUST NOT merely restate the signature.
- Types belong in annotations, not duplicated in docstrings.
- Comments SHOULD explain why a decision exists, not narrate what code does.

## Types and Data Modeling

### Type Checking

- All functions, methods, and class attributes MUST have accurate type
  annotations. Local variables MAY rely on inference.
- Repositories SHOULD use Pyright strict mode or document disabled diagnostics.
- Use modern syntax: `T | None` instead of `Optional`, `A | B` instead of
  `Union`, built-in generics such as `list[T]`, and `Self` for methods returning
  the current class. Repositories supporting Python older than 3.11 SHOULD use
  `from __future__ import annotations` and `typing_extensions` as needed.
- String forward references MAY be used when needed to resolve import cycles or
  recursive models. Their presence does not by itself indicate a design problem.
- `Any`, casts, and ignored diagnostics MUST be localized and justified.

### Semantic Types

Use `NewType`, enums, or value objects when two values share a primitive
representation but are not safely interchangeable. Do not wrap every primitive
solely to satisfy a stylistic rule.

`Annotated` adds metadata but no static distinction, so combine it with
`NewType` when both are needed:

```python
# Domain meaning, checked statically.
UserId = NewType("UserId", int)

# Boundary contract, checked at runtime by Pydantic.
ValidatedUserId = Annotated[
    UserId,
    Field(gt=0, description="Identifier of an existing user."),
]
```

When one alias serves every layer, define the `NewType` privately and export the
annotated alias, for example `_UserId = NewType("_UserId", int)` and
`UserId = Annotated[_UserId, Field(...)]`.

### Generics and Protocols

- Reusable functions and containers SHOULD use generics to preserve element and
  return types. Use PEP 695 syntax (`class Batch[T]:`) when the minimum Python
  version is 3.12 or later; otherwise use `TypeVar`.
- Prefer structural subtyping with `Protocol` over nominal inheritance for
  interchangeable behavior such as strategies, adapters, observers, and
  repositories.
- Use `@runtime_checkable` only at API boundaries or other high-stakes
  interfaces. It checks member presence, not signatures or behavior.

### Boundaries and Domain Models

Custom types SHOULD be dataclasses or Pydantic models.

- Use Pydantic models to parse, validate, and serialize untrusted boundary data
  such as API payloads, settings, messages, and external records.
- Use dataclasses for internal domain state and behavior.
- Domain models MUST NOT depend on FastAPI, database clients, HTTP clients, or
  other infrastructure frameworks.
- Pydantic model attributes MUST use `Annotated[T, Field(...)]` with a
  description explaining what the value means and how it relates to its owner,
  not merely restating the field name.
- Dataclasses nested in Pydantic models SHOULD use the same pattern so the
  owner's schema is complete. Dataclasses without runtime schema consumers MAY
  omit `Field` metadata.
- `Field` constraints on a dataclass are enforced only when validated through a
  Pydantic owner such as `Owner.model_validate(...)`, not by the dataclass
  constructor.
- `Field` constraints MUST hold for every construction path. Pydantic logic
  SHOULD be limited to type coercion and structural validation; domain mapping
  and business rules belong in explicit `from_*` factories or boundary
  converters.

```python
class CollectionRequest(BaseModel):
    """Untrusted input for creating a collection."""

    model_config = ConfigDict(frozen=True)

    collection_id: Annotated[
        CollectionId,
        Field(gt=0, description="Identity of the new collection."),
    ]
    document_ids: Annotated[
        tuple[DocumentId, ...],
        Field(description="Documents to include as entries in this collection."),
    ]
```

### Immutability

Value objects SHOULD be immutable. Dataclass value objects SHOULD normally use:

```python
@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: Currency
```

Pydantic value models SHOULD normally use `ConfigDict(frozen=True)`. Mutable
entities are acceptable when mutation represents a controlled domain operation
and invariants remain encapsulated.

Mutable collections MUST NOT be unintentionally shared between instances. Copy
or convert caller-owned collections when an object takes ownership of them.

Use `model_copy` to derive new Pydantic instances rather than reimplementing
copying. `model_copy(update=...)` does not validate the updated values; use
`model_validate` when those values are untrusted.

### Construction

- The default constructor SHOULD remain predictable and free of I/O.
- Use a named `@classmethod` beginning with `from_` when construction requires
  parsing, conversion, multi-step derivation, or a distinct source format.
  Factories SHOULD return `Self`.
- Stable domain defaults MAY be declared on fields. Environment-dependent,
  time-dependent, or surprising defaults belong in explicit factories.
- `__post_init__` MAY enforce local dataclass invariants. Complex parsing and
  orchestration SHOULD use a named factory or application service.
- When nested types require factory construction, outer factories MUST call the
  inner factories explicitly. An outer constructor does not run them.
- Conversions between types SHOULD be factories on the target type, so only that
  type depends on its own construction details.
- Validation shared by several factories SHOULD live in one helper classmethod.

### Validation Placement

Validation MUST occur at the lowest layer that owns the relevant invariant.

| Rule | Location |
| --- | --- |
| Dataclass construction invariant | `from_*` factory or shared helper |
| Pydantic invariant true for every construction path | `Field(...)` constraint |
| Reusable check on an annotated type | `AfterValidator` or `BeforeValidator` |
| Custom rule on one Pydantic field | `field_validator` |
| Rule across several Pydantic fields | `model_validator(mode="after")` returning `Self` |
| Domain mapping or business rule | `from_*` factory or boundary converter |

### Serialization

- Custom conversions MUST use `to_*` for serialization and `from_*` for
  deserialization.
- Conversions of composite types MUST delegate to the conversions of nested
  types.
- Dataclasses that need serialization MUST expose explicit `to_*` and `from_*`
  methods, even when `to_*` only wraps `dataclasses.asdict`, because the standard
  library has no recursive inverse.
- Pydantic models SHOULD rely on `model_dump`, `model_dump_json`,
  `model_validate`, and `model_json_schema`. Use `Field(alias=...)` for naming
  differences and custom methods only for genuinely complex mappings.
- Use `computed_field` to include values derived from existing fields.
- Use `AliasChoices` sparingly for a small, known set of input variants. Do not
  use it to absorb arbitrary inconsistency.

### Collections

Use built-in typed collections by default. Create a domain collection type when
it constructs many elements through their factories, enforces collection-level
invariants, or provides behavior meaningful only for that collection.

- Immutable sequences SHOULD subclass `tuple[T, ...]`. Add `from_*` factories and
  domain methods, but MUST NOT override existing methods, especially
  constructors.
- Mutable collections SHOULD use `collections.UserList` or `UserDict` rather than
  subclassing `list` or `dict`.
- Use a frozen dataclass wrapper when the collection needs a different interface
  or must be returned as a single root object.
- Boundary collections needing schema, validation, or serialization SHOULD use
  `RootModel[list[T]]` or `RootModel[dict[K, V]]` and access values through
  `self.root`. Enforce collection-level invariants with
  `model_validator(mode="after")` returning `Self`.

```python
class Measurements(tuple[Measurement, ...]):
    """Measurements supporting summary operations."""

    @classmethod
    def from_values(cls, values: Iterable[float]) -> Self:
        """Build measurements from raw values."""
        return cls(Measurement.from_value(value) for value in values)

    def mean(self) -> float:
        """Return the mean measurement value.

        Raises:
            EmptyMeasurementsError: No measurements are present.
        """
        if not self:
            raise EmptyMeasurementsError("Cannot average zero measurements.")
        return sum(item.value for item in self) / len(self)
```

## Error Handling

- Errors MUST NOT pass silently.
- Invalid input MUST be rejected with a specific error. Do not automatically
  repair it, substitute defaults, or guess the intended value.
- Raise specific exceptions at the lowest layer that detects a problem; handle
  them at the highest layer that can respond meaningfully.
- Catch only exceptions that the current layer can handle, enrich, translate, or
  clean up after.
- Preserve the original cause when translating errors with `raise ... from error`.
- Custom exceptions SHOULD represent stable failure categories callers can act on
  or add meaningful domain context. Do not create one class per error message.
- Organize custom exceptions under a package- or domain-level base class so
  callers can handle a whole failure family.
- Broad `except Exception` handlers MAY be used at process boundaries for logging,
  cleanup, or protocol translation, but they MUST re-raise or return an explicit
  failure response.
- Use direct dictionary indexing for required keys. Handle optional keys explicitly
  or validate the entire payload with a boundary model.
- User-facing errors MUST avoid leaking secrets or sensitive internal details.

## Architecture

### Layering

Larger applications SHOULD separate these responsibilities:

- **Domain:** business concepts, invariants, and policies.
- **Application:** use-case orchestration and transaction boundaries.
- **Infrastructure:** databases, external APIs, queues, files, and implementations.
- **Interface:** HTTP, CLI, scheduled jobs, and message handlers.

Dependencies point inward: domain code knows nothing about outer layers, and
application code depends on infrastructure through narrow interfaces where
substitution provides real value.

Use `Protocol` for meaningful dependency boundaries, interchangeable strategies,
and test seams. Do not create an interface for every class by default.

Prefer composition over inheritance, even when it produces more structured data.
Organize modules around cohesive domain concepts with low coupling rather than
around technical categories alone.

### Domain-Driven Design

DDD patterns SHOULD be used when the domain has substantial rules, language, and
state transitions. They are optional for small utilities and simple CRUD services.

When DDD is used:

- Entities have identity and lifecycle.
- Value objects are defined by immutable values, and their operations are
  side-effect-free.
- Aggregate roots protect consistency within an aggregate boundary. External
  code holds references only to the root, never to interior objects.
- Factories assemble complex aggregates or large value objects and enforce
  creation invariants.
- Repositories expose aggregate roots rather than persistence records, presenting
  a collection-like interface that hides storage technology.
- Domain services hold rules that do not naturally belong to an entity or value
  object.
- Domain events are immutable records of significant completed domain actions.

Entities and value objects MAY be reused across layers, for example as parts of
API responses, when this avoids near-duplicate types. Use separate boundary types
when contracts differ, private or infrastructure details would leak, or reuse
would introduce forbidden dependencies.

Consistency within an aggregate SHOULD be synchronous. Cross-aggregate work MAY
be asynchronous when eventual consistency is acceptable; it is not a universal
requirement.

Architecture SHOULD be introduced in response to demonstrated complexity, not in
anticipation of every possible future need.

## Web APIs

FastAPI is the preferred Python framework for HTTP APIs unless repository needs
justify another choice.

- Request and response contracts MUST use explicit Pydantic models. They SHOULD
  reuse domain or application types where the contracts genuinely align.
- Route handlers SHOULD translate transport concerns and delegate business work.
- Business logic MUST NOT be embedded in dependency functions or middleware.
- Use dependency injection for settings, authentication context, and replaceable
  service dependencies.
- Middleware SHOULD be reserved for genuinely cross-cutting HTTP concerns.
- Async functions SHOULD be used for asynchronous I/O, not automatically for all
  code.
- Public API changes MUST consider compatibility, versioning, and migration.

If a graphical interface is required, build the API first and have an HTML UI
call its endpoints asynchronously rather than duplicating business logic. MCP
servers SHOULD use FastMCP and reuse the same application use cases.

## Data and Persistence

- Prefer typed records or domain objects for ordinary application data.
- Use Polars rather than Pandas for new dataframe workloads unless compatibility
  or ecosystem constraints justify Pandas.
- Use `pathlib` for filesystem work: `Path.glob` or `Path.rglob` instead of
  `os.walk`, and `Path.open` instead of the built-in `open`.
- SQLAlchemy Core is preferred for SQL access. An ORM MAY be used when its unit-of-
  work and relationship model materially simplify the application.
- PyMongo is preferred for direct MongoDB access, with documents represented by
  custom types. Object-document mappers such as Beanie require a documented
  benefit.
- Database migrations MUST be reviewed, reversible where practical, and tested
  against representative data.
- Persistence models MUST NOT leak into the domain when doing so couples business
  rules to storage details.

## Testing

- New behavior and bug fixes MUST include tests at the lowest useful level.
- Tests MUST be deterministic and independent of execution order.
- Unit tests SHOULD cover domain rules without network, database, or filesystem
  dependencies.
- Integration tests SHOULD cover boundaries such as databases, APIs, queues, and
  settings loading.
- Contract tests SHOULD be used for important external integrations.
- Tests MUST cover failure paths and invalid configuration, not only successful
  examples.
- Time, randomness, identity, and external I/O SHOULD be injected when control is
  needed for deterministic testing.
- Coverage is a diagnostic, not the objective. Repositories MAY set a threshold,
  but assertions must verify meaningful behavior.

## Security and Observability

- Secrets, credentials, tokens, and personal data MUST NOT be logged.
- Authentication and authorization checks MUST default to denial.
- Development bypasses MUST be explicit, documented, tested, and impossible to
  enable in staging or production.
- Logs SHOULD be structured and include useful request, job, or correlation
  identifiers where available.
- Expected operational failures SHOULD be logged once at the layer responsible
  for handling them.
- Network calls MUST define timeouts. Retries MUST be bounded and used only for
  operations that are safe to repeat.
- Services SHOULD expose health and readiness information appropriate to their
  runtime environment.

## Dependencies and Package Choices

Preferred packages are defaults, not permanent prohibitions:

- Package and environment management: UV.
- Formatting and linting: Ruff.
- Static type checking: Pyright/Pylance.
- Testing: Pytest.
- Task automation: Just.
- Settings: pydantic-settings.
- HTTP APIs: FastAPI.
- Dataframes: Polars.
- AI agents: pydantic-ai.
- Google-specific features such as grounded web search: Google Gen AI SDK
  (`google-genai`, imported as `from google import genai`).
- SQL: SQLAlchemy Core.
- MongoDB: PyMongo.
- MCP servers: FastMCP.

New dependencies SHOULD have active maintenance, acceptable licensing, compatible
Python support, and a clear advantage over the standard library or existing
dependencies. Significant deviations from preferred packages SHOULD be recorded
in an Architecture Decision Record.

## Automation and Enforcement

CI MUST run the repository's supported checks on every proposed change. Standards
that can be checked mechanically SHOULD be encoded in Ruff, Pyright, Pytest,
dependency scanning, or repository scripts.

The default branch SHOULD be protected from changes that fail required checks.
Automated dependency updates and security scanning SHOULD be enabled where the
hosting platform supports them.

## Exceptions and Governance

This guide is a maintained team standard, not an immutable rulebook.

- Exceptions MUST state the rule, reason, scope, owner, and intended review date.
- Repository-wide exceptions SHOULD be documented in an Architecture Decision
  Record or the repository's contribution guide.
- Local exceptions SHOULD be narrow and linked to an issue when follow-up is
  expected.
- The team SHOULD review this guide periodically and remove rules that cannot be
  explained, enforced, or shown to improve outcomes.

## Definition of Done

A change is complete when, as applicable:

- Behavior is implemented and tested, including relevant failure paths.
- Formatting, linting, type checking, and tests pass.
- Public interfaces and configuration remain typed and validated.
- `.env.example` and setup documentation reflect configuration changes.
- API, architecture, operational, and migration documentation is current.
- No secrets or insecure development settings are introduced.
- Compatibility and deployment consequences have been considered.

## Coding Assistant Instructions

Coding assistants MUST read this guide once at the beginning of each new coding
session. After that initial read, they SHOULD revisit only the sections relevant
to the current task. The guide may remain comprehensive because it is a durable
reference rather than an instruction repeated in every interaction.

Keep the always-on instructions short. The team version lives in
`.github/copilot-instructions.md` and MUST be updated whenever a change here
affects one of its rules.