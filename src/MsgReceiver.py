import sqlite3
from dotenv import dotenv_values
import subprocess
import os
from karellen.sqlite3 import Connection
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../.env')

class MsgReceiver():
    

    def __init__(self):
        # Open chat.db file
        self.con = Connection(env['CHAT_DB'])
        self.cur = self.con.cursor()
        
        with open (f"{dir_path}/../chat/contacts.json", "r") as contactsfile:
            self.contacts = json.load(contactsfile)

        # Queue that holds the 10 most recent messages from newest to oldest
        self.recent_messages = []
        self.read()
        self.new_messages = []

        self.watching = False
        
        

    # read the chat.db file and return new messages in format [sender_number1: message1, ...]
    def read(self):
        # query for messages
        res = self.cur.execute(f"""
                            SELECT m.rowid, m.attributedBody,
                            CASE WHEN m.is_from_me THEN '{env['MY_NUMBER']}' ELSE h.id END
                            FROM message AS m
                            LEFT JOIN handle AS h ON m.handle_id = h.rowid
                            WHERE cache_roomnames='{env['CHAT_ID']}'
                            ORDER BY m.date desc
                            LIMIT 10
        """)

        messages = []
        rows = res.fetchall()
        rows.reverse()
        # 'attributedBody' column has message content, but it's encoded so we have to clean it up
        for (ROWID, attributedBody, sender) in rows:
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
                        if msg not in self.recent_messages:
                             messages.insert(0, msg)
        self.new_messages = messages
        self.recent_messages = (self.new_messages + self.recent_messages)[:10]
        self.watching = False
    
    def get_new_messages(self):
        ret = self.new_messages
        self.new_messages = []
        return ret
    
    def has_new_messages(self):
         return len(self.new_messages) != 0

    # wait for changes then read them
    def watch_db(self):
         self.watching = True
         self.con.set_update_hook(self.read())
                    

              


