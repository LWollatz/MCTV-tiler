from __future__ import absolute_import, unicode_literals
#from tiler.celery import app
from celery import Celery
from tiler.tasks import add, readdir, tile
import sys


def inspect(method):
    app = Celery('tiler',
             broker='pyamqp://guest@localhost//',
             backend='amqp')
    inspect_result = getattr(app.control.inspect(),method)()
    app.close()
    return inspect_result


###read commandline input
argdic = {"executionpath":sys.argv.pop(0)}
## set defaults
argdic["-h"] = False
argdic["--help"] = False
argdic["-f"] = None
curkey = ""
curval = ""
if __name__ == "__main__":  
    ## go through arguments provided
    for arg in sys.argv:
        if (arg.startswith("-") and len(arg) == 2) or arg == "--help":
            if curval == "":
                argdic[curkey] = True
            else:
                argdic[curkey] = curval.lstrip(" ").rstrip(" ")
            curval = ""
            curkey = arg
        else:
            curval += ' ' + arg
            curval = curval.lstrip(' ')
    if curkey != "":
        if curval == "":
            argdic[curkey] = True
        else:
            argdic[curkey] = curval
    ## print help
    if argdic["--help"] or argdic["-h"] or argdic["-f"] == None:
        print("maketiles help")
        print("-f directory to create preview for")
        print("-h --help shows this help")
    ## submit job to queue
    else:
        jobvar = readdir.apply_async([argdic["-f"]]) #,priority=1)
        print("job submitted: '"+argdic["-f"]+"'")
