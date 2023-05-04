import sqlite3
from dotenv import dotenv_values
import subprocess
import os

env = dotenv_values('../.env')

class msg_receiver():
    def __init__(self):
        self.recent_messages = []

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
        # 'attributedBody' column has message content, but it's encoded so we have to clean it up
        for (ROWID, attributedBody, sender) in res.fetchall():
              if attributedBody:
                    filename = f'../bin/{ROWID}.bin'
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
                        # clean up output -- there's probably a way to break this if someone sends a 
                        # really specific message, but at worst the message would just be truncated
                        msg_text = output.split('(')[1].split(')\n')[0]
                        msg = f"{sender}: {msg_text}"
                        if msg not in self.recent_messages:
                            messages.append(msg)
                            self.recent_messages.append(msg)
        while len(self.recent_messages) > 10:
            self.recent_messages.pop(0)
        return messages
                    

              


