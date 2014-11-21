import xml.dom.minidom as minidom

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


#-----------------------------------------------------------------
def isElement(node):
    return node.nodeType == node.ELEMENT_NODE

#-----------------------------------------------------------------
def setAttribute(node, name, value):
    if node.attributes.has_key(name):
        attr = node.attributes[name]
    else:
        attr = node.ownerDocument.createAttribute(name)
        node.attributes.setNamedItem(attr)
    attr.value = value

#-----------------------------------------------------------------
def getAttributeValue(node, name):
    if node.attributes.has_key(name):
        return node.attributes[name].value
    return None

#-----------------------------------------------------------------
def addChildElement(parent, tagname, attrs=None, ns=None):
    node = parent.ownerDocument.createElement(tagname)
    if attrs:
        for attr in attrs:
            setAttribute(node, attr, attrs[attr])
    parent.appendChild(node)
    return node

def appendChild(parent, node):
    parent.appendChild(node)

#-----------------------------------------------------------------
def addTextNode(parent, text):
    node = parent.ownerDocument.createTextNode(text)
    parent.appendChild(node)
    return node

#-----------------------------------------------------------------
def addComment(parent, text):
    node = parent.ownerDocument.createComment(text)
    parent.appendChild(node)
    return node

#-----------------------------------------------------------------
def getAttributes(node):
    attributes = {}
    if node.nodeType == node.ELEMENT_NODE:
        for attr in node.attributes.items():
            attributes[attr[0]] = attr[1]
    return attributes

#-----------------------------------------------------------------
def getChildElements(node):
    children = []
    for child in node.childNodes:
        if child.nodeType == node.ELEMENT_NODE:
            children.append(child)
    return children

#-----------------------------------------------------------------
def findFirstChildElement(node, name, attrs = None):
    for child in node.childNodes:
        if child.nodeType == node.ELEMENT_NODE and child.localName == name:
            if attrs != None:
                targetAttrs = getAttributes(child)
                testlen = len(attrs)
                for attr in attrs:
                    if targetAttrs[attr] == attrs[attr]:
                        testlen -= 1
                if testlen == 0:
                    return child
            else:
                return child
    return None

#-----------------------------------------------------------------
def getText(node):
    text = []

    def walk(node, text):
        if node.nodeType == node.TEXT_NODE:
            text.append(node.data)
        elif node.nodeType == node.ELEMENT_NODE:
            for child in node.childNodes:
                walk(child, text)

    walk(node, text)
    return ''.join(text)

#-----------------------------------------------------------------
def removeNode(node):
    parent = node.parentNode
    if parent:
        parent.removeChild(node)


#-----------------------------------------------------------------
def cloneNode(node):
    return node.cloneNode(True)


def toPrettyXML(node):
    if node.nodeType == node.ELEMENT_NODE:
        return node.toprettyxml()
    elif node.nodeType == node.DOCUMENT_NODE:
        return node.documentElement.toprettyxml()

    return "????????????"

