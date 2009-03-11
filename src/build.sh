#!/bin/sh
rm -rf dist/

python setup.py bdist_egg
rm -rf build/
rm -rf waferslim.egg-info/

python setup.py sdist --formats=zip
name=`ls dist/*.zip | awk -F\.zip '{print $1}'`
mv $name.zip $name-py2.5.zip
