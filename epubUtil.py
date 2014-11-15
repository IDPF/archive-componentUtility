#!/usr/local/bin/python

from __future__ import with_statement

import os
import sys
import optparse
import zipfile
import posixpath
import urllib
import time
import xmlom
import xmlElement

__author__ = 'wmanis'

componentPrefix = 'component'
componentDirectory = 'components'
componentNamespace = 'component: http://www.idpf.org/vocab/component/#'
opfNamespace = "{http://www.idpf.org/2007/opf}"

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class PackageDom(xmlom.XMLOM):
    def getPackageElement(self):
        return self.getRootElement()

    # ---------------------------------------------------------------------------
    # get the manifest

    def getManifest(self):
        return self.findAllByTagName('manifest')[0]

    # ---------------------------------------------------------------------------
    # get the manifest

    def getManifestItems(self):
        items = []
        for item in self.getManifest().childNodes:
            if xmlElement.isElement(item):
                items.append(item)

        return items


    # ---------------------------------------------------------------------------
    # get the metadata

    def getMetadata(self):
        return self.findAllByTagName('metadata')[0]

    # ---------------------------------------------------------------------------
    # get the metadata

    def getMetadataItems(self):
        return self.findChildrenByTagName(self.getMetadata(), 'meta')

    #---------------------------------------------------------------------------
    # get the spine

    def getSpine(self):
        return self.findAllByTagName('spine')[0]

    #---------------------------------------------------------------------------
    # get the spine items

    def getSpineItems(self):
        return self.findChildrenByTagName(self.getSpine(), 'itemref')

    #---------------------------------------------------------------------------
    # get the spine items

    def getCollections(self):
        return self.findChildrenByTagName(self.packagedom_.getRootElement(), 'collection')

    #
    # #---------------------------------------------------------------------------
    # # debug - print out opf manifest
    #
    # def printManifest(self):
    #     for child in self.getManifest():
    #         print child.tag, child.attrib
    #
    #
    # #---------------------------------------------------------------------------
    # # debug - print out opf metadata
    #
    # def printMetadata(self):
    #     for child in self.getMetadata():
    #         print child.tag, child.attrib
    #
    # #---------------------------------------------------------------------------
    # # debug - print out opf spine
    #
    # def printSpine(self):
    #     for child in self.getSpine():
    #         print child.tag, child.attrib
    #
    # #---------------------------------------------------------------------------
    # # debug - print out opf spine
    #
    # def printCollections(self):
    #     collections = self.getCollections()
    #     for collection in collections:
    #         print collection.tag, collection.attrib
    #

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class EPUBZipContainer:
    def __init__(self, name, debug=True):
        self.name_ = name
        self.zipfile_ = zipfile.ZipFile(name, 'r')
        self.__unzip()
        self.opfpath_ = None
        self.getOpfPath()
        self.debug_ = debug
        self.packagedom_ = PackageDom(self.contents_[self.opfpath_])


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
        if self.opfpath_ == None:
            xmlDom = xmlom.XMLOM(self.contents_['META-INF/container.xml'])
            root = xmlDom.findAllByTagName('rootfile')[0]
            self.opfpath_ = xmlDom.getAttribute(root, 'full-path')
        return self.opfpath_


    # ---------------------------------------------------------------------------
    # get the package xmldom

    def getOpfDom(self):
        if self.packagedom_ == None:
            path = self.getOpfPath()
            opfXML = self.contents_[path]
            self.packagedom_ = xmlom.XMLOM(opfXML)
        return self.packagedom_

    # ---------------------------------------------------------------------------
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

        for item in manifest:
            if xmlElement.getAttributeValue(item, 'id') == xmlid:
                return xmlElement.getAttributeValue(item, 'href')
        return None


    #---------------------------------------------------------------------------
    # get spineitem files
    def getOpfSpineItemFiles(self):
        spinefiles = []
        spineitems = self.getOpfSpineItems()

        for itemref in spineitems:
            idref = xmlElement.getAttributeValue(itemref, 'idref')
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

        srcOpfDir = posixpath.dirname(srcComponent.getOpfPath())

        for item in itemList:
            if xmlElement.getAttributeValue(item, 'properties') == 'nav':
                #do not copy nav doc
                continue

            href = xmlElement.getAttributeValue(item, 'href')
            srcPath = posixpath.normpath(posixpath.join(srcOpfDir, href))
            dstPath = posixpath.normpath(posixpath.join(dstDir, href.split('../').pop()))

            # copy the bytes over
            srcbytes = srcComponent.getfile(srcPath)
            self.putfile(dstPath, srcbytes)


    #---------------------------------------------------------------------------
    # build the collection containing the component

    def buildCollection(self, dstComponentDir, items, srcMetadata, idref, vendorName, componentName):
        rootElement = self.packagedom_.getPackageElement()

        # add comment
        commentString = ' start of component ' + vendorName + ' - ' + componentName + ' transfer time ' + time.asctime(
            time.gmtime()) + ' UTC '
        xmlElement.addComment(rootElement, commentString)

        # add collection
        collection = xmlElement.addChildElement(rootElement, 'collection', {'role': 'component:component'})

        # add metadata to collection
        metadata = xmlElement.addChildElement(collection, 'metadata')

        for datum in srcMetadata:
            meta = xmlElement.addChildElement(metadata, 'meta')
            xmlElement.setAttribute(meta, 'property', datum['property'])
            xmlElement.addTextNode(meta, datum['value'])

        # add manifest collection to collection
        collectionManifest = xmlElement.addChildElement(collection, 'collection', {'role': 'manifest'})
        component = None

        for item in items:
            link = xmlElement.addChildElement(collectionManifest, "link")
            if idref == xmlElement.getAttributeValue(item, 'id'):
                component = item

            #link.set('id', creatorName + item.get('id'))

            href = xmlElement.getAttributeValue(item, 'href')
            print href
            href = posixpath.normpath(posixpath.join(dstComponentDir, href))
            print href
            xmlElement.setAttribute(link, 'href', href)


        # add the html of the component
        link = xmlElement.addChildElement(collection, 'link')
        href = posixpath.normpath(posixpath.join(dstComponentDir, xmlElement.getAttributeValue(component, 'href')))
        xmlElement.setAttribute(link, 'href', href)

    #---------------------------------------------------------------------------
    # add the component items to the manifest

    def addManifestItems(self, dstComponentDir, items, vendorName, componentName):

        # get the manifest element of the package file
        dstManifest = self.getOpfManifest()

        # add comment to indicate start component items
        xmlElement.addComment(dstManifest,
                              ' start of component manifest items ' + vendorName + ' - ' + componentName + ' ')

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
                    xmlElement.setAttribute(newitem, attr, 'foo_' + value)

        # add comment to indicate end of component items

        xmlElement.addComment(dstManifest,
                              ' end of component manifest items ' + vendorName + ' - ' + componentName + ' ')

    #---------------------------------------------------------------------------
    # transfer data into the destintation package file
    def transferMetadata(self, srcComponent, dstComponentDir, vendorName, componentName):

        # get the component items, ignoring the nav doc
        items = srcComponent.getOpfManifestItems()
        for item in items:
            if xmlElement.getAttributeValue(item, 'properties') == 'nav':
                items.remove(item)
                break

        # get the idref of the component base html doc
        srcSpineItems = srcComponent.getOpfSpineItems()
        assert (len(srcSpineItems) == 1)
        idref = xmlElement.getAttributeValue(srcSpineItems[0], 'idref')

        # create component collection
        self.buildCollection(dstComponentDir, items, srcComponent.getComponentMetadata(), idref, vendorName,
                             componentName)

        # copy over component items into manifest
        self.addManifestItems(dstComponentDir, items, vendorName, componentName)

        # ensure component vocab is present
        package = self.packagedom_.getPackageElement()
        prefix = xmlElement.getAttributeValue(package, 'prefix')
        if prefix == None:
            xmlElement.setAttribute(package, 'prefix', componentNamespace)
        elif prefix.find(componentNamespace) < 0:
            xmlElement.setAttribute(package, 'prefix', prefix + ' ' + componentNamespace)

        if self.debug_:
            print self.packagedom_.toPrettyXML()

        # write out the updated manifest
        self.putfile(self.getOpfPath(), self.packagedom_.toPrettyXML())


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class EPUBSpineItem:
    def __init__(self, zipfile, path):
        self.zipfile_ = zipfile
        self.path_ = path
        self.spineXML_ = xmlom.XMLOM(self.zipfile_.getBytes(path))

    def insert(self, elementID, src):
        def walk(node, elementid):
            attributes = xmlElement.getAttributes(node)
            for attr in attributes:
                if attr == 'id' and attributes[attr] == elementid:
                    return node

            children = xmlElement.getChildElements(node)
            for child in children:
                id = walk(child, elementid)
                if id != None:
                    return id
            return None

        node = walk(self.spineXML_.getRootElement(), elementID)
        if node != None:
            xmlElement.setAttribute(node, 'src', src)
            return

        raise "no element with that id"


    def tostring(self):
        lines = self.spineXML_.toPrettyXML()
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
            prop = xmlElement.getAttributeValue(meta, 'property')
            if prop != None:
                componentMetadatum.append({'property': prop, 'value': xmlElement.getText(meta)})

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