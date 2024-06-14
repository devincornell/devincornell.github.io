---
title: "Better Exceptions Using Static Factory Methods"
subtitle: "Tips for building clean data objects using the dataclasses module."
date: "August 25, 2023"
id: "dsp0_patterns_for_dataclasses"
blogroll_img_url: "https://storage.googleapis.com/public_data_09324832787/dataclasses.svg"
---

I was recently watching an [ArjanCodes Video](https://www.youtube.com/watch?v=ebZB8dPrrog) about [writing Custom Exception Types](https://www.youtube.com/watch?v=ebZB8dPrrog) and felt like the suggested approaches, which both involve overriding `__init__`. I find these approaches to be relatively common in public Python packages, but I believe they greatly limit the flexibility that custom exception types offer. Instead, I recommend creating custom exception types with factory constructor methods that 



![MY IMATE.](https://storage.googleapis.com/public_data_09324832787/dataclasses.svg)
