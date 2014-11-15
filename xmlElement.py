import xml.dom.minidom as minidom

__author__ = 'wmanis'


def setAttribute(node, name, value):
    if node.attributes.has_key(name):
        attr = node.attributes[name]
    else:
        attr = node.ownerDocument.createAttribute(name)
        node.attributes.setNamedItem(attr)
    attr.value = value

def getAttributeValue(node, name):
    if node.attributes.has_key(name):
        return node.attributes[name].value
    return None

def addChildElement(parent, tagname, attrs=None, ns=None):
    node = parent.ownerDocument.createElement(tagname)
    if attrs:
        for attr in attrs:
            setAttribute(node, attr, attrs[attr])
    parent.appendChild(node)
    return node

def addTextNode(parent, text):
    node = parent.ownerDocument.createTextNode(text)
    parent.appendChild(node)
    return node

def addComment(parent, text):
    node = parent.ownerDocument.createComment(text)
    parent.appendChild(node)
    return node

def getAttributes(node):
    attributes = {}
    if node.nodeType == node.ELEMENT_NODE:
        for attr in node.attributes.items():
            attributes[attr[0]] = attr[1]
    return attributes

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

def removeNode(node):
    parent = node.parentNode
    if parent:
        parent.removeChild(node)
