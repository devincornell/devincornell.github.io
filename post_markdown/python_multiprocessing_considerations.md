---
title: "Distributed Processing in Python using multiprocessing"
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

I found a good comparison of _fork_ and _spawn_ on a [StackOverflow page](https://stackoverflow.com/questions/64095876/multiprocessing-fork-vs-spawn). 
The responses indicate that overall, _fork_ is fastest because it simply copies the entire python process, along with any information stored globally 


#### _fork_

> [docs](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods): The parent process uses os.fork() to fork the Python interpreter. 
> The child process, when it begins, is effectively identical to the parent process. 
> All resources of the parent are inherited by the child process. Note that safely forking a multithreaded process is problematic. 
> Available on Unix only. The default on Unix.

This [StackOverflow page](https://stackoverflow.com/questions/64095876/multiprocessing-fork-vs-spawn) suggests that _fork_ is default for POSIX systems because it is very fast and uses the kernel to manage memory copying efficiently. 
When creating a forked process, your OS essentially copies the entire process, including global variables, file handles, and any other connection resources (e.g. database connections) associated with the original process. 

The biggest challenge with this method is the way it manages memory.
The copy-on-write method used by the OS means that memory pages are only copied when they are modified. 
In theory this appears to be quite efficient - two processes can use the same memory as long as they don't modify it. 
Note that this is not the same as shared memory implemented in Python or by your application, but rather a kernel-level implementation of virtual memory paging (as I understand it).
This would be fine for programs implemented closer to hardware, but in Python memory writes are less predictable - they can even happen simply by iterating over a set of data (for instance, a global variable). 
In general, accessing a global variable from a thread/process target function would be a bad idea, but either way this could cause some unexpected behavior.

In fact, [some have suggested](https://bugs.python.org/issue40379) that _fork_ be replaced by _spawn_ as the default process spawning method on Unix systems because they can cause thread lockups that are difficult for many people to debug ([this blog post](https://pythonspeed.com/articles/python-multiprocessing/) gives more detial). 


More specifically, the OS applies a  

The responses indicate that overall, _fork_ is fastest because it simply copies the entire python process, along with any information stored globally 

#### _spawn_

From [docs](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods): "The parent process starts a fresh python interpreter process. The child process will only inherit those resources necessary to run the process object’s run() method. In particular, unnecessary file descriptors and handles from the parent process will not be inherited. Starting a process using this method is rather slow compared to using fork or forkserver."

This method is the default on Windows and Mac





