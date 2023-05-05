# iMessage-GPT

## Overview:
This project allows you to add ChatGPT functionality into an iMessage groupchat. The chat is monitored for messages that tag the model, and these messages are interpreted by ChatGPT using OpenAI API. The responses are then automatically sent in the groupchat. This project supports the use of multiple customizable independent models that have different system commands and independent chat histories.

## Setup:
* Download dependencies
* Create .env file from using .env.template
* You can add multiple independent models in chat/models.json. The "system" field is the first message that is given to the model, which can tell it what tone to use, how it should act, how it should format its reponses, etc. It's recommended to include that it should never use the @ symbol in its responses, as if it does it has a chance to respond to itself or other models.
* Optionally fill out the chat/contacts.json file with (phone_number: name) relations if you want the model to know the names of people in the chat

## Dependencies: 
* python-dotenv
* python-typedstream: https://github.com/dgelessus/python-typedstream
* karellen-sqlite

## Usage:
* From the root directory, run using python3 src/main.py
* Send a message in the groupchat with the name specified in /chat/models (@ChatGPT by default)
* Chat history can be cleared by including '--c' in a message
