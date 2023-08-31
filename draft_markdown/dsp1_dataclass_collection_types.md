---
title: "Patterns for data collection types"
subtitle: "Patterns for creating useful collections of data objects: filtering, grouping, aggregation, mutation, parallelization, and plotting."
date: "August 31, 2023"
id: "dsp1_collections"
---


![Data collection visualization.](https://storage.googleapis.com/public_data_09324832787/data_collections2.svg)

In this article I discuss some patterns and anti-patterns for building specialized types that act as data collections, and I will focus on variable-sized collections of fixed-size data types. This will typically mean iterables of structs or classes that exclusively store atomic data types. Built-in lists, dicts, and arrays are all powerful tools for managing data objects, but I argue that either extending or encapsulating them with custom types can improve the readability, maintainability, and error robustness of your data pipelines.

This article serves as a natural progression from my article on [patterns for dataclasses](/post/dsp0_patterns_for_dataclasses.html) (essentially the data objects I reference here) and builds on some of the basic strategies described in my article on [weaknesses of using dataframes in your pipelines](/post/zods0_problem_with_dataframes.html). The examples I offer here are based in Python, but I believe they could apply to most other languages.

### Data Object Collections

Built-in collection types such as lists, arrays, or dicts offer the simplest methods for storing and manipulating sequences of data objects: they are designed to handle collections of any type and are therefore fit for most applications. For example purposes, let us start with a very basic data object in Python built using the `dataclasses` module. This type has exactly two properties - an int and a float - and is used to represent a single element in your dataset.

    import dataclasses

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float

Creating a list of these objects is then fairly straightforward: we can simply call the constructor in a loop to create a new list of these objects. We can even add a type hint to note that this is a list of objects of this specific type.

    import typing

    mytypes: typing.List[MyType] = [MyType(i, 1/(i+1)) for i in range(10)]

And, of course, we can continue to use methods that operate on iterables to manipulate these objects, typically in for loops (or list comprehensions). These objects are very general and you can work with them in the same way you work with any other iterable.

    mytype_products = [mt.a * mt.b for mt in mytypes]

The problem, I argue, is that they are a little too general - there is nothing in the code that indicates how these objects will be transformed and any downstream customers/functions must use functions that create iterables from scratch. The alternative is that instead of using these built-in types directly, you can create your own application-specific types that can be manipulated according to methods that you define.

In most languages, there are two primary ways to create collection types: (a) extend an existing collection type, or (b) encapsulate a collection in another custom type. I will discuss each approach below, but most subsequent patterns will focus on the encapsulating approach because it is more complicated and should make clear the approach you would use for extended types.

#### A. Encapsulate Collection Types

The most typical approach for building custom collection types is to create a wrapper object that contains and encapsulates a collection type. You may choose which features of the collections (such as iteration or indexing) to expose, and add additional methods  The `dataclasses` module can be helpful here as it can build a constructor that accepts a single object: a collection of objects of some type (note that it very well could contain more). The constructor simply assigns the collection to an attibute of the object.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List

And you might instantiate the new collection like this:

    MyCollection([])

You could even default set a default to allow you to create an empty collection.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
    
In which case you could use `MyCollection()` to instantiate a collection with an empty list.

#### B. Extend Existing Types

Alternatively, for simple cases, you may extend an existing collection type. To do this in Python, you will probably want to use the `typing` module instead of `list`, `dict`, or `set` directly. This object will work almost exactly like the inherited type, but with any additional methods you would like to assign.

    class MyCollectionExtended(typing.List[MyType]):
        pass

You would access this the same way you use the list constructor.

    MyCollectionExtended(MyType(i, i + 1) for i in range(10))

For the purpose of this article, I will use the former approach that involves wrapping collections, but I certainly do find extending existing types to be valuable in simple cases where I want to minimize code. Using some of the encapsulation principles I discuss here (namely static factory methods), you could easily design your pipeline such that you could shift from one approach to another as the project changes.

Now I will cover strategies for building more features into these collection types.


### Static Factory Methods

The first concern we have for custom collections will be the methods by which they are constructed - for this, I recommend using static factory methods almost exclusively. Static factory methods are static functions that return instances of the parent object. It is generally best to contain any type of working logic into a static factory method instead of the constructor in case there are cases where you want to instantiate it without that logic.

One benefit of these methods is that they can also call the constructors or static factory methods of your containing types. For example, using the `dataclass`-generated constructor of the below collection requires you to either pass a set of pre-constructed instances to the underlying list, or append them afterwards. Alternatively, the static factory method calls the `MyType` constructor for you, so you can simply pass it an iterable of relevant information to make the collection with the proper types.

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

You could imagine how this would scale to more complicated cases.

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

In cases where you are wrapping dictionaries or sets, you might want to add additional pass-through functionality.

### Interface for adding elements

The essential characteristic of the collections I am discussing here is that they contain only data objects of the specified type. Without further work, you would rely on the customer to create a new instance of the containing type before it can be added. Basic software engineering principles suggest that we should encapsulate relevant functionality for the contained function, so we could add an `.append()` method to the collection (although obviously, and less ideally, the customer could add to the list directly).

The most basic encapsulation method would simply act as a pass-through.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...
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
    mytypes.append_from_number(1)


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

Returning the same type means that you can still use any methods defined in the original object.

### Aggregation

Aggregation functions are used to reduce a set of contained elements into a single element according to some function. As an example, lets say we want to return the average element in a collection - that is, an element that represents the average of `a` and `b` attributes. We would start by creating a custom type for the return value so that the customer knows it is an aggregation of multiple elements and not an observation itself. Not much is needed here unless we want to add new functionality.

    class MyTypeAverage(MyType):
        pass

Actually computing the average can be done in the new method. It would return the new average type.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)

        ...
        def average(self) -> MyTypeAverage:
            return MyType(
                a = statistics.mean([o.a for o in self.objs]),
                b = statistics.mean([o.b for o in self.objs]),
            )

If you would expect the averaging to appear in other places, you could place that code into the average object itself as a static factory method.

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

In this way, you could call the aggregated object's static factory method from other functions that return that type.

### Grouping and Aggregation

Aggregation is often used in conjunction with grouping, or splitting elements into subgroups according to some criteria and aggregating within those groups. In Python, you could represent groups as a dictionary mapping some key to our collection objects. It will be important to reference `self.__class__` to ensure you are creating groups that are the same type as the original collection - this is important.

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

Instead of using `.group_by_average()`, you could use `.group_by().average()`. This is possible because you are creating the intermediary collection for the grouping.

    mytypes.group_by(lambda mt: int(mt.a) % 2 == 0).average()

And the output would look like the following:

    {
        True: MyTypeAverage(a=4, b=0.3574603174603175),
        False: MyTypeAverage(a=3.5, b=0.7052083333333333)
    }

Note that for practical purposes, I recommend fixing the key function in this example so that the customer can see all the types of groupings that one would expect to use with a given collection - I simply used this for example purposes. This improves readability and avoids leaving the key function specification to the customer since there may be many cases they must consider.


### Mutations and Element-wise Transformations

Mutations always involve transforming objects from one type to another - rarely would I output a simple list/array of numbers, for instance, as you might in the `mutate` function in `R`/`dplyr`. As such, we would create a new type for the result of the transformation as well as the associated collection type. We would also define static factory methods on each to support the transformation.

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

This creates a fairly simple interface, and you could imagine chaining these methods to perform more complicated operations.

##### Parallelized transformations

In the case where you want to implement parallelization, you can call the element-level static factory method directly in each process. This way, all parallelization code is maintained within the object itself. 

    import multiprocessing

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...
        def transform_parallelized(self) -> MyCollectionTwo:
            with multiprocessing.Pool() as p:
                results = p.map(MyTypeTwo.from_mytype, self)
            return MyCollectionTwo(results)

The fact that you are using parallelized code need not even be transparent to the customer.

### Extend Functionality Using Composition

Following the recommendation in my previous article discussing [patterns for dataclasses](/post/dsp0_patterns_for_dataclasses.html), I recommend extending functionality using composition in this range too. This addresses the problem of creating collection objects with massive numbers of methods. You simply create a wrapper object that is instanted from the original collection and operates on the original function. For instance, lets say you need to implement a number of math and statistical methods but don't want to clog the main object with these methods. First you would create such a wrapper objects - fairly easy with the `dataclasses` module. Notice that I am breaking the encapsulation of the original collection - it isn't necessary to do this in my opinion, but it would be a fair choice.

    @dataclasses.dataclass
    class MyCollectionMath:
        mc: MyCollection

        def total_a(self) -> float:
            return sum([mt.a for mt in self.mc.objs])
        
        def total_b(self) -> float:
            return sum([mt.b for mt in self.mc.objs])

And add the constructor to a method within the original collection. Python makes a clean interface for this using the `property` decorator.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...
        @property
        def math(self):
            return MyCollectionMath(self)

And you can access all the additional methods through temporary instances of the wrapper object.

    mytypes.math.total_a()


### Plotting Objects

The last pattern I will discuss involves specifically managing interfaces for plotting results, although it could apply to many scenarios where extending your collection types involves some type of transformation. I recommend creating objects specifically for plotting values in your collection types. To do this, you can create a wrapper object similar to my pattern for extending collections, except have it instead wrap a dataframe and create a static factory method to create the dataframe from the original collection. You can then add any plotting functionality to that object - here I chose a function to create a bar graph.

    import plotly.express as px
    import pandas as pd

    @dataclasses.dataclass
    class MyCollectionPlotter:
        df: pd.DataFrame
        
        @classmethod
        def from_mycollection(cls, mc: MyCollection):
            df = pd.DataFrame([dataclasses.asdict(mt) for mt in mc])
            return cls(df)
        
        def bar(self):
            return px.bar(self.df, x='a', y='b')

And to make the interface clean you can simply add it to a method of the original collection.

    @dataclasses.dataclass
    class MyCollection:
        objs: typing.List[MyType] = dataclasses.field(default_factory=list)
        ...
        def plotter(self):
            return MyCollectionPlotter.from_mycollection(self)

This is a method for extending the object with plotting functionality even when it requires a transformation to a transformation prior to plotting. In many cases you would likely want to call multiple plotting functions in the same script/function, so this gives you that ability. Plotting is a good use-case because it offers an easy to organize a large number of plotting functions with different aesthetics, but this may be an appropriate pattern for other problem types as well.

### Conclusions

Creating custom types for collections makes your code more readable and generally has the same benefits I discussed in my article about the [challenges with dataframes](/post/zods0_problem_with_dataframes.html). The general idea is that more structure is better - it can make your code more readable, easier to maintain, and less error-prone. While at first glance it may feel like overkill because it requires so much additional code, the payoff surely comes as projects become large or dynamic enough such that you need better ways to organize your code.

