import dataclasses
import typing
import enum
from typing import Any
import timeit
import cProfile
import pstats

########################## option 1: baseline - check flag before using #########################
@dataclasses.dataclass
class ExDataType1:
    a: typing.Optional[int]
    def access_a(self) -> int:
        return self.a # type: ignore
    
    def a_is_missing(self) -> bool:
        return self.a is None
    
    def a_is_not_even(self) -> bool:
        return self.a % 2 != 0 # type: ignore
    
def average_values_check(objs: typing.List[ExDataType1]):
    values: typing.List[int] = list()
    for obj in objs:
        if obj.a_is_missing():
            pass
        elif obj.a_is_not_even():
            values.append(0)
        else:
            values.append(obj.access_a())
    return sum(values)/len(values)


######################### option 2: use exceptions #########################

class ValueIsMissing(BaseException):
    pass

class ValueIsNotEven(BaseException):
    pass

@dataclasses.dataclass
class ExDataType2:
    a: typing.Optional[int]
    def access_a(self) -> int:
        if self.a is None:
            raise ValueIsMissing('The data for a is missing.')
        elif self.a % 2 != 0: # typing: ignore
            raise ValueIsNotEven('The data for a is missing.')
        else:
            return self.a

def average_values_exc(objs: typing.List[ExDataType2]) -> float:
    values: typing.List[int] = list()
    for obj in objs:
        try:
            values.append(obj.access_a())
        except ValueIsMissing:
            pass
        except ValueIsNotEven:
            values.append(0)
    return sum(values)/len(values)

########################## option 3a: use result object#########################

class ResultStatus(enum.Enum):
    Ok = enum.auto()
    Err = enum.auto()
    
T = typing.TypeVar("T")
@dataclasses.dataclass
class Ok(typing.Generic[T]):
    data: T
    status: ResultStatus = ResultStatus.Ok

E = typing.TypeVar("E")
@dataclasses.dataclass
class Err(typing.Generic[E]):
    error: E
    status: ResultStatus = ResultStatus.Err

Result = typing.Union[Ok[T],  Err[E]]
    
class ErrorType(enum.Enum):
    MISSING = enum.auto()
    NOT_EVEN = enum.auto()
    
@dataclasses.dataclass
class ExDataType3:
    a: typing.Optional[int]
    def access_a(self) -> Result:
        if self.a is None:
            return Err(ErrorType.MISSING)
        elif self.a % 2 != 0:
            return Err(ErrorType.NOT_EVEN)
        else:
            return Ok(self.a)

def average_values_result(objs: typing.List[ExDataType3]):
    values = list()
    for obj in objs:
        result = obj.access_a()
        if result.status is ResultStatus.Ok:
            values.append(result.data) # type: ignore
        else:
            if result.error is ErrorType.NOT_EVEN: # type: ignore
                values.append(0)
            else:
                pass
        
    return sum(values)/len(values)


########################## option 3b: use result object #########################

@dataclasses.dataclass
class Ok2(typing.Generic[T]):
    data: T
    is_ok: bool = True
    
@dataclasses.dataclass
class Err2(typing.Generic[E]):
    error: E
    is_ok: bool = False
    


if __name__ == '__main__':
    k = 100000
    test_values = [None]*k*3 + list(range(k))
    
    objs1 = [ExDataType1(v) for v in test_values]
    #with Profiler(f'prof_check.prof'):
    u = average_values_check(objs1)
    print(u)
    
    objs2 = [ExDataType2(v) for v in test_values]
    #with Profiler(f'prof_exc.prof'):
    u = average_values_exc(objs2)
    print(u)
