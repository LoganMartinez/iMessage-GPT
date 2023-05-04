from receiver import msg_receiver
from utils.clean_bin import clean_bin

clean_bin()

receiver = msg_receiver()
while True:
    print(receiver.read())

