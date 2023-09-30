

import typing
import dataclasses

@dataclasses.dataclass
class MyBasicType:
    x: typing.Any

T = typing.TypeVar("T")

@dataclasses.dataclass
class MyType(typing.Generic[T]):
    '''Wraps a value.'''
    x: typing.Optional[T]


Number = typing.Union[float, int]

@dataclasses.dataclass
class MyFirstType:
    '''Wraps a value.'''
    x: typing.Optional[Number]
    
@dataclasses.dataclass
class MySecondType:
    '''Wraps value that is not None.'''
    x: Number
    def add(self, y: Number) -> Number:
        return self.x + y

@dataclasses.dataclass
class MyThirdType:
    '''Wraps value that is not None or zero.'''
    x: Number

    def add(self, y: Number) -> Number:
        return self.x + y

    def invert(self) -> float:
        return 1.0 / self.x
    
SomeType = typing.Union[MyFirstType, MySecondType, MyThirdType]


def make_third_type(x: typing.Optional[Number]) -> MyThirdType:
    return MyThirdType(x)

def make_new_type(x: typing.Optional[Number]) -> SomeType:
    if x is None:
        return MyType(x)
    elif x == 0:
        return MySecondType(x)
    else:
        return MyThirdType(x)
    
if __name__ == '__main__':
    a: typing.List[typing.Optional[int]] = [None, 1, 2, 3]
    #sum(a)
    b = [v for v in a if v is not None]
    sum(b)
    c: typing.List[int] = [v for v in a if v is not None]
    sum(c)
    
    mbt = MyBasicType(1)
    #mbt.x + 'hello world'
    
    mt = MyType[float](1)
    print(mt)
    # mt.x + 'hello world'
    
    nt = make_new_type(0.0)
    print(nt.add(1.0))
    print(nt.add(1.0)) # typing: ignore
    print(typing.cast(nt, MySecondType).add(1.0))
    if isinstance(nt, MySecondType):
        print(nt.add(1.0))


