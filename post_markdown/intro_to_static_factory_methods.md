---
title: "Introduction to Static Factory Constructor Methods"
subtitle: "Change the way you initialize custom types in Python."
date: "June 14, 2024"
id: "intro_to_static_factory_constructor_methods"
blogroll_img_url: "https://storage.googleapis.com/public_data_09324832787/static_factory_methods.svg"
---

In this article, I show how we can use static factory constructor methods to initialize types instead of including complicated logic in `__init__` methods. A ***static factory constructor method*** (SFCM hereafter) is simply a static method which returns an instance of the object that implements it. A single class can have multiple SFCMs that accept different parameters, and the methods should contain any logic needed to initialize the object. While these methods are common in many software engineering applications, I believe they are especially important in data analysis code because they fit well with the way data flows through your program.

![Static factory constructor method diagram.](https://storage.googleapis.com/public_data_09324832787/static_factory_methods.svg)

Here are a few benefits of implementing SFCMs for any type.

+ A class can have multiple SFCMs, and therefore can be initialized in different ways from different source types. This means that the reader can easily see in the source code the various way the object may be initialized and the data from which it can be derived.
+ SFCM paramters can include data that is not intended to be stored in the object but is otherwise needed for initalization. This reduces the cases where partial/multi-stage initialization is the best option.
+ SFCMs are a superior alternative to overriding constructor methods when using inheritance. Subclasses can call SFCMs of parent classes explicitly instead of using `super()` or otherwise referring to the parent class (which may be especially useful in multiple-inheritance scenarios). This solves a number of challenges involved when inheriting from built-in types.

If we look at the flow of data through our programs, you can see that SFCMs can handle all logic involved with transforming data from one type to another. As all data pipelines essentially follow the structure shown in the diagram below, we can see how SFCMs could be ubiquitous in your code.

![Data flow control diagram.](https://storage.googleapis.com/public_data_09324832787/sfcm_data_flow.svg)

## Some Examples

Now I'll show some examples of static factory constructor methods in Python. We typically create these methods using the `@classmethod` parameter, and they always return an instance of the containing class.

For example purposes, let us start by creating the most basic container object: a coordinate with `x` and `y` attributes. Users may more easily replicate this behavior using the [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module, but in this case the definition is very simple anyways. The `__init__` method simply takes `x` and `y` parameters and stores them as attributes. I include `x` and `y` as part of the definition to support type checkers. I also create basic `__repr__` and `__add__` methods.

    import typing
    import math

    class Coord:
        x: float
        y: float
        def __init__(self, x: float, y: float):
            self.x = x
            self.y = y

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}(x={self.x}, y={self.y})'

        def __add__(self, other: typing.Self) -> typing.Self:
            return self.__class__(
                x = self.x + other.x,
                y = self.y + other.y,
            )

### Initializing with Common Values

We can instantiate the object using `__init__` by passing both `x` and `y` in the calling function.

    Coord(0.0, 0.0)

The simplest possible static factory method could create an instance using no parameters at all. The coordinate where `x` and `y` equal zero is especially important in many scenarios, so let us say we want to create a static factory method so that every calling function need not use the literal 0.0 as parameters.
        
        @classmethod
        def zero(cls) -> typing.Self:
            return cls(x=0.0,y=0.0)

Calling `Coord.zero()` is cleaner than assigning `x = 0.0` and `y = 0.0` every time you need this coordinate.

### Use Non-data Parameters

Now let us say we want a static factory method that includes data not meant to be stored in the object. Adding a `verbose` flag to the `__init__` method makes it a little unclear how it may be used. If the parameter is included in `__init__` for an otherwise data-only class, the user may assume that value will be stored and thus used later. If the flag is only included in the static factory method but not in the `__init__` method, we can guess that it may only be used on instantiation.

        @classmethod
        def new(cls, x: float, y: float, verbose: bool = False) -> typing.Self:
            o = cls(
                x = x,
                y = y,
            )
            if verbose:
                print(f'New {cls.__name__} was created: {o}')
            return o



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

### Co-dependent Parameters

At times, the value of some parameters might be inferred or dependent on other parameters. This logic could always be done outside instantiation, but, if it is needed frequently enough, it might be worth adding to the same static factory method. Let us say we want to create a coordinate from a given value of `x` where `y` is a function of `x`. The static factory method needs only to include `x` in this case because we can calculate `y` from `x`. The following static factory method could be used to create a new instance of `Coord` from `x`.

        @classmethod
        def from_quadratic(cls, x: float) -> typing.Self:
            return cls(x=x, y=x**2)

Static factory methods can allow for more complicated relationships between the inputs and stored variables. In this example, we can instantiate the coord from [polar coordinates](https://www.mathsisfun.com/polar-cartesian-coordinates.html), and neither input is stored directly.

        @classmethod
        def from_polar(cls, r: float, theta: float) -> typing.Self:
            return cls(
                x = r * math.cos(theta),
                y = r * math.sin(theta),
            )

    Coord.from_polar(1.0, math.pi / 3)

In the output we can see the computed result.

    Coord(x=0.5000000000000001, y=0.8660254037844386)

From these simple examples you can imagine a wide range of use cases where this might be the best solution. I will now show some of the most common.

### Instantiating Child Classes

While inheritance should be used sparingly (consider composition-oriented approaches instead), they can be great in situations where you want to extend a class by adding new methods - including SFCMs. In this example, say we want to create a new coordinate type representing a coordinate which is derived from other coordinates. I create a new subclass with a new SFCM that relies on the previously created `.zero()` method. Only the new type has access to the new SFCM, but it can rely on SFCMs from the base class.

    class ResultCoord(Coord):
        '''Coordinate that results from an operation between other coordinates.'''
        @classmethod
        def from_sum_of_coords(cls, coords: typing.List[Coord]) -> typing.Self:
            return sum(coords, start=cls.zero())

    ResultCoord.from_sum_of_coords([Coord(0,1), Coord(10,4), Coord(11, 100)])

### Returning Multiple Instances

In cases where it may be too tedious to create [custom collection types](dsp1_data_collection_types.html), SFCMs can be used to return collections of the implementing type. As an example, say we want to return a set of coordinates created by the reflection of the original point across the x and y axes. In that case, we can return a set of instances representing the desired coordinates.

        @classmethod
        def from_reflected(cls, x: float, y: float) -> typing.List[typing.Self]:
            return [
                cls(x = x, y = y),
                cls(x = -x, y = y),
                cls(x = x, y = -y),
                cls(x = -x, y = -y),
            ]

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




