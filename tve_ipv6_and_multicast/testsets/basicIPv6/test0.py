#!/usr/bin/env python
import sys
import os
rootdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.sys.path.insert(0, rootdir)
import unittest
import pexpect
import re
import json
import random
import uuid
from ofertieutils import Ofertie
from time import sleep
from mininet.util import quietRun

class BasicIPv6Test0( unittest.TestCase ):

    output_type = "machine"
    output_destination = "file"
    topology = "basicIPv6"
    basepath = str(os.path.normpath(rootdir))

    def test0( self ):
        print >> sys.stderr, "Test 0: Sanity test that IPv6 and OpenFlow controller are working"
        network = Ofertie.setupNetwork( self.topology, self.basepath )

        ping = Ofertie.doPing( network, 'h1', '10.0.0.2', '-s 8186' )
        self.assertGreater( ping.pkts_recv,  0, 'Received ' + str(ping.pkts_recv) + ' packet(s) for ping h1 -> 10.0.0.2' )
        print >> sys.stderr, "SUCCESS: Received " + str(ping.pkts_recv) + " packet(s) for ping h1 -> 10.0.0.2"
        ping6 = Ofertie.doPing6( network, 'h1', 'fd10:0:0::2', '-s 8186' )
        self.assertGreater( ping6.pkts_recv, 0, 'Received ' + str(ping6.pkts_recv) + ' packet(s) for ping6 h1 -> fd10:0:0::2' )
        print >> sys.stderr, "SUCCESS: Received " + str(ping6.pkts_recv) + " packet(s) for ping6 h1 -> fd10:0:0::2"

        print >> sys.stderr, "Modifying flow for switch s1 to significantly rate limit IPv6 packets."
        Ofertie.doDpctl( network, 's1', 'meter-mod', 'cmd=add,flags=1,meter=1 drop:rate=20' )
        Ofertie.doDpctl( network, 's1', 'flow-mod', 'cmd=add,table=0 in_port=2,eth_type=0x86dd meter:1 apply:output=1' )
        Ofertie.doDpctl( network, 's1', 'flow-mod', 'cmd=add,table=0 in_port=1,eth_type=0x86dd meter:1 apply:output=2' )
        print >> sys.stderr, "Modified flow for switch s1 to significantly rate limit IPv6 packets.  Sleeping for " + str(Ofertie.rule_change_sleep) + " seconds to ensure changes are applied."
        sleep(Ofertie.rule_change_sleep)

        ping = Ofertie.doPing( network, 'h1', '10.0.0.2', '-s 8186' )
        self.assertGreater( ping.pkts_recv, 0, 'Received ' + str(ping.pkts_recv) + ' packet(s) for ping h1 -> 10.0.0.2' )
        print >> sys.stderr, "SUCCESS: Received " + str(ping.pkts_recv) + " packet(s) for ping h1 -> 10.0.0.2"
        ping6 = Ofertie.doPing6( network, 'h1', 'fd10:0:0::2', '-s 8186' )
        self.assertLess( ping6.pkts_recv, 3, 'Received ' + str(ping6.pkts_recv) + ' packet(s) for ping6 h1 -> fd10:0:0::2' )
        print >> sys.stderr, "SUCCESS: Received " + str(ping6.pkts_recv) + " packet(s) for ping6 h1 -> fd10:0:0::2"

        Ofertie.finished( network )


if __name__ == '__main__':
    unittest.main()

