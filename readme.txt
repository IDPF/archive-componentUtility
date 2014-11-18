You will need python v2.7, should exist on Macs, Windows may require an install.

This is alpha software, largely untested.

The goal is to use this to learn and validate our ideas around EPUB Scriptable Component Packaging Specification.

Implementation notes:
    All xml processing is done using xml.dom.minidom, all calls to minidom are hidden behind xmlom and xmlelement.
    No doubt we will have to move to more robust xml (html?) processing, as such I hope to have made the
    transition to another xml/html implementation tractable.

There are two directories in this project containing files for a container epub and two component epubs. These are the
only files used for test cases for far :-(. The files in here can be used to create epubs using epubcheck or the following
bash script:

    function createpub()
    {
        rm -f $@.epub;
        cd $@
        zip -q0X ../$@.epub mimetype;
        zip -qXr9D ../$@.epub *
        cd ..
    }

Run this in the parent directory containing the epub
(e.g. cd epub; createpub componentContainer; epubcheck componentContainer.epub)


Component Utility

Utility for integrating, listing, checking and extracting EPUB components


    Examples:
        componentUtility -i component.epub book.epub
            integrates component.epub into a copy of book.epub named book.merged.epub

        componentUtility -I component.epub book.epub OPS/chap.xhtml component1
            integrates component.epub into a copy of book.epub named book.merged.epub
            and updates iframe element id='component1' in chap.xhtml

        componentUtility -l book.epub
            lists components contained in book.epub

        componentUtility -c component.epub
            checks component.epub to ensure that it is a valid component

        componentUtility -x book.epub creator componentName
            extracts the component with creator & componentName to creator_componentName.extracted.epub
            which should be a valid component epub


See license.txt for license, the license does not apply to the test epubs and their files which may have their own
licenses.