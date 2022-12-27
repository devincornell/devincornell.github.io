
import pandas as pd
import typing
import irises
import dataclasses


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

def dataframe_to_entries(df: pd.DataFrame, EntryType: type) -> typing.List:
    entries = list()
    for ind, row in df.iterrows():
        new_iris = EntryType.from_dataframe_row(row)
        entries.append(new_iris)
    return entries


if __name__ == '__main__':
    iris_df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')

    print(iris_df.head())
    
    entries = dataframe_to_entries(iris_df, IrisEntryDataclass)
        
    print(len(entries))
    print(entries[0])
    
    entries = dataframe_to_entries(iris_df, irises.IrisEntry)
    print(len(entries))
    print(entries[0])


    # this one inherits from a list - it's a bit easier
    entries = irises.IrisEntriesList.from_dataframe(iris_df)
    
    # show them again
    print(len(entries))
    print(entries[0])
    
    # this one uses encapsulation - takes a bit more boilerplate
    entries_container = irises.IrisEntriesContainer.from_dataframe(iris_df)
    
    # show them again
    print(len(entries_container))
    print(entries_container[0])
    
    
    # show filtering
    filtered_entries = entries.filter_sepal_area(20)
    print(type(filtered_entries), len(filtered_entries))
    
    # show grouping
    groups = entries.group_by_species()
    print({s:len(entries) for s,entries in groups.items()})
    
    
    print(entries.as_dataframe().head())
        