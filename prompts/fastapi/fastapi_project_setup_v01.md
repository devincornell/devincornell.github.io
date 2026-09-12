I'll help you modify the guide to match your current template repository. Let me first examine the current structure and key files to understand how this template is organized. 

Read [](file:///Users/devin/code/server-template-main/pyproject.toml)

Read [](file:///Users/devin/code/server-template-main/Makefile)

Read [](file:///Users/devin/code/server-template-main/src/api/main.py)

Read [](file:///Users/devin/code/server-template-main/src/api/routes.py)

Read [](file:///Users/devin/code/server-template-main/src/module1/example.py)

Read [](file:///Users/devin/code/server-template-main/src/module1/__init__.py)

Read [](file:///Users/devin/code/server-template-main/README.md)

Read [](file:///Users/devin/code/server-template-main/tests/test_telemetry.py#1-1), lines 1 to 20

Based on the template repository structure, I'll create a modified guide that reflects your FastAPI server template. Here's the updated version:

## FastAPI Server Template with UV and Reusable Modules

### Project Initialization

This FastAPI server template provides a foundation for building web APIs with reusable business logic modules:

```bash
# Use this repository as a template or clone it
git clone <your-template-repo> your-server-name
cd your-server-name
```

### Project Structure

The template follows a clean separation between web API code and reusable business logic:

```
your-server-name/
├── Dockerfile                 # Container configuration
├── LICENSE
├── Makefile                   # Development commands
├── pyproject.toml             # Project configuration and dependencies
├── README.md
├── src/
│   ├── __init__.py
│   ├── api/                   # FastAPI web layer
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application factory
│   │   └── routes.py          # API route definitions
│   └── module1/               # Reusable business logic modules
│       ├── __init__.py        # Clean public API
│       └── example.py         # Core functionality
└── tests/                     # Test suite
    └── test_telemetry.py
```

This structure provides:
- **API separation**: FastAPI web layer is cleanly separated from business logic
- **Reusable modules**: Core functionality can be packaged and distributed independently
- **Container ready**: Dockerfile included for easy deployment
- **Development focused**: Hot-reload support and simple workflow commands

### Package Configuration (pyproject.toml)

The project uses modern Python packaging with selective module inclusion:

```toml
[project]
name = "simple-server-app"
version = "0.1.0"
description = "FastAPI server and reusable modules"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.135.3",
    "pydantic-settings>=2.13.1", 
    "pytest>=9.0.2",
    "sqlalchemy>=2.0.49",
    "uvicorn>=0.44.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# Critical: Only package the reusable business logic, exclude API layer
[tool.hatch.build.targets.wheel]
packages = [
    "src/module1"
]
```

The key insight is the `[tool.hatch.build.targets.wheel]` section, which explicitly packages only the reusable business logic modules, allowing you to distribute core functionality separately from the web API layer.

### Dependencies Management

The template includes essential FastAPI server dependencies managed through UV:

- **FastAPI**: Modern web framework with automatic OpenAPI generation
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic Settings**: Configuration management and validation
- **SQLAlchemy**: Database ORM for data persistence
- **Pytest**: Testing framework with comprehensive fixture support

Additional dependencies are easily added via `uv add package-name` and automatically managed in pyproject.toml.

### FastAPI Architecture

The API layer follows a modular structure:

**main.py** - Application factory pattern:
```python
import fastapi
from src.api.routes import router

def create_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    
    @app.get('/')
    async def get_home() -> fastapi.responses.HTMLResponse:
        return fastapi.responses.HTMLResponse(content="ok", status_code=200)
    
    # Include modular routers
    app.include_router(
        router,
        prefix='/module',
        tags=['module_tag1', 'module_tag2']
    )
    
    return app

app = create_app()
```

**routes.py** - Route definitions that consume business logic:
```python
import fastapi
import src.module1

router = fastapi.APIRouter()

@router.get('/')
async def test_function() -> str:
    return src.module1.test()
```

### Reusable Module Architecture

Business logic modules provide clean APIs for both the FastAPI layer and external consumers:

**__init__.py** - Public API:
```python
from .example import test
```

**example.py** - Core functionality:
```python
def test() -> str:
    return "Hello world"
```

This pattern allows modules to be imported by the API layer (`src.module1.test()`) while maintaining a clean public interface for external consumers.

### Development Workflow (Makefile)

The Makefile provides essential commands for FastAPI development:

```makefile
install:
	uv pip install -e . --native-tls

server:
	uv run uvicorn src.api.main:app --reload

pytest:
	uv run pytest
```

**Command Breakdown**:
- `make install`: Installs the package in editable mode with secure dependency resolution
- `make server`: Launches the FastAPI development server with automatic reload on code changes
- `make pytest`: Runs the complete test suite with pytest

### Container Deployment

The included Dockerfile enables consistent deployment across environments:

- **Multi-stage builds**: Efficient container images with minimal production footprint  
- **Dependency caching**: UV dependency resolution cached for faster builds
- **Production ready**: Optimized for performance and security

### Testing Strategy

The test suite validates both API endpoints and business logic:

- **API integration tests**: Full request/response cycle testing through FastAPI test client
- **Business logic unit tests**: Isolated testing of core functionality modules
- **Mock scenarios**: External dependency simulation and error condition handling
- **Async testing**: Proper async/await pattern validation for FastAPI routes

### Development Workflow Benefits

This template enables professional FastAPI development patterns:

**Hot Reload Development**: The `make server` command provides immediate feedback on code changes without manual server restarts, supporting rapid API development cycles.

**Modular Testing**: Individual modules can be tested independently, enabling focused debugging and faster feedback loops during business logic development.

**Clean Architecture**: The separation between API routes and business logic enables better testability, reusability, and maintainability as the application grows.

**Distribution Flexibility**: Business logic modules can be packaged and distributed separately from the web API, enabling code reuse across multiple applications.

**Container-First**: Built-in Docker support ensures consistent behavior across development, staging, and production environments.

**Modern Python Tooling**: UV dependency management provides fast, reliable package resolution and virtual environment handling.

This FastAPI server template creates a professional foundation for building scalable web APIs while maintaining clean separation between web concerns and business logic. The structure scales well as the application grows and accommodates additional modules or API routes without requiring architectural changes.