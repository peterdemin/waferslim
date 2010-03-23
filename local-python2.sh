#!/bin/bash
# Convenience script for using waferslim without installing it with setup.py
# - use COMMAND_PATTERN=/some/full/file/system/path/local-python2.sh -m waferslim.server ...
basedir=`dirname $0`
cd $basedir/src
python2 $1 $2 $3 $4 $5 $6 $7 $8 $9
