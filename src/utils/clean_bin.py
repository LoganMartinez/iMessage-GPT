# this solves bin files being leftover after an interuption
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
def clean_bin():
    binfiles = os.listdir(f'{dir_path}/../../bin')
    for file in binfiles:
        if file != '.gitkeep':
            os.remove(f'{dir_path}/../../bin/{file}')