You will need python v2.7, should exist on Macs, Windows may require an install.

Execute 'python componentInstaller.py', this defaults to transferring
the 2 components in the components directory into a copy of the
epub/componentContainer.epub.

Or you can execute 'python componentInstaller.py dst.epub component.epub component2.epub ...'

Notes:

components/gallery.epub - has the structure that Garth proposed
components/gallery2.epub - has a more conventional structure 

I have opted not to rely on the directory structure in the epub, but
rather on the component:creator and component:name to creat the destination
directory.