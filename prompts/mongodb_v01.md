
# MongoDB Development Guide: Raw PyMongo with Type Safety

**Starting Premise:** I prefer to use raw pymongo without other layers such as Beanie. I define types to represent each document, and manually create serialization methods to read/write objects to the database.

## Core Architecture Patterns

### 1. Document Models with Pydantic

You define each MongoDB document as a Pydantic model for type safety and validation:

```python
import pydantic
from datetime import datetime
from typing import Optional

class ResearchTaskDoc(pydantic.BaseModel):
    title: str = Field(description="Descriptive title for the research task")
    other_info: str | None = Field(default=None, description="Additional information")
    status: TaskStatus = Field(default=TaskStatus.WORKING, description="Current status")
    started_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    reason: str | None = Field(default=None, description="Reason for failure, if applicable")

class BookDoc(pydantic.BaseModel):
    title: str = Field(description="The full standard title of the book")
    authors: list[str] = Field(description="The authors' names")
    publication_year: int = Field(description="The year the book was published")
    research_output: BookResearchOutput = Field(description="Comprehensive researched information")
    embedding: list[float] = Field(description="Embedding vector representing the book")
```

**Key Benefits:**
- Type safety at compile time
- Automatic validation
- Self-documenting with Field descriptions
- IDE autocompletion support

### 2. Collection Base Class Pattern

Create a base class for all collection operations:

```python
import dataclasses
from typing import Type, TypeVar, Any
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

T = TypeVar('T')

@dataclasses.dataclass
class CollectionBase:
    """Base class for MongoDB collections"""
    _collection: AsyncCollection
    collection_name: str

    @classmethod
    def from_database(cls, db: AsyncDatabase, collection_name: str) -> typing.Self:
        return cls.from_collection(collection=db[collection_name])

    @classmethod
    def from_collection(cls, collection: AsyncCollection) -> typing.Self:
        return cls(_collection=collection, collection_name=collection.name)

    async def create_indexes(self):
        """Override this method in subclasses to define collection indexes"""
        raise NotImplementedError("create_indexes must be implemented by subclass")
```

### 3. Dedicated Collection Classes

Each collection gets its own class inheriting from `CollectionBase`:

```python
class ResearchTaskCollection(CollectionBase):
    """Document model for tracking asynchronous research tasks"""

    async def create_indexes(self):
        '''Create a unique index on title to speed up upserts.'''
        await self._collection.create_index("title", unique=True)

    async def find_task_by_title(self, title: str) -> tuple[ResearchTaskID, ResearchTaskDoc]:
        """Retrieve a research task by its title."""
        return await self.find_task({"title": title})

    async def find_task(self, filter: dict[str, Any]) -> tuple[ResearchTaskID, ResearchTaskDoc]:
        """Find a research task matching the given filter."""
        data = await self._collection.find_one(filter)
        if data is None:
            raise ResearchTaskDoesNotExist(f"Research task matching {filter} does not exist.")
        return str(data["_id"]), ResearchTaskDoc.model_validate(data)

    async def insert_task(self, doc: ResearchTaskDoc) -> str:
        """Insert a new research task document into the collection."""
        try:
            result = await self._collection.insert_one(doc.model_dump())
        except pymongo.errors.DuplicateKeyError:
            raise ResearchTaskAlreadyExists(f"A task with title '{doc.title}' already exists.")
        return result.inserted_id
```

## Manual Serialization Patterns

### Reading from Database (Deserialization)

```python
# Single document
data = await self._collection.find_one(filter)
if data is None:
    raise DocumentNotFound()
return DocumentModel.model_validate(data)

# Multiple documents
cursor = await self._collection.find(filter).to_list()
return [(str(doc["_id"]), DocumentModel.model_validate(doc)) for doc in cursor]

# With aggregation pipeline
pipeline = [{"$match": filter}, {"$project": projection}]
cursor = self._collection.aggregate(pipeline)
results = await cursor.to_list()
return [DocumentModel.model_validate(doc) for doc in results]
```

### Writing to Database (Serialization)

```python
# Insert single document
doc = MyDocumentModel(title="Example", status="active")
result = await self._collection.insert_one(doc.model_dump())
return result.inserted_id

# Update document
update_data = {"status": new_status, "updated_at": datetime.now()}
result = await self._collection.update_one(
    {"_id": document_id}, 
    {"$set": update_data}
)

# Upsert pattern
await self._collection.replace_one(
    filter={"title": doc.title},
    replacement=doc.model_dump(),
    upsert=True
)
```

## Advanced Patterns from Your Code

### 1. Vector Search Integration

```python
async def vector_similarity(self, query_vector: List[float], limit: int = 5) -> list[BookResearchWithSimilarity]:
    '''Perform vector search with MongoDB Atlas vector search.'''
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding", 
                "queryVector": query_vector,
                "numCandidates": limit * 10,
                "limit": limit,
            }
        },
        {
            "$project": BookResearchWithSimilarity.project()
        }
    ]
    return await self.aggregate(pipeline, projection_model=BookResearchWithSimilarity).to_list()

# Companion model with projection method
class BookResearchWithSimilarity(pydantic.BaseModel):
    book: BookDoc = Field(description="The researched book document")
    similarity: float = Field(description="Similarity score from vector search")

    @staticmethod
    def project() -> dict[str, str | int | list[float]]:
        '''Projection definition for MongoDB aggregation to return this model.'''
        return {
            "_id": 0,
            "book": "$research_output.info",
            "similarity": {"$meta": "vectorSearchScore"}
        }
```

### 2. Custom Exception Handling

```python
# Define domain-specific exceptions
class ResearchTaskDoesNotExist(Exception):
    """Custom exception for when a research task is not found in the database."""
    pass

class ResearchTaskAlreadyExists(Exception):
    """Custom exception for when a research task with the same title already exists."""
    pass

# Use in collection methods
async def find_task(self, filter: dict[str, Any]) -> tuple[str, ResearchTaskDoc]:
    data = await self._collection.find_one(filter)
    if data is None:
        raise ResearchTaskDoesNotExist(f"Research task matching {filter} does not exist.")
    return str(data["_id"]), ResearchTaskDoc.model_validate(data)
```

### 3. Manager Pattern for Multi-Collection Operations

```python
@dataclasses.dataclass
class BookManager:
    _db: AsyncDatabase
    _books: BookCollection
    _tasks: ResearchTaskCollection

    @classmethod
    def from_database(cls, db: AsyncDatabase) -> typing.Self:
        return cls(
            _db=db,
            _books=BookCollection.from_database(db, collection_name="books"),
            _tasks=ResearchTaskCollection.from_database(db, collection_name="research_tasks")
        )

    @property
    def books(self) -> BookCollection:
        return self._books
    
    @property 
    def tasks(self) -> ResearchTaskCollection:
        return self._tasks
```

## Database Connection Management

```python
from pymongo import AsyncMongoClient
from typing import Optional

# Module-level singleton pattern
_client: Optional[AsyncMongoClient] = None

async def get_database_client() -> AsyncMongoClient:
    """Get or create the MongoDB client singleton."""
    global _client
    if _client is None:
        _client = AsyncMongoClient(app_settings.MONGODB_URL)
    return _client

async def close_database_connection():
    """Close the MongoDB connection. Call this on app shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None
```

## Best Practices Derived from Your Code

1. **Type Safety First**: Always define Pydantic models before collection classes
2. **Explicit Index Management**: Create dedicated `create_indexes()` methods for each collection
3. **Consistent Error Handling**: Define custom exceptions for domain-specific error scenarios
4. **Return Tuples for ID + Document**: When you need the MongoDB `_id`, return `(id, doc)` tuples
5. **Projection Models**: For complex aggregation queries, create dedicated models with static projection methods
6. **Async Throughout**: Use async/await consistently across all database operations
7. **Manager Pattern**: Coordinate multiple collections through a manager class for complex operations
8. **Singleton Connections**: Reuse database connections via module-level singletons

This approach gives you the control and performance of raw PyMongo while maintaining type safety and clean abstractions through Pydantic models and collection classes.