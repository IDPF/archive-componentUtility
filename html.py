import xml.dom.minidom as minidom

__author__ = 'wmanis'


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


html = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang='en-us' lang='en-us'>
	<head>
		<meta charset="utf-8"/>
		<meta name="description" content=""/>
		<meta name="author" content=""/>


		<title>IDPF Component - Gallery Sample</title>
	</head>

	<body>
		<h3>Component container</h3>
        xx
		<iframe id="component1"/>
        xx
	</body>
</html>"""

doc = minidom.parseString(html)

node = walk(doc, 'component1')

if node != None:
    attr = doc.createAttribute('src')
    attr.value = 'foo/bar.html'
    node.attributes.setNamedItem(attr)

lines = doc.toprettyxml()
lines = lines.split('\n')

trimmedlines = []
for line in lines:
    line = line.rstrip()
    if len(line) != 0:
        trimmedlines.append(line)

#print trimmedlines
cleanedup = '\n'.join(trimmedlines)

print cleanedup
