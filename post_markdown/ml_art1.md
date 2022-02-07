---
title: "Generating Visual Art Using Deep Learning Models"
subtitle: "Some examples of techniques and approaches I've been using to generate visual art using deep learning models."
date: "February 6, 2022"
id: "clip_model_experiments"
---

I've recently been playing with approaches to generate visual art using machine learning models. Inspired by [some blog articles](https://ml.berkeley.edu/blog/posts/clip-art/) on the topic, I extended some code to give me more flexibility over the types of inputs and outputs I can use to alter the asthetics, styles and other aspects of the resulting visual products. Here I wanted to describe some approaches I've been using as well as the resulting products based on custom artwork produced by friends.

---

Powered by models trained and released by [OpenAI](https://openai.com/), some early approaches, such as the [DALL-E neural network models](https://openai.com/blog/dall-e/), were created specifically to generate images from text ([see explanation here](https://ml.berkeley.edu/blog/posts/vq-vae/)). In contrast, newer approaches are built on models that were designed to generalize classical image classification and caption generation tasks. Perhaps the most popular of these is the [CLIP model](https://openai.com/blog/clip/). In the process of being trained to solve tasks involving the relationship between images and natural language, the models learn about the complex relationships between the two modalities that can be revealed by trying various combinations of inputs and outputs. Given that these models were not originally designed to create visual art, the results of experiments can be both surprising and interesting - exactly the features that excite visual art creators and enthusiasts. 

My use of the model involves training the last layer of the deep learning network model provided by CLIP, where the objective function is provided by any combination of image and text inputs. The total objective function is a simple linear combination of objective functions produced by each of the text and image inputs, and so in this way I can carefully choose inputs that might produce the images I think are interesting. Through a process of trial and error I've been playing with a number of approaches to image generation that I have found to produce meaningful differences.


### Text inputs only

The simplest use of these models would start with random initialization and use a single text input to generate the objective function. For the examples below, I created gifs where each frame is two training iterations. You can see that they all start with random (but correlated) noise. These images are fairly sensitive to random noise since it is a highly nonconvex objective function.

Here are a few examples I created:

##### "sunset in the city"

![sunset in the city](https://storage.googleapis.com/public_data_09324832787/mlart/text_only03-None-im-text0%3Dsunset_in_the_city-0_final.gif)

This example shows how the model clearly has a sense of the set of textures that might be associted with a city at sunset. The consistent appearance of aligning (yet sometimes slightly offset) windows, glow that might appear as reflections of the sun, and even the colors of concrete and steel that you might find in a photo or painting of a cityscape. Keep in mind that the CLIP model used to generate all of these was trained on real images in databases, so it's no surprise that they capture some of the realism we'd see in a regular photo.


##### "orcas in the north pole"

![orcas in the north pole](https://storage.googleapis.com/public_data_09324832787/mlart/text_only03-None-im-text0%3Dorcas_in_the_north_pole-4_final.gif)

The first thing to note is that the white background and snowy trees clearly capture some aspects of winter in the North Pole. The "orcas" part of the image is less clear though - they appear as random blobs that emulate the curvature and black/white contrast of the animals. We also see small bodies of water spread throughout the image.


##### "enter the matrix"

![enter the matrix](https://storage.googleapis.com/public_data_09324832787/mlart/text_only03-None-im-text0%3Denter_the_matrix-1_final.gif)

This test clearly demonstrates that the training data used to generate the full CLIP model included images from popular movies like the matrix. In my exploration I found that a lot of other popular media is represented here as well.

### Stylized text inputs

Now I will show a way we can use artifacts from the training data to produce stylized versions of the previous examples. I got the idea for this approach from [this blog article](https://ml.berkeley.edu/blog/posts/clip-art/), and extended it by further hypothesizing which kinds of data were included in the training data.

##### "building at sunset in the style of Studio Ghibli"

![Building at Sunset in the Style of Studio Ghibli](https://storage.googleapis.com/public_data_09324832787/mlart/stylized02-None-im-text0%3Dbuilding_at_sunset_in_the_style_of_Studio_Ghibli-0_final.gif)

I though this example was particularly cool because it shows how the addition of the text "in the style of Studio Ghibli" brings both stylistic elements and actual objects into the scene. In contrast to the previous city example, this shows rounded roofs like you might see in the era of japan portrayed in a Miyazaki film. It also introduces grass fields and trees into the imagery, clearly drawing inspiration from Ghibli films. While I don't have space to show them here, Studio Ghibli stylizations can contribute an interesting connections between human technology and nature into scenes.

### Non-random initialization



### Image-based objective functions

