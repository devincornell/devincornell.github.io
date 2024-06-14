---
title: "Introduction to Static Factory Methods"
subtitle: "A brief overview of methods used to initialize custom types."
date: "June 14, 2024"
id: "intro_to_static_factory_methods"
blogroll_img_url: "https://storage.googleapis.com/public_data_09324832787/dataclasses.svg"
---

Over the last two decades we've seen a shift towards programming patterns that place data first. Many classical design patterns have fallen out of favor as the popularity of languages with [first-class functions](https://en.wikipedia.org/wiki/First-class_function) has risen, and the recent explosion of interest in data analysis means that young programmers are being trained to think of objects as containers for data rather than maintainers of system state. In Python, the popular [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module (a successor of [Pydantic](https://docs.pydantic.dev/latest/) and [attrs](https://www.attrs.org/en/stable/)) has gotten a lot of attention because it makes it easy to create data-specific classes by simply listing a set of attribute names and their types.


The popular [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module has been pushing many data scientists to adopt more object-oriented patterns in their data pipelines since it was [introduced](https://www.google.com/search?client=firefox-b-1-d&q=dataclasses+pep) to the Python standard library. This module makes it easy to create data types by offering a decorator that automatically generates `__init__` and a number of other boilerplate dunder methods from only a set of statically defined attributes with type hints (I recommend [this tutorial](https://realpython.com/python-data-classes/)). Previously I have written about [object-oriented alternatives to dataframes](/post/zods0_problem_with_dataframes.html) for data science, and in this article I wanted to share a few patterns I use for data objects created with `dataclasses` in my own work.





![MY IMATE.](https://storage.googleapis.com/public_data_09324832787/dataclasses.svg)
