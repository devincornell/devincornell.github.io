---
title: "Are dataframes too flexible?"
subtitle: "The challenges with implicit data structures."
date: "May 28, 2023"
id: "zods2_problem_with_dataframes"
---

Dataframe interfaces are useful because they are so flexible: filtering, mutatating, selecting, and grouping functions have simple interfaces and can be chained to perform a wide range of transformations on tabular data. The cost of this flexibility, I argue, is that your data pipelines are less readable, more difficult to maintain, and more error prone. Recently I wrote a [piece](../zods1_more_structure.html) where I argued that including more explicit data structures like classes and structs can drastically improve your data pipelines, and dateframes or other flexible data structures tend to fall far short of this aim. In this piece, I will illustrate the shortcomings of using these data structures and then provide some suggestions for alternative approaches.

Admittedly, part of my motivation for this article is reactionary. Over the last decade of teaching and reading about data science practices, I have seen a shift in the way that students are learning. Students start learning with tools like Jupyter and RStudio markdown because they allow for quick experimentation on a step-by-step basis and enable them to try new things with near-instant feedback. Expansive packages like Pandas and tidyverse are becoming essential material, and students often engage with them before they even understand the language they are built in (me too, sometimes). There is no doubt that they are learning powerful tools, but my concern is that we are sacraficing fundamentals of programming that are essential for building real-world projects. Anyone can learn to write code on their own, but time with teachers and mentors should be spent learning how to write _good_ code.



The selling point for packages like Pandas or other tabular data structures in R for beginners is precisely that they require minimal code to do powerful things. For instance, much can be acheived using basic filter, mutate, select, join, and grouping functions, and many tutorials, especially those from the tidyverse, teach students to explicitly 

that modifying the operations we perform and the 


While there are more tutorials and guides to learn programming than ever before, I 



Before students learn about classes they are taught to manipulate dataframes, usually in a serial manner where data is transformed from one to the other.

Dataframes (or other tabular data structures) are quentissential to 






# The data science pipeline

For illustration, I created a simple diagram with two linear data pipelines depicting the transformation of the input data into an intermediate data structure which is changed into the final data to be shared with the customer (a table or figure, let's say). As I noted earlier, almost every part of your data analysis pipeline will look something like this. In the top example, we do not keep track of the structure of the input or intermediate data in our code explicitly, wheras in the bottom pipeline we represent them as objects A, B, and C. The idea is that pipelines with explicit references to data structure in the code make it easier to understand what each transformation is doing - in theory, we (and the static analyzer in your IDE) could understand the entire pipeline without ever running our code.

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
