from __future__ import annotations
import attrs
import attr
import typing

import seaborn
import pandas as pd

import attrs
import attr

@attr.s(frozen=True, slots=True)
class IrisEntry:
    sepal_length: int = attrs.field(converter=float)
    sepal_width: int = attrs.field(converter=float)
    species: str = attrs.field(converter=str)
    
    @classmethod
    def from_dataframe_row(cls, row: pd.Series):
        return cls(
            sepal_length = row['sepal_length'],
            sepal_width = row['sepal_width'],
            species = row['species'],
        )
        
    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Union[float,str]]):
        return cls(
            sepal_length = data['sepal_length'],
            sepal_width = data['sepal_width'],
            species = data['species'],
        )
    
    def sepal_area(self) -> float:
        return SepalArea.from_entry(self)
        
@attr.s(frozen=True, slots=True)
class SepalArea:
    sepal_area: int = attrs.field(converter=float)
    species: str = attrs.field(converter=str)
    
    @classmethod
    def from_entry(cls, entry: IrisEntry):
        return cls(
            sepal_area = entry.sepal_length * entry.sepal_width,
            species = entry.species,
        )

@attr.s(frozen=True, slots=True)
class Plotter:
    sepal_areas: typing.List[SepalArea] = attrs.field()
    
    def plot_by_species(self):
        # some plotting code here
        pass

    
if __name__ == '__main__':
    iris_df: pd.DataFrame = seaborn.load_dataset("iris")
    print(iris_df.shape)
    print(iris_df.head())

    entries = IrisEntries.from_dataframe(iris_df)
    print(entries)
    
    grouped_areas = {sp:IrisAreas.from_entries(es) 
                    for sp,es in entries.group_by_species()}
    
    print({sp: ars.av_areas() for sp,ars in grouped_areas.items()})
    
    
        
    
    
    
    

