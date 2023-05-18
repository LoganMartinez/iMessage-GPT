import requests
from dotenv import dotenv_values
import os
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../../.env')

def api_request(url, files=None, data=None, j=None):
    try:
        r = requests.post(url, headers={ "Authorization": f"Bearer {env['API_KEY']}" },
                          files=files,
                          data=data,
                          json=j)
    except Exception as e:
        print(f'Error sending request to OpenAI api: {e}')
        return (False, "Error sending request to OpenAI api")
    if r.status_code >= 500:
        print(f'problem with openai server: {r.status_code}')
        return (False, "Problem with OpenAI server when sending request")
    
    response = json.loads(r.text)
    if 'error' in response.keys():
        print('error with sending request: ' + str(response['error']))
        return (False, response['error']['message'])
    else:
        return (True, response)


# given a chatHistory, generates and returns (success, response)
def gpt_request(chatHistory):
    req_body = { 'model': "gpt-3.5-turbo",
                'messages': chatHistory,
                "temperature": 0.7
                }
    (success, response) = api_request('https://api.openai.com/v1/chat/completions', j=req_body)

    return (success, response)


def dalle_request(prompt, referenceImage=None):
    req_body = {
                "prompt": prompt,
                "n": 1,
                "size": "256x256",
            }
    if referenceImage:
        url = 'https://api.openai.com/v1/images/edits'
        files = {"image": open(referenceImage, 'rb')}
        data = req_body
        j = None
    else:
        url = 'https://api.openai.com/v1/images/generations'
        files = None
        data = None
        j = req_body
    (success, response) = api_request(url, files=files, data=data, j=j)

    if files:
        files['image'].close()

    return (success, response)