from dotenv import dotenv_values
import os
import json
from utils.api_requests import *

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../.env')

class GPT_model():
    def __init__(self):
        with open(f"{dir_path}/../chat/config.json", "r") as configfile:
            config = json.load(configfile)
            self.chatIds = config['chatIds']
            self.models = config['models']

        with open (f"{dir_path}/../chat/chat.json", "r") as chatfile:
            self.chatHistory = json.load(chatfile)
        
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
                if 'text_prompt' in self.models[model].keys():
                    self.chatHistory[chatId][model] = [{ "role": "system", 
                                                          "content": self.models[model]['text_prompt']}]
            
        with open (f"{dir_path}/../chat/chat.json", "w") as chatfile: 
            json.dump(self.chatHistory, chatfile)

    # receives any message, but will only use ones that contain @<ainame>
    def interpret_messages(self, chatId, messages):
        # don't think i need to do this
        lowercaseMsgs = map(lambda msg: msg.lower(), messages)
        gptMessages = []
        for msg in lowercaseMsgs:
            for modelName in self.models.keys():
                if modelName.lower() in msg:
                    gptMessages.append((modelName, msg))

        responses = []
        for (modelName, message) in gptMessages:
            print(f'interpretting message: {message}...')
            response = {}
            # generate text response
            if 'text_prompt' in self.models[modelName].keys():
                self.chatHistory[chatId][modelName].append({'role': 'user', 'content': message})
                (success, full_response) = gpt_request(self.chatHistory[chatId][modelName])
                if not success:
                    responses.append(full_response)
                    continue
                response = full_response['choices'][0]['message']
                self.chatHistory[chatId][modelName].append(response)
                responses.append(response['content'])
                    
            # generate image response
            if 'include_image' in self.models[modelName].keys():
                # will use the generated text response as a prompt if text generation is enabled
                if ':' in message:
                    message = message.split(':')[1]
                prompt = response.get('content', message)
                if len(prompt) >= 400:
                    # prompt needs to be truncated
                    truncatePrompt = [{'role':'system',
                                       'content':"""You will be given a prompt, and your response 
                                       should be a summarization of that prompt. Your response should 
                                       not be more than 300 characters, and it should be visually descriptive."""
                                       }]
                    truncatePrompt.append({'role':'user', 'content': prompt})
                    (success, full_response) = gpt_request(truncatePrompt)
                    if not success:
                        responses.append(full_response)
                        continue
                    prompt = full_response['choices'][0]['message']['content']
                    print(f'generated text was truncated for image generation: {prompt}')

                if 'reference_image' in self.models[modelName].keys():
                    referenceUrl = self.models[modelName]['reference_image']
                    (success, response) = dalle_request(prompt, referenceImage=referenceUrl)
                else:
                    (success, response) = dalle_request(prompt)

                if not success:
                    responses.append(response)
                    continue
                id = response['created']
                imageUrl = response['data'][0]['url']
                img_data = requests.get(imageUrl).content
                imagePath = f'{env["PICTURES_FOLDER"]}/gpt/{id}.png'
                with open(imagePath, 'wb') as handler:
                    handler.write(img_data)
                responses.append(f'imagePath:{imagePath}')

        with open (f"{dir_path}/../chat/chat.json", "w") as chatfile: 
            json.dump(self.chatHistory, chatfile)
        return responses

if __name__ == '__main__':
    gpt = GPT_model()
    messages = ['@image of a dog']
    print(gpt.interpret_messages("", messages))
    
