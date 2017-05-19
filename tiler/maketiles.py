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
root = "L:\\mydocuments\\PhD\\MCTV\\TileMaker\\testing\\tiles\\"
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
    a = filepath.rindex("\\")
    b = filepath.rindex(".")
    filename = filepath[a:b]
    if ftype == "raw":
        outpath = filepath[:a] + "\\.previews\\" + str(num)
    else:
        outpath = filepath[:a] + "\\.previews\\" + filename
    return outpath

def maketilesImage(filepath,minval,maxval,ftype="image",rawdata={"snum":"0001","start":0,"length":1,"bits":32,"ntype":"f"}):
    """open the file and save tiles in a subdir of the outdir specified"""
    verbose=False
    # open the image passed
    logging.info("attempt opening " + filepath)
    if ftype == "raw":
        imarray = readRAW(filepath,rawdata["start"],rawdata["length"],rawdata["bits"],rawdata["ntype"],rawdata["width"],rawdata["height"])
        imarray = flt(imarray)
        maxX,maxY = int(rawdata["width"]),int(rawdata["height"])
    else:
        img = Image.open(filepath)
        if img.mode == "F;32BF":
            img.mode = "F"
        logging.debug("attempt succesful")
        imarray = flt(np.array(img))
        maxX,maxY = img.size
    # get image information
    outpath = getoutpath(filepath,ftype,rawdata["snum"])
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    
    if verbose:
        logging.debug("maxX:%d, maxY:%d, stepX:%d, stepY:%d", maxX, maxY, stepX, stepY)
    maxZoomlevel = int(ceil(log(max(float(maxX)/stepX,float(maxY)/stepY))/log(2)));
    logging.debug(str(maxZoomlevel))

    ##fout = open(outpath + "\\original.jpg","wb")
    ##imgX = img.convert("L")
    ##imgX.save(fout,"JPEG")
    ##fout.close()
        
    # balance image
    #img = img.convert("L")
    
    logging.debug("minval" + str(np.min(imarray)) + str(minval))
    logging.debug("maxval" + str(np.max(imarray)) + str(maxval))
    logging.debug(str(imarray[:500][:500]))
    imarray -= minval
    imarray /= float(maxval-minval)
    imarray *= 255
    imarray = npint(imarray)
    if verbose:
        print("minval", np.min(imarray), 0)
        print("maxval", np.max(imarray), 255)
        print(imarray[:500][:500])
    img = Image.fromarray(imarray)
    #imgX = img.convert("RGB")
    #imarray = np.array(imgX)
    #if verbose:
    #    print("minval", np.min(imarray))
    #    print("maxval", np.max(imarray))
    #    print(imarray[:500][:500])

    #fout = open(outpath + "\\balanced.jpg","wb")
    #imgX = img.convert("RGB")
    ##imgX.save(fout,"JPEG")
    ##fout.close()
    # create the tiles
    centrestrip = None
    for zoomlevel in range(maxZoomlevel+1)[::-1]:
        for x in range(0,maxX,stepX):
            for y in range(0,maxY,stepY):
                xs = stepX;
                ys = stepY;
                #zs = stepZ;
                
                x2 = x+xs;
                if (x2 >= maxX):
                        xs = maxX - 1 - x
                y2 = y+ys;
                if (y2 >= maxY):
                        ys = maxY - 1 - y
                #z2 = z+zs;
                #if (z2 > maxZ):
                #    zs = maxZ - z
                if verbose:
                    print(x, y, xs, ys, maxX, maxY)
                tim = img.convert("RGB")
                tim = tim.crop((x, y, x+xs, y+ys))
                #tiles are scaled by height
                #=> if height is smaller than 256, need to add y-padding
                #   OR fix MCTV to work with %
    # save the tiles
                fout = open(outpath + "\\" + str(zoomlevel)+"-"+str(x//stepX)+"-"+str(y//stepY)+".jpg","wb")
                #table = [i/256 for i in range(65536)]
                #tim = tim.point(table, 'L')
                tim.save(fout,"JPEG")
                fout.close()

        #TODO: for last zoom level, save crossectional center strip
        centrestrip = img.convert("RGB")
        centrestrip = centrestrip.crop((0, int(maxY/2), maxX, int(maxY/2)+1))
        #TODO: save
        
    # scale image
        img.thumbnail((maxX//2,maxY//2), Image.ANTIALIAS)
        maxX,maxY = img.size
    return outpath, centrestrip


def imgFromFolder(path):
    filelist = []
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
    for fileName in files:
        a = fileName.rindex(".")
        fileEnding = fileName[a+1:]
        if fileEnding in ["tif","jpg","png","tiff"]:
            filelist.append(fileName)
            logging.debug("choose " + fileName)
        else:
            logging.debug("ignore " + fileName + " " + fileEnding)
    return filelist

def imgFromPath(path):
    filelist = []
    for root, dirs, files in os.walk(path):
        print(dirs)
        for fileName in files:
            a = fileName.rindex(".")
            fileEnding = fileName[a+1:]
            if fileEnding in ["tif","jpg","png","tiff"]:
                filelist.append(fileName)
                logging.debug("choose " + fileName)
            else:
                logging.debug("ignore " + fileName + " " + fileEnding)
    return filelist

def propertiesFromImg(filepath):
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
    while width > 255:
        width = width/2
        height = height/2
    imarray = np.zeros((int(height),int(width)))
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
    imarray[posY][:][:] = np.array(stripe)[0][:][:]
    img = Image.fromarray(imarray)
    fout = open(filepath,"wb")
    img.save(fout,"JPEG")
    fout.close()
    return None

###read commandline input
##argdic = {"executionpath":sys.argv.pop(0), "-v":False}
##curkey = ""
##curval = ""
##
##if __name__ == "__main__":
##    #    default arguments for testing
##    argdic["-f"] = "L:\\mydocuments\\PhD\\MCTV\\TileMaker\\testing\\Sampleblock\\"
##    #argdic["-f"] = "L:\\mydocuments\\PhD\\MCTV\\TileMaker\\testing\\Sampleblock\\DigiSens_20140530_HUTCH_581_MJr_0914546B_0481.tif"
##    #argdic["-f"] = "L:\\mydocuments\\PhD\\MCTV\\TileMaker\\testing\\Figure8g.JPG"
##    argdic["-o"] = "SFCT"
##    argdic["-v"] = False
##    argdic["-h"] = False
##    argdic["--help"] = False
##
###print time()
##for arg in sys.argv:
##    if arg.startswith("-"):
##        if curval == "":
##            argdic[curkey] = True
##        else:
##            argdic[curkey] = curval
##        curval = ""
##        curkey = arg
##    else:
##        curval = arg
##if curkey != "":
##    if curval == "":
##        argdic[curkey] = True
##    else:
##        argdic[curkey] = curval
##
##if argdic["--help"] or argdic["-h"]:
##    print "maketiles help"
##    print "-f filenpath and filename"
##    print "-h --help shows this help"
##    print "-o output filenpath"
##    print "-v if set, displays debug information"
##else:
##    images = imgFromFolder(path = argdic["-f"])
##    images = [propertiesFromImg(argdic["-f"] + image) for image in images]
##    maxval = max([image["Max"] for image in images])
##    minval = min([image["Min"] for image in images])
##    print minval, maxval
##    jsn = newjson({"width":images[0]["Width"], "height":images[0]["Height"]})
##    writejson(root + argdic["-o"]+"\\JSONinfo.txt",jsn)
##    for image in images:
##        maketilesImage(image["filepath"],argdic["-o"],minval,maxval,verbose=argdic["-v"])
##        print root + argdic["-f"]+"\\.previews\\JSONinfo.txt"
##        jsn = openjson(root + argdic["-o"]+"\\JSONinfo.txt")
##        jsn = addslide(jsn,"../" + argdic["-o"]+"/"+image["filename"].replace("\\","/").lstrip("/")) #.lstrip(root).replace("\\","/")
##        writejson(argdic["-f"]+"\\.previews\\JSONinfo.txt",jsn)

