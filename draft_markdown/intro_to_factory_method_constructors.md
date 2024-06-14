---
title: "Introduction to Static Factory Methods"
subtitle: "A brief overview of methods used to initialize custom types."
date: "June 14, 2024"
id: "intro_to_static_factory_methods"
blogroll_img_url: "https://storage.googleapis.com/public_data_09324832787/dataclasses.svg"
---

Over the last several decades, we have seen a shift towards programming patterns that place data first. The strong interest in data analysis means that young programmers are being trained to think of objects as containers for data rather than maintainers of system state. At its core, this is a shift away from complicated inheritance heirarchies towards using classes more like structs, or basic data containers with minimal inheritance and constructors that primarily serve to pass data into the containers. Instead, analysts can use factory constructor method patterns to instantiate data objects from different types and with different argument types. In this article I will discuss the advantages of using these patterns and show some real-world applications where these are likley the most elegant solution.

A ***static factory method*** is simply a class method which returns an instance of the object. A single class can have multiple static factory methods, and they may all accept different combinations of parameters. These are some of the benefits of using static factory methods over overriding `__init__`.

+ The object knows how to create itself - it can contain any logic used to prepare the data to be stored.
+ Classes can include multiple methods for instantiation; that is, they can be created form multiple different sources.
+ The reader can tell from which kinds of data the objects are derived
+ It is explicit: `__init__` functions need not contain large parameter sets to determine the method for construction.
+ Paramters can include data that is not intended to be stored in the object.


## Some Examples

Now I'll show some examples of static factory methods in Python. We typically create these methods using the `@classmethod` parameter, and they always return an instance of the containing class.

### Initializing Common Values

For example purposes, let us start by creating the most basic container object: a coordinate with `x` and `y` attributes. Users may more easily replicate this behavior using the [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module, but in this case the definition is very simple anyways. The `__init__` method simply takes `x` and `y` parameters and stores them as attributes. I include `x` and `y` as part of the definition to support type checkers.

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

We can instantiate the object using `__init__` by passing both `x` and `y` in the calling function.

    Coord(0.0, 0.0)

The simplest possible static factory method could create an instance using no parameters at all. The coordinate where `x` and `y` equal zero is especially important in many scenarios, so lets say we want to create a static factory method so that every calling function need not use the literal 0.0 as parameters.
        
        @classmethod
        def zero(cls) -> typing.Self:
            return cls(x=0.0,y=0.0)

Calling `Coord.zero()` is cleaner than assigning `x = 0.0` and `y = 0.0` every time you need this coordinate.

### Non-data Parameters

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

As another example, imagine we want to add validation code when instantiating in some scenarios, but not in others. One approach could be to add a `validate: bool` flag to the constructor, but we face the same readability point mentioned above. Instead we can use a static factory method: when the user does not need to validate the input (or perhaps the first case where they might expect invalid data), they can use `__init__`, otherwise, they can use a static factory method.

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

Static factory methods can allow for more complicated relationships between the inputs and stored variables. In this example, we can instantiate the coord from [polar coordinates](https://www.mathsisfun.com/polar-cartesian-coordinates.html), and neither inputs are stored directly.

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




## High-level Application: Custom Exceptions

Now I will discuss one higher-level application of static factory methods: creating custom exceptions.

Start with an example where we want to create a custom exception that includes additional data to be used when it is caught up the call stack. We see this, for instance, in the `requests` module when raising generic HTTP errors: the request and response (along with HTTP error code) are attached to the exception type. One way to implement this is to override `__init__` to call `super().__init__` and then add the attribute dynamically. Every class can only have one `__init__` method, and so all users of this exception must provide the same data; in this case, only the error code, but in more complicated scenarios the downstream user may need to do more work.

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

Note that we could create an exception heirarchy tree that allows us to get more specific, but too many custom exceptions can add a lot of clutter to your codebase.

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

Static factory methods can be the best option in a wide range of scenarios, and I recommend considering them in cases where you feel limited by having a single `__init__` function or you are doing a lot of work to transform data prior to instantiation.



