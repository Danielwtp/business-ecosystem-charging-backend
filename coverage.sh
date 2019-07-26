#!/bin/bash

trap 'exit' ERR

pip3 install "coverage==4.5.3"
pip3 install "mock==3.0.5"
pip3 install "nose-parameterized==0.6.0"

cd $WORKSPACE/src

coverage run --branch --source=wstore ./manage.py test --noinput --with-xunit --nologcapture -v 2
coverage xml --omit="*urls*" -i

# Prettify Coverate Report
COVERAGE_FILE=coverage.xml
sed -i 's/\(<coverage [^>]*>\)/\1<sources><source>src<\/source><\/sources>/' $COVERAGE_FILE
sed -i 's/\/opt\/jenkins\/jobs\/WStore-python2.6-django1.4\/workspace\/src\/virtenv\/lib\/python2.7\/site-packages\///g' $COVERAGE_FILE
sed -i 's/.opt.jenkins.jobs.WStore-python2.6-django1.4.workspace.src.virtenv.lib.python2/WStore/g' $COVERAGE_FILE
