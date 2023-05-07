from MsgReceiver import MsgReceiver
from utils.clean_bin import clean_bin
from dotenv import dotenv_values
import os
import time
from GPT_model import GPT_model
import subprocess

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../.env')
chatdb_path = env['CHAT_DB']

receiver = MsgReceiver()
gpt = GPT_model()
if env['CLEAR_ON_RESTART']:
    gpt.clear_history()

print('Listening for messages...')
# while True:
#     try:
#         while not receiver.has_new_messages():
#             time.sleep(int(env['READ_RATE']))
#             receiver.read()
#         gptResponses = gpt.interpret_messages(receiver.get_new_messages())
#         for (id, response) in gptResponses:
#             # There will be a problem if there's a quotation in the response
#             formattedRes = response.replace('"','')
#             print(f'sending response: {response}\n----------')
#             cmd = ['osascript', f'{dir_path}/sender.scpt', dir_path, str(id), formattedRes]
#             result = subprocess.run(cmd, stderr=subprocess.STDOUT, text=True)
#             err = result.stdout
#             if err:
#                 print(f'Error with sending gpt response {response}: {err}')
#     except KeyboardInterrupt:
#         clean_bin()
#         break
(id, response) = (253466, 'hello')
cmd = cmd = ['osascript', f'{dir_path}/sender.scpt', dir_path, str(id), response]
result = subprocess.run(cmd, stderr=subprocess.STDOUT, text=True)


