from __future__ import annotations
import numpy as np
import pandas as pd
import dataclasses
import typing


class Variable:
    pass

@dataclasses.dataclass
class RatioVar(Variable):
    '''Variable representing interval measurements.
    '''
    v: np.ndarray[np.float64]

    @classmethod
    def from_iter(cls,
        elements: typing.Iterable[float|int],
        dtype: np.float64,
    ) -> typing.Iterable:
        return cls(
            v = np.array(elements, dtype=dtype),
        )

class OrdinalVar(Variable):
    pass

class NominalVar(Variable):
    v: np.ndarray[np.float64]

    @classmethod
    def from_iter(cls,
        elements: typing.Iterable[str|float|int],
        order: typing.List[str|float|int],
        dtype: np.float64,
    ) -> typing.Iterable:
        return cls(
            v = np.array(elements, dtype=dtype),
        )

