---
title: "Are dataframes too flexible? Optimal data structures for data pipelines."
subtitle: "The challenges with implicit data structures."
date: "May 28, 2023"
id: "zods2_problem_with_dataframes"
---

Dataframe interfaces are useful because they are so flexible: filtering, mutatating, selecting, and grouping functions have simple interfaces and can be chained to perform a wide range of transformations on tabular data. The cost of this flexibility, I argue, is that your data pipelines are less readable, more difficult to maintain, and more error prone. Instead, I argue that it is better to use more explicit data structures like classes or structs with fixed attributes, specific methods for construction, and defined methods for transformation/analysis. 

Over the last decade of teaching and reading about data science practices, I have seen a shift in the way that students are learning. Students start learning with tools like Jupyter and RStudio markdown because they allow for quick experimentation on a step-by-step basis and enable trying new things with near-instant feedback. Expansive packages like Pandas and tidyverse are becoming essential material, and students often engage with them before they even understand the language they are built in (me too, sometimes). There is no doubt that these are learning powerful tools, but my concern is that we are sacraficing fundamentals of programming that are essential for building real-world projects that are maintainable. Anyone can learn to write code, but, in my opinion, we should be teaching how to write _good_ code from the start.

In this article, I will describe what I mean by data structures within the context of data pipelines, the essential form of any data analysis project, in order to discuss optimal patterns on a theoretical level. Next, I will discuss three patterns for creating data pipelines in Python, although I believe the examples here apply to many languages - especially interpreted ones.

I believe that using custom data types, rather than dataframes or other less-explicit schemes, can make pipelines easier to understand, easier to maintain, and less error-prone.


## Data Structures and Pipelines

A _data pipeline_ is a series of sequential steps for changing data from one format to another - the essential core of all data science projects. Maybe you want to visualize some variables from a CSV file in a 2-dimensional plot, produce a statistical model to capture trends of Tweets in json format, or even build a classifier to identify cats from an image training data set. In each of these cases, the data pipeline simply describes the set of transformations and intermediary representations needed to produce the final form from the given input data.

I use the term _data structures_ to describe the intermediary representations of data in these pipelines. Essentially, this means the format in which your data is represented in your computer system and the interface (API) in your code used to access and manipulate it. Any [computer science cirriculum](https://ocw.mit.edu/courses/6-851-advanced-data-structures-spring-2012/) includes an analysis of common data structures and optimal algorithms for manipulating and analyzing them, but they play what is perhaps a more important role in software engineering of data pipelines: they can be used to make your data pipelines easier to understand, less error-prone, and more efficient to maintain.


<div id="illustration">.</div>

### Illustration of Data Pipeline

Below I created a simple diagram with two linear data pipelines depicting the transformation of the input data into an intermediate data structure which is changed into the final data to be shared with the customer (a table or figure, let's say). 

![data science pipeline overview](https://storage.googleapis.com/public_data_09324832787/pipeline_structures.png)

Anything represented in the computer is a data structure. For instance, the input could be a CSV file that you first read as a dataframe (intermediate data structure), average a set of values to produce another dataframe (another intermediate structure), and then convert to a figure which you then display on your screen (the final data structure). Or, for instance, the input could be a set of images and classification labels and the output could be a machine learning model trained to identify the classes. In this way, the pipeline captures the essence of any data analysis project. 


<div id="features">.</div>

### Features of Data Structures

I will focus on three aspects of data structures which are relevant for design patterns I will discuss. They exist in almost every type of data structure, and the key is in where and how they appear in your code.

1. **Properties or attributes.** Data structures often include sets of properties, attributes, or features that are associated with a single element - the "what" of your data pipelines. These might be represented as columns in dataframes where each row is an element, attributes in custom types, or as separate variables. They can be defined at instantiation (point where the structures are created) or later added, modified, or removed throughout your pipeline. The data is called _immutable_ if it cannot be changed, and _mutable_ otherwise. 

2. **Construction methods.** Functions used to create and instantiate data structures are called construction methods. These functions are critical because they include at least some, if not all, information about which data will be contained within the structure. As such, the function signature should tell the reader (and compiler or static analyzer) a lot about what type of data is being represented. These methods can appear in your code as class methods, functions, or entire scripts. As an example, they may include the code used to parse json or csv data into a data object.

3. **Transformation methods.** These are the methods which actually convert your data structures from one form to the next - the "how" of your data pipelines. They may appear in your code as class methods, functions, or entire scripts. Common transformations might include filtering, summarizing, or normalizing your data. This is a more general case than construction methods, which could also be considered as transformation methods.

Next I will use these three features as comparison points.

<div id="attributes">.</div>

## Comparison of Data Structures

I will now compare dataframes with other data structures using Python examples, although I believe these points apply to many different languages. Specifically I will use the classic Iris datasets loaded from the seaborn package.

In Python, we would load the Iris dataset as a dataframe using the following code (note that seaborn is only used to load the data).

    import seaborn
    import pandas as pd

    iris_df = seaborn.load_dataset("iris")
    iris_df.head()

The dataframe looks like this.

    sepal_length  sepal_width  petal_length  petal_width species
    0           5.1          3.5           1.4          0.2  setosa
    1           4.9          3.0           1.4          0.2  setosa
    2           4.7          3.2           1.3          0.2  setosa
    3           4.6          3.1           1.5          0.2  setosa
    4           5.0          3.6           1.4          0.2  setosa

However, for illustrative purposes, I convert this dataframe to a list of dict objects.

    iris_data = iris_df.to_dict(orient='records')

The first few elements of this data looks like the following:

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
        },
        ...
    ]


### 1. Properties or Attributes of Data Structures

#### The dataframe approach

Dataframes typically represent data attrbutes as columns, and each column is represented as an array of an internal type, rather than a type within the langauge. Python, for instance, implements int and float objects, but Pandas dataframes include more specific types like 64 bit integers and floating point numbers (following Numpy arrays) that do not appear in the Python specification.

In Python, you would access columns using the following notation.

    iris_df['species']
    iris_df.species

And subsets of columns in Python can be extracted using the following.

    iris_df = iris_df[['sepal_length', 'sepal_width', 'species']]


#### Combine the following two paragraphs
The major downside here is that  the existence of a dataframe object alone does not gaurantee that it will include columns with these exact names. If the dataframe is loaded directly from disk (or the seaborn package, for instance), the structure of that data is determined by the actual input. If a column is renamed in the file, the structure of the data will change and the code used to access the data may fail. You cannot know that the code will fail without looking at the input data itself. 

In a pipeline with a series of transformations, this becomes concerning becaue you cannot know if a column exists unless you know the input data and all subsequent transformations up until the point where you try to access it. While there may be tansformations that standardize the format of the data (i.e. select columns in a particular format) you must still know that this transformation occurred to construct the object. 

#### Custom type approach

As an alternative, consider using custom data object types with specified attributes to represent your data. While more code is needed to create the types, the mere existence of the object comes with gaurantees about which attributes they contain. You do not need to understand the transformation used to create the object to know that the attributes will exist.

In most languages, I recommend creating classes or struct types to represent you data. In Python, you can use dataclasses or the attrs package to easily create objects that are meant to store data. The following class represents a single Iris object.

    import dataclasses

    @dataclasses.dataclass
    class IrisEntry:
        sepal_length: float
        sepal_width: float
        petal_length: float
        petal_width: float
        species: str
        ...

The dataclasses module creates a constructor where all these values are required, so you may instantiate an IrisEntry like the following:

    IrisEntry(1.0, 1.0, 1.0, 1.0, 'best_species')

You can then store these objects in collection types, but I recommend either encapsulating those collections or at least extending an existing collection type to make the intent clearer to the reader - especially in weakly typed langauges. In Python, you might extend a List using the following.

    class Irises(typing.List[IrisEntry]):
        ...

The benefit of defining these types is that it should be obvious to any reader which properties are associated with witch types of data. If you try to access an attribute that does not exist, you will see an exception, and furthermore your static analyzer or IDE will be able to autocomplete or let you know when you make an error before you ever run your code. You are making a gaurantee that every time an object like this exists, it will have these attributes.

One final note here - in more weakly typed languages like Python or R, I recommend creating immutable types, or objects that cannot be modified or extended after construction. This restriction will make for cleaner methods/functions throughout your pipeline.

### 2. Constuction Methods

Construction methods are critical for understanding your data pipeline because they often reveal which data the structure will encapsulate and the oeprations needed to encapsulate it. 

Moving forward, we're going to be 
To demonstrate construction methods with dataframes, I'll simply show what it would be like to convert whatever.

For example purposes, lets try deconstructing the original iris dataframe into Python dictionaries and recreate a dataframe from there. First I'll use the `to_dict` method to create the list of dictionaries.

    iris_data = iris_df.to_dict(orient='records')

This data looks like the following:

    [
        {'sepal_length': 5.1,
        'sepal_width': 3.5,
        'petal_length': 1.4,
        'petal_width': 0.2,
        'species': 'setosa'},
        {'sepal_length': 4.9,
        'sepal_width': 3.0,
        'petal_length': 1.4,
        'petal_width': 0.2,
        'species': 'setosa'},
        {'sepal_length': 4.7,
        'sepal_width': 3.2,
        'petal_length': 1.3,
        'petal_width': 0.2,
        'species': 'setosa'},
        ...
    ]

And now let us create a function to convert this data from a list of dictionaries to a dataframe. We can do this easily using the `from_records` method, again demonstrating the flexibility and power of dataframe-oriented packages.

    def make_iris_dataframe(iris_data: typing.List[typing.Dict[str, typing.Union[float, str]]]) -> pd.DataFrame:
        return pd.DataFrame.from_records(iris_data)

The drawback of this design is that we do not know the structure of the output data without both knowing the input data and reading the entirety of the function to see how that input data relates to the output. 

Imagine you have a data pipeline where this function is the first step, and one day the data source changes the "species" attribute to be "type". This example function would not raise any exceptions or flags, but instead propogate this change further in your data pipeline such that you only know it would be broken when you try to access the column with the old name. When the downstream function raises an exception, you will not immediately know whether it was because the original dataset changed or if it was an error in that first function. 

The common solution to this small problem is to add a column selection that would fail if a column has been renamed, but again it requires us to know the content of the function and also remember to build these code lines into any function that makes the dataframe from any source data. 

    def make_iris_dataframe_standardize(iris_data: typing.List[typing.Dict[str, typing.Union[float, str]]]) -> pd.DataFrame:
        df = pd.DataFrame.from_records(iris_data)
        return df[['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']]


A principle of good design is that your system should fail as early in the pipeline as possible so that you can isolate any issues at the point of the failure rather than to downstream functions which rely on them.

Alternatively, you can consider using a static factory method (see the `classmethod` decorator in Python) to contain code needed to create the object from various sources. This example shows code needed to create a `IrisEntry` object from a single row of the iris dataframe.

    @dataclasses.dataclass
    class IrisEntry:
        sepal_length: float
        sepal_width: float
        petal_length: float
        petal_width: float
        species: str
        
        @classmethod
        def from_series(cls, row: pd.Series):
            return cls(
                sepal_length = row['sepal_length'],
                sepal_width = row['sepal_width'],
                petal_length = row['petal_length'],
                petal_width = row['petal_width'],
                species = row['species'],
            )

And the collection type could tie it together by calling the static factory method on each row of the dataframe.

    class Irises(typing.List[IrisEntry]):
        @classmethod
        def from_iris_df(cls, iris_df: pd.DataFrame):
            return cls([IrisEntry.from_series(row) for ind, row in iris_df.iterrows()])

One could imagine creating similar static factory methods for constructing this data structure from any type of input data - not just a dataframe.


#### VVVVVVVVVVV ALL EXPERIMENTAL VVVVVVVVVVV


They do not appear in your code except at the type of conversion or enforcement, or, even more sketchy. 

but my concern is that the types of individual columns are never known by your interpreter until you actually run the code. While you may specify and enforce column  

or contained elements are not known by your interpreter

by the reader or static analyzer prior to runtime. You can specify and enforce the types of columns in dataframes, but your interpreter or analyzer never actually



they are not probject-specific - that is, they do not enforce structures that are relevant to the specific project for which the pipeline is being built. When you read a dataframe from a csv file, for example, you can specify the code 

As such, simply knowing the type of an object does not give us insight into the representations that appear in the pipeline. 

Dataframes maintain types for the columns they maintain, however, you cannot see the types unless you do some introspection into the 



For a further elaboration on what I mean by adding more structure, see 


. As an example, if you read a csv file as a dataframe, consider creating a class definition that represents a single row of that dataframe and include the code to parse that data within the same class, as well as any methods that operate on that class' data. Then encapsulate those objects into collections in which you can build additional methods for parsing, grouping, filtering, or transforming collections/lists/etc. By defining classes explicitly, your analyzer knows which attributes and methods are available on that object at any point in time. Avoid using lists of dictionaries or other datastructures without defined types, as they have the same pitfalls as dataframes.


#### ^^^^^^^^^^^^^^^^^


Hiiiii^[Note that dataframes themselves are types and their columns have specific types within those objects, but the defining characteristic is that the interpreter or analyzer cannot infer those types without looking at the behavior of the functions or scripts used to produce it (which they often do not). They are types within the underlying package code, but they are not considered as types within the language itself. If you build your pipelines using functions that both accept and return dataframes, you do not know the structure of the new dataframe unless you look at the code used to transform it. In contrast, if you define custom types for the input and output data, you can know without looking at the]

#### ^^^^^^^^^^^^^^^^^

## Data pipelines: separating the "what" from the "how"

The topmost path in the figure shows the case where we do not keep track of the structure of the input or intermediate data in our code explicitly (imagine using a list of dictionaries or a dataframe read from a csv file), wheras in the bottom pipeline we represent them as objects A, B, and C explicitly in our code. The idea is that pipelines with explicit references to data structure in the code make it easier to understand what each transformation is doing - in theory, we (and the static analyzer in your IDE) could understand the entire pipeline without ever _running_ our code.

#### ^^^^^^^^^^^^^^^^^^^ 


## Debugging Pipelines

Let us explore the case where you do not use custom data objects, and instead use dataframes or lists of dictionary/collections, or some other non-explicit data structures. As a hypothetical, say you are seeing a potential issue in your final data structure - a figure, let's say - and you want to investigate why you observe a given value. First, you hypothesize that the issue may have been with function/script 2, and so we first need to understand the structure of the intermediary data which it transformed. There are three approaches to understanding the intermediate data structure when we have not been explicit in our code: 

1. remember the structure of that data - generally a bad thing to rely on in software design because you may be looking at this years later or someone else may be looking at it;

2. run the first pipeline component and use some runtime introspection tool (breakpoints, print statements, debuggers, etc) to look at the data - possible but clunky and time-consuming; or 

3. do some mental bookkeeping to trace the original input data (which may also require introspection) through the pipeline - also a time-consuming activity. 

None of these options look good - the best scenario is option 3, and even that is only viable if you know both the structure of the input data and are okay reading through the logic up until that point. Unfortunately, debugging or changing intermediary stages of your data pipeline will happen all the time - this can create some big problems as your project grows and your requirements change.

What is the problem with running the code in real time? In my experience, this simply takes a lot longer than keeping track of the code itself (either reading it or using a static analyzer) when it comes to large data pipelines. Each step or set of steps in your pipeline are expensive and probably time-consuming. To make it easier, you might optimize the pipeline by storing intermediary steps (RData or pickle files) so you can load them into separate notebooks more quickly, but this optimization is time-consuming and would need to be done every time you set out to work. In software engineering, it is generally far better to detect any problems without needing to actually run your code.

In the case where you represent the structure of your data as part of the code itself (i.e. use classes/structs to define intermediate structures), however, you (and your compiler/static analyzer) know the structure of the data at every stage of the pipeline because it is explicitly defined. From this alone you know not only that your data will appear in the specified formats (providing some gaurantees), but also that the role of that particular function/script is to convert data of type B to type C. In this case, the pipeline issue will be much easier to identify.




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
