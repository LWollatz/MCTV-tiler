"""maketiles
creates tiles for MCTV
"""
from __future__ import absolute_import, unicode_literals
from .celery import app
from celery.utils.log import get_task_logger
from .jsonhandler import *
from .maketiles import *
from .vgireader import *
import ctypes
import logging

logger = get_task_logger(__name__)

@app.task
def add(x,y):
    """adding - for testing purposes"""
    return x+y

@app.task(ignore_result=True)
def tile(image,directory,sliceNum,imgtotal,minval,maxval,ftype="image",rawdata={}):
    outdir, centrestrip = maketilesImage(image["filepath"],minval,maxval,ftype,rawdata)
    print(directory+"\\.previews\\infoJSON.txt")
    jsn = openjson(directory+"\\.previews\\infoJSON.txt")
    outdir = outdir.replace("\\","/").replace("//","/").lstrip("/")+"/"
    outdir = outdir.replace("C:/data","../data").replace("c:/data","../data")
    jid = tile.request.id
    logging.info("current jobid: %s",jid)
    jsn = addslide(jsn,outdir,jid) #would want relative path from MCTV here - requires MCTV to be set up first
    writejson(directory+"\\.previews\\infoJSON.txt",jsn)
    addtoThumbnail(directory+"\\.previews\\tc.jpg",sliceNum,imgtotal,centrestrip)
    return None

@app.task(ignore_result=True)
def readdir(directory):
    #files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
    #TODO: more efficient to pass list of files instead of path?
    images = imgFromFolder(path = directory)
    headers = vgiFromFolder(path = directory)
    surfaces = stlFromFolder(path = directory)
    if len(headers) > 1:
        logging.info("Multiple headers found - choosing first header by default.")
    if len(headers) < 1:
        logging.info("No vgi header found.")
        if len(images) > 1:
            logging.info("found %d images - extracting properties.",len(images))
            _readdirSTACK(directory,images)
        elif len(surfaces) >= 1:
            logging.info("found %d surface files - saving.",len(surfaces))
            _readdirSTL(directory,surfaces)
        else:
            logging.warn("No image data found - no preview will be created!")
    else:
        _readdirRAW(directory,headers)
    
    return None

def _remoldjobs(jsndir):
    logging.warn("checking for %s",jsndir)
    if os.path.isfile(jsndir):
        logging.warn("checking for old jobs in %s",jsndir)
        jsn = openjson(jsndir)
        for s in jsn["slides"]:
            if "jobid" in s.keys():
                jid = s["jobid"]
                logging.info("removing old tiler job %s",jid)
                app.control.revoke(jid)
                #app.control.terminate(jid)
    return None

def _ensurePreviews(directory):
    fullpath = directory+"\\.previews"
    if not os.path.exists(fullpath):
        os.makedirs(fullpath)
    suc = ctypes.windll.kernel32.SetFileAttributesW(fullpath,0x02)
    if not suc:
        logging.error(ctypes.WinError())
    return None

def _readdirSTL(directory,files):
    _ensurePreviews(directory)
    infodir = directory+"\\.previews\\infoSTL.txt"
    #create list of images
    fout = open(infodir,"w")
    for f in files:
        logging.debug("%s",f)
        fout.write(f+"\n")
    fout.close()
    logging.info("List of all STLs created.")
    return None

def _readdirRAW(directory,headers):
    #read header file
    header = headers[0]
    vgidata = readVGI(directory + "\\" + header)
    filename = vgidata["volume1"]["file1"]["Name"]
    width, height, numSlices = vgidata["volume1"]["representation"]["size"]
    bits = vgidata["volume1"]["representation"]["bitsperelement"]
    minval = vgidata["volume1"]["representation"]["datarange"][0]
    maxval = vgidata["volume1"]["representation"]["datarange"][1]
    res = vgidata["volumeprimitive1"]["geometry"]["resolution"][0]
    zres = vgidata["volumeprimitive1"]["geometry"]["resolution"][2]
    unit = vgidata["scene"]["resolution"]["unit"]
    logging.warn("minval: " + str(minval) + ", maxval: " + str(maxval))
    #remove old jobs
    _ensurePreviews(directory)
    jsndir = directory+"\\.previews\\infoJSON.txt"
    _remoldjobs(jsndir)
    #determine value range of interest
    ntype = vgidata["volume1"]["representation"]["datatype"]
    if ntype == "float":
        ntype = "f"
    elif ntype == "double":
        ntype = "d"
    elif ntype == "int":
        ntype = "i"
    elif ntype == "unsigned int":
        ntype = "I"
    elif ntype == "short":
        ntype = "h"
    elif ntype == "unsigned short":
        ntype = "H"
    else:
        ntype = ntype[0]
    voxel = width*height*numSlices
    totsize = voxel*bits
    sample = getRandomValFromRAW(directory+"\\"+filename,bits,ntype,voxel,10000)
    minval,maxval = MajRange(sample,0.99)
    logging.warn("99% minval: " + str(minval) + ", maxval: " + str(maxval))
    #create json header
    jsn = newjson({"width":width, "height":height, "res":res, "zres":zres, "resunits":unit, "densmin":minval, "densmax":maxval, "densunit":str(int(bits))+"-bits"})
    writejson(jsndir,jsn)
    logging.info("JSON file created - starting image tiling.")
    #initiate Thumbnail
    initiateThumbnails(directory+"\\.previews\\tc.jpg",numSlices,width)
    #submit jobs for tiler
    sizeKB = totsize/8.0/1024.0
    logging.info("File to read: %s\n  with\n  %d voxel\n  %dKB size\n  %d  images",filename,voxel,sizeKB,numSlices)
    length = width*height*bits/8
    for Slice in range(int(numSlices)):
        startpos = int(Slice*length)
        snum = "%04d" % Slice
        
        rawdata={"snum":snum,"start":startpos,"length":int(length),"bits":bits,"ntype":ntype,"height":int(height),"width":int(width)}
        #tile.delay({"filepath":directory+"\\"+filename,"filename":filename},directory,minval,maxval,"raw",rawdata)
        jobvar = tile.apply_async([{"filepath":directory+"\\"+filename,"filename":filename},directory,Slice,numSlices,minval,maxval,"raw",rawdata],countdown=15,priority=2)
        jid = jobvar.task_id
        jsn = openjson(jsndir)
        jsn = addid(jsn,jid,path=getoutpath(directory+"\\"+filename,"raw",snum)) #store id instead of directory
        logging.debug("recorded %s",jid)
        writejson(jsndir,jsn)
    logging.info("All image tiling jobs queued.")
    return None

def _readdirSTACK(directory,images):
    images = [propertiesFromImg(directory + "\\" + image) for image in images]
    logging.info("properties of images extracted - creating JSON file.")
    #maxval = max([image["Max"] for image in images])
    #minval = min([image["Min"] for image in images])
    minval,maxval = MinMaxFromImg(images[int(len(images)/3)]["filepath"])
    min2,max2=MinMaxFromImg(images[int(2*len(images)/3)]["filepath"])
    maxval = max(maxval,max2)
    minval = max(minval,min2)
    logging.debug("minval: " + str(minval) + ", maxval: " + str(maxval))
    #check for old jobs
    jsndir = directory+"\\.previews\\infoJSON.txt"
    _remoldjobs(jsndir)
    #creating new json
    jsn = newjson({"width":images[0]["Width"], "height":images[0]["Height"]})
    _ensurePreviews(directory)
    writejson(jsndir,jsn)
    #initiate Thumbnail
    initiateThumbnails(directory+"\\.previews\\tc.jpg",len(images),images[0]["Width"])
    logging.info("JSON file created - starting image tiling.")
    #submitting jobs per slice to tiler
    Slice = 0
    for image in images:
        #jobvar = tile.delay(image,directory,minval,maxval)
        jobvar = tile.apply_async([image,directory,Slice,len(images),minval,maxval],countdown=15,priority=2)
        jid = jobvar.task_id
        jsn = openjson(jsndir)
        jsn = addid(jsn,jid,path=getoutpath(image["filepath"],"image")) #store id instead of directory
        writejson(jsndir,jsn)
        Slice += 1
    logging.info("All image tiling jobs queued.")
    return None
