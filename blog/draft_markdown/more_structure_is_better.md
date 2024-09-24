---
title: "Why More Structure (and More Code) is Better"
subtitle: "Using principles of encapsulation to improve the ways you work with tabular data."
date: "May 3, 2024"
id: "more_structure_is_better"
blogroll_img_url: ""
---

My first formal introduction to programming came from reading the 1983 C Programming Language Book by Kernighan and Ritchie. This book is a classic - written by the creators of the foundational C language itself (and one of the UNIX founders), this book allows readers to see code through the eyes of one who designs languages, rather than one who simply uses them. The authors demonstrated the elegance and beauty that an expressive language can provide, and show how complex design patterns can emerge from seemingly simple principles. The poetry in this book encourages readers to develop elegant, efficient solutions to programming problems and take full advantage of language features. This approach served me well as an electrical engineer, where elegant solutions are often very powerful.

Fast forward 7 years to my first year of the Sociology Ph.D. program in UC Santa Barbara where I was investing heavily in learning Python as a tool for empirical analysis. I carried these same habits into my work manipulating large datasets 





While now antiquated in style (the language was never really intended to be a patterns/style book) there is an inherent and enduring focus on the elegance and beauty that an expressive langauge can provide. After all, if you are going to design a language, why not make it beautiful?

Fast forward 7 years where I am starting to invest serious time in Python 






Much like methematics, C code reads more like poetry than instructions to be sent to the comptuer

The C language and its peers was a massive step forward for programmers - 

get in the heads of the language designers in a way that we don't see



Last year I wrote an article about [why I try to avoid using dataframes](/post/zods0_problem_with_dataframes.html). Dataframes are powerful because they are so versatile and flexible, but my argument was that rigorous data analysis code should introduce as much rigidity as possible to reduce the likelihood of mistakes. Over the last decade learning, teaching, and practicing 



















The popular [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module has been pushing many data scientists to adopt more object-oriented patterns in their data pipelines since it was [introduced](https://www.google.com/search?client=firefox-b-1-d&q=dataclasses+pep) to the Python standard library. This module makes it easy to create data types by offering a decorator that automatically generates `__init__` and a number of other boilerplate dunder methods from only a set of statically defined attributes with type hints (I recommend [this tutorial](https://realpython.com/python-data-classes/)). Previously I have written about [object-oriented alternatives to dataframes](/post/zods0_problem_with_dataframes.html) for data science, and in this article I wanted to share a few patterns I use for data objects created with `dataclasses` in my own work.

![Dataclass transformation visualization.](https://storage.googleapis.com/public_data_09324832787/dataclasses.svg)

### Dataclass Basics

Firstly, I strongly recommend reading more about the [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module before reading this article if you are not familiar, but the general principles may still be useful otherwise.

You can create a dataclass using the `dataclasses.dataclass` decorator on a class definition. The class definition should contain a set of static attributes with type hints that can have default values. From this class definition, the decorator creates an `__init__` method which includes all of these attributes as parameters, and the defaulted attributes are also default parameter values.

    import dataclasses

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float
        c: str = ''

You can instantiate this object using the generated constructor as you would expect.

    obj = MyType(1, 1.0)
    obj = MyType(1, 2.0, c='hello')
    obj = MyType(
        a = 1,
        b = 2,
        c = 'hello world',
    )

There are many more features than this that I may bring up when discussing anti-patterns, but it is worth reading more about the module if you are interested in using it.

### 1. Immutabile

Firstly, I recommend that you make your dataclass objects immutable - that is, objects with a fixed set of attributes whose values cannot be changed after instantiation. Normally Python objects can have new attributes assigned to them at any point - this is part of the power and flexibility of the language. That said, adding additional attributes to the object other than those described in the definition tends to weaken the value of dataclasses - I recommend avoiding them. 

You can require that dataclasses enforce this rule by passing the `frozen=True` argument to the `dataclass` decorator.

    @dataclasses.dataclass(frozen=True)
    class MyType:
        a: int
        b: float

You will then see an exception when you attempt to assign a value to a new or existing attribute.

    obj = MyType(1, 0.0)

You'll see an exception when changing an existing attribute.

    obj.b = 2

    <string> in __setattr__(self, name, value)
    FrozenInstanceError: cannot assign to field 'b'

And even when creating an additional attribute.

    obj.c = 5

    <string> in __setattr__(self, name, value)
    FrozenInstanceError: cannot assign to field 'c'


### 2. Slots

Next, I recommend using the _slots_ interface to fix the set of attributes associated with your object, whether or not you choose to make the values immutable. You can read more about this interface [on the related Python wiki page](https://wiki.python.org/moin/UsingSlots), but essentially you make this guarantee to the interpreter so that it doesn't need to create extra resources to allow for the introduction of new attributes dynamically. In my experience, this can cut memory usage down by around half, depending on the number of attributes you use.

To use the slots interface, simply provide the attribute names as a list of strings associated with the `__slots__` static attribute. Note that the `dataclass` decorator will ignore this particular attribute, so it should not affect other aspects of your object.

    @dataclasses.dataclass
    class MyType:
        __slots__ = ['a', 'b']
        a: int
        b: float
    
It works like a regular dataclass but will raise an `AttributeError` if you try to assign a value to a new attribute.

    obj = MyType(1, 0.0)
    obj.b = 2
    obj.c = 5

The error will look like this:
    
    ---> 11 obj.c = 5
    AttributeError: 'MyType' object has no attribute 'c'

Starting in Python 3.11, you can alternatively provide the `slots=True` argument to the `dataclasses.dataclass` decorator to accomplish this (read more [here](https://docs.python.org/3/library/dataclasses.html)).

    @dataclasses.dataclass(slots=True)
    class MyType:
        a: int
        b: float


### 3. Static Factory Methods

Next, I recommend using static factory methods, or static methods that return instances of the containing class, to instantiate dataclasses for cases other than direct assignment of attributes. I believe this is preferable to relying on logic placed in `__post_init__`, which will be executed any time you instantiate the object, even if no actual work should be done.

In Python, you can use the `classmethod` decorator to create a static factory method like the example below. You can see that `new` just passes `a` and `b` directly to the object constructor - essentially doing nothing except acting as a pass-through.

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float

        @classmethod
        def new(cls, a: int, b: float):
            # logic goes here
            return cls(a=a, b=b)

Using this approach, instantiating a new object is straightforward.

    obj = MyType.new(1.0, 2.0)

Alternatively, the `dataclass` decorator allows you to place some logic requred to instantiate the object in a method called `__post_init__`, which will be called at the end of the generated `__init__` after attribute assignment is complete. This method accepts a single argument: a reference to the object itself after assignment.
        
        ...
        def __post_init__(self):
            # post-init code here
            pass

I will now cover a few use-cases to demonstrate the value of using static factory methods over `__post_init__`.

##### Non-data Arguments

The most obvious use-case for static factory methods arises when the interface you use to create the object will be different than the interface offered in the dataclass-generated `__init__` method. This might occur, for instance, if some parameters needed to create the object will not be used later, or when the data being stored is actually a function of some other parameters.

For example, imagine we want to create an object that maintains the current timestamp and some other data. The dataclass will just include a timestamp and the other data, but we shouldn't need to provide a timestamp object directly from the outside since we know that attribute always be a timestamp - we should be able to create it from within the object. To do this, we create a static factory method that just requires a time zone - the timestamp can then use that information, but the time zone itself need not be stored elsewhere because we can always get it from the timestamp.

    import datetime

    @dataclasses.dataclass
    class MyTimeKeeper:
        ts: datetime.datetime
        other_data: dict

        @classmethod
        def now(cls, tz: datetime.timezone, **other_data):
            return cls(datetime.datetime.now(tz=tz), other_data)

Of course, you can build out even higher-level static factory methods to support the object as well. Both allow you to create the object without providing a timestamp.
        
        ...
        @classmethod
        def now_utc(cls, **other_data):
            return cls.now(datetime.timezone.utc, **other_data)
        
        @classmethod
        def now_naive(cls, **other_data):
            return cls.now(None, **other_data)

Creating these objects only using the static factory methods guarantees that the stored timestamp will always be a timestamp but also makes clear to the reader that we only need the time zone for making the timestamp - not for later use.


An approach using `__post_init__` would require us to partially initialize the object by leaving `ts = None` and then create it later, but this has several downsides: (a) it is unclear to the reader how and if the timestamp may be used in the future, (b) you do not have a lot of flexibility in the ways you instantiate these objects, and (c) the interface for creating the object is not that clean.

    @dataclasses.dataclass
    class MyTimeKeeperPostInit:
        tz: datetime.timezone
        other_data: dict
        ts: datetime.datetime = None
        
        def __post_init__(self):
            self.ts = datetime.datetime.now(self.tz)


##### Parameter Co-dependence

Now let us explore the case where have a dataclass with two attributes `a` and `b` and we know that if one of these values is not provided, the object should compute the other following the relationship `b = 2a`. I created two static factory methods to handle each of these cases. Note that we require the customer (user) to choose this case explicitly following the [Zen of Python](https://peps.python.org/pep-0020/), which suggests that "explicit is better than implicit." This object should not be required to guess which case will need to be handled - the user can do that. 

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float

        @classmethod
        def from_a_only(cls, a: int):
            return cls(a=a, b=a*2)

        @classmethod
        def from_b_only(cls, b: float):
            return cls(a=b/2, b=b)

    obj = MyType.from_a_only(1)
    obj = MyType.from_b_only(2)

The anti-pattern that relies on `__post_init__` would require us to place some if-else logic inside the object constructor to handle these cases. Unfortunately many Python APIs rely on this type of "guessing", even though the [Zen of Python](https://peps.python.org/pep-0020/) says "in the face of ambiguity, refuse the temptation to guess."

    @dataclasses.dataclass
    class MyType:
        a: int = None
        b: float = None

        def __post_init__(self):
            if self.b is None and a is not None:
                self.b = self.a * 2
            elif self.a is None and self.b is not None:
                self.a = self.b / 2
            elif self.a is None and self.b is None:
                raise Exception('Neither a nor b were provided.')

It is also worth noting that in many cases, static factory methods provide cleaner alternatives to using `default_factory` parameters or anything that requires more complex logic. 

### 4. Extend Functionality Using Composition

As projects grow and requirements change, the number of methods associated with a single dataclass might become unwieldy. To organize some of these methods, I recommend creating a new container object that contains only an instance of the original object and operates on that instance. The interface can be exposed from the original object using a `property` method that simply returns a new instance of the container object.

In this example, we define `MyTypeMath` to be a container around `MyType` using the dataclass decorator, and in methods simply refer to this attribute instead of `self`. In this way, you can easily grow the code associated with the dataclass.

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float

        @property
        def math(self):
            return MyTypeMath(self)

    @dataclasses.dataclass
    class MyTypeMath:
        mt: MyType

        def product(self):
            return self.mt.a * self.mt.b

        def sum(self):
            return self.mt.a + self.mt.b

And the interface would be used like this:

    obj = MyType(1.0, 1.0)
    obj.math.product()
    obj.math.sum()

If the container object does any other transformation, you could create the new container and then access its many methods directly.

    mather = obj.math
    mather.sum()
    mather.product()


### 5. Define custom types for transformations

My last pattern concerns chaining transformations from one dataclass object to another. This will look much like the previous pattern, but instead of creating a wrapper object that only adds functionality, we create a second object that uses a static factory method involving some transformation. In turn, the original class uses that static factory method instead of the basic `__init__` method provided by `dataclasses`.

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float
        
        def get_summary(self):
            return MySummaryType.from_mytype(self)

    @dataclasses.dataclass
    class MySummaryType:
        added: float
        product: float
        
        @classmethod
        def from_mytype(cls, mt: MyType):
            return cls(mt.a + mt.b, mt.a * mt.b)

    print(MyType(1, 4).get_summary())

While most transformations will operate on collections of dataclasses (which I will cover in a future article), this approach works well for basic object-wise transformations.

### Conclusions

Object oriented design can drastically improve the maintainability of your data science code, and these patterns will improve the readability and error robustness of those designs.

In [the next article](/post/dsp1_collections.html) I will be covering patterns for working with collections of dataclasses - aggregation, filtering, grouping, and more.




