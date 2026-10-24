This is an example of a FastAPI application that implements the layered architecture using dependency inversion, ensuring the domain layer remains completely isolated from infrastructure concerns.

### 1. The Domain Layer

This layer contains the pure business logic and the Repository interface. It has zero dependencies on FastAPI, SQLAlchemy, or any external libraries, fulfilling the requirement to eliminate any dependency on infrastructure or application logic.

```python
from dataclasses import dataclass
from typing import Protocol
from datetime import datetime

# 1. Entity: Has an identity and encapsulates business rules
@dataclass
class Order:
    id: str
    customer_id: str
    total_amount: float
    is_shipped: bool = False

    def ship_order(self):
        if self.total_amount <= 0:
            raise ValueError("Cannot ship an empty order.")
        self.is_shipped = True

# 2. Repository Interface: Defines the contract for data access in domain terms
class OrderRepository(Protocol):
    def get_by_id(self, order_id: str) -> Order:
        """Returns a fully instantiated Order object."""
        ...
        
    def save(self, order: Order) -> None:
        """Persists the Order object."""
        ...

```

### 2. The Application (Service) Layer

This layer orchestrates the high-level tasks. It depends only on the Domain layer. By relying on the `OrderRepository` interface rather than a concrete database connection, it successfully delegates all object storage and access to the repository.

```python
class OrderService:
    # Depends purely on the domain interface, not the database
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def process_shipment(self, order_id: str) -> Order:
        # Fetch the pure Domain object
        order = self.repository.get_by_id(order_id)
        
        # Apply the business rule
        order.ship_order()
        
        # Delegate saving back to the repository
        self.repository.save(order)
        
        return order

```

### 3. The Infrastructure Layer

This layer handles the actual database operations. It implements the interface defined by the domain layer, creating the illusion of an in-memory collection of objects while encapsulating the actual storage technology.

```python
# (Assuming SQLAlchemy is configured elsewhere)
from sqlalchemy.orm import Session
from some_orm_models import OrderModel # The database schema representation

class SqlAlchemyOrderRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, order_id: str) -> Order:
        # Infrastructure logic: query the database
        db_record = self.db.query(OrderModel).filter_by(id=order_id).first()
        if not db_record:
            raise Exception("Order not found")
            
        # Map the database record back to a pure Domain Entity
        return Order(
            id=db_record.id,
            customer_id=db_record.customer_id,
            total_amount=db_record.total_amount,
            is_shipped=db_record.is_shipped
        )

    def save(self, order: Order) -> None:
        # Infrastructure logic: map the Domain Entity to the DB and save
        db_record = self.db.query(OrderModel).filter_by(id=order.id).first()
        db_record.is_shipped = order.is_shipped
        self.db.commit()

```

### 4. The API Layer (FastAPI)

The FastAPI router handles HTTP requests and acts as the entry point. It wires the concrete Infrastructure class into the Application Service using dependency injection, ensuring the Application and Domain layers remain entirely unaware of the database.

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel

app = FastAPI()

# Dependency Injection setup
def get_db_session():
    # Yields a real database session
    pass

def get_order_repository(db: Session = Depends(get_db_session)) -> OrderRepository:
    # Injects the concrete infrastructure implementation
    return SqlAlchemyOrderRepository(db)

def get_order_service(repo: OrderRepository = Depends(get_order_repository)) -> OrderService:
    # Injects the repository interface into the application service
    return OrderService(repo)

# API Schema (User Interface Layer)
class ShipmentResponse(BaseModel):
    id: str
    is_shipped: bool

@app.post("/orders/{order_id}/ship", response_model=ShipmentResponse)
def ship_order(
    order_id: str, 
    service: OrderService = Depends(get_order_service)
):
    # The API layer only triggers the application layer
    shipped_order = service.process_shipment(order_id)
    
    return ShipmentResponse(
        id=shipped_order.id, 
        is_shipped=shipped_order.is_shipped
    )

```