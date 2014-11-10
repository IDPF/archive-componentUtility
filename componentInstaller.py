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
# get the path to the opf file from container.xml

def getOpfPath(epub):
    xmlDom = xml.dom.minidom.parseString(epub.read('META-INF/container.xml'))
    container = xmlDom.documentElement
    root = container.getElementsByTagName('rootfile')[0]
    return root.getAttribute('full-path')

#---------------------------------------------------------------------------
# get the opf xmldom

def getOpfXmlDom(epub):
    path = getOpfPath(epub)
    opfXML = epub.read(path)
    xmlDom = xml.dom.minidom.parseString(opfXML)
    return xmlDom

#---------------------------------------------------------------------------
# get the manifest

def getOpfManifest(epub):
    xmlDom = getOpfXmlDom(epub)
    return xmlDom.getElementsByTagName('manifest')[0]

#---------------------------------------------------------------------------
# get the metadata

def getOpfMetadata(epub):
    xmlDom = getOpfXmlDom(epub)
    return xmlDom.getElementsByTagName('metadata')[0]

#---------------------------------------------------------------------------
# get the spine
def getOpfSpine(epub):
    xmlDom = getOpfXmlDom(epub)
    return xmlDom.getElements.ByTagName('spine')

#---------------------------------------------------------------------------
# debug - print out opf

def printOPF(epub):
    path = getOpfPath(epub)
    opfXML = epub.read(path)
    print opfXML

#---------------------------------------------------------------------------
# debug - print out opf manifest

def printOpfManifest(epub):
    print getOpfManifest(epub)

#---------------------------------------------------------------------------
# debug - print out opf metadata

def printOpfMetadata(epub):
   print getOpfMetadata(epub)

#---------------------------------------------------------------------------
# debug - print out opf spine

def printOpfSpine(epub):
    print getOpfSpine(epub)

#---------------------------------------------------------------------------
# if the component prefix not defined add to opf

def addComponentPrefix(package):
    prefix = package.get('prefix')
    if prefix == None:
        package.set('prefix', componentNamespace)
    elif prefix.find(componentNamespace) < 0:
        package.set('prefix', prefix + ' ' + componentNamespace)

#---------------------------------------------------------------------------
# write out the opf dom

def puttOPfXmlDom(epub, manifestXmlDom):

    addComponentPrefix(manifestXmlDom)

    path = epub.getOpfPath()

    lines = xml.dom.minidom.parseString(ET.tostring(manifestXmlDom)).toprettyxml()
    lines = lines.split('\n')
    trimmedlines = []
    for line in lines:
        line = line.rstrip()
        if len(line) != 0:
            trimmedlines.append(line)

    #print trimmedlines
    cleanedup = '\n'.join(trimmedlines)
    ##print cleanedup
    epub.putfile(path, cleanedup)

#---------------------------------------------------------------------------
# get the component metadata from the opf

def getComponentMetadata(opfXMLDom):
    componentMetadatum = []
    metadataItems = opfXMLDom.getElementsByTagName('meta');
    for meta in metadataItems:
        property = meta.getAttribute('property');
        if property.find(componentPrefix) == 0:
            componentMetadatum.append({ 'property': property, 'value': meta.firstChild.nodeValue })
    return componentMetadatum

#---------------------------------------------------------------------------
# get a list of the items in the manifest that we want to transfer
# ignoring unneeded files

def getComponentManifest(epub):
    files = []
    xmlDom = getOpfXmlDom(epub)
    manifest = xmlDom.getElementsByTagName('item')
    for item in manifest:
        # remove nav stuff, there may be other to remove
        if item.getAttribute('properties') != 'nav':
            #print 'componentManifest: ' + item.getAttribute('href')
            files.append(item.getAttribute('href'))
    return files

#---------------------------------------------------------------------------
# get the collection associated with this component

def getCollection(xmlDom, creator, name):

    package = xmlDom.getElementsByTagName('package')[0]

    collections = []
    for child in package.childNodes:
        if child.localName == 'collection':
            collections.append(child)

    # this could be made much simpler with an xpath lib, but i am trying to use plain vanilla python
    for collection in collections:
        metadata = collection.getElementsByTagName('meta')
        found = 0
        for meta in metadata:
            value = meta.getAttribute('property')
            if value == 'component:creator' and meta.firstChild.nodeValue == creator:
                found += 1
            if value == 'component:name' and meta.firstChild.nodeValue == name:
                found += 1
            if found == 2:
                return collection
    return None

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

    addComponentPrefix(opfDOM)

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
def makecopy(dstfile):
    dstCopy = posixpath.normpath(posixpath.join(posixpath.splitext(dstfile)[0] + ".merged.epub"))
    if os.path.exists(dstCopy):
        os.remove(dstCopy)
    shutil.copyfile(dstfile, dstCopy)
    return dstCopy

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

