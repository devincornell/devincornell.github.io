---
title: "Data Science Software Design Principles"
subtitle: "I wanted to propose some basic principles for engineering your data science codebases."
date: "December 26, 2022"
id: "data_science_design_principles"
---

I wanted to reflect on a few design principles for software design of your data science pipeline that I have come to after doing data analysis for research and consulting over the last 7 years. Some of these projects were quick and simple, while others started out that way and quickly became cumbersome. It is the latter category of projects that encouraged me to propose these principles. While some are derived directly from accepted software design principles, others directly contradict them - in these cases, I relied on my own experience on the patterns we fall into and the needs of data science projects to propose alternative approaches. First I list the principles, then I go into more details.

1. ***The structure of your data should be explicit.*** I propose several general principles and some Python-based examples of how you might go about implementing them. Here are some of the general principles: avoid dataframes when possible, use object-oriented designs, implement data validation upon ingestion and throughout your pipeline, and use custom exceptions for missing data.

2. ***Version almost everything.*** This means both within your code and with data files or databases. While this violates conventional software design principles because it will lead to extreme code rot, it will be critical for keeping track of which pipelines and settings were used to generate each intermediary or final piece of data. This is especially important when you try different parameter sets and need to know exactly which settings were used to generate each result. Git is the bare minimum here, although using the releases features there could be a good temporary substitute. While following this in every situation might be overkill, I recommend doing it for especially critical parts of your code - particularly for your final (or communicated) result result files.

3. ***Create settings objects files that live in your code.*** Create explicit settings objects to store parameters used to generate each intermediary or final dataset in your project. This follows directly from the previous two points, and it will make it easy to identify which parameters were used to create each set of files. I have found this to be a more common issue than I expected.

4. ***Make I/O explicit in your top-level scripts.*** Filenames and write functions should always appear in the files you run directly (e.g. main file or toplevel script). This will make it easier to keep track of the data you generate to the scripts used to create them. It also makes clear to the reader that you are, in fact, producing output in the script.


# The structure of your data should be explicit

By this I mean that the structure of your data should be explicitly defined as part of your code. While it is tempting to pass dataframes from csv viles or nested iterables (e.g. lists of dictionaries) from json format through your data pipeline, these data structures can be error-prone and will make it more difficult to make changes once your data structures become sufficiently complicated. I recommend creating objects to represent each piece of data that you ingest. For instance, if you read in a csv file as a dataframe, consider creating a class definition that represents a single row of that dataframe and include the code to parse that data within the same class. 

Creating an explicit object definition for your data will provide built-in validation because you are making gaurantees for what your data will look like and how you will access its attributes downstream. Consistent with broader motivations for using OOP, you could build out your entire data pipeline beginning-to-end with just the knowledge of the properties of the data you will be using - it can be agnostic to the structure of the data you take as input. Similarly, explicit data definitions could also make things easier to test because you can write tests using synthetic data or even generate random data for Monte Carlo simulations. Additionally, your IDE can take advantage of intellisense or other autocomplete tools to help you code faster and with fewer errors.

I also recommend using [class method constructors](https://web.archive.org/web/20210130220433/http://as.ynchrono.us/2014/12/asynchronous-object-initialization.html) to handle the mapping between your source data (e.g. json or csv formatted data) and the object instances. For instance, say you have been working with a dataset in csv format for some time and your client then sends you a new data file that includes additional entries in a dataframe with different column names and variable codings. It is easy to add a new class method constructor that can load the same data from a different source.

Now I will show an example in Python. Lets start with the iris dataset as a pandas dataframe. You can see that each entry in the dataframe includes four measurements and a string representing the species.
    
    import pandas as pd
    import typing

    iris_df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
    print(iris_df.head())

    sepal_length  sepal_width  petal_length  petal_width species
    0           5.1          3.5           1.4          0.2  setosa
    1           4.9          3.0           1.4          0.2  setosa
    2           4.7          3.2           1.3          0.2  setosa
    3           4.6          3.1           1.5          0.2  setosa
    4           5.0          3.6           1.4          0.2  setosa


Now we want to create a Python object that will represent a single row from the original dataframe. [Dataclasses](https://realpython.com/python-data-classes/), which have now been added to the Python standard library, are a great place to start for implementing this pattern. This example below shows the object representing a single entry in the dataframe shown above. It includes an entry for each column, a method for calculating the sepal area, and the class method constructor (created using @classmethod) `from_dataframe_row` which can be used to create an instance from a row of the dataframe.

    @dataclasses.dataclass(frozen=True)
    class IrisEntryDataclass:
        idx: str
        sepal_length: int
        sepal_width: int
        petal_length: int
        petal_width: int
        species: str
        
        # class method constructors are great btw
        @classmethod
        def from_dataframe_row(cls, idx: str, row: pd.Series):            
            # create intermediate variable with type hint to indicate
            # this function will return whatever type it is
            new_obj: cls = cls(
                idx=idx,
                sepal_length = row['sepal_length'],
                sepal_width = row['sepal_width'],
                petal_length = row['petal_length'],
                petal_width = row['petal_width'],
                species = row['species'],
            )
            return new_obj
    
        def sepal_area(self) -> float:
            return self.sepal_length * self.sepal_width

And then you can create a function to make a list of these objects from a dataframe.

    def dataframe_to_entries(df: pd.DataFrame) -> typing.List[IrisEntryDataclass]:
        entries = list()
        for ind, row in iris_df.iterrows():
            new_iris = IrisEntryDataclass.from_dataframe_row(ind, row)
            entries.append(new_iris)
        return entries

While dataclasses are useful, I recommend going a step further by using `attrs` to include explicit data validation. The [attrs package](https://www.attrs.org/en/stable/overview.html) provides some convenient methods for creating classes meant for storing data, so we will use that. Note: `attrs` [provides a superset of the features found in `dataclasses`](https://www.attrs.org/en/stable/why.html#data-classes) because it acted partially as their inspiration for inclusion in the standard library. Next I will create a class that does the following things: uses class constructor methods instead of `__init__` for mapping the original data to this data structure, has explicit attributes representing data in each row, is immutable (cannot be changed after creation), uses slots, and implements data validation methods.

I use the `frozen=True` and `slots=True` settings to make sure the object is immutable (cannot be changed) and uses slots (see [this explanation](https://www.geeksforgeeks.org/python-use-of-__slots__/)), which reduces memory usage and prevents the user from creating attributes later on. Thus, we can gaurantee that the object cannot be modified after creation, although we define methods that derive from the original data. 

I implement validation using several methods. I use the `converter` parameter of `attrs.field()` to enforce data conversion - in addition to throwing errors for non-convertable types, this can prevent your code from being sensitive to the way that the data was ingested (e.g. whether pandas converted a column to a string). I also added two data validation methods using decorators recognized by `attrs`: `species_validator` and `meas_validator`; these define the criteria of the data being inserted upon instantiation. Note that because I did not use the `default` parameter in `attrs.field`, all of this data must be provided during instantiation. This is my class definition:

    import attrs
    import attr

    @attr.s(frozen=True, slots=True)
    class IrisEntry:
        idx: str = attrs.field()
        
        # these are all measurements in the attrs dataframe
        sepal_length: int = attrs.field(converter=float)
        sepal_width: int = attrs.field(converter=float)
        petal_length: int = attrs.field(converter=float)
        petal_width: int = attrs.field(converter=float)

        # adding converter=str makes sure that the property is a string (and string convertable)
        # these will both be validated later using the species_validator method.
        species: str = attrs.field(converter=str) 

    # class constructors are great btw
    @classmethod
    def from_dataframe_row(cls, idx: IrisEntryID, row: pd.Series):
        '''Class constructor from dataframe row.'''
        
        # create intermediate variable with type hint to indicate
        # this function will return whatever type it is
        new_obj: cls = cls(
            idx=idx,
            sepal_length = row['sepal_length'],
            sepal_width = row['sepal_width'],
            petal_length = row['petal_length'],
            petal_width = row['petal_width'],
            species = row['species'],
        )
        return new_obj

    ################### Validator Methods ###################
    # validates the length of names
    @species.validator
    def species_validator(self, attr, value) -> None:
        if not len(value) > 0:
            raise ValueError(f'Attribute {attr} must be a '
                'string larger than 0 characters.')
        
    # this can act as a validator for all of these attributes by adding the decorators
    @sepal_length.validator
    @sepal_width.validator
    @petal_length.validator
    @petal_width.validator
    def meas_validator(self, attr, value) -> None:
        if not value > 0:
            raise ValueError(f'Attribute {attr.name} was {value}, but it must be larger than zero.')

    ################### Methods ###################
    def sepal_area(self) -> float:
        '''Get '''
        return self.sepal_length * self.sepal_width
    
    def petal_area(self) -> float:
        return self.petal_length * self.petal_width

This class provides gaurantees about the structure of your data - if your class method constructor runs without errors, you know that your data structure will have the required data early in your pipeline. Furthermore, all validation and data structuring is done as part of the object - you won't need to write an additional validation script to verify that the data meets some assumed criteria. Multiple methods for producing the same dataset can be implemented in the same class. In this way, all checks and gaurantees about your data exists in this single class. If you want to change assumptions or structure of the data, it will appear here.

Later on in our pipeline we will create functions and methods for working with these lists of entries, but upon reading this definition we can't necessarily tell how it will be used. To this end, we can subclass a Python list to include both a class method constructor and any additional operations a user may need to perform on the list. Placing any transformation logic here will also make things easier later in the data pipeline. If something is needed in the future, you can always come back and additionally extend the class. Note that extending a List builtin is always risky - be sure to use specific method names so as to not overload an existing attribute of List.

In this example, I create a class method constructor `from_dataframe` that iterates through each row of the dataframe and creates a new entry by calling `IrisEntry.from_dataframe_row`. This returns a IrisEntriesList instance that we can then access like a normal list or through the provided methods. I provided grouping and filtering methods, and, if needed, you can always convert back to a dataframe if really needed.

    class IrisEntriesList(typing.List[IrisEntry]):
        
        @classmethod
        def from_dataframe(cls, df: pd.DataFrame):
            # add type hint by hinting at returned variable
            new_entries: cls = cls([IrisEntry.from_dataframe_row(ind, row) for ind,row in df.iterrows()])
            return new_entries
        
        def as_dataframe(self) -> pd.DataFrame:
            return pd.DataFrame({
                'sepal_length': [e.sepal_length for e in self],
                'sepal_width': [e.sepal_width for e in self],
                'petal_length': [e.petal_length for e in self],
                'petal_width': [e.petal_width for e in self],
            })
        
        def group_by_species(self) -> typing.Dict[str, IrisEntriesList]:
            groups = dict()
            for e in self:
                groups.setdefault(e.species, self.__class__())
                groups[e.species].append(e)
            return groups

        def filter_sepal_area(self, sepal_area: float):
            entries: self.__class__ = self.__class__([e for e in self if e.sepal_area() >= sepal_area])
            return entries



