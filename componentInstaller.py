#!/usr/local/bin/python

from __future__ import with_statement

import os
import sys
import posixpath
import optparse
import zipfile
import xml.dom.minidom
import shutil
import time
import epubUtil
import xml.etree.ElementTree as ET



componentPrefix = 'component'
componentDirectory = 'components'
componentNamespace = 'component: http://www.idpf.org/vocab/component/#'
opfNamespace = "{http://www.idpf.org/2007/opf}"


#---------------------------------------------------------------------------

def transferMetadata(dstEpub, srcComponent, dstComponentDir, creatorName):

    scrMetadata = srcComponent.getComponentMetadata()

    opfDOM = dstEpub.getOpfDom()

    dstManifest = opfDOM.find(opfNamespace + 'manifest')

    collection = ET.SubElement(opfDOM, opfNamespace + 'collection')
    collection.set('role', "component:component")

    #transferTime = manifestXmlDom.createComment(' == transfer time ' + time.asctime(time.gmtime()) + ' UTC ==')
    #collection.appendChild(transferTime)

    metadata = ET.SubElement(collection, opfNamespace + 'metadata')


    for datum in scrMetadata:
        meta = ET.SubElement(metadata, opfNamespace + 'meta');
        meta.set( 'property', datum['property'])
        meta.text = datum['value']

    spineitems = srcComponent.getOpfSpineItems()

    assert(len(spineitems) == 1)
    idref = spineitems[0].get('idref')

    componentManifest = ET.SubElement(collection, opfNamespace + 'collection', {'role' : 'manifest'})
    component = None

    items = srcComponent.getOpfManifestItems()

    for item in items:
        if item.get('properties') == 'nav':
            #do not copy nav doc
            continue
        link = ET.SubElement(componentManifest, opfNamespace + "link")
        if idref == item.get('id'):
            component = item

        #link.set('id', creatorName + item.get('id'))

        href = item.get('href')
        print href
        href = posixpath.normpath(posixpath.join(dstComponentDir, href))
        print href
        link.set('href', href)

        newitem = ET.SubElement(dstManifest, item.tag)
        for attr in item.attrib:
            if attr == 'href':
                newitem.set('href', href)
            elif attr != 'id':
                newitem.set(attr, item.get(attr))
            else:
                newitem.set(attr, 'foo_' + item.get(attr))



    link = ET.SubElement(collection, opfNamespace + 'link')
    href = posixpath.normpath(posixpath.join(dstComponentDir, component.get('href')))
    link.set('href', href)

    print xml.dom.minidom.parseString(ET.tostring(opfDOM)).toprettyxml()

    #write out the updated manifest

    prefix = opfDOM.get('prefix')
    if prefix == None:
        opfDOM.set('prefix', componentNamespace)
    elif prefix.find(componentNamespace) < 0:
        opfDOM.set('prefix', prefix + ' ' + componentNamespace)

    path = dstEpub.getOpfPath()

    lines = xml.dom.minidom.parseString(ET.tostring(opfDOM)).toprettyxml()
    lines = lines.split('\n')
    trimmedlines = []
    for line in lines:
        line = line.rstrip()
        if len(line) != 0:
            trimmedlines.append(line)

    #print trimmedlines
    cleanedup = '\n'.join(trimmedlines)
    
    ##print cleanedup
    dstEpub.putfile(path, cleanedup)

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

    dstEpub = epubUtil.EPUBZipContainer(dstEpubFile)

    dstOPFPath = dstEpub.getOpfPath()

    componentCreator = srcComponent.getComponentCreatorAndName()

    #TODO : move to epub class
    dstComponentDir = posixpath.normpath(posixpath.join(componentDirectory, componentCreator['creator'], componentCreator['name']))

    dstComponentRelPath = os.path.relpath(dstComponentDir, os.path.dirname(dstOPFPath))

    transferMetadata(dstEpub, srcComponent, dstComponentRelPath, componentCreator['creator'] + '_' + componentCreator['name'] + '_')

    dstEpub.transferItems(srcComponent, dstComponentDir)

    dstSpineItem = epubUtil.EPUBSpineItem(dstEpub, spineitem)

    componentFilename = srcComponent.getComponentHTML()
    componentFilename = posixpath.normpath(posixpath.join(dstComponentRelPath, componentFilename))

    dstSpineItem.insert(elementId, componentFilename)

    print dstSpineItem.tostring()

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

