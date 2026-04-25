## Python Package Project Structure with UV

### Project Initialization

This project was initialized using UV's modern Python package management:

```bash
uv init your-project-name
cd your-project-name
```

### Project Structure

The project follows Python packaging best practices with a clear separation of concerns:

```
your-project-name/
├── LICENSE
├── Makefile                    # Common development commands
├── pyproject.toml             # Project configuration and dependencies
├── README.md
├── src/
│   └── your_package_name/     # Main package source modules
│       ├── __init__.py        # Package entry point
│       ├── module_a/          # Feature module A
│       │   ├── __init__.py
│       │   ├── core.py
│       │   ├── errors.py
│       │   └── submodule/     # Nested functionality
│       └── module_b/          # Feature module B
│           ├── __init__.py
│           └── implementation.py
├── tests/                     # Test suite
│   ├── test_module_a.py
│   └── test_module_b.py
├── example_api/               # Example usage
│   └── main.py
└── notebooks/                 # Jupyter notebooks for exploration
    └── exploration.ipynb
```

This structure provides:
- **src/ layout**: Prevents import issues and follows modern Python packaging standards
- **Modular design**: Features are cleanly separated into their own modules with clear boundaries
- **Extensible architecture**: New modules and strategies can be added without disrupting existing code
- **Clear boundaries**: Tests, examples, and documentation are separate from core package code

### Package Configuration (pyproject.toml)

The project uses modern Python packaging with Hatchling as the build backend:

```toml
[project]
name = "your-project-name"
version = "0.1.0"
description = "Description of your reusable package"
requires-python = ">=3.10"
dependencies = [
    # Runtime dependencies added via uv add
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# Critical configuration: Only package the reusable modules
[tool.hatch.build.targets.wheel]
packages = [
    "src/your_package_name", 
]
```

The key insight is the `[tool.hatch.build.targets.wheel]` section, which explicitly tells the build system to only package the reusable library code, excluding example applications and other project-specific files.

### Dependencies Management

Dependencies are managed through UV and automatically added to pyproject.toml. The project typically includes:

- **Core functionality libraries**: Domain-specific packages that provide the main features
- **Configuration management**: Libraries for settings, environment variables, and validation
- **Testing framework**: Comprehensive testing tools with fixtures and parametrization support
- **Development tools**: Static analysis, formatting, and code quality tools
- **Optional integrations**: Jupyter support, web frameworks, or database ORMs as needed

### Module Architecture

The package follows a hierarchical module structure where the main package's __init__.py provides a clean public API:

```python
from .module_a import *
from .module_b import *
```

This allows consumers to import everything they need from the top-level package while maintaining internal organization. Each module contains its core functionality, error handling, and any necessary submodules.

### Development Workflow (Makefile)

The Makefile provides essential commands for daily development:

```makefile
install:
	uv pip install -e . --native-tls

server:
	uv run uvicorn src.api.main:app --reload

test:
	uv run pytest tests/test_module_a.py
	uv run pytest tests/test_module_b.py

example:
	uv run uvicorn example_api.main:app --reload
```

**Command Breakdown**:
- `make install`: Installs the package in editable mode using UV's pip interface with native TLS support for secure connections
- `make server`: Launches the main API server with auto-reload for development, typically used when the package includes web service components
- `make test`: Runs the comprehensive test suite module by module, allowing for granular testing and easier debugging of specific components
- `make example`: Starts the example application server demonstrating package usage in realistic scenarios with hot reloading

### Testing Strategy

The test suite is organized by module with comprehensive coverage. Tests typically include:

- **Unit tests**: Individual function and class behavior validation
- **Integration tests**: Module interaction and end-to-end workflow testing
- **Mock scenarios**: Simulated external dependencies and error conditions
- **Parametrized testing**: Multiple input scenarios covered efficiently

Tests use pytest fixtures for setup/teardown and follow naming conventions that mirror the source module structure.

### Development Workflow Benefits

This structure enables several powerful development patterns:

**Editable Installation**: The `uv pip install -e .` approach allows immediate code changes without reinstallation, supporting rapid iteration cycles.

**Granular Testing**: Individual test modules can be executed independently, enabling focused debugging and faster feedback loops during development.

**Live Reload Development**: Both server and example commands support automatic reloading, allowing developers to see changes immediately without manual restarts.

**Static Analysis Integration**: The project structure supports modern Python tooling for code quality, type checking, and formatting enforcement.

**Interactive Development**: Jupyter notebooks enable exploration and prototyping of package functionality in an interactive environment.

**Example-Driven Documentation**: Working example applications provide concrete usage patterns and serve as living documentation that stays synchronized with code changes.

This approach creates a professional, maintainable codebase that can be easily distributed as a Python package while supporting efficient development and testing cycles. The structure scales well as the package grows and accommodates additional modules or features without requiring architectural changes.