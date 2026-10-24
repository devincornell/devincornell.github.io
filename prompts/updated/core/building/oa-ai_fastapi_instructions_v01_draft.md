# FastAPI Best Practices & Architectural Guide

**Version 2.0 | Reviewed October 2, 2026**

## Purpose and scope

This guide establishes conventions for designing, implementing, documenting, and evaluating FastAPI applications. Its priorities are explicit API contracts, meaningful types, immutable data, clear resource relationships, predictable HTTP behavior, and testable application boundaries.

Use standard FastAPI and Pydantic mechanisms rather than creating a custom framework around them. The mandatory `Annotated` documentation convention, immutable-by-default data models, and rejection of unknown request fields are project standards adopted by this guide; they are not requirements imposed by FastAPI itself.

Examples use Pydantic v2 and Python 3.11-compatible syntax unless noted. Pin and test the project's supported dependency versions. Query parameter models require a FastAPI version that supports that feature; verify version-sensitive features such as dependency cleanup scopes against the project's installed version.[^query-models][^yield]

The User and Workspace examples illustrate one coherent resource model: a Workspace has exactly one owning User, and a User can own multiple Workspaces. These are example business rules, not framework behavior. Replace them with the actual rules of the application.

---

## 1. Mandatory attribute annotations and documentation

### 1.1 Every model field must use `Annotated`

Every Pydantic data field must declare its type and a meaningful description using:

```python
attribute: Annotated[SomeType, Field(description="...")]
```

This applies to request, response, nested, query, header, cookie, error, collection, and settings models, including a `RootModel`'s `root` field. There is no exemption for fields whose names appear obvious. Configuration attributes such as `model_config` are not data fields.

Keep the description on the field declaration even when its type is a reusable alias. The alias explains the kind of value; the field description explains that value's role in this particular contract. Pydantic supports `Annotated` metadata and uses field descriptions and other schema metadata in generated JSON Schema.[^fields][^json-schema]

Ordinary defaults belong outside `Annotated`:

```python
limit: Annotated[
    int,
    Field(
        ge=1,
        le=100,
        description="Maximum number of matching workspaces returned in this page.",
    ),
] = 50
```

When a default factory or constructor alias needs assignment-form `Field(...)` for static type-checker support, retain the documented `Annotated` type and put that additional configuration on the assignment. Do not discard the documentation convention to accommodate tooling.[^fields]

### 1.2 Descriptions must explain meaning, not repeat names

A description must explain what the value represents and what the consumer can do with it. Include the following information where applicable:

| Concern | Required documentation |
|---|---|
| Meaning and constraints | Business meaning, units, valid range, format, normalization, and whether the value is generated or supplied. Encode enforceable constraints in types or validators as well. |
| Presence and nullability | Whether the field is required, what omission means, what `null` means, and what default applies. |
| Resource relationships | The referenced resource and field, the relationship's purpose and cardinality, and the operation used to retrieve or traverse it. |
| Collections and calculations | Which resources qualify, authorization filtering, ordering, pagination boundaries, and whether a count describes a page or the full filtered result. |
| Lifecycle and permissions | Whether a field can change, how deletion affects the relationship, and any distinction between ownership, membership, and permission. |

For example, "Owner ID" is insufficient. A useful description is:

> ID of the User that owns this Workspace; matches UserResponse.id. Retrieve that User with GET /users/{owner_id}, subject to authorization. Each Workspace has one owner; a User may own multiple Workspaces. This field does not enumerate other users who can access the Workspace.

Do not assert guarantees that the implementation does not enforce. An email-format validator is not proof that the address belongs to the user. A well-formed resource ID is not proof that the resource exists or that the caller can access it.

### 1.3 Models and endpoints must explain their place in the resource model

Every schema class must have a docstring explaining its purpose: a resource representation, a creation request, a partial update, a filter, or a collection envelope. State important relationships and distinctions from other representations.

Every operation must explain what resource it acts on, the relevant ownership or parent-child relationship, meaningful side effects, authorization expectations, and expected failures. Readers should understand the API from its generated documentation without reading service or persistence code.

A description of a relationship does not create a machine-readable OpenAPI link or enforce a database foreign key. Add OpenAPI link metadata where supported and useful, and enforce relational rules in the application and database. Documentation, schema validation, authorization, and referential integrity are separate responsibilities.

---

## 2. Strong typing and immutable model configuration

### 2.1 Model structured API data precisely

Use Pydantic models for JSON objects with a known structure. Nested objects must also have explicit schemas. Type scalar parameters and homogeneous collections directly when that accurately represents the contract; do not add wrappers with no semantic purpose.

Unparameterized `dict`, `list`, and boundary-level `Any` are prohibited as substitutes for a known contract. Dynamic JSON is permitted only when it is genuinely part of the contract. For example, an intentionally extensible metadata field may use `Annotated[dict[str, JsonValue], Field(description="...")]`; document permitted uses and size limits. This is an explicit mutable-data exception, not a deeply immutable structure.

Dictionaries produced temporarily for serialization or controlled model reconstruction are implementation details, not an exemption from defining the public schema.

### 2.2 Do not create configuration-only base classes

Inherit directly from `BaseModel` unless a parent represents a genuine reusable contract. Do not introduce an `ImmutableModel` superclass solely to hold configuration.

Set `model_config = ConfigDict(...)` on each model. Small shared configuration constants are also acceptable; treat them as fixed configuration and do not mutate them at runtime.

```python
from typing import Annotated, NewType

from pydantic import BaseModel, ConfigDict, EmailStr, Field

UserId = NewType("UserId", int)
WorkspaceId = NewType("WorkspaceId", int)

REQUEST_MODEL_CONFIG = ConfigDict(
    frozen=True,
    extra="forbid",
    validate_default=True,
)

RESPONSE_MODEL_CONFIG = ConfigDict(
    frozen=True,
    validate_default=True,
)


class UserResponse(BaseModel):
    """Client-facing User resource, subject to the operation's access policy."""

    model_config = RESPONSE_MODEL_CONFIG

    id: Annotated[
        UserId,
        Field(
            gt=0,
            description=(
                "Stable, server-generated User identifier. Referenced by "
                "WorkspaceResponse.owner_id. Retrieve with GET /users/{id}."
            ),
        ),
    ]
    username: Annotated[
        str,
        Field(
            min_length=3,
            max_length=64,
            description=(
                "User-chosen account handle. Use id, rather than this handle, "
                "when referring to the User from another resource."
            ),
        ),
    ]
    email: Annotated[
        EmailStr,
        Field(
            description=(
                "Contact email address associated with this User. Valid email "
                "syntax does not imply that ownership has been verified."
            ),
        ),
    ]


class WorkspaceResponse(BaseModel):
    """Workspace resource owned by one User; a User can own many Workspaces."""

    model_config = RESPONSE_MODEL_CONFIG

    id: Annotated[
        WorkspaceId,
        Field(
            gt=0,
            description=(
                "Stable, server-generated Workspace identifier. "
                "Retrieve with GET /workspaces/{id}."
            ),
        ),
    ]
    owner_id: Annotated[
        UserId,
        Field(
            gt=0,
            description=(
                "ID of the User that owns this Workspace; matches "
                "UserResponse.id. Retrieve with GET /users/{owner_id}, "
                "subject to authorization. Each Workspace has one owner; "
                "a User can own many. This is not a list of all users "
                "permitted to access the Workspace."
            ),
        ),
    ]
    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description=(
                "Human-readable Workspace name. It is not the resource "
                "identifier; use id for lookups and relationships."
            ),
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            max_length=2000,
            description=(
                "Optional explanatory text about the Workspace. This response "
                "field is always present; null means no description is set."
            ),
        ),
    ]
```

Input and output configuration need not be identical. Reject unknown structured request fields by default. For response models, choose extra-field handling deliberately; the declared public fields, rather than the internal object's entire attribute set, define the response contract.[^models][^response-model]

### 2.3 Immutability includes nested values

Treat data containers as immutable. Use `frozen=True` for Pydantic data models and prefer `tuple[T, ...]` and `frozenset[T]` over mutable lists and sets. Nested models must follow the same policy. Use a tuple when order matters; do not use a set-like type for ordered API results.

Pydantic freezing prevents normal field reassignment, but does not recursively freeze contained objects. A frozen model containing a list or dictionary still contains mutable state. A read-only annotation such as `Mapping` also does not, by itself, make its backing object immutable.[^models][^typing]

Immutable tuples can still serialize as JSON arrays. The Python representation and the JSON wire format need not use identical container types.[^serialization]

This policy concerns data and value objects. Database sessions, network clients, caches, and other operational resources have lifecycles and mutable state; do not force them into frozen Pydantic models.

### 2.4 New values must preserve validation

Construct a new validated object when changing data. Prefer an explicit constructor for small models:

```python
updated_workspace = WorkspaceResponse(
    id=current_workspace.id,
    owner_id=current_workspace.owner_id,
    name=replacement_name,
    description=current_workspace.description,
)
```

`model_copy(update=...)` does **not** validate the update values. Use it only for trusted updates whose field types and cross-field invariants are already guaranteed. `deep=True` changes copying behavior; it does not add validation or deep immutability.[^base-model]

For straightforward schemas, merging a controlled field mapping and calling `model_validate()` is another option. Do not assume a generic dump-and-revalidate helper works for every model: aliases, excluded fields, custom serializers, and context-dependent validation require deliberate handling.

---

## 3. Semantic types, constraints, and validation

### 3.1 Distinguish aliases from nominal types

Use aliases to improve readability and reuse constraints. Use `NewType` when a static type checker should distinguish otherwise identical primitive representations, such as `UserId` and `WorkspaceId`.

A plain alias such as `type UserId = int` on Python 3.12+ does not create that distinction. `NewType` supplies a static distinction, not a new runtime validation rule: a positive-ID constraint still belongs in `Field(gt=0)` or a reusable constrained annotation.[^typing]

Choose types that express the actual domain: `Enum` or `Literal` for closed choices; `UUID` for UUID identifiers; appropriate date/time types; `Decimal` when decimal arithmetic is required; and validated string types where appropriate. Document timezone, precision, rounding, normalization, and wire representation rather than leaving clients to guess.

When multiple payload shapes represent distinct variants, prefer a discriminated union with a documented discriminator instead of a permissive union of loosely overlapping objects.[^unions]

### 3.2 Reject unknown request fields deliberately

Use `extra="forbid"` on structured request and query models unless an extensibility requirement explicitly justifies another policy. Typos and unsupported fields must not disappear silently. Pydantic otherwise ignores extra fields by default.[^config]

Apply this to client-controlled structures, not indiscriminately to the complete HTTP header set: browsers and proxies legitimately add unrelated headers. Define header-model policies accordingly.

### 3.3 Choose coercion intentionally

Do not globally enable strict validation without considering the transport. Path and query values arrive through textual HTTP representations. Accept conversions that are part of the documented wire contract, and use field-level strictness when another input type would conceal an error.

For example, a JSON boolean flag can require an actual boolean:

```python
enabled: Annotated[
    bool,
    Field(
        strict=True,
        description="Whether this configuration is enabled; send a JSON boolean.",
    ),
]
```

Pydantic strict behavior depends on the type and validation entry point. Test actual HTTP requests, not just direct model construction, before claiming that a schema accepts or rejects a particular representation.[^strict]

### 3.4 Keep validation pure and appropriately placed

Use `Field` constraints for structural rules, `field_validator` for field-specific transformations or checks, and `model_validator` for cross-field invariants.[^validators]

Validators must not query databases, call external services, or perform authorization. Put resource existence, access checks, and transactional business rules in the application/service layer. Enforce uniqueness and referential integrity in the database as well; a prior application lookup is not a concurrency-safe substitute.

Enable default-value validation where defaults must satisfy the same contract as supplied values. This guide's shared configurations enable it explicitly.[^config]

---

## 4. Construction, mapping, and schema evolution

### 4.1 Use standard Pydantic construction

Do not override `BaseModel.__init__` in project models. This is a project simplification, not a claim that Pydantic cannot support customized initialization.

Use normal construction or `model_validate()` for routine validation. For compatible domain or persistence objects, `model_validate(source, from_attributes=True)` can read named attributes; alternatively configure `from_attributes=True` on the relevant model.[^models]

Introduce a named conversion method such as `from_domain()` only when it expresses a meaningful transformation. Such methods should normally be `@classmethod` methods returning `Self`, not mandatory wrappers around every constructor. Keep them free of I/O and business side effects.

Do not use `model_construct()` to bypass validation of untrusted input. Avoid manual `model_dump()` or JSON serialization in ordinary JSON endpoints; return the declared response model and let FastAPI perform its response processing.[^base-model][^response-model]

### 4.2 Separate independently evolving representations

Use distinct request, response, and partial-update schemas when their responsibilities differ. Client requests must not gain permission to submit server-owned fields merely because those fields appear in a response.

For example, a creation request can derive ownership from the authenticated caller:

```python
class CreateWorkspaceRequest(BaseModel):
    """Create a Workspace owned by the authenticated User; id and owner_id are server-set."""

    model_config = REQUEST_MODEL_CONFIG

    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Initial Workspace name; returned as WorkspaceResponse.name.",
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            max_length=2000,
            description=(
                "Initial Workspace description. Omission or null creates "
                "the Workspace without a description."
            ),
        ),
    ] = None
```

Use schema inheritance only when the parent represents a stable conceptual contract. Do not couple create and response schemas just to eliminate several duplicate declarations. Reusable semantic types, composition, and small amounts of duplication are often clearer.

The public schema must not be an ORM model. Returning an ORM object through an explicit response schema can be acceptable, but persistence fields and database migrations must not implicitly redefine the API.

---

## 5. Partial updates and field presence

Define PATCH semantics explicitly. Distinguish omitted fields, explicit `null`, and concrete replacement values. In Pydantic v2, a nullable annotation does not itself make a field optional to supply; a default controls whether omission is accepted.[^fields]

```python
class UpdateWorkspaceRequest(BaseModel):
    """Partially update the Workspace selected by the path; ownership is unchanged."""

    model_config = REQUEST_MODEL_CONFIG

    description: Annotated[
        str | None,
        Field(
            max_length=2000,
            description=(
                "Replacement for WorkspaceResponse.description. Omit to leave "
                "unchanged; send null to clear it; send text to replace it. "
                "This field does not modify Workspace ownership."
            ),
        ),
    ] = None
```

Use `model_fields_set` or `model_dump(exclude_unset=True)` to preserve this distinction. Do not use `exclude_none=True` when explicit null is a meaningful update.[^patch]

```python
unchanged = UpdateWorkspaceRequest()
cleared = UpdateWorkspaceRequest(description=None)

assert unchanged.model_dump(exclude_unset=True) == {}
assert cleared.model_dump(exclude_unset=True) == {"description": None}
```

If a field can be omitted but must not be explicitly null, enforce that separate rule. Do not silently turn an invalid null into "no change." Define nested-update behavior and whether an empty PATCH is accepted.

Apply updates through the service layer, recheck complete-object invariants, and persist transactionally. Replacing an in-memory model is not a database update. For resources at risk of lost updates, adopt a documented revision or conditional-request policy.

---

## 6. Collections, pagination, and related query parameters

A typed collection such as `tuple[UserResponse, ...]` or `list[UserResponse]` can be a complete response contract. A `RootModel` is not mandatory merely because the response is an array. FastAPI supports typed collection responses.[^response-model]

Use an object envelope when pagination or collection metadata is part of the contract:

```python
class WorkspaceListResponse(BaseModel):
    """One ordered page of Workspaces matching the request and visible to the caller."""

    model_config = RESPONSE_MODEL_CONFIG

    items: Annotated[
        tuple[WorkspaceResponse, ...],
        Field(
            description=(
                "Workspaces in this page after authorization and query filtering. "
                "Ordered by the requested sort key, with id as a stable tie-breaker. "
                "An empty array means this page contains no matching resources."
            ),
        ),
    ]
    next_cursor: Annotated[
        str | None,
        Field(
            description=(
                "Opaque continuation token for GET /workspaces. Send as cursor "
                "with the same filters and ordering. Null means there is no "
                "further page in this result traversal."
            ),
        ),
    ]
```

Set a bounded default and maximum page size. Document filtering, ordering, tie-breaking, cursor expiry, and consistency under concurrent changes. Do not promise snapshot consistency unless implemented. If a total is returned, specify whether it is exact or estimated and what it counts; do not require expensive totals unnecessarily.

Group query parameters when they form a coherent concept, not because their count exceeds an arbitrary threshold:

```python
from typing import Literal


class WorkspaceFilters(BaseModel):
    """Filtering, ordering, and pagination for the caller-visible Workspace collection."""

    model_config = REQUEST_MODEL_CONFIG

    owner_id: Annotated[
        UserId | None,
        Field(
            gt=0,
            description=(
                "Restrict results to Workspaces whose owner_id matches this "
                "UserResponse.id. Omission applies no owner filter. This filter "
                "never grants access to otherwise inaccessible Workspaces."
            ),
        ),
    ] = None
    limit: Annotated[
        int,
        Field(ge=1, le=100, description="Maximum Workspaces returned in this page."),
    ] = 50
    cursor: Annotated[
        str | None,
        Field(
            min_length=1,
            description=(
                "WorkspaceListResponse.next_cursor from the preceding page. "
                "Omit for the first page; retain the same filters and ordering."
            ),
        ),
    ] = None
    sort_by: Annotated[
        Literal["id", "name"],
        Field(
            description=(
                "Ascending Workspace sort key. Name sorting uses ascending id "
                "to break ties; keep the same sort key while following cursors."
            ),
        ),
    ] = "id"
```

Bind this model with `Annotated[WorkspaceFilters, Query(description="...")]`. FastAPI extracts and validates the query values and includes them in its API documentation. Cohesive header and cookie models may follow the same principle.[^query-models]

Reserve `RootModel` for a root value that deserves its own named contract, validation, or behavior. Parameterize it and document its root explicitly:

```python
from pydantic import RootModel


class UserCollection(RootModel[tuple[UserResponse, ...]]):
    """A User array without pagination metadata, for operations declaring that shape."""

    model_config = ConfigDict(frozen=True)

    root: Annotated[
        tuple[UserResponse, ...],
        Field(description="User resources included by the operation's documented selection rules."),
    ]
```

This still produces an array on the wire, not an object containing a `root` property.[^root-model]

---

## 7. Endpoint contracts and HTTP behavior

### 7.1 Declare input sources and response contracts

All client-supplied path, query, body, header, cookie, form, and file parameters must have precise types and source-appropriate `Annotated` metadata: `Path`, `Query`, `Body`, `Header`, `Cookie`, `Form`, or `File`, with meaningful descriptions. Framework objects such as `Request` and injected services are not client-data fields.

Every JSON endpoint must have an explicit response contract. Prefer a return annotation when the function actually returns that type. Use `response_model=` when the runtime return type differs from the public representation. Do not lie in the Python annotation merely to obtain the desired documentation. When both are specified, they must be intentionally consistent; FastAPI gives `response_model` precedence.[^response-model]

FastAPI uses the response contract for documentation and response processing, including validation and filtering. Nonetheless, keep secrets out of public schemas and build representations for the authorized audience. Schema filtering is not object-level or field-level authorization.[^response-model][^object-auth]

The following router fragment assumes the project provides the service and authentication dependencies and the error schema described below:

```python
from fastapi import APIRouter, Path

from app.api.dependencies import CurrentUserDep, WorkspaceServiceDep
from app.api.schemas.errors import ErrorResponse

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get(
    "/{workspace_id}",
    summary="Retrieve a workspace",
    operation_id="get_workspace",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Workspace does not exist or is not visible to the caller.",
        },
    },
)
async def get_workspace(
    workspace_id: Annotated[
        WorkspaceId,
        Path(
            gt=0,
            description=(
                "WorkspaceResponse.id of the Workspace to retrieve. "
                "This identifies a Workspace, not its owning User."
            ),
        ),
    ],
    service: WorkspaceServiceDep,
    actor: CurrentUserDep,
) -> WorkspaceResponse:
    """Retrieve one Workspace visible to the authenticated caller.

    The returned owner_id references UserResponse.id. Ownership identifies
    the owning User, not every User permitted to access this Workspace.
    This operation does not modify the Workspace or its ownership.

    This example uses the same 404 response for missing and inaccessible
    Workspaces so that it does not reveal their existence.
    """
    workspace = await service.get_visible(
        workspace_id=workspace_id,
        actor=actor,
    )
    return WorkspaceResponse.model_validate(workspace, from_attributes=True)
```

Declare all applicable documented errors, including authentication and validation responses, through shared router/application metadata where appropriate. Adding `responses` metadata does not implement an exception handler or validate a manually constructed error response.[^additional-responses]

### 7.2 Treat non-JSON responses explicitly

Files, streams, redirects, and empty responses require appropriate response classes, media types, headers, and documentation rather than artificial JSON models. Returning a `Response` directly bypasses FastAPI's normal model conversion and validation; the implementation must perform any required validation and serialization itself.[^direct-response]

For manually constructed `JSONResponse` objects, serialize models with `model_dump(mode="json")` so values such as UUIDs and datetimes become JSON-compatible. Do not pass `model_dump_json()` as JSONResponse content, which would encode an already serialized string rather than the intended object.[^serialization]

### 7.3 Use HTTP semantics intentionally

Use resource-oriented paths, consistent naming, and methods whose behavior matches their HTTP meaning. State idempotency and retry behavior where clients need it. Do not use GET for business-state mutations.

Use `201 Created` when a resource has been created and provide its canonical location when appropriate; `202 Accepted` for accepted work that has not completed; and `204 No Content` only when the response has no body. For long-running work, define a task/status resource rather than implying that acceptance means completion.[^http]

Distinguish authentication failure, authorization failure, missing resources, conflicts, validation errors, and unexpected server failures. A policy of returning 404 for inaccessible resources must be intentional and consistent. Preserve required authentication headers when translating errors.[^http]

For retry-sensitive creates or costly operations, define an idempotency policy, including key scope, expiry, duplicate handling, and behavior when the same key accompanies a different payload. For concurrent edits, define revision checks or conditional requests where warranted. These are contract decisions, not automatic benefits of using FastAPI.

---

## 8. Architecture and dependency direction

Keep HTTP concerns in routers, API schemas, dependency providers, and exception handlers. Put use cases and transaction orchestration in application services. Put business concepts and invariants in domain code. Put database and external-service implementations in infrastructure adapters.

A useful request-processing flow is:

```text
HTTP input
    -> Pydantic request/query model
    -> application service or command
    -> domain logic and persistence/external adapters
    -> application result or domain object
    -> Pydantic response model
    -> HTTP response
```

This describes responsibilities, not a requirement to allocate a different class at every step. Simple CRUD services may use a smaller design. Do not create factories, repository interfaces, or command types that merely rename an existing object without establishing a useful boundary.

Domain and application code must not require `Request`, `Depends`, `HTTPException`, or route declarations. Dependencies are resolved at the HTTP/composition boundary and passed inward as ordinary typed arguments. A framework-independent domain object can be a standard `@dataclass(frozen=True, slots=True)`; Pydantic is not mandatory throughout the application.

API request models must not become the accidental vocabulary of every internal layer. Likewise, database models must not become the public contract. If using repository interfaces, keep those interfaces inward-facing and have infrastructure implementations depend on them, rather than making domain code import concrete database adapters.

A project may organize code by feature or by layer. Either is acceptable when responsibilities and imports remain clear. For example:

```text
app/
    main.py                 # Application factory and composition
    settings.py             # Validated application configuration
    api/
        routes/             # HTTP operations
        schemas/            # Request, response, and error contracts
        dependencies.py     # Authentication and resource/service providers
        handlers.py         # Exception-to-HTTP translation
    application/            # Use cases and transaction orchestration
    domain/                 # Business types, rules, and errors
    infrastructure/         # Database and external-service adapters
tests/
```

---

## 9. Dependency injection, middleware, and request lifetimes

Use `Depends` for request-scoped application concerns: authenticated principals, resource access checks, sessions, request context, and service construction. Use reusable aliases such as `SessionDep`, `CurrentUserDep`, and `WorkspaceServiceDep` rather than repeating dependency declarations throughout routers.[^dependencies]

```python
from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
```

Use middleware for genuinely cross-cutting HTTP behavior, such as correlation IDs, access logging, tracing, CORS, and security headers. Middleware surrounds request/response processing; dependencies provide values and requirements used by request handling. They are complementary mechanisms, not interchangeable alternatives.[^middleware][^dependencies]

Use `yield` dependencies to make acquisition and cleanup explicit. Do not swallow exceptions caught during cleanup. FastAPI supports function- and request-scoped cleanup; choose the lifetime deliberately, particularly when responses stream or serialization needs access to a resource. A function-scoped resource cannot be relied on during subsequent streaming.[^yield]

Do not pass request-scoped sessions or transient resources to work that outlives the request. Background workers must acquire and release their own resources.

---

## 10. Application lifespan, async execution, and external calls

### 10.1 Manage shared resources in lifespan

Use FastAPI's lifespan context manager for application-scoped resources such as database engines/pools, reusable HTTP clients, broker connections, and loaded models. FastAPI recommends lifespan over the older startup/shutdown event handlers. Do not open external connections or perform expensive initialization as a module-import side effect.[^lifespan]

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=3.0),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
        ),
    ) as client:
        app.state.http_client = client
        yield


def get_http_client(request: Request) -> httpx.AsyncClient:
    client = getattr(request.app.state, "http_client", None)
    if not isinstance(client, httpx.AsyncClient):
        raise RuntimeError("HTTP client is not initialized")
    return client


HTTPClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]

app = FastAPI(lifespan=lifespan)
```

The timeout and pool values above are illustrative; load production values from validated settings. Keep dynamic application state behind typed providers. Initialize shared resources per application process; do not assume that in-memory state coordinates multiple workers.

### 10.2 Keep async code nonblocking

Use `async def` with genuinely asynchronous database and network clients. Do not call blocking I/O directly from the event loop. Use synchronous endpoints/dependencies or a deliberate thread-offloading mechanism when a required library is blocking.

FastAPI offloads ordinary `def` endpoints and dependencies that it invokes. It does not automatically offload an arbitrary synchronous helper merely because an async endpoint calls that helper. CPU-intensive work also requires an explicit execution strategy; declaring a function async does not make that work parallel.[^async]

### 10.3 Reuse clients and bound work

Reuse HTTP clients to benefit from connection pooling instead of constructing one for every outbound request. Set finite timeouts, connection limits, and bounded concurrency. Check upstream response status and validate upstream payloads before treating them as trusted application data.[^httpx]

Retry only operations and failures for which retrying is safe. Bound retries and backoff, and account for the overall request deadline. Avoid retrying non-idempotent operations without a deduplication policy. Do not convert all upstream failures into an unrelated 404 or silently return success.

### 10.4 Distinguish small background work from durable jobs

Use FastAPI `BackgroundTasks` only for small, in-process work whose operational requirements fit that mechanism. Use a worker/queue system for durable jobs, expensive processing, independent retries, or work that must survive application-process failure. FastAPI itself distinguishes its lightweight mechanism from larger background-processing tools.[^background]

Document job states, ownership, polling, cancellation, and failure behavior when an API exposes asynchronous jobs.

---

## 11. Transactions and persistence boundaries

Application services must own transaction boundaries. Repositories should not independently commit fragments of a use case that is intended to be atomic. Commit required work before returning a success result; do not defer a critical commit to request cleanup that may occur after the response has been sent.[^yield][^sessions]

Keep transactions short, roll back on failure, and do not hold a database transaction open across slow external calls unless the design explicitly requires it. Enforce uniqueness and foreign-key rules in the database and translate known constraint failures into meaningful application errors.

A SQLAlchemy `Session` is not a concurrent shared resource. Use an appropriate session per thread or async task; an `AsyncSession` must not be shared by concurrent tasks. A shared engine or session factory is different from a shared session.[^sessions][^async-sessions]

Ensure attributes required for response serialization are available before closing the session. Load relationships intentionally rather than triggering hidden database access during serialization. SQLAlchemy's async guidance specifically calls out implicit attribute-access I/O as something to avoid.[^async-sessions]

Use reviewed migrations for schema changes. Do not turn application startup into an uncontrolled production schema-migration mechanism.

---

## 12. Error contracts and exception translation

Raise domain/application exceptions at the layer that understands their meaning. Infrastructure adapters may translate known database or upstream failures into these exceptions. Do not require every low-level exception to become a domain error, and do not translate unexpected programming failures into misleading client errors.

Map expected exceptions to HTTP centrally using FastAPI exception handlers. Use `HTTPException` for HTTP-specific concerns in the API layer or its dependencies; do not make domain code depend on it.[^errors]

Choose one documented application-wide error representation. RFC 9457 Problem Details is a standardized choice for a new shared API contract. An existing, consistently typed JSON envelope is also viable. If adopting Problem Details, implement its actual fields and media type rather than labelling a custom envelope RFC-compliant.[^problem]

The following is a **project-specific JSON envelope**, not an RFC 9457 representation:

```python
class ValidationIssue(BaseModel):
    """One validation failure within the submitted HTTP request."""

    model_config = RESPONSE_MODEL_CONFIG

    location: Annotated[
        tuple[str | int, ...],
        Field(
            description=(
                "Path to the invalid input, starting with its source, such as "
                "body or query. String elements identify fields; integers "
                "identify collection indexes."
            ),
        ),
    ]
    code: Annotated[
        str,
        Field(description="Machine-readable identifier for this validation failure."),
    ]
    message: Annotated[
        str,
        Field(description="Safe explanation of the invalid value and expected constraint."),
    ]


class ErrorResponse(BaseModel):
    """Stable error contract for a failed API operation; not a resource representation."""

    model_config = RESPONSE_MODEL_CONFIG

    code: Annotated[
        str,
        Field(
            description=(
                "Stable application error identifier. Clients must use this "
                "code, rather than parsing message text, for conditional handling."
            ),
        ),
    ]
    message: Annotated[
        str,
        Field(description="Human-readable explanation that does not disclose sensitive internals."),
    ]
    request_id: Annotated[
        str | None,
        Field(
            description=(
                "Correlation identifier for the failed HTTP request, not a "
                "User or Workspace ID. Null when no identifier is available."
            ),
        ),
    ] = None
    issues: Annotated[
        tuple[ValidationIssue, ...],
        Field(description="Specific input-validation failures; empty for errors without field-level issues."),
    ] = ()
```

A handler constructs and serializes the declared error model:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.errors import WorkspaceNotFoundError


@app.exception_handler(WorkspaceNotFoundError)
async def handle_workspace_not_found(
    request: Request,
    exc: WorkspaceNotFoundError,
) -> JSONResponse:
    error = ErrorResponse(
        code="WORKSPACE_NOT_FOUND",
        message="The workspace does not exist or is not accessible.",
    )
    return JSONResponse(
        status_code=404,
        content=error.model_dump(mode="json"),
    )
```

To claim an application-wide contract, cover request validation failures, HTTP exceptions, and unexpected failures as well as domain errors. FastAPI supports overriding its validation and HTTP exception handlers. Update the corresponding OpenAPI responses; changing runtime handling alone is insufficient.[^errors][^additional-responses]

Preserve relevant headers such as authentication challenges. Do not expose stack traces, SQL, credentials, raw request bodies, or sensitive validation inputs. Unexpected failures and invalid server-generated responses are server errors, not evidence that the caller submitted an invalid request.[^errors]

---

## 13. Settings, secrets, and application initialization

Use `pydantic-settings` as the application's configuration boundary. Load configuration into typed settings rather than reading environment variables throughout business code. Instantiate and validate settings during application construction or lifespan startup, before readiness is reported. Defining a settings class alone does not validate the deployment environment.[^settings]

Settings fields must follow the same mandatory `Annotated` and description convention:

```python
from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Validated configuration for one application process; never an API response."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        frozen=True,
        extra="forbid",
        hide_input_in_errors=True,
    )

    database_url: Annotated[
        PostgresDsn,
        Field(
            repr=False,
            description=(
                "PostgreSQL connection URL for application persistence. "
                "May contain credentials; never include it in logs or API output."
            ),
        ),
    ]
    jwt_signing_secret: Annotated[
        SecretStr,
        Field(
            min_length=32,
            description=(
                "Secret for the configured symmetric JWT-signing scheme, "
                "when this application issues tokens. Supply a securely generated "
                "key through secret management, never a client-provided value."
            ),
        ),
    ]
    upstream_timeout_seconds: Annotated[
        float,
        Field(
            gt=0,
            description="Configured timeout in seconds for outbound service calls.",
        ),
    ] = 10.0
```

This is an example for an application that issues symmetric JWTs, not a requirement to introduce JWT issuance. Omit unused settings and use the configuration appropriate to the actual authentication design. A length constraint is not proof of adequate key entropy.

Use local `.env` files for development where appropriate, for example `AppSettings(_env_file=".env")`. In production, use the deployment's approved environment or secret-injection mechanism. Never commit real secrets or return settings models from API endpoints.[^settings]

Secret-aware types and suppressed representations reduce accidental disclosure; they do not make logging arbitrary settings dumps safe. Inject settings into services and provide test-specific settings. Avoid global caches that accidentally retain one test's configuration in another.

---

## 14. Authentication, authorization, and resource isolation

Authentication identifies the caller. Authorization decides whether that caller can perform the requested action on the specific resource. Validate both; accepting a valid ID or authenticated request is not sufficient. OWASP specifically identifies missing object-level authorization checks as an API security risk.[^object-auth]

Perform resource checks on reads, writes, searches, exports, background jobs, and relationship changes. Scope collection queries and counts to the caller's authorized data. Never trust `owner_id`, tenant identifiers, or membership information simply because they came from a validated request model.

When a request links resources, validate the referenced resource, its eligibility for the relationship, and the caller's right to create that relationship. For example, transferring Workspace ownership requires more than checking that the target User ID is positive.

Use established security dependencies and libraries rather than implementing custom authentication parsing throughout endpoints. Document applicable security requirements in OpenAPI. CORS is a browser-access policy, not an authorization mechanism.[^cors]

Constrain request size, upload size, page size, expensive filters, and concurrent work. Apply rate limits or quotas where needed. Treat these limits as part of the API contract and deployment design, not as benefits automatically provided by type annotations.

---

## 15. OpenAPI as a maintained deliverable

The generated specification is part of the product. Each operation must expose a clear summary, stable unique operation identifier, suitable tags, documented parameters, request schemas, response schemas, security requirements, and expected status codes.

Review descriptions at both field and operation level. A field description explains its local meaning; a model description explains the representation; an operation description explains the action and workflow. None replaces the others.

Provide realistic examples where relationships or update semantics are difficult to understand. Example IDs must agree across related resources. Describe alias names as they appear on the wire, not just internal Python names. Keep examples consistent with the validators and actual response serialization.[^json-schema]

Review compatibility deliberately. Renaming fields, changing requiredness or nullability, narrowing accepted values, changing pagination behavior, or changing relationships can affect clients. Even an additive response change should be assessed against the actual consumer ecosystem rather than assumed universally harmless.

Do not rely on runtime response include/exclude options as a substitute for a dedicated public schema when they leave the published contract misleading. Prefer explicit representations for distinct audiences or operations, and review generated input and output schemas rather than assuming they are identical.[^response-model]

Document deprecations and migration paths. Review the OpenAPI diff alongside implementation changes.

---

## 16. Testing, static analysis, and documentation checks

### 16.1 Test at the appropriate boundaries

Use unit tests for pure business rules, integration tests for persistence and external adapters, and HTTP-level tests for API behavior. Override dependencies that touch external systems using `app.dependency_overrides`; avoid relying exclusively on monkey-patching private implementation details. Restore overrides after each test.[^test-overrides]

Endpoint tests must exercise valid requests, malformed requests, unknown fields, bounds, null/omission behavior, errors, permissions, and response shape. Include cross-user or cross-tenant access attempts and accidental exposure of fields that are not in the public schema. Test transaction rollback and failure paths, not only successful responses.

Use `TestClient` as a context manager when lifespan initialization matters. For async HTTPX tests, manage application lifespan explicitly; the client/ASGI transport does not automatically perform that startup/shutdown lifecycle.[^test-lifespan][^test-async]

### 16.2 Enforce the annotation convention automatically

Maintain a registry or discovery mechanism covering every project-owned schema and settings model. Check both the original annotation form and the resolved description. For example, with the models above imported into the test module:

```python
from typing import get_origin, get_type_hints

import pytest

DOCUMENTED_MODELS = (
    UserResponse,
    WorkspaceResponse,
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
    WorkspaceListResponse,
    WorkspaceFilters,
    UserCollection,
    ValidationIssue,
    ErrorResponse,
    AppSettings,
)


@pytest.mark.parametrize("model_type", DOCUMENTED_MODELS)
def test_model_fields_are_annotated_and_documented(
    model_type: type[BaseModel],
) -> None:
    annotations = get_type_hints(model_type, include_extras=True)

    for name, field in model_type.model_fields.items():
        assert get_origin(annotations[name]) is Annotated, (
            f"{model_type.__name__}.{name} must use Annotated"
        )
        assert field.description and field.description.strip(), (
            f"{model_type.__name__}.{name} needs a description"
        )
```

Python's `include_extras=True` preserves `Annotated` metadata for introspection; Pydantic exposes model-field information through the model class.[^typing][^base-model]

This test checks presence, not quality, and only covers registered models. Add an AST/lint check when the exact `Field(description=...)` declaration must be enforced independently of metadata supplied through aliases. Inspect generated OpenAPI too: verify that field and parameter descriptions actually appear where consumers see them.

### 16.3 Review semantics and compatibility, not just syntax

Human review must reject descriptions that merely repeat field names, refer to nonexistent operations, conflate ownership with access, omit relevant null semantics, or promise rules the implementation does not enforce.

Use a consistent formatter/linter, static type checking, and dependency/version checks in continuous integration. Add an OpenAPI contract check or reviewed snapshot/diff, with focused tests for requiredness, bounds, descriptions, status codes, error shapes, and sensitive-field exclusion. A schema snapshot alone does not prove runtime behavior.

---

## 17. Operational readiness and evaluation standard

Use structured logs with request/correlation identifiers and appropriate redaction. Capture latency, failure rates, dependency failures, and resource saturation. Avoid logging request bodies or credentials indiscriminately. Keep unexpected internal details in protected diagnostics, not client error messages.

Separate liveness from readiness. Readiness should reflect whether the application can serve its intended traffic; liveness should not trigger unnecessary restart cascades simply because a downstream service is briefly unavailable. Define startup, shutdown, draining, and request-timeout behavior in the deployment configuration.

Evaluate the implementation against three outcomes:

**A consumer can understand and use the API from its documentation.** Every data field has a documented `Annotated` declaration. Resource references, ownership, collections, field presence, permissions, and lifecycle behavior are understandable. The generated contract agrees with the running API.

**An engineer can change the system without accidental coupling.** HTTP, application, domain, and persistence responsibilities are clear. Types carry meaning. Data is immutable by default. Configuration-only inheritance, mandatory pass-through factories, and unnecessary wrappers do not obscure the design.

**The service behaves predictably under failure and load.** Blocking work does not enter the event loop accidentally. Resources close correctly. Transactions complete before success is reported. Errors are stable and safe. Authorization applies to the actual resources involved. Tests cover these properties, not merely happy-path output.

When a check fails, evaluation feedback must identify the specific field, operation, or component; describe the observed behavior; explain the consumer or operational consequence; and recommend a concrete correction and a test that demonstrates it is fixed.

---

## Reference documentation

These sources describe framework and protocol behavior. The mandatory conventions and evaluation standards above are the policy choices of this guide.

[^fields]: Pydantic, [Fields](https://docs.pydantic.dev/latest/concepts/fields/): Annotated metadata, defaults, requiredness, and static type-checker considerations.
[^json-schema]: Pydantic, [JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/): field/model documentation and generated schemas.
[^models]: Pydantic, [Models](https://docs.pydantic.dev/latest/concepts/models/): construction, attribute-based validation, extra data, and shallow freezing.
[^config]: Pydantic, [Configuration API](https://docs.pydantic.dev/latest/api/config/): frozen models, extra-field policy, and default validation.
[^base-model]: Pydantic, [BaseModel API](https://docs.pydantic.dev/latest/api/base_model/): model_copy, model_construct, serialization, and field introspection.
[^serialization]: Pydantic, [Serialization](https://docs.pydantic.dev/latest/concepts/serialization/): Python versus JSON output and collection serialization.
[^typing]: Python, [typing](https://docs.python.org/3/library/typing.html): aliases, NewType, Annotated, and get_type_hints.
[^strict]: Pydantic, [Strict Mode](https://docs.pydantic.dev/latest/concepts/strict_mode/): strictness by field, model, type, and validation mode.
[^validators]: Pydantic, [Validators](https://docs.pydantic.dev/latest/concepts/validators/): field and model validation mechanisms.
[^unions]: Pydantic, [Unions](https://docs.pydantic.dev/latest/concepts/unions/): discriminated unions and variant validation.
[^root-model]: Pydantic, [RootModel API](https://docs.pydantic.dev/latest/api/root_model/): models whose serialized root is not an ordinary object envelope.
[^query-models]: FastAPI, [Query Parameter Models](https://fastapi.tiangolo.com/tutorial/query-param-models/): grouped query validation and documentation.
[^response-model]: FastAPI, [Response Model - Return Type](https://fastapi.tiangolo.com/tutorial/response-model/): response contracts, filtering, validation, and schema generation.
[^patch]: FastAPI, [Body - Updates](https://fastapi.tiangolo.com/tutorial/body-updates/): partial updates and exclude_unset. Read alongside Pydantic's model_copy validation warning.
[^additional-responses]: FastAPI, [Additional Responses in OpenAPI](https://fastapi.tiangolo.com/advanced/additional-responses/): documented error/status schemas versus runtime handling.
[^direct-response]: FastAPI, [Return a Response Directly](https://fastapi.tiangolo.com/advanced/response-directly/): bypassing automatic response conversion.
[^http]: IETF, [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html): methods, status codes, authentication challenges, and conditional requests.
[^dependencies]: FastAPI, [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/): dependency injection and reusable Annotated declarations.
[^middleware]: FastAPI, [Middleware](https://fastapi.tiangolo.com/tutorial/middleware/): cross-cutting request/response processing.
[^yield]: FastAPI, [Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/): resource cleanup, scopes, and streaming implications.
[^lifespan]: FastAPI, [Lifespan Events](https://fastapi.tiangolo.com/advanced/events/): initialization and shutdown of application resources.
[^async]: FastAPI, [Concurrency and async / await](https://fastapi.tiangolo.com/async/): sync/async execution and threadpool boundaries.
[^httpx]: HTTPX, [Async Support](https://www.python-httpx.org/async/): reusable clients, connection pooling, and async lifecycle.
[^background]: FastAPI, [Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/): lightweight tasks and larger worker-based alternatives.
[^sessions]: SQLAlchemy, [Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html): transaction framing, session lifecycle, and concurrent usage.
[^async-sessions]: SQLAlchemy, [Asynchronous I/O](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html): per-task sessions and avoiding implicit I/O.
[^errors]: FastAPI, [Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/): domain-to-HTTP handlers, validation failures, and HTTP exception overrides.
[^problem]: IETF, [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html): standardized HTTP error representations.
[^settings]: Pydantic, [Settings Management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/): typed environment configuration and settings sources.
[^object-auth]: OWASP, [API1:2023 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/): authorization of individual API resources.
[^cors]: FastAPI, [CORS](https://fastapi.tiangolo.com/tutorial/cors/): browser cross-origin configuration.
[^test-overrides]: FastAPI, [Testing Dependencies with Overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/): replacing dependencies in tests.
[^test-lifespan]: FastAPI, [Testing Events](https://fastapi.tiangolo.com/advanced/testing-events/): triggering lifespan with TestClient.
[^test-async]: FastAPI, [Async Tests](https://fastapi.tiangolo.com/advanced/async-tests/): HTTPX testing and explicit lifespan management.