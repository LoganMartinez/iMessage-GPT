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
        with open(f"{dir_path}/../chat/chatIds.json", "r") as idfile:
            self.chatIds = json.load(idfile)['chatIds']
        
        if self.chatHistory.keys() != self.chatIds:
            self.clear_history()
        for chatId in self.chatIds:
            if self.models.keys() != self.chatHistory[chatId].keys():
                self.clear_history()
    
    def clear_history(self):
        self.chatHistory = {}
        for chatId in self.chatIds:
            self.chatHistory[chatId] = {}
            for model in self.models.keys():
                self.chatHistory[chatId][model] = [{ "role": "system", 
                                                      "content": self.models[model]['system']}]
            
        with open (f"{dir_path}/../chat/chat.json", "w") as chatfile: 
            json.dump(self.chatHistory, chatfile)

    # receives any message, but will only use ones that contain @<ainame>
    def interpret_messages(self, chatId, messages):
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
            self.chatHistory[chatId][msg['model']].append({'role': 'user', 'content': msg['message']})
            req_body = { 'model': "gpt-3.5-turbo",
                         'messages': self.chatHistory[chatId][msg['model']],
                         "temperature": 0.7
                        }
            try:
                r = requests.post('https://api.openai.com/v1/chat/completions',
                                headers={ "Authorization": f"Bearer {env['API_KEY']}", },
                                json=req_body
                                )
            except Exception as e:
                print(f'Error sending request to OpenAI api: {e}')
                return []
            full_response = json.loads(r.text)
            if 'error' in full_response.keys():
                print('error with sending request: ' + str(full_response['error']))
                return []
            response = full_response['choices'][0]['message']
            self.chatHistory[chatId][msg['model']].append(response)
            responses.append(response['content'])

        with open (f"{dir_path}/../chat/chat.json", "w") as chatfile: 
            json.dump(self.chatHistory, chatfile)
        return responses

if __name__ == '__main__':
    gpt = GPT_model()
    
