VirtualBox Bridging Host and Guest Machines
===========================================

http://eglug.org/book/export/html/3439 provides some useful instructions on how to bridge the host and a guest on VirtualBox.  It's last suggestion is that the instructions for the host machine could be converted into a script which has been done here.  You can run vbox-bridge as follows:

./vbox-bridge COMMAND

Where COMMAND can be either start, stop restart or status.

Beyond this you will still need to configure the guest machine afterwards:

1. Go into VirtualBox and in Settings for the VM (guest machine), Go to Network and enable a second network adapter and attach it to Bridged Adapter.  In the dropdown list select the tap interface as set in the vbox-bridge script (by default this is tap14).  Once done click OK and start up the VM.

2. When the VM has booted login and in a terminal window edit /etc/network/interfaces (using sudo).  Add the following config for the new interface.  Assuming you already had a NAT interface this new Bridged Adapter interface will be eth1.  E.g.:

auto eth1
iface eth1 inet static
  address 192.168.1.101
  netmask 255.255.255.0
  gateway 192.168.0.1
  network 192.168.0.0

  dns-nameservers 8.8.8.8 8.8.4.4

The value for the gateway should be the same as set as GATEWAY in the vbox-bridge script.  The address you use should be an address you are allowed to use on the LAN your Host machine is connected to.  The netmask and network will almost certainly be the same as bridge interface (by default br14) on your host machine.  The DNS servers are just the ones provided by Google.  Feel free to choice other DNS servers you prefer.

3. Once you have saved and exited the editor for /etc/network/interfaces run the following command to bring up the interface (assuming it is eth1):

sudo ifconfig eth1 up

4. You should now be able to ping 8.8.8.8, as well as a global IP address such as google.com.


Using with MiniNet VMs
----------------------
The reason for producing these instructions was to allow a MiniNet network setup on a VirtualBox VM the ability to connect through to the Internet.  If you have an instance of Mininet (and the Open vSwitch controller and switch) installed and the GitHub repoistory (https://github.com/mininet/mininet.git) checked out you can run the script nat.py in examples/.  

Once the MiniNet network is setup and configure after running the script, you can test the network has Internet connetivity by typing:

h1 ping -c 4 8.8.8.8

The functions of nat.py can be used as part of your own Mininet Python scripts to give your own MiniNet networks Internet connectivity.
