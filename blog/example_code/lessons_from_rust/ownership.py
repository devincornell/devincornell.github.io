from __future__ import annotations
import typing

class MyCounter:
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1
        
    def combine(self, other: MyCounter):
        self.count += other.count
        
def count_even_inplace(values: typing.List[int], ctr: MyCounter) -> None:
    for v in values:
        if v % 2 == 0:
            ctr.increment()

def count_even_newctr(values: typing.List[int]) -> MyCounter:
    ctr = MyCounter()
    for v in values:
        if v % 2 == 0:
            ctr.increment()
    return ctr

def count_even_transfer_ownership(values: typing.List[int], ctr: MyCounter) -> MyCounter:
    for v in values:
        if v % 2 == 0:
            ctr.increment()
    return ctr
            
def remove_zeroes_inplace(values: typing.List[int]) -> None:
    while True:
        try:
            values.remove(0)
        except ValueError:
            break

def remove_zeroes_newlist(values: typing.List[int]) -> typing.List[int]:
    return [v for v in values if v != 0]

def remove_zeroes_transfer_ownership(values: typing.List[int]) -> typing.List[int]:
    while True:
        try:
            values.remove(0)
        except ValueError:
            break
    return values



import dataclasses

if __name__ == '__main__':
    mylist1 = list(range(10))
    ctr1 = MyCounter()
    count_even_inplace(mylist1, ctr1)
    print(ctr1.count)
    
    ctr1 = MyCounter()
    ctr2 = count_even_newctr(mylist1)
    ctr1.count += ctr2.count
    print(ctr1.count)
    
    ctr1 = MyCounter()
    ctr1 = count_even_transfer_ownership(mylist1, ctr1)
    print(ctr1.count)

    mylist1 = list(range(5))
    remove_zeroes_inplace(mylist1)
    print(len(mylist1))
    


    