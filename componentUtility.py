#!/usr/local/bin/python

from __future__ import with_statement

version_ = "0.0.1"

__license__ = """
    Copyright (c) 2014, Will Manis
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

    The views and conclusions contained in the software and documentation are those
    of the authors and should not be interpreted as representing official policies,
    either expressed or implied, of the FreeBSD Project.
"""



import sys
import os
import posixpath
import argparse
import xmlElement
import epubUtil

app_name_ = "Component Utility "
short_description_ = """Utility for integrating, listing, checking and extracting EPUB components"""

examples_ = """
    Examples:
        componentUtility -i component.epub book.epub
            integrates component.epub into a copy of book.epub named book.merged.epub

        componentUtility -I component.epub book.epub OPS/chap.xhtml component1
            integrates component.epub into a copy of book.epub named book.merged.epub
            and updates iframe element id='component1' in chap.xhtml

        componentUtility -l book.epub
            lists components contained in book.epub

        componentUtility -c component.epub
            checks component.epub to ensure that it is a valid component

        componentUtility -x book.epub creator componentName
            extracts the component with creator & componentName to creator_componentName.extracted.epub
            which should be a valid component epub

"""

#---------------------------------------------------------------------------
def listComponents(epubFile):
    epub = epubUtil.EPUBZipContainer(epubFile)
    collections = epub.getOpfDom().getComponentCollections()

    print '\n  List of installed components'
    for collection in collections:
        creatorname = epubUtil.getCollectionCreatorAndName(collection)
        print '    Component creator: "' + creatorname['creator'] + '" - name: "' + creatorname['name'] + '"'
    print "  Done"


#---------------------------------------------------------------------------
def installComponent(dstEpubFile, componentFile, outputFilename, spineitem = None, elementId = None):

    # open source component epub and get vendor and component name
    srcComponent = epubUtil.ComponentZipContainer(componentFile)
    componentCreator = srcComponent.getComponentCreatorAndName()

    print "    Install component:", componentCreator['creator'], componentCreator['name']

    # open destination epub and determine component directory and relative path from
    # package file
    dstEpub = epubUtil.EPUBZipContainer(dstEpubFile)

    if dstEpub.testComponentExistance(componentCreator['creator'], componentCreator['name']):
        print "    Already installed"
        return

    dstComponentDir = epubUtil.getComponentDir(componentCreator['creator'], componentCreator['name'])
    dstComponentRelPath = dstEpub.getComponentRelativePath(dstComponentDir)


    #transfer data
    dstEpub.transferMetadata(srcComponent, dstComponentRelPath, componentCreator['creator'], componentCreator['name'])
    dstEpub.transferItems(srcComponent, dstComponentDir)

    if spineitem and elementId:
        dstSpineItem = epubUtil.EPUBSpineItem(dstEpub, spineitem)

        componentFilename = srcComponent.getComponentHTML()
        componentFilename = posixpath.normpath(posixpath.join(dstComponentRelPath, componentFilename))

        dstSpineItem.insert(elementId, componentFilename)

        dstSpineItem.update()

    # write out the contents and close the epub
    dstEpub.close(outputFilename)

    print "    Installed: ", componentCreator['creator'], componentCreator['name']

#---------------------------------------------------------------------------
def checkComponent(epub):
    print '\n    Checking component epub: "' + epub + '"\n'
    valid = True

    # check creator and name
    srcComponent = epubUtil.ComponentZipContainer(epub)
    componentCreator = srcComponent.getComponentCreatorAndName()

    if componentCreator['creator'] != None and componentCreator['name'] != None:
        print '    Creator:', componentCreator['creator'], '   name:', componentCreator['name']
    else:
        print '    No creator and/or component name'
        valid = False

    # check that version is present
    version = None

    vitem = srcComponent.getOpfDom().getOpfMetadataItemsByAttr('property', 'component:version')

    if len(vitem) > 0:
        version = xmlElement.getText(vitem[0])
        print '    Version: ', version
    else:
        print '    No version'
        valid = False


    # check number of spineitems
    spineItems = srcComponent.getOpfDom().getSpineItems()
    if len(spineItems) == 1:
        print '    spine items:', len(spineItems)
    else:
        print '    Too many spine items, which one is the widget?'
        valid = False

    if valid == False:
        print "\n    INVALID COMPONENT EPUB"
    else:
         print "\n    VALID COMPONENT EPUB (limited testing)"

#---------------------------------------------------------------------------
def extractComponent(epub, creator, componentName):
    print "NYI - incomplete implementation"
    srcEpub = epubUtil.EPUBZipContainer(epub)
    destComponent = epubUtil.ComponentZipContainer(creator + '_' + componentName + '.extracted.epub', creator, componentName)
    if destComponent.extract(srcEpub) == True:
        destComponent.close(destComponent.get_filename())
    else:
        os.remove(destComponent.get_filename())


#---------------------------------------------------------------------------
def parse_args(argv):
    parser = argparse.ArgumentParser(description='Utility for integrating, extracting, checking and listing components in epubs')

    # TODO add types
    parser.add_argument('-v', action='store_true', help="Show version and license")
    parser.add_argument('-examples', action='store_true', help='Show examples')
    parser.add_argument('-l', nargs=1, help='List components in EPUB')
    parser.add_argument('-c', nargs=1, help='Check that EPUB is a valid component ready for integration')
    parser.add_argument('-i', nargs=2, help='Integrate COMPONENT into EPUB')
    parser.add_argument('-I', nargs=4, help='Integrate COMPONENT into EPUB into PATHtoXHTML, attach at ID (an iframe)')
    parser.add_argument('-o', nargs=1, help='EPUB to output integrated component, default is into name.merged.epub')
    parser.add_argument('-x', nargs=3, help='Extract CREATOR & COMPONENT name from EPUB')
    parser.add_argument('-D', action='store_true', help='Debug')

    return parser.parse_args()

#---------------------------------------------------------------------------
def main(argv):

    args = parse_args(argv)


    output = None
    if args.examples:
        print "\n   ", short_description_
        print examples_
        return

    if args.v:
        print "\n   ", app_name_, version_, "\n    "
        print "   ", short_description_
        print __license__
        return

    if args.o:
        output = args.o[0]

    if args.l:
        # print 'list', args.l
        epubFile = args.l[0]
        listComponents(epubFile)
    elif args.c:
        #print 'check', args.c
        epubFile = args.c[0]
        checkComponent(epubFile)
    elif args.i:
        dstEpubFile = args.i[1]
        componentFile = args.i[0]
        installComponent(dstEpubFile, componentFile, output)
    elif args.I:
        print 'INTEGRATE', args.I
        dstEpubFile = args.I[1]
        componentFile = args.I[0]
        spineitem = args.I[2]
        elementId = args.I[3]
        installComponent(dstEpubFile, componentFile, output, spineitem, elementId)
    elif args.x:
        print 'Extract', args.x
        epubFile = args.x[0]
        creator = args.x[1]
        componentName = args.x[2]
        extractComponent(epubFile, creator, componentName)



    # except Exception as e:
    #      print'\n\n================= error ==============================='
    #      print e.message
    #      print'================================================\n\n'
    #      return -1
    # except:
    #      print "Unknown Error:", sys.exc_info()[0]
    #      return -1




#---------------------------------------------------------------------------
if __name__=='__main__':
    ret = main(sys.argv)

