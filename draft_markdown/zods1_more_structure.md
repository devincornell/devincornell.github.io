---
title: "Data Science Patterns: More structure is better"
subtitle: "I propose several patterns for building your data science pipelines."
date: "May 28, 2023"
id: "zods_more_structure"
---

As I wrap up my data-heavy PhD in Sociology and do some freelance consulting, I wanted to share some suggestions for software design principles that can improve the flexibility, reproducibility, and risk of errors in your data analysis code. I grew into these principles as I completed a wide range research projects and taught many cohorts of data-oriented social science undergraduates, but I found discussions with professional software engineers to be especially helpful, as they are specifically trained to write high-quality code. There is much that data scientists can learn from software engineers.

While some of these are derived directly from classical design patterns and guidelines proposed in the [Zen of Python](https://peps.python.org/pep-0020/), others come directly from my own experience in managing both large and small data science projects. Some of these recommendations depart from conventional wisdom, and, in those cases, I argue that the specific requirements of data science projects may indeed justify the departure.

My students (and a younger me) have often argued that the approaches here can be tedious to implement and unnescary for most applications. I have been fortunate to have my own mentors that have convinced me, over time, that it is often worth it, in the long run, as no project is ever as small and simple as it seems. It also took me some adjustment to get used to using a proper IDE to help me navigate callstacks and object definitions more quickly - I highly recommend familiarizing yourself with an IDE if you have interest in writing more modular code.

High-quality code means that it is easy to read, requires minimal restructuring, and embodies optimal computational performance - all important aspects of any data science project. This will likely be the first of several blog posts on the topic. The principle for this article is as follows.

> ***The structure of your data should be explicit in your code.***

More specifically, *use objects to explicitly represent your data* at every stage of your pipeline, and avoid dataframes or nested iterables when possible. This builds upon the  principles suggesting that "explicit is better than implicit" and "flat is better than nested." Building explicit structure into your data pipeline can provide some built-in gaurantees about your data at every stage of your pipeline.

Now I propose five more specific recommendations that follow this tenant.

1. ***Use objects to represent data.*** The object definition should explicitly describe attributes of the data, and it should _only_ be used to store and manipulate the defined features. It should probably be immutable, too.

2. ***Instantiate the objects using factory method constructors.*** The constructors of your data objects should only accept raw data elements - use factory methods for alternate constructors that involve any parsing or conversion/validation logic.

3. ***For simple cases, extend collection data types.*** When you need to create objects for collections of data, first try subclassing existing types like lists or arrays to create case-specific factory method constructors. This is simpler than creating new objects that contain collection types, and worth using until your use case becomes more complicated.

4. ***Add additional functionality through classes that access the same data.*** Create methods in your data objects to return new objects with that functionality instead of using inheritance or other OOP techniques. This prevents your data objects from becoming too cluttered as you add new functionality to extend your analyses.

5. ***Also keep objects for missing data.*** Instead of filtering missing data early in your pipeline to simplify downstream methods, continue to use objects even for missing data. While this add additional logic to downstream methods, it may be worth the effort when evaluating the effect of missing data or the project shifts to use a wider range of data.

# 1. Use objects to represent your data

First, I recommend representing each observation or data point as a class or struct with a defined set of properties that is explicit in your code. These classes should follow two principles: (1) the data they contain should be immutable - any transformations should result in new data objects; and (2) data objects should _only_ be used to store and transform the attributes of the data - any other functionality can be implemented through defined methods; 

Here are a few benefits of using this approach.

+ Most importantly, your code can be understood by the reader without running your code or even reading data description documentation.

+ Your compiler or static analyzer (typically as part of your IDE) can identify any errors in your code before you actually run it.

+ You can create objects that represent placeholders for your data to build out your pipeline before you even have your data (assuming you know what it will look like). 

+ You can easily create simulations using dummy objects.


### Example in Python

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

With the help of the increasingly popular `dataclasses` package, the following class can be used to represent a single observation of this data instead. You can see that the following object has five attributes, four of which are floats and one of which is a string. A dataclass simply creates a default constructor that requres these five attributes of the same names to be passed. As promised, the object is only focused on is data.

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

Later I will discuss collections of these objects, but for now lets stick with classes representing single observations.

## Enums for Categorical Variables

Note that in cases where we have categorical variables that can take any of a small, fixed, and enumerable set of values, it is usually best to create an explicit enum type to make their behavior clearer to the reader and make some gaurantees about the input data. I will illustrate this feature in Python using the species variable, although this may not be the best application since it can't handle new species types. In cases where your dataset is not expected to change, it may still be the best option.

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

Then, as part of the object construction code, we would pass the input string through this map to get the actual species type.

Note that in cases where there are a larger number of species that are held in some database, it might still be good to do validation when the object is being created.

## Basic Transformations

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


# 2. Instantiate data objects using factory method constructors

My second recommendation is to use factory methods, rather than default constructors, to instantiate data objects. This means putting any logic needed for parsing or preprocessing into a non-constructor method that returns an instance of the data object. This recommendation involves use of the [factory design pattern](https://web.archive.org/web/20210130220433/http://as.ynchrono.us/2014/12/asynchronous-object-initialization.html), an important design pattern used by software engineers. The essential feature of this pattern is that you can separate the logic of parsing or transforming data from the actual data itself by placing them in separate functions.

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
                species = row['species'],
            )

Note that in class methods, we follow the convention of calling the first argument "`cls`" instead of "`self`" because these methods are passed the class type itself instead of an instance of the class. So the call to `cls()` is actually calling the object constructor, which is created by the `dataclass` decorator in this case. So we pass the rows of the iris dataframe to the factory method using the following code.

    for ind, row in iris_df.iterrows():
        new_iris = IrisEntry.from_dataframe_row(row)
        print(new_iris)
        break

Which prints the following:

    IrisEntry(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species='setosa')

Pretty straightforward - you can apply the factory method to each row of the dataframe after using pandas to read the csv file.

Now lets say that you have additional data in json format, which I simulate here by transforming the dataframe.

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
                species = iris_data['species'],
            )


# 3. Represent Collections as Objects

My third recommendation is to create custom collection objects by extending existing collection types, or, at the very least, by encapsulating the collections (the decision may be language-dependent). This alone improves readability, but, perhaps more importantly, it makes it easier to assess exactly which operations can and should be done on a collection of these particular objects. This too follows the Zen of Data Science tenant that "explicit is better than implicit."


In python, you would most likely want to use the `typing` package.

    import typing
    class Irises(typing.List):
        
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

Note that alternatively you could create a more complicated encapsulation scheme when the collection needs to do more complicated things.

    @dataclasses.dataclass
    class IrisCollection:
        irises: typing.List[IrisEntry]
        
        @classmethod
        def from_json(cls, iris_list: list):
            return cls(irises=[IrisEntry.from_json(irow) for irow in iris_list])

    iris_collection = IrisCollection.from_json(iris_list)

This requires more work to build out methods for the collection though, so I recommend it primarily in more complicated cases.



## Transformations on Collections

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

### Concurrency in Transformations

As a logical extension, note that these may be good placess to add parallelization code.

For instance, refer to the `IrisEntry.calc_area` method we created earlier to produce the `IrisArea` object associated with each `IrisEntry` object. We can create a new method on `Irises` which opens a [pool of workers](https://docs.python.org/3/library/multiprocessing.html) with the multiprocessing module and calls the `calc_area` method on each iris in parallel.

        ...
        def calc_areas_parallel(self, n_processes: int = 4) -> typing.List[IrisArea]:
            with multiprocessing.Pool(n_processes) as p:
                areas = p.map(self.calc_iris_area, self)
            return areas
        
        @staticmethod
        def calc_iris_area(iris: IrisEntry) -> IrisArea:
            return iris.calc_area()



One logical application of transformations on collections might be to provide parallization.

of this interface for transformation would be to add parellized code to the transformations on collections. For instance, 

        def calc_area(self) -> tuple:
            return IrisArea(self.sepal_area(), self.petal_area())



# 4. Add additional functionality through method-only classes that access the same data

Now I offer a solution to the situation where you need to add a large number of methods to your data objects. Instead of attaching all methods to the data object itself or creating a new base class from which the data object inherits, you can create an additional object definition with the relevant methods that operate on the original data object, and, ideally, _only_ on that data object. You can then call those methods on a temporary instance of the child object created through a method of the original data object.

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

This solution works quite fine. However, it may be convenient to access these methods directly from the Irises object. Because teh `PyPlotter` object contains only the irises data, we can create a method to return the plotter on which we can then call the plotting methods. In python, we can use the `property` decorator that will call a function merely by accessing an attribute of the same name. 

        ...
        @property
        def plot(self):
            return PyPlotter(self)

This method simply calls the default constructor of the plot class. Now we can access these methods as attributes of the `plot` property.

    irises.plot.sepal_scatter()

While there is some performance cost to this approach, the organizational benefit may be substantial enough to be worth it.

## More Complicated Method Classes

There may be cases where you want to similarly extend the data object in a way that changes the format of the original data without transforming it in any substantive way. In cases when that format change is expensive, you can follow a formula that is similar to the above, but do the transformation in a factory method of the child class which is called from a method of the data class.

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


# 5. Also keep objects for missing data

My final recommendation here is to keep track of missing data throughout your pipeline rather than filtering it in intermediary steps. As with any software engineering project, the questions you ask using your data will change along with the assumptions you make to answer them. For that reason, I recommend refraining from filtering missing data at any point in your pipeline - instead, create objects that store the missing data just as you would with non-missing data, and build methods to check for the missing data.

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





# ----------------------- 
methods have something in common - they all produce visualization.

Logically, it might clutter things up to add plotting methods


The next recommendation is that you create additional classes that contain the original data object to add additional methods once you require a large number of them. Ideally your code would be organized in a way such that you do not end up with classes with a large number of methods, but this can be a consequence of my first principle - that is, methods that operate on a particular piece of data (and only that data) should appear in the data object. To make your code more modular, I recommend


Now lets say you want to add additional features to the original data object but don't necessarily want to create a large number of new methods on the same class. This challenge is more organizational than necessary, as these methods could easily be added 


# ------------------------------------------------ (old stuff)




## The problem with implicit data structures

My students (and a younger me) often argue that building in more structure is tedious and unnessecary given the power of data frames and other collection types. Why create objects when you can just apply a series of operations on a dataframe? While it is true that using simple dataframes is faster - and still, perhaps, appropriate for demonstrations or quick analyses, I have decided over the years that this additional overhead is probably worth it as projects evolve and requirements start to change. I will now go through 



For illustration, I created a simpler diagram with two linear data pipelines depicting the transformation of the input data into an intermediate data structure which is changed into the final data to be shared with the customer (a table or figure, let's say). As I noted earlier, almost every part of your data analysis pipeline will look something like this. In the top example, we do not keep track of the structure of the input or intermediate data in our code explicitly, wheras in the bottom pipeline we represent them as objects A, B, and C. The idea is that pipelines with explicit references to data structure in the code make it easier to understand what each transformation is doing - in theory, we (and the static analyzer in your IDE) could understand the entire pipeline without ever running our code.

![data science pipeline overview](https://storage.googleapis.com/public_data_09324832787/pipeline_structures.png)

As a hypothetical, let's say you are seeing a potential issue in your final data structure - a figure, let's say - and you want to investigate why you observe a given value. First you hypothesize that the issue may have been with function/script 2, and so we first need to understand the structure of the intermediary data which it transformed. There are three approaches to understanding the intermediate data structure when we have not been explicit in our code: 

1. remember the structure of that data - generally a terrible idea in software design because you may be looking at this years later or someone else may be looking at it;

2. run the first pipeline component and use some runtime introspection tool (breakpoints, print statements, debuggers, etc) to look at the data - possible but clunky and time-consuming; or 

3. do some mental bookkeeping to trace the original input data (which may also require introspection) through the pipeline - also a time-consuming activity. If, however, you had built explicit object definitions into your code, you would know the structure of the data exactly without looking at the code used to generate it. Thus, it separates the logic of your operations from the structure of your data.

Instead, I recommend creating objects to represent atomic or higher-order pieces of data that you ingest as a starting point. As an exampl, use 

For example, if you read in a csv file as a dataframe, consider creating a class definition that represents a single row of that dataframe and include the code to parse that data within the same class. While json data may be more heirarchical, there are almost always equivalent data units at various levels - you can create a data structure for each level. Using this approach, you can know the structure of your data at any point in your pipeline and your IDE's static analyzer can identify any downstream issues that arise from a change in that data structure. This can be an invaluable tool for 

### Case Against Dataframes
While dataframes are important data structures that a large suite of languages and packages have been built around, I have two primary concerns about using them as a central feature of your data pipelines: (1) all of the problems we observe above, and (2) they are often the wrong tools for the job (performance-wise) - even though they may be fine for many tasks involving small datasets.

The first point appears to be acceptable for many data scientists given that it is common to use Jupyter or R Markdown notebooks to write large portions of code. Except in initial development or in your toplevel scripts, I recommend using project file structures that are recommended for your language of choice - in Python, this means separating functions and classes (including the data containers) into modules, but there are equivalent recommended project structures for most langauges. Data science projects in particular tend to grow in scope or change in structure often, so modular project structures are especially important. The more complex your code becomes, the more important this is.

More concretely, lets refer to the iris example dataset we loaded. We access a column of that data using a subscript or as a property of the dataframe (although be careful with the latter):

    iris_df['species']
    iris_df.species

Or, similarly in R:

    iris_df[:,'species']
    iris_df$species

The problem with this is that you have no gaurantees that this property exists with this name in your input data. Even though the R and Python versions are both written as if the columns are object properties, they are not - they are simply syntactic sugar used to make it feel like they are - the reader, and your static analyzer, cannot gaurantee they exist except in runtime.

Sure, you could run a verification or transformation function that selects/orders columns and does some validation, but this code is implemented as part of the script loading the data, not in the definition of the data itself.

    iris_df = iris_df[['sepal_length', 'sepal_width', 'species']]
    assert((iris_df['sepal_length']>0).sum() == iris_df.shape[0])

In short, you have no gaurantees that a property will exist in runtime (assuming, as in the case of weakly typed languages, you follow the hints/gaurantees that you yourself provided).

I a also caution against using dataframes for performance reasons. Traditional data structures like `set`s, `dict`s (any kind of map), or `list`s (arrays) in Python all have implementations that are akin to different tasks. If you want to store an unordered set of unique elements, use a `set` object. If you want to perform lookups from a string or other hashable object to another object directly (i.e. in O(1) time), use a `dict`. If you want to store an ordered sequence of elements that can be indexed by their order in the sequence, use a `list`.

As an example of this issue, lets say that you want to perform a join on a two unindexed dataframes A with `n` rows and B with `m` rows that have a many-to-one relationship: that is there are zero or more rows of A that correspond to a single row of B. Because dataframe columns are implemented as sequential elements, the time it will take for this join to complete will be proportional to `n*m`: you would iterate through every element of A to find the associated row in B (note that this is worst case: `O(n*m)`). This is the wrong tool for the job because it could be done faster with a dictionary or hash map that allows you to look up the associated row in dataframe B instantly, so the time would be proportional to `n` (even if you have to create the dictionary first, you end up with `n + m ~ O(n)`).

Note that indexing dataframes is an operation that would allow for faster joins (typically through binary search, which is `O(n*log(m))`), indexing and multiindexing implementations are somewhat clunky to use and often involve explicit indexing between transformations. It is worth noting they exist, though I don't often see them used.

Dataframes can also be more memory intensive because joins and most other operations often create copies of data - even when it may be unnessecary. Be wary of this as your dataset gets larger.

As an alternative, I recommend creating an object to represent each row of your dataset, and parsing each row using a factory method - I will give some examples later.

### Nested Iterables are Also Bad

It may also be tempting to use raw nested iterables like `set`s, `dict`s, or `list`s either because they follow directly from the structure of the input data (especially json data) or because they solve the second issue I have with dataframes - you can use the right tool for the job. My main concern with these structures is that they can get very complicated with high levels of nesting and requre missing data/error handling at every point of usage.

As another example, let us consider a json dataset parsed as a list of dictionaries with properties associated with irises. The type hint for the parsed structure would be `typing.List[typing.Dict[str, typing.Union[float, str]]]`.

    [
        {
            "sepal_length": 5.1, 
            "sepal_width": 3.5, 
            "species": "setosa"
        }, 
        {
            "sepal_length": 4.9, 
            "sepal_width": 3.0, 
            "species": "setosa"
        },
        ...
    ]

Sqy we want to get the average petal length for irises in our dataset, so we do this:

    import statistics
    statistics.mean([iris['petal_length'] for iris in irises])

The problem here is the same as that of selecting columns in dataframes: we have no gaurantees that each iris will include a member called 'petal_length' until runtime. We can't know it exists unless we recall the data being passed in, and static analysis tools cannot help us.

The solution to these problems would again be to create a class representing a single Iris object and parsing them into a list of these objects. Even better, we could encapsulate the sequence of irises to add additional convenience. I will show some examples in the next sections.

## How to make explicit data structures

Creating an explicit object definition for your data will provide built-in validation because you are making gaurantees for what your data will look like and how you will access its attributes downstream. Consistent with broader motivations for using OOP, you could build out your entire data pipeline beginning-to-end with just the knowledge of the properties of the data you will be using - it can be agnostic to the structure of the data you take as input. You could even build downstream components of your pipeline before writing upstream - an approach that requires dicipline but ensures you have the appropriate data needed for each step of the procress. Similarly, explicit data definitions could also make things easier to test because you can write tests using synthetic data or even generate random data for Monte Carlo simulations. This way, your IDE's static analyzer can take advantage of intellisense or other autocomplete tools to help you code faster and with many errors caught prior to even running your code.

More concretely, I recommend creating data encapsulation classes that (1) use factory methods for class creation instead of constructors; (2) are immutable, or cannot be changed after creation; (3) include some level of data validation. In the following sections I will be drawing on [the examples in this notebook](/example_code/zen_of_data_science/zen_of_data_science1.html) for illustration.

[Class factory methods](https://realpython.com/factory-method-python/) can be used to handle the mappings between your source data (e.g. json or csv formatted data) and the object instances. [Among other benefits](https://web.archive.org/web/20210130220433/http://as.ynchrono.us/2014/12/asynchronous-object-initialization.html), they are especially convenient in cases where your input data may come from multiple source formats. For instance, say your input data is split into two files with different formats but essentially correspond to the same type of data elements. You could create two separate factory methods - one to handle each. This also makes it possible to create your classes immutable. This approach follows a principle from the [Zen of Python](https://peps.python.org/pep-0020/): "in the face of ambiguity, refuse the temptation to guess."

To make these points clearer, I will make an example out of the iris dataset we have been looking at so far. [Dataclasses](https://realpython.com/python-data-classes/) have been extremely popular lately as they provide convenient ways to create classes meant for storing data. The example below shows my example dataclass with three properties and two class factory methods - one for creating the object from a dictionary, and one for creating the object from a dataframe row.

    import dataclasses

    @dataclasses.dataclass(frozen=True)
    class IrisEntryDataclass:
        sepal_length: int
        sepal_width: int
        species: str
        
        # factory method constructor
        @classmethod
        def from_dataframe_row(cls, row: pd.Series):
            new_obj: cls = cls(
                sepal_length = row['sepal_length'],
                sepal_width = row['sepal_width'],
                species = row['species'],
            )
            return new_obj
        
        @classmethod
        def from_dict(cls, data: dict):
            new_obj: cls = cls(
                sepal_length = data['sepal_length'],
                sepal_width = data['sepal_width'],
                species = data['species'],
            )
            return new_obj

We can simply iterate through each row of the dataframe and use the factory method to convert the dataframe rows to these dataclasses.

    entries = list()
    for ind, row in iris_df.iterrows():
        new_iris = IrisEntryDataclass.from_dataframe_row(row)
        entries.append(new_iris)

Alternatively we could create the objects from the parsed json data we showed in the previous example about nested iterables. This line of code produces the exact same result.

    iris_dict = iris_df.to_dict(orient='records')
    entries = [IrisEntryDataclass.from_dataframe_row(d) for d in iris_dict]

    entries[:3]

Output:

    [IrisEntryDataclass(sepal_length=5.1, sepal_width=3.5, species='setosa'),
    IrisEntryDataclass(sepal_length=4.9, sepal_width=3.0, species='setosa'),
    IrisEntryDataclass(sepal_length=4.7, sepal_width=3.2, species='setosa')]

The advantage is that Python and our static analyzers providing autocomplete and error analysis know that these are all valid properties of the object. If we ran this code:

    entries[0].some_property

Our IDE would give us a warning that objects of type `IrisEntryDataclass` have no property called `some_property`, and we cannot assign a value to it because we used `frozen=True` - our class is immutable. This provides strict enforcement of our data format - we know for sure that each instance of this class will have exactly the specified properties, and no more. If we have a function that accepts a list of `IrisEntryDataclass` objects, we (and our IDE) know exactly which properties are available to us.

## Consider using `attrs`

While dataclasses are useful, I recommend going a step further by using `attrs` to include explicit data validation. The [attrs package](https://www.attrs.org/en/stable/overview.html) provides some convenient methods for creating classes meant for storing data, so that may be preferable in many cases. Note: `attrs` [provides a superset of the features found in `dataclasses`](https://www.attrs.org/en/stable/why.html#data-classes) because it acted partially as their inspiration for inclusion in the standard library. 

### See: [`Example Notebook`](/example_code/zen_of_data_science/zen_of_data_science1.html)

I will not include my implementation of the `attrs` version of the same class, but instead direct you to Example 2 of my [example notebook](/example_code/zen_of_data_science/zen_of_data_science1.html). In that class I use the `frozen=True` and `slots=True` settings to make sure the object is immutable (cannot be changed) and uses slots (see [this explanation](https://www.geeksforgeeks.org/python-use-of-__slots__/)), which reduces memory usage and prevents the user from creating attributes later on.

I implemented validation using several methods. I used the `converter` parameter of `attrs.field()` to enforce data conversion - in addition to throwing errors for non-convertable types, this can prevent your code from being sensitive to the way that the data was ingested (e.g. whether pandas converted a column to a string). I also added two data validation methods using decorators recognized by `attrs`: `species_validator` and `meas_validator`; these define the criteria of the data being inserted upon instantiation. Note that because I did not use the `default` parameter in `attrs.field`, all of this data must be provided during instantiation. This is my class definition:

This class provides gaurantees about the structure of your data - if your class method constructor runs without errors, you know that your data structure will have the required data early in your pipeline. Furthermore, all validation and data structuring is done as part of the object - you won't need to write an additional validation script to verify that the data meets some assumed criteria. Multiple methods for producing the same dataset can be implemented in the same class. In this way, all checks and gaurantees about your data exists in this single class. If you want to change assumptions or structure of the data, it will appear here.

## Wrap collections

I also recommend using class objects for higher-order data structures composed of multiple pieces of data or even data in different formats. While this can be dangerous in general, in certain select scenarios I recommend creating collections classes that inherit directly from builtin iterable types. This can eliminate a lot of the boilerplate `__iter__`, `__getitem__`, and `__len__` code that we often need when encapsulating iterables, and also allows us to wrap factory constructor methods that produce multiple data objects - see the factory method `from_dataframe` here. I also implemented a couple useful functions for working with lists of this specific data type. Functions for grouping and filtering these objects also fit better here than in downstream consumers.


    class IrisEntriesList(typing.List[IrisEntryAttrs]):
        
        ######################### Factory Methods #########################
        @classmethod
        def from_dataframe(cls, df: pd.DataFrame):
            # add type hint by hinting at returned variable
            elist = [IrisEntryAttrs.from_dataframe_row(row) for ind,row in df.iterrows()]
            new_entries: cls = cls(elist)
            return new_entries
            
        ######################### Grouping and Filtering #########################
        def group_by_species(self) -> typing.Dict[str, IrisEntriesList]:
            groups = dict()
            for e in self:
                groups.setdefault(e.species, self.__class__())
                groups[e.species].append(e)
            return groups

        def filter_sepal_area(self, sepal_area: float):
            elist = [e for e in self if e.sepal_area() >= sepal_area]
            entries: self.__class__ = self.__class__(elist)
            return entries

By always using factory methods here to create the sequence of IrisEntries, we are creating further gaurantees for the structure of the data inside these objects. You could accomplish the same thing by inheriting through composition - and indeed in many cases this is safer - but direct iterable inheritance is better than nothing, in my opinion.

In my experience, adding more structure to your data pipelines - at least where the actual data is concerned - can improve the quality of your code and the speed with which you produce results, even if it requires more time and dicipline up-front. While speed is important in producing results, nothing is more important than getting the analysis right.

# 2. Version almost everything

My next recommendation is related to managing projects. A key challenge in project management is keeping track of different intermediary data products and the code used to generate them. It is typical to be in a scenario where, halfway through building a data pipeline, your requirements change or you produce results that encourage you to take a different approach to analysis. In that case, you don't want to delete the old intermediary results because you may want to refer back to them later. Or, worse yet, you shared them with a client and may need to refer back to them for their sake. Either way, you also want to keep track of the code you used to create those files, in case you get any questions about it or are simply curious. It is in this scenario that I recommend that you retain multiple class definitions for the same type of object and keep track using naming conventions. Then, when you go to look closer at a result you generated previously, you can easily track the code you used to generate it. 

It might be worth thinking more about typical data science workflows to get a sense of why this might make sense. First, lets take a look at the following figure.

![data science pipeline overview](https://storage.googleapis.com/public_data_09324832787/ds_pipeline_workflow.svg)

At the top of this figure we see the original dataset, composed of one csv file and one json file. Each of the scripts that appear here involve some type of transformation from one data type to another. Script 1 takes the original csv data and converts it into a new Intermediate csv file. Script 3 takes the orignal csv file, the original json file, and the intermediate csv file generated by Script 1, and converts it into Final table csv file. Script 4 then converts this table into a visualization that will be presented to the client. Note that on the right we also see that Script 2 converts the original json data to Some figure png file - possibly for another analysis.

In an ideal world, we work on and finish Script 1, then work on and finish Script 2, and so on until we finish coding and can produce the final data from the original data. In a more practical scenario, most likely will need to go back and fix some upstream script to add or edit some information according to requirement changes or just changing realization of the information needed to produce intermediary results. When we do this, however, it doesn't always make sense to delete data that was previously generated - either so we can use it as reference or present it as intermediary results to the client. In these cases, it makes the most sense to keep track of the data and the code that was used to generate it through an informal versioning system of your design.

For an object-oriented example, let's assume that the client gives you data in the format represented by the class `IrisA`.

    @dataclasses.dataclass
    class IrisA:
        sepal_length: int
        sepal_width: int
        species: str

You write a script that converts `IrisA` data to `IrisB` data using its class method constructor `from_a`, and you saved the result as `resultB.csv`. This result will be used later on by another script to produce the final figure. Lets say you produce the final figure and call it `finalB.png`, then share it with your client as intermediate results. See my example class below.

    @dataclasses.dataclass
    class IrisB:
        sepal_area: float
        
        @classmethod
        def from_a(cls, a: IrisA):
            return cls(sepal_area = a.sepal_length * a.sepal_width)

The client has some suggested improvements, and you realize you need one additional piece of information from the `IrisA` dataset to be included in `IrisB`: the `species`. So you go back and edit `IrisB` to include this information. You use this dataset to produce the final result `finalB2.png`, and share with the client. 

    @dataclasses.dataclass
    class IrisB:
        sepal_area: float
        species: str
        
        @classmethod
        def from_a(cls, a: IrisA):
            return cls(sepal_area = a.sepal_length * a.sepal_width, species=a.species)


The client asks about a discrepency between `finalB.png` and `finalB2.png` - can you answer their question? You could go back to the correct commit based on datetimes, but that might be a little tricky if the file timestamp was changed after copying/etc. Instead, I recommend creating a versioning system that is consistent between the names of your data objects and the intermediate data files they were used to generate.

    @dataclasses.dataclass
    class IrisB_v1:
        sepal_area: float
        
        @classmethod
        def from_a(cls, a: IrisA):
            return cls(sepal_area = a.sepal_length * a.sepal_width)

    @dataclasses.dataclass
    class IrisB_v2:
        sepal_area: float
        species: str
        
        @classmethod
        def from_a(cls, a: IrisA):
            return cls(sepal_area = a.sepal_length * a.sepal_width, species=a.species)

When you save the files, you could integrate the name of the class into the filename. For instance, you could call them `result_IrisB_v1.csv` and `result_IrisB_v2.csv`, which you could then translate to a final figure names like `final_result_IrisB_v1.png` `final_result_IrisB_v2.png`. This is what it might look like:

    a = IrisA(1.0, 2.0, 'big')
    
    b1 = IrisB_v1.from_a(a)
    save(b1, f'result_{b1.__class__}.csv')

    b2 = IrisB_v2.from_a(a)
    save(b2, f'result_{b2.__class__}.csv')

Of course every case is unique and I don't recommend using this everywhere, but I have found it to be useful in scenarios where I am getting a lot of client feedback and I need to refer to old code when I'm trying to explain differences between results figures or intermediate data.

# 3. Create parameter or settings objects that live in your code

Building off of the previous two examples, I recommend creating parameter objects that you can use to keep track of results created with different parameters. This essentially follows from the previous two examples, but further introduces the possibility that you may generate results from many different parameter sets over the lifetime of your project. Ideally the defined parameter set will be used at every step of your data pipeline to make it perfectly reproducable. Lets see the example below.

Start by creating a dataclass to contain parameter information. This defines all the variables that will be used to generate results throughout your data pipeline. It might be helpful to have some `version_name` member to make it easy to get the version as a string. This even includes a parameter that accepts a type - this will allow you to control which version of a class is being used throughout your pipeline. This may be overkill, but you can imagine projects that are of sufficient complexity as to benefit to this level of detail.

    @dataclasses.dataclass
    class Params:
        version_name: str
        IrisB: type
        intermediate_fname: str
        final_fname: str

Now I recommend creating functions or module-level variables for param object instances, including the version number as part of the object name. Here I have two params objecs, which I named `0x1` and `0x2`.

    def params_0x1() -> Params:
        return Params(
            version_name = '0x1',
            IrisB = IrisB_v1,
            intermediate_fname = 'intermediate_0x1.csv',
            final_fname = 'final_0x1.csv',
        )
        
    def params_0x2() -> Params:
        return Params(
            version_name = '0x2',
            IrisB = IrisB_v2,
            intermediate_fname = 'intermediate_0x2.csv',
            final_fname = 'final_0x2.csv',
        )

So at the beginning of each script you can instantiate a params object and use it at various points.

    params = params_0x1()
    a = IrisA(1.0, 2.0, 'big')
    b = params.IrisB.from_a(a)
    save(b, f'result_{params.version_name}.csv')

This approach may be overkill in some scenarios, but if the project gets large enough it is an option you may want to consider.


# 4. Make I/O explicit in your top-level scripts

This principle is very simple: make it such the user can see save and read functions at the top level of your script (even if the filenames are hidden). It should be clear to the reader that the script is ingesting one or more datasets and exporting others. Adding this to your script can save you a lot of time later when you try to determine which types of data this script makes and outputs.

    df = pd.read_csv('test.csv')
    new_data = myfunc(df)
    new_data.save_json('new_data.json')

This can still be consistent with previous recommendations as long as you access filename properties at the top level of your script. In this example, the filenames are stored as members of the `params` object.

    params = params_0x1()
    df = pd.read_csv(params.test_csv_fname)
    new_data = myfunc(df)
    new_data.save_json(params.output_json_fname)


# 5. Include validation when possible

Validation has the potential to drastically increase your speed as an analyst because it allows you to build assumptions about your data into your production pipeline directly. As you begin to build your pipeline, you will start to ask questions about your dataset that you can typically answer through exploratory analysis. This requires overhead, however, because you must move back-and-forth between the exploratory analysis and the pipeline code. Furthermore, if your data changes or you add additional data, you need to remember to re-run your exploratory analysis code and verify that the same assumptions hold. Instead, I recommend that you make assumptions as you build your pipeline and integrate them as part of your production code (to be disabled later if needed). You can always change these assumptions as you learn more about your data, but I have found that it is best to implement them early in development.

I typically recommend implementing validation as far upstream as possible - ideally when the data is ingested into an object - often this means within constructors or factory methods. When possible, this is easier than validating results downstream after some transformations have happened. For instance, it would be better to validate that an age value is greater or equal to zero within a class constructor than it is to check every value before calculating an average. Also consider inserting validation code during the exploratory phase of your analysis, when you are implicitly validating assumptions anyways.

Of course, validation is also helpful for detecting issues in your code. While unit tests tend to be a gold standard, you may not have the time or desire to implement a full-featured test suite. In lew of that, I at least recommend you include exceptions or assertions at various points in your pipeline - especially when they are obvious or come before a portion of code that might be particularly difficult to debug if your assumptions do not hold.

## Validation in Python

In Python, there are generally two options for including validation in your production pipeline: assertions and exceptions. Use assertions when you want a full-stop on your program if an assumption does not hold. You may want to use assertions if there is a major error upstream that will cause any subsequent results to be nonsense. In this case you will likely need to go back into full development mode to fix the issues that arose before you can begin to run anything. Assertions may also be the best option if you are lazy. Alternatively, if there are cases in which you may want to ignore particular assumptions (at least momentarily), you can raise exceptions when an assumption in your data does not hold. It is generally best to create custom exceptions to handle these issues so that when you go to ignore or do some logic based on the error, you are catching the correct issue.

In Python you will ideally create custom exceptions for your applications - a process which is easier than you might think. Now I will illustrate how you can use exceptions using an example class called `Person` created using `attrs` with some validator functions. The object has two properties: `age` and `full_name`. There are several things that can be wrong with a `Person` entry, so we will later add validators with custom exceptions to indicate which aspect of the data is wrong. We start by making the custom exceptions. First, the most obvious issue would be that the `age` is too high or below zero - the entry is obviously wrong if that is the case. So, we make a custom exception that inherits from `ValueError` (we could also inherit from `BaseException`, but this has some utility).

    class PersonAgeOutOfRangeError(ValueError):
        pass

Next we want to raise an exception if there is an issue with the `full_name` of the `Person`. This is an interesting case because two things can be wrong: `full_name` can be an empty string or it can only include a single word when at least two words are needed to make a full name (at least in most of the Americas). Because they are both issues with the name, we can start by making an exception `PersonNameEror` to be raised when the name is out of range. But we can also improve granularity of this exception by indicating whether the issue was that the name string was empty or whether they only had one name. For that, we create two additional exceptions - one for empty name, and the other for a last name error.

    class PersonNameEror(ValueError):
        pass

    class PersonNameWasEmptyError(PersonNameEror):
        pass

    class PersonFirstLastNameError(PersonNameEror):
        pass

Now we can define the `Person` class with validation functions using `attrs`. Notice that `validate_age` and `validate_name` are both added to the `__init__` constructor generated by the `attr.s` decorator.

    @attr.s
    class Person:
        age: int = attrs.field(converter=float)
        full_name: int = attrs.field(converter=str)
        
        @age.validator
        def validate_age(self, attr, value):
            if value < 0 or value > 150:
                raise PersonAgeOutOfRangeError(f'{attr.name} must be between '
                    f'0 and 150')
        
        @full_name.validator
        def validate_name(self, attr, full_name: str):
            if not len(full_name):
                raise PersonNameWasEmptyError(f'{attr.name} cannot '
                    f'be empty string.')
            
            elif not len(full_name.split()) > 1:
                raise PersonFirstLastNameError(f'{attr.name} requires '
                    f'first and last names.')

Instantiating this object is simple. When we create this person, we get no errors.

    Person(age=10, full_name='yo holla')

However, we do get an error when we provide an incorrect age:

    Person(age=-1, full_name='jose dillan')

Exception raised:

    __main__.PersonAgeOutOfRangeError: age must be between 0 and 150

Now try making a person with a single name:
    
    Person(age=10, full_name='Jose')

Exception raised:

    __main__.PersonFirstLastNameError: full_name requires first and last names.

This is great - if these assumptions are violated, we will see an error in our code and we can decide how to handle it. Hypothetically, let's say you received full names and ages of some individuals from a survey. As we know, survey data is messy; in this case, some respondents did not provide their full names, but we need the full names for our analysis. In this case, we still want to make assumptions about age and name cannot be an empty string - the program should fail if those are violated. We would, however, simply like to drop the entries where the full name was not provided. To do this, we can use `try` and `catch` keywords to implement exception handling.

We start with a dataset that looks like this:

    person_data = [
        {'age': 22, 'name': 'jose rodriguez'},
        {'age': 5, 'name': 'johnny'},
        {'age': 30, 'name': 'carol carn'},
        {'age': 55, 'name': 'david duke'},
    ]

And we want to make a list of `Person` objects from this dataset. To do this, we can wrap the person constructor in a `try` statement and choose to ignore the case when the `PersonFirstLastNameError` exception was raised. In this way, entries that don't have first and last names are dropped from the list and will not be included in the dataset. The program will still crash if one of the other two exceptions was raised, however. Using this technique, we can choose to ignore entries with one type of error while still retaining the other two assumptions.
    
    people = list()
    num_invalid = 0
    for d in person_data:
        try:
            people.append(Person(age=d['age'], full_name=d['name']))
        except PersonFirstLastNameError:
            num_invalid += 1

If, however, we wanted to ignore persons with any type of name issue, we can either catch multiple exceptions or use the more generic exception `PersonNameEror`. Here we catch any exception which is a subclass of `PersonNameEror`.

    try:
        Person(age=pd['age'], full_name=pd['name'])
    except PersonNameEror:
        pass

We can also capture multiple exceptions at once - useful if you want to integrate more validation checks in the future but do not necessarily want to drop those rows.

    try:
        Person(age=d['age'], full_name=d['name'])
    except (PersonFirstLastNameError, PersonNameWasEmptyError):
        pass

If, however, you want to relax any of the validation functions so they don't raise exceptions, you'll need to update your validation logic.

Including validation for assumptions about the data and pipeline can add additional gaurantees about your data that will be useful later. Through use of exceptions and assertions in validators, you will know that every instance of your object will maintain a set of characteristics that your analyses are predicated on - and, as the analyst, you can make intentional calls about which errors to ignore and how to handle errors that do arise.





