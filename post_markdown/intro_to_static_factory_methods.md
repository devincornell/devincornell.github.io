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

If we look at the flow of data through our programs, you can see that SFCMs can contain all logic involved with transforming data from one type to another. As all data pipelines essentially follow the structure shown in the diagram below, we can see how SFCMs could be ubiquitous throughout your data pipelines.

![Data flow control diagram.](https://storage.googleapis.com/public_data_09324832787/sfcm_data_flow.svg)



I have written at length why it is best to use immutable custom types to represent intermediary data formats, and SFCMs can play the role of converting the data from one type to another. Here are a few benefits of implementing SFCMs for data pipelines using these patterns.

+ A class can have multiple SFCMs, and therefore can be initialized in different ways from different source types and parameters. The reader can easily see the types from which it can be constructed.
+ When creating [dataclass](https://docs.python.org/3/library/dataclasses.html) (or [pydantic](https://docs.pydantic.dev/latest/)/[attrs](https://www.attrs.org/en/stable/)) types, they allow you to pass non-data parameters and avoid using `__post_init__` or requiring partial initialization states.
+ These methods offer a superior alternative to overriding constructor methods when using inheritance. Subclasses can call SFCMs of parent classes explicitly instead of using `super()` or otherwise referring to the parent class. This is especially useful when inheriting from built-in types such as collections or exceptions.










The SFCM always belongs to the new type being constructed, and therefore building data pipelines is a matter of defining a source type (the original data or an intermediary type), defining the downstream type, and then building the SFCM to facilitate the transformation from one to another.






## Next Section

As the project grows and the objectives change, pipelines and types may be added or removed.




to adapt to the needs of the project.

This creates a series of interlocking pipelines which intersect as types, which shows the various ETL data pipelines required to transform the data from the source type to an output type - a figure, table, or anything else. 











Here are a few benefits of implementing SFCMs for any type.




## When to use SFCMs

+ The type may be constructed in multiple ways, each using different logics or source data.
+ Substantial logic is required to instantiate the type but that logic is only used for that purpose.
+ You want to avoid situation-specific or inter-dependent defaulted parameters.
+ You are using an existing constructor of an inherited type.

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

SFCMs are particularly useful for addressing challenges in the following situations.

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

SFCMs are good to use when you want to use the `__init__` method of the parent class without referencing `super().__init__`.

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



## SFCM Dependency Trees

All of the SFCM examples above have called the `__init__` constructor to actually instantiate the object. The fact that SFCMs are class methods, however, suggests that they can call each other. 

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

<img style="width:80%;" class="figure-center" src="https://storage.googleapis.com/public_data_09324832787/blog/sfcm_heirarchy.svg" /> 








### Optional Validation and Type Conversion
SFCMs allow us to apply input data validation on an as-needed basis. For instance, we can call `float` to ensure that `x` and `y` are of float type, and the SFCM will raise an exception if either value is not coercible. Other SFCMs can buld on this method to make the same gaurantees - for instance, `from_xy_line` might benefit from building on this method to gaurantee `x` and `y` are of type `float` rather than `int`,  but methods like `from_zero` may not need it because they assign the value `0.0` directly and thus we wouldn't want to incur the validation overhead. It is all about making selective 

        @classmethod
        def from_xy(cls, x: float, y: float) -> typing.Self:
            return cls(
                x = float(x),
                y = float(y),
            )







### Situational Validation

As another example, imagine we want to add validation code when instantiating in some scenarios, but not in others. One approach could be to add a `validate: bool` flag to the constructor, but we face the same readability point mentioned above. , we can use a static factory method: when the user does not need to validate the input (or perhaps the first case where they might expect invalid data), they can use `__init__`, otherwise, they can use a static factory method.

Here I demonstrate by creating a function which first makes sure that both `x` and `y` are finite values. This method should be used when coordinates with infinite values may be expected but not desired.

        @classmethod
        def new_finite(cls, x: float, y: float) -> typing.Self:
            invalids = (float('inf'), float('-inf'))
            if x in invalids or y in invalids:
                raise ValueError(f'x and y must be finite values.')
            return cls(
                x = x,
                y = y,
            )


### Instantiating Child Classes

While inheritance should be used sparingly (consider composition-oriented approaches instead), they can be great in situations where you want to extend a class by adding new methods - including SFCMs. In this example, say we want to create a new coordinate type representing a coordinate which is derived from other coordinates. I create a new subclass with a new SFCM that relies on the previously created `.zero()` method. Only the new type has access to the new SFCM, but it can rely on SFCMs from the base class.

    class ResultCoord(Coord):
        '''Coordinate that results from an operation between other coordinates.'''
        @classmethod
        def from_sum_of_coords(cls, coords: typing.List[Coord]) -> typing.Self:
            return sum(coords, start=cls.zero())

    ResultCoord.from_sum_of_coords([Coord(0,1), Coord(10,4), Coord(11, 100)])


### Inheriting from Built-in Types

SFCMs can be especially useful when creating types that inherit from built-in types. The following class inherits from the built-in `typing.List` type and is intended to store coordinates. The new type acts like a regular list except for the addition of the SFCM, which is especially useful because it can call the constructor (or another SFCM) of the contained type. Whenever the new collection appears, the reader knows it should contain only coordinates and should be created using a SFCM.

    class Coords(typing.List[Coord]):
        @classmethod
        def from_reflected_points(cls, x: float, y: float) -> typing.List[typing.Self]:
            return cls([
                Coord(x = x, y = y),
                Coord(x = -x, y = y),
                Coord(x = x, y = -y),
                Coord(x = -x, y = -y),
            ])
    Coords.from_reflected_points(1, 1)


### Inheriting from Built-in Types

SFCMs can be especially useful when creating types that inherit from built-in types. The following class inherits from the built-in `typing.List` type and is intended to store coordinates. The new type acts like a regular list except for the addition of the SFCM, which is especially useful because it can call the constructor (or another SFCM) of the contained type. Whenever the new collection appears, the reader knows it should contain only coordinates and should be created using a SFCM.

    class Coords(typing.List[Coord]):
        @classmethod
        def from_reflected_points(cls, x: float, y: float) -> typing.List[typing.Self]:
            return cls([
                Coord(x = x, y = y),
                Coord(x = -x, y = y),
                Coord(x = x, y = -y),
                Coord(x = -x, y = -y),
            ])
    Coords.from_reflected_points(1, 1)



## High-level Application: Custom Exceptions

Now I will discuss one higher-level application of static factory methods: creating custom exceptions.

Start with an example where we want to create a custom exception that includes additional data to be used when it is caught up the call stack. We see this, for instance, in the `requests` module when raising generic HTTP errors: the request and response (along with HTTP error code) are attached to the exception type.

### Overriding `__init__`

One way to implement this is to override `__init__` to call `super().__init__` and then add the attribute dynamically. Every class can only have one `__init__` method, and so all users of this exception must provide the same data; in this case, only the error code, but in more complicated scenarios the downstream user may need to do more work.

    class MyError1(Exception):
        error_code: int

        def __init__(self, error_code: int):
            super().__init__(f'Received error with code {error_code}.')
            self.error_code: int

The function that wants to raise this exception should include the error code then.

    try:
        raise MyError1(500)
    except MyError1 as e:
        print(e.error_code)

Note that we could create an exception hierarchy tree that allows us to get more specific, but too many custom exceptions can add a lot of clutter to your codebase.

### The static factory method approach

Alternatively, we can create a static factory method that will instantiate the object using the default constructor and then bind the additional data. This way we do not need to provide `__super__`, and all subclasses can either use this method or define another, more specific method. Here I create a low-level method to bind the additional data, then two higher-level methods to generate the error code more specifically.

    class MyError2(Exception):
        error_code: int
        
        @classmethod
        def with_msg_code(cls, message: str, code: int) -> typing.Self:
            o = cls(message)
            o.error_code = code
            return o

        @classmethod
        def from_error_code(cls, code: int) -> typing.Self:
            return cls.with_msg_code(f'Encountered error {code}.', code=code)

The ability to create multiple static factory methods means we can further implement code-specific static factory methods that absolve the calling function from needing to provide the method directly. We simply use the method associated with the error we want to raise.
        
        @classmethod
        def from_io_error(cls) -> typing.Self:
            code = 500
            return cls.with_msg_code(f'Encountered IO error (error code {code}).', code=code)

We can also abstract away the error codes entirely, and check error code cases using additional properties.

        @property
        def is_io_error(self) -> bool:
            return self.error_code is 500

The benefit of this approach is that error codes can all be internally managed by the exception type and need not be provided by a calling or excepting function. We can continue to use a single exception type, and simply extend that type when we want to handle more cases. This supports a much higher level of logic complexity in the exception handling function.


## In Conclusion

SFCMs are widely applicable in a number of data-oriented software design patterns, and I highly recommend integrating them into your workflow.

I have also mentioned using SFCMs in a number of other articles you can check out.

+ [Are Data Frames too flexible?](zods0_problem_with_dataframes.html)
+ [Patterns and Antipatterns for Dataclasses](dsp1_data_collection_types.html)
+ [Patterns for data collection types](dsp1_data_collection_types.html)




