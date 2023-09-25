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
    a: int
    def a_is_missing(self) -> bool:
        return self.a is None
    
    def a_is_not_even(self) -> bool:
        return self.a % 2 != 0

def average_values_check(objs: typing.List[ExDataType1]):
    values = list()
    for obj in objs:
        if obj.a_is_missing():
            pass
        elif obj.a_is_not_even():
            values.append(0)
        else:
            values.append(obj.a)
    return sum(values)/len(values)

######################### option 2: use exceptions #########################

class ValueIsMissing(BaseException):
    pass

class ValueIsNotEven(BaseException):
    pass

@dataclasses.dataclass
class ExDataType2:
    a: int
    def access_a(self):
        if self.a is None:
            raise ValueIsMissing('The data for a is missing.')
        elif self.a % 2 != 0:
            raise ValueIsNotEven('The data for a is missing.')
        else:
            return self.a

def average_values_exc(objs: typing.List[ExDataType2]):
    values = list()
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
class Result:
    data: typing.Any
    status: ResultStatus = ResultStatus.Ok
    
    @classmethod
    def ok(cls, data: typing.Any):
        return cls(data, ResultStatus.Ok)
    
    @classmethod
    def err(cls, data: typing.Any):
        return cls(data, ResultStatus.Err)

class ErrorType(enum.Enum):
    MISSING = enum.auto()
    NOT_EVEN = enum.auto()
    
@dataclasses.dataclass
class ExDataType3a:
    a: int
    def access_a(self) -> Result:
        if self.a is None:
            return Result.err(ErrorType.MISSING)
        elif self.a % 2 != 0:
            return Result.err(ErrorType.NOT_EVEN)
        else:
            return Result.ok(self.a)

def average_values_result1(objs: typing.List[ExDataType3a]):
    values = list()
    for obj in objs:
        result = obj.access_a()
        if result.status is ResultStatus.Ok:
            values.append(result.data)
        elif result.status is ErrorType.NOT_EVEN:
            values.append(0)
        elif result.status is ErrorType.MISSING:
            pass
        
    return sum(values)/len(values)


########################## option 3b: use result object#########################

class ErrorTypeNotHandled(BaseException):
    pass
    
class Result2:
    def handle(self, 
            error_handlers: typing.Dict[enum.Enum, typing.Callable[[Any],Any]],
            okay_func: typing.Callable[[Any],Any] = lambda x: x,
        ) -> typing.Any:
        if self.status is ResultStatus.Ok:
            return okay_func(self.data)
        else:
            try:
                return error_handlers[self.error](**self.error_kwargs)
            except KeyError as e:
                raise ErrorTypeNotHandled(f'Error type {self.error} was not handled') from e

@dataclasses.dataclass
class Ok2(Result2):
    data: typing.Any
    status: ResultStatus = ResultStatus.Ok

@dataclasses.dataclass
class Err2(Result2):
    error: BaseException
    status: ResultStatus = ResultStatus.Err
    
@dataclasses.dataclass
class ExDataType3b:
    a: int
    def access_a(self) -> Result2:
        if self.a is None:
            return Err2(ErrorType.MISSING)
        elif self.a % 2 != 0:
            return Err2(ErrorType.NOT_EVEN)
        else:
            return Ok2(self.a)

def average_values_result2(objs: typing.List[ExDataType3b]):
    values = list()
    for obj in objs:
        result = obj.access_a()
        if result.status is ResultStatus.Ok:
            values.append(result.data)
        else:
            if result.error is ErrorType.NOT_EVEN:
                values.append(0)
            else:
                pass
        
    return sum(values)/len(values)


########################## option 3c: use result object#########################
    
class Result3:
    pass
    
@dataclasses.dataclass
class Ok3(Result3):
    data: typing.Any

@dataclasses.dataclass
class Err3(Result3):
    error: BaseException
    
@dataclasses.dataclass
class ExDataType3c:
    a: int
    def access_a(self) -> Result3:
        if self.a is None:
            return Err3(ErrorType.MISSING)
        elif self.a % 2 != 0:
            return Err3(ErrorType.MISSING)
        else:
            return Ok3(self.a)

def average_values_result3(objs: typing.List[ExDataType3c]):
    values = list()
    for obj in objs:
        result = obj.access_a()
        if isinstance(result, Ok3):
            values.append(result.data)
        else:
            if result.error is ErrorType.NOT_EVEN:
                values.append(0)
            elif result.error is ErrorType.MISSING:
                pass
        
    return sum(values)/len(values)


########################## option 3b: use result object#########################
    
class Result4:
    pass

@dataclasses.dataclass
class Ok4(Result4):
    data: typing.Any
    is_ok: bool = True

@dataclasses.dataclass
class Err4(Result4):
    error: BaseException
    is_ok: bool = False
    
@dataclasses.dataclass
class ExDataType3d:
    a: int
    def access_a(self) -> Result2:
        if self.a is None:
            return Err4(ErrorType.MISSING)
        elif self.a % 2 != 0:
            return Err4(ErrorType.NOT_EVEN)
        else:
            return Ok4(self.a)

def average_values_result4(objs: typing.List[ExDataType3d]):
    values = list()
    for obj in objs:
        result = obj.access_a()
        if result.is_ok:
            values.append(result.data)
        elif result.error is ErrorType.NOT_EVEN:
            values.append(0)
        else:
            pass
    
    return sum(values)/len(values)





class Profiler:
    def __init__(self, fname: str):
        self.pr = cProfile.Profile()
        self.fname = fname
        
    def __enter__(self):
        self.pr.enable()
        return self
    
    def __exit__(self, *args):
        self.pr.disable()
        r = pstats.Stats(self.pr)
        r.sort_stats(pstats.SortKey.TIME)
        r.dump_stats(self.fname)


if __name__ == '__main__':
    k = 100000
    test_values = [None]*k*3 + list(range(k))
    
    objs = [ExDataType1(v) for v in test_values]
    #with Profiler(f'prof_check.prof'):
    average_values_check(objs)

    objs = [ExDataType2(v) for v in test_values]
    #with Profiler(f'prof_exc.prof'):
    average_values_exc(objs)

    objs = [ExDataType3a(v) for v in test_values]
    #with Profiler('prof_status.prof'):
    average_values_result1(objs)

    objs = [ExDataType3b(v) for v in test_values]
    #with Profiler('prof_status.prof'):
    average_values_result2(objs)

    objs = [ExDataType3c(v) for v in test_values]
    #with Profiler('prof_status.prof'):
    average_values_result3(objs)

    objs = [ExDataType3d(v) for v in test_values]
    #with Profiler('prof_status.prof'):
    average_values_result4(objs)
