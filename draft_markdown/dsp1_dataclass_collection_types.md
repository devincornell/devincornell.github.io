---
title: "Patterns for Data Collection Types"
subtitle: "Patterns for creating collections of dataclasses and data objects."
date: "August 24, 2023"
id: "dsp1_dataclass_collections"
---


By _data collection types_, I mean types that act as collections of basic data objects that offer special functionality (or minimally annotation) relevant to collections of a particular type.


Here I start by creating a basic data object using the `dataclasses` module. The goal of collection types is to manipulate these objects.

    import dataclasses
    import typing

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float


## Two Approaches

In most languages, there are two primary ways to create collection types: (1) extend an existing collection type such as std::vector, Array, Dict, or List; or (2) encapsulate a collection in another custom type.


#### Wrapping Collection Types

The most typical approach for building collection types is to create a wrapper object that contains a collection type. The `dataclasses` module can be helpful here as it can build a constructor that accepts a single object: a collection of objects of some type. The constructor simply assigns the collection to an attibute of the class.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List

And you might instantiate a new collection like this:

    MyCollection([])

You could even default set a default to allow you to create an empty collection.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
    
In which case you could use `MyCollection()` to instantiate a collection with an empty list.

#### Extending Existing Types

Alternatively, for simple cases, you may extend an existing collection type. To do this in Python, you will probably want to use the `typing` module instead of `list`, `dict`, or `set` directly. This object will work almost exactly like the inherited type, but with any additional methods you would like to assign.

class MyCollectionExtended(typing.List[MyType]):
    pass

You would access this the same way you use the list constructor.

MyCollectionExtended(MyType(i, i + 1) for i in range(10))

For the purpose of this article, I will use the former approach that involves wrapping collections, but I certainly do find extending existing types to be valuable in simple cases where I want to minimize code. Using some of the encapsulation principles I discuss here (namely static factory methods), you could easily design your pipeline such that you could shift from one approach to another as the project changes.

Now I will cover strategies for building these collection types.


### Static Factory Methods

Aside from clearer semantics, the main benefit of defining collection types is that you can add application-specific methods. Static factory methods are functions that return instances of the object - in this, case, collections of the objects. The main benefit of these methods is that they can also call the constructors or static factory methods of your containing types. For example, using the `dataclass`-generated constructor of the below collection requires you to either pass a set of pre-constructed instances to the underlying list, or append them afterwards. Alternatively, the static factory method calls the `MyType` constructor for you, so you can simply pass it an iterable of relevant information to make the collection with the proper types.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        
        @classmethod
        def from_ab_pairs(cls, elements: typing.Iterable):
            return cls([MyType(*el) for el in elements])

For more complicated cases, you may need to use a static factory method of the contained types instead of their constructors. In a case where we want to create `MyType` objects from a single integer, we can add a static factory method to that type.

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float
        
        @classmethod
        def from_number(cls, i: int):
            return cls(i, 1/(i+1))

Then we simply call that as we iterate over the data being used to create the collection.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        
        @classmethod
        def from_numbers(cls, numbers: typing.Iterable[int]):
            return cls([MyType.from_number(i) for i in numbers])

This greatly simplifies the process of creating new collections using only the data needed for the contained types.

    MyCollection.from_numbers(range(10))


### Manipulating Collections

The essential characteristic of the collections I am discussing here is that they contain only objects of the specified type. Without further work, you would rely on the customer to create a new instance of the containing type before it can be added. Basic software engineering principles suggest that we should encapsulate relevant functionality for the contained function, so we could add an `.append()` method to the collection (although obviously, and less ideally, the customer could add to the list directly).

The most basic encapsulation method would simply act as a pass-through.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        
        def append(self, *args, **kwargs) -> None:
            return self.objs.append(*args, **kwargs)

A better solution would be to add object construction code from within the append method so that you do not need to create it.

        ...
        def append_mytype(self, *args, **kwargs) -> None:
            return self.objs.append(MyType(*args, **kwargs))


    mc = MyCollection()
    mc.append(MyType(1, 2.0))

It would be better, however, to be able to create an 


MyCollectionExtended

Instead, it is best to encapsulate this functionality within static factory methdods to make the interface simpler.


The useful characteristic of default types in weakly-typed languages is that 


### Filtering

Filtering functions are used to return a collection of the same type that excludes some elements. To return the same type, you will likely need to access the `self.__class__` attribute.
        
        ...
        def filter(self, keep_if: typing.Callable[[MyType], bool]):
            return self.__class__([o for o in self.objs if keep_if(o)])


### Aggregation

Aggregation functions are used to reduce a set of contained elements into a single element according to some function. As an example, lets say we want to return the average element in a collection - that is, an element that represents the average of `a` and `b` attributes. We would start by creating a custom type for the return value so that the customer knows it is an aggregation of multiple elements and not an observation itself. Not much is needed here unless we want to add new functionality.

    class MyTypeAverage(MyType):
        pass

Actually computing the average can be done in the new method.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)

        ...
        def average(self) -> MyType:
            return MyType(
                a = statistics.mean([o.a for o in self.objs]),
                b = statistics.mean([o.b for o in self.objs]),
            )

Or, if you would expect the averaging to appear in other places, you could place that code into the average object itself as a static factory method.

    class MyTypeAverage(MyType):

        @classmethod
        def from_mytypes(self, mtypes: typing.Iterable[MyType]):
            return self.__class__(
                a = statistics.mean([o.a for o in self.objs]),
                b = statistics.mean([o.b for o in self.objs]),
            )

Then simply call that from the collection object.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)

        ...
        def average_sfm(self) -> MyTypeAverage:
            return MyTypeAverage.from_mytypes(self.objs)

### Grouping and Aggregation

Aggregation is often used in conjunction with grouping, or splitting elements into subgroups according to some criteria.


### Mutations and Element-wise Transformations


