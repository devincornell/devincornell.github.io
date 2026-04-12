

## Using Static Factory Methods as Alternative Constructors

Static factory methods are a powerful pattern for instantiating custom types, especially in data pipelines. By using the `@classmethod` decorator, you can create multiple alternative constructors that handle specific instantiation logic, keeping your `__init__` method clean and focused solely on assigning data attributes.

### The Baseline: A Clean `__init__`
Your default constructor (`__init__`) should only be responsible for inserting data attributes. The `dataclasses` module is perfect for this.

```python
import dataclasses
import typing
import math
import random

@dataclasses.dataclass
class Coord:
    x: float
    y: float
```

### 5 Ways to Use Alternative Constructors

#### 1. Handling Multiple Input Formats
When a type can be constructed from different source data, use alternative constructors to handle the necessary conversions.

```python
    @classmethod
    def from_xy(cls, x: float, y: float) -> typing.Self:
        # Enforces type consistency
        return cls(x=float(x), y=float(y))

    @classmethod
    def from_polar(cls, r: float, theta: float) -> typing.Self:
        return cls(
            x=r * math.cos(theta),
            y=r * math.sin(theta),
        )
```

#### 2. Encapsulating Specialized Logic
If creating an object requires substantial logic (like random generation), keep that logic bound to the class via a dedicated constructor.

```python
    @classmethod
    def from_gaussian(cls, x_mu: float, y_mu: float, x_sigma: float, y_sigma: float) -> typing.Self:
        return cls(
            x=random.gauss(mu=x_mu, sigma=x_sigma),
            y=random.gauss(mu=y_mu, sigma=y_sigma)
        )
```

#### 3. Simplifying Common Configurations
Avoid complicated default parameters in `__init__`. Instead, create purpose-built methods for specific situations.

```python
    @classmethod
    def from_xy_line(cls, x: float) -> typing.Self:
        return cls(x=x, y=x)

    @classmethod
    def from_zero(cls) -> typing.Self:
        return cls(x=0.0, y=0.0)
```

#### 4. Returning Multiple Instances
Alternative constructors can return collections of the implementing type, saving you from writing custom collection logic elsewhere.

```python
    @classmethod
    def from_reflected(cls, x: float, y: float) -> list[typing.Self]:
        return [
            cls(x=x, y=y),
            cls(x=-x, y=y),
            cls(x=x, y=-y),
            cls(x=-x, y=-y),
        ]
```

#### 5. Inheriting Safely
When inheriting from built-in types or existing classes, alternative constructors let you add instantiation methods without the risk of overriding and breaking the parent's `__init__`.

```python
class Coords(list[Coord]):
    @classmethod
    def from_gaussian(cls, n: int, x_mu: float, y_mu: float, x_sigma: float, y_sigma: float) -> typing.Self:
        return cls([Coord.from_gaussian(x_mu, y_mu, x_sigma, y_sigma) for _ in range(n)])
```

---

### Chaining Constructors for Validation
When instantiating objects requires varying levels of specificity or validation, you can chain alternative constructors together. Think of this as a tree where every method eventually routes down to `__init__`.

For example, `from_xy_finite` adds validation, then relies on `from_xy` for type coercion, which finally relies on `__init__` for assignment:

```python
    @classmethod
    def from_xy_finite(cls, x: float, y: float) -> typing.Self:
        invalids = (float('inf'), float('-inf'))
        if x in invalids or y in invalids:
            raise ValueError('x and y must be finite')
        
        # Chains to another factory method
        return cls.from_xy(x=x, y=y)
```

---

### Applying this to Data Pipelines
In data pipelines, transformations between immutable types are standard. A strong design principle is that **downstream types should know how to construct themselves** from upstream types.

```python
@dataclasses.dataclass
class RadialCoord:
    r: float
    theta: float

    @classmethod
    def from_cartesian(cls, coord: Coord) -> typing.Self:
        return cls(
            r = math.sqrt(coord.x**2 + coord.y**2),
            theta = math.atan2(coord.y, coord.x),
        )
```

**Usage:**
```python
c = Coord(5, 4)
rc = RadialCoord.from_cartesian(c)
```

For a cleaner interface, you can optionally add a helper method to the upstream type that simply passes itself to the downstream constructor:

```python
    # Placed inside the Coord class
    def to_radial(self) -> RadialCoord:
        return RadialCoord.from_cartesian(self)
```