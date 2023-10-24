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
    
    # ================= NEWER EXAMPLES =================    
    
    import enum
    class MissingValueType(enum.Enum):
        MISSING = enum.auto()
        def __repr__(self):
            return "MISSING"

    MISSING = MissingValueType.MISSING
    '''Represents a missing Value.'''

    ValueOrMissing = typing.Union[T, MissingValueType]

    def get_correct_option(
        default_a: typing.Optional[int] = None,
        default_b: typing.Optional[int] = None,
    ) -> int:
        '''Multiplies x and y if do_square is True.'''
        if default_a is not None and default_b is not None:
            raise ValueError('default_a and default_b cannot both be set')
        elif default_a is not None:
            return default_a
        elif default_b is not None:
            return default_b
        else:
            raise ValueError('default_a or default_b must be set')

    def get_correct_option(
        default_a: typing.Optional[int] = MISSING,
        default_b: typing.Optional[int] = MISSING,
    ) -> typing.Optional[int]:
        pass
        

    def get_correct_option(
        default_a: ValueOrMissing[typing.Optional[int]] = MISSING,
        default_b: ValueOrMissing[typing.Optional[int]] = MISSING,
    ) -> typing.Optional[int]:
        '''Multiplies x and y if do_square is True.'''
        if default_a is not MISSING and default_b is not MISSING:
            raise ValueError('default_a and default_b cannot both be set')
        elif default_a is not MISSING:
            return default_a
        elif default_b is not MISSING:
            return default_b
        else:
            raise ValueError('default_a or default_b must be set')



    
    # ================= OLDER EXAMPLES =================
    
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


