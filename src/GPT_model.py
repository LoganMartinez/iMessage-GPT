from dotenv import dotenv_values
import os
import json
import requests

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../.env')

class GPT_model():
    def __init__(self):
        with open (f"{dir_path}/../chat/models.json", "r") as modelfile:
            self.models = json.load(modelfile)
        with open (f"{dir_path}/../chat/chat.json", "r") as chatfile:
            self.chatHistory = json.load(chatfile)
        if self.models.keys() != self.chatHistory.keys():
            self.clear_history()
    
    def clear_history(self):
        self.chatHistory = {}
        for model in self.models.keys():
            self.chatHistory[model] = [{ "role": "system", "content": self.models[model]['system']}]
        with open (f"{dir_path}/../chat/chat.json", "w") as chatfile: 
            json.dump(self.chatHistory, chatfile)

    # receives any message, but will only use ones that contain @<ainame>
    def interpret_messages(self, messages):
        lowercaseMsgs = map(lambda msg: msg.lower(), messages)
        gptMessages = []
        for msg in lowercaseMsgs:
            for modelName in self.models.keys():
                if modelName.lower() in msg:
                    gptMessages.append({ 'model': modelName,
                                         'message': msg 
                                       })

        responses = []
        for msg in gptMessages:
            print(f'interpretting message: {msg["message"]}...')
            if '--c' in msg:
                self.clear_history()
            self.chatHistory[msg['model']].append({'role': 'user', 'content': msg['message']})
            req_body = { 'model': "gpt-3.5-turbo",
                         'messages': self.chatHistory[msg['model']],
                         "temperature": 0.7
                        }
            try:
                r = requests.post('https://api.openai.com/v1/chat/completions',
                                headers={ "Authorization": f"Bearer {env['API_KEY']}", },
                                json=req_body
                                )
            except Exception as e:
                print(f'Error sending request to OpenAI api: {e}')
            full_response = json.loads(r.text)
            if 'error' in full_response.keys():
                print('error with sending request: ' + str(full_response['error']))
                return []
            response = full_response['choices'][0]['message']
            self.chatHistory[msg['model']].append(response)
            responses.append(response['content'])

        with open (f"{dir_path}/../chat/chat.json", "w") as chatfile: 
            json.dump(self.chatHistory, chatfile)
        return responses
    