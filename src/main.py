from MsgReceiver import MsgReceiver
from utils.clean_bin import clean_bin
from dotenv import dotenv_values
import os
import time
from GPT_model import GPT_model

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../.env')
chatdb_path = env['CHAT_DB']

receiver = MsgReceiver()
gpt = GPT_model()

print('Listening for messages...')
while True:
    try:
        while not receiver.has_new_messages():
            time.sleep(int(env['READ_RATE']))
            receiver.watch_db()
            while receiver.watching:
                time.sleep(int(env['READ_RATE'])) 
        # new messages go to GPT
        print(receiver.get_new_messages())
    except KeyboardInterrupt:
        clean_bin()
        break


