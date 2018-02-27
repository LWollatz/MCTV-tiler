"""maketiles
creates tiles for MCTV
"""
import sys
import os
import numpy as np
from .jsonhandler import *
from .vgireader import *
from PIL import Image
from math import ceil, log
import logging

#Logger.propagate = True
stepX = 256 #tile size X
stepY = 256 #tile size Y

def flt(x):
    """float array from np array"""
    return float(x)
flt = np.vectorize(flt)

def npint(x):
    """int array from np array"""
    return int(x)
npint = np.vectorize(npint)

def getoutpath(filepath,ftype,num="0000"):
    """get the output path for the tiles"""
    a = filepath.rindex("\\")
    b = filepath.rindex(".")
    filename = filepath[a:b]
    if ftype == "raw":
        outpath = filepath[:a] + "\\.previews\\" + str(num)
    else:
        outpath = filepath[:a] + "\\.previews\\" + filename
    return outpath

def maketilesImage(filepath,minval,maxval,ftype="image",rawdata={"snum":"0001","start":0,"length":1,"bits":32,"ntype":"f"}):
    """open the file and save tiles in a subdir of the outdir specified
    filepath     string  path to the image file
    minval       float  minimum pixel value to use for the mapping (i.e.
                        maps to 0 in 8-bit)
    minval       float  maximum pixel value to use for the mapping (i.e.
                        maps to 255 in 8-bit)
    ftype        string  "image" or "raw" to tell the function, what type
                         of file to expect
    rawdata      dictionary  provides all the details required when a raw
                             file is given rather than an image file
    - "snum"     string  subfolder to save tiles to
    - "start"    integer  first byte to read
    - "length"   long  number of pixel to read
    - "bits"     integer  number of bits per pixel/voxel
    - "ntype"    string  n[umber]type string for converting the bytes into
                         numbers
    - "width"
    - "height"
    """
    verbose=False
    # open the image passed
    logging.info("attempt opening " + filepath)
    if ftype == "raw":
        imarray = readRAW(filepath,rawdata["start"],rawdata["length"],rawdata["bits"],rawdata["ntype"],rawdata["width"],rawdata["height"])
        imarray = flt(imarray)
        maxX,maxY = int(rawdata["width"]),int(rawdata["height"])
        outpath = getoutpath(filepath,ftype,rawdata["snum"])
    else:
        img = Image.open(filepath)
        if img.mode == "F;32BF":
            img.mode = "F"
        logging.debug("attempt succesful")
        imarray = flt(np.array(img))
        maxX,maxY = img.size
        outpath = getoutpath(filepath,ftype)
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    
    logging.debug("maxX:%d, maxY:%d, stepX:%d, stepY:%d", maxX, maxY, stepX, stepY)
    maxZoomlevel = int(ceil(log(max(float(maxX)/stepX,float(maxY)/stepY))/log(2)));
    logging.debug("maxZoomlevel: %d", maxZoomlevel)
    # adjust image values to 0 to 255 range for 24bit RGB conversion
    logging.debug("minval %d >= %d", np.min(imarray), minval)
    logging.debug("maxval %d <= %d", np.max(imarray), maxval)
    logging.debug(str(imarray[:500][:500]))
    imarray -= minval
    imarray /= float(maxval-minval)
    imarray *= 255
    imarray = npint(imarray)
    if verbose:
        logging.debug("minval %d (expected %d)", np.min(imarray), 0)
        logging.debug("maxval %d (expected %d)", np.max(imarray), 255)
        logging.debug(str(imarray[:500][:500]))
    img = Image.fromarray(imarray)
    # create the tiles
    centrestrip = None
    for zoomlevel in range(maxZoomlevel+1)[::-1]:
        for x in range(0,maxX,stepX):
            for y in range(0,maxY,stepY):
                xs = stepX;
                ys = stepY;
                
                x2 = x+xs;
                if (x2 >= maxX):
                        xs = maxX - 1 - x
                y2 = y+ys;
                if (y2 >= maxY):
                        ys = maxY - 1 - y
                logging.debug("x: %d, y: %d, xs: %d, ys: %d, maxX: %d, maxY: %d", x, y, xs, ys, maxX, maxY)
                tim = img.convert("RGB")
                tim = tim.crop((x, y, x+xs, y+ys))
    # save the tiles
                fout = open(outpath + "\\" + str(zoomlevel)+"-"+str(x//stepX)+"-"+str(y//stepY)+".jpg","wb")
                tim.save(fout,"JPEG")
                fout.close()

    # for last zoom level, save crossectional center strip
        centrestrip = img.convert("RGB")
        centrestrip = centrestrip.crop((0, int(maxY/2), maxX, int(maxY/2)+1))
        
    # scale image
        img.thumbnail((maxX//2,maxY//2), Image.ANTIALIAS)
        maxX,maxY = img.size
    return outpath, centrestrip

def imgFromFiles(files):
    for fileName in files:
        a = fileName.rindex(".")
        fileEnding = fileName[a+1:]
        if fileEnding in ["tif","jpg","png","tiff"]:
            filelist.append(fileName)
            logging.debug("choose " + fileName)
        else:
            logging.debug("ignore " + fileName + " " + fileEnding)
    return filelist

def imgFromFolder(path):
    """get all image files in a folder (not including sub-directories)"""
    filelist = []
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
    return imgFromFiles(files)

def imgFromPath(path):
    """get all image files on a path (including sub-directories)"""
    filelist = []
    for root, dirs, files in os.walk(path):
        filelist = filelist + imgFromFiles(files)
    return filelist

def propertiesFromImg(filepath):
    """get main properties from an image"""
    pMax = 0
    pMin = 0
    pWidth = 0
    pHeight = 0
    img = Image.open(open(filepath,"rb"))
    if img.mode == "F;32BF":
            img.mode = "F"
    pWidth, pHeight = img.size
    logging.debug(str(img))
    #imarray = np.array(img)
    #logging.debug(str(imarray))
    #imarray = flt(imarray)
    #pMin = np.min(imarray)
    #pMax = np.max(imarray)
    pMin=0
    pMax=255

    a = filepath.rindex("\\")
    b = filepath.rindex(".")
    filename = filepath[a:b]
    
    return {"Width":pWidth, "Height":pHeight, "Min":pMin, "Max":pMax, "filepath":filepath, "filename":filename}

def MinMaxFromImg(filepath):
    """get the minimum and maximum pixel value from an image"""
    pMax = 0
    pMin = 0
    img = Image.open(open(filepath,"rb"))
    if img.mode == "F;32BF":
            img.mode = "F"
    logging.debug(str(img))
    imarray = np.array(img)
    imarray = flt(imarray)
    pMin = np.min(imarray)
    pMax = np.max(imarray)
    
    return pMin,pMax

def MajRange(points,percentage):
    """finds the minimum and maximum so that percentage percent of the
    points are included in that range."""
    points.sort()
    lowid = int(0.5*(1-percentage)*len(points))
    higid = -1*lowid
    logging.debug("Rnd min:%d, max:%d",points[0],points[-1])
    return float(points[lowid]),float(points[higid])

def initiateThumbnails(filepath,imgcount,imsize):
    """creates a black image of the size required for the cross-sectional
    thumbnail so taht individual parts of the image can be added later"""
    width = int(imsize)
    height = int(imgcount)
    while width > 256:
        width = width/2
        height = height/2
    imarray = np.zeros((int(height)+1,int(width)))
    img = Image.fromarray(imarray)
    img = img.convert("RGB")
    fout = open(filepath,"wb")
    img.save(fout,"JPEG")
    fout.close()
    return None

def addtoThumbnail(filepath,imgcount,imgtotal,stripe):
    """loads cross-sectional thumbnail and adds stripe specified"""
    
    img = Image.open(filepath)
    img = img.convert("RGB")
    imarray = np.array(img)
    maxX,maxY = img.size
    posY = int(maxY*imgcount/imgtotal)
    #TODO: fix issue if not all images have the same size...
    imarray[posY][:][:] = np.array(stripe)[0][:][:]
    img = Image.fromarray(imarray)
    fout = open(filepath,"wb")
    img.save(fout,"JPEG")
    fout.close()
    return None
