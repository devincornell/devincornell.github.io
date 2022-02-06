---
title: "Experimentation with Visual Art using CLIP Models"
subtitle: "Generating visual art using models originally designed to create transcirptions from images."
date: "April 11, 2019"
id: "ucsb_instructional_development_grant"
---

I've recently been playing with approaches to generate visual art using machine learning models. Inspired by [some blog articles](https://ml.berkeley.edu/blog/posts/clip-art/) on the topic, I extended some code to give me more flexibility over the types of inputs and outputs I can use to alter the asthetics, styles and other aspects of the resulting visual products. Here I wanted to describe some approaches I've been using as well as the resulting products based on custom artwork produced by friends.

---

Powered by models trained and released by [OpenAI](https://openai.com/), some early approaches, such as the [DALL-E neural network models](https://openai.com/blog/dall-e/), were created specifically to generate images from text ([see explanation here](https://ml.berkeley.edu/blog/posts/vq-vae/)). In contrast, newer approaches are built on models that were designed to generalize classical image classification and caption generation tasks. Perhaps the most popular of these is the [CLIP model](https://openai.com/blog/clip/). In the process of being trained to solve tasks involving the relationship between images and natural language, the models learn about the complex relationships between the two modalities that can be revealed by trying various combinations of inputs and outputs. Given that these models were not originally designed to create visual art, the results of experiments can be both surprising and interesting - exactly the features that excite visual art creators and enthusiasts. 

My use of the model involves training the last layer of the deep learning network model provided by CLIP, where the objective function is provided by any combination of image and text inputs. The total objective function is a simple linear combination of objective functions produced by each of the text and image inputs, and so in this way I can carefully choose inputs that might produce the images I think are interestign. Through a process of trial and error I've been playing with a number of approaches to image generation that I have found to produce meaningful differences.

Starting with the base CLIP model and any combination of image and text inputs, I train an additional neural network hidden layer to produce aoutput

this model trains a layer of hidden weights to create some 


initialization of the hidden weights that can be based on an image, and any number of texts or images that are 

The models work by accepting any number of texts and images. 



https://openai.com/blog/dall-e/


Some approaches have been specifically aimed 

Inspired by some blog articles 

I believe that computation in the sciences and the arts offers the possibility to expand the ways we think about solving theoretical and empirical problems. Using a combination of simulations and and learning algorithms, we can begin to ask more open-ended questions about our data and the models we use to understand them. In stead of using on social theory or specific artistic styles 

We are fored to question the language we use and conceptions of the underlying priciples on which products like scientific papers and modern art are based

They force us to question 


. In the visual arts, we can start to deconstruct distinctions between asthetics, shapes, strokes, imagery, symbolism 

In the sciences they can help us re-think 
My MA thesis at UC Santa Barbara was an attempt to take such an approach. I used genetic algorithms to perform a "search" for the particular 


 to understand the evolution of discursive fields produced by a particular Colombian political party, and I used genetic algorithms to search for the discursive distinctions 


I've long been interested in using computation to generate visual and auditory imagery. I think computation in the sciences and the arts offers the possibility to re-think theoretical and empirical problems

Much like the possibilities of using computation for science,

[test](https://ml.berkeley.edu/blog/posts/clip-art/)




