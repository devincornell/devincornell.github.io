# FastAPI + FastMCP Server Architecture Documentation

## Overview

This architecture implements a hybrid API server that combines FastAPI's traditional REST endpoints with FastMCP's Model Context Protocol (MCP) capabilities. This design provides both RESTful HTTP endpoints and MCP tool interfaces for AI agents to interact with the same underlying business logic.

## Architecture Components

### 1. Core Structure

```
src/api/
├── main.py                      # Application factory and router registration
├── common/                      # Shared utilities and configuration
│   ├── transport_security.py    # CORS and MCP security settings
│   ├── authorizer.py            # Authentication middleware
│   └── telemetry.py             # Logging and monitoring
└── feature_a/v1/                # Feature-specific modules
    ├── feature_a_endpoints.py   # FastAPI router definitions
    └── feature_a_mcp.py         # FastMCP server definitions
```

### 2. FastAPI Router Pattern (feature_a_endpoints.py)

The FastAPI router is structured using the following pattern:

```python
# 1. Router Initialization
feature_a_router_v1 = fastapi.APIRouter(prefix='/feature-a/v1')

# 2. Endpoint Definition with Decorator
@feature_a_router_v1.get('/config')
async def feature_a_v1_config(
    request: fastapi.Request,
    auth: AuthResults = fastapi.Depends(authorizer.dependency(Scope.all())),
) -> fastapi.responses.JSONResponse:
    # Implementation logic
    pass

# 3. Additional Functions (without decorators - work in progress)
async def feature_a_v1_process(
    # Function parameters with FastAPI Query/Depends annotations
    param1: int = fastapi.Query(description="Primary parameter", default=1),
    param2: str = fastapi.Query(description="Secondary parameter"),
    # ... other parameters
) -> fastapi.responses.JSONResponse:
    # Business logic implementation
    pass
```

**Key Features:**
- **Router Registration**: Each module creates its own `APIRouter` with a prefix
- **Decorator-based Registration**: Use `@router.get()`, `@router.post()`, etc. to register endpoints
- **Dependency Injection**: FastAPI's dependency system for authentication, request validation
- **Type Annotations**: Heavy use of Python typing for automatic API documentation

**Current Status**: The router is partially complete - some functions like `feature_a_v1_process` exist but need the `@feature_a_router_v1.get('/process')` decorator to be registered as endpoints.

### 3. FastMCP Server Pattern (feature_a_mcp.py)

The MCP server follows this initialization pattern:

```python
# 1. Server Initialization
feature_a_mcp = mcp.server.FastMCP(
    'Feature A MCP',
    stateless_http=True,
    streamable_http_path="/",
    transport_security=TransportSecuritySettings(
        allowed_hosts=['localhost:*', '127.0.0.1:*', 'api-dev.example.com', 'api.example.com'],
        allowed_origins=['http://localhost:*', 'http://127.0.0.1:*', 'https://api-dev.example.com', 'https://api.example.com']
    )
)

# 2. Tool Function Definition
async def process_data(
    input_param: typing.Annotated[str, ParamDescs.INPUT],
    options: typing.Annotated[list[str], ParamDescs.OPTIONS],
    # ... other parameters with type annotations and descriptions
) -> str:
    # Business logic implementation
    pass

# 3. Tool Registration with Decorator (MISSING - needs to be added)
# @feature_a_mcp.tool()
# async def process_data(...):
#     pass
```

**Key Features:**
- **Server Initialization**: Create FastMCP instance with security settings at module level
- **Stateless HTTP**: Configured for stateless operation suitable for API deployment
- **Transport Security**: CORS and host allowlisting for security
- **Type Annotations**: Rich typing with descriptions for automatic MCP tool schema generation

**Current Status**: The server is initialized and functions are defined, but the `@feature_a_mcp.tool()` decorators are missing to register functions as MCP tools.

### 4. Main Application Integration (main.py)

The main application factory brings everything together:

```python
def create_app() -> fastapi.FastAPI:
    # 1. Create FastAPI app with MCP lifespan management
    app = fastapi.FastAPI(lifespan=create_mcp_lifespan([]))
    
    # 2. Add CORS middleware
    add_cors_middleware(app)
    
    # 3. Register FastAPI routers
    app.include_router(feature_a_router_v1)
    app.include_router(feature_b_router_v1)
    
    # 4. MCP Server Integration (COMMENTED OUT - work in progress)
    # The MCP servers would be mounted here when complete
    
    return app
```

**Integration Points:**
- **Router Registration**: `app.include_router(feature_a_router_v1)` adds REST endpoints
- **MCP Mounting**: MCP servers will be mounted at paths like `/feature-a/v1/mcp/` 
- **Shared Lifespan**: Both FastAPI and MCP servers share the same application lifecycle
- **Common Security**: Both use the same CORS and transport security settings

## Expected Complete Integration

When fully implemented, the integration would look like:

```python
# In main.py (currently commented out)
from .feature_a.v1 import feature_a_mcp
from .feature_b.v1 import feature_b_mcp

def create_app():
    app = fastapi.FastAPI(lifespan=create_mcp_lifespan([feature_a_mcp, feature_b_mcp]))
    
    # REST endpoints
    app.include_router(feature_a_router_v1)
    app.include_router(feature_b_router_v1)
    
    # MCP endpoints  
    app.mount('/feature-a/v1/mcp', feature_a_mcp.asgi_app)
    app.mount('/feature-b/v1/mcp', feature_b_mcp.asgi_app)
    
    return app
```

## Benefits of This Architecture

### 1. **Dual Interface Support**
- **REST Endpoints**: Traditional HTTP API for web applications
- **MCP Tools**: AI agent-friendly interface for the same functionality

### 2. **Code Reuse**
- Business logic can be shared between REST and MCP interfaces
- Common authentication, validation, and error handling

### 3. **Type Safety**
- FastAPI generates OpenAPI schemas from type annotations
- FastMCP generates MCP tool schemas from the same annotations

### 4. **Modular Design**
- Each feature area (feature_a, feature_b, etc.) has its own module
- Independent routers and MCP servers that can be developed separately

### 5. **Security Consistency**
- Shared transport security settings
- Common authentication middleware
- Unified CORS configuration

## Current Refactoring Status

This is a work-in-progress refactoring with several incomplete elements:

### Missing Components:
1. **MCP Tool Decorators**: Functions in `feature_*_mcp.py` need `@feature_*_mcp.tool()` decorators
2. **FastAPI Endpoint Decorators**: Some functions in `feature_*_endpoints.py` need route decorators
3. **MCP Server Mounting**: Integration code in `main.py` is commented out
4. **Lifespan Management**: MCP servers need to be added to the lifespan manager

### Testing Infrastructure:
The project includes comprehensive tests expecting:
- MCP tools accessible at `/feature-a/v1/mcp/` endpoint
- Tools named according to their business logic (e.g., `process_data`)
- Standard MCP protocol compliance

## Implementation Recommendations

1. **Complete MCP Decorators**: Add `@feature_*_mcp.tool()` to functions in `feature_*_mcp.py`
2. **Complete REST Decorators**: Add route decorators to remaining functions in `feature_*_endpoints.py`
3. **Enable Integration**: Uncomment and update the MCP mounting code in `main.py`
4. **Add to Lifespan**: Include MCP servers in the `create_mcp_lifespan([feature_a_mcp, ...])` call
5. **Shared Logic**: Consider extracting common business logic to avoid duplication between REST and MCP implementations

This architecture provides a robust foundation for serving the same business capabilities through both traditional REST APIs and modern MCP interfaces, making the system accessible to both web applications and AI agents.