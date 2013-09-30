#!/bin/bash

# Set up an l2 ethernet bridge (TAP) on this host.
# Installs bridge-start, bridge-stop scripts, configures
# everything and generates CA, server and client certificates.

# Change the following variables as approperiate:
#================================================

# For client setup: the remote server to connect
VPN_SERVER_IP="10.216.33.103"

# Bridge details (server):
BRIDGE_IFACE="eth2"
BRIDGE_IP="192.168.0.10"
BRIDGE_NETMASK="255.255.255.0"
BRIDGE_BCAST="192.168.0.255"

CLIENT_ADDRESS_RANGE="192.168.0.50 192.168.0.100"
VPN_PROTOCOL="udp"

# CA certficate values:
KEY_COUNTRY="GB"
KEY_PROVINCE="HAMPSHIRE"
KEY_CITY="SOUTHAMPTON"
KEY_ORG="OpenVPN-OFELIA-test"
KEY_EMAIL="xyz@soton.ac.uk"

# for client key generation
CLIENT="client1"

# Source config file?
if [ -f "./tap.conf" ]; then { source ./tap.conf; } fi
if [ -f "/etc/openvpn/tap.conf" ]; then { source /etc/openvpn/tap.conf; } fi

#================================================


if [ $USER != root ]; then { echo "ERROR: Run as root" ; exit 1; } fi

apt-get -qy install openvpn
if [ $? -ne 0 ]; then { echo "ERROR: Can't apt-get install openvpn: check connection and try apt-get update" ; exit 1; } fi



if [ "$1" = "server" ]
then

echo "SERVER SETUP"

apt-get -qy install bridge-utils
if [ $? -ne 0 ]; then { echo "ERROR: Can't apt-get install bridge-utils: check connection and try apt-get update" ; exit 1; } fi

echo "installing bridge-start and bridge-stop"
cat << EOF > /usr/local/bin/bridge-start
#!/bin/bash

#################################
# Set up Ethernet bridge on Linux
# Requires: bridge-utils
#################################

# Define Bridge Interface
br="br0"

# Define list of TAP interfaces to be bridged,
# for example tap="tap0 tap1 tap2".
tap="tap0"

# Define physical ethernet interface to be bridged
# with TAP interface(s) above.
eth="${BRIDGE_IFACE}"
eth_ip="${BRIDGE_IP}"
eth_netmask="${BRIDGE_NETMASK}"
eth_broadcast="${BRIDGE_BCAST}"

for t in \$tap; do
    openvpn --mktun --dev \$t
done

brctl addbr \$br
brctl addif \$br \$eth

for t in \$tap; do
    brctl addif \$br \$t
done

for t in \$tap; do
    ifconfig \$t 0.0.0.0 promisc up
done

ifconfig \$eth 0.0.0.0 promisc up

ifconfig \$br \$eth_ip netmask \$eth_netmask broadcast \$eth_broadcast

exit 0
EOF

cat << EOF > /usr/local/bin/bridge-stop
#!/bin/bash

####################################
# Tear Down Ethernet bridge on Linux
####################################

# Define Bridge Interface
br="br0"

# Define list of TAP interfaces to be bridged together
tap="tap0"

ifconfig \$br down
brctl delbr \$br

for t in \$tap; do
    openvpn --rmtun --dev \$t
done
EOF

chmod +x /usr/local/bin/bridge-start
chmod +x /usr/local/bin/bridge-stop


if [ ! -f "/etc/openvpn/easy-rsa/vars" ] ; then
  echo "copying easy-rsa directory"
  cp -r /usr/share/doc/openvpn/examples/easy-rsa/2.0 /etc/openvpn/easy-rsa/
fi

cd /etc/openvpn/easy-rsa

echo "backing up vars"
echo "substituting vars"
sed -i.backup "s/KEY_COUNTRY=\"US\"/KEY_COUNTRY=\"${KEY_COUNTRY}\"/g" ./vars
sed -i.backup "s/KEY_PROVINCE=\"CA\"/KEY_PROVINCE=\"${KEY_PROVINCE}\"/g" ./vars
sed -i.backup "s/KEY_CITY=\"SanFrancisco\"/KEY_CITY=\"${KEY_CITY}\"/g" ./vars
sed -i.backup "s/KEY_ORG=\"Fort-Funston\"/KEY_ORG=\"${KEY_ORG}\"/g" ./vars
sed -i.backup "s/KEY_EMAIL=\"me@myhost.mydomain\"/KEY_EMAIL=\"${KEY_EMAIL}\"/g" ./vars

if [ ! -f ./vars ]; then
  echo "I lost the vars file :("
  exit 1
fi

if [ ! -s ./vars ]; then
  echo "I broke the vars file :("
  exit 1
fi

echo "generating keys for CA and server"
source ./vars
sh ./clean-all
sh ./build-dh
sh ./pkitool --initca
sh ./pkitool --server server

echo "generating key for client"
sh ./pkitool $CLIENT

cd keys
echo "generating TLS key"
openvpn --genkey --secret ta.key

echo "installing server keys in /etc/openvpn"
cp server.crt server.key ca.crt dh1024.pem ta.key /etc/openvpn/

echo "packing up certificates for ${CLIENT}"
echo "moving them to /tmp/openvpn/${CLIENT}.tar"
mkdir -p /tmp/openvpn
tar cf /tmp/openvpn/${CLIENT}.tar ${CLIENT}.{crt,csr,key} ca.crt
chmod 777 /tmp/openvpn/${CLIENT}.tar 


echo "installing /etc/openvpn/server.conf"
cat << EOF > /etc/openvpn/server.conf
##########################################
# Server config file for ethernet bridging
# /etc/openvpn/server.conf
##########################################

proto ${VPN_PROTOCOL}
port 1194

dev tap0

ca /etc/openvpn/ca.crt
cert /etc/openvpn/server.crt
key /etc/openvpn/server.key  # This file should be kept secret
dh /etc/openvpn/dh1024.pem

ifconfig-pool-persist ipp.txt
server-bridge ${BRIDGE_IP} ${BRIDGE_NETMASK} ${CLIENT_ADDRESS_RANGE}
;push "redirect-gateway"

client-to-client
duplicate-cn

keepalive 10 120

;tls-auth /etc/openvpn/ta.key 0 # This file is secret

comp-lzo
persist-key
persist-tun
status openvpn-status.log
verb 3
mute 20
EOF

echo "making firewall rules for tap0 and br0"
iptables -A INPUT -i tap0 -j ACCEPT
iptables -A INPUT -i br0 -j ACCEPT
iptables -A FORWARD -i br0 -j ACCEPT

echo "Server setup COMPLETE"
echo "Now you need to run client setup"





elif [ "$1" = "client" ]
then

echo "CLIENT SETUP"
echo "installing /etc/openvpn/client.conf"
cat << EOF > /etc/openvpn/client.conf
##############################################
# OpenVPN Ethernet bridge client config file
# /etc/openvpn/client.conf
##############################################

client
dev tap
proto udp
remote ${VPN_SERVER_IP} 1194
resolv-retry infinite
nobind
persist-key
persist-tun
;http-proxy-retry # retry on connection failures
;http-proxy [proxy server] [proxy port #]

ca /etc/openvpn/ca.crt
cert /etc/openvpn/${CLIENT}.crt
key /etc/openvpn/${CLIENT}.key
;tls-auth /etc/openvpn/ta.key 1

ns-cert-type server

comp-lzo
verb 3
mute 20
EOF


echo "Retreiving certs for client from server via scp to $VPN_SERVER_IP"
echo -n "username:"
read SCPUSERNAME
scp $SCPUSERNAME@$VPN_SERVER_IP:/tmp/openvpn/${CLIENT}.tar /etc/openvpn/${CLIENT}.tar

if [ $? -ne 0 ]; then { echo "ERROR: Unable to download $VPN_SERVER_IP:/etc/openvpn/$CLIENT.tar" ; exit 1; } fi

cd /etc/openvpn
tar xf ${CLIENT}.tar
rm ${CLIENT}.tar

echo "CLIENT SETUP COMPLETE"
echo "On server:# bridge-start ; service openvpn start"
echo "On this client:$ sudo openvpn /etc/openvpn/client.conf"
echo "And you're away"

else
  echo "Usage: setup-tap (server|client)"
fi

exit 0
