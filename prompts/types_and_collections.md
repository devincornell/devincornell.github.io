
# Introduction to Static Factory Methods as Alternative Constructors

In this article, I discuss and give examples for one of my favorite patterns for data analysis code: static factory methods used as alternative constructors[cite: 8]. A static factory method used as an alternative constructor is simply a static method which returns an instance of the object that implements it[cite: 9]. A single class can have multiple alternative constructors that accept different parameters, and the methods should contain any logic needed to initialize the object[cite: 10]. While these methods are common in many software engineering applications, I believe they are especially useful in data analysis code because they align with the way data flows through your program[cite: 11].

### Managing Instantiation Logic

The static factory method pattern is a way of writing logic to instantiate your custom types[cite: 16]. Broadly speaking, there are three possible places where instantiation logic can exist: (1) outside of the type, (2) inside the `__init__` method, or (3) inside an alternative constructor[cite: 17]. 

Place logic outside the object itself when the same logic is required to create multiple different types[cite: 18, 22]. If this is the case, you may be better off creating an intermediary type anyways[cite: 22]. Use `__init__` for any logic that MUST be done every time an object is instantiated and there are no ways to instantiate the object without that logic[cite: 23]. In all other cases, static factory methods are the best option[cite: 24].

If you construct your data pipelines as a series of immutable types and the transformations between them (which I recommend), these alternative constructors can contain all logic involved with transforming data from one type to another[cite: 26]. As all data pipelines essentially follow a structure flowing from source data to types, we can see how static factory methods could be ubiquitous throughout your data pipelines[cite: 27].

I have written at length why it is best to use immutable custom types to represent intermediary data formats, and alternative constructors can play the role of converting the data from one type to another[cite: 39]. Here are a few benefits of implementing static factory methods for data pipelines using these patterns[cite: 40]:

* A class can have multiple alternative constructors, and therefore can be initialized in different ways from different source types and parameters[cite: 41]. The reader can easily see the types from which it can be constructed[cite: 42].
* When creating dataclass (or pydantic/attrs) types, they allow you to pass non-data parameters and avoid using `__post_init__` or requiring partial initialization states[cite: 43, 48].
* These methods offer a superior alternative to overriding constructor methods when using inheritance[cite: 48]. Subclasses can call alternative constructors of parent classes explicitly instead of using `super()` or otherwise referring to the parent class[cite: 49]. This is especially useful when inheriting from built-in types such as collections or exceptions[cite: 50].

---

### Python Examples

Now I will show some examples of static factory methods used as alternative constructors in Python[cite: 52, 53]. We typically create these methods using the `@classmethod` decorator, and they always return an instance of the containing class[cite: 54].

For example purposes, let us start by creating the most basic container object: a coordinate with `x` and `y` attributes[cite: 55]. The `__init__` method simply takes `x` and `y` parameters and stores them as attributes[cite: 56]. I include `x` and `y` as part of the definition to support type checkers[cite: 57]. I also create a basic `__repr__` method for readability[cite: 58].

```python
import typing
import math
import random

class Coord:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(x={self.x}, y={self.y})'
```

The implementation of the `__init__` default constructor method is important because it must be called any time you want to instantiate the object[cite: 73]. Ideally, it should ONLY be responsible for inserting data attributes[cite: 74]. Most of the time, all attributes should be required[cite: 74]. Note that the `__init__` created by the dataclasses module is perfect for this, so I highly recommend using it[cite: 75]. This definition is exactly equivalent to the above[cite: 76].

```python
import dataclasses

@dataclasses.dataclass
class Coord:
    x: float
    y: float
```

We can instantiate this type using `__init__` by passing both `x` and `y` in the calling function[cite: 82]. All of the following examples will start with this type[cite: 84].

---

### Useful Situations

For practical purposes, I have identified several situations in which alternative constructors may be useful to you, whether or not you apply other design patterns I have discussed[cite: 86, 91]. 

* The type needs to be constructed in multiple ways, each using different logics or source data[cite: 92].
* Substantial logic is required to instantiate the type but that logic is only used for that purpose[cite: 93].
* You want to avoid situation-specific or inter-dependent defaulted parameters[cite: 94].
* You need to return multiple instances of the type[cite: 95].
* You are using an existing constructor of an inherited type[cite: 96].

#### Alternative Instantiation Methods
The most obvious situation in which you may want to use a static factory method is when there are multiple alternative methods for creating an instance[cite: 99]. The following two methods allow you to create the `Coord` object from either cartesian or polar coordinates[cite: 100].

Note that the `from_xy` method here enforces type consistency by calling `float`, which would also raise an exception if the `x` or `y` arguments are not coercible[cite: 101]. The `from_polar` method is also enforcing type consistency implicitly through the use of `math.cos` and `math.sin`, which both return floating point numbers[cite: 102].

```python
    @classmethod
    def from_xy(cls, x: float, y: float) -> typing.Self:
        return cls(
            x=float(x),
            y=float(y),
        )

    @classmethod
    def from_polar(cls, r: float, theta: float) -> typing.Self:
        return cls(
            x=r * math.cos(theta),
            y=r * math.sin(theta),
        )
```

An alternative approach would be to place the float calls inside of the `__init__` constructor[cite: 118]. With that approach, `from_polar` would be forced to execute that logic even though it is not necessary because `math.sin` and `math.cos` already create type safety[cite: 119, 120]. 

#### Type-specific Instantiation Logic
Alternative constructors are a good option when instantiation requires substantial logic but the logic is only used for that purpose[cite: 122, 123]. The instantiation logic should live as part of the type, and the static factory method is a good place to put it[cite: 124].

For example, say we need to sample points from a gaussian distribution by creating a new random coordinate instance according to some parameters[cite: 125]. The instantiation logic involves calling `random.gauss`, and so we put that inside a new `from_gaussian` method[cite: 126]. In contrast to the default constructor, none of the parameters here are actually stored as data - only the data generated from the random functions[cite: 127]. You would instantiate the new object with the expression `Coord.from_gaussian(...)`[cite: 128].

```python
    @classmethod
    def from_gaussian(cls,
        x_mu: float,
        y_mu: float,
        x_sigma: float,
        y_sigma: float
    ) -> typing.Self:
        return cls(
            x=random.gauss(mu=x_mu, sigma=x_sigma),
            y=random.gauss(mu=y_mu, sigma=y_sigma)
        )
```
Most other solutions to this situation are complicated: you either require the calling function to implement this logic or add it to `__init__` with some complicated defaulted parameters[cite: 143].

#### Situation-specific Parameters
Static factory methods are a good alternative to the situation where you have an `__init__` method where the behavior of some parameters varies according to the values of other parameters[cite: 145]. Instead, create multiple situation-specific alternative constructors for use in different situations[cite: 146].

For example, say we want to create instances of points that lie along the line $x=y$[cite: 147]. We can create a new instance from a single parameter in this case, because both values can be calculated given the value of `x`[cite: 148].

```python
    @classmethod
    def from_xy_line(cls, x: float) -> typing.Self:
        return cls(x=x, y=x)
```

If we wanted a simple way to create the origin coordinate, we can create a method that accepts no parameters[cite: 151].

```python
    @classmethod
    def from_zero(cls) -> typing.Self:
        return cls(x=0.0, y=0.0)
```

In this way, the function signatures themselves make it clear which parameters are needed for a given situation[cite: 158].

#### Returning Multiple Instances
In cases where it may be too tedious to create custom collection types, alternative constructors can be used to return collections of the implementing type[cite: 160]. As an example, say we want to return a set of coordinates created by the reflection of the original point across the x and y axes[cite: 161]. In that case, we can return a set of instances representing the desired coordinates[cite: 162].

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

#### Calling a Parent Constructor Method
Static factory methods are good to use when you want to use the `__init__` method of the parent class and overriding `__init__` could have unintended side effects[cite: 172].

Say that we want to create a 2-dimensional vector type that contains the same data as `Coord` but has some additional methods for vector operations that are not typically defined for coordinates[cite: 173]. The data is not different, and therefore we should not define a new `__init__` method[cite: 174, 178]. If any other logic is required, we can add that to the alternative constructor[cite: 181].

```python
class Vector2D(Coord):
    @classmethod
    def unity(cls) -> typing.Self:
        return cls(x=1.0, y=1.0)

    def dot(self, other: typing.Self) -> float:
        return (self.x * other.x) + (self.y * other.y)
```

Another situation where this might arise is when inheriting from built-in types when you do not want to risk altering the behavior of the original type[cite: 187]. In this case, we can call the `Coord.from_gaussian` method and return a list of `Coord` types in the container `from_gaussian` method[cite: 188]. This approach makes it easy and safe to inherit from built-in collection types[cite: 189].

```python
class Coords(list[Coord]):
    @classmethod
    def from_gaussian(cls,
        n: int,
        x_mu: float,
        y_mu: float,
        x_sigma: float,
        y_sigma: float
    ) -> typing.Self:
        return cls([Coord.from_gaussian(x_mu, y_mu, x_sigma, y_sigma) for _ in range(n)])
```

You could also use this as an alternative to returning multiple instances from the `Coord` type[cite: 200].

```python
    @classmethod
    def from_reflected_points(cls, x: float, y: float) -> typing.Self:
        return cls([
            Coord(x=x, y=y),
            Coord(x=-x, y=y),
            Coord(x=x, y=-y),
            Coord(x=-x, y=-y),
        ])
```

---

### Inter-dependent Constructor Calls

It is often helpful to be able to instantiate an object with varying levels of specificity, depending on the situation[cite: 213]. In this case, you can create multiple alternative constructors that call each other successively, effectively chaining the instantiation logic down the call stack[cite: 214]. If you know that the instantiation methods will build on each other, this approach is clearer than creating a pool of helper methods that are selectively invoked in every static factory method[cite: 215].

Beyond the ability to instantiate an object in different ways, you can start to think in terms of a tree of successive alternative constructors which all lead back to the `__init__` method[cite: 216]. Every time you need a new constructor method, it is worth thinking about where it could exist in this tree[cite: 217].

Let us return to the example `from_xy`[cite: 228]. Recall that this simple method actually applies a level of validation: by calling `float`, we ensure the input values are coercible to floats[cite: 228, 232]. Now revisit the definition of `from_xy_line`[cite: 242]. In the original definition, we simply assigned the input value to both `x` and `y` of the new object[cite: 242]. Instead of calling `__init__`, we can call `from_xy` to add the same validation functionality to this method as well[cite: 243].

```python
    @classmethod
    def from_xy_line(cls, x: float) -> typing.Self:
        return cls.from_xy(x=x, y=x)
```

Now say we may want to add an additional validation step where we ensure `x` and `y` are finite[cite: 246]. We can create a new method `from_xy_finite` which checks for finiteness and also calls `from_xy` to perform the floating point validation[cite: 247]. In this way, `from_xy_finite` is actually adding to the functionality of `from_xy` without overlap[cite: 248].

```python
    @classmethod
    def from_xy_finite(cls, x: float, y: float) -> typing.Self:
        # raise exception if values are invalid
        invalids = (float('inf'), float('-inf'))
        if x in invalids or y in invalids:
            raise ValueError('x and y must be finite')
        
        return cls.from_xy(x=x, y=y)
```

If we revisit the alternative constructor `from_zero`, we can see that it still should be calling the `__init__` constructor because we can guarantee that the inputs are valid floating point numbers, and therefore do not benefit from calling any other static factory method[cite: 258, 259, 260].

```python
    @classmethod
    def from_zero(cls) -> typing.Self:
        return cls(x=0.0, y=0.0)
```

Taken together, we can think of these dependencies as a tree where all methods call `__init__` at the lowest level[cite: 263]. Creating a new alternative constructor is a matter of determining which operations are needed for instantiation[cite: 264].

---

### Data Pipelines Using Alternative Constructors

I have written more extensively about this in the past, but I think it is worth noting how static factory methods fit within larger data pipelines[cite: 266]. If we structure our code as a set of immutable data types and the transformations between them, we can do most of the transformation work inside alternative constructors[cite: 267].

A good design principle is that downstream types should know how to construct themselves, and that logic can be placed in static factory methods[cite: 268]. For instance, we have our `Coord` object from the previous example[cite: 269]. Now say we may want to transform these existing Cartesian coordinates to radial coordinates[cite: 270]. We can create a new type `RadialCoord` to represent this new data, and write the transformation code in an alternative constructor `from_cartesian`[cite: 271]. 

The radial coordinate can be constructed using either the `__init__` method with the `r` and `theta` parameters or the `from_cartesian` static factory method, which accepts a `Coord`[cite: 272].

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

We can create a radial coordinate using a `Coord` instance[cite: 285].

```python
c = Coord(5, 4)
rc = RadialCoord.from_cartesian(c)
```

Alternatively, we could make this accessible as a call to `to_radial()`[cite: 289].

```python
@dataclasses.dataclass
class Coord:
    x: float
    y: float

    def to_radial(self) -> RadialCoord:
        return RadialCoord.from_cartesian(self)
```

The latter step increases the coupling between the two objects, but, in exchange, the resulting interface is quite clean[cite: 296]. Placing all of the construction logic in the downstream type's alternative constructor means that the coupling is weak and can be removed from the upstream type very easily[cite: 297].

```python
Coord(5, 5).to_radial()
```

You can imagine how this pattern could be used throughout your data pipelines[cite: 303].

### In Conclusion

Static factory methods used as alternative constructors allow you to write modular and extensible data pipelines, and are especially useful when building pipelines composed of immutable types and their transformations[cite: 305]. Most of my own work relies heavily on this pattern, and I hope you can benefit too! [cite: 306]