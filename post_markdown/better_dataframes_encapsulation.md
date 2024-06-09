---
title: "Better Dataframes: Encapsulation"
subtitle: "Using basic principles of encapsulation to improve the ways you work with tabular data."
date: "June 8, 2024"
id: "bdf1_encapsulation"
blogroll_img_url: "https://storage.googleapis.com/public_data_09324832787/better_dataframes_encapsulation.svg"
---

Last year I wrote an article about [why I try to avoid using dataframes](zods0_problem_with_dataframes.html). Dataframes are powerful because they are so versatile and flexible, but my argument was that rigorous data analysis code should introduce as much rigidity as possible to reduce the likelihood of mistakes. As an alternative, I suggested we implement data pipelines as transformations between custom object types - types you define yourself with (intentionally) limited functionality and readable structure. That said, as a professional social scientist who often has to analyze survey data, I recognize that sometimes dataframes are still the best tools for the job. In this article, I will explain how my suggested approaches can be used for dataframe-oriented pipelines. 

![Dataframe transformation visualization.](https://storage.googleapis.com/public_data_09324832787/better_dataframes_encapsulation.svg)


[Encapsulation](https://www.datacamp.com/tutorial/encapsulation-in-python-object-oriented-programming) is one of the most basic principles of object-oriented programming; it means bundling data elements with methods that operate on the data (fundamental to Python classes) and creating interfaces for working with those data elements rather than requiring users to access or modify that data directly. By encapsulating dataframes within custom types, we can create interfaces that (1) implicitly or explicitly enforce structure and (2) have clear interfaces for transformations that may be applied to our particular dataset. Now I'll use some Python examples to show how we can use this principle in our design patterns.

For these examples, I'll use the iris dataset, which can easily be accessed through the `seaborn` package. You can see the 

    import pandas as pd
    import dataclasses
    import typing
    import seaborn

    iris_df = seaborn.load_dataset("iris")
    print(iris_df.head(3))

The first several rows of that dataframe look like this:

        sepal_length  sepal_width  petal_length  petal_width species
    0           5.1          3.5           1.4          0.2  setosa
    1           4.9          3.0           1.4          0.2  setosa
    2           4.7          3.2           1.3          0.2  setosa


## Create Custom Types to Encapsulate the Dataframes

Now we create a custom type to encapsulate this dataframe. We can do this by creating a new [dataclass](https://realpython.com/python-data-classes/) with a single attribute: the dataframe we are encapsulating (see also [my tips for writing effective dataclasses](dsp0_patterns_for_dataclasses.html)). I will also add a `__repr__` method to make any output more readable. Note that here I'm using a variable name with a double underscore prefix "__" so that Python will strictly enforce encapsulation: the inner dataframe cannot be accessed from outside methods of this class. For most cases I believe this is overkill - you need not place that restriction unless you believe something could go very wrong.

    @dataclasses.dataclass
    class IrisData0:
        __df: pd.DataFrame

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}(size={self.__df.shape[0]})'
    
The `dataclass` decorator created a constructor for this object underneath the hood, so creating a new IrisData1 object is as simple as using the constructor.

    idata = IrisData0(iris_df)
    idata

The `__repr__` method we created above shows the object name and the number of rows in the table.

    output:
        IrisData0(size=150)

To encapsulate our data, we need to create methods that allow users to access aspects of the underlying data explicitly. I will create two property methods which allow the user to access columns of the underlying dataset. For this application, I would recommend creating properties for each column of the dataframe.

        @property
        def sepal_length(self) -> pd.Series:
            return self.__df['sepal_length']

        @property
        def species(self) -> pd.Series:
            return self.__df['species']

These properties return regular Pandas `Series` objects, so we may transform them but they cannot be reassigned by the downstream user. For instance, we can compute the number of observations by species.

    idata.species.value_counts()

And the result is a regular Series object.

    output:
        species
        setosa        50
        versicolor    50
        virginica     50
        Name: count, dtype: int64

To make this object useful, we will also need to create methods for transforming the data. A common operation we might want to perform on the data is to calculate the average lengths and widths by species. Recall that we must implement this as part of the `IrisData0` class because the contained dataframe should not be exposed to the downstream user.

        def species_mean_dataframe(self) -> pd.DataFrame:
            return self.__df.groupby('species').mean()

The downstream user can call the method without accessing the dataframe directly.

    idata.species_mean_dataframe()

This function returns a regular dataframe that can be manipulated however the user see fit.

    output:
                    sepal_length  sepal_width  petal_length  petal_width
        species                                                         
        setosa             5.006        3.428         1.462        0.246
        versicolor         5.936        2.770         4.260        1.326
        virginica          6.588        2.974         5.552        2.026

#### Oh, the Power

While this most basic example is trivial to implement, the improvement over using raw dataframes cannot be understated. Here are some of the benefits:

1. _We gave it a name. This is so important._ This name can be used as a type hint for static analyzers or as an input library so that you know what kind of dataframe is expected. If you inspect the dataframe inside objects of this type, you will have certain expectations for what the underlying data will look like regardless of where it fits within your data pipeline.

2. _We restricted the ways that users can access the underlying data._ The user can only access the properties we defined on the object. From simply inspecting our object definition, we know that the user will never be able to change the column or index names, for instance, without changing the underlying dataframe being encapsulated. Because of this, we can guarantee that the property `sepal_length` will always return the pandas series for that column, 

3. _We defined the transformations that may be applied to this data._ We know that `species_mean_dataframe` is the only transformation that will ever be applied to this dataframe directly. If you ever go back to change this class, you will know all use cases to support simply by looking at the object methods. A static analyzer can look _only_ at this object and know whether any of the methods will fail.


## Connecting the Pipes

The benefits of these patterns only grow as we apply them to other parts of our data pipelines. Let us return to the method we used to compute averages of all the attributes within each species above. The return type of this function is a dataframe, and so we should consider encapsulating it as well. Let us call the encapsulating class `SpeciesMean0` and the definition will look familiar. I make an additional property to access all the unique species in the dataset as well.

    @dataclasses.dataclass
    class SpeciesMean0:
        __species_av: pd.DataFrame

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}(num_species={self.__species_av.shape[0]})'

        @property
        def all_species(self) -> typing.List[str]:
            return list(self.__species_av.index)

Now we can create a factory constructor method for `SpeciesMean0` so that it knows how to create itself from the original type. To create it, we call the existing `species_mean_dataframe` method.

        @classmethod
        def from_iris_data(cls, iris_data: IrisData0) -> typing.Self:
            return cls(iris_data.species_mean_dataframe())

Call this factory method constructor to create the average from the original Iris data object.

    SpeciesMean0.from_iris_data(idata)

The new object `__repr__` makes it look very similar to the previous example object.

    output:
        SpeciesMean0(num_species=3)

To make a cleaner interface, we can even call this constructor method from a method of the original data source. While this increases coupling between the objects, it ensures every object knows how to create itself from any other object type.

    @dataclasses.dataclass
    class IrisData0:
        __df: pd.DataFrame
        ...
        def species_mean(self) -> SpeciesMean0:
            return SpeciesMean0.from_iris_data(self)

And you can use this method like any other.

    idata.species_mean()

The expected return type is returned.

    output:
        SpeciesMean0(num_species=3)

In this way, you could imagine a series of dataframe transformations being represented as a series of custom types with factory construction methods determining how each object was created from others. It is much simpler to describe your data pipelines in terms of sequences of defined types instead of sequences of dataframes with different structures. From a quick scan, the reader knows the kinds of transformations which are expected to occur on the data. This is a powerful benefit of encapsulation and custom types.

## A Little Bookkeeping

The example above shows the power of encapsulation, but we can create stronger guarantees about the structure of the data from the input all the way through the pipeline by doing a little more bookkeeping. Recall that the optimal behavior for a buggy data pipeline is to fail fast and early. To do this, we can more explicitly keep track of structural features of the dataframe such as column names, and access attributes only through other objects or data tables. 

For example, let us design a type which contains all of the column names that should appear in the input data. If we can guarantee that the input data has all of these columns when it is ingested, we can make sure our program fails right away rather than waiting until we try to access the property. Here I create the classmethod `all` so we can grab the full list later.

    class IrisColNames:
        sepal_length = 'sepal_length'
        sepal_width = 'sepal_width'
        petal_length = 'petal_length'
        petal_width = 'petal_width'
        species = 'species'

        @classmethod
        def all(cls) -> typing.List[str]:
            return [cls.sepal_length, cls.sepal_width, cls.petal_length, cls.petal_width, cls.species]

The encapsulating object itself looks very similar to the previous example, except that the factory method constructor explicitly selects the columns defined in `IrisColNames` instead of waiting for them to be accessed downstream. You can also see that we referenced the `IrisColNames` attributes instead of the names of the columns explicitly.

    @dataclasses.dataclass
    class IrisData1:
        __df: pd.DataFrame
        
        @classmethod
        def from_dataframe(cls, df: pd.DataFrame) -> typing.Self:
            return cls(
                df[IrisColNames.all()]
            )

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}(size={self.__df.shape[0]})'

        @property
        def sepal_length(self) -> pd.Series:
            return self.__df[IrisColNames.sepal_length]
        
        @property
        def species(self) -> pd.Series:
            return self.__df[IrisColNames.species]
        
        def filter_by_species(self, species: str) -> typing.Self:
            return self.__class__(self.__df.query(f'{IrisColNames.species} == "{species}"'))


Without enforcing these column names at ingestion, there is a potential for simple errors to propagate downstream and cause errors in the future. For instance, consider our first example of `IrisData0`. If the input data file had named the sepal length property `"sepal_len"` instead of `"sepal_length"`, we wouldn't know there was an error until we either accessed the `sepal_length` attribute or a related parameter downstream. Even worse, imagine the dataset is one that might be averaged downstream without first checking if all columns are present. We would have a significant error that goes silently through our data pipeline.

Explicitly enumerating the columns associated with the input data takes more work but can also make your code more modular. Imagine that another way of Iris data is collected, but the format of the input data is slightly different: some of the column names are different. In this case, we may want to separate our column name sets into `IrisColNames2013` and `IrisColNames2024` types which both inherit from `BaseIrisColNames`. The `IrisData.from_dataframe` factory method constructor could then accept a subtype of `BaseIrisColNames` or you could create multiple constructor such as `from_2024_dataframe` which load the appropriate column name type but otherwise behaves the exact same. In either case, the user will be required to call the correct input parsing code for the given input data. 

## In Conclusion

The tips I shared here are a great start to improving data pipelines that involve dataframes, and I strongly encourage you to explore other ways of building more structure into your data pipelines. While I do believe that dataframes are the wrong choice most of the time, with a little work we can drastically improve our code to prevent many of the pitfalls. Happy analyzing!



