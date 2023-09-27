---
title: "Lessons from Rust 4: Stronger Typing"
subtitle: "Use the ownership pattern from Rust to increase_safety."
date: "Sept 27, 2023"
id: "lessons_from_rust4_typing"
---


Part of the appeal of Rust and other statitically typed languages such as C++ is the strong typing system - that is, the user must specify the type of each variable and function parameter. While the effort involved in this specification may not always be advantageous, it certainly contributes to the correctness of your code: your compiler will be able to identify basic errors even prior to runtime. A strong typing system creates gaurantees about the structure of your data at various points in your code, and this can be very useful for data pipelines with many steps.

While Python is a dynamically typed language, there has been a lot of interest recently in using type hints to improve the readability and correctness of code. The syntax of type hints tends to be fairly close to typing specifications in Rust, and much of the support for typing has come as part of the [`typing`](https://docs.python.org/3/library/typing.html) module in the Python standard library. Type hints are especially useful when working with static analysis tools such as [`mypy`](https://github.com/python/mypy) that can check types at every point in your code to identify potential issues prior to runtime. I will now cover some features of the type hint system that I have found to follow Rust's design in useful ways.

#### `typing.Optional` for Potentially Missing Data

Where Rust relies on the popular [`Option` enum](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html?highlight=Option%3C#the-option-enum-and-its-advantages-over-null-values) to specify when a returned value may be a valid value or `None`, in Python we can use the `typing.Optional[T]` hint to specify that we may expect a `None` value. Adding this type hint will notify type checkers such as `mypy` that any downstream functions should be able to filter or otherwise deal with `None` values (ideally also with type hints).

As an example, imagine we have a list of integers where some elements may take the value of `None` because they are missing.

    import typing
    a: typing.List[typing.Optional[int]] = [None, 1, 2, 3]

This type hint is basically giving your downstream program a heads up that some values may be None and therefore it should be able to handle them. Using `mypy`, we can see an error when we try to use the sum function on the list of this type.

        sum(a)

You will see an error suggesting that the `sum` function cannot accept None values.

    typing_examples.py:38: error: Argument 1 to "sum" has incompatible type "list[Optional[int]]"; expected "Iterable[bool]"  [arg-type]

You will receive the following error because you expliictly include a `None` element in your list.

    typing_examples.py:28: error: List item 0 has incompatible type "None"; expected "int"  [list-item]

The solution is to remove the `Optional` component of the hint after you have filtered `None` values at some point in your code.

    b: typing.List[int] = [v for v in a if v is not None]
    sum(b)

#### `typing.TypeVar` for Generic Types

In strongly typed languages there is typically syntax to denote cases where the client can decide the type downstream. The `typing` module implements something similar using `TypeVar`, which allows you to define a new template type prior to function or class definitions

    T = typing.TypeVar("T")

You then may use it in a function or class by inheriting from `typing.Generic[T]`. This makes it clear to the reader that the type specified in one location is the same as the type in the next location. Building on the previous example, imagine a scenario where we have a dataclass containing an attribute that could be `None`, and we want the client to see an exception when they attempt to get the variable through a particular interface. We can specify that the attribute in the dataclass is `typing.Optional[T]` and in the accessor function either raise the exception or return a value of type `T` (notice that I used the `# type: ignore` comment to avoid strict typing). 

    import dataclasses

    @dataclasses.dataclass
    class MyType(typing.Generic[T]):
        x: typing.Optional[T]

        def access_z(self) -> T:
            if self.x is None:
                raise ValueError("z is missing")
            else:
                return self.x # type: ignore
        
        def set_z(self, x: T) -> None:
            self.x = x

#### `typing.Union` Instead of Enums

Rust allows you to define related objects as enums objects with different attributes and methods for operation. In Python, we can instead use the `typing.Union` hint to specify that a function may accept one of several (ideally related) types. To do this, you may simply assign a type hint to a variable that can then be used in a downstream function definition. 

For example, imagine that we want to make a function that accepts either a generic `MyType[T]` object  can store a `None` value, or a value of type `T`. We simply assign the full type hint to a variable.

    MyValue = typing.Union[MyType[T], T]

In the case where we pass a `MyType[T]` object, we can access the value using the `access_z` method which will raise a `ValueError` if it is `None`. In the case where we pass a value of type `T`, we can deal with it directly. For practical purposes I would not recommend using this strategy for this particular example, but you can see how it might be the best option in other cases.

    def convert_to_string(val: MyValue[T]) -> str:
        try:
            return str(val.access_x())
        except AttributeError:
            return str(val)

Using these tools you have all the powerful advantages of a dynamically types languages with the extra security that static analysis can provide. I highly recommend using type hints - especially for critical aspects of your code.

