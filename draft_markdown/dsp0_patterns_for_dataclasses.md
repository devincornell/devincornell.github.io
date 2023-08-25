---
title: "Patterns and Antipatterns for Dataclasses"
subtitle: "Tips for building clean data objects using the dataclasses module."
date: "August 24, 2023"
id: "dsp0_patterns_for_dataclasses"
---

The popular [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module has been pushing many data scientists to adopt more object-oriented patterns in their data pipelines since its [introduction](https://www.google.com/search?client=firefox-b-1-d&q=dataclasses+pep) to the Python standard library. This module makes it easy to create data types by offering a decorator that automatically generates `__init__` and a number of other boilerplate dunder methods from only a set of statically defined attributes with type hints (I recommend [this tutorial](https://realpython.com/python-data-classes/)). I wanted to share a few patterns I use for working with dataclasses.

### Dataclass Basics

I strongly recommend reading more about the [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module before reading this article if you are not familiar, but the general principles may still be useful if you are not well-versed.

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

### Immutabile

Firstly, I recommend that you make your dataclass objects immutable - that is, objects with a fixed set of attributes whos values cannot be changed after instantiation. Normally Python objects can have new attrributes assigned to them at any point - this is part of the power and flexibility of the language. That said, adding additional attributes to the object other than those described in the definition tends to weaken the value of dataclasses - I recommend avoiding them. 

You can require that dataclasses enforce this rule by passing the `frozen=True` argument to the `dataclass` decorator.

    @dataclasses.dataclass(frozen=True)
    class MyType:
        a: int
        b: float

You will then see an exception when you attempt to assign a value to a new or existing attribute.

    obj = MyType(1, 0.0)

You'll see an exception when changing an exising attribute.

    obj.b = 2

    <string> in __setattr__(self, name, value)
    FrozenInstanceError: cannot assign to field 'b'

And even when creating an additional attribute.

    obj.c = 5

    <string> in __setattr__(self, name, value)
    FrozenInstanceError: cannot assign to field 'c'


### Slots

Next I recommend using the _slots_ interface to fix the set of attributes associated with your object, whether or not you choose to make the values immutable. You can read more about this interface [on the related Python wiki page](https://wiki.python.org/moin/UsingSlots), but essentially you make this gaurantee to the interpreter so that it doesn't need to create extra resources to allow for the introduction of new attributes dynamically. In my experience, this can cut memory usage down by around half, depending on the number of attributes you use.

To use the slots interface, simply provide the attribute names as a list of strings associated with the `__slots__` static attribute. Note that the `dataclass` decorator will ignore this particular attribute, so it should not affect other aspects of your object.

    @dataclasses.dataclass
    class MyType:
        __slots__ = ['a', 'b']
        a: int
        b: float
    
It works like a regular dataclass, but will raise an `AttributeError` if you try to assign a value to a new attribute.

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


### Static Factory Methods

Next I recommend using static factory methods, or static methods that return instances of the containing class, to instantiate dataclasses for cases other than direct assignment of attributes. I believe this is preferable to relying on logic placed in `__post_init__`, which will be executed any time you instantiate the object, even if no actual work should be done.

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

Alternatively, some logic requred to instantiate the object may be placed in a method called `__post_init__`, which will be called at the end of the generated `__init__` after attribute assignment is complete. This method accepts a single argument: a reference to the object itself.
        
        ...
        def __post_init__(self):
            # post-init code here
            pass

Now lets explore an anti-pattern that involves the use of `__post_init__` to see the real value of static factory methods. For example, let us say that you may not always know both `a` and `b`, but you know that the relationship between them should be `a = b/2`. Our new object should be able to fill in the missing attribute given one or the other. So we default both `a` and `b` attributes to None, and add some logic to `__post_init__` that will detect which is missing and compute the other.

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

Using a static factory method approach, we would create two methods: one to be used in the case where `a` is missing and the other to be used when `b` is missing. We want two separate methods because the calling function should know which will be needed and we want to ensure that the input data is always as expected. This follows the [Zen of Python](https://peps.python.org/pep-0020/), which suggests that "explicit is better than implicit." We should ask for what we need explicitly instead of relying on the `__init__` method to infer it.

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


It is also worth noting that in many cases, static factory methods provide cleaner alternatives to using `default_factory` parameters or anything that requires more complex logic. For instance, here I create a more complicated `now_utc` static factory method to record the current datetime with a timestamp. This is better than creating a wrapper or lambda function to pass to `default_factory`.

    import datetime

    @dataclasses.dataclass
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

And the interface would look like this:

    obj = MyType(1.0, 1.0)
    obj.math.product()
    obj.math.sum()

If the container object does any other transformation, you could create the new container and then access its many methods directly.

    mather = obj.math
    mather.sum()
    mather.product()










