#!/bin/bash

${EPUBCHECKDIR:?"Need to set env variable EPUBCHECKDIR to directory containing EPUBCHECK"}

function createpub()
{
    rm -f $@.epub;
    if [ -d "$@" ]; then
        cd $@
        zip -q0X ../$@.epub mimetype;
        zip -qXr9D ../$@.epub *
        cd ..
        echo 'created:' $@.epub
    else
        echo 'unknown directory' $@
    fi
}

function epubcheck()
{
   java -jar  $EPUBCHECKDIR/target/epubcheck.jar $@
}

function xxclean()
{
	find . -name "*.epub" | xargs rm -f
	find . -name .DS_Store | xargs rm -f
	find . -name "*.*~" | xargs rm -f
}


xxclean

rm -rf Acme_Gallery_example.extracted
rm -rf integratedComponent
rm -rf componentContainer.merged


echo ""
echo "############################"
echo "	Setup - build epubs"
echo "############################"
cd epub

createpub componentContainer

cd ../components

createpub gallery
createpub gallery2
createpub gallery3

cd ..
echo "###########################A#"
echo "	Complete setup"
echo "############################"

echo ""
echo "############################"
echo "############################"
echo "	Check for valid component epubs"
echo "############################"
echo "############################"

epubcheck components/gallery.epub
epubcheck components/gallery2.epub
epubcheck components/gallery3.epub

python componentUtility.py -c components/gallery.epub
python componentUtility.py -c components/gallery2.epub
python componentUtility.py -c components/gallery3.epub
echo ""


echo "############################"
echo "############################"
echo "	Install components into epubs"
echo "############################"
echo "############################"
python componentUtility.py -i components/gallery.epub epub/componentContainer.epub
epubcheck epub/componentContainer.merged.epub
echo ""

python componentUtility.py -i components/gallery2.epub epub/componentContainer.merged.epub -o epub/integratedComponent.epub
epubcheck epub/integratedComponent.epub
echo ""

python componentUtility.py -i components/gallery3.epub epub/integratedComponent.epub -o epub/integratedComponent.epub
epubcheck epub/integratedComponent.epub

unzip -o epub/componentContainer.merged.epub -d epub/componentContainer.merged
unzip -o epub/integratedComponent.epub -d epub/integratedComponent
unzip -o epub/integratedComponent.merged.epub -d epub/integratedComponent.merged


echo ""
echo "############################"
echo "############################"
echo "	List installed components"
echo "############################"
echo "############################"
python componentUtility.py -l epub/integratedComponent.epub
echo ""

echo ""
echo "############################"
echo "############################"
echo "	Extract components"
echo "############################"
echo "############################"
python componentUtility.py -x epub/integratedComponent.epub Acme Gallery_example
echo ""


echo "############################"
echo "	check work"
echo "############################"
epubcheck Acme_Gallery_example.extracted.epub

unzip -o Acme_Gallery_example.extracted.epub -d Acme_Gallery_example.extracted


python componentUtility.py -I Acme_Gallery_example.extracted.epub epub/componentContainer.epub OPS/componentContainer.xhtml component1
epubcheck epub/componentContainer.merged.epub
echo "********** DONE **********"