#!/usr/local/bin/python

from __future__ import with_statement

import os
import sys
import optparse
import xml.dom.minidom as minidom
import zipfile
import posixpath
import xml.etree.ElementTree as ET
import urllib

__author__ = 'wmanis'

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class PackageDom:
    def __init__(self, opfdom):
        self.packagedom_ = opfdom

    def getPackageDom(self):
        return self.packagedom_

    # ---------------------------------------------------------------------------
    # get the manifest

    def getManifest(self):
        return self.getPackageDom().find('./{http://www.idpf.org/2007/opf}manifest')

    # ---------------------------------------------------------------------------
    # get the manifest

    def getManifestItems(self):
        items = self.getManifest()
        return list(items)


    #---------------------------------------------------------------------------
    # get the metadata

    def getMetadata(self):
        return self.getPackageDom().find('./{http://www.idpf.org/2007/opf}metadata')


    #---------------------------------------------------------------------------
    # get the spine

    def getSpine(self):
        return self.getPackageDom().find('./{http://www.idpf.org/2007/opf}spine')

    #---------------------------------------------------------------------------
    # get the spine items

    def getSpineItems(self):
        return list(self.getSpine())

    #---------------------------------------------------------------------------
    # get the spine items

    def getCollections(self):
        return self.getPackageDom().findall('.//{http://www.idpf.org/2007/opf}collection')


    #---------------------------------------------------------------------------
    # debug - print out opf manifest

    def printManifest(self):

        for child in self.getManifest():
            print child.tag, child.attrib


    #---------------------------------------------------------------------------
    # debug - print out opf metadata

    def printMetadata(self):
        for child in self.getMetadata():
            print child.tag, child.attrib

    #---------------------------------------------------------------------------
    # debug - print out opf spine

    def printSpine(self):
        for child in self.getSpine():
            print child.tag, child.attrib

    #---------------------------------------------------------------------------
    # debug - print out opf spine

    def printCollections(self):
        collections = self.getCollections()
        for collection in collections:
            print collection.tag, collection.attrib


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class EPUBZipContainer:
    def __init__(self, name):
        self.name_ = name
        self.zipfile_ = zipfile.ZipFile(name, 'r')
        self.__unzip()
        self.packagedom_ = None
        self.packagedom2_ = PackageDom(self.getOpfDom())


    # ---------------------------------------------------------------------------
    # get original zipfile
    def __unzip(self):
        self.names_ = self.zipfile_.namelist()
        self.contents_ = {}
        for name in self.names_:
            self.contents_[name] = self.zipfile_.read(name)

     # ---------------------------------------------------------------------------
    # update original
    def close(self):
        mergedName = posixpath.normpath(posixpath.join(posixpath.splitext(self.name_)[0] + ".merged.epub"))
        if os.path.exists(mergedName):
            os.remove(mergedName)
        newzipfile = zipfile.ZipFile(mergedName, 'a')
        for name in self.contents_:
            newzipfile.writestr(name, self.contents_[name])



    # ---------------------------------------------------------------------------
    # get original zipfile

    def getBytes(self, name):
        return self.contents_[name]

    # ---------------------------------------------------------------------------
    # get the path to the opf file from container.xml

    def getOpfPath(self):
        xmlDom = minidom.parseString(self.contents_['META-INF/container.xml'])
        container = xmlDom.documentElement
        root = container.getElementsByTagName('rootfile')[0]
        return root.getAttribute('full-path')


    #---------------------------------------------------------------------------
    # get the package xmldom

    def getOpfDom(self):
        path = self.getOpfPath()
        opfXML = self.contents_[path]
        tree = ET.fromstring(opfXML)
        return tree


    #---------------------------------------------------------------------------
    # get the package xmldom

    def getfile(self, path):
        return self.contents_[path]

    #---------------------------------------------------------------------------
    # get the package xmldom

    def putfile(self, path, text):
        self.contents_[path] = text

    #---------------------------------------------------------------------------
    # get the package xmldom

    def getPackageDom(self):
        if self.packagedom_ == None:
            path = self.getOpfPath()
            opfXML = self.contents_[path]
            self.packagedom_ = xml.dom.minidom.parseString(opfXML).getElementsByTagName('package')[0]
        return self.packagedom_


    #---------------------------------------------------------------------------
    # get the manifest

    def getOpfManifest(self):
        return self.packagedom2_.getManifest()

    #---------------------------------------------------------------------------
    # get the manifest

    def getOpfManifestItems(self):
        return self.packagedom2_.getManifestItems()

    #---------------------------------------------------------------------------
    # get the metadata

    def getOpfMetadata(self):
        return self.packagedom2_.getMetadata()


    #---------------------------------------------------------------------------
    # get the spine

    def getOpfSpine(self):
        return self.packagedom2_.getSpine()

    #---------------------------------------------------------------------------
    # get the spine items

    def getOpfSpineItems(self):
        return self.packagedom2_.getSpineItems()


    #---------------------------------------------------------------------------
    def getSpineItemPath(self, xmlid):
        manifest = self.getOpfManifestItems()

        for item in manifest:
            if item.get('id') == xmlid:
                return item.get('href')
        return None

    #---------------------------------------------------------------------------
    # get spineitem files
    def getOpfSpineItemFiles(self):
        spinefiles = []
        spineitems = self.getOpfSpineItems()

        for itemref in spineitems:
            idref = itemref.get('idref')
            spinefiles.append(self.getSpineItemPath(idref))

        return spinefiles

    #---------------------------------------------------------------------------
    # get the spine items

    def getOpfCollections(self):
        return self.packagedom2_.getCollections()

    #---------------------------------------------------------------------------
    # debug - print out opf

    def printOPF(self):
        path = self.getOpfPath()
        opfXML = self.contents_[path]
        print opfXML


    #---------------------------------------------------------------------------
    # debug - print out opf manifest

    def printOpfManifest(self):
        self.packagedom2_.printManifest()


    #---------------------------------------------------------------------------
    # debug - print out opf metadata

    def printOpfMetadata(self):
        self.packagedom2_.printMetadata()


    #---------------------------------------------------------------------------
    # debug - print out opf spine

    def printOpfSpine(self):
        self.packagedom2_.printSpine()

    #---------------------------------------------------------------------------
    # debug - print out opf spine

    def printOpfCollections(self):
        self.packagedom2_.printCollections()


    #---------------------------------------------------------------------------
    # transfer component assets and update the destination opf file

    def transferItems(self, srcComponent, dstDir):

        # get items from manifest for transfer
        itemList = srcComponent.getOpfManifestItems()

        srcOpfDir = posixpath.dirname(srcComponent.getOpfPath())

        for item in itemList:
            if item.get('properties') == 'nav':
                #do not copy nav doc
                continue

            srcPath = posixpath.normpath(posixpath.join(srcOpfDir, item.get('href')))
            dstPath = posixpath.normpath(posixpath.join(dstDir, item.get('href').split('../').pop()))

            # copy the bytes over
            srcbytes = srcComponent.getfile(srcPath)
            self.putfile(dstPath, srcbytes)


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class EPUBSpineItem:
    def __init__(self, zipfile, path):
        self.zipfile_ = zipfile
        self.path_ = path
        self.spineXML_ = minidom.parseString(self.zipfile_.getBytes(path))

    def insert(self, elementID, src):
        def walk(node, elementid):
            if node.attributes != None:
                for attr in node.attributes.values():
                    if attr.name == 'id' and attr.value == elementid:
                        return node

            for child in node.childNodes:
                if child.nodeType == child.ELEMENT_NODE:
                    id = walk(child, elementid)
                    if id != None:
                        return id
            return None

        node = walk(self.spineXML_, elementID)
        if node != None:
            attr = self.spineXML_.createAttribute('src')
            attr.value = src
            node.attributes.setNamedItem(attr)
            return

        raise "no element with that id"


    def tostring(self):
        lines = self.spineXML_.toprettyxml()
        lines = lines.split('\n')

        trimmedlines = []
        for line in lines:
            line = line.rstrip()
            if len(line) != 0:
                trimmedlines.append(line)

        print '\n'.join(trimmedlines)
        return '\n'.join(trimmedlines)


    def update(self):
        self.zipfile_.putfile(self.path_, self.tostring())


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class ComponentZipContainer(EPUBZipContainer):
    prefix = 'component'
    namespace = 'component:http://www.idpf.org/vocab/component/#'


    # get the component metadata from the opf
    def getComponentMetadata(self):
        componentMetadatum = []
        metadataItems = self.getOpfMetadata().findall('./{http://www.idpf.org/2007/opf}meta')
        for meta in metadataItems:
            if meta.attrib['property']:
                componentMetadatum.append({'property': meta.attrib['property'], 'value': meta.text})
        return componentMetadatum

    # get the component metadata from the opf
    def getComponentManifest(self):
        componentManifest = []
        manifestItems = self.getOpfManifestItems()
        for item in manifestItems:
            componentManifest.append({'property': item.get('property'), 'value': item.text})
        return componentManifest

    # get component base html
    def getComponentHTML(self):
        return self.getOpfSpineItemFiles()[0]

    #---------------------------------------------------------------------------    
    # get the component creator and name from the meta properties

    def getComponentCreatorAndName(self):
        creatorProp = self.prefix + ":creator"
        nameProp = self.prefix + ":name"

        creator = 'unknown'
        name = 'unknown'

        metadata = self.getComponentMetadata()
        for meta in metadata:
            if meta['property'] == creatorProp:
                creator = meta['value']
            if meta['property'] == nameProp:
                name = meta['value']

        return {'creator': urllib.quote(creator), 'name': urllib.quote(name)}


def makeQName(ns, tag):
    return '{' + ns + '}' + tag


def splitQName(name):
    return name.split('{')[1].split('}')


#---------------------------------------------------------------------------
def parse_args(argv):
    usage = """
Usage: %s [FILE] [OPTIONS]...
Transfers components to epub, currently does not integrate component into destination XHTML
"""[1:-1] % os.path.basename(argv[0])

    parser = optparse.OptionParser(usage=usage)
    return parser.parse_args(argv[1:])


#---------------------------------------------------------------------------
def main(argv):
    options, args = parse_args(argv)

    if len(args) > 1:
        epubs = args
    else:
        epubs = ['epub/componentContainer.epub']

    try:
        # transfer components to destination epub
        for epub in epubs:
            epubzip = zipfile.ZipFile(epub, 'r')

            container = EPUBZipContainer(epubzip)

            spineitem = EPUBSpineItem(container, 'OPS/componentContainer.html')
            print spineitem.tostring()
            spineitem.insert("component1", "foo.html")
            print spineitem.tostring()



    except Exception as e:
        print'\n\n================================================'
        print e.message
        print'================================================\n\n'
        return -1
    except:
        print "Unknown Error:", sys.exc_info()[0]
        return -1


#---------------------------------------------------------------------------
if __name__ == '__main__':
    ret = main(sys.argv)