from PIL import Image, ImageFilter, ImageChops
import numpy as np
import sys
from glob import glob
import os

out_dir = "data"

def selectColor(image, color):
    size = image.size
    color = Image.new('RGBA', size, color)
    blank = Image.new('L', size, (0))
    diff = ImageChops.difference(image, color)
    r,g,b,_ = diff.split()
    maxDiff = ImageChops.lighter(r,ImageChops.lighter(g, b))
    result = maxDiff.point(lambda x : 255 if x > 32 else 0, mode='1').convert('L')
    return ImageChops.invert(result)


def getImgTraffic(file):
    img = Image.open(file)
    g = selectColor(img, (22,224,152))
    y = selectColor(img, (255,207,67))
    r = selectColor(img, (242,78,66))
    m = selectColor(img, (169,39,39))
    g = np.sum(np.array(g))
    y = np.sum(np.array(y))
    r = np.sum(np.array(r))
    m = np.sum(np.array(m))
    
    avg = -1
    max_value = -1
    if g+y+r+m > 0:
        avg = (g*0 + y *1 + r *2 + m*3) / (g+y+r+m)
        max_value = [g,y,r,m].index(max([g,y,r,m]))
    return avg, max_value

def extractTraffic(file):
    avg, max_value = getImgTraffic(file)
    name = os.path.basename(file).split('.')[0]
    day, hour, minute = name.split("-")
    hour = int(hour)
    if minute.endswith('pm') and hour != 12:
        hour += 12
    return {'avg':[avg],'max':[max_value], 'day':[day],'hour':[hour]}
