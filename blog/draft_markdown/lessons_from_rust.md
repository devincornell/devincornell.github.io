---
title: "Lessons from the Rust Language"
subtitle: "Patterns and concepts we can use to improve our data pipelines in any language."
date: "Sept 26, 2023"
id: "lessons_from_rust"
---

The Rust programming language has taken the award for "most loved programming language" in the [Stack Overflow Developer Survey](https://survey.stackoverflow.co/2022#overview) since 2016. The power of Rust comes in that it is nearly as fast as C++ without the potential issues that come with pointers and manual memory management. This advantage comes as much from what the languages allows you to do as what it restricts you from doing, and we can learn much from understanding the design of the language. Whether or not you can convince your stakeholders or company to allow you to write your data pipelines in Rust, there are some lessons we can learn from Rust that we can apply to our data pipelines in any language. 

In this article, I will describe some patterns for Python code that mimic the features and, perhaps more importantly, the restrictions built into the language that improve safety and readability.

## 1. Immutability

By default, variables in Rust are are immutable - that is, once you assign a value to a variable, you cannot change it. You must manually specify that a variable is mutable if you want to be able to change it later, and thus you should be thinking of variables as immutable unless otherwise specified. 

I wrote about the benefits of immutability in [a previous article](/post/dsp0_patterns_for_dataclasses.html), but in general I recommend transforming data from one type to another instead of modifying it in-place. This makes it easier to debug and generally reason about your code.

## 2. Stronger Typing


## 3. Ownership


## 4. Enums for Errors and Missing Data


## 5. Use Composition over Inheritance and Generally Avoid OOP Practices




## Conclusions
