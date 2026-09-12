# Architectural Guide: Type-Safe MongoDB with Raw PyMongo

This guide details a pattern for implementing a type-safe MongoDB data layer using raw PyMongo and Pydantic. 

The core philosophy of this architecture relies on strict separation of concerns:
1. **Document Types** act purely as data containers with explicit serialization (`to_dict`) and deserialization (`from_dict`) methods.
2. **Collection Types** are dataclasses instantiated via static factory methods. They encapsulate all MongoDB behavior, maintain the connection state, and expose high-level operations using native PyMongo naming conventions (e.g., `find_*`, `insert_*`). 

## 1. Document Models (Data Containers)

Define Pydantic models to represent the data stored in MongoDB. Each model must include custom `to_dict` and `from_dict` methods to handle the precise translation between the application's data representation and MongoDB's storage format.

```python
import pydantic
from datetime import datetime
from typing import Any

class ResearchTaskDoc(pydantic.BaseModel):
    id: str | None = pydantic.Field(default=None, description="Stringified MongoDB _id")
    title: str = pydantic.Field(description="Descriptive title for the research task")
    status: str = pydantic.Field(default="WORKING", description="Current status")
    started_at: datetime = pydantic.Field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the document for MongoDB insertion/updates."""
        return self.model_dump(exclude={"id"}, exclude_none=True)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ResearchTaskDoc":
        """Deserialize a MongoDB dictionary into the document type."""
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        return ResearchTaskDoc.model_validate(data)

class BookDoc(pydantic.BaseModel):
    id: str | None = None
    title: str
    authors: list[str]
    publication_year: int
    embedding: list[float]

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude={"id"})

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "BookDoc":
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        return BookDoc.model_validate(data)
```

## 2. Dedicated Collection Classes (Behavior Encapsulation)

Create a dedicated dataclass for every collection. Use a `@classmethod` factory (like `from_database`) to handle the initialization of the underlying PyMongo `AsyncCollection`. 

Method names must follow native PyMongo conventions to clearly indicate the underlying operation being performed.

```python
import dataclasses
import typing
import pymongo
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

class ResearchTaskDoesNotExist(Exception): pass

@dataclasses.dataclass
class ResearchTaskCollection:
    _collection: AsyncCollection
    collection_name: str

    @classmethod
    def from_database(cls, db: AsyncDatabase, collection_name: str = "research_tasks") -> typing.Self:
        """Factory method to instantiate the collection handler."""
        return cls(
            _collection=db[collection_name],
            collection_name=collection_name
        )

    async def create_indexes(self):
        """Define and build collection indexes."""
        await self._collection.create_index("title", unique=True)

    async def find_one_task(self, filter_query: dict) -> ResearchTaskDoc:
        """Executes a find_one query and returns the deserialized document."""
        data = await self._collection.find_one(filter_query)
        if data is None:
            raise ResearchTaskDoesNotExist(f"No task matches {filter_query}")
            
        return ResearchTaskDoc.from_dict(data)

    async def find_tasks(self, filter_query: dict) -> list[ResearchTaskDoc]:
        """Executes a find query and returns a list of deserialized documents."""
        cursor = await self._collection.find(filter_query).to_list(length=None)
        return [ResearchTaskDoc.from_dict(doc) for doc in cursor]

    async def insert_one_task(self, doc: ResearchTaskDoc) -> str:
        """Executes an insert_one query using the document's serialized dictionary."""
        try:
            result = await self._collection.insert_one(doc.to_dict())
            return str(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            raise ValueError(f"Task '{doc.title}' already exists.")

    async def update_one_task_status(self, task_id: str, new_status: str) -> bool:
        """Executes an update_one query."""
        from bson import ObjectId
        result = await self._collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": new_status}}
        )
        return result.modified_count > 0
```

## 3. Advanced Querying and Projections

For complex aggregations, define specialized data containers to handle the specific projection returned by the pipeline. Maintain the dataclass factory pattern for the collection handling it.

```python
class BookResearchWithSimilarity(pydantic.BaseModel):
    book_title: str
    similarity: float

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "BookResearchWithSimilarity":
        return BookResearchWithSimilarity.model_validate(data)

@dataclasses.dataclass
class BookCollection:
    _collection: AsyncCollection
    collection_name: str

    @classmethod
    def from_database(cls, db: AsyncDatabase, collection_name: str = "books") -> typing.Self:
        return cls(
            _collection=db[collection_name],
            collection_name=collection_name
        )

    async def aggregate_vector_similarity(self, query_vector: list[float], limit: int = 5) -> list[BookResearchWithSimilarity]:
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
                "$project": {
                    "_id": 0,
                    "book_title": "$title",
                    "similarity": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        cursor = self._collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        return [BookResearchWithSimilarity.from_dict(doc) for doc in results]
```

## 4. Multi-Collection Management

Coordinate operations across multiple collections using a Manager dataclass. This centralizes database dependency injection and utilizes the collection factory methods.

```python
@dataclasses.dataclass
class DatabaseManager:
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

## 5. Connection Lifecycle

Manage the `AsyncMongoClient` via a module-level singleton to prevent connection pooling exhaustion.

```python
from pymongo import AsyncMongoClient

_client: AsyncMongoClient | None = None

async def get_database_client(mongodb_url: str) -> AsyncMongoClient:
    global _client
    if _client is None:
        _client = AsyncMongoClient(mongodb_url)
    return _client

async def close_database_connection():
    global _client
    if _client:
        _client.close()
        _client = None
```


## 6. Using in Your Application

To use this in your application, you retrieve the client, select the specific database instance, and pass that database to either your individual collection factories or your `DatabaseManager` factory. 

Because PyMongo's asynchronous client requires an event loop, this initialization must happen within an async context (such as an app startup event or an async main function).

Here is the implementation script demonstrating the complete lifecycle.

### Application Entry Point (`main.py`)

```python
import asyncio
from datetime import datetime

# Assuming the previous classes are imported from your data layer modules:
# from db.connection import get_database_client, close_database_connection
# from db.manager import DatabaseManager
# from db.models import ResearchTaskDoc

async def main():
    # 1. Initialization Phase
    mongodb_url = "mongodb://localhost:27017"
    
    try:
        # Get the singleton client
        client = await get_database_client(mongodb_url)
        
        # Select the specific database
        db = client["my_application_db"]
        
        # Instantiate the manager (which instantiates all collections)
        db_manager = DatabaseManager.from_database(db)
        
        # Optional: Initialize indexes on startup
        await db_manager.tasks.create_indexes()
        # await db_manager.books.create_indexes()

        # 2. Application Logic Phase
        print("--- Executing Database Operations ---")
        
        # Create a document type
        new_task = ResearchTaskDoc(
            title=f"Task generated at {datetime.now().isoformat()}",
            status="WORKING"
        )
        
        # Insert using the encapsulated collection method
        task_id = await db_manager.tasks.insert_one_task(new_task)
        print(f"Inserted Task ID: {task_id}")
        
        # Retrieve and deserialize using the encapsulated collection method
        retrieved_task = await db_manager.tasks.find_one_task({"_id": task_id}) # Or search by title
        print(f"Retrieved Task Type: {type(retrieved_task)}")
        print(f"Retrieved Task Data: {retrieved_task.model_dump()}")

    finally:
        # 3. Cleanup Phase
        # Ensure the connection pool is closed when the application exits
        await close_database_connection()
        print("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
```

### Integration with Web Frameworks (e.g., FastAPI)

If you are using a framework like FastAPI, you tie this lifecycle directly to the application lifespan context manager rather than a standard script execution:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    client = await get_database_client("mongodb://localhost:27017")
    db = client["my_application_db"]
    app.state.db_manager = DatabaseManager.from_database(db)
    
    # Ensure indexes exist
    await app.state.db_manager.tasks.create_indexes()
    
    yield
    
    # Shutdown
    await close_database_connection()

app = FastAPI(lifespan=lifespan)

@app.post("/tasks/")
async def create_task(request: Request):
    manager: DatabaseManager = request.app.state.db_manager
    
    doc = ResearchTaskDoc(title="API Triggered Task")
    task_id = await manager.tasks.insert_one_task(doc)
    
    return {"id": task_id}
```
