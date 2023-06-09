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
while True:
    try:
        while not receiver.has_new_messages():
            time.sleep(int(env['READ_RATE']))
            receiver.read()
        new_messages = receiver.get_new_messages()
        for chatId in new_messages.keys():
            isGroupChat = '1' if 'chat' in chatId else '0'
            gptResponses = gpt.interpret_messages(chatId, new_messages[chatId])
            for res in gptResponses:
                # this will cause a problem if there's a quotation in the response
                formattedRes = res.replace('"','')
                print(f'sending response: {res}\n----------')
                cmd = ['osascript', f'{dir_path}/sender.scpt', chatId, isGroupChat, formattedRes]
                result = subprocess.run(cmd, stderr=subprocess.STDOUT, text=True)
                err = result.stdout
                if err:
                    print(f'Error with sending gpt response {res}: {err}')
    except KeyboardInterrupt:
        clean_bin()
        break


