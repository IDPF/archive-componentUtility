#!/usr/bin/python

from __future__ import with_statement

import os
import sys
import optparse
import xml.dom.minidom
import zipfile


__author__ = 'wmanis'

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class PackageDom:
    def __init__(self, opfdom):
        self.packagedom_ = opfdom.getElementsByTagName('package')[0]

    def getPackageDom(self):
        return self.packagedom_

    #---------------------------------------------------------------------------
    # get the manifest

    def getManifest(self):
        return self.getPackageDom().getElementsByTagName('manifest')[0]

    #---------------------------------------------------------------------------
    # get the manifest

    def getManifestItems(self):
        files = []
        items = self.getPackageDom().getElementsByTagName('manifest')[0].getElementsByTagName('item')
        for item in items:
            files.append(item.getAttribute('href'))
        return files



    #---------------------------------------------------------------------------
    # get the metadata

    def getMetadata(self):
        return self.getPackageDom().getElementsByTagName('metadata')[0]


    #---------------------------------------------------------------------------
    # get the spine

    def getSpine(self):
        return self.getPackageDom().getElementsByTagName('spine')[0]

    #---------------------------------------------------------------------------
    # get the spine items

    def getSpineItems(self):
        return self.getSpine().getElementsByTagName('itemref')

    #---------------------------------------------------------------------------
    # get the spine items

    def getCollections(self):
        collections = []
        package = self.getPackageDom()
        for child in package.childNodes:
            if child.localName == 'collection':
                collections.append(child)
        return collections

    #---------------------------------------------------------------------------
    # debug - print out opf manifest

    def printManifest(self):
        print self.getManifest().toxml()

    #---------------------------------------------------------------------------
    # debug - print out opf metadata

    def printMetadata(self):
        print self.getMetadata().toxml()

    #---------------------------------------------------------------------------
    # debug - print out opf spine

    def printSpine(self):
        print self.getSpine().toxml()

    #---------------------------------------------------------------------------
    # debug - print out opf spine

    def printCollections(self):
        collections = self.getCollections()
        for collection in collections:
            print collection.toxml()

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class EPUBZipContainer:

    def __init__(self, zipfile):
        self.zipfile_ = zipfile
        self.packagedom_ = None
        self.packagedom2_ = PackageDom(self.getOpfDom())

    # ---------------------------------------------------------------------------
    # get original zipfile

    def getZipfile(self):
        return self.zipfile_

    # ---------------------------------------------------------------------------
    # get the path to the opf file from container.xml

    def getOpfPath(self):
        xmlDom = xml.dom.minidom.parseString(self.zipfile_.read('META-INF/container.xml'))
        container = xmlDom.documentElement
        root = container.getElementsByTagName('rootfile')[0]
        return root.getAttribute('full-path')


    #---------------------------------------------------------------------------
    # get the package xmldom

    def getOpfDom(self):
        path = self.getOpfPath()
        opfXML = self.zipfile_.read(path)
        return xml.dom.minidom.parseString(opfXML)


    #---------------------------------------------------------------------------
    # get the package xmldom

    def getPackageDom(self):
        if self.packagedom_ == None:
            path = self.getOpfPath()
            opfXML = self.zipfile_.read(path)
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
    # get the spine items

    def getOpfCollections(self):
        return self.packagedom2_.getCollections()

    #---------------------------------------------------------------------------
    # debug - print out opf

    def printOPF(self):
        path = self.getOpfPath()
        opfXML = self.zipfile_.read(path)
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


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class ComponentZipContainer(EPUBZipContainer):

    prefix = 'component'
    namespace = 'component:http://www.idpf.org/vocab/component/#'


    # get the component metadata from the opf

    def getComponentMetadata(self):
        componentMetadatum = []
        metadataItems = self.getOpfMetadata().getElementsByTagName('meta')
        for meta in metadataItems:
            property = meta.getAttribute('property')
            if property.find(self.prefix) == 0:
                componentMetadatum.append({ 'property': property, 'value': meta.firstChild.nodeValue })
        return componentMetadatum

    #---------------------------------------------------------------------------    
    # get the component creator and name from the meta properties

    def getComponentCreatorAndName(self):
        creatorProp = self.prefix + ":creator"
        nameProp = self.prefix + ":name"

        creator = 'unknown'
        name = 'unknown'

        metadata = self.getComponentMetadata()
        for meta in metadata:
            if (meta['property'] == creatorProp):
                creator = meta['value']
            if (meta['property'] == nameProp):
                name = meta['value']

        return {'creator' : creator, 'name': name}
        
    
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
        epubs = ['epub/componentContainer.epub', 'components/gallery.epub', 'components/gallery2.epub']

    try:
        # transfer components to destination epub
        for epub in epubs:
            epubzip = zipfile.ZipFile(epub, 'r')

            container = EPUBZipContainer(epubzip)
            container.printOPF()
            container.printOpfManifest()
            container.printOpfMetadata()
            container.printOpfSpine()
            container.printOpfCollections()

            print container.getOpfSpineItems().length



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