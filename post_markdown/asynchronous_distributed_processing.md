---
title: "Building Asynchronous Distributed Processing Systems"
subtitle: "Strategies for "
date: "June 15, 2021"
id: "asynchronous_distributed_processing_systems"
---

Here I'll talk about some code I wrote for doctable.

_Motivation_: I wanted to create a parallel processing interface that is suited for situations where (1) there is large variance in the time it takes to complete each subtask, (2) the time to complete each subtask cannot be estimated prior to execution, and (3) the memory overhead required to complete each subtask is such that each process cannot maintain data for multiple tasks at once. 

To the latter point, the common 

parallel processing separate (embarrassingly parallel) 


1. assertion in main block - tell threads to die

2. assertion in thread function - tell main process to die, raise exception


EOFError

