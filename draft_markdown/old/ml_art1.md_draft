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

Now I will show a way we can use artifacts from the training data to produce stylized versions of the previous examples. I got the idea for this approach from [this blog article](https://ml.berkeley.edu/blog/posts/clip-art/), and extended it by further hypothesizing which kinds of data were included in the training data. The so-called "artifacts" in the training data are simply the source of the images. For instance, experimentation suggests that some of the training data may consist of images from Flickr, and by including "Flickr" in the text we can ask the model to re-create some stylistic elements from those photos. I also had success experimenting with Deviantart, Unreal Engine, etc. Similarly to our Matrix example, we can also use stylistic elements from certain types of media such as films by Studio Ghibli.

##### "sunset in the city on Flickr"

![sunset in the city on Flickr](https://storage.googleapis.com/public_data_09324832787/mlart/stylized02-None-im-text0%3Dsunset_in_the_city_on_Flickr-1_final.gif)

Here I re-used one of the previous examples but added the text "on Flickr" at the end. Instead of appearing like the side of buildings in the sunset, this image includes what appear to be power lines, traffic light poles, sides of cars, and even shapes that look suspiciously like people viewed from behind. The implications of these artifacts are really interesting. First, the inclusion of elements like power lines suggests that images from Flicker that are captioned with "city" are more likely to be photos from the ground than from the sky - it makes sense intuitively. Also note that it seems to carry realism styles into the image.


##### "sunset in the city Artstation"

![sunset in the city Artstation](https://storage.googleapis.com/public_data_09324832787/mlart/stylized03-None-im-text0%3Dsunset_in_the_city_Artstation-0_final.gif)

I tried "[Artstation](https://www.artstation.com)" because it is another popular website for posting user-created art. Note tha variation in building design, the distribution of open space over the scene, and the human body-like objects. It is worth looking at the [Arstation website](https://www.artstation.com) to give a sense of what images there look like.


##### "sunset in the city Ghibli"

![sunset in the city Ghibli](https://storage.googleapis.com/public_data_09324832787/mlart/stylized03-None-im-text0%3Dsunset_in_the_city_Ghibli-1_final.gif)


I thought this example was particularly cool because it shows how the addition of the text "Ghibli" brings both stylistic elements and actual objects from movies produced by Studio Ghibli into the scene. The sun appears as round globes instead of just reflections off of buildings - unsuprising given that real photographs can rarely capture the sun alongside an actual scene in the way that a cartoon could. Also note the grass and trees that don't appear in the other images. This fits neatly within the realm of the relationship between human technology and nature that we often see in Miyazaki films. The buildings here are not made of square edges as we saw in the last several examples, but rather have rounded roofs and are made of concrete instead of closely packed windows.

##### "Angel's Landing Artstation"

![Angel's Landing Artstation](https://storage.googleapis.com/public_data_09324832787/mlart/Angels_Landing_artstation_4_iter1004.png)




## Nonrandom initialization

Until now we've been using random initialization to begin the model training, but the coolest outputs from these models come when we actually initialize parameters from an existing image. By giving it an initial image and some text, we can begin to add information to the existing photos which previously did not exist.

The simplest example I can show

#### Freedom

Initial image: ["Freedom"](https://storage.googleapis.com/public_data_09324832787/mlart/kiersten_freedom_painting_cropped.jpeg)

Text prompt: "freedom"

![freedom](https://storage.googleapis.com/public_data_09324832787/mlart/freedom1.gif)

#### Transcendance

Initial image: "[peace and transcendance](https://storage.googleapis.com/public_data_09324832787/mlart/varun_painting_1.jpeg)"

Text prompt: "transcendance"
![Transcendance](https://storage.googleapis.com/public_data_09324832787/mlart/varun1.gif)


#### Sunset in the mountains

Initial image: stock photo

Text prompt: "Sunset in the mountains"

![Sunset in the mountains](https://storage.googleapis.com/public_data_09324832787/mlart/sunset1.gif)


## Image-based objective functions

The real advantage of using these CLIP models is that we can add images to generate the objective function.

### Symbols

The image-based objective functions can add complex textures to even the simplest initial images. I have only tried it on a few starting images so far though.

#### Om

Text prompt: "peace and love"

Image prompt: ["The Aluren Forest"](https://www.artstation.com/artwork/mDWZxY)

Initial image: [Om symbol](https://storage.googleapis.com/public_data_09324832787/mlart/Aum_Om_black.png)

"Peace and Love Deviantart"

![peace and love Om](https://storage.googleapis.com/public_data_09324832787/mlart/peace_and_love_deviantart_step0.05_0_final.png)


### Paintings

#### "Our Garden"

Original image: "[Angela's garden](https://storage.googleapis.com/public_data_09324832787/mlart/angela_garden1.jpg)"

Image prompt: ["The Aluren Forest"](https://www.artstation.com/artwork/mDWZxY)

Text prompt: "garden"

![garden](https://storage.googleapis.com/public_data_09324832787/mlart/angela04_garden-garden--angela_garden1-angela_garden1.sunset_forest-0_final.png)


Text prompt: "lush green forest with flowers"

![garden](https://storage.googleapis.com/public_data_09324832787/mlart/angela04_garden-lush_green_forest_with_flowers--angela_garden1-angela_garden1.sunset_forest-0_final.png)


Text prompt: "flowers at sunset"

![flowers at sunset](https://storage.googleapis.com/public_data_09324832787/mlart/angela04_garden-flowers_at_sunset--angela_garden1-angela_garden1.sunset_forest-0_final.png)

Animation:

![flowers at sunset animation](https://storage.googleapis.com/public_data_09324832787/mlart/angela04_garden-flowers_at_sunset--angela_garden1-angela_garden1.sunset_forest-0_final.gif)


#### Campfire in the night


Original image: [campfire scene](https://storage.googleapis.com/public_data_09324832787/mlart/sujaya_camping.jpg)

##### "campfire starry night"

![sujaya](https://storage.googleapis.com/public_data_09324832787/mlart/sujaya12_campfire_starrynight-campfire_in_starry_night--sujaya_camping-sujaya_camping.starry_night-0_final.png)

##### "forest at sunset"

![sujaya](https://storage.googleapis.com/public_data_09324832787/mlart/sujaya13_campfire_sunset-forest_at_sunset--sujaya_camping-sujaya_camping.sunset_forest-0_final.png)

##### "Stars in the Sky Ghibli"

![sujaya](https://storage.googleapis.com/public_data_09324832787/mlart/sujaya10_campfire-stars_in_the_sky-ghibli-sujaya_camping-sujaya_camping.cosmos_stock-0_final.png)







### Time-dynamic animations

So far I have shown gifs that show each training iteration as the model converges. In addition to giving us an intuition as to how the model is training, it feels like it brings the scenes to life - objects and stylistic elements are constantly moving and changing slightly. This gave me the inspiration to try changing the text and image objective functions while the model trains.



