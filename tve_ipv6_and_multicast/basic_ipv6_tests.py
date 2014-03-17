#!/usr/bin/env python

import unittest
import pexpect
import os
import re
import sys
import json
from ofertieutils import Ofertie
from time import sleep
from mininet.util import quietRun

class IPv6Tests( unittest.TestCase ):

    network = '' 

    def nottest1( self ):
        print "Test 1: Sanity test that IPv6 and OpenFlow controller are working"
        network = Ofertie.createShell( 'basicIPv6' )
        Ofertie.configureNetwork( network, 'basicIPv6' )
	ping = Ofertie.doPing( network, 'h1', 'h2' )
        self.assertGreater( ping.pkts_recv,  0, 'Received ' + str(ping.pkts_recv) + ' packet(s) for ping h1 -> h2' )
        print "SUCCESS: Received " + str(ping.pkts_recv) + " packet(s) for ping h1 -> h2"
        ping6 = Ofertie.doPing6( network, 'h1', 'fd10:0:0::2' )
        self.assertGreater( ping6.pkts_recv, 0, 'Received ' + str(ping6.pkts_recv) + ' packet(s) for ping6 h1 -> fd10:0:0::2' )
        print "SUCCESS: Received " + str(ping6.pkts_recv) + " packet(s) for ping6 h1 -> fd10:0:0::2"
        Ofertie.doDpctl( network, 's1', 'meter-mod', 'cmd=add,flags=1,meter=1 drop:rate=20' )
        Ofertie.doDpctl( network, 's1', 'flow-mod', 'table=0,cmd=add eth_type=0x86dd meter:1 apply:output=2' )
        print "Modified flow for switch s1 to significantly rate limit IPv6 packets."
        sleep(5)
        ping = Ofertie.doPing( network, 'h1', 'h2' )
        self.assertGreater( ping.pkts_recv, 0, 'Received ' + str(ping.pkts_recv) + ' packet(s) for ping h1 -> h2' )
        print "SUCCESS: Received " + str(ping.pkts_recv) + " packet(s) for ping h1 -> h2"
        ping6 = Ofertie.doPing6( network, 'h1', 'fd10:0:0::2' )
        self.assertEqual( ping6.pkts_recv, 0, 'Received ' + str(ping6.pkts_recv) + ' packet(s) for ping6 h1 -> fd10:0:0::2' )
        print "SUCCESS: Received " + str(ping6.pkts_recv) + " packet(s) for ping6 h1 -> fd10:0:0::2"
        Ofertie.finished( network )

    def test2( self ):
	print "Test 2: Various types of IPv4 and IPv6 traffic pre and post flow mods"
	network = Ofertie.createShell( 'basicIPv6' )
        Ofertie.configureNetwork( network, 'basicIPv6' )
	print "Starting iperf3 server on ROIA provider"
	iperf_pid = Ofertie.doIperf3Server( network, 'h2' )

        print "Testing IPv4 TCP from ROIA player"
        filename = Ofertie.doIperf3( network, 'h1', '10.0.0.2', '-4' )
        results = Ofertie.getIperf3Results(filename)
        self.assertFalse('error' in results)
        print "  Data rate: " + str(results['bandwidth']) + "Mb/s"
        print "  Data loss: " + str(results['throughput']['lost_percent']) + "%"
	print "  Data restransmits: " + str(results['throughput']['retransmits'])

#	print "Testing IPv4 TCP from ROIA player"
#        Ofertie.doIperf3Debug( network, 'h1', '10.0.0.2', '-t 10 -P 5' )
#	sleep(5)
#	Ofertie.finished( network )
#	sleep(5)

        print "Testing IPv6 TCP from ROIA player"
	filename = Ofertie.doIperf3( network, 'h1', 'fd10:0:0::2', '-6' )
        results = Ofertie.getIperf3Results(filename)
	self.assertFalse('error' in results)
        print "  Data rate: " + str(results['bandwidth']) + "Mb/s"
        print "  Data lost: " + str(results['throughput']['lost_percent']) + "%"
	print "  Data restransmits: " + str(results['throughput']['retransmits'])

	print "Testing IPv4 UDP from ROIA player"
        filename = Ofertie.doIperf3( network, 'h1', '10.0.0.2', '-4 -u -b 10M' )
        results = Ofertie.getIperf3Results(filename)
        self.assertFalse('error' in results)
        print "  Data rate: " + str(results['bandwidth']) + "Mb/s"
        print "  Data lost: " + str(results['throughput']['lost_percent']) + "%"
	print "  Data jitter: " + str(results['throughput']['jitter']) + "ms"

        print "Testing IPv6 TCP from ROIA player"
        filename = Ofertie.doIperf3( network, 'h1', 'fd10:0:0::2', '-6 -u -b 10M' )
        results = Ofertie.getIperf3Results(filename)
        self.assertFalse('error' in results)
        print "  Data rate: " + str(results['bandwidth']) + "Mb/s"
        print "  Data lost: " + str(results['throughput']['lost_percent']) + "%"
        print "  Data jitter: " + str(results['throughput']['jitter']) + "ms"

	print "Testing IPv4 UDP in parallel from ROIA player"
        filename = Ofertie.doIperf3( network, 'h1', '10.0.0.2', '-4 -u -b 10M -P 5' )
        results = Ofertie.getIperf3Results(filename)
        self.assertFalse('error' in results)
        print "  Data rate: " + str(results['bandwidth']) + "Mb/s"
        print "  Data lost: " + str(results['throughput']['lost_percent']) + "%"
        print "  Data jitter: " + str(results['throughput']['jitter']) + "ms"

	Ofertie.finished( network )


if __name__ == '__main__':
    unittest.main()

