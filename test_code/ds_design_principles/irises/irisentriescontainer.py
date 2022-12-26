from __future__ import annotations

import pandas as pd
import typing
from .irisentry import IrisEntry
from .ids import IrisEntryID

class IrisEntriesContainer:
    def __init__(self, entries: typing.List[IrisEntry]):
        self.entries = entries
        
    def __getitem__(self, ind: int) -> IrisEntry:
        return self.entries[ind]
    
    def __iter__(self) -> typing.Iterator[IrisEntry]:
        return iter(self.entries)
    
    def __len__(self) -> int:
        return len(self.entries)
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame):
        # add type hint by hinting at returned variable
        new_entries: cls = cls([IrisEntry.from_dataframe_row(ind, row) for ind,row in df.iterrows()])
        return new_entries
        
    def group_by_species(self) -> typing.Dict[str, IrisEntriesContainer]:
        groups = dict()
        for e in self.entries:
            groups.setdefault(e.species, list())
            groups[e.species].append(e)
        
        return {s:self.__class__(es) for s,es in groups.items()}

    def filter_sepal_area(self, sepal_area: float):
        entries: self.__class__ = self.__class__([e for e in self.entries if e.sepal_area() >= sepal_area])
        return entries
    
    
    