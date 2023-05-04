import os

def clean_bin():
    binfiles = os.listdir('../bin')
    for file in binfiles:
        os.remove(f'../bin/{file}')