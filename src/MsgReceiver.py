import sqlite3
from dotenv import dotenv_values
import subprocess
import os
import sqlite3
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../.env')

class MsgReceiver():
    
    def __init__(self):
        # Open chat.db file
        self.con = sqlite3.connect(env['CHAT_DB'])
        self.cur = self.con.cursor()

        with open(f"{dir_path}/../chat/config.json", "r") as configfile:
            config = json.load(configfile)
            self.contacts = config['contacts']
            self.chatIds = config['chatIds']

        # dict that holds rowid for most recent message for each chatId
        self.most_recent_messages = {}
        self.new_messages = {}
        self.read()
        self.new_messages = {}
        

    # read the chat.db file and return new messages in format [sender_number1: message1, ...]
    def read(self):
        # query for messages (id, messageContent, phone#_of_sender, chatId)
        for chatId in self.chatIds:
            res = self.cur.execute(f"""
                SELECT m.rowid, m.attributedBody,
                        CASE WHEN m.is_from_me THEN '{env['MY_NUMBER']}' ELSE h.id END as fromNumber,
                        COALESCE(cache_roomnames, h.id) as chatId
                FROM message AS m
                        LEFT JOIN handle AS h ON m.handle_id=h.rowid
                WHERE chatId='{chatId}'
                        AND m.rowid>{self.most_recent_messages.get(chatId, -1)}
                ORDER BY m.date desc
                LIMIT 10
            """)
            rowsForThisId = res.fetchall()
            if len(rowsForThisId) == 0:
                continue

            rowsForThisId.reverse()
            
            messages = []
            rowIds = []
            # 'attributedBody' column has message content, but it's encoded so we have to clean it up
            for (ROWID, attributedBody, sender, cid) in rowsForThisId:
                rowIds.append(ROWID)
                if attributedBody:
                      filename = f'{dir_path}/../bin/{ROWID}.bin'
                      with open(filename, 'wb') as binfile:
                            binfile.write(attributedBody)
                      cmd = ['python3', '-m', 'typedstream', 'decode', filename]
                      result = subprocess.run(cmd, capture_output=True)
                      os.remove(filename)

                      err = result.stderr.decode()
                      if err:
                          print(f'Error with running typedstream on message {ROWID}: {err}')
                      else:
                          output = result.stdout.decode()
                          # clean up typedstream output
                          msg_text = output.split('(')[1].split(')\n')[0]
                          contact = self.contacts.get(sender, sender)
                          msg = f"{contact}: {msg_text}"
                          messages.insert(0, msg)
            self.new_messages[chatId] = messages
            self.most_recent_messages[chatId] = max(rowIds)
    
    def get_new_messages(self):
        ret = self.new_messages
        self.new_messages = {}
        return ret
    
    def has_new_messages(self):
        return any([len(self.new_messages[key]) != 0 for key in self.new_messages.keys()])
    

if __name__ == '__main__':
    import time
    receiver = MsgReceiver()
    while True:
        while not receiver.has_new_messages():
            time.sleep(5)
            receiver.read()
        print('new messages')
        new_messages = receiver.get_new_messages()
        print(new_messages)

                    




