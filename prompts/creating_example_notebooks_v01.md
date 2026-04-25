# Guide to Writing Documentation Example Notebooks

This guide outlines the best practices for creating Jupyter notebooks that serve as documentation and demonstrations for your packages. These notebooks bridge the gap between technical API documentation and practical usage examples.

## Overview

Documentation notebooks serve multiple purposes:
- **Onboarding**: Help new developers understand how to use your package
- **Examples**: Provide working code that users can copy and adapt
- **Testing**: Serve as executable documentation that stays current with your code
- **Exploration**: Allow users to experiment with functionality interactively

## Notebook Structure and Organization

### 1. Title and Introduction Cell
Start every notebook with a clear markdown cell that includes:
```markdown
# Introduction to [Feature/Module Name]

Brief description of what this notebook demonstrates, including:
- The main functionality covered
- Prerequisites or dependencies
- Key concepts users will learn
```

**Example from `intro_to_auth.ipynb`:**
```markdown
# Introduction to Authentication

This notebook demonstrates the authentication and authorization system from `oa_ai_common`...
```

### 2. Import Section
Always start with a dedicated imports cell:
```python
import your_package
import supporting_libraries  # fastapi, etc.
```

Keep imports minimal and grouped logically. Import only what you'll actually use in the notebook.

### 3. Core Structure Pattern

#### Setup and Configuration
- Show how to instantiate main classes/objects
- Demonstrate configuration options
- Explain key parameters and their purpose

#### Basic Usage Examples
- Start with the simplest possible working example
- Build complexity gradually
- Show common use cases first

#### Advanced Features
- Cover edge cases and advanced configurations
- Show integration with other systems (FastAPI, middleware, etc.)
- Demonstrate error handling

#### Practical Scenarios
- Provide realistic examples users might encounter
- Show how features work together
- Include troubleshooting examples

## Writing Effective Code Cells

### 1. Mock Data and Helper Functions
Create realistic mock data early in the notebook:

```python
def mock_bearer_request(token: str) -> fastapi.Request:
    return mock_request({"authorization": f"Bearer {token}"})

def mock_request(headers: dict[str, str], path: str = '/dummy-path') -> fastapi.Request:
    return fastapi.Request(scope={...})
```

**Why this works:**
- Makes examples self-contained and executable
- Allows users to run code without external dependencies
- Demonstrates the expected data structures

### 2. Progressive Complexity
Build examples incrementally:

```python
# Step 1: Basic instantiation
bearer_strat = oa_ai_common.BearerDictStrategy.from_string(
    keys_str = 'key1:scope1,scope2;key2:scope2,scope3'
)

# Step 2: Multiple strategies
okta_strat = oa_ai_common.OktaDictStrategy.from_string(...)

# Step 3: Composite usage
authorizer = oa_ai_common.CompositeAuthorizer.from_strategies({
    'bearer': bearer_strat,
    'okta': okta_strat,
}, valid_scopes = {'scope1', 'scope2', 'scope3'})
```

### 3. Demonstrate Multiple Usage Patterns
Show different ways to use the same functionality:

```python
# Method 1: Dependency Injection
auth_dep = authorizer.dependency({'scope1', 'scope2'})

# Method 2: Middleware
authorizer.add_auth_middleware(sse_app, {'scope1', 'scope2'})
```

## Writing Clear Markdown Documentation

### 1. Explain the "Why" Not Just the "How"
```markdown
## Authentication Methods

### Authenticating With Dependency Injection

We can use the authorizer through dependency injection in FastAPI endpoints or as regular middleware. In the case of dependency injection, you can create the dependency function by calling the `dependency` method along with the scopes that you would like that particular endpoint to have.
```

### 2. Use Clear Section Headers
- Use `##` for main sections (Authentication Methods, Core Concepts)
- Use `###` for subsections (Basic Usage, Advanced Features)
- Use `####` for specific scenarios (Error Handling, Edge Cases)

### 3. Provide Context for Code Examples
Always explain what the next code block will demonstrate:

```markdown
Now we make a mock request with a bearer token and simulate the behavior of the dependency injection by passing it the request. Note that the resulting object contains the results of all the authorization methods at once.
```

## Covering Core Functionality Patterns

### 1. Object Instantiation
Show multiple ways to create objects:
```python
# From string configuration
strategy = BearerDictStrategy.from_string('key1:scope1,scope2')

# From connect string  
telemetry = Telemetry.from_connect_string("sqlite:///:memory:")
```

### 2. Basic Operations
Demonstrate the most common use cases:
```python
# Recording an event
telemetry.record(
    app_id="example-app",
    action="startup", 
    message="app started successfully",
    metadata={"version": "1.0.0"}
)

# Retrieving records
records = telemetry.retrieve_records("example-app")
```

### 3. Error Handling and Edge Cases
Show what happens when things go wrong:
```python
try:
    auth_results['okta'].auth_info.identity
except oa_ai_common.UnauthenticatedAccessError as e:
    print(f'Error: {e}')
```

### 4. Integration Patterns
Show how your package integrates with common frameworks:
```python
# FastAPI integration
@app.get('/endpoint')
def endpoint(auth: AuthResults = Depends(authorizer.dependency({'scope1'}))):
    if not auth.is_authorized():
        raise auth.get_http_exception()
```

## Advanced Notebook Techniques

### 1. Interactive Exploration
Use the notebook format to show step-by-step analysis:
```python
# Examine the results structure
auth_results

# Look at individual components  
for result in auth_results.get_results():
    print(f'{result.validation_type.__name__}: {result.status}')
```

### 2. Comparison Examples
Show different approaches side by side:
```python
# Method 1: Top-level telemetry
telemetry.record(app_id="myapp", action="event", ...)

# Method 2: App-scoped telemetry  
app_telemetry = telemetry.app_telemetry("myapp")
app_telemetry.record(action="event", ...)
```

### 3. Real-World Configuration Examples
Include production-ready patterns:
```python
# Development setup
telemetry = Telemetry.from_connect_string(
    "sqlite:///:memory:", 
    create_if_not_exists=True
)

# Production setup (show in markdown)
```markdown
In production you would use:
```python
telemetry = Telemetry.from_connect_string(
    os.environ["DATABASE_URL"],
    create_if_not_exists=True  
)
```

## Quality Checklist

### Before Publishing a Notebook:

#### ✅ Content Coverage
- [ ] All major public classes and methods are demonstrated
- [ ] Common use cases are covered with working examples
- [ ] Integration patterns (FastAPI, middleware) are shown
- [ ] Error handling and edge cases are addressed

#### ✅ Code Quality
- [ ] All code cells execute without errors
- [ ] Mock data is realistic and self-contained
- [ ] Examples build in logical complexity order
- [ ] Variable names are clear and consistent

#### ✅ Documentation Quality  
- [ ] Each section has a clear purpose and explanation
- [ ] Code blocks are preceded by explanatory markdown
- [ ] Technical concepts are explained in accessible language
- [ ] Links to API documentation are included where helpful

#### ✅ User Experience
- [ ] New users can follow the notebook start-to-finish
- [ ] Examples can be easily adapted to real use cases
- [ ] The notebook serves as a reference for later consultation
- [ ] Key patterns and best practices are highlighted

## File Organization

### Naming Convention
- Use descriptive names: `intro_to_auth.ipynb`, `intro_to_telemetry.ipynb`
- Prefix with feature area for large packages
- Use underscores for readability

### Notebook Scope
- **One notebook per major feature area** (auth, telemetry, etc.)
- **Keep notebooks focused** - avoid covering too many unrelated topics
- **Create specialized notebooks** for complex integration scenarios

### Supporting Files
Consider including:
- `example_api/` - Working application examples
- `notebooks/data/` - Sample data files if needed
- `notebooks/README.md` - Index of available notebooks

## Common Pitfalls to Avoid

### ❌ Don't Do This:
1. **Assuming prior knowledge** - Always explain concepts clearly
2. **Showing only success paths** - Include error handling examples  
3. **Using real credentials** - Always use mock/fake data
4. **Skipping explanations** - Don't just show code without context
5. **Making notebooks too long** - Break complex topics into multiple notebooks

### ✅ Do This Instead:
1. **Start from basics** - Assume users are new to your package
2. **Show realistic scenarios** - Include both success and failure cases
3. **Use safe mock data** - Create convincing but safe examples
4. **Explain the reasoning** - Help users understand why, not just how
5. **Keep focused** - One clear learning objective per notebook

## Maintenance

### Keeping Notebooks Current
- **Test notebooks with CI/CD** - Run notebooks as part of your test suite
- **Update with API changes** - Notebooks should reflect current API
- **Refresh examples regularly** - Keep examples relevant and modern
- **Gather user feedback** - Ask users what examples would be helpful

### Version Control Best Practices
- **Clear cell outputs before committing** - Avoid noise in diffs
- **Use meaningful commit messages** - Explain what examples were added/changed
- **Tag notebook versions** - Link notebooks to package releases when relevant

---

This guide reflects the patterns used successfully in `oa-ai-common` notebooks. Following these practices will help create documentation that serves both as learning material and practical reference for your package users.