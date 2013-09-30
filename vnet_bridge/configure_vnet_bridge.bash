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
ip_addr=`ifconfig ${primary_intf} | grep "inet " | awk 'BEGIN{FS="[\t :]+"}{print $4}'`
ip_nmask=`ifconfig ${primary_intf} | grep "inet " | awk 'BEGIN{FS="[\t :]+"}{print $8}'`
gw_host=`route | grep default | grep ${primary_intf} | awk 'BEGIN{FS="[\t ]+"}{print $2}'`
if [ `echo ${gw_host} | grep "[a-z]" | wc -l` -gt 0 ]; then
	gw_ip=`nslookup ${gw_host} | grep "Address: " | awk 'BEGIN{FS=" "}{print $2}'`
else
	gw_ip=${gw_host}
fi
if [ "${ip_addr}" == "" -o "${ip_nmask}" == "" -o "${gw_ip}" == "" ]; then
	echo "Primary interface (${primary_intf}) is not currently configured."
	echo "${ip_addr}|${ip_nmask}|${gw_ip}"
	exit 1
fi
echo -e "service openvswitch-switch restart"
service openvswitch-switch restart
echo -e "\n\novs-vsctl del-br ${bridge_intf}"
ovs-vsctl del-br ${bridge_intf}
echo -e "\n\novs-vsctl add-br ${bridge_intf}"
ovs-vsctl add-br ${bridge_intf}
echo -e "\n\nadd-port ${bridge_intf} ${primary_intf}"
ovs-vsctl add-port ${bridge_intf} ${primary_intf}
echo -e "\n\nadd-port ${bridge_intf} ${vnet_intf}"
ovs-vsctl add-port ${bridge_intf} ${vnet_intf}
echo -e "\n\nifconfig ${primary_intf} 0"
ifconfig ${primary_intf} 0
echo -e "\n\nifconfig ${bridge_intf} ${ip_addr} netmask ${ip_nmask}"
ifconfig ${bridge_intf} ${ip_addr} netmask ${ip_nmask}
echo -e "\n\nroute add default gw ${gw_ip} ${bridge_intf}"
route add default gw ${gw_ip} ${bridge_intf}
