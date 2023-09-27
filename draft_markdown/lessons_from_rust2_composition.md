---
title: "Lessons from Rust 2: Composition over Inheritance."
subtitle: "Consider abandoning classical OOP patterns like inheritance to make your data pipelines more maintainable."
date: "Sept 27, 2023"
id: "lessons_from_rust2_composition"
---

Classical OOP design patterns have fallen in popularity compared to compositional-based approaches, and there is much we can from looking at the Rust language


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



