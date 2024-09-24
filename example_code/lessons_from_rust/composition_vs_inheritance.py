from __future__ import annotations
import typing
import dataclasses

class BaseResult:
    def summary_stats(self) -> typing.Dict[str, float]:
        return {
            'mean': self.mean(),
            'variance': self.variance()
        }
    
    def variance(self) -> float:
        raise NotImplementedError()
    
    def mean(self) -> float:
        return sum(self.numbers)/len(self.numbers)

@dataclasses.dataclass
class SimpleResultInherited(BaseResult):
    numbers: typing.List[float]
        
    def variance(self):
        u = self.mean()
        return sum([(r - u)**2 for r in self.numbers])/len(self.numbers)

@dataclasses.dataclass
class ComplexResultInherited(BaseResult):
    numbers: typing.List[float]
    offset: float
    
    def summary_stats(self) -> typing.Dict[str, float]:
        return {
            **super().summary_stats(),
            'median': self.median(),
        }
            
    def variance(self) -> float:
        u = self.mean()
        return sum([(r - u)**2 for r in self.numbers])/len(self.numbers)
    
    def mean(self) -> float:
        return super().mean() + self.offset
    
    def median(self) -> float:
        return sorted(self.numbers)[len(self.numbers)//2] + self.offset

    
    
@dataclasses.dataclass
class NumberContainer:
    numbers: typing.List[float]
    
    def __len__(self) -> int:
        return len(self.numbers)
    
    def mean(self, offset: float) -> float:
        return sum(self.numbers)/len(self.numbers) + offset
    
    def variance(self, offset: float) -> float:
        u = self.mean(offset=offset)
        return sum([(r - u)**2 for r in self.numbers])/len(self.numbers)

    def median(self, offset: float) -> float:
        return sorted(self.numbers)[len(self.numbers)//2] + offset

@dataclasses.dataclass
class SimpleResult:
    results: NumberContainer
    
    @classmethod
    def from_list(cls, numbers: typing.List[float]):
        return cls(NumberContainer(numbers))
    
    def summary_stats(self) -> typing.Dict[str, float]:
        return {
            'mean': self.mean(),
            'variance': self.variance()
        }
    
    def variance(self) -> float:
        return self.results.variance(offset=0)
    
    def mean(self) -> float:
        return self.results.mean(offset=0)
        
@dataclasses.dataclass
class ComplexResult:
    results: NumberContainer
    offset: float
    
    @classmethod
    def from_list(cls, numbers: typing.List[float], offset: float):
        return cls(NumberContainer(numbers), offset)
    
    def summary_stats(self) -> typing.Dict[str, float]:
        return {
            'mean': self.mean(),
            'variance': self.variance(),
            'median': self.median(),
        }
    
    def mean(self) -> float:
        return self.results.mean(offset=self.offset)
    
    def variance(self) -> float:
        return self.results.variance(offset=self.offset)
    
    def median(self) -> float:
        return self.results.median(offset=self.offset)


if __name__ == '__main__':
    mylist1 = list(range(10))
    sri = SimpleResultInherited(mylist1)
    print(sri.summary_stats())
    
    cri = ComplexResultInherited(mylist1, 1.0)
    print(cri.summary_stats())
    
    si = SimpleResult.from_list(mylist1)
    print(si.summary_stats())
    
    ci = ComplexResult.from_list(mylist1, 1.0)
    print(ci.summary_stats())
    
    



    