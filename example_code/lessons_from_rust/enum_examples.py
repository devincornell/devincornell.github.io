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
class Valid(typing.Generic[T]):
    data: T
    is_ok: bool = True
    
    @property
    def error(self) -> typing.NoReturn:
        raise AttributeError(f'{self.__class__.__name__} has no attribute "error"')
    
@dataclasses.dataclass
class Invalid(typing.Generic[E]):
    error: typing.Optional[E] = None
    is_ok: bool = False
    
    @property
    def data(self) -> typing.NoReturn:
        raise AttributeError(f'{self.__class__.__name__} has no attribute "data"')
    
ValidOrInvalid = typing.Union[Valid[T],  Invalid[E]]

class InvalidErrorType(enum.Enum):
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
    
    def access_x(self) -> ValidOrInvalid[typing.Optional[int], None]:
        if self.x is None or self.x >= 0:
            return Valid(self.x)
        else:    
            return Invalid()
        
    def access_x_notnone_exception(self) -> int:
        if self.x is None:
            raise TypeError('x is None so it is invalid')
        elif self.x < 0:
            raise ValueError('x is negative so it is invalid')
        else:
            return self.x

    def access_x_notnone(self) -> ValidOrInvalid[int, InvalidErrorType]:
        if self.x is None:
            return Invalid(InvalidErrorType.IS_NONE)
        elif self.x < 0:
            return Invalid(InvalidErrorType.IS_NEGATIVE)
        else:
            return Valid(self.x)


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
        elif v.error is InvalidErrorType.IS_NEGATIVE:
            values.append(0)
    return sum(values)/len(values)

@dataclasses.dataclass
class MyObjWrapper:
    obj: MyObj
    def access_value(self) -> ValidOrInvalid[int, InvalidErrorType]:
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
    
@dataclasses.dataclass
class Ok(typing.Generic[T]):
    data: T
    status: ResultStatus = ResultStatus.Ok

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



    

if __name__ == '__main__':
    k = 100
    test_values = [None]*k*3 + list(range(k))
    
    objs1 = [ExDataType1(v) for v in test_values]
    #with Profiler(f'prof_check.prof'):
    u = average_values_check(objs1)
    print(u)
    
    objs2 = [ExDataType2(v) for v in test_values]
    #with Profiler(f'prof_exc.prof'):
    u = average_values_exc(objs2)
    print(u)
    
    
    
