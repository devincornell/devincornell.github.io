---
title: "Software Engineering for Data Science"
subtitle: "Change the way you initialize custom types in Python."
date: "June 14, 2024"
id: "intro_to_static_factory_constructor_methods"
blogroll_img_url: "https://storage.googleapis.com/public_data_09324832787/sfcm_data_flow.svg"
---


To help us think about the role these patterns play within a data science project, start by thinking of code in terms of data flow. While it may be more or less explicit in the code itself, all data science projects can essentially be reduced to a set of data types and the transformations required to convert between them. While the source types can take nearly any format, the result data type is often a figure, table, or some other piece of format that can be interpreted by a human. 


To help us think about the role these patterns play within a data science project, start by thinking of code in terms of data flow. While it may be more or less explicit in the code itself, all data science projects can essentially be reduced to a set of data types and the transformations required to convert between them. While the source types can take nearly any format, the result data type is often a figure, table, or some other piece of format that can be interpreted by a human. 


![Data flow control diagram.](https://storage.googleapis.com/public_data_09324832787/sfcm_data_flow.svg)

Design patterns have the power to make the flow of this data more explicit, extensible, and reliable, allowing you to adapt to project changes and reducing the risk of errors as you do it. 

Design patterns have the power to make the flow of this data more explicit, extensible, and reliable, allowing you to adapt to project changes and reducing the risk of errors as you do it. 
