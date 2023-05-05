from dotenv import dotenv_values
import os
import json
import requests

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../.env')

class GPT_model():
    def __init__(self):
        with open (f"{dir_path}/../chat/chat.json", "r") as chatfile:
            self.chatHistory = json.load(chatfile)
        if 'messages' not in self.chatHistory.keys() or len(self.chatHistory['messages']) == 0:
            self.clear_history()
    
    def clear_history(self):
        self.chatHistory['messages'] = [{ "role": "system", "content": env['SYSTEM_PROMPT'] }]
        with open (f"{dir_path}/../chat/chat.json", "w") as chatfile: 
            json.dump(self.chatHistory, chatfile)

    # receives any message, but will only use ones that contain @<ainame>
    def interpret_messages(self, messages):
        lowercaseMsgs = map(lambda msg: msg.lower(), messages)
        gptMessages = list(filter(lambda msg: env['AI_NAME'] in msg, lowercaseMsgs))

        responses = []
        for message in gptMessages:
            self.chatHistory['messages'].append({'role': 'user', 'content': message})
            req_body = { 'model': "gpt-3.5-turbo",
                         'messages': [{"role": "user", "content": "Say this is a test!"}],
                         "temperature": 0.7
                        }
            r = requests.post('https://api.openai.com/v1/chat/completions',
                             headers={ "Authorization": f"Bearer {env['API_KEY']}", },
                             json=req_body
                             )
            response = r.text['choices'][0]['message']
            self.chatHistory['messages'].append(response)
            responses.append(response['content'])

        with open (f"{dir_path}/../chat/chat.json", "w") as chatfile: 
            json.dump(self.chatHistory, chatfile)
        return responses