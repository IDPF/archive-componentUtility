#!/bin/bash


find . -name *.epub | xargs rm;
find . -name .DS_Store | xargs rm;
find . -name *.*~ | xargs rm;

rm -f *.pyc
rm -rf Acme_Gallery_example.extracted
rm -rf epub/integratedComponent
rm -rf epub/componentContainer.merged




