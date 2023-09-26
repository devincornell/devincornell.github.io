---
title: "Lessons from the Rust Language"
subtitle: "Ideas we can use to improve our data pipelines in any language."
date: "Sept 6, 2023"
id: "lessons_from_rust"
---

The Rust programming language has taken the award for "most loved programming language" in the [Stack Overflow Developer Survey](https://survey.stackoverflow.co/2022#overview) since 2016. The power of Rust comes in that it is nearly as fast as C++ without the potential issues that come with pointers and manual memory management. I argue that this advantage comes as much from what the languages allows you to do as what it restricts you from doing. Whether or not you can convince your stakeholders or company to allow you to write your data pipelines in Rust, there are some lessons we can learn from Rust that we can apply to our data pipelines in any language. 

In this article, I will describe some patterns for Python code that mimic the features and, perhaps more importantly, the restrictions built into the language that improve safety and readability.

## 1. Immutability

By default, variables in Rust are are immutable - that is, once you assign a value to a variable, you cannot change it. You must manually specify that a variable is mutable if you want to be able to change it later, and thus you should be thinking of variables as immutable unless otherwise specified. I wrote about the benefits of immutability in [a previous article](/post/dsp0_patterns_for_dataclasses.html), but in general I recommend transforming data from one type to another instead of modifying it in-place. This makes it easier to reason about your code and to debug it when something goes wrong.

## 2. Stronger Typing




## 3. Ownership

The key to memory safety in Rust comes from a concept called _ownership_. As an example, it is common practice to allocate a piece of heap memory (e.g. list or vector) at the top level of your program and then pass a reference or pointer into a function that will use or modify it. In languages such as Python or C++, you can continue to use that allocated memory after the function has returned, and either you must remember to free the memory manually or let the garbage collector take care of it after it is no longer needed.

Rust adds the restriction that only one scope can _own_ a variable, so by passing a mutable variable into the function you are actually transferring ownership to it - you cannot continue to access that memory from outside the function. You can, however, return ownership to the outer scope by returning the reference. This makes it clear to the reader that you are, in fact modifying some of the data being passed into the function.

While we cannot place this restriction into our Python code explicitly, we can force ourselves to use patterns consistent with the ownership concept. As a first example, let us say that you have a list and you want to write a function that counts the number of even elements in the list. Let us say that you want to keep track of this information in a custom counter object that simply records the count.

    from __future__ import annotations
    import typing

    class MyCounter:
        def __init__(self):
            self.count = 0
        
        def increment(self):
            self.count += 1
            
        def combine(self, other: MyCounter):
            self.count += other.count

One solution to this problem is to write a function that accepts a counter and simply increments it within the function, allowing you to use it afterwards. The advantage of this approach is that it is memory efficient - you only need to maintain a single counter in memory in your program at a time. The downside is that the reader cannot tell that the counter will be modified within the function - the reader can only see that by looking into the function.

    def count_even_inplace(values: typing.List[int], ctr: MyCounter) -> None:
        for v in values:
            if v % 2 == 0:
                ctr.increment()

You can still access the updated data in the outer scope using the same variable name.

    mylist1 = list(range(10))
    ctr1 = MyCounter()
    count_even_inplace(mylist1, ctr1)

An alternative would be to write a more "pure" function - that is, a function with no side effects. One could do this by accepting only a list and returning a new counter that would need to be merged back into the original counter. This is a more functional approach, but it is less memory efficient because you need to maintain two counters in memory at the same time. The upside is that there are no side-effects - no objects are being modified in-place.

    def count_even_newctr(values: typing.List[int]) -> MyCounter:
        ctr = MyCounter()
        for v in values:
            if v % 2 == 0:
                ctr.increment()
        return ctr

Assuming you have an existing counter, you simply call the function on the list and then combine the returned counter with the existing one to be used downstream.

    ctr1 = MyCounter()
    ctr2 = count_even_newctr(mylist1)
    ctr1.count += ctr2.count

An alternative approach that follows the ownership model would be to accept and modify the existing counter, but return ownership by returning a reference to the same modified counter.This combines some of the advantages of both: it makes it clear that the counter is being modified but does not need to create a copy of the counter. There is essentially no side-effect because you are returning a reference to the same object.

def count_even_transfer_ownership(values: typing.List[int], ctr: MyCounter) -> MyCounter:
    for v in values:
        if v % 2 == 0:
            ctr.increment()
    return ctr

To use this function, you would modify an existing counter in-place, and re-assign the reference to the modified counter to a variable with the same name. 

    ctr1 = MyCounter()
    ctr1 = count_even_transfer_ownership(mylist1, ctr1)

To further drive home this point, imagine we want to create a function that returns a list with zero values removed. The memory-efficient approach that decreases readability would be to modify the list in-place and return nothing.

    def remove_zeroes_inplace(values: typing.List[int]) -> typing.List[int]:
        while True:
            try:
                values.remove(0)
            except ValueError:
                break

The more "pure" and readable approach would be to return a new list with the zeroes removed.

    def remove_zeroes_newlist(values: typing.List[int]) -> typing.List[int]:
        return [v for v in values if v != 0]

And the solution using the ownership model would be to modify the existing list in-place and return a reference to the same list that would be used in the outer scope.

    def remove_zeroes_transfer_ownership(values: typing.List[int]) -> typing.List[int]:
        while True:
            try:
                values.remove(0)
            except ValueError:
                break
        return values

Rust has even more complicated rules for ownership that allow for memory safety, but these examples simply show patterns .

## 4. Enums for Errors and Missing Data

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

## 3. Use Composition over Inheritance and Generally Avoid OOP Practices

Over the last decade we have seen a shift away from complex inheritance heirarchies that were common (and even necessary) in OOP-heavy design patterns towards more functional approaches (see [this example][https://www.youtube.com/watch?v=0mcP8ZpUR38&t=3s] for more information). This is perhaps best embodied by the use of the `dataclasses` package, which allows you to create what are essentially structs in Python (see my previous article on [best practices for dataclasses](/post/dsp0_patterns_for_dataclasses.html)). The motivation for these changes is that inheritance-heavy codebases tend to be more difficult to read and refactor.

In Rust, there is little support for inheritance or other OOP concepts at all - instead you create structs that can contain and operate on other structs using methods. This is called _composition_ and it is a more flexible approach that creates weaker coupling between your objects.

#### Example Using Inheritance

For example, consider the case where we want to create a result object that can generate summary statistics to describe a set of numbers. In some cases, we only need to track the set of numbers, but there is a special case where we need to calculate statistics that consider an additional baseline parameter. 

An inheritance-based approach would suggest that we should start by creating a base class that handles some functionality that is shared between the two object types. This base class provides some functionality that makes assumption about the implementations we will create later.

    class BaseResult:
        def summary_stats(self) -> typing.Dict[str, float]:
            return {
                'mean': self.mean(),
                'variance': self.variance()
            }
        
        def variance(self) -> float:
            raise NotImplementedError()
        
        def mean(self) -> float:
            return sum(self.numbers)/len(self.numbers)

First we implement the simpler result object which only tracks the set of numbers from which to generate statistics. We should ensure that this object implements the methods and contains attributes expected by the base class. In this case, we need to implement the variance method and make sure our object contains the numbers. It will inherit the base class's mean and summary statistics methods.

    @dataclasses.dataclass
    class SimpleResultInherited(BaseResult):
        numbers: typing.List[float]
            
        def variance(self):
            u = self.mean()
            return sum([(r - u)**2 for r in self.numbers])/len(self.numbers)

The more complex object should track the set of numbers and an additional offset value that is needed for the summary statistics. First we overload the variance and mean functions to take the baseline into account, and add a method to calculate the median. The new summary statistics method will call the base class summary statistics method which will rely on the overloaded mean and variance methods.

    @dataclasses.dataclass
    class ComplexResultInherited(BaseResult):
        numbers: typing.List[float]
        offset: float
        
        def summary_stats(self) -> typing.Dict[str, float]:
            return {
                **super().summary_stats(),
                'median': self.median(),
            }
                
        def variance(self) -> float:
            u = self.mean()
            return sum([(r - u)**2 for r in self.numbers])/len(self.numbers)
        
        def mean(self) -> float:
            return super().mean() + self.offset
        
        def median(self) -> float:
            return sorted(self.numbers)[len(self.numbers)//2] + self.offset

We would create and use these objects in similar ways with the exception that the complex object accepts an offset value.

    mylist1 = list(range(10))
    sri = SimpleResultInherited(mylist1)
    print(sri.summary_stats())
    
    cri = ComplexResultInherited(mylist1, 1.0)
    print(cri.summary_stats())

This approach creates a strong coupling between the base class and derivative objects that makes it more difficult to read and refactor if changes are needed later. 

#### Composition Approach

Using the composition approach, we would instead wrap the collection of numbers into a separate class which is contained by both our new objects. This collection would include methods for calculating the mean and variance, and the result objects would simply call these methods. We know that methods for the two result objects differ only by the baseline, so we create methods which accept this as a parameter - the simple result object will pass zero as the baseline.

The container class will wrap the set of numbers and include several methods that all accept offset values.

    @dataclasses.dataclass
    class NumberContainer:
        numbers: typing.List[float]
        
        def __len__(self) -> int:
            return len(self.numbers)
        
        def mean(self, offset: float) -> float:
            return sum(self.numbers)/len(self.numbers) + offset
        
        def variance(self, offset: float) -> float:
            u = self.mean(offset=offset)
            return sum([(r - u)**2 for r in self.numbers])/len(self.numbers)

        def median(self, offset: float) -> float:
            return sorted(self.numbers)[len(self.numbers)//2] + offset

The simple result object will accept these numbers as a parameter, and we construct this object as part of a factory method constructor that takes only the list of numbers. The mean and variance methods call the methods from the numbers container by specifying that the offset should equal zero.

    @dataclasses.dataclass
    class SimpleResult:
        results: NumberContainer
        
        @classmethod
        def from_list(cls, numbers: typing.List[float]):
            return cls(NumberContainer(numbers))
        
        def summary_stats(self) -> typing.Dict[str, float]:
            return {
                'mean': self.mean(),
                'variance': self.variance()
            }
        
        def variance(self) -> float:
            return self.results.variance(offset=0)
        
        def mean(self) -> float:
            return self.results.mean(offset=0)

In the complex result object we accept the baseline parameter in the factory constructor method and that baseline will be passed to the container functions.

    @dataclasses.dataclass
    class ComplexResult:
        results: NumberContainer
        offset: float
        
        @classmethod
        def from_list(cls, numbers: typing.List[float], offset: float):
            return cls(NumberContainer(numbers), offset)
        
        def summary_stats(self) -> typing.Dict[str, float]:
            return {
                'mean': self.mean(),
                'variance': self.variance(),
                'median': self.median(),
            }
        
        def mean(self) -> float:
            return self.results.mean(offset=self.offset)
        
        def variance(self) -> float:
            return self.results.variance(offset=self.offset)
        
        def median(self) -> float:
            return self.results.median(offset=self.offset)

We can create and use these objects in the same way as before with the primary difference being that we use teh factory method constructor to call the constructor for the container class.

    si = SimpleResult.from_list(mylist1)
    print(si.summary_stats())
    
    ci = ComplexResult.from_list(mylist1, 1.0)
    print(ci.summary_stats())

While the interfaces for our inheritance and composition examples are very similar, the patterns we draw on make this code much easier to extend and refactor. We can read it systematically starting with the collections object and progressing to the objects that use it, rather than looking back and forth between the base class and implementations to see how they interact. I highly recommend looking at [more examples](https://www.youtube.com/watch?v=0mcP8ZpUR38) if you are interested in learning more about this approach.



## Conclusions
