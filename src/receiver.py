import sqlite3
from dotenv import dotenv_values
import subprocess
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../.env')

class msg_receiver():
    def __init__(self):
        # holds the 10 most recent messages from newest to oldest
        self.recent_messages = []

    # read the chat.db file and return new messages in format [sender_number1: message1, ...]
    def read(self):
        # query for messages
        con = sqlite3.connect(env['CHAT_DB'])
        cur = con.cursor()
        res = cur.execute(f"""
                            SELECT m.rowid, m.attributedBody,
                            CASE WHEN m.is_from_me THEN {env['MY_NUMBER']} ELSE h.id END
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
                        print(f'Error with message {ROWID}: {err}')
                    else:
                        output = result.stdout.decode()
                        # clean up typedstream output
                        msg_text = output.split('(')[1].split(')\n')[0]
                        msg = f"{sender}: {msg_text}"
                        # check if message is new
                        if msg not in self.recent_messages:
                            messages.append(msg)
                            self.recent_messages.insert(0, msg)
                            if len(self.recent_messages) > 10:
                                 self.recent_messages.pop(10)
        for message in self.recent_messages:
            print(message)
        print('----')
        return messages
                    

              


