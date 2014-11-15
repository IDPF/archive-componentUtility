import xml.dom.minidom as minidom
import xmlElement

__author__ = 'wmanis'


class XMLOM:
    def __init__(self, xmltext):
        self.dom_ = minidom.parseString(xmltext)

    def getRootElement(self):
        for child in self.dom_.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                return child
        return self.dom_

    def findByID(self, elementid):
        def walk(node, elementid):
            if node.attributes != None:
                for attr in node.attributes.values():
                    if attr.name == 'id' and attr.value == elementid:
                        return node

            for child in node.childNodes:
                if child.nodeType == node.ELEMENT_NODE:
                    id = walk(child, elementid)
                    if id != None:
                        return id
            return None

        return walk(self.dom_.documentElement, elementid)

    def findChildrenByTagName(self, node, tagname):
        children = []
        if node.nodeType == node.ELEMENT_NODE:
            for child in node.childNodes:
                if child.nodeType == node.ELEMENT_NODE and child.localName == tagname:
                    children.append(child)
        return children

    def findAllByTagName(self, tagname):
        def walk(node, tagname, found):
            if node.nodeType == minidom.Element.ELEMENT_NODE:
                if node.localName == tagname:
                    found.append(node)

                for child in node.childNodes:
                    walk(child, tagname, found)

        found = []
        walk(self.dom_.documentElement, tagname, found)
        return found

    def setAttribute(self, node, name, value):
        xmlElement.setAttribute(node, name, value)

    def getAttribute(self, node, name):
        return xmlElement.getAttributeValue(node, name)


    def getAttributes(self, node):
        return xmlElement.getAttributes(node)


    def addChild(self, parent, tagname, attrs=None, ns=None):
        return xmlElement.addChildElement(parent, tagname, attrs, ns)


    def addTextNode(self, parent, text):
        return xmlElement.addTextNode(parent, text)

    def addComment(self, parent, data):
        return xmlElement.addComment(parent, data)

    def getText(self, node):
        return xmlElement.getText(node)


    def removeNode(self, node):
        xmlElement.removeNode(node)

    def toPrettyXML(self):
        lines = self.dom_.toprettyxml()
        lines = lines.split('\n')

        trimmedlines = []
        for line in lines:
            line = line.rstrip()
            if len(line) != 0:
                trimmedlines.append(line)

        # print trimmedlines
        return '\n'.join(trimmedlines)


def unitTest():
    html = """<!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang='en-us' lang='en-us'>
            <head>
                <meta charset="utf-8"/>
                <meta name="description" content=""/>
                <meta name="author" content=""/>

                <foo name="1"/>
                <title>IDPF Component - Gallery Sample</title>
            </head>

            <body>
                <h3>Component container</h3>
                xx
                <iframe id="component1"/>
                xx
                <img id="xx"></img>
                <foo name="2dd"/>
                <foo name="3"/>
                <foo name="4"/>
                <foo namex="5dd"/>
            </body>
        </html>"""

    xmlom = XMLOM(html)

    iframeNode = xmlom.findByID('component1')

    xmlElement.setAttribute(iframeNode, 'foo', 'bar')

    node = xmlom.findByID('xx')

    xmlElement.addChildElement(node, 'baz', {'foo': 'bar', 'id': 'monkey'})

    node = xmlom.findByID('monkey')
    print xmlom.toPrettyXML()
    xmlElement.setAttribute(node, 'foo', 'graz')

    print xmlom.toPrettyXML()

    xmlElement.removeNode(iframeNode)

    print xmlom.toPrettyXML()

    nodes = xmlom.findAllByTagName('foo')
    for node in nodes:
        print node, xmlElement.getAttributeValue(node, 'name'), xmlElement.getAttributeValue(node, 'namex')

    print "eoj"


if __name__ == '__main__':
    unitTest()