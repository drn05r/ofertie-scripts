#!/bin/bash
if [ `whoami` != "root" ]; then
        echo "This script must be run as root or with sudo."
        exit 1
fi
d=`dirname $0`
basedir=`cd ${d}; pwd` # We need to know the base directory where the script resides
cd ${basedir}
if [ -f settings.bash ]; then
        source settings.bash
else
        source default_settings.bash
fi
echo -e "\n\novs-vsctl del-br ${bridge_intf}"
ovs-vsctl del-br ${bridge_intf}
echo -e "\n\nservice networking restart"
service networking restart
echo -e "\n\ndhclient ${primary_intf}"
dhclient ${primary_intf}
