![GitHub last commit (branch)](https://img.shields.io/github/last-commit/suntrackspb/chimera-gpt-bot/master)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Telegram Chimera GPT & Kandinsky Bot

### Project status: `Refactoring`

#### Work version: https://t.me/SNTRKGptBot

### Description
This project is a telegram chatbot that works based on the chatgpt neural network to generate responses to users' messages. Thanks to this technology, the bot is able to recognize the meaning of users' messages and respond to them using pre-trained algorithms.

However, that's not all. In addition to being able to generate text responses, the bot can also generate images based on text descriptions. This is achieved by utilizing a Kandinsky neural network that is capable of generating images in multiple styles. Now, users can describe the image they want and the bot will generate them using predefined algorithms. Once the image is created, the chat bot will offer to share it by posting it in its gallery.

But, another useful feature of the bot is the ability to remove the background from the image. For this purpose, the u2net model is used and after image processing, the result can be obtained in PNG or WEBP format.

In general, this Telegram chatbot is a universal tool for users who are looking not only for text answers to their queries, but also ready to work with images. Also, this project is an excellent example of using neural networks in practical tasks.

**_Used:_**
* NagaAI Api or OpenAi Api
* Generate images from NagaAI
* rembg with u2net 


**_Stack:_**
* Aiogram
* MongoDB
* Pillow
* SpeechRecognition
* gTTS
* Celery
* Redis

* FastApi - gallery api
* React - gallery-frontend (Thanks to ![Static Badge](https://img.shields.io/badge/Frontend-Fil4tov-blue?style=social&logo=github&link=https%3A%2F%2Fgithub.com%2Ffil4tov))

