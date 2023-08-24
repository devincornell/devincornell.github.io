---
title: "Patterns and Antipatterns for Dataclasses"
subtitle: "Tips for building clean data objects using the dataclasses module."
date: "August 24, 2023"
id: "dsp0_patterns_for_dataclasses"
---

The popular [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module has been pushing many data scientists to adopt more object-oriented patterns in their data pipelines since its [introduction](https://www.google.com/search?client=firefox-b-1-d&q=dataclasses+pep) to the Python standard library. This module makes it easy to create data types by offering a decorator that automatically generates `__init__` and a number of other boilerplate dunder methods from only a set of statically defined attributes with type hints (I recommend [this tutorial](https://realpython.com/python-data-classes/)). I wanted to share a few patterns I use for working with dataclasses.

### Static Attributes and Slots

My first recommendation is to create dataclasses that contain only the attributes that are provided in the original definition, and no more. If you are willing to commit to this restriction, Python can also offer a performance improvement through the _slots_ interface. You can read more about it [on the Python wiki page](https://wiki.python.org/moin/UsingSlots), but essentially it allows Python to refrain from creating a dictionary for every instance of the object and instead allocate a fixed memory space that only has room for references to the attributes you defined.

This example below shows how to use slots - simply provide the attribute names as a list of strings associated with the `__slots__` static attribute. 

    import dataclasses

    @dataclasses.dataclass
    class MyType:
        __slots__ = ['a', 'b']
        a: int
        b: float

This object will refrain from creating a `.__dict__` object that would be used to add a new property to the instance - you would get an error if you tried to define a new one.
    
    obj = MyType(1, 0.0)
    obj.c = 5

    ERROR!!!

Starting in Python 3.11, you can alternatively provide the `slots=True` argument to the `dataclasses.dataclass` decorator to accomplish this (read more [here](https://docs.python.org/3/library/dataclasses.html)).

    @dataclasses.dataclass(slots=True)
    class MyType:
        a: int
        b: float


### Frozen and Immutabile

Next I recommend creating immutable dataclass objects - that is, objects that cannot change after being created. Most of the time you would implement your pipeline as a series of transformations, each of which results in a new object. You may add this restriction to your objects explicitly by passing the `frozen=True` argument to the `dataclasses.dataclass` decorator.

    @dataclasses.dataclass(frozen=True)
    class MyType:
        a: int
        b: float

You will then see an exception when you attempt to assign a value to one of these attributes.

    obj = MyType(1, 0.0)
    obj.b = 5

    ERROR!

### Static Factory Methods

I recommend using static factory methods to instantiate dataclasses for all cases other than direct assignment of attributes. The `dataclasses` module allows you to create a `__post_init__` method that will be called at the end of the generated `__init__` after attribute assignment is complete, but this is not a good solution in most cases. 

In Python, you can use the `classmethod` decorator to create a static factory method like the example below. You can see that `new` just passes `a` and `b` directly to the object constructor - essentially doing nothing except acting as a pass-through.

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float

        @classmethod
        def new(cls, a: int, b: float):
            return cls(a=a, b=b)

Alternatively, you would define the `__post_init__` method like the example below. Notice there are no parameters because all necessary information should already be bound to the object in the generated `__init__`.

        ...
        def __post_init__(self):
            # post-init code here
            pass

As a new example, let us say that you may not always know both `a` and `b` but you know that the relationship `a = b/2`. We can solve this issue by setting `default=None` parameters to `dataclasses.field` and modifying `__post_init__` to look like the following. Note that we throw an exception if neither `a` nor `b` are not `None`.

    @dataclasses.dataclass
    class MyType:
        a: int = dataclasses.field(default=None)
        b: float = dataclasses.field(default=None)

        def __post_init__(self):
            if self.b is None and a is not None:
                self.b = self.a * 2
            elif self.a is None and self.b is not None:
                self.a = self.b / 2
            elif self.a is None and self.b is None:
                raise Exception('Neither a nor b were provided.')

From that logic we know that an instance of `MyType` should always have values for `a` and `b` that are not None, so instead we should build that into the object interface. One approach (although not the best) would be to place this logic in a classmethod called `new` so that one can still create a `MyType` instance if both `a` and `b` are known. 

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float
        
        @classmethod
        def new_partial(cls, a: int = None, b: float = None):
            if b is None and a is not None:
                b = a * 2
            elif a is None and b is not None:
                a = b / 2
            elif a is None and b is None:
                raise Exception('Neither a nor b were provided.')
            return cls(a=a, b=b)

Following the [Zen of Python](https://peps.python.org/pep-0020/), however, we know that "explicit is better than implicit," and so instead of using the defaulted parameters we should create separate class methods for cases where we know `a` but not `b` and vice-versa. This is the best approach.

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float

        @classmethod
        def from_a_only(a: int):
            return cls(a=a, b=a*2)

        @classmethod
        def from_b_only(b: float):
            return cls(a=b/2, b=b)

This pattern is quite useful because the method of creation appears simply as part of the design rather than sequences of if-else logic within functions. This makes the object interface very clear.

In many cases, static factory methods provide cleaner alternatives to using `default_factory` parameters or anything that requires more complex logic. For instance, here I create a more complicated `now_utc` static factory method to record the current datetime with a timestamp. This is better than creating a wrapper or lambda function to pass to `default_factory`.

    import datetime

    @dataclasses.dataclass(slots=True)
    class MyType:
        ts: datetime.datetime

        @classmethod
        def now_naive(cls):
            return cls(datetime.datetime.now())

        @classmethod
        def now_utc(cls):
            return cls(datetime.datetime.now(tz=datetime.timezone.utc))


### Add Functionality Using Composition

As projects grow and requirements change, the number of methods associated with a single dataclass might become unweildy. To organize some of these methods, I recommend creating a new container object that contains only an instance of the original object and operates on that instance. The interface can be exposed from the original object using a `property` method that simply returns a new instance of the container object.

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

        def sum(self)
            return self.mt.a + self.mt.b

And the interface would look like this:

    obj = MyType(1.0, 1.0)
    obj.math.product()
    obj.math.sum()

If the container object does any other transformation, you could create the new container and then access it's many methods directly.

    mather = obj.math
    mather.sum()
    mather.product()


### Handle Missing Data

In many projects, the analyst expects missing data ...

    @dataclasses.dataclass
    class MyType:
        a: int
        b: float

        @property
        def is_missing_a(self) -> bool:
            return self.a is None




