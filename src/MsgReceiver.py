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
        
        with open (f"{dir_path}/../chat/contacts.json", "r") as contactsfile:
            self.contacts = json.load(contactsfile)

        with open (f"{dir_path}/../chat/chatIds.json", "r") as idsfile:
            self.chatIds = json.load(idsfile)['chatIds']

        # dict that holds queues that hold the 10 most recent messages from newest to oldest
        self.recent_messages = {}
        for id in self.chatIds:
            self.recent_messages[id] = []
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
                                ORDER BY m.date desc
                                LIMIT 10
            """)
            rowsForThisId = res.fetchall()
            rowsForThisId.reverse()
            
            messages = []
            # 'attributedBody' column has message content, but it's encoded so we have to clean it up
            for (ROWID, attributedBody, sender, cid) in rowsForThisId:
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
                          contact = self.contacts[sender] if sender in self.contacts.keys() else sender
                          msg = f"{contact}: {msg_text}"
                          if msg not in self.recent_messages[chatId]:
                              messages.insert(0, msg)
            self.new_messages[chatId] = messages
            self.recent_messages[chatId] = (self.new_messages[chatId] + self.recent_messages[chatId])[:10]
    
    def get_new_messages(self):
        ret = self.new_messages
        self.new_messages = {}
        return ret
    
    def has_new_messages(self):
        return any([len(self.new_messages[key]) != 0 for key in self.new_messages.keys()])
    

if __name__ == '__main__':
    receiver = MsgReceiver()
    receiver.read()
    for id in receiver.chatIds:
        print(receiver.recent_messages[id])

                    

              


