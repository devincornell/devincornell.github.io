---
title: "Are dataframes too flexible? Optimal data structures for data pipelines."
subtitle: "The challenges with implicit data structures."
date: "May 28, 2023"
id: "zods2_problem_with_dataframes"
---

Dataframe interfaces are useful because they are so flexible: filtering, mutatating, selecting, and grouping functions have simple interfaces and can be chained to perform a wide range of transformations on tabular data. The cost of this flexibility, I argue, is that your data pipelines are less readable, more difficult to maintain, and more error prone. Instead, I argue that it is better to use more explicit data structures like classes or structs with fixed attributes, specific methods for construction, and defined of methods for transformation/analysis. 

Over the last decade of teaching and reading about data science practices, I have seen a shift in the way that students are learning. Students start learning with tools like Jupyter and RStudio markdown because they allow for quick experimentation on a step-by-step basis and enable trying new things with near-instant feedback. Expansive packages like Pandas and tidyverse are becoming essential material, and students often engage with them before they even understand the language they are built in (me too, sometimes). There is no doubt that these are learning powerful tools, but my concern is that we are sacraficing fundamentals of programming that are essential for building real-world projects that are maintainable. Anyone can learn to write code, but, in my opinion, we should be teaching how to write _good_ code from the start.

In this article, I will describe what I mean by data structures within the context of data pipelines, the essential form of any data analysis project, in order to discuss optimal patterns on a theoretical level. Next, I will discuss three patterns for creating data pipelines in Python, although I believe the examples here apply to many languages - especially interpreted ones.

I believe that using custom data types, rather than dataframes or other less-explicit schemes, can make pipelines easier to understand, easier to maintain, and less error-prone.


## Data structures and pipelines

A data pipeline is a series of sequential steps for changing data from one format to another - the essential core of all data science projects. Maybe you want to visualize some variables from a CSV file in a 2-dimensional plot, produce a statistical model to capture trends of Tweets in json format, or even build a classifier to identify cats from an image training data set. In each of these cases, the data pipeline simply describes the set of transformations required to reach the final form from the given input data.

In computer science, data structures are defined as formats for organizing, processing, retrieving, and storing data^[Note that the term "data structure" has a somewhat institutionalized and more specific meaning within the field, but I will use this definition more literally and loosely.]. The way you choose to structure your data determines 



Aside from the input and output, which are identified prior to the work, the analyst has a lot of freedom to decide


At every stage in the pipeline, your data is represented as a kind of structure 

While the input and output data structures are often fixed according to the desired analysis, the analyst has a lot of flexibility over the way they construct the intermediary representations - so it is there that I will focus.


At every stage in the pipeline, your data takes on a format that makes it more or less easy to manipulate and run computations. 

In all cases, these data objects are stages in the data pipeline with a particular structure. A data structure means that the way that particular pieces of information are organized within your computers system - that is, how it is accessed and changed.


## Data pipelines: separating the "what" from the "how"


For illustration of a data pipeline, below I created a simple diagram with two linear data pipelines depicting the transformation of the input data into an intermediate data structure which is changed into the final data to be shared with the customer (a table or figure, let's say). 

![data science pipeline overview](https://storage.googleapis.com/public_data_09324832787/pipeline_structures.png)

The topmost path in the figure shows the case where we do not keep track of the structure of the input or intermediate data in our code explicitly (imagine using a list of dictionaries or a dataframe read from a csv file), wheras in the bottom pipeline we represent them as objects A, B, and C explicitly in our code. The idea is that pipelines with explicit references to data structure in the code make it easier to understand what each transformation is doing - in theory, we (and the static analyzer in your IDE) could understand the entire pipeline without ever _running_ our code.



### Features of Data Structures

In this article I will draw a dichotomy between two primary types of data structures: the dataframe, a tabular data structure with any number of columns and where each column is an array of numbers or objects; and custom data object types, implemented as structs or classes with project-specific representations and methods.

For the purpose of this article, I group data structures into two categories: objects such as dataframes or dictionaries/maps and custom object types with defined attributes such as classes or structs that are project/application-specific. I construct this dichotomy as it is essentially divided by three particular characteristics.

1. **Properties or attributes the elements contain.** Dataframes are flexible enough to allow you to dynamically add or remove columns, and custom object types tend to have a fixed set of properties which can be accessed/changed. 

2. **Method for construction.** Dataframes can be initialized using any number of methods, including transformations from other object types or read directly from csv or excel files on disks. Custom object types ideally have a limited set of methods for construction, and those methods are clear.

3. **Methods for summarizing or characterizing attributes.** There is a wide range of possible methods for summarizing or characterizing data in a dataframe, but, in the ideal case, custom data objects have a small set of methods for summarizing or characterizing their data.

Hiiiii^[Note that dataframes themselves are types and their columns have specific types within those objects, but the defining characteristic is that the interpreter or analyzer cannot infer those types without looking at the behavior of the functions or scripts used to produce it (which they often do not). They are types within the underlying package code, but they are not considered as types within the language itself. If you build your pipelines using functions that both accept and return dataframes, you do not know the structure of the new dataframe unless you look at the code used to transform it. In contrast, if you define custom types for the input and output data, you can know without looking at the]


They do not appear in your code except at the type of conversion or enforcement, or, even more sketchy. 

but my concern is that the types of individual columns are never known by your interpreter until you actually run the code. While you may specify and enforce column  

or contained elements are not known by your interpreter

by the reader or static analyzer prior to runtime. You can specify and enforce the types of columns in dataframes, but your interpreter or analyzer never actually



they are not probject-specific - that is, they do not enforce structures that are relevant to the specific project for which the pipeline is being built. When you read a dataframe from a csv file, for example, you can specify the code 

As such, simply knowing the type of an object does not give us insight into the representations that appear in the pipeline. 

Dataframes maintain types for the columns they maintain, however, you cannot see the types unless you do some introspection into the 



For a further elaboration on what I mean by adding more structure, see 


. As an example, if you read a csv file as a dataframe, consider creating a class definition that represents a single row of that dataframe and include the code to parse that data within the same class, as well as any methods that operate on that class' data. Then encapsulate those objects into collections in which you can build additional methods for parsing, grouping, filtering, or transforming collections/lists/etc. By defining classes explicitly, your analyzer knows which attributes and methods are available on that object at any point in time. Avoid using lists of dictionaries or other datastructures without defined types, as they have the same pitfalls as dataframes.




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
