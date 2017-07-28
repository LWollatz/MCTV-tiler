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
argdic = {"executionpath":sys.argv.pop(0), "-v":False}
argdic["-h"] = False
argdic["--help"] = False
curkey = ""
curval = ""

if __name__ == "__main__":
    #    default arguments for testing
    argdic["-f"] = "C:\\data\\lw6g10\\DigiSens_20140530_HUTCH_581_MJr_0914546B"
    argdic["-f"] = "C:\\data\\lw6g10\\20121206_HMX_376_AS_test5 [2012-12-07 14.58.08]\\20121206_HMX_376_AS_test5_recon"
##    argdic["-o"] = "SFCT"
##    argdic["-v"] = False
##    
##
if True:
    ###print time()
    print sys.argv
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
    #help
    if argdic["--help"] or argdic["-h"]:
        print("maketiles help")
        print("-f directory to create preview for")
        print("-h --help shows this help")
    else:

    
        #add.delay(4,4)
        #i = app.control.inspect()

        #print inspect("active_queues")
        #print app.control.inspect().registered()
        #print app.control.inspect().active()
        #print inspect("scheduled")
        #print app.control.inspect().reserved()
        #jobvar = readdir.delay(argdic["-f"])
        print argdic["-i"], "'"+argdic["-f"]+"'"
        jobvar = readdir.apply_async([argdic["-f"]]) #,priority=1)
        print "job submitted"
