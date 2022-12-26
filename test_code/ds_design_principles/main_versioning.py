

import pandas as pd
import typing
import irises
import dataclasses

@dataclasses.dataclass
class IrisA:
    sepal_length: int
    sepal_width: int
    species: str

@dataclasses.dataclass
class IrisB:
    sepal_area: float
    
    @classmethod
    def from_a(cls, a: IrisA):
        return cls(sepal_area = a.sepal_length * a.sepal_width)


class IrisB:
    pass

@dataclasses.dataclass
class IrisB_v1(IrisB):
    sepal_area: float
    
    @classmethod
    def from_a(cls, a: IrisA):
        return cls(sepal_area = a.sepal_length * a.sepal_width)

@dataclasses.dataclass
class IrisB_v2(IrisB):
    sepal_area: float
    species: str
    
    @classmethod
    def from_a(cls, a: IrisA):
        return cls(sepal_area = a.sepal_length * a.sepal_width, species=a.species)

@dataclasses.dataclass
class Params:
    version_name: str
    IrisB: type
    intermediate_fname: str
    final_fname: str


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

if __name__ == '__main__':
    params = params_0x1()
    
    a = IrisA(1.0, 2.0, 'big')
    
    b = params.IrisB.from_a(a)
    
    f'result_{params.version_name}.csv'
    
    

        