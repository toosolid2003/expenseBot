#encoding: utf-8
from PIL import Image
from io import BytesIO
import os

def createImagePath(exp):
    '''Creates an image from the byte array stored in the expense object (exp.receipt).
    The path to this image can then be sent to IQ Navigator as a receipt.
    Input: an expense object
    Output: path to the image file'''

    img = Image.open(BytesIO(exp.receipt))
    filename = 'receipt.png'
    img.save(filename)

    filepath = os.getcwd() + '/' + filename

    return filepath
