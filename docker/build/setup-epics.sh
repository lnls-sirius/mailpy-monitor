#!/bin/sh

# this script download and compile EPICS base 3.15.6
# author: Rafael Ito
# Controls Group LNLS - Brazilian Synchrotron Light Source Laboratory

cd /opt
mkdir epics-R3.15.6
cd epics-R3.15.6
wget https://epics.anl.gov/download/base/base-3.15.6.tar.gz
tar -xvzf base-3.15.6.tar.gz
rm base-3.15.6.tar.gz
mv base-3.15.6 base
cd base
make
