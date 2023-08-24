---
title: "Patterns and Antipatterns for Dataclasses"
subtitle: "Tips for building clean data objects using the dataclasses module."
date: "August 24, 2023"
id: "dsp0_patterns_for_dataclasses"
---

Since [introduction](https://www.google.com/search?client=firefox-b-1-d&q=dataclasses+pep) to the Python standard library, the [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module has been pushing many data scientists to adopt more object-oriented patterns in their pipelines. This module makes it easy to create data types by offering a decorator that automatically generates `__init__` and a number of other boilerplate dunder methods you would be writing for classes primarily intended to store data. While the module offers great flexibility, not all options 




