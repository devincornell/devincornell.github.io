---
title: "Lessons from Rust 1: Enums for Errors and Missing Data"
subtitle: "Consider using patterns that emulate the `Option` and `Result` enums from Rust to make your code more robust and readable."
date: "Sept 27, 2023"
id: "lessons_from_rust1_enums"
---


Rust has a robust infrastructure for handling enum types compared to languages like Python or C++, but there are two particular built-in enums that may be useful for data pipelines: `Option` and `Result`. The `Option` enum is used to represent a value that may or may not be present (equivalent of None in Python), and the `Result` enum is used to represent a value that may or may not be an error. As a strongly typed language, function signatures in Rust must specify that they accept or return one of these enum types, making it expcit to the reader that they should expect these.

As an example, lets say that we want to build an object with an attribute that could have missing data, and, depending on the reason that the data is missing, the client may want to handle the result differently. For example purposes, lets say that we have a collection of objects containing an integer attribute, and we want to compute the average value of that attribute across all the objects. For the mean calculation, we will consider the value as invalid if it is either None or if it is not divisible by two (i.e. it is not even): if it is None, it should be ignored when computing the average; if it is not even, it should be treated as zero when computing the average.

The simplest design would be to create functions returning boolean values indicating if one of these issues occur, and, when computing the average, simply check these flags. To make this solution comparable to the later ones, I use a wrapper function that simply accesses the property directly.

    @dataclasses.dataclass
    class ExDataType0:
        a: int
        def access_a(self) -> int:
            return self.a
        
        def a_is_missing(self) -> bool:
            return self.a is None
        
        def a_is_not_even(self) -> bool:
            return self.a % 2 != 0

The client must always remember to perform these checks, otherwise they may get a `TypeError` (if any value is `None`) or a silent runtime error. From the function definition alone we do not know whether this data should be considered as valid or not.

    def average_values_check(objs: typing.List[ExDataType0]):
        values = list()
        for obj in objs:
            if obj.a_is_missing():
                pass
            elif obj.a_is_not_even():
                values.append(0)
            else:
                values.append(obj.access_a())
        return sum(values)/len(values)

A more Pythonic approach would be to create custom exceptions to indicate that the value is invalid and specify why. In Python, any object which inherits from `BaseException` is considered as a valid exception type.

    class ValueIsMissing(BaseException):
        pass

    class ValueIsNotEven(BaseException):
        pass

Instead of requiring the client to call functions to check if the value is valid, we can raise the relevant exception.

    @dataclasses.dataclass
    class ExDataType2:
        a: int
        def access_a(self):
            if self.a is None:
                raise ValueIsMissing('The data for a is missing.')
            elif self.a % 2 != 0:
                raise ValueIsNotEven('The data for a is missing.')
            else:
                return self.a

The client can then use `try..except` blocks to handle the different cases. If the attribute is requested and an exception is not handled by the caller, it will raise a runtime exception bubbling up to the top level of the program. As a general design principle, it is better to fail fast than deal with silent errors that may be causing issues downstream.

    def average_values_exc(objs: typing.List[ExDataType2]):
        values = list()
        for obj in objs:
            try:
                values.append(obj.access_a())
            except ValueIsMissing:
                pass
            except ValueIsNotEven:
                values.append(0)
        return sum(values)/len(values)

The only downside of this approach is that it would not be clear to the client that they should expect either of these exceptions unless they read the implementation or encountered the exception at runtime. This makes it more difficult for the client to know to expect errors and handle the error types differently.

A more robust solution would allow us to indicate firstly that it is possible for the value to be invalid and secondly the range of reasons it could be invalid (if they are to be handled differently) so that the user knows directly when attempting to implement solutions. As an alternative, consider creating a Rust-inspired type that can indicate whether the return value is valid and information about the reason.

First it might make sense to define an enum that can be assigned to an attribute to indicate whether the value is valid or not (note: you could probably accomplish this with a bool also). In Python, we create enums by inheriting from `enum.Enum`. 

    class ResultStatus(enum.Enum):
        Ok = enum.auto()
        Err = enum.auto()
        
We can create `Ok[T]` and `Err[E]` generic types that both contain a `status` attribute indicating whether the object is okay or an error (consistent with duck-typing). The `Ok` object will have a data attribute, and the `Err` object will have an error attribute. This will ensure that you'll get a runtime error if you incorrectly check whether it is an error or not.

    T = typing.TypeVar("T")
    @dataclasses.dataclass
    class Ok(typing.Generic[T]):
        data: T
        status: ResultStatus = ResultStatus.Ok

    E = typing.TypeVar("E")
    @dataclasses.dataclass
    class Err(typing.Generic[E]):
        error: E
        status: ResultStatus = ResultStatus.Err

For the purpose of stricter typing, you can create a new type `Result` that could be an instance of either.

    Result = typing.Union[Ok[T],  Err[E]]

For the particular use-case described here, we could then make another enum to specify the type of invalid data that appeared so that we may handle it appropriately downstream. The `Err.error` attribute will contain one of these values.

    class ErrorType(enum.Enum):
        MISSING = enum.auto()
        NOT_EVEN = enum.auto()

    @dataclasses.dataclass
    class ExDataType3:
        a: int
        def access_a(self) -> Result[int, ErrorType]:
            if self.a is None:
                return Err(ErrorType.MISSING)
            elif self.a % 2 != 0:
                return Err(ErrorType.NOT_EVEN)
            else:
                return Ok(self.a)

The client would first check if the result is ok, and then handle the type of error appropriately.

    def average_values_result(objs: typing.List[ExDataType3]):
        values = list()
        for obj in objs:
            result = obj.access_a()
            if result.status is ResultStatus.Ok:
                values.append(result.data)
            else:
                if result.error is ErrorType.NOT_EVEN:
                    values.append(0)
                else:
                    pass
            
        return sum(values)/len(values)

Note that in some cases it may be valuable to avoid using status enums, in which case you could create `Ok` and `Err` objects with `bool` attributes instead.

    @dataclasses.dataclass
    class Ok2(typing.Generic[T]):
        data: T
        is_ok: bool = True
        
    @dataclasses.dataclass
    class Err2(typing.Generic[E]):
        error: E
        is_ok: bool = False

This approach would work very similarly but the client would not need to reference the enum.

