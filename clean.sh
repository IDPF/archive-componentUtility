#!/bin/bash

find . -name "*.epub" | xargs rm -f
find . -name .DS_Store | xargs rm -f
find . -name "*.*~" | xargs rm -f

rm -f *.pyc
rm -rf Acme_Gallery_example.extracted
rm -rf epub/integratedComponent
rm -rf epub/componentContainer.merged




