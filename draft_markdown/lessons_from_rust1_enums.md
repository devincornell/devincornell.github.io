---
title: "Lessons from Rust 1: Enums for Errors and Missing Data"
subtitle: "Consider using patterns that emulate the Option and Result enums from Rust to make your code more robust and readable."
date: "Sept 27, 2023"
id: "lessons_from_rust1_enums"
---

The Rust programming language has taken the award for "most loved programming language" in the [Stack Overflow Developer Survey](https://survey.stackoverflow.co/2022#overview) since 2016. The power of Rust comes in that it is nearly as fast as C++ without the potential issues that come with pointers and manual memory management. Whether or not you can convince your stakeholders to write Rust code, there are some lessons we can apply to our data pipelines in any language. In the next several blog articles I will provide some patterns that use ideas from the Rust language to improve your data science code in any language.

+ (current article) Lessons from Rust 1: Enums for Errors and Missing Data
+ (future article) Lessons from Rust 2: Composition over Inheritance

The first pattern I will discuss is the use of enums to indicate missing data and errors. Rust has a robust infrastructure for handling enum types compared to languages like Python or C++, but there are two particular built-in enums that may be useful for data pipelines: [`Option[T]`](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html?highlight=Option%3C#the-option-enum-and-its-advantages-over-null-values) and [`Result[T, E]`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html?highlight=Result%3C#recoverable-errors-with-result). The `Option[T]` enum is used to represent a value that may or may not be present (equivalent of None in Python), and the `Result` enum is used to represent a return value that is either a value or an error. 

### When `None` is a Valid Return Value

Our first example will cover the case when you need to access some variable for which `None` might be considered a valid value but there is also a case where the return value may be alltogether invalid. This breaks typical convention where we often use `None` to represent invalid values. The strong typing system in rust necessitates the use of the wrapper class because `None` cannot be a valid integer type, but we can adapt it for our scenario even in weakly typed environments.

For example purposes we create an object that stores a singele variable that can either be an integer or a `None` value. For a particular application we want to get that value, but we consider it to be invalid if it is not None and it is less than zero.

    @dataclasses.dataclass
    class MyObj:
        x: typing.Optional[int]

We can access the attribute directly, but then we would have to check the value downstream to see if it is negative - it would be better to indicate the value is invalid when we access it. Perhaps the most Pythonic solution to this problem is to use exceptions. We create an accessor function that raises a `ValueError` exception if the value is negative and passes the value otherwise.

    @dataclasses.dataclass
    class MyObj:
        x: typing.Optional[int]
        
        def access_x_exception(self) -> typing.Optional[int]:
            if self.x is None or self.x >= 0:
                return self.x
            else:    
                raise ValueError('x is negative so it is invalid')

As a use case, lets say we have a list of these objects and for each object we want to print the value if it is valid, and otherwise state that it is invalid. We would handle this the same way we handle any other exception.

    def print_values_exception(objs: typing.List[MyObj]) -> None:
        for obj in objs:
            try:
                print(obj.access_x_exception())
            except ValueError:
                print('x is invalid')

The challenge with this approach is that the user has no way of recognizing that this function will raise an exception unless they read the implementation or details of the documentation, and the point where it should be handled is not clear.

A better solution that emulates the `Option[T]` enum would be to create custom wrapper objects to indicate whether the value is valid aside from looking at the actual value. By adding type hints for this wrapper object we can indicate to the reader exactly where the error will be handled. We can create the wrapper types using generic type hints, and create a union type hint (using `typing.Union`) which indicates the accessor might return either value. Using the dynamic duck typing scheme, we can check which type of object it is by accessing the `is_ok` attribute (there are a number of ways this could be handled), and note that I added dummy property methods so that this design will pass strict typing checks.

    T = typing.TypeVar("T")
    E = typing.TypeVar("E")

    @dataclasses.dataclass
    class Valid(typing.Generic[T]):
        data: T
        is_ok: bool = True
        
        @property
        def error(self) -> typing.NoReturn:
            raise AttributeError(f'{self.__class__.__name__} has no attribute "error"')
        
    @dataclasses.dataclass
    class Err(typing.Generic[E]):
        error: typing.Optional[E] = None
        is_ok: bool = False
        
        @property
        def data(self) -> typing.NoReturn:
            raise AttributeError(f'{self.__class__.__name__} has no attribute "data"')
        
    Result = typing.Union[Valid[T],  Err[E]]

We then create a new accessor which returns one of the new type hints we created.

    @dataclasses.dataclass
    class MyObj:
        x: typing.Optional[int]
        
        def access_x(self) -> Result[typing.Optional[int], None]:
            if self.x is None or self.x >= 0:
                return Valid(self.x)
            else:    
                return Err()
                
In the use case, we first check if the results is valid and then either print the value or the error information (which will always be `None` in this example).

    def print_values(objs: typing.List[MyObj]) -> None:
        for obj in objs:
            result = obj.access_x()
            if result.is_ok:
                print(result.data)
            else:
                print(f'x is invalid: {result.error}')

# Multiple Error Types

In some cases, there may be multiple situations in which the accessed values are invalid, and we want to handle them differently. As a use case, let us say we need to calculate the mean value of an attribute across a set of objects. The `sum` function cannot accept `None` values, and so we should omit those values from the mean; in the case where the value is negative, we want to replace it with a `0`.

The exception approach is fairly simple: we could create custom exceptions, or, perhaps less optimally, use two existing exceptions to indicate the different scenarios (we will do the latter for this example, although I would encourage the former in most cases).

    @dataclasses.dataclass
    class MyObj:
        x: typing.Optional[int]
            
        def access_x_notnone_exception(self) -> int:
            if self.x is None:
                raise TypeError('x is None so it is invalid')
            elif self.x < 0:
                raise ValueError('x is negative so it is invalid')
            else:
                return self.x

In the use case we simply catch the exceptions and handle them as expected.

    def average_values_exception(objs: typing.List[MyObj]) -> float:
        values = list()
        for obj in objs:
            try:
                values.append(obj.access_x_notnone_exception())
            except ValueError:
                values.append(0)
            except TypeError:
                pass
        return sum(values)/len(values)

The alternative approach would be to re-use the wrapper objects from before but provide a custom error enum to indicate which type of error was encountered. The enum module can be used to create a new enum type describing our two error types.

    import enum
    class MyErrorType(enum.Enum):
        IS_NONE = enum.auto()
        IS_NEGATIVE = enum.auto()

The accessor just performs the checks and returns invalid objects with teh expected error type.

    @dataclasses.dataclass
    class MyObj:
        x: typing.Optional[int]

        def access_x_notnone(self) -> Result[int, MyErrorType]:
            if self.x is None:
                return Err(MyErrorType.IS_NONE)
            elif self.x < 0:
                return Err(MyErrorType.IS_NEGATIVE)
            else:
                return Valid(self.x)

The client can then check the error type and handle it appropriately.

    def average_values(objs: typing.List[MyObj]) -> float:
        values = list()
        for obj in objs:
            v = obj.access_x_notnone()
            if v.is_ok:
                values.append(v.data)
            elif v.error is MyErrorType.IS_NEGATIVE:
                values.append(0)
        return sum(values)/len(values)

To see the true value of this approach, imagine we are propogating these types of errors up multiple levels through a callstack. For example, we could make a wrapper class that wraps another wrapper class that accesses the `ValidOrInvalid` type we defined above, and it includes a method to access the original inner value. When appropriate type hints are used, the client knows when to expect a value that might possibly be invalid, and to be prepared to handle that instance when using the value. This is essentially an elaborate extension of type checking using Python's `typing.Optional[T]` type hint that allows for multiple error types.

    @dataclasses.dataclass
    class MyObjWrapper:
        obj: MyObj
        def access_value(self) -> Result[int, MyErrorType]:
            return self.obj.access_x_notnone()
        
    @dataclasses.dataclass
    class MySecondWrapper:
        obj_wrapper: MyObjWrapper
        def access_value_wrapper(self) -> int:
            val = self.obj_wrapper.access_value()
            if val.is_ok:
                return val.data
            else:
                raise ValueError('SOMETHING BAD HAPPENED')

Precisely because exceptions are exceptional, they break the regular control flow in a way that may obscure important cases that you want to handle explicitly.


