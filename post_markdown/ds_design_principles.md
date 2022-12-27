---
title: "Data Science Software Design Principles"
subtitle: "I propose some basic software design principles that will improve the flexibility, reproducibility, and error-tolerance of your data science code and then give some concrete design patterns that you can start using today."
date: "December 26, 2022"
id: "data_science_design_principles"
---

I wanted to reflect on a few design principles for software design of your data science pipeline that I have come to after doing data analysis for research and consulting over the last 7 years. Some of these projects were quick and simple, while others started out that way and quickly became cumbersome. It is the latter category of projects that encouraged me to propose these principles. While some are derived directly from accepted software design principles, others directly contradict them - in these cases, I relied on my own experience on the patterns we fall into and the needs of data science projects to propose alternative approaches. First I list the principles, then I go into more details.

1. ***The structure of your data should be explicit.*** Avoid dataframes or nested iterables when possible, use object-oriented designs, implement data validation upon ingestion and throughout your pipeline, and use custom exceptions for missing data. This approach will give you some built-in data validation and make it easier to extend later. I provide some Python-based recipes that might illustrate these points.

2. ***Version almost everything.*** Version both your code and data files/databases. While this can (and will) lead to a high level of code rot, it will be critical for keeping track of which pipelines and settings were used to generate each intermediary or final piece of data. This is especially important when you try different parameter sets and need to know exactly which parameters were used to generate each result. Git is the bare minimum here, although using the releases features there could be a good temporary substitute. While following this in every situation might be overkill, I recommend doing it for especially critical parts of your code - particularly for your final (or communicated) result result files.

3. ***Create param objects files that live in your code.*** Create explicit param objects to store parameters used to generate each intermediary or final dataset in your project. This follows directly from the previous two points, and it will make it easy to identify which parameters were used to create each set of files. I have found this to be a more common issue than I expected.

4. ***Make I/O explicit in your top-level scripts.*** Read and write functions should always appear in the files you run directly (e.g. main file or toplevel script) and it should be clear which type of data you are reading/writing. By this principle I mean that it should be easy to tell which types of data are being ingested and which types are being saved through a quick scan of your script. I further suggest this should apply to everything.

5. ***Write custom exceptions to handle missing data (among other things).*** When 

Custom exceptions create a lot of flexibility when working with missing data. 

# The structure of your data should be explicit

By this I mean that the structure of your data should be explicitly defined as part of your code. While it is tempting to pass dataframes from csv viles or nested iterables (e.g. lists of dictionaries) from json format through your data pipeline, these data structures can be error-prone and will make it more difficult to make changes once your data structures become sufficiently complicated. I recommend creating objects to represent each piece of data that you ingest. For instance, if you read in a csv file as a dataframe, consider creating a class definition that represents a single row of that dataframe and include the code to parse that data within the same class. 

Creating an explicit object definition for your data will provide built-in validation because you are making gaurantees for what your data will look like and how you will access its attributes downstream. Consistent with broader motivations for using OOP, you could build out your entire data pipeline beginning-to-end with just the knowledge of the properties of the data you will be using - it can be agnostic to the structure of the data you take as input. Similarly, explicit data definitions could also make things easier to test because you can write tests using synthetic data or even generate random data for Monte Carlo simulations. Additionally, your IDE can take advantage of intellisense or other autocomplete tools to help you code faster and with fewer errors.

I also recommend using [class method constructors](https://web.archive.org/web/20210130220433/http://as.ynchrono.us/2014/12/asynchronous-object-initialization.html) to handle the mapping between your source data (e.g. json or csv formatted data) and the object instances. For instance, say you have been working with a dataset in csv format for some time and your client then sends you a new data file that includes additional entries in a dataframe with different column names and variable codings. It is easy to add a new class method constructor that can load the same data from a different source.

Now I will show an example in Python. Lets start with the iris dataset as a pandas dataframe. You can see that each entry in the dataframe includes four measurements and a string representing the species.
    
    import pandas as pd
    import typing

    url = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv'
    iris_df = pd.read_csv(url)
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
        sepal_length: int
        sepal_width: int
        species: str
        
        # class constructors are great btw
        @classmethod
        def from_dataframe_row(cls, row: pd.Series):
            '''Class method constructor from dataframe row.'''
            new_obj: cls = cls(
                sepal_length = row['sepal_length'],
                sepal_width = row['sepal_width'],
                species = row['species'],
            )
            return new_obj
        
        def sepal_area(self) -> float:
            return self.sepal_length * self.sepal_width


And then you can create a function to make a list of these objects from a dataframe.

    def dataframe_to_entries(df: pd.DataFrame, EntryType: type) -> typing.List:
        entries = list()
        for ind, row in df.iterrows():
            new_iris = EntryType.from_dataframe_row(row)
            entries.append(new_iris)
        return entries

While dataclasses are useful, I recommend going a step further by using `attrs` to include explicit data validation. The [attrs package](https://www.attrs.org/en/stable/overview.html) provides some convenient methods for creating classes meant for storing data, so we will use that. Note: `attrs` [provides a superset of the features found in `dataclasses`](https://www.attrs.org/en/stable/why.html#data-classes) because it acted partially as their inspiration for inclusion in the standard library. Next I will create a class that does the following things: uses class constructor methods instead of `__init__` for mapping the original data to this data structure, has explicit attributes representing data in each row, is immutable (cannot be changed after creation), uses slots, and implements data validation methods.

I use the `frozen=True` and `slots=True` settings to make sure the object is immutable (cannot be changed) and uses slots (see [this explanation](https://www.geeksforgeeks.org/python-use-of-__slots__/)), which reduces memory usage and prevents the user from creating attributes later on. Thus, we can gaurantee that the object cannot be modified after creation, although we define methods that derive from the original data. 

I implement validation using several methods. I use the `converter` parameter of `attrs.field()` to enforce data conversion - in addition to throwing errors for non-convertable types, this can prevent your code from being sensitive to the way that the data was ingested (e.g. whether pandas converted a column to a string). I also added two data validation methods using decorators recognized by `attrs`: `species_validator` and `meas_validator`; these define the criteria of the data being inserted upon instantiation. Note that because I did not use the `default` parameter in `attrs.field`, all of this data must be provided during instantiation. This is my class definition:

    import attrs
    import attr

    @attr.s(frozen=True, slots=True)
    class IrisEntry:
        '''Represents a single iris.'''
        sepal_length: int = attrs.field(converter=float)
        sepal_width: int = attrs.field(converter=float)
        species: str = attrs.field(converter=str) 
        
        @classmethod
        def from_dataframe_row(cls, row: pd.Series):
            '''Class method constructor from dataframe row.'''
            new_obj: cls = cls(
                sepal_length = row['sepal_length'],
                sepal_width = row['sepal_width'],
                species = row['species'],
            )
            return new_obj
        
        @species.validator
        def species_validator(self, attr, value) -> None:
            if not len(value) > 0:
                raise ValueError(f'Attribute {attr.name} must be a '
                    'string larger than 0 characters.')
        
        @sepal_length.validator
        @sepal_width.validator
        def meas_validator(self, attr, value) -> None:
            if not value > 0:
                raise ValueError(f'Attribute {attr.name} was '
                    f'{value}, but it must be larger than zero.')
        
        def sepal_area(self) -> float:
            return self.sepal_length * self.sepal_width


This class provides gaurantees about the structure of your data - if your class method constructor runs without errors, you know that your data structure will have the required data early in your pipeline. Furthermore, all validation and data structuring is done as part of the object - you won't need to write an additional validation script to verify that the data meets some assumed criteria. Multiple methods for producing the same dataset can be implemented in the same class. In this way, all checks and gaurantees about your data exists in this single class. If you want to change assumptions or structure of the data, it will appear here.

Later on in our pipeline we will create functions and methods for working with these lists of entries, but upon reading this definition we can't necessarily tell how it will be used. To this end, we can subclass a Python list to include both a class method constructor and any additional operations a user may need to perform on the list. Placing any transformation logic here will also make things easier later in the data pipeline. If something is needed in the future, you can always come back and additionally extend the class. Note that extending a List builtin is always risky - be sure to use specific method names so as to not overload an existing attribute of List.

In this example, I create a class method constructor `from_dataframe` that iterates through each row of the dataframe and creates a new entry by calling `IrisEntry.from_dataframe_row`. This returns a IrisEntriesList instance that we can then access like a normal list or through the provided methods. I provided grouping and filtering methods, and, if needed, you can always convert back to a dataframe if really needed.

    class IrisEntriesList(typing.List[IrisEntry]):
        
        @classmethod
        def from_dataframe(cls, df: pd.DataFrame):
            # add type hint by hinting at returned variable
            elist = [IrisEntry.from_dataframe_row(row) for ind,row in df.iterrows()]
            new_entries: cls = cls(elist)
            return new_entries
        
        def as_dataframe(self) -> pd.DataFrame:
            return pd.DataFrame({
                'sepal_length': [e.sepal_length for e in self],
                'sepal_width': [e.sepal_width for e in self],
                'species': [e.species for e in self],
            })
        
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

While this general approach has high overhead and requires more dicipline than using dataframes or nested iterables, it is much less prone to error and makes it easier to extend functionality in the future. Object-oriented design is essential for working with data, but it can also be helpful for improving other aspects of your data pipeline design.

# Version almost everything

More concretly, I suggest that you can retain multiple class definitions for the same type of object using naming conventions. It is easy to see how this can get out of hand, but the benefit is that you can always associate intermediate or final data files with the code used to create it. I recommend it in some specific scenarios, however: (1) when you produce a result that is shared with the client but possibly not a final version, (2) when producing a result that you may want to use as a comparison later, or (3) when keeping track of many intermediary data files. It can get complicated quickly, but using Python submodule encapsulation can help with some of it.

It might be worth thinking more about typical data science workflows to get a sense of why this might make sense. First, lets take a look at the following figure.

![data science pipeline overview](https://storage.googleapis.com/public_data_09324832787/ds_pipeline_workflow.svg)

At the top of this figure we see the original dataset, composed of one csv file and one json file. Each of the scripts that appear here involve some type of transformation from one data type to another. Script 1 takes the original csv data and converts it into a new Intermediate csv file. Script 3 takes the orignal csv file, the original json file, and the intermediate csv file generated by Script 1, and converts it into Final table csv file. Script 4 then converts this table into a visualization that will be presented to the client. Note that on the right we also see that Script 2 converts the original json data to Some figure png file - possibly for another analysis.

In an ideal world, we work on and finish Script 1, then work on and finish Script 2, and so on until we finish coding and can produce the final data from the original data. In a more practical scenario, most likely will need to go back and fix some upstream script to add or edit some information according to requirement changes or just changing realization of the information needed to produce intermediary results. When we do this, however, it doesn't always make sense to delete data that was previously generated - either so we can use it as reference or present it as intermediary results to the client. In these cases, it makes the most sense to keep track of the data and the code that was used to generate it through an informal versioning system of your design.

Assume that you are using some kind of object-data design, lets assume that the client gives you data in the format represented by the class `IrisA`.

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

The client has some suggested improvements, and you realize you need one additional piece of information from the `IrisA` dataset to be included as `IrisB`: the `species`. So you go back and edit `IrisB` to include this information. You use this dataset to produce the final result `finalB2.png`, and share with the client. 

    @dataclasses.dataclass
    class IrisB:
        sepal_area: float
        species: str
        
        @classmethod
        def from_a(cls, a: IrisA):
            return cls(sepal_area = a.sepal_length * a.sepal_width, species=a.species)


The client asks about a discrepency between `finalB.png` and `finalB2.png` - can you answer their question? You could go back to the correct commit based on datetimes, but that might be a little tricky. Instead, I recommend creating a versioning system that is consistent between the names of your data objects and the intermediate data files they were used to generate.

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

# Create parameter objects that live in your code

Building off of the previous two examples, I recommend creating parameter objects that you can use to keep track of results created with different parameters. This essentially follows from the previous two examples, but further introduces the possibility that you may generate results from many different parameter sets over the lifetime of your project. Ideally the defined parameter set will be used at every step of your data pipeline to make it perfectly reproducable. Lets see the example below.

Start by creating a dataclass to contain parameter information. This defines all the variables that will be used to generate results throughout your data pipeline. It might be helpful to have some `version_name` member to make it easy to get the version as a string. This even includes a parameter that accepts a type - this will allow you to control which version of a class is being used throughout your pipeline. This may be overkill, but I could imagine projects that are of sufficient complexity as to benefit to this level of detail.

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

This approach may be overkill in many scenarios, but if the project gets large enough it is an option you may want to consider.


# Make I/O explicit in your top-level scripts

This principle is very simple: make it such the user can see save and read functions at the top level of your script (even if the filenames are hidden). It should be clear to the reader that the script is ingesting one or more datasets and exporting others. Adding this to your script can save you a lot of time later when you try to determine which types of data this script makes and outputs.






