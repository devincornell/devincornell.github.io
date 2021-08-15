---
title: "Distributed Processing in Python using _multiprocessing_"
subtitle: "Considerations for constructing custom systems."
date: "Aug 15, 2021"
id: "distributed_processing_using_multiprocessing"
---



Here I'll talk about some factors to consider when creating any distributed processing system using Python's [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) package.


These are some of the major considerations:

1. Contexts and starting methods: i.e. _spawn_ vs _fork_

2. Inter-process communication - _Pipe_ VS _Queue_

3. Exception handling across processes


## Contexts and process starting methods

The [multiprocessing documentation](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods) details the three methods that Python can use to start processes: _spawn_, _fork_, and _forkserver_. 
I will focus on _spawn_ and _fork_ because they appear to be the most popular. 
I quoted the official docs and added some additional considerations based on my research.

#### _fork_

> From [docs](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods): _The parent process uses os.fork() to fork the Python interpreter. 
> The child process, when it begins, is effectively identical to the parent process. 
> All resources of the parent are inherited by the child process. Note that safely forking a multithreaded process is problematic. 
> Available on Unix only. The default on Unix.

As the docs note, 


#### _spawn_

From [docs](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods): "The parent process starts a fresh python interpreter process. The child process will only inherit those resources necessary to run the process object’s run() method. In particular, unnecessary file descriptors and handles from the parent process will not be inherited. Starting a process using this method is rather slow compared to using fork or forkserver."

This method is the default on Windows and Mac





