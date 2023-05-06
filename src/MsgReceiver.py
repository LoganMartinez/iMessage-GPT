import sqlite3
from dotenv import dotenv_values
import subprocess
import os
import json
import sqlite3
import fswatch.libfswatch as fsw
from threading import Thread
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../.env')

class MsgReceiver():
    
    def __init__(self):
        with open (f"{dir_path}/../chat/contacts.json", "r") as contactsfile:
            self.contacts = json.load(contactsfile)

        # Queue that holds the 10 most recent messages from newest to oldest
        self.recent_messages = []
        self.new_messages = []

    # read the chat.db file and return new messages in format [sender_number1: message1, ...]
    def read(self):
        print('reading...')
        con = sqlite3.connect(env['CHAT_DB'])
        cur = con.cursor()
        # query for messages
        res = cur.execute(f"""
                            SELECT m.rowid, m.attributedBody,
                            CASE WHEN m.is_from_me THEN '{env['MY_NUMBER']}' ELSE h.id END
                            FROM message AS m
                            LEFT JOIN handle AS h ON m.handle_id = h.rowid
                            WHERE cache_roomnames='{env['CHAT_ID']}'
                            ORDER BY m.date desc
                            LIMIT 10
        """)

        
        rows = res.fetchall()
        con.close()
        rows.reverse()

        messages = []
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
        self.new_messages = messages + self.new_messages
        self.recent_messages = (self.new_messages + self.recent_messages)[:10]
        

    def get_new_messages(self):
        ret = self.new_messages
        self.new_messages = []
        return ret
    

    def has_new_messages(self):
         return len(self.new_messages) != 0
    

    # blocking call that waits for changes to chat.db and reads them
    # this never ends, so calling this function should be put in a separate thread
    def watch_db(self):
        def callback(events, event_num):
            # TODO: check how the file has changed
            self.read()

        # initial read to set recent_messages
        self.read()
        # new_messages will be equal to recent messages on first read, so it needs to be cleared
        self.new_messages = []

        # setup monitor
        fsw.fsw_init_library()
        handle = fsw.fsw_init_session(1)
        fsw.fsw_add_path(handle, "/Users/logan/Desktop/test.txt".encode('UTF-8'))
        c_callback = fsw.cevent_callback(callback)
        fsw.fsw_set_callback(handle, c_callback)

        # start monitoring file for changes
        fsw.fsw_start_monitor(handle)

receiver = MsgReceiver()
thread = Thread(target=receiver.watch_db, daemon=True)
thread.start()
while True:
     print(receiver.get_new_messages())
     time.sleep(10)