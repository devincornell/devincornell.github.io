import dataclasses
import typing
import enum
from typing import Any
import timeit
import cProfile
import pstats


########################## option 3b: use result object #########################

T = typing.TypeVar("T")
E = typing.TypeVar("E")

@dataclasses.dataclass
class Ok(typing.Generic[T]):
    data: T
    is_ok: bool = True
    
    @property
    def error(self) -> typing.NoReturn:
        raise AttributeError(f'{self.__class__.__name__} has no attribute "error"')
    
@dataclasses.dataclass
class Err(typing.Generic[E]):
    error: typing.Optional[E] = None
    is_ok: bool = False
    
    @property
    def data(self) -> typing.NoReturn:
        raise AttributeError(f'{self.__class__.__name__} has no attribute "data"')
    
Result = typing.Union[Ok[T],  Err[E]]

class MyErrorType(enum.Enum):
    IS_NONE = enum.auto()
    IS_NEGATIVE = enum.auto()

@dataclasses.dataclass
class MyObj:
    x: typing.Optional[int]
    
    def access_x_exception(self) -> typing.Optional[int]:
        if self.x is None or self.x >= 0:
            return self.x
        else:    
            raise ValueError('x is negative so it is invalid')
    
    def access_x(self) -> Result[typing.Optional[int], None]:
        if self.x is None or self.x >= 0:
            return Ok(self.x)
        else:    
            return Err()
        
    def access_x_notnone_exception(self) -> int:
        if self.x is None:
            raise TypeError('x is None so it is invalid')
        elif self.x < 0:
            raise ValueError('x is negative so it is invalid')
        else:
            return self.x

    def access_x_notnone(self) -> Result[int, MyErrorType]:
        if self.x is None:
            return Err(MyErrorType.IS_NONE)
        elif self.x < 0:
            return Err(MyErrorType.IS_NEGATIVE)
        else:
            return Ok(self.x)


def print_values_exception(objs: typing.List[MyObj]) -> None:
    for obj in objs:
        try:
            print(obj.access_x_exception())
        except ValueError:
            print('x is invalid')
    
def print_values(objs: typing.List[MyObj]) -> None:
    for obj in objs:
        result = obj.access_x()
        if result.is_ok:
            print(result.data)
        else:
            print(f'x is invalid: {result.error}')

def average_values_exception(objs: typing.List[MyObj]) -> float:
    values = list()
    for obj in objs:
        try:
            values.append(obj.access_x_notnone_exception())
        except ValueError:
            values.append(0)
        except TypeError:
            pass
    return sum(values)/len(values)

def average_values(objs: typing.List[MyObj]) -> float:
    values = list()
    for obj in objs:
        v = obj.access_x_notnone()
        if v.is_ok:
            values.append(v.data)
        elif v.error is MyErrorType.IS_NEGATIVE:
            values.append(0)
    return sum(values)/len(values)

@dataclasses.dataclass
class MyObjWrapper:
    obj: MyObj
    def access_value(self) -> Result[int, MyErrorType]:
        return self.obj.access_x_notnone()
    
@dataclasses.dataclass
class MySecondWrapper:
    obj_wrapper: MyObjWrapper
    def access_value_wrapper(self) -> int:
        val = self.obj_wrapper.access_value()
        if val.is_ok:
            return val.data
        else:
            raise ValueError('SOMETHING BAD HAPPENED')
    

if __name__ == '__main__':
    k = 100
    test_values = [None]*k*3 + list(range(k))
    
    objs = [MyObj(v) for v in test_values]
    
    print_values_exception(objs)
    print_values(objs)
    print(average_values_exception(objs))
    print(average_values(objs))
    
    
