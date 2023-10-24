---
title: "Lessons from Rust 2: Stronger Typing"
subtitle: "Use the ownership pattern from Rust to increase_safety."
date: "Sept 30, 2023"
id: "lessons_from_rust2_typing"
---

Let's face it - no matter effective we are at writing data pipelines in dynamically typed languages such as R and Python, the lack of a strong typing system puts us at risk of introducing runtime errors that may not be obvious until late in development, if at all. I recently read [an article](https://www.svix.com/blog/strong-typing-hill-to-die-on/) by Tom Hacohen that discusses advantages of strong typing systems, and I tend to agree with many of those points from my own experiences with strongly and weakly typed langauges. Weakly typed languages free the programmer to think about big-picture designs rather than focusing on every detail, but, in Tom's words, "Writing software without types lets you go at full speed. Full speed towards the cliff." Rust's compiler is famously verbose and strict by default, and proponents often conclude that "if you can get it to compile, it usually works the first time." There are big advantages to strong typing systems, and we can take advantage of some of those benefits in dynamically typed languages using type hints and static type checkers that have become very popular over the last several years.

In Python, a lot of work has been going into developing the standardization of "type hints," or annotations you can place into your code to make it easier to understand. While type hints are largely ignored by the Python interpreter, they can be used by static type checkers such as [Pyright](https://microsoft.github.io/https://realpython.com/python312-typing/) or [mypy](https://mypy-lang.org/) that can be integrated into your build system, essentially checking if your code is consistent with the type hints you offer. This allows you to take advantage of the benefits of using weakly typed languages while also making it possible to apply some of the benefits of strong typing.

Much of the safety that comes from using Rust comes from the strict and rigorous type checking that support the robust enum system and facilitate the unique memory management system. In this article, I will discuss some of the features of the Python typing system that emulate some of the benefits of the Rust type system.

The strict and rigorous Rust compiler is considered

"benevolent dictator" that will not allow you to compile code that is not consistent with the language specification. The Python interpreter is not nearly as strict, but we can use static type checkers to emulate some of the benefits of the Rust compiler.

Here I will discuss some features of the Python typing system that emulate particularly useful aspects of typing system in Rust.

These tools perform the same type of checks that the Rust compiler does, but your code may still run even if it fails the checks. You also have the freedom to switch between strong and weak typing depending on when you use the type hints (usually for critical points of your code). 


These tools perform the same type of checks that the Rust compiler does, but your code may still run even if it fails the checks. You also have the freedom to switch between strong and weak typing depending on when you use the type hints (usually for critical points of your code). Here I will discuss some features of the Python typing system that emulate particularly useful aspects of typing system in Rust.

While some of the new type hint systems have been integrated into the Python language specification itself, much of it has gone into developing features of the `typing` module. I will focus on several features that emulate common behaviors in Rust.

#### `typing.Optional` for Potentially Missing Data

Where Rust relies on the popular [`Option` enum](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html?highlight=Option%3C#the-option-enum-and-its-advantages-over-null-values) to specify when a returned value may be a valid value or `None`, in Python we can use the `typing.Optional[T]` hint to specify that we may expect a `None` value. Adding this type hint will notify type checkers that any downstream functions should be able to filter or otherwise deal with `None` values (ideally also with type hints).

As an example, imagine we have a list of integers where some elements may take the value of `None` because they are missing.

    import typing
    a: typing.List[typing.Optional[int]] = [None, 1, 2, 3]

This type hint is basically giving your downstream program a heads up that some values may be None and therefore it should be able to handle them. Mostly we will be accessing lists based on user input rather than static definitions, but the type checker will pick up on that too. Using `mypy`, we can see an error when we try to use the sum function on the list of this type.

        sum(a)

The error will indicate that the `sum` function cannot accept None values.

    > typing_examples.py:38: error: Argument 1 to "sum" has incompatible type "list[Optional[int]]"; expected "Iterable[bool]"  [arg-type]

The solution is to remove the `Optional` component of the hint after you have filtered `None` values at some point in your code.

    b: typing.List[int] = [v for v in a if v is not None]
    sum(b)

For calculating the sum we can simply remove `None` values, but you may want to handle those in different ways that the type checker cannot pick up on. To indicate that you have stripped None values using more complicated designs, you can simply add the type hint donstream after the filtering has been done.

#### `typing.TypeVar` and `typing.Generic` for Generic Types

Generic types are typically containers of other defined types that can be specified by the downstream client. In statically typed languages, the placeholder for that type must be included explicitly, although in dynamically typed languages we can get away without specifying at all - the interpreter does not need to know this information. To demonstrate this, start by making a simple class that wraps a single variable of any type.

    import dataclasses
    @dataclasses.dataclass
    class MyBasicType:
        x: typing.Any

Then as a use case you can pass an integer to the container and add it to a string. It will throw a runtime error, but the type checker will say nothing because no type hints were used other than `typing.Any`, the hint that accepts any type.

    mbt = MyBasicType(1)
    mbt.x + 'hello world'

The modern `typing` module implements some features that allow us to specify this type explicitly as we would in statically defined languages. We do this using a combination of the `TypeVar` and `Generic` objects, which are used to define a new template type prior to function or class definitions. The type checker will then track this type from the time it is instantiated to the time it is used.

    @dataclasses.dataclass
    class MyType(typing.Generic[T]):
        x: typing.Optional[T]

We would use this in our main script the same way as before, but this time the type checker will keep track of it.

    mt = MyType(1)
    
    > typing_examples.py:49: note: Left operand is of type "Optional[int]"

And when we attempt to do something that would raise an exception, the type checker raises an error.
    
    mt.x + 'hello world'

    > typing_examples.py:49: error: Unsupported operand types for + ("int" and "str")  [operator]

Note that you may also specify the type of the variable when you instantiate it, which will override the type hint downstream.

    mt = MyType[float](1)
    mt.x + 'hello world'

    > typing_examples.py:49: note: Left operand is of type "Optional[float]"
    > typing_examples.py:49: error: Unsupported operand types for + ("float" and "str")  [operator]

Even though the type is not specified at the definition, the type checker will be able to track this generic downstream as the client uses it for other purposes. This is a significantly better alternative to the `typing.Any` hint.


#### `typing.Union` Instead of Enums

In Python we can use `typing.Union` to indicate that a function may accept one of several parallel types in the same way that Rust enum types do. To do this, you may simply assign a type hint to a variable that can then be used as a type hint later. For instance, we may want to refer to a number that can be used as either an integer or a float, since they can be used interchangably in many cases.

    Number = typing.Union[float, int]

We can use this new type as a regular type hint later. To demonstrate how multiple types can be grouped together to exhibit enum-like behavior, I create three new types: the first one contains a number that is None or a number, second one contains a number that is not None, and the third one contains a number that is not None or zero. They each contain methods that would be appropriate for the valid values the contained value, and we use this to avoid receiving a `TypeError` when adding a number with a `None` value or a `ZeroDivisionError` when inverting a zero value - instead, both operations will throw an `AttributeError` because the operation simply would not be valid for that type.

    @dataclasses.dataclass
    class MyFirstType:
        '''Wraps a value.'''
        x: typing.Optional[Number]
        
    @dataclasses.dataclass
    class MySecondType:
        '''Wraps value that is not None.'''
        x: Number
        def add(self, y: Number) -> Number:
            return self.x + y

    @dataclasses.dataclass
    class MyThirdType:
        '''Wraps value that is not None or zero.'''
        x: Number

        def add(self, y: Number) -> Number:
            return self.x + y

        def invert(self) -> float:
            return 1.0 / self.x

Of course, any of these can be used as type hints in other functions - the following definition raises an error in mypy because the function accepts a number that can be none, which is a mismatch with the `MySecondType` hint.

    def make_third_type(x: typing.Optional[Number]) -> MyThirdType:
        return MyThirdType(x)

    > typing_examples.py:47: error: Argument 1 to "MyThirdType" has incompatible type "Union[float, int, None]"; expected "Union[float, int]"  [arg-type]

Say instead that we create a function that returns one of these three types depending on the input. We can do this by using the `typing.Union` hint to specify that the function accepts any of these three types. The function then returns one of these three values depending on the value. Note that the function parameter accepts a `typing.Optional` number, whereas the `MySecondType` and `MyThirdType` constructors both accept a number that is not `None`. The type checker is smart enough to realize that we actually did check if the object was `None` before passing it to the constructor, so it will not raise an error.

    SomeType = typing.Union[MyFirstType, MySecondType, MyThirdType]

    def make_new_type(x: typing.Optional[Number]) -> SomeType:
        if x is None:
            return MyType(x)
        elif x == 0:
            return MySecondType(x)
        else:
            return MyThirdType(x)

When we go to actually use a method which only appears in a subset of these types, we will get an error because the use should fit any of these types, as described in the hint.

    print(nt.add(1.0))
    
    > typing_examples.py:73: error: Item "MyFirstType" of "Union[MyFirstType, MySecondType, MyThirdType]" has no attribute "add"  [union-attr]

If, in the logic of a particular use, you actually know that the object will be a subset of these types, you may use a couple workarounds that effectively silence your type checker. This is not typically advised though - it is better to design your type hints so you never need to silence the type checker.

    print(nt.add(1.0)) # typing: ignore
    
    print(typing.cast(nt, MySecondType).add(1.0))
    
    if isinstance(nt, MySecondType):
        print(nt.add(1.0))

This behavior is similar to the Rust compiler: it will not allow you to use a method that is not valid for all of the enumerated types. It is better to create an appropriate return type that ensures the method is available than to silence the type checker. 

#### Use Sentinels for Default Parameter Values

While it is common practice to use `None` as a default parameter value to represent missing data or other exceptional cases, there are times when you may want to handle `None` as a separate valid case. For example start with the simplest case we have a function with two parameters, where exactly one should be provided by the user. In this case, we simply return whichever value should be propogated and raise an exception if neither or both are provided.

    def get_correct_option(
        default_a: typing.Optional[int] = None,
        default_b: typing.Optional[int] = None,
    ) -> int:
        '''Multiplies x and y if do_square is True.'''
        if default_a is not None and default_b is not None:
            raise ValueError('default_a and default_b cannot both be set')
        elif default_a is not None:
            return default_a
        elif default_b is not None:
            return default_b
        else:
            raise ValueError('default_a or default_b must be set')

The problem with this approach is that `None` cannot be a valid input value because, in that example, it is used to represent a non-value. In Python, we often solve this by creating sentinel values as defaults that we can check against, and treat `None` the same as any other type. Following the pattern used in `dataclasses`, we create an enum and assign an enum value to an accessible variable.

    import enum
    class MissingValueType(enum.Enum):
        MISSING = enum.auto()
        def __repr__(self):
            return "MISSING"

    MISSING = MissingValueType.MISSING
    '''Represents a missing Value.'''

We simply use this value as a default parameter value and check against it in the function body.

    def get_correct_option(
        default_a: typing.Optional[int] = MISSING,
        default_b: typing.Optional[int] = MISSING,
    ) -> typing.Optional[int]:

Because this sentinel value is not of type `Optional[int]`, however, our type checker will issue an error.

    > Incompatible default for argument "default_a" (default has type "MissingValueType", argument has type "Optional[int]")

To make our code more readable and our type hints internally consistent, we simply create a new hint using `Union`. 

    T = typing.TypeVar("T")
    ValueOrMissing = typing.Union[T, MissingValueType]

The new type hints would use this new variable and we would check against the sentinel instead of a `None` value.

    def get_correct_option(
        default_a: ValueOrMissing[typing.Optional[int]] = MISSING,
        default_b: ValueOrMissing[typing.Optional[int]] = MISSING,
    ) -> typing.Optional[int]:
        '''Multiplies x and y if do_square is True.'''
        if default_a is not MISSING and default_b is not MISSING:
            raise ValueError('default_a and default_b cannot both be set')
        elif default_a is not MISSING:
            return default_a
        elif default_b is not MISSING:
            return default_b
        else:
            raise ValueError('default_a or default_b must be set')

The type checker does not rasie any issues with this and it is clear to the reader that `None` would be a default value for either of these parameters.

Note that in the [previous article](https://devinjcornell.com/post/lessons_from_rust1_enums.html) I discussed some patterns to emulate several useful Rust enum types using wrapper classes that may include additional data to indicate why the data is missing, but this sentinel solution works well when no additional data is needed. Many Python packages solve this case in this way.




### Conclusions

The features of the type hint system I described here are helpful because they allow us to combine the safety of using strongly-typed languages in some scenarios with the freedom to use weakly-typed approaches in others. As such, I highly recommend integrating type checking programs into your build systems.




