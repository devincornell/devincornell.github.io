---
title: "Using Slot Classes in DocTable Schemas"
subtitle: "The challenge of dynamically creating"
date: "June 15, 2021"
id: "using_slots_with_doctable_schema"
---

_Motivation_: I thought it would be convenient to use [slot-based classes](https://book.pythontips.com/en/latest/__slots__magic.html) to represent database rows because of their lower memory usage and faster variable access. 
Typically results from `sqlalchemy` select queries are provided as named tuples, but my work in allowing `DocTable` schemas to be defined in terms of [dataclasses](https://doctable.org/examples/dataclass_example.html) also allows users to use these classes to represent rows as objects. 
There is overhead in the construction of these classes (more for time than memory usage), but it can be valuable because we can add additional methods to interact with the rows (of course, this behavior can be disabled). 
Ideally I could use slots to further reduce memory overhead while maintaining the ability to write custom methods, but the problem is that creating slot-based classes with defaulted parameters like those needed to construct database schemas is not allowed. 

For example, the definition of the following class will result in the exception "`ValueError`: 'a' in __slots__ conflicts with class variable."

    class Test1:
        __slots__ = ['a']
        a: int = 5


Typically the dataclasses I use to define doctable schemas look like the following. 
Note that the `id` column (typical of database schemas) is listed first and given a default parameter to indicate that it is the primary key and automatically incremented. 
Thus, all member variables after this are required to have defaulted parameters (which are usually `doctable.Col()` objects) and normally adding `__slots__` to this class would then not be allowed. 

    @dataclasses.dataclass
    class MyRow(doctable.DocTableRow):
        id: int = doctable.IDCol()
        payload: int = doctable.Col()


***My solution*** was to create a [decorator](https://realpython.com/primer-on-python-decorators) that would convert the provided class to a dataclass so that it would add `__init__` (among other dunder methods) with defaulted parameter values. 
Next, I remove defaulted values from the class definition, and add them as `__slots__`. 
Finally, I create a new class which inherits from this modified class as well as `DocTableRow` to include methods that doctable schemas require for basic operation. 

For an example of the usage of this decorator (which I called `doctable.row`), this is how we would define a schema under this paradigm:

    @doctable.row
    class MyRow:
        __slots__ = []
        id: int = doctable.IDCol()
        payload: int = doctable.Col()

Note that we must include `__slots__ = []` so that the end class (which inherits from the original `MyRow`) will be a slot-based class (all inheriting classes must include this in the original definition). 
The decorator will issue an error if this is not included, but it can be disabled (along with all the advantages of slot classes) using the syntax `@doctable.row(require_slots=False)`. 
We can also pass typical `@dataclasses.dataclass` parameters such as `init=False` or `repr=False` through the `row` decorator parameters. 
Now we can just include the `@doctable.row` as a decorator instead of using `@dataclasses.dataclass` _and_ inheriting from `DocTableRow`. 

## Benchmarks

I ran some benchmarks to test memory usage between my solution with slots. 
The x-axis shows the number of objects I created. 
Each object has 10 integer member variabilles (arbitrarily). 
The y-axis shows memory usage in GB.

![benchmark results](https://storage.googleapis.com/public_data_09324832787/slots_memory_usage.png)

On average, with objects of this size, slot classes use about 1/2 the memory of a regular dict-based class.



