#!/usr/local/bin/python

from __future__ import with_statement

import os
import sys
import optparse
import xml.dom.minidom as minidom
import zipfile
import posixpath
import urllib
import xmlom
import time
import xmlElement

__author__ = 'wmanis'


componentPrefix = 'component'
componentDirectory = 'components'
componentNamespace = 'component: http://www.idpf.org/vocab/component/#'
opfNamespace = "{http://www.idpf.org/2007/opf}"

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
        return self.packagedom_.findAllByTagName('manifest')[0]

    # ---------------------------------------------------------------------------
    # get the manifest

    def getManifestItems(self):
        items = []
        for item in self.getManifest().childNodes:
            if item.nodeType == item.ELEMENT_NODE:
                items.append(item)

        return items


    # ---------------------------------------------------------------------------
    # get the metadata

    def getMetadata(self):
        return self.packagedom_.findAllByTagName('metadata')[0]

    #---------------------------------------------------------------------------
    # get the metadata

    def getMetadataItems(self):
        return self.packagedom_.findChildrenByTagName(self.getMetadata(), 'meta')

    #---------------------------------------------------------------------------
    # get the spine

    def getSpine(self):
        return self.packagedom_.findAllByTagName('spine')[0]

    #---------------------------------------------------------------------------
    # get the spine items

    def getSpineItems(self):
        return self.packagedom_.findChildrenByTagName(self.getSpine(), 'itemref')

    #---------------------------------------------------------------------------
    # get the spine items

    def getCollections(self):
        return self.packagedom_.findChildrenByTagName(self.packagedom_.getRootElement(), 'collection')


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
    def __init__(self, name, debug = True):
        self.name_ = name
        self.zipfile_ = zipfile.ZipFile(name, 'r')
        self.__unzip()
        self.tree_ = None
        self.packagedom_ = PackageDom(self.getOpfDom())
        self.debug_ = debug


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
        xmlDom = xmlom.XMLOM(self.contents_['META-INF/container.xml'])
        root = xmlDom.findAllByTagName('rootfile')[0]
        return xmlDom.getAttribute(root, 'full-path')


    # ---------------------------------------------------------------------------
    # get the package xmldom

    def getOpfDom(self):
        if self.tree_ == None:
            path = self.getOpfPath()
            opfXML = self.contents_[path]
            self.tree_ = xmlom.XMLOM(opfXML)
        return self.tree_

    #---------------------------------------------------------------------------
    # get the package xmldom

    def getfile(self, path):
        return self.contents_[path]

    #---------------------------------------------------------------------------
    # get the package xmldom

    def putfile(self, path, text):
        self.contents_[path] = text


    #---------------------------------------------------------------------------
    # get the manifest

    def getOpfManifest(self):
        return self.packagedom_.getManifest()


    #---------------------------------------------------------------------------
    # get the manifest

    def getOpfManifestItems(self):
        return self.packagedom_.getManifestItems()


    #---------------------------------------------------------------------------
    # get the metadata

    def getOpfMetadata(self):
        return self.packagedom_.getMetadata()

    #---------------------------------------------------------------------------
    # get the spine

    def getOpfSpine(self):
        return self.packagedom_.getSpine()

    #---------------------------------------------------------------------------
    # get the spine items

    def getOpfSpineItems(self):
        return self.packagedom_.getSpineItems()

    #---------------------------------------------------------------------------
    def getSpineItemPath(self, xmlid):
        manifest = self.getOpfManifestItems()

        opfDOM = self.getOpfDom()

        for item in manifest:
            if opfDOM.getAttribute( item, 'id') == xmlid:
                return opfDOM.getAttribute(item, 'href')
        return None


    #---------------------------------------------------------------------------

    # get spineitem files
    def getOpfSpineItemFiles(self):
        spinefiles = []
        spineitems = self.getOpfSpineItems()

        opfDOM = self.getOpfDom()

        for itemref in spineitems:
            idref = opfDOM.getAttribute(itemref, 'idref')
            spinefiles.append(self.getSpineItemPath(idref))

        return spinefiles

    #---------------------------------------------------------------------------
    # get the spine items

    def getOpfCollections(self):
        return self.packagedom_.getCollections()

    #---------------------------------------------------------------------------
    # debug - print out opf

    def printOPF(self):
        path = self.getOpfPath()
        opfXML = self.contents_[path]
        print opfXML


    #---------------------------------------------------------------------------
    # debug - print out opf manifest

    def printOpfManifest(self):
        self.packagedom_.printManifest()


    #---------------------------------------------------------------------------
    # debug - print out opf metadata

    def printOpfMetadata(self):
        self.packagedom_.printMetadata()


    #---------------------------------------------------------------------------
    # debug - print out opf spine

    def printOpfSpine(self):
        self.packagedom_.printSpine()

    #---------------------------------------------------------------------------
    # debug - print out opf spine

    def printOpfCollections(self):
        self.packagedom_.printCollections()

    def getComponentDir(self, creator, name):
        return posixpath.normpath(posixpath.join(componentDirectory, creator, name))

    def getComponentRelativePath(self, componentDir):
        dstOPFPath = self.getOpfPath()
        return os.path.relpath(componentDir, os.path.dirname(dstOPFPath))

    #---------------------------------------------------------------------------
    # transfer component assets and update the destination opf file
    def transferItems(self, srcComponent, dstDir):

        # get items from manifest for transfer
        itemList = srcComponent.getOpfManifestItems()

        opfDOM = srcComponent.getOpfDom()

        srcOpfDir = posixpath.dirname(srcComponent.getOpfPath())

        for item in itemList:
            if opfDOM.getAttribute(item, 'properties') == 'nav':
                #do not copy nav doc
                continue

            href = opfDOM.getAttribute(item, 'href')
            srcPath = posixpath.normpath(posixpath.join(srcOpfDir, href))
            dstPath = posixpath.normpath(posixpath.join(dstDir, href.split('../').pop()))

            # copy the bytes over
            srcbytes = srcComponent.getfile(srcPath)
            self.putfile(dstPath, srcbytes)


    #---------------------------------------------------------------------------
    # build the collection containing the component
    def buildCollection(self, dstComponentDir, items,  srcMetadata, idref,vendorName, componentName):
        opfDOM = self.getOpfDom()
        commentString = ' start of component ' + vendorName + ' - ' + componentName + ' transfer time ' + time.asctime(time.gmtime()) + ' UTC '
        xmlElement.addComment(opfDOM.getRootElement(), commentString)

        collection = opfDOM.addChild(opfDOM.getRootElement(), 'collection', {'role' : 'component:component'})
        metadata = opfDOM.addChild(collection, 'metadata')


        for datum in srcMetadata:
            meta = opfDOM.addChild(metadata, 'meta')
            opfDOM.setAttribute(meta, 'property', datum['property'])
            opfDOM.addTextNode(meta, datum['value'])



        collectionManifest = opfDOM.addChild(collection, 'collection', {'role' : 'manifest'})
        component = None


        for item in items:
            link = opfDOM.addChild(collectionManifest, "link")
            if idref == opfDOM.getAttribute(item, 'id'):
                component = item

            #link.set('id', creatorName + item.get('id'))

            href = opfDOM.getAttribute(item, 'href')
            print href
            href = posixpath.normpath(posixpath.join(dstComponentDir, href))
            print href
            opfDOM.setAttribute(link, 'href', href)


        link = opfDOM.addChild(collection, 'link')
        href = posixpath.normpath(posixpath.join(dstComponentDir, opfDOM.getAttribute(component, 'href')))
        opfDOM.setAttribute(link, 'href', href)

    #---------------------------------------------------------------------------
    # add the component items to the manifest
    def addManifestItems(self, dstComponentDir, items, vendorName, componentName):
        print 'addManifestItems'
        dstManifest = self.getOpfDom().findAllByTagName('manifest')[0]

        xmlElement.addComment(dstManifest, ' start of component manifest items ' + vendorName + ' - ' + componentName + ' ')

        for item in items:
            newitem = xmlElement.addChildElement(dstManifest, item.localName)

            attributes = xmlElement.getAttributes(item)

            for attr in attributes:
                value = attributes[attr]
                if attr == 'href':
                    href = posixpath.normpath(posixpath.join(dstComponentDir, value))
                    xmlElement.setAttribute(newitem, 'href', href)
                elif attr != 'id':
                    xmlElement.setAttribute(newitem, attr, value)
                else:
                    xmlElement.setAttribute( newitem, attr, 'foo_' + value)

        xmlElement.addComment(dstManifest, ' end of component manifest items ' + vendorName + ' - ' + componentName + ' ')

    # transfer data into the destintation package file
    def transferMetadata(self, srcComponent, dstComponentDir, vendorName, componentName):

        opfDOM = self.getOpfDom()


        items = srcComponent.getOpfManifestItems()
        for item in items:
            if opfDOM.getAttribute(item, 'properties') == 'nav':
                items.remove(item)
                break


        srcMetadata = srcComponent.getComponentMetadata()

        srcSpineItems = srcComponent.getOpfSpineItems()
        assert(len(srcSpineItems) == 1)
        idref = opfDOM.getAttribute(srcSpineItems[0], 'idref')


        self.buildCollection(dstComponentDir, items,  srcMetadata, idref, vendorName, componentName)
        self.addManifestItems(dstComponentDir, items,  vendorName, componentName)

        if self.debug_:
            print opfDOM.toPrettyXML()

        # ensure component vocab is present
        package = opfDOM.getRootElement()
        prefix = opfDOM.getAttribute(package, 'prefix')
        if prefix == None:
            opfDOM.setAttribute(package, 'prefix', componentNamespace)
        elif prefix.find(componentNamespace) < 0:
            opfDOM.setAttribute(package, 'prefix', prefix + ' ' + componentNamespace)


        #write out the updated manifest
        ##print cleanedup
        self.putfile(self.getOpfPath(), opfDOM.toPrettyXML())

# ------------------------------------------------------------------------------
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

        metadataItems = self.packagedom_.getMetadataItems()
        for meta in metadataItems:
            prop = self.getOpfDom().getAttribute(meta, 'property')
            if prop != None:
                componentMetadatum.append({'property': prop, 'value': self.getOpfDom().getText(meta)})

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