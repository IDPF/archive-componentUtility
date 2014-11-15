#!/usr/local/bin/python

from __future__ import with_statement

import os
import sys
import posixpath
import optparse
import shutil
import time
import epubUtil



#---------------------------------------------------------------------------
def parse_args(argv):
    usage = """
Usage: %s [FILE] [OPTIONS]...
Transfers components to epub, currently does not integrate component into destination XHTML
"""[1:-1] % os.path.basename(argv[0])

    parser = optparse.OptionParser(usage=usage)
    return parser.parse_args(argv[1:], ['spineitem', 'id'])

#---------------------------------------------------------------------------
def main(argv):
    options, args = parse_args(argv)

    if len(args) == 5:
        dstEpubFile = args[1]
        componentFile = args[2]
        spineitem = args[3]
        elementId = args[4]
        print dstEpubFile, componentFile, spineitem, id
    else:
        print "insufficient args ", len(args)


    srcComponent = epubUtil.ComponentZipContainer(componentFile)
    componentCreator = srcComponent.getComponentCreatorAndName()


    dstEpub = epubUtil.EPUBZipContainer(dstEpubFile)
    dstComponentDir = dstEpub.getComponentDir(componentCreator['creator'], componentCreator['name'])
    dstComponentRelPath = dstEpub.getComponentRelativePath(dstComponentDir)

    #dstOPFPath = dstEpub.getOpfPath()
    #dstComponentRelPath = os.path.relpath(dstComponentDir, os.path.dirname(dstOPFPath))

    dstEpub.transferMetadata(srcComponent, dstComponentRelPath, componentCreator['creator'], componentCreator['name'])
    dstEpub.transferItems(srcComponent, dstComponentDir)

    if spineitem:
        dstSpineItem = epubUtil.EPUBSpineItem(dstEpub, spineitem)

        componentFilename = srcComponent.getComponentHTML()
        componentFilename = posixpath.normpath(posixpath.join(dstComponentRelPath, componentFilename))

        dstSpineItem.insert(elementId, componentFilename)

        dstSpineItem.update()

    dstEpub.close()

    #     #
    #     # transferredComponents[dstDir] = True
    #
    # printOPF(dstZip)
    # return 0
    #
    # except Exception as e:
    #      print'\n\n================================================'
    #      print e.message
    #      print'================================================\n\n'
    #      return -1
    # except:
    #      print "Unknown Error:", sys.exc_info()[0]
    #      return -1




#---------------------------------------------------------------------------
if __name__=='__main__':
    ret = main(sys.argv)

