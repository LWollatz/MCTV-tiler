import os
import logging
import numpy as np
from struct import unpack
from random import randint

def vgiFromFolder(path):
    filelist = []
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
    for fileName in files:
        a = fileName.rindex(".")
        fileEnding = fileName[a+1:]
        if fileEnding in ["vgi"]:
            filelist.append(fileName)
            logging.debug("choose " + fileName)
        else:
            logging.debug("ignore " + fileName + " " + fileEnding)
    return filelist

def readRAW(fin,start,length,bits,ntype,width,height):
    start = int(start)
    length = int(length)
    bits = int(bits)
    width = int(width)
    height = int(height)
    f1 = open(fin,'rb')
    f1.seek(int(start))
    pixels = f1.read(int(length))
    pixels = unpack(str(int(length*8/bits))+ntype,pixels)
    pixels = np.array(pixels)
    #print len(pixels), width, height
    return pixels.reshape((width,height))

def getRandomValFromRAW(fin,bits,ntype,length,count):
    """
    fin = file input
    bits = bits per pixel
    ntype = number type of pixel
    length = numper of pixel in file
    count number of pixels to read"""
    bits = int(bits)
    length = int(length)-1
    count = int(count)
    f1 = open(fin,'rb')
    ans = []
    for i in range(count):
        pxid = randint(0,length)
        byteid = pxid*bits/8
        f1.seek(int(byteid))
        pixel = f1.read(int(bits/8))
        pixel = unpack(str(ntype),pixel)
        ans.append(pixel[0])
    return ans

def readVGI(fin):
    
    f1 = open(fin,'r')
    lines = f1.readlines()
    f1.close()

    level1 = ""
    level2 = ""
    l3dic = {}
    l2dic = {}
    l1dic = {}
        
    for line in lines:
        if line.startswith("{"):
            #new level 1 heading
            if level1 != "":
                l2dic[level2] = l3dic
                l1dic[level1] = l2dic
            level1 = line.lstrip("{").rstrip("}\n")
            level2 = ""
            l3dic = {}
            l2dic = {}
        elif line.startswith("["):
            #new level 2 heading
            if level2 != "":
                l2dic[level2] = l3dic
            level2 = line.lstrip("[").rstrip("]\n")
            l3dic = {}
        else:
            #key-value pair
            parts = line.rstrip("\n").split(" = ")
            key = parts[0]
            value = parts[1]
            #try splitting value into number list:
            numbers = value.split(" ")
            try:
                numbers = [float(num) for num in numbers]
                value = numbers
                if len(value) == 1:
                    value = value[0]
            except ValueError:
                pass
            l3dic[key] = value
    l2dic[level2] = l3dic
    l1dic[level1] = l2dic
    return l1dic

if __name__ == "__main__":
    json = readVGI("20170222_MEDX_1445_AN001ciii_.vgi")
    print json
    print "size", json["volume1"]["representation"]["size"]
    print "bits", json["volume1"]["representation"]["bitsperelement"]
    print "min", json["volume1"]["representation"]["datarange"][0]
    print "max", json["volume1"]["representation"]["datarange"][1]
    print "res", json["volumeprimitive1"]["geometry"]["resolution"][0]
    print "z-res", json["volumeprimitive1"]["geometry"]["resolution"][2]
    print "unit", json["scene"]["resolution"]["unit"]
