

import typing
import dataclasses

T = typing.TypeVar("T")

@dataclasses.dataclass
class MyType(typing.Generic[T]):
    x: typing.Optional[T]

    def access_x(self) -> T:
        if self.x is None:
            raise ValueError("x is missing")
        else:
            return self.x # type: ignore
    
    def set_z(self, x: T) -> None:
        self.x = x

MyValue = typing.Union[MyType[T], T]

def convert_to_string(val: MyValue[T]) -> str:
    try:
        return str(val.access_x())
    except AttributeError:
        return str(val)

if __name__ == '__main__':
    
    #a: typing.List[int] = [None, 1, 2, 3]
    
    a: typing.List[typing.Optional[int]] = [None, 1, 2, 3]
    
    a_filtered = [v for v in a if v is not None]
    
    sum(a_filtered)

    b: typing.List[int] = [v for v in a if v is not None]
    sum(b)

    print(MyType(1.0).access_x())
    print(MyType(None).access_x())



