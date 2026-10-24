This is exactly the right instinct. Building a single generic wrapper for cursor pagination perfectly aligns with the architectural guidelines you established, specifically the mandates to use modern Python generics (`MyClass[T]`) and to enforce strict compositional typing.

Using a generic collection type eliminates the need to write boilerplate `UserPaginationResponse`, `ArticlePaginationResponse`, and `CommentPaginationResponse` classes, while still providing OpenAPI with the exact schema for the nested models.

Here is how you can implement this utilizing Pydantic's native support for Python 3.12 generics, strict immutability, and factory-driven instantiation.

### The Generic Pagination Model

```python
import typing
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

class ImmutableBaseModel(BaseModel):
    """Base model enforcing strict immutability."""
    model_config = ConfigDict(frozen=True)

# Utilizing Python 3.12 generic syntax as requested
class CursorPaginated[T](ImmutableBaseModel):
    """
    A generic wrapper for cursor-based pagination.
    Pass the specific Pydantic model as the type parameter (e.g., CursorPaginated[UserResponse]).
    """
    data: Annotated[list[T], Field(description="The requested page of resources.")]
    next_cursor: Annotated[str | None, Field(description="Opaque pointer to the start of the next page. Null if no more pages exist.")]
    has_more: Annotated[bool, Field(description="Indicates whether additional pages exist beyond the current one.")]

    @classmethod
    def from_page(cls, items: list[T], next_cursor: str | None) -> typing.Self:
        """
        Static factory method for instantiating the paginated response.
        Calculates `has_more` automatically based on the presence of a cursor.
        """
        return cls(
            data=items,
            next_cursor=next_cursor,
            has_more=next_cursor is not None
        )

```

### Implementing in the API

When you use this in an endpoint, FastAPI and Pydantic automatically inspect the generic type argument (`ArticleResponse` or `UserResponse`). This ensures that the generated OpenAPI specification correctly documents the exact schema of the items inside the `data` array.

```python
from fastapi import APIRouter, Query
from typing import Annotated
# Assuming ArticleResponse and UserResponse are defined elsewhere

router = APIRouter(prefix="/v1")

@router.get("/articles", response_model=CursorPaginated[ArticleResponse])
async def list_articles(
    cursor: Annotated[str | None, Query(description="Pagination cursor")] = None,
    limit: Annotated[int, Query(le=100)] = 50
) -> CursorPaginated[ArticleResponse]:
    
    # ... database logic returning a list of ArticleResponse objects and a new cursor ...
    articles = [ArticleResponse(...), ArticleResponse(...)]
    next_cursor = "encoded_cursor_string"
    
    return CursorPaginated[ArticleResponse].from_page(
        items=articles, 
        next_cursor=next_cursor
    )

@router.get("/users", response_model=CursorPaginated[UserResponse])
async def list_users(
    cursor: Annotated[str | None, Query(description="Pagination cursor")] = None,
    limit: Annotated[int, Query(le=100)] = 50
) -> CursorPaginated[UserResponse]:
    
    # ... database logic returning a list of UserResponse objects ...
    users = [UserResponse(...)]
    
    return CursorPaginated[UserResponse].from_page(
        items=users, 
        next_cursor=None # No more pages
    )

```

### Why this architecture wins:

1. **Type Safety:** Static analysis tools (like MyPy/Pyright) will flag an error if your database service tries to pack a `list[UserResponse]` into a `CursorPaginated[ArticleResponse]`.
2. **OpenAPI Integrity:** FastAPI resolves `T` at runtime, meaning your Swagger UI will correctly display the distinct fields for an Article vs. a User under the `data` attribute.
3. **Encapsulation:** The logic for determining `has_more` lives in one central factory method rather than being duplicated across dozens of endpoints.