#!/bin/bash

if [ -d "./virtenv" ]; then
    source virtenv/bin/activate
fi

# Download and install Python dependencies
pip3 install "pymongo==3.4.0" "paypalrestsdk==1.11.0"
pip3 install "Django==2.2.1"
pip3 install https://github.com/django-nonrel/djangotoolbox/archive/master.zip
pip3 install https://github.com/django-nonrel/mongodb-engine/archive/master.zip

pip3 install "nose==1.3.6" "django-nose==1.4"

pip3 install "schedule==0.6.0" #"django-crontab==0.6.0"
pip3 install requests
pip3 install requests[security]
pip3 install regex
pip3 install six
pip3 install paypalrestsdk

pip3 install "coverage==4.0.3"
pip3 install "mock==1.0.1"
pip3 install "nose-parameterized==0.5.0"
