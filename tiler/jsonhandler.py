"""MCTV JSON HANDLER"""
import json

def openjson(filename):
    """opens the json file "filename" and
    returns a python object with the content of that file"""
    f1 = open(filename,"r")
    lines = f1.readlines()
    f1.close()
    lines = "".join(lines).replace("\n","")
    jsn = json.loads(lines)
    return jsn

def newjson(dic):
    """takes a dictionary and returns a json object with the main
    MCTV things defined.
    The dictionary contains:
    "height" (REQUIRED)    height of the images
    "width"  (REQUIRED)    width of the images
    "densmin" (optional)   density value of minimum pixel value (defaults to 0)
    "densmax" (optional)   density value of maximum pixel value (defaults to 255)
    "densunit" (optional)  unit of density values (defaults to 8-bit)
    "res" (optional)       resolution per pixel in-plane
    "zres" (optional)      resolution per pixel inter-planes
    "resunits" (optional)  units of the resolution (defaults to micro-meter)
"""
    jsn = {"height":dic["height"],"width":dic["width"],"slides":[]}
    if "densmin" in dic:
        jsn["densmin"] = dic["densmin"]
    else:
        jsn["densmin"] = 0
    if "densmax" in dic:
        jsn["densmax"] = dic["densmax"]
    else:
        jsn["densmax"] = 255
    if "densunit" in dic:
        jsn["densunit"] = dic["densunit"]
    else:
        jsn["densunit"] = "8-bit"
    if "res" in dic:
        jsn["res"] = dic["res"]
    else:
        jsn["res"] = 1
    if "zres" in dic:
        jsn["zres"] = dic["zres"]
    else:
        jsn["zres"] = 1
    if "resunits" in dic:
        jsn["resunits"] = dic["resunits"]
    else:
        jsn["resunits"] = "px"
    return jsn


def addslide(jsn,path,jid=0,height=0,width=0):
    """add a slide to the jsonInfo.txt replacing the job-id specified
    or sorting it by name, returning the json object with the added slide"""
    if width == 0:
        width = jsn["width"]
    if height == 0:
        height = jsn["height"]
    path = path.replace("\\","/").replace("//","/").lstrip("/")+"/"
    path = path.replace("C:/data","../data").replace("c:/data","../data")
    slide = {"path":path, "height":height, "width":width}
    slides = jsn["slides"]
    if jid == 0: #old case - no job id provided
        newslides = []
        cntr = 0
        hasAppended = False
        for s in slides:
            if s["path"] < slide["path"]:
                newslides.append(s)
            else:
                newslides.append(slide)
                newslides += slides[cntr:]
                hasAppended = True
                break
            cntr += 1
        if not hasAppended:
            newslides.append(slide)
    else: #new solution: replace slide with same jobid
        newslides = slides
        cntr = 0
        slideid=len(slides)
        for s in slides:
            if s["path"] == None:
                if s["jobid"] == jid:
                    slideid = cntr
                    break
            cntr += 1
        if slideid != len(slides):
            newslides[slideid] = slide
    jsn["slides"] = newslides
    return jsn

def addid(jsn,jid,path=None):
    """add slide with job-id"""
    width = jsn["width"]
    height = jsn["height"]
    if path != None:
        path = path.replace("\\","/").replace("//","/").lstrip("/")+"/"
        path = path.replace("C:/data","../data").replace("c:/data","../data")
    slide = {"jobid":jid, "path":path, "height":height, "width":width}
    slides = jsn["slides"]
    newslides = slides
    newslides.append(slide)
    jsn["slides"] = newslides
    return jsn


def writejson(filename,jsn):
    """write json object to file"""
    f1 = open(filename,"w")
    f1.write(json.dumps(jsn, indent=4, separators=(',', ': ')))
    f1.close()
    return None

if __name__ == "__main__":
    """run tests"""
    jsn = openjson("testing\\tiles\\SFCT\\JSONinfo.txt")
    addslide(jsn,"../MCTV/exampleblock/_00185")
    writejson("testing\\tiles\\SFCT\\JSONinfo.txt",jsn)
