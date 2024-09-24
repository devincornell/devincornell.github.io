from __future__ import annotations

import pandas as pd
import typing
from .irisentry import IrisEntry

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
    