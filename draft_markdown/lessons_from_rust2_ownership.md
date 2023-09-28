---
title: "Lessons from Rust 3: Ownership and Scope"
subtitle: "Use the ownership pattern from Rust to increase_safety."
date: "Sept 27, 2023"
id: "lessons_from_rust3_ownership"
---

The key to memory safety in Rust comes from a concept called _ownership_. As an example, it is common practice to allocate a piece of heap memory (e.g. list or vector) at the top level of your program and then pass a reference or pointer into a function that will use or modify it. In languages such as Python or C++, you can continue to use that allocated memory after the function has returned, and either you must remember to free the memory manually or let the garbage collector take care of it after it is no longer needed.

Rust adds the restriction that only one scope can _own_ a variable, so by passing a mutable variable into the function you are actually transferring ownership to it - you cannot continue to access that memory from outside the function. You can, however, return ownership to the outer scope by returning the reference. This makes it clear to the reader that you are, in fact modifying some of the data being passed into the function.

While we cannot place this restriction into our Python code explicitly, we can force ourselves to use patterns consistent with the ownership concept. As a first example, let us say that you have a list and you want to write a function that counts the number of even elements in the list. Let us say that you want to keep track of this information in a custom counter object that simply records the count.

    from __future__ import annotations
    import typing

    class MyCounter:
        def __init__(self):
            self.count = 0
        
        def increment(self):
            self.count += 1
            
        def combine(self, other: MyCounter):
            self.count += other.count

One solution to this problem is to write a function that accepts a counter and simply increments it within the function, allowing you to use it afterwards. The advantage of this approach is that it is memory efficient - you only need to maintain a single counter in memory in your program at a time. The downside is that the reader cannot tell that the counter will be modified within the function - the reader can only see that by looking into the function.

    def count_even_inplace(values: typing.List[int], ctr: MyCounter) -> None:
        for v in values:
            if v % 2 == 0:
                ctr.increment()

You can still access the updated data in the outer scope using the same variable name.

    mylist1 = list(range(10))
    ctr1 = MyCounter()
    count_even_inplace(mylist1, ctr1)

An alternative would be to write a more "pure" function - that is, a function with no side effects. One could do this by accepting only a list and returning a new counter that would need to be merged back into the original counter. This is a more functional approach, but it is less memory efficient because you need to maintain two counters in memory at the same time. The upside is that there are no side-effects - no objects are being modified in-place.

    def count_even_newctr(values: typing.List[int]) -> MyCounter:
        ctr = MyCounter()
        for v in values:
            if v % 2 == 0:
                ctr.increment()
        return ctr

Assuming you have an existing counter, you simply call the function on the list and then combine the returned counter with the existing one to be used downstream.

    ctr1 = MyCounter()
    ctr2 = count_even_newctr(mylist1)
    ctr1.count += ctr2.count

An alternative approach that follows the ownership model would be to accept and modify the existing counter, but return ownership by returning a reference to the same modified counter.This combines some of the advantages of both: it makes it clear that the counter is being modified but does not need to create a copy of the counter. There is essentially no side-effect because you are returning a reference to the same object.

def count_even_transfer_ownership(values: typing.List[int], ctr: MyCounter) -> MyCounter:
    for v in values:
        if v % 2 == 0:
            ctr.increment()
    return ctr

To use this function, you would modify an existing counter in-place, and re-assign the reference to the modified counter to a variable with the same name. 

    ctr1 = MyCounter()
    ctr1 = count_even_transfer_ownership(mylist1, ctr1)

To further drive home this point, imagine we want to create a function that returns a list with zero values removed. The memory-efficient approach that decreases readability would be to modify the list in-place and return nothing.

    def remove_zeroes_inplace(values: typing.List[int]) -> typing.List[int]:
        while True:
            try:
                values.remove(0)
            except ValueError:
                break

The more "pure" and readable approach would be to return a new list with the zeroes removed.

    def remove_zeroes_newlist(values: typing.List[int]) -> typing.List[int]:
        return [v for v in values if v != 0]

And the solution using the ownership model would be to modify the existing list in-place and return a reference to the same list that would be used in the outer scope.

    def remove_zeroes_transfer_ownership(values: typing.List[int]) -> typing.List[int]:
        while True:
            try:
                values.remove(0)
            except ValueError:
                break
        return values

Rust has even more complicated rules for ownership that allow for memory safety, but these examples simply show patterns .


