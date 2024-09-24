from __future__ import annotations

import pandas as pd
import typing
from .irisentry import IrisEntry
from .ids import IrisEntryID

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
    