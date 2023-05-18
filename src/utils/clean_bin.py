import os
from dotenv import dotenv_values

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../../.env')

# this solves bin files being leftover after an interuption
def clean_bin():
    binfiles = os.listdir(f'{dir_path}/../../bin')
    for file in binfiles:
        if file != '.gitkeep':
            os.remove(f'{dir_path}/../../bin/{file}')

def clean_pictures():
    pictures = os.listdir(f'{env["PICTURES_FOLDER"]}/gpt')
    for file in pictures:
        os.remove(f'{env["PICTURES_FOLDER"]}/gpt/{file}')