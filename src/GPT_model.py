import openapi
from dotenv import dotenv_values
import os
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../.env')

openapi.api_key=env['API_KEY']


class GPT_model():
    def __init__(self):
        pass
    
    # receives any message, but will only use ones that contain @<ainame>
    def receive_messages(self, messages):
        lowercaseMsgs = map(lambda msg: msg.lower(), messages)
        gptMessages = list(filter(lambda msg: env['AI_NAME'] in msg, lowercaseMsgs))

        for message in gptMessages:
            print(message)



        
        
model = GPT_model()
model.receive_messages(["+15128180555: 'Wow holy shit'", "+15128180555: 'Fucked up my damn phone '", "+17138289771: '@shitnuts House'", "+15128180555: 'Where in lib'"])