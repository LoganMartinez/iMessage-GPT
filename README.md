# IMessage-GPT

Setup:
- Download dependencies
- Create .env file from using .env.template
- You can add multiple independent models in chat/models.json. The "system" field is the first message that is given to the model, which can tell it what tone to use, how it should act, how it should format its reponses, etc. It's recommended to include that it should never use the @ symbol in its responses, as if it does it has a chance to respond to itself or other models.
- Optionally fill out chat/contacts.json file with number: name relations if you want the model to know names of people in chat

Dependencies: 
- python-dotenv
- python-typedstream: https://github.com/dgelessus/python-typedstream
- karellen-sqlite

Usage:
- run src/main.py
- send a message in the groupchat with the name specified in /chat/models (@ChatGPT by default)