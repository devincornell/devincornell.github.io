---
title: "The Future of AI for Organizations: Integrating Systems through Large Language Models"
subtitle: "Investment in AI is about more than investing in AI technology itself - it is about investing in the ecosystem of technologies and human processes that make organizations unique."
date: "Sept 24, 2024"
id: "llm_integrating_systems"
blogroll_img_url: "https://storage.googleapis.com/public_data_09324832787/llm_integrating_systems/llm_as_hci.png"
---

Generative AI and, more specifically, [large language models (LLMs)](https://www.nvidia.com/en-us/glossary/large-language-models/) are now ubiquitous in information-related work. From composing emails to summarizing documents, there is no doubt that modern AI tools like ChatGPT have already had a big impact on individual productivity. What is less understood, however, is the mechanism by which these tools can have an impact at the organizational level. Management consulting firms have been deemed "[early winners](https://www.nytimes.com/2024/06/26/technology/ai-consultants.html)" of the A.I. boom because [organizations clearly want to invest](https://www.technologyreview.com/2023/07/18/1076423/the-great-acceleration-cio-perspectives-on-generative-ai/) - it just isn’t clear how.

I believe that at the organizational level, investment in AI means thinking about the ways that LLMs can connect various systems that the organization uses every day. Once we start to think of LLMs as user interfaces for interacting with these systems, we can start to take a different approach to the development of data infrastructure, communication and information services, and even the ways we integrate organizational values and commitments into everyday work.

![LLMs as HCI](https://storage.googleapis.com/public_data_09324832787/llm_integrating_systems/llm_as_hci.png)

I have identified four primary types of systems that LLMs have the potential to integrate. In each case, we have the technical building blocks to connect LLMs to these systems today, and improvements to the foundational technologies will expand the ways we are able to move information between and across these systems. Of course, this list is not exhaustive - I only use them as a starting point to build a picture of a high-level strategic vision.


These are the four types of systems.

+ ***Communication/information Services***. Work with active systems and services that your organization uses every day. May include email, instant messaging, calendars, version control, document storage, and/or project management solutions, but can also include more organization-specific systems.
+ ***Data Lakes / Warehouses***. Access and manipulate raw proprietary data used to support research or inform business intelligence often prepared by data engineers or scientists.
+ ***Organizational information***. Access information about the organization itself. May include HR policies, employee directories, organizational charts, or operating procedures.
+ ***Institutional Knowledge and Practices***. Integration of everything from core values of the organization to important practices or methodologies that the organization uses on a daily basis. Could also include background information about the theoretical frameworks that the organization uses.

Now I’ll elaborate on how each of these systems could integrate with LLMs and compare the vision with the current state of technology. 

# Communication / Information Services

Communication and information services vary by the type and industry of the organization, but at minimum they would include email and tools like Skype, Slack, Teams, GChat, Google Drive, OneDrive or other kinds of communication and data management tools. It also likely includes more industry-specific tools around which the organizations work. For instance, a software company might have some combination of version control systems, continuous integration servers, or bug reporting platforms. Other organizations might use systems that track tasks or highly organized documentation systems. These systems all provide the structure around which people work, and they all leave digital trace data that can be used to understand the operation or status of the organization at any given point in time.

![LLMs and Communication Systems](https://storage.googleapis.com/public_data_09324832787/llm_integrating_systems/llms_and_communication.png)

These are the types of things I expect that LLMs should be able to do.

+ Send messages or create posts that include contents of work.
    
    _Create a line plot from the most recent financial trend data, summarize the chart in three bullet points, and send it as an email to my team._

+ Create complex queries for information across all platforms.
    
    _Has anyone asked me on Slack or Email to get back to them or complete some task by EOD today?_

+ Create summaries of activity levels or status of the company as well.
    
    _Produce a status report on the overall level of activity in the organization broken down by weekday._

It is not difficult to imagine the wide range of functionality this could provide - the LLMs are limited only by the information platforms they can access through the LLM. Giving an LLM access to these systems involves enabling their functionality as Application Programming Interfaces, or APIs, which allow other programs to do things like send/receive messages without opening the software interface itself. The LLM essentially just requires information about the various capabilities and information needed to execute each task, and it can make decisions about which actions to perform and what data to send based on queries from the user. ChatGPT, for instance, refers to these API interfaces as “Actions”.

Companies that sell communication software as a service have not historically been open to making their data available even to the organizations that use them, but AI could be impactful enough to create disruption in the software market. In theory, an LLM could be the only interface for these types of systems - that is, a particular system may not even need to provide a visual interface which users can open and interact with others. This possibility has huge implications for the future of the software market.

# Data Lakes / Warehouses

The advent of the data-obsessed economy brought with it a still-growing level of investment in data infrastructure, and LLMs have great potential for making collected data even more useful. Data Lakes and Data Warehouses are names given to collections of data managed by organizations. These systems are often created by data engineers and made valuable through the work of data scientists, who spend a lot of effort to translate raw data into data dashboards or analyses that answer hypotheses from management.


![LLMs and Data Systems](https://storage.googleapis.com/public_data_09324832787/llm_integrating_systems/ai_and_data.png)


I expect the LLM would be able to perform these types of tasks.

+ Describe the types of data that are available in the current systems.
    _I am looking for data about how long users spend browsing different pages on our corporate website. What is available to me?_

+ Create visualizations.
    _Create a bar chart comparing the time spent on our company website based on the type of user account they have._

+ Run analyses to test hypotheses.
    _Create a regression model predicting time spent on our company website from the user’s age, controlling for user account type._

The technology that is most relevant to this work is generally referred to as “code interpretation”. The ability to convert human commands into arbitrary computer instructions, or code generation, has been well-established - in fact, many LLMs are specifically designed to write code. The next step is to be able to execute the generated code on the computer to produce analyses. The technology available to us today is at the level where it can write fairly sophisticated code for data analysis, and we can expect this to get much better over time.

In theory, this technology has the potential to replace data analysts and data engineers because anyone can run the kinds of analysis they currently perform, but in practice it will probably lead to more of a shift in their work: these roles will be more about designing data interfaces and producing accurate metadata so that humans can perform analyses without knowing the internal structure of the data. When a manager wants to see certain information, they can create visualizations or models themselves as long as the source data is made available to them.

# Organizational Policies

Every organization has a set of formal documents which describe the policies and operating procedures of the organization. HR policies, employee directories, organizational charts, and operating procedures are all examples of these types of information. Users should be able to ask questions about the policies and identify policies that may be relevant for a given situation.

![LLMs and Organizational Policies](https://storage.googleapis.com/public_data_09324832787/llm_integrating_systems/ai_and_organizational_info.png)

These are examples of tasks that the AI should be able to perform with administrative documents.

+ Query information from the documents.
    _What is the company policy on paternity leave?_

+ Summarize information for those that are unfamiliar with the documents.
    _Summarize the contents of the company social media policy._

+ Infer meta-information such as the purpose of the documents and the situations in which users may require particular knowledge.
    _Yesterday I posted a social media post that got a lot of critical engagement online. Could I be at risk with the company due to the things I said there?_

+ Identify important/unusual sections to generate new employee training content.
    _Is there anything in the social media policy that might be unusual or unique to this organization?_

+ Synthesize information across documents that may each contain part of the information needed to answer a given query or resolve a situation.
    _The social media policy suggests that I cannot be held liable for my political orientation, but some of my political opinions may relate to our DEI policy. Can you point out the intersections and differences of these two policies as they pertain to my situation?_

While LLMs today are especially well-suited to do these kinds of operations on a small scale, the foundational technologies that support these operations require further development before we can see this kind of use. The fundamental limitation for many of these tasks is based on a feature of LLMs called “context window size”. This is essentially the size of the working memory that the model has access to at any given time. While the challenge is well-documented, the issue is that context window size is directly related to the computational resources required to run the models: that is, larger context windows require more powerful computers.

Currently, the most popular solution for document retrieval is a technology called ["Retrieval-Augmented Generation", or RAG](https://blogs.nvidia.com/blog/what-is-retrieval-augmented-generation/). This technology essentially takes your query and searches through snippets of your documents using a simpler algorithm to send only relevant parts of the document to the LLM. The LLM can then ingest the snippets of text instead of the full documents for summarization and synthesis with its limited working memory. The problem comes when the user’s query requires a more holistic understanding of the documents to answer the user query: RAG must necessarily break documents down into small chunks to be effective. I expect that this technology or other solutions to this problem will evolve rapidly.


# Institutional Knowledge and Practices

This final category of systems is the most abstract, but also perhaps the most powerful: it can allow us to integrate the overarching values, commitments, and stances of the organization into every level of work. By “documented institutional knowledge and practices,” I broadly mean any kind of documented information about the perspectives or guiding principles of the organization. This could range from a simple list of organizational goals or values to every piece of work output that the organization has ever created, or even a set of documents containing blog articles which most resonate with organization leaders. 

![LLMs and Institutional Knowledge](https://storage.googleapis.com/public_data_09324832787/llm_integrating_systems/ai_and_culture.png)


Integrating organizational commitments could mean different things depending on the work being done. The premise is that individuals are already using LLMs to automate tasks and improve their work. If the documented information is, for instance, every output the organization has created, we would at least want the LLM to draw on lingo, framing, and perhaps even examples from that work into any given task. If the documentation consists of explicitly stated values, we would want it to be able to integrate those values or ideas into other work more implicitly - perhaps by altering the default assumptions or framings of problems for which solutions are being created.

Today’s LLMs have the fundamental components to integrate values and commitments into different kinds of work. The simplest approach would be to explicitly ask LLMs to assess or include elements from these organizational values. Of course, this approach assumes that the organizational values are widely understood and that the LLMs would have a basic understanding of what they mean. For instance, diversity and inclusion is a widely applicable concept that the LLM likely has some background information on.

+ Check and iterate on existing work.
    _Identify new ways that our proposed solution could address the needs of more diverse populations._

+ Explicit integration into brainstorming.
    _Develop a plan for evaluating the effectiveness of vaccine distribution programs in Venezuela with a specific mind towards diversity and inclusion._

To integrate diversity and inclusion into work in every query, it might be better to use a “system prompt”, or a prompt that is submitted to the LLM before the user even asks a query or makes a request. On the OpenAI platform, for instance, this is defined when creating a Custom GPT and referred to as “instructions” for the AI, and most LLMs have this capability. The underlying LLM technology will start the conversation with the system prompt as chat history, and so we can integrate values into this work at the start of every chat.

+ Implicit integration into brainstorming.
    **System prompt**: _Your goal is to assist users in designing evaluation programs for healthcare-related interventions in different regions. In proposing new evaluation approaches, always attempt to frame challenges in terms of “systems thinking.” Systems thinking is “...”._

    **User prompt**: _Develop a plan for evaluating the effectiveness of vaccine distribution programs in Venezuela._

More complicated organizational commitments could alternatively be provided as documents that the LLM has access to like the administrative systems previously discussed. With this approach, the LLM would need to ingest this information prior to completing any task. Alternatively, when accessing a large number of documents, we could use a multi-step process where we first use an LLM to distill key values from a wide range of other documents and then ingest that output into another LLM.

The final and most effortful way that this information can be ingested into work with LLMs is through fine-tuning the LLM itself. This means taking an existing model that was fit on a massive amount of data, and giving it additional information on which to focus. This partially solves the context size working memory limitation because it means the LLM will be able to integrate the values and commitments at every level of work without explicitly needing to describe it in the user or system prompts. That said, it will require an AI specialist to implement.


# A Single Integrated System

Integrating these systems with a single LLM will allow us to make huge leaps in productivity because we can [automate multi-step processes](https://www.linkedin.com/posts/zainkahn_ex-google-ceo-eric-schmidt-says-3-developments-activity-7234892626666110976-LxN4?utm_source=share&utm_medium=member_desktop) that have always required human effort. Most of the productivity tools we use today accomplish tasks within a single domain, and the goal of information work is to translate, synthesize, and summarize that information across those platforms in new and creative ways. LLMs have the potential to support this work by integrating systems through one of the most foundational and unique technologies that humankind has ever developed: natural language.

Organizations can take advantage of current LLM technologies by developing multiple specialized chat interfaces that each access a small number of systems, and many organizations have already started doing so. For instance, OpenAI has created a marketplace of “Custom GPTs”, or chatbots that specialize in particular tasks defined by the systems they connect to, the resources they have access to, and the system prompt that guides their behavior. Using the Chat GPT Enterprise Subscription, organizations may create their own Custom chatbots that connect to specific proprietary systems. Specialized chatbots are limited, however, because they cannot integrate information across platforms and data systems. In the near future, however, each organization will be able to use a single chatbot that could connect to all internal and external systems.

The advantage of investing in AI systems now is that the investment will only compound: the integration of any one system is more impactful when the LLM already has access to other systems. The LLM hype is leading to huge advancements in both foundational technologies and support for integrating systems, so the features that we will see next year will be much more advanced than those we can use today. Soon we will start to see a movement away from specialized chatbots to ones that have access to a wide range of interfaces and integrations, and you can start today by investing in the supporting infrastructure that will enable it.




