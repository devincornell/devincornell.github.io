To populate the auto-generated OpenAPI documentation with the specific HTTP errors an endpoint might raise, you must use the `responses` parameter within the FastAPI route decorator.

FastAPI does not automatically inspect your code to see which `HTTPException`s you raise. You have to explicitly declare them so they map to the standardized RFC 9457 Problem Details schema we established earlier.

### 1. Documenting Errors on a Single Endpoint

You can define the expected error schemas directly in the `@router.get()` (or similar) decorator. The `responses` parameter takes a dictionary where the keys are HTTP status codes and the values dictate the OpenAPI schema metadata.

```python
from fastapi import APIRouter, Path
from typing import Annotated
# Assuming RFC9457ProblemDetails and UserResponse are defined

router = APIRouter(prefix="/v1/users")

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        404: {
            "model": RFC9457ProblemDetails,
            "description": "The user was not found."
        },
        422: {
            "model": RFC9457ProblemDetails,
            "description": "Validation failed on the request parameters."
        }
    }
)
async def get_user(
    user_id: Annotated[int, Path(description="The internal system ID.")]
) -> UserResponse:
    # Logic goes here
    pass

```

### 2. Reusable Error Schemas (Architectural Best Practice)

Defining error dictionaries directly on every endpoint quickly clutters the API layer. Because REST APIs rely on predictable errors, the best practice is to define reusable dictionaries of common responses and unpack them (`**`) into the decorator.

```python
from typing import Any

# Define reusable response dictionaries mapping to our standard RFC 9457 schema
STANDARD_ERRORS: dict[int | str, dict[str, Any]] = {
    400: {"model": RFC9457ProblemDetails, "description": "Bad Request - Malformed syntax."},
    401: {"model": RFC9457ProblemDetails, "description": "Unauthorized - Invalid or missing JWT."},
    403: {"model": RFC9457ProblemDetails, "description": "Forbidden - Insufficient OAuth scopes."},
    404: {"model": RFC9457ProblemDetails, "description": "Resource Not Found."},
    409: {"model": RFC9457ProblemDetails, "description": "Conflict - Resource already exists or state mismatch."},
    429: {"model": RFC9457ProblemDetails, "description": "Too Many Requests - Rate limit exceeded."}
}

# You can now selectively unpack these into specific endpoints
@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    responses={
        **{k: STANDARD_ERRORS[k] for k in (400, 401, 403, 409)}
    }
)
async def create_user(payload: UserCreateRequest) -> UserResponse:
    pass

```

### 3. Applying Global Errors to an Entire Router

If certain errors apply to every endpoint within a specific domain (e.g., authentication failures or rate limit errors), you can apply them at the `APIRouter` level. This ensures you never forget to document them on new endpoints.

```python
from fastapi import APIRouter

# All endpoints under this router will automatically inherit the 401, 403, and 429 OpenAPI documentation
users_router = APIRouter(
    prefix="/v1/users",
    tags=["Users"],
    responses={
        401: STANDARD_ERRORS[401],
        403: STANDARD_ERRORS[403],
        429: STANDARD_ERRORS[429],
    }
)

@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    # This endpoint now documents 200 (Success), 401, 403, and 429 automatically.
    pass

```