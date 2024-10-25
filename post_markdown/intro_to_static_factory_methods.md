---
title: "Introduction to Static Factory Constructor Methods"
subtitle: "Change the way you initialize custom types in Python."
date: "June 14, 2024"
id: "intro_to_static_factory_constructor_methods"
blogroll_img_url: "https://storage.googleapis.com/public_data_09324832787/static_factory_methods.svg"
---

In this article, I discuss and give examples for one of my favorite patterns for data analysis code: static factory constructor methods. A ***static factory constructor method*** (SFCM hereafter) is simply a static method which returns an instance of the object that implements it. A single class can have multiple SFCMs that accept different parameters, and the methods should contain any logic needed to initialize the object. While these methods are common in many software engineering applications, I believe they are especially useful in data analysis code because they align with the way data flows through your program.

<img style="width:80%;" class="figure-center" src="https://storage.googleapis.com/public_data_09324832787/static_factory_methods.svg" /> 

The SFCM pattern is a way of writing logic to instantiate your custom types. Broadly speaking, there are three possible places where instantiation logic can exist: (1) outside of the type, (2) inside the `__init__` method, or (3) inside a SFCM. Place logic outside the object itself when the same logic is required to create multiple different types. If this is the case, you may be better off creating an intermediary type anyways. Use `__init__` for any logic that MUST be done every time an object is instantiated and there are no ways to instantiate the object without that logic. In all other cases, SFCMs are the best option.

If you construct your data pipelines as a series of immutable types and the transformations between them ([which I recommend](https://devinjcornell.com/post/dsp0_patterns_for_dataclasses.html)), SFCMs can contain all logic involved with transforming data from one type to another. As all data pipelines essentially follow the structure shown in the diagram below (more or less explicitly), we can see how SFCMs could be ubiquitous throughout your data pipelines.

<img style="width:80%;" class="figure-center" src="https://storage.googleapis.com/public_data_09324832787/sfcm_data_flow.svg" /> 


I have [written at length](https://devinjcornell.com/post/dsp0_patterns_for_dataclasses.html) why it is best to use immutable custom types to represent intermediary data formats, and SFCMs can play the role of converting the data from one type to another. Here are a few benefits of implementing SFCMs for data pipelines using these patterns.

+ A class can have multiple SFCMs, and therefore can be initialized in different ways from different source types and parameters. The reader can easily see the types from which it can be constructed.
+ When creating [dataclass](https://docs.python.org/3/library/dataclasses.html) (or [pydantic](https://docs.pydantic.dev/latest/)/[attrs](https://www.attrs.org/en/stable/)) types, they allow you to pass non-data parameters and avoid using `__post_init__` or requiring partial initialization states.
+ These methods offer a superior alternative to overriding constructor methods when using inheritance. Subclasses can call SFCMs of parent classes explicitly instead of using `super()` or otherwise referring to the parent class. This is especially useful when inheriting from built-in types such as collections or exceptions.

In the following sections, I will discuss some situations where SFCMs may be particularly useful, elaborate on strategies for building complex object structures, and then discuss how these patterns fit within larger data pipelines.


# Python Examples

Now I will show some examples of static factory constructor methods in Python. We typically create these methods using the `@classmethod` parameter, and they always return an instance of the containing class.

For example purposes, let us start by creating the most basic container object: a coordinate with `x` and `y` attributes. The `__init__` method simply takes `x` and `y` parameters and stores them as attributes. I include `x` and `y` as part of the definition to support type checkers. I also create a basic `__repr__` method for readability.

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

The implementation of the `__init__` default constructor method is important because it must be called any time you want to instantiate the object. Ideally, it should ONLY be responsible for inserting data attributes. Most of the time, all attributes should be required.

Note that the `__init__` created by the [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module is perfect for this, so I highly recommend using it. This definition is exactly equivalent to the above.

    import dataclasses

    @dataclasses.dataclass
    class Coord:
        x: float
        y: float

We can instantiate this type using `__init__` by passing both `x` and `y` in the calling function.

    Coord(0.0, 0.0)

All of the following examples will start with this type.

## Useful Situations

For practical purposes, I have identified several situations in which SFCMs may be useful to you, whether or not you apply other design patterns I have discussed. I will give Python examples for each of these situations and then discuss approaches.

+ The type needs to be constructed in multiple ways, each using different logics or source data.
+ Substantial logic is required to instantiate the type but that logic is only used for that purpose.
+ You want to avoid situation-specific or inter-dependent defaulted parameters.
+ You need to return multiple instances of the type.
+ You are using an existing constructor of an inherited type.

I will now give examples for each of these situations.

#### Alternative Instantiation Methods

The most obvious situation in which you may want to use a SFCM is when there are multiple alternative methods for creating an instance. The following two methods allow you to create the `Coord` object from either cartesian or [polar coordinates](https://www.mathsisfun.com/polar-cartesian-coordinates.html). Note that the `from_xy` method here enforces type consistency by calling `float`, which would also raise an exception if the `x` or `y` arguments are not coercible. The `from_polar` method is also enforcing type consistency implicitly through the use of `math.cos` and `math.sin`, which both return floating point numbers.

        @classmethod
        def from_xy(cls, x: float, y: float) -> typing.Self:
            return cls(
                x = float(x),
                y = float(y),
            )

        @classmethod
        def from_polar(cls, r: float, theta: float) -> typing.Self:
            return cls(
                x = r * math.cos(theta),
                y = r * math.sin(theta),
            )

An alternative approach would be to place the `float` calls inside of the `__init__` constructor. With that approach, `from_polar` would be forced to execute that logic even though it is not necessary because `math.sin` and `math.cos` already create type safety. Of course, in this example the call to `float` is computationally inexpensive, but some types may require more complicated validation or conversion that will not be nessecary for every possible way that the object can be instantiated.

#### Type-specific Instantiation Logic

SFCMs are a good option when instantiation requires substantial logic but the logic is only used for that purpose. The instantiation logic should live as part of the type, and the SFCM is a good place to put it.

For example, say we need to sample points from a gaussian distribution by creating a new random coordinate instance according to some parameters. The instantiation logic involves calling `random.gauss`, and so we put that inside a new `from_gaussian` method. In contrast to the default constructor, none of the parameters here are actually stored as data - only the data generated from the random functions. You would instantiate the new object with the expression `Coord.from_gaussian(..)`.

        @classmethod
        def from_gaussian(cls,
            x_mu: float, 
            y_mu: float, 
            x_sigma: float, 
            y_sigma: float
        ) -> typing.Self:
            return cls(
                x = random.gauss(mu=x_mu, sigma=x_sigma),
                y = random.gauss(mu=y_mu, sigma=y_sigma),
            )

Most other solutions to this situation are complicated: you either require the calling function to implement this logic or add it to `__init__` with some complicated defaulted parameters.

#### Situation-specific Parameters

SFCMs are a good alternative to the situation where you have an `__init__` method where the behavior of some parameters vary according to the values of other parameters. Instead, create multiple situation-specific SFCMs for use in different situations.

For example, say we want to create instances of points that lie along the line `x`=`y`. We can create a new instance from a single parameter in this case, because both values can be calculated given the value of x.

        @classmethod
        def from_xy_line(cls, x: float) -> typing.Self:
            return cls(x=x, y=x)

If we wanted a simple way to create the origin coordinate, we can create a method that accepts no parameters.

        @classmethod
        def from_zero(cls) -> typing.Self:
            return cls(x=0.0,y=0.0)

In this way, the function signatures themselves make it clear which parameters are needed for a given situation.

#### Returning Multiple Instances

In cases where it may be too tedious to create [custom collection types](dsp1_data_collection_types.html), SFCMs can be used to return collections of the implementing type. As an example, say we want to return a set of coordinates created by the reflection of the original point across the x and y axes. In that case, we can return a set of instances representing the desired coordinates.

        @classmethod
        def from_reflected(cls, x: float, y: float) -> typing.List[typing.Self]:
            return [
                cls(x = x, y = y),
                cls(x = -x, y = y),
                cls(x = x, y = -y),
                cls(x = -x, y = -y),
            ]


#### Calling a Parent Constructor Method

SFCMs are good to use when you want to use the `__init__` method of the parent class and overriding `__init__` could have unintended side effects. 

Say that we want to create a 2-dimensional vector type that contains the same data as `Coord` but has some additional methods for vector operations that are not typically defined for coordinates. The data is not different, and therefore we should not define a new `__init__` method. If any other logic is required, we can add that to the SFCM.

    class Vector2D(Coord):
        @classmethod
        def unity(cls) -> typing.Self:
            return cls(x=1.0, y=1.0)
        
        def dot(self, other: typing.Self) -> float:
            return (self.x * other.x) + (self.y * other.y)

Another situation where this might arise is when inheriting from built-in types when you do not want to risk altering the behavior of the original type. In this case, we can call the `Coord.from_gaussian` method and return a list of `Coord` types in the container `from_gaussian` method. This approach makes it easy and safe to inherit from built-in collection types.

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

You could also use this as an alternative to returning multiple instances from the `Coord` type.

        @classmethod
        def from_reflected_points(cls, x: float, y: float) -> typing.Self:
            return cls([
                Coord(x = x, y = y),
                Coord(x = -x, y = y),
                Coord(x = x, y = -y),
                Coord(x = -x, y = -y),
            ])

## Inter-dependent SFCM Calls

It is often helpful to be able to instantiate an object with varying levels of specificity, depending on the situation. In this case, you can create multiple SFCMs that call each other successively, effectively chaining the instantiation logic down the call stack. If you know that the instantiation methods will build on each other, this approach is clearer than creating a pool of helper methods that are selectively invoked in every SFCM. 

This approach offers some theoretical perspective. Beyond the ability to instantiate an object in different ways, you can start to think in terms of a tree of successive SFCMs which all lead back to the `__init__` method. Every time you need a new constructor method, it is worth thinking about where it could exist in this tree.

<img style="width:80%;" class="figure-center" src="https://storage.googleapis.com/public_data_09324832787/blog/sfcm_heirarchy.svg" /> 

Let us return to the example `from_xy`. Recall that this simple method actually applies a level of validation: by calling `float`, we ensure the the input values are coercable to floats.

        @classmethod
        def from_xy(cls, x: float, y: float) -> typing.Self:
            return cls(
                x = float(x),
                y = float(y),
            )

Now revisit the definition of `from_xy_line`. In the original definition, we simply assigned the input value to both `x` and `y` of the new object. Instead of calling `__init__`, we can call `from_xy` to add the same validation functionality to this method as well.

        @classmethod
        def from_xy_line(cls, x: float) -> typing.Self:
            return cls.from_xy(x=x, y=x)

Now say we may want to add an additional validation step where we ensure `x` and `y` are finite. We can create a new method `from_xy_finite` which checks for finiteness and also calls `from_xy` to perform the floating point validation. In this way, `from_xy_finite` is actually adding to the functionality of `from_xy` without overlap.

        @classmethod
        def from_xy_finite(cls, x: float, y: float) -> typing.Self:
            # raise exception if values are invalid
            invalids = (float('inf'), float('-inf'))
            if x in invalids or y in invalids:
                raise ValueError(f'x and y must be finite values.')
            
            return cls.from_xy(x=x, y=y)

If we revisit the SFCM `from_zero`, we can see that it still should be calling the `__init__` constructor because we can gaurantee that the inputs are valid floating point numbers, and therefore do not benefit from calling any other SFCM.

    @classmethod
    def from_zero(cls) -> typing.Self:
        return cls(x=0.0,y=0.0)

Taken together, we can think of these SFCM dependencies as a tree where all methods call `__init__` at the lowest level. Creating a new SFCM is a matter of determining which operations are needed for instantiation.

## Data Pipelines Using FCMs

I have [written more extensively](dsp1_data_collection_types.html) about this in the past, but I think it is worth noting how SFCMs fit within larger data data pipelines. If we structure our code as a set of immutable data types and the transformations between them, we can do most of the transformation work inside SFCMs.

A good design principle is that downstream types should know how to construct themselves, and that logic can be placed in SFCMs. For instance, we have our `Coord` object from the previous example. Now say we may want to transform these existing Cartesian coordinates to radial coordinates. We can create a new type `RadialCoord` to represent this new data, and write the transformation code in a SFCM `from_cartesian`. The radial coordinate can be constructed using either the `__init__` method with the `r` and `theta` parameters or the `from_cartesian` SFCM, which accepts a `Coord`.
    
    @dataclasses.dataclass
    class RadialCoord:
        r: float
        theta: float

        @classmethod
        def from_cartesian(cls, coord: Coord) -> typing.Self:
            return cls(
                r = math.sqrt(coord.x**2 + coord.y**2),
                theta = math.atan2(coord.y/coord.x),
            )

We can create a radial coordinate using a `Coord` instance.

    c = Coord(5, 4)
    rc = RadialCoord.from_cartesian(c)

Alternatively, we could make this accessible as a call to `to_radial(..)`.

    @dataclasses.dataclass
    class Coord:
        x: float
        y: float

        def to_radial(self) -> RadialCoord:
            return RadialCoord.from_cartesian(self)

The latter step increases the coupling between the two objects, but, in exchange, the resulting interface is quite clean. Placing all of the construction logic in the downstream type's SFCM means that the coupling is weak and can be removed from the upstream type very easily.

    Coord(5, 5).to_radial()

You can imagine how this pattern could be ubiqutuous throughout your data pipelines.

## In Conclusion

SFCMs allow you to write module and extensible data pipelines, and are especially useful when building pipelines composed of immutible types and their transformations. Most of my own work relies heavily on this pattern, and I hope you can benefit too!

I have also mentioned using SFCMs in a number of other articles that might be helpful:

+ [Patterns and Antipatterns for Dataclasses](dsp0_patterns_for_dataclasses.html)
+ [Patterns for data collection types](dsp1_data_collection_types.html)
+ [Are Data Frames too flexible?](zods0_problem_with_dataframes.html)




