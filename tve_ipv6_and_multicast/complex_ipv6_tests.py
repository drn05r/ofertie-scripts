#!/usr/bin/env python

import unittest
import pexpect
import os
import re
import sys
from ofertieutils import Ofertie
from time import sleep
from mininet.util import quietRun

class ComplexIPv6Tests( unittest.TestCase ):

    output_type = 'machine'
    output_destination = 'file'
    topology = 'complexIPv6'

    def test1( self ):
        "IPv6 Test Complex Topology"
        network = Ofertie.setupNetwork( self.topology )
	
        ping = Ofertie.doPing( network, 'h1', '10.0.1.2' )
        self.assertGreater( ping.pkts_recv,  0, 'Received ' + str(ping.pkts_recv) + ' packet(s) for ping h1 -> 10.0.1.2' )
        print "SUCCESS: Received " + str(ping.pkts_recv) + " packet(s) for ping h1 -> 10.0.1.2"
        ping6 = Ofertie.doPing6( network, 'h1', 'fd10:0:1::2' )
        self.assertGreater( ping6.pkts_recv, 0, 'Received ' + str(ping6.pkts_recv) + ' packet(s) for ping6 h1 -> fd10:0:1::2' )
        print "SUCCESS: Received " + str(ping6.pkts_recv) + " packet(s) for ping6 h1 -> fd10:0:1::2"
        Ofertie.doDpctl( network, 's1', 'meter-mod', 'cmd=add,flags=1,meter=1 drop:rate=20' )
        Ofertie.doDpctl( network, 's1', 'flow-mod', 'table=0,cmd=add eth_type=0x86dd meter:1 apply:output=2' )
        print "Modified flow for switch s1 to significantly rate limit IPv6 packets."
        sleep(5)
        ping = Ofertie.doPing( network, 'h1', '10.0.1.2' )
        self.assertGreater( ping.pkts_recv, 0, 'Received ' + str(ping.pkts_recv) + ' packet(s) for ping h1 -> 10.0.1.2' )
        print "SUCCESS: Received " + str(ping.pkts_recv) + " packet(s) for ping h1 -> 10.0.1.2"
        ping6 = Ofertie.doPing6( network, 'h1', 'fd10:0:1::2' )
        self.assertEqual( ping6.pkts_recv, 0, 'Received ' + str(ping6.pkts_recv) + ' packet(s) for ping6 h1 -> fd10:0:1::2' )
        print "SUCCESS: Received " + str(ping6.pkts_recv) + " packet(s) for ping6 h1 -> fd10:0:1::2"
        Ofertie.finished( network )

if __name__ == '__main__':
    unittest.main()

