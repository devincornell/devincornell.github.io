---
title: "Distributed Processing in Python using `multiprocessing`"
subtitle: "Considerations for constructing custom systems."
date: "Aug 15, 2021"
id: "distributed_processing_using_multiprocessing"
---



Here I'll talk about some factors to consider when creating any distributed processing system using Python's [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) package.


These are some of the major considerations:

1. Contexts and starting methods: i.e. _spawn_ vs _fork_

2. Inter-process communication - _Pipe_s VS _Queue_s

3. Exception handling across processes


## Contexts and process starting methods

The [multiprocessing documentation](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods) details the three methods that Python can use to start processes: _spawn_, _fork_, and _forkserver_. 
I will focus on _spawn_ and _fork_ because they appear to be the most popular. 
I quoted the official docs and added some additional considerations based on my research.

+ _spawn_: "The parent process starts a fresh python interpreter process. The child process will only inherit those resources necessary to run the process object’s run() method. In particular, unnecessary file descriptors and handles from the parent process will not be inherited. Starting a process using this method is rather slow compared to using fork or forkserver."




