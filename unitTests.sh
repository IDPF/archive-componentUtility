#!/bin/bash

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


rm -f *.epub
rm -rf Acme_Gallery_example.extracted


echo ""
echo "############################"
echo "	Setup"
echo "############################"
cd epub
rm -f *.epub
rm -rf integratedComponent
rm -rf componentContainer.merged
createpub componentContainer
cd ..

cd components
rm -f *.epub
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
./componentUtility.py -c components/gallery.epub
./componentUtility.py -c components/gallery2.epub
./componentUtility.py -c components/gallery3.epub
echo ""


echo "############################"
echo "############################"
echo "	Install components into epubs"
echo "############################"
echo "############################"
./componentUtility.py -i components/gallery.epub epub/componentContainer.epub
echo ""
./componentUtility.py -i components/gallery2.epub epub/componentContainer.merged.epub -o epub/integratedComponent.epub
echo ""
./componentUtility.py -i components/gallery3.epub epub/integratedComponent.epub -o epub/integratedComponent.epub


unzip -o epub/componentContainer.merged.epub -d epub/componentContainer.merged
unzip -o epub/integratedComponent.epub -d epub/integratedComponent


echo ""
echo "############################"
echo "############################"
echo "	List installed components"
echo "############################"
echo "############################"
./componentUtility.py -l epub/integratedComponent.epub
echo ""

echo ""
echo "############################"
echo "############################"
echo "	Extrac components"
echo "############################"
echo "############################"
./componentUtility.py -x epub/integratedComponent.epub Acme Gallery_example
echo ""

unzip -o Acme_Gallery_example.extracted.epub -d Acme_Gallery_example.extracted


