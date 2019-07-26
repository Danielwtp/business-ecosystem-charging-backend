#!/bin/bash

if [ -d "./virtenv" ]; then
    source virtenv/bin/activate
fi

# Download and install Python dependencies
pip3 install "pymongo==3.8.0"
pip3 install "Django==2.0"
#pip3 install https://github.com/django-nonrel/djangotoolbox/archive/master.zip
pip3 install djongo
pip3 install "nose==1.3.6" "django-nose==1.4.6"

pip3 install "schedule==0.6.0" #"django-crontab==0.6.0"
pip3 install requests
pip3 install requests[security]
pip3 install regex
pip3 install six
#pip3 install paypalrestsdk

pip3 install "coverage==4.5.3"
pip3 install "mock==3.0.5"
pip3 install "nose-parameterized==0.6.0"
