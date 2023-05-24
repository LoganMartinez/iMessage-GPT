from PIL import Image
import random
import os
from dotenv import dotenv_values
import math

# the width and height of the final image
finalDim = 256

dir_path = os.path.dirname(os.path.realpath(__file__))
env = dotenv_values(f'{dir_path}/../../.env')

def generateTemplate(imagePath, objectSize=.3):
    """From an image of an object, creates a new wider canvased image with the object in a
    random part of the frame and returns the path to that image. This allows more variety 
    when dalle generates images from a reference image. objectSize is a value between 0 and 1 
    which represents how much of the frame the object should take up, with 1 meaning the object 
    takes up the entire frame."""
    assert(objectSize > 0 and objectSize <= 1) 
    
    with Image.open(imagePath) as oimg:
        # resize object so it takes up objectSize amount of the frame
        (owidth, oheight) = oimg.size
        # first potential scalar would make the object take up objectSize % of the image, but this may 
        # be too big if width and height are too disproportionate
        oscalar1 = math.sqrt((finalDim ** 2) * objectSize / (owidth * oheight))
        # second potential scalar would make one of the dimensions of the object take up the entire
        # dimension of the image
        oscalar2 = finalDim / max(owidth, oheight)
        # use the smaller of these two values to ensure that the object never exceeds the size of the final image
        oscalar = min(oscalar1, oscalar2)
        (new_owidth, new_oheight) = ((int(oscalar*owidth), int(oscalar*oheight)))
        oimg = oimg.resize((new_owidth, new_oheight))
        xoffset = random.randint(0, finalDim-new_owidth)
        yoffset = random.randint(0, finalDim-new_oheight)

        nimg = Image.new('RGBA', (finalDim, finalDim), (0,0,0,0))
        nimg.paste(oimg, (xoffset, yoffset, xoffset+new_owidth, yoffset+new_oheight))
        outfile_name = imagePath.split('/')[-1]
        outfile_path = f'{env["PICTURES_FOLDER"]}/gpt/templates/{outfile_name}'
        nimg.save(outfile_path)
        return outfile_path

if __name__ == '__main__':
    generateTemplate('/Users/logan/Pictures/references/example.png', objectSize=.1)

