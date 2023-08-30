---
title: "Patterns for Collection Types"
subtitle: "Patterns for creating useful collections of data objects."
date: "August 24, 2023"
id: "dsp1_collections"
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

### Exposing collection methods

Whereas extending existing types gives you access to behavior of collections directly, building custom wrapper types may require you to implement some boilerplate functionality such as iteration and numerical (or other) indexing. You can do some of this by creating `__iter__` and `__getitem__` attributes.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...
        def __iter__(self) -> typing.Iterator[MyType]:
            return iter(self.objs)
        
        def __getitem__(self, ind: int) -> MyType:
            return self.objs[ind]


### Interface for adding elements

The essential characteristic of the collections I am discussing here is that they contain only objects of the specified type. Without further work, you would rely on the customer to create a new instance of the containing type before it can be added. Basic software engineering principles suggest that we should encapsulate relevant functionality for the contained function, so we could add an `.append()` method to the collection (although obviously, and less ideally, the customer could add to the list directly).

The most basic encapsulation method would simply act as a pass-through.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        
        def append(self, *args, **kwargs) -> None:
            return self.objs.append(*args, **kwargs)

A better solution would be to add object construction code from within the append method so that you do not need to create it each time. You can use either the constructor or a static factory method to make this.
    
    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...
        def append_mytype(self, *args, **kwargs) -> None:
            return self.objs.append(MyType(*args, **kwargs))
        
        def append_from_number(self, *args, **kwargs) -> None:
            return self.objs.append(MyType.from_number(*args, **kwargs))


    mc = MyCollection()
    mc.append(MyType(1, 2.0))

Adding this to an extended collection type involves use of builtin collection methods directly, instead of manipulating the contained collection.

    class MyCollectionExtended(typing.List[MyType]):
        ...    
        def append_mytype(self, *args, **kwargs) -> None:
            return self.append(MyType(*args, **kwargs))
        
        def append_from_number(self, *args, **kwargs) -> None:
            return self.append(MyType.from_number(*args, **kwargs))

You would create interfaces for similar methods such as element removal by following a similar pattern.

### Filtering

Filtering functions are used to return a collection of the same type that includes only a subset of the original elements. To return the same type, you will likely need to access the `self.__class__` attribute.
        

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
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

Aggregation is often used in conjunction with grouping, or splitting elements into subgroups according to some criteria and aggregating within those groups. In Python, you could represent groups as a dictionary mapping some key to our collection objects. It will be important to reference the `self.__class__` to ensure you are creating groups that are the same type as the original collection - this is important.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...
        def group_by_as_dict(self, key_func: typing.Callable[[MyType], typing.Hashable]) -> typing.Dict[str, MyCollection]:
            groups = dict()
            for el in self.objs:
                k = key_func(el)
                if k not in groups:
                    groups[k] = list()
                groups[k].append(el)
            return {k:self.__class__(grp) for k,grp in groups.items()}

For readability, it may also be helpful to create a custom type, however simple, to represent the grouped objects.

class GroupedMyCollection(typing.Dict[typing.Hashable, MyCollection]):
    pass

Because the return type of these functions is a set of the original collection types, you can use the previously defined aggregation functions on each group.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...
        def group_by_average(self, *args, **kwargs) -> typing.Dict[typing.Hashable, MyTypeAverage]:
            return {k:grp.average() for k,grp in self.group_by(*args, **kwargs).items()}

A better approach may be to add functionality to the grouping object such that you can apply the groupby first and then perform additional operations on the grouping.

    class GroupedMyCollection(typing.Dict[typing.Hashable, MyCollection]):
        def average(self) -> typing.Dict[typing.Hashable, MyTypeAverage]:
            return {k:grp.average() for k,grp in self.items()}

To do this, you'd wrap the grouping function with the custom grouping type.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...

        def group_by(self, key_func: typing.Callable[[MyType], typing.Hashable]):
            groups = dict()
            for el in self.objs:
                k = key_func(el)
                if k not in groups:
                    groups[k] = list()
                groups[k].append(el)
            return GroupedMyCollection({k:self.__class__(grp) for k,grp in groups.items()})

This way, instead of using `.group_by_average()`, you could use `.group_by().average()`. For instance, to split the values into true or false, you would use the following expression.

    mytypes.group_by(lambda mt: int(mt.a) % 2 == 0).average()

And the output would look like the following:

    {
        True: MyTypeAverage(a=4, b=0.3574603174603175),
        False: MyTypeAverage(a=3.5, b=0.7052083333333333)
    }

Note that for practical purposes, I recommend fixing the key function so that the customer can see all the types of groupings that one would expect to use with a given collection. This improves readability and avoids leaving the key function specification to the customer since there may be many cases they must consider.


### Mutations and Element-wise Transformations

The way that I use mutations always involves transforming objects from one type to another - rarely would I output a simple list/array of numbers, for instance, as you might in the `mutate` function in R dplyr. As such, we would create a new type for the result of the transformation as well as the associated collection type. We would also define static factory methods on each to support the transformation.

    @dataclasses.dataclass
    class MyTypeTwo:
        sum: int
        prod: float
        
        @classmethod
        def from_mytype(cls, mt: MyType):
            return cls(sum = mt.a + mt.b, prod = mt.a * mt.b)

    @dataclasses.dataclass
    class MyCollectionTwo:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        
        @classmethod
        def from_mycollection(cls, mytypes: MyCollection):
            return MyCollectionTwo([MyTypeTwo.from_mytype(mt) for mt in mytypes])

To further improve readability, I further recommend adding a method to call the static factory method from within the original collection object. You can then call this method to return a new collection of the transformed types.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...

        def transform_to_two(self) -> MyCollectionTwo:
            return MyCollectionTwo.from_mycollection(self)

##### Parallelized transformations

In the case where you want to implement parallelization, you can call the element-level static factory method directly in each process.

    import multiprocessing

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...
        def transform_parallelized(self) -> MyCollectionTwo:
            with multiprocessing.Pool() as p:
                results = p.map(MyTypeTwo.from_mytype, self)
            return MyCollectionTwo(results)



