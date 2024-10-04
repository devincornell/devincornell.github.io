---
title: "Investing in AI-enabled Data Infrastructure"
subtitle: "Re-think how we invest in data infrastructure by separating the LLM technology from the data interfaces and resources they can access."
date: "October 2, 2024"
id: "investing_in_data_infrastructure"
blogroll_img_url: "https://storage.googleapis.com/public_data_09324832787/ai_data_infrastructure/plug_and_play_tools.svg"
---

What does it mean to invest in data infrastructure to support Large Language Models (LLMs) and other AI tools? A [recent report from MIT Technology Review](https://www.technologyreview.com/2023/07/18/1076423/the-great-acceleration-cio-perspectives-on-generative-ai/) suggests that AI-enabled data infrastructure should be “flexible, scalable, and efficient.” The LLM technologies are improving and changing quickly, but the foundational building blocks have remained consistent and will likely remain consistent for the foreseeable future. Investment in new data infrastructure should focus on coordinating data interfaces to make various data and service resources available to any new LLM technology. 

There are many ways to integrate data systems into everyday work with LLMs. One possibility is that users can explicitly execute no-code data queries and run models from the chat interfaces, replacing effort to create time-intensive data data dashboards or analysis reports. Another approach would be for data analysis to happen behind the scenes, to guide the execution of other tasks such as generating evaluation strategies or proposals for new initiatives. The data here could range from summary statistics to recommender algorithms, but either way the user can focus more on the substantive aspects of their work which is informed by data at every step.

<img style="width:100%;" class="figure-center" src="https://storage.googleapis.com/public_data_09324832787/ai_data_infrastructure/llm_data_infrastructure.svg" /> 

We can start to identify opportunities for investment by thinking of data infrastructure in three parts. The first part, on the right in the figure below, is data and other computational resources. This part contains a combination of structured and unstructured data or external services. On the other end, we have the LLM, which will act as the user interface through which we can retrieve and manipulate data. Finally, we have the data interface, which connects the user interface and the data resources. This interface can take many forms - it can be “thin”, giving the LLM direct access to source technologies, or it can be “thick”, involving complicated ETL pipelines or entirely new ways of interacting with the underlying data. While the LLM may be swapped out and the data sources may vary widely, the primary focus of investment should be on data interfaces, and that will be the primary focus of this article.

Now I will give some background on how LLMs access data interfaces and show how we can connect and disconnect data interfaces dynamically.

## Access to Data Interfaces

LLMs are able to access data interfaces using a feature called _[function calling]_(https://platform.openai.com/docs/guides/function-calling). Support for function calling varies by LLM, but most modern models have some variation of this feature. It allows users to define a set of parameterized functions which the LLMs have access to, where definitions include textual descriptions of both the function and parameters (see [technical details](https://python.langchain.com/v0.1/docs/modules/tools/) in a popular Python package). Depending on the user’s query, the LLM may then “decide” to request that a function be executed and supply parameter values based on the conversation history. The supporting technology surrounding the LLM can take this output and execute the associated operation, returning the result back to the chat history so the LLM can either show the result to the user or even execute more operations.


<img style="width:80%;" class="figure-center" src="https://storage.googleapis.com/public_data_09324832787/ai_data_infrastructure/llm_supporting_technology.svg" /> 


The LLM is made aware of available functions every time it is asked for a response, but most supporting technologies have ways of storing available functions so they are automatically sent to the LLM every time it is accessed - this happens on Chat GPT, for instance, when users create Custom GPTs. In general, the available functions can be added or removed at any point in a conversation - or, if the supporting technology allows, even added or removed as an effect of another tool call. 

## Orchestrating Data Resources as Packages

At a higher level, we can think of a data interface as a group of functions that are associated with the same resource. For instance, imagine we had a database and we wanted to allow users to do exactly three things with it: insert an element, retrieve an element, and list all elements. The data interface for that resource would include a function call for each of these operations. Because there is no theoretical limit to the number of functions available to the LLM, it is possible to add other resources, each with their own set of available functions.


<img style="width:90%;" class="figure-center" src="https://storage.googleapis.com/public_data_09324832787/ai_data_infrastructure/resources_and_functions.svg" /> 

The beauty of this is that the LLM and resources are independent - one LLM can be swapped out for another, and resources can be added or removed or upgraded as needed. Because of this independence, it makes sense to think of the LLM as a system with many sockets into which we can insert new services or data resources via the data interfaces. The size and shape of the plugs are the data interfaces, which will necessarily be different for every data resource.


<img style="width:90%;" class="figure-center" src="https://storage.googleapis.com/public_data_09324832787/ai_data_infrastructure/plug_and_play_tools.svg" /> 


An orchestration layer should be able to manage a repository of these resources with different data interfaces. Imagine a system where each resource is a kind of “package” that can be versioned and added or removed from a given chat interface at any point. Investment in data infrastructure, then, is less about the actual AI technology and more about supporting the orchestration of data interfaces and resources they connect.

## Existing Data Interface Technologies
The important thing to note is that the fundamental technologies behind this are not new - in fact, all of the most popular user-facing chatbot interfaces today use some combination of data interfaces and resources. Software packages like [LangChain](https://www.langchain.com/) have explicit support for building data interfaces where each available function is a [tool](https://python.langchain.com/v0.1/docs/modules/tools/) which can be defined and described in the language of choice. In fact, they even provide a set of [built-in tools](https://python.langchain.com/v0.1/docs/integrations/tools/) like web browsers and Google service integrations which can be plugged into any LLM with only a few lines of code. Using packages like LangChain make it easy to swap between LLMs even with all of the same tools. 

<img style="width:90%;" class="figure-center" src="https://storage.googleapis.com/public_data_09324832787/ai_data_infrastructure/chatgpt_data_interface.svg" /> 

As a more accessible example, OpenAI has invested in a lot of supporting technology for the [Chat GPT product](https://chatgpt.com/). Through the chat interface, users have access to an image generator, REST API calls, a RAG document retriever, a code interpreter which can read data files and generate images, a web browser, and a web interface to configure it all. In this case, the OpenAI service actually consists of both the LLMs and access to some of its own data interfaces. They manage the considerable infrastructure required for image generation, document retrieval, and code interpreter, making the product very powerful out of the box. At the same time, they also created a mostly thin data interface for initiating API calls that users can use to build very customized systems.

Once we view data interfaces this way, we can see that features like RAG are not fundamental aspects of LLMs, but rather just data interfaces that can be added or removed the same as any other. Typically, their data interfaces only involve a single function: a document search where the LLM must generate the search query. The returned data is simply the search results, which the LLM can use to answer the original question. The same is true of image generation - the LLM generates an image prompt which is sent to the image generator and the result is shared back with the user. While these tools feel like magic to the user, they are not particularly difficult to implement from scratch in any LLM workflow.

## Designing New Data Interfaces
As an example, imagine a scenario where we would like to give users access to an employee directory, stored in our systems as an SQL database. The user needs to be able to search for employees by name or job title. One way we could write the data interface would be to allow the LLM to write SQL queries which are then executed by the database client directly. Fortunately, SQL is a pretty common language, and thus LLMs are good at writing properly structured queries if given the database schema and likely some additional information about what each column means. The LLM would need to convert the output of the SQL command to a format the LLM can interpret.

An alternative approach to the same problem might be to enumerate several parameterized functions that the LLM can perform - in this case, the user can either search by name or search by job title. In this approach, the data interface would need to convert either function into an SQL command which is sent to the database. With this approach, the LLM does not need to know the full database schema or even how to write correct SQL (a weak point of smaller models), it only needs to know about the two functions and their parameters. This approach requires more effort on the part of the developer, but it requires the LLM to do less and therefore may scale better and be usable by smaller LLMs. We will talk about that tradeoff later.

In the third example, we can lean even further back in the other direction. Now imagine that the LLM is equipped with a “code interpreter”, or the ability to write and execute Python code on a machine with access to the data. If we allowed the LLM to use a code interpreter, we could give it as little as a URL or path to the database where the data is. The LLM could write Python code that would figure out what type of database it is interacting with, extract the database schema, and then execute queries according to any request the user makes. This is putting much more effort on the part of the LLM, but offers high flexibility.


<img style="width:90%;" class="figure-center" src="https://storage.googleapis.com/public_data_09324832787/ai_data_infrastructure/data_interface_tradeoffs.svg" /> 


These three approaches illustrate an apparent tradeoff between three aspects of data interfaces: developer effort, the time and thought that must go into designing the interface; flexibility, the number of different ways the data can be accessed/stored; and LLM effort, the compute resources and complexity of the model required to complete tasks consistently and accurately. The first example required medium developer effort because they need to extract and describe the database schemas, medium LLM effort because the LLM needs to write SQL queries, and medium flexibility because the LLM can access any feature available to the database engine. The second approach requires high developer effort and low flexibility, but results in low LLM effort - that is, the design is reliable and efficient. The final example offers minimum developer effort and maximum flexibility, but reliability may drop off if the LLM is not sophisticated enough.

## Thinking Widely
Separating the LLM from the data resources and interfaces can help us think differently about the infrastructure we can create to support user-facing chatbots. By defining data interfaces as tools that users can plug and unplug from LLMs, investment in data infrastructure means orchestrating a system for packaging these systems and producing metadata to describe their use. Here are a few ideas for data resources that could exist as packages within such a system.

+ **LLMs as resources**. The chat interface could offload some tasks to more specialized LLM agents that can do some processing and return results. From a technical level, this is a partial solution to the issue of limited context window size - agents can break down projects into sub-tasks that can be solved by separate chatbots. One example could be to have a set of specialized LLMs receive an original idea and iterate on it from different perspectives to produce a new result that is passed back to the primary LLM. Or imagine having a data resource with an LLM that specializes in code interpretations with precise instructions to make sure the main chatbot has access to consistent results.

+ **ETL pipelines as resources**. LLMs could run ETL pipelines with many parameters dynamically as the user needs them. If the parameters need to be adjusted depending on the desired use case, this chatbot could provide flexibility that would otherwise be very difficult to achieve with a dashboard or report. It combines the power of complicated ETL pipelines with the flexibility of an LLM to bring insights directly to the user who never needs to touch code.

+ **Data lakes as resources**. The most straightforward type of resource would be data storage technologies. Imagine creating an interface for connecting to simple databases or enterprise-level storage systems such as Snowflake. This could allow users to quickly extract more specific or aggregated data that they can use for simpler applications.

+ **Working memory as resources**. Another possible resource could be to a type of memory that an LLM could use for storing and accessing intermediary work. Say the user creates a specialized chatbot for creating project proposals. When they develop a report they like, they could store it in a database to be retrieved later. Alternatively, imagine a web research bot which could download main content from web pages and insert them in a database for retrieval later. These resources might be best used to augment other types of tools.

As I mentioned, data interfaces can be used to manipulate any computational resource at all, creating limitless possibilities for connecting systems in organizations. The key to investment is to be able to package and orchestrate these systems to make them available to other members of the organization.


