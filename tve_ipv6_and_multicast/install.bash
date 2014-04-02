#!/bin/bash
d=`dirname $0`
BASE_DIR=`cd ${d}; pwd`

echo "Installing package based dependencies"
#sudo apt-get update || { echo "Could not update package list using APT ... aborting!"; exit 1; }
#sudo apt-get install -y autoconf automake bison bridge-utils build-essential bzip2 cmake debhelper dkms fakeroot flex git graphviz libboost-devlibc6-dev libpcap-dev libpcre3-dev libssl-dev libtool libxerces-c2-dev make module-init-tools netbase openssl pkg-config procps python python-all python-argparse python-nose python-pexpect python-qt4 python-twisted-conch python-zopeinterface traceroute unzip uuid-runtime vlan wget || { echo "Could not install all package dependencies ... aborting!"; exit 1; }

cd ${BUILD_DIR}
echo "Downloading non-package dependencies"
if [ ! -d mininet ]; then
	git clone git://github.com/mininet/mininet || echo "Could not clone Git respository for Mininet ... aborting!"; exit 1; }
fi
#if [ ! -d ofsoftswitch13 ]; then
#	git clone https://github.com/CPqD/ofsoftswitch13.git || echo "Could not clone Git respository for OpenFlow 1.3 Soft Switch ... aborting!"; exit 1; }
#fi
#if [ ! -d nox13oflib ]; then
#	git clone https://github.com/CPqD/nox13oflib.git || echo "Could not clone Git respository for OpenFlow 1.3 modifieed NOX controller ... aborting!"; exit 1; }
fi
if [ ! -d iperf ]; then
	git clone https://github.com/esnet/iperf.git  echo "Could not clone Git respoistory for iperf3 ... aborting!"; exit 1; }
fi
#if [ ! -f nbeesrc-12-05-16.zip ]; then
#	wget http://www.nbee.org/download/nbeesrc-12-05-16.php || { echo "Could not download nbeesrc-12-05-16.zip ... exiting!"; exit 1; }
#	unzip nbeesrc-12-05-16.zip || { echo "Could not unzip nbeesrc-12-05-16.zip ... aborting!"; exit 1; }
#fi

echo "\nInstalling Mininet with OpenFlow Software Switch and Modified NOX Controller"
#sudo modprobe 8021q || { echo "Could not enable 8021q kernel module for vlans ... aborting!"; exit 1; }
mininet/util/install.sh -3fxn || { echo "Could not install Mininet core files and dependencies ... aborting!"; exit 1; }

#echo -e "\nInstalling NetBee (Dependency of OpenFlow 1.3 Software Switch)"
#
#cd nbeesrc/src || { echo "No nbeesrc/src/ directory in ${BUILD_DIR} ... aborting!"; exit 1;}
#cmake . || { echo "Could not cmake NetBee from source ... aborting!"; exit 1; }
#make || { echo "Could not make NetBee from source ... aborting!"; exit 1; }
#sudo cp ../bin/libn*.so /usr/local/lib || { echo "Could not copy NetBee shared object files to /usr/local/lib/ ... aborting!"; exit 1; }
#sudo ldconfig || { echo "ldconfig failed to run successfully ... aborting!"; exit 1; }
#sudo cp -R ../include/* /usr/include/ || { echo "Could not copy NetBee include files to /usr/include/ ... aborting!"; exit 1; }

#echo -e "\nInstalling OpenFlow 1.3 Software Switch"
#cd ${BUILD_DIR}/ofsoftswitch13
#./boot.sh || { echo "Could not run boot.sh for OpenFlow 1.3 Software Switch ... aborting!";  exit 1; }
#./configure || { echo "Could not run configure for OpenFlow 1.3 Software Switch ... aborting!";  exit 1; }
#make || { echo "Could not make OpenFlow 1.3 Software Switch ... aborting!";  exit 1; }
#sudo make install || { echo "Could not make install OpenFlow 1.3 Software Switch ... aborting!";  exit 1; }
#cd ${BUILD_DIR}
#
#echo -e "\nInstall OpenFlow 1.3 Modified NOX Controller"
#cd ${BUILD_DIR}/nox13oflib  
#./boot.sh || { echo "Could not run boot.sh for OpenFlow 1.3 Modified NOX Controller ... aborting!";  exit 1; }
#mkdir build || { echo "Could not create build directory for OpenFlow 1.3 Modified NOX Controller ... aborting!";  exit 1; }
#cd build 
#../configure --with-python=no || { echo "Could not run configure for OpenFlow 1.3 Modified NOX Controller ... aborting!";  exit 1; }
#make { echo "Could not make for OpenFlow 1.3 Modified NOX Controller ... aborting!";  exit 1; }
#
