---
title: "Patterns for Data Science: More structure is better"
subtitle: "Use these patterns to create better data pipelines."
date: "May 28, 2023"
id: "zods1_more_structure"
---

As I wrap up my PhD and do some freelance consulting, I wanted to share some programming patterns and principles that I have been using for data science projects. Over the years, I drew on general programming principles like [Zen of Python](https://peps.python.org/pep-0020/) and discussions with software engineers to improve my own research code and teaching materials. I will provide several specific guidelines and patterns based on the needs and trajectories of data science projects I have been involved with up to this point.

My students (and a younger me) have often argued that the approaches here can be tedious to implement and unnescary for most applications. I have been fortunate to have my own mentors that have convinced me, over time, that it is often worth it, in the long run, as no project is ever as small and simple as it seems. It also took me some adjustment to get used to using a proper IDE to help me navigate callstacks and object definitions more quickly - I highly recommend familiarizing yourself with an IDE if you have interest in writing more modular code.

High-quality code means that it is easy to read, requires minimal restructuring, and embodies optimal computational performance - all important aspects of any data science project. The principle for this article is as follows.

> ***The structure of your data should be explicit in your code.***

Now I propose five more specific recommendations from this principle.

1. ***Use objects to represent data.*** The object definition should explicitly describe attributes of the data, and it the object should _only_ be used to store and manipulate the defined features. It should probably be immutable, too.

2. ***Use static factory methods to instantiate data objects.*** Include any logic for creating the object in static factory methods, instead of constructors. Use separate methods for constructing the object from different data sources. Data object constructors should not include any logic - it should simply store the provided data.

3. ***Create types for collections of data objects.*** Create custom types to manage collections of data objects instead of using builtin lists or arrays. For simple cases, you can extend existing builtin types, although collection containers may be appropriate in some cases. At a minimum, you can add static class methods to initialize multiple data objects in sequence.

4. ***Group related methods into wrapper objects.*** Instead of cluttering data objects with a large number of methods for analyzing or transforming, create factory methods that return new objects for transforming or summarizing the original data.

5. ***Retain objects representing missing data.*** Instead of filtering missing data early in your pipeline to simplify downstream methods, continue to use objects even for missing data. While this add additional logic to downstream methods, it may be worth the effort when evaluating the effect of missing data or the project shifts to use a wider range of data.

Now I will give some more detailed guidance.

## 1. Use objects to represent your data

First, I recommend representing each observation or data point as a class or struct with a defined set of properties that is explicit in your code. These classes should follow two principles: (1) the data they contain should be immutable - any transformations should result in new data objects; and (2) data objects should _only_ be used to store and transform the attributes of the data - any other functionality can be implemented through defined methods; 

Here are a few benefits of using this approach.

+ Most importantly, your code can be understood by the reader without running your code or even reading data description documentation.

+ Your compiler or static analyzer (typically as part of your IDE) can identify any errors in your code before you actually run it.

+ You can create objects that represent placeholders for your data to build out your pipeline before you even have your data (assuming you know what it will look like). 

+ You can easily create simulations using dummy objects.


#### Basic Example in Python

First let me start with an illustration of what I mean using Python, although I believe most popular languages will support this approach. To this end, I am going to use the iris dataset loaded from the seaborn package. The dataset is provided as a single dataframe with five columns (of which we will use the 3 shown here).

    import seaborn
    import pandas as pd

    iris_df = seaborn.load_dataset("iris")
    iris_df.head()

The first five rows look like the following:

    sepal_length  sepal_width species
    0           5.1          3.5  setosa
    1           4.9          3.0  setosa
    2           4.7          3.2  setosa
    3           4.6          3.1  setosa
    4           5.0          3.6  setosa

With the help of the increasingly popular `dataclasses` package (see an introduction [here](https://realpython.com/python-data-classes/)), the following class can be used to represent a single observation of this data instead. You don't need to use packages like `dataclasses` or `attrs`, but they make your life easier by creating basic data-only constructors.

You can see that the following object has five attributes, four of which are floats and one of which is a string. A dataclass simply creates a default constructor that requres these five attributes of the same names to be passed. As promised, the object is only focused on is data.

    import dataclasses

    @dataclasses.dataclass
    class IrisEntry:
        sepal_length: float
        sepal_width: float
        petal_length: float
        petal_width: float
        species: str

It is a regular class, so you may add methods or additional attributes, but be sure not to add any additional state information to the class itself.

        ...
        def sepal_area(self) -> float:
            return self.sepal_length * self.sepal_width
        
        def petal_area(self) -> float:
            return self.petal_length * self.petal_width

Later I will discuss collections of these objects, but for now lets stick with classes representing single observations (irises, in this case).

#### Enums for Categorical Variables

In cases where we have categorical variables that can take any of a small, fixed, and enumerable set of values, it is usually best to create an explicit enum type to make their behavior clearer to the reader and make some gaurantees about the input data. I will illustrate this feature in Python using the species variable, although this may not be the best application since it can't handle new species types. In cases where your dataset is not expected to change, it may still be the best option.

First, we can list all species in the dataset:

    {'setosa', 'versicolor', 'virginica'}

Now, create an enum using the enum package to represent the various species.

    import enum
    class Species(enum.Enum):
        SETOSA = enum.auto()
        VERSICOLOR = enum.auto()
        VIRGINICA = enum.auto()

For clarity, change the type hint on the species attribute.

        ...
        species: Species

Then, we will need a mapping from the original input data to the enum values. We can use a simple dictionary for that. This dictionary maps the strings to species types.

    species_name_map = {
        'setosa': Species.SETOSA,
        'versicolor': Species.VERSICOLOR,
        'virginica': Species.VIRGINICA,
    }

Then, as part of the object construction code, we would pass the input string through this map to get the actual species type. This creates gaurantees that the specified enum values are exhaustive of all possible inputs, and the construction code will raise an exception if it does not appear in this set.

Note that in cases where there are a larger number of species that are held in some database, it might still be good to do validation when the object is being created.

#### Basic Transformations

While this particular data object should be immutable, we can create methods to return objects of a different data type to represent some data transformation. For instance, lets say we want to create an additional object to represent surface areas in an iris. Using the same procedure, we create a new dataclass and add a method to `IrisEntry` to create this object.

    @dataclasses.dataclass
    class IrisArea:
        sepal_area: float
        petal_area: float
        species: Species
        
        def surface_area(self) -> float:
            return self.sepal_area + self.petal_area

And the method used to create the iris area will look like the following.

        ...
        def calc_area(self) -> tuple:
            return IrisArea(self.sepal_area(), self.petal_area())

Create the iris entry and the area objects like this:

    iris_entry = IrisEntry(1.0, 2.0, 3.0, 4.0, 'setosa')
    iris_area = iris_entry.calc_area()
    iris_area.petal_area, iris_area.species

In this way, each data object stores only one type of data and derivative data types can be produced using methods that are part of data objects. This is a simple, yet powerful, example of a fundamental operation in data science projects.

Using the data object approach, you are building gaurantees into any downstream operation that uses these objects: namely, you are gauranteeing that these attributes exist as part of your object. Any methods that are part of this data object use only these original attributes (in addition to any input), and apply only to a single iris object (rather than a set of them). Without ever touching your code, both human readers and static analyzers know the structure of your data.


## 2. Use static factory methods to instantiate data objects

My second recommendation is to use static factory methods, rather than constructors, to instantiate data objects. This means putting any logic needed for conversion or preprocessing into a non-constructor method that returns an instance of the class itself. The essential feature of this pattern is that you can separate the logic of parsing or transforming data from the actual data itself by placing them in separate functions.

Perhaps the most useful feature of this approach is that you can easily add methods for constructing the object from different types of input data. For instance, you could have separate methods for constructing a data object from JSON and CSV file formats. Or, perhaps you have two different html formats in which your data could appear - in that case, you can add a factory method for each version.

In Python, the factory design pattern is implemented using a [class method](https://realpython.com/factory-method-python/), which is a function with the `classmethod` decorator that returns an instance of the data object to which it is attached. Building on the previous code, the factory method would look like the following:

        ...
        @classmethod
        def from_dataframe_row(cls, row: pd.Series):
            return cls(
                sepal_length = row['sepal_length'],
                sepal_width = row['sepal_width'],
                petal_length = row['petal_length'],
                petal_width = row['petal_width'],
                species = species_name_map[row['species']],
            )

Note that in class methods, we follow the convention of calling the first argument "`cls`" instead of "`self`" because these methods are passed the class type itself instead of an instance of the class. So the call to `cls()` is actually calling the object constructor, which is created by the `dataclass` decorator in this case.

We then pass the rows of the iris dataframe to the factory method using the following code.

    for ind, row in iris_df.iterrows():
        new_iris = IrisEntry.from_dataframe_row(row)
        print(new_iris)
        break

Which prints the following:

    IrisEntry(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species='setosa')

Pretty straightforward - you can apply the factory method to each row of the dataframe after using pandas to read the csv file. I will give an example of an extended solution to this later when I discuss creating types for collections of data objects.

#### Additional Static Factory Methods

Now, for example, lets say that you have additional data in json format, which I simulate here by transforming the dataframe.

    iris_list = iris_df.to_dict(orient='records')
    iris_list[:2]

The data will look something like this after parsing the json to python objects.

    [
        {
            'sepal_length': 5.1,
            'sepal_width': 3.5,
            'petal_length': 1.4,
            'petal_width': 0.2,
            'species': 'setosa'
        },
        {
            'sepal_length': 4.9,
            'sepal_width': 3.0,
            'petal_length': 1.4,
            'petal_width': 0.2,
            'species': 'setosa'
        }
    ]

Simply create a new factory method called `from_json` to create a data object from json instead of a dataframe.

        ...
        @classmethod
        def from_json(cls, iris_data: dict):
            return cls(
                sepal_length = iris_data['sepal_length'],
                sepal_width = iris_data['sepal_width'],
                petal_length = iris_data['petal_length'],
                petal_width = iris_data['petal_width'],
                species = species_name_map[iris_data['species']],
            )

You must explicitly choose the constructor depending on the input data this way, which is a good thing. 

#### Simple Factory Patterns

Sometimes your program may need to decide which method to used - in that case you can use a factory-like pattern.

    constructor_method_map = {
        'json': IrisEntry.from_json,
        'dataframe': IrisEntry.from_dataframe_row,
    }

    def iris_factory(data_format: str, raw_data: typing.Union[dict, pd.Series]) -> IrisEntry:
        return constructor_method_map[data_format](raw_data)

## 3. Create types for collections of data objects

My third recommendation is to create custom collection objects by extending existing collection types, or, in more complicated cases, by encapsulating the collections (the decision may be language-dependent). This alone improves readability, but, perhaps more importantly, it makes it easier to assess exactly which operations can and should be done on a collection of these particular objects. This too follows the Zen of Data Science tenant that "explicit is better than implicit."

#### Inherit from builtin types

In python, you would most likely want to use the `typing` package to inherit from builtin types. We inherit from `typing.List` here, and the type hint gives additional information about the intended use of the class.

    import typing
    class Irises(typing.List[IrisEntry]):
        
        @classmethod
        def from_dataframe(cls, df: pd.DataFrame):
            irises = cls()
            for ind, row in iris_df.iterrows():
                irises.append(IrisEntry.from_dataframe_row(row))
            return irises

You can also add the json factory method.

        ...
        @classmethod
        def from_json(cls, iris_list: list):
            return cls([IrisEntry.from_json(irow) for irow in iris_list])

Then construct the object as follows.
    
    irises = Irises.from_json(iris_list)

Here `Irises` is essentially a list with a custom type that includes additional factory methods at this point.

#### Encapsulation approach

Note that alternatively you could create a more complicated encapsulation scheme when the collection needs to do more complicated things.

    @dataclasses.dataclass
    class IrisCollection:
        irises: typing.List[IrisEntry]
        
        @classmethod
        def from_json(cls, iris_list: list):
            return cls(irises=[IrisEntry.from_json(irow) for irow in iris_list])

    iris_collection = IrisCollection.from_json(iris_list)

This requires more work to build out methods for the collection though, so I recommend it primarily in more complicated cases.



#### Transformations on collections

Transformations on collections may be useful for a number of applications. Whether you extended a built-in collection or made your own, any methods you would apply to a collection of data objects can be placed in these classes.

As an example, lets create a function that groups irises by their species. Note, importantly, that we use `self.__class__()` to construct an `Irises` object instead of a regular list.

        ...
        def group_by_species(self) -> typing.Dict[Species, Irises]:
            groups = dict()
            for ir in self:
                groups.setdefault(ir.species, self.__class__())
                groups[ir.species].append(ir)
            return groups

You could create filter, map, or a number of other methods here for manipulating collections, just be sure to wrap the output in the collection object constructor.


#### Concurrency in Transformations

Naturally, these may be good places to add parallelization code. Parallelization is another case where having immutable data objects, and therefore clean functions (those that have no side effects other than to produce the output), is particularly useful.

For example, refer to the `IrisEntry.calc_area` method we created earlier to produce the `IrisArea` object associated with each `IrisEntry` object. We can create a new method on `Irises` which opens a [pool of workers](https://docs.python.org/3/library/multiprocessing.html) with the multiprocessing module and calls the `calc_area` method on each iris in parallel.

        ...
        def calc_areas_parallel(self, n_processes: int = 4) -> typing.List[IrisArea]:
            with multiprocessing.Pool(n_processes) as p:
                areas = p.map(self.calc_iris_area, self)
            return areas
        
        @staticmethod
        def calc_iris_area(iris: IrisEntry) -> IrisArea:
            return iris.calc_area()

All parallelization code here exists within the transformation method itself.


## 4. Group related methods into wrapper objects

It is generally inadvisable to create data objects with a large number of methods for transformation or summarization because it will make it harder to maintain and use (see [discussions amongst Pandas developers](https://www.reddit.com/r/Python/comments/11fio85/comment/jajz9a0/?utm_source=share&utm_medium=web2x&context=3)). As you develop new ways to transform and view your data objects, it will be useful to extend functionality into new namespaces.

To do this, I recommend adding functionally-related methods to a separate wrapper class which maintains _only_ a reference to the original data object. You can then create a method in the data object which instantiates the wrapper object simply by passing a reference to itself, and you can call any methods on that instance.

#### Basic wrapper object

Let us start with an example where we want to create plotting functionality to our data object. In this case, we could imagine a wide range of functions that make visualizations in various ways, and it might clean things up to have them defined in a single place that won't clutter up the tranformation methods that are a part of the original data object. This is a good case for this approach.

Lets first create a new class that will manage the plotting methods. The following is a dataclass with exactly one attribute - the `Irises` that will be plotted. I include one example method that plots the sepal length against it's width. Note that this method primarily access data from the `self.irises` instance.

    import matplotlib.pyplot as plt
    @dataclasses.dataclass
    class PyPlotter:
        irises: Irises
        
        def sepal_scatter(self):
            plot = plt.scatter(
                x = [ir.sepal_length for ir in self.irises], 
                y = [ir.sepal_width for ir in self.irises], 
            )
            return plot
    
Because it is a dataclass, you can use the constructor directly and then call the method on that object. 

    plotter = PyPlotter(irises)
    plotter.sepal_scatter()

This solution works quite fine. However, it may be convenient to access these methods directly from the Irises object. Because the `PyPlotter` object contains only the irises data, we can create a method to return the plotter on which we can then call the plotting methods. In python, we can use the `property` decorator that will call a function merely by accessing an attribute of the same name. 

        ...
        @property
        def plot(self):
            return PyPlotter(self)

This method simply calls the default constructor of the plot class. Now we can access these methods as attributes of the `plot` property.

    irises.plot.sepal_scatter()

While there is some performance cost to this approach, the organizational benefit may be substantial enough to warrant it.

#### More Complicated Method Classes

There may be cases where you want to similarly extend the data object in a way that changes the format of the original data. In cases when that format change is expensive, you can follow a formula that is similar to the above, but do the transformation in a factory method of the child class which is called from a method of the data class.

As an example, lets say we want to use ggplot through the `plotnine` python package to plot features of our irises. Unlike `matplotlib`, plotting in this package is typically done through dataframes, so we will need to convert the `Irises` object to a dataframe before doing any plotting. This new class includes the factory method constructor and a method to create a scatter plot.

    import plotnine
    @dataclasses.dataclass
    class GGPlotter:
        iris_df: pd.DataFrame
            
        @classmethod
        def from_irises(cls, irises: Irises):
            return cls(pd.DataFrame([dataclasses.asdict(ir) for ir in irises]))
        
        def sepal_scatter(self):
            return (plotnine.ggplot(plotnine.aes(x='sepal_length', y='sepal_width'), self.iris_df)
                + plotnine.geom_point()
            )

Then, we simply call the factory method constructor from a data object method to instantiate the plotter. The method requires more than a call to a constructor, so we do not use the `property` decorator to make it clear to the user that something expensive is happening here.
        
        ...
        def ggplotter(self):
            return GGPlotter.from_irises(self)

And then we can access the plotting methods from a temporary or permanent instance of `GGPlotter`.

    irises.ggplotter().sepal_scatter()

    plotter = irises.ggplotter()
    plotter.sepal_scatter()

Notice that this example is very similar to the `IrisArea` above - it is a convenient pattern for both extending functionality and creating substantive transformations.


## 5. Also keep objects for missing data

My final recommendation here is to keep track of missing data throughout your pipeline rather than filtering it in intermediary steps. As with any software engineering project, the questions you ask using your data will change along with the assumptions you make to answer them. For that reason, I recommend refraining from filtering missing data at any point in your pipeline - instead, create objects that store the missing data just as you would with non-missing data, and build methods to check for the missing data.


#### Explicit Checking

The method could simply look like the following.

        ...
        @property
        def species_is_missing(self) -> bool:
            return self.species is None

And use this method to filter at the point of use, rather than as a step in the process.

    missing_irises = [
        IrisEntry(1.0, 1.0, 1.0, 1.0, None),
        IrisEntry(1.0, 1.0, 1.0, 1.0, None),
    ]
    sepal_lengths = [ir.sepal_length for ir in missing_irises if not ir.species_is_missing]

#### Custom Exceptions

While you would experience a performance hit, you could also use exception handling to identify missing data. This approach is more "pythonic" in that you try to access the data and simply raise an error when it fails or is not available. Again, this would incur a performance hit, so I typically use it less.

In Python, an exception is any class which inherits from `BaseException`, so we can create a custom missing data exception using the following code.

    class MissingSepalLength(BaseException):
        pass

Now we simply want to raise the exception when the data is missing. There are other ways to do this, but lets say we simply access the `sepal_length` attribute through a custom getter method. The method raises an exception if the value is None, and otherwise returns the value.

        ...
        def get_sepal_length(self) -> float:
            if self.sepal_length is None:
                raise MissingSepalLength(f'The sepal length attribute is None.')
            return self.sepal_length

Then in your downstream code you should use a `try`...`except` to handle the missing data - in this case, we simply ignore it.

    for ie in missing_irises:
        try:
            print(ie.get_sepal_length())
        except MissingSepalLength:
            pass # ignore it


## Feedback?

Message me on Instagram/Threads/Twitter @ devinjcornell

