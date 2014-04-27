#!/usr/bin/env python
import sys
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
import unittest
import pexpect
import re
import json
import random
import uuid
from ofertieutils import Ofertie
from time import sleep
from mininet.util import quietRun

class BasicIPv6MulticastTests( unittest.TestCase ):

    network = '' 

    def test1( self ):
        print "Test 1: Sanity test that IPv6 multicast and OpenFlow controller are working"
        network = Ofertie.createShell( 'basicIPv6Multicast' )
        Ofertie.configureNetwork( network, 'basicIPv6Multicast' )
	ping = Ofertie.doPing( network, 'h1', 'h3' )
        self.assertGreater( ping.pkts_recv,  0, 'Received ' + str(ping.pkts_recv) + ' packet(s) for ping h1 -> h3' )
        print "SUCCESS: Received " + str(ping.pkts_recv) + " packet(s) for ping h1 -> h3"
        ping6 = Ofertie.doPing6( network, 'h1', 'fd10:0:0::3' )
        self.assertGreater( ping6.pkts_recv, 0, 'Received ' + str(ping6.pkts_recv) + ' packet(s) for ping6 h1 -> fd10:0:0::2' )
        print "SUCCESS: Received " + str(ping6.pkts_recv) + " packet(s) for ping6 h1 -> fd10:0:0::3"
	ping6multicast = Ofertie.doPing6( network, 'h1', 'ff02::1', '-I h1-eth1' )
        Ofertie.finished( network )

if __name__ == '__main__':
    unittest.main()

