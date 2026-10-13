from __future__ import annotations


from dataclasses import dataclass
from typing import Iterable, Self, NewType
from collections import UserList, UserDict

@dataclass(slots=True, frozen=True)
class MyType:
    value: int

class ImmutableMyTypeList(tuple[MyType, ...]):
    @classmethod
    def from_values(cls, values: Iterable[int]) -> Self:
        return cls(MyType(value=v) for v in values)
    def mean(self) -> float:
        if not self:
            raise ValueError("Cannot compute mean of an empty ImmutableMyTypeList.")
        return sum(item.value for item in self) / len(self)

MyTypeName = NewType("MyTypeName", str)

class MyTypeDict(UserDict[MyTypeName, MyType]):
    @classmethod
    def from_values(cls, values: dict[str, int]) -> Self:
        return cls({MyTypeName(k): MyType(value=v) for k, v in values.items()})

ImmutableMyTypeList.from_values([4, 5, 6]).mean()
MyTypeDict.from_values({"a": 7, "b": 8, "c": 9})


@dataclass(slots=True, frozen=True)
class AnotherType:
    values: tuple[MyType, ...]
    @classmethod
    def from_values(cls, values: Iterable[int]) -> Self:
        return cls(values=tuple(MyType(value=v) for v in values))


