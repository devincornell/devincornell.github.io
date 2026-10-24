To model resources correctly, an API must adhere to strict naming conventions, limit nesting depth, and explicitly map relationships through strongly typed fields and documentation. Industry consensus dictates that resource nesting must be strictly limited to a maximum of two levels.

The following implementation demonstrates how to properly design independent root resources (Articles) and dependent sub-resources (Comments), using annotations and docstrings to clearly define how the entities relate to one another.

### 1. Resource Schemas with Relationship Mapping

Every field that acts as a foreign key must be explicitly documented so consumers understand how to traverse the API.

```python
import typing
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

type ArticleId = str
type UserId = str
type CommentId = str

class ImmutableBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True)

class CommentResponse(ImmutableBaseModel):
    """
    Representation of a Comment resource.
    
    A comment is strictly contextual and has no semantic meaning without its parent article. 
    The `article_id` field maps directly to an `Article.id`. 
    The `author_id` field maps directly to a `User.id`.
    """
    id: Annotated[CommentId, Field(description="Unique system identifier for the comment.")]
    article_id: Annotated[ArticleId, Field(description="Foreign key mapping to the parent Article this comment belongs to.")]
    author_id: Annotated[UserId, Field(description="Foreign key mapping to the User who authored the comment.")]
    content: Annotated[str, Field(description="The text body of the comment.")]
    created_at: Annotated[datetime, Field(description="Timestamp of when the comment was posted.")]

    @classmethod
    def from_domain(cls, comment_id: str, article_id: str, author_id: str, content: str) -> typing.Self:
        return cls(
            id=comment_id,
            article_id=article_id,
            author_id=author_id,
            content=content,
            created_at=datetime.now()
        )

class CommentCreateRequest(ImmutableBaseModel):
    """
    Payload for creating a new comment.
    Notice that `article_id` is intentionally omitted here because it is inferred from the URI path.
    """
    content: Annotated[str, Field(description="The text body of the comment. Must not be empty.", min_length=1)]

class CommentPatchRequest(ImmutableBaseModel):
    """
    Payload for partially updating an existing comment using JSON Merge Patch semantics.
    """
    content: Annotated[str | None, Field(description="The updated text body. Null indicates no change.", default=None)]

```

### 2. Endpoint Design: Creation and Nesting

Creating a comment inherently binds the new comment to the parent article without requiring the client to explicitly pass the `article_id` inside the JSON body. Therefore, the creation endpoint is nested under the parent article.

```python
from fastapi import APIRouter, Path, Body, Header, Response
from typing import Annotated

router = APIRouter(prefix="/v1", tags=["Comments"])

@router.post(
    "/articles/{article_id}/comments",
    response_model=CommentResponse,
    status_code=201,
    summary="Create a comment on an article"
)
async def create_article_comment(
    response: Response,
    article_id: Annotated[ArticleId, Path(
        description="The unique identifier of the parent Article resource. The created comment will be permanently bound to this ID."
    )],
    payload: Annotated[CommentCreateRequest, Body(
        description="The comment details to be created."
    )],
    idempotency_key: Annotated[str, Header(
        alias="Idempotency-Key",
        description="UUID v4 key to ensure safe retries without duplicating the comment."
    )]
) -> CommentResponse:
    """
    Appends a new Comment resource to the specified Article collection.
    
    **Resource Relationships:**
    This endpoint establishes a one-to-many relationship between the `Article` 
    (identified by the path parameter) and the newly created `Comment`. 
    The authenticated user's ID (injected via authentication dependencies) will 
    be bound as the `author_id`.
    """
    # ... business logic to create the comment ...
    new_comment_id = "cmt_123"
    
    # The server responds with a 201 Created status code and a Location header containing the absolute URI[cite: 1].
    response.headers["Location"] = f"https://api.example.com/v1/comments/{new_comment_id}"
    
    return CommentResponse.from_domain(
        comment_id=new_comment_id,
        article_id=article_id,
        author_id="usr_456",
        content=payload.content
    )

```

### 3. Endpoint Design: Flattened Updates

While creation occurs via a nested route, operations on an individual comment occur at the root level. This prevents deeply nested URIs (like `/articles/{article_id}/comments/{comment_id}`) which force the server to needlessly query the database to validate that the comment actually belongs to the article before executing a simple text update.

```python
@router.patch(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="Update a specific comment"
)
async def update_comment(
    comment_id: Annotated[CommentId, Path(
        description="The globally unique identifier of the Comment resource to modify."
    )],
    payload: Annotated[CommentPatchRequest, Body(
        description="The fields to update using JSON Merge Patch semantics."
    )]
) -> CommentResponse:
    """
    Partially modifies an existing Comment resource.
    
    **Architectural Note:** 
    This endpoint exists at the root `/comments` path rather than being nested under `/articles`. 
    Because `comment_id` is globally unique, the client does not need to know the parent 
    `article_id` to perform modifications. The returned `CommentResponse` will still 
    contain the `article_id` to maintain relationship visibility.
    """
    # ... business logic to update the comment ...
    
    return CommentResponse.from_domain(
        comment_id=comment_id,
        article_id="art_789", # Maintained from the database record
        author_id="usr_456",
        content=payload.content or "Updated content fallback"
    )

@router.delete(
    "/comments/{comment_id}",
    status_code=204,
    summary="Delete a specific comment"
)
async def delete_comment(
    comment_id: Annotated[CommentId, Path(
        description="The globally unique identifier of the Comment resource to delete."
    )]
) -> None:
    """
    Removes the specified Comment resource. 
    
    Subsequent GET requests for this `comment_id` will return a 404 Not Found. 
    This action will also decrement the comment count on the parent Article resource.
    """
    # ... business logic to delete the comment ...
    return None

```