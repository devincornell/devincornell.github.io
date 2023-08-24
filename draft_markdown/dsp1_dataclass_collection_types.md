---
title: "Patterns for Dataclass Collection Types"
subtitle: "Patterns for creating collections of dataclass (or data-oriented type) objects."
date: "August 24, 2023"
id: "dsp1_dataclass_collections"
---



## Two Approaches

In Python, there are two primary ways to create collection types: (1) extend an existing collection type such as Dict, List, or Set, or (2) encapsulate a collection in another custom type. The former is best for simple cases, where the latter is best for more complex use-cases.

### Extending Existing Types

To extend an existing type in Python, you will probably want to use the `typing` module instead of `list`, `dict`, or `set` directly.

    import typing

    class MyCollection(typing.List):
        pass



