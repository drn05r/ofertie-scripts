#!/usr/bin/env python
mport sys
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


class ComplexLoopIPv6Tests( unittest.TestCase ):

    output_type = 'machine'
    output_destination = 'file'
    topology = 'complexLoopIPv6'

    def nottest1( self ):
        print >> sys.stderr, "Test 1: Sanity test that IPv6 and OpenFlow controller are working"
        network = Ofertie.setupNetwork( self.topology )

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

    def test2( self ): 
        print >> sys.stderr, "Test 2: Various types of IPv4 and IPv6 traffic pre and post flow mods"
        network = Ofertie.setupNetwork( self.topology )
        iperf_pid = Ofertie.doIperf3Server( network, 'h2' )

	json_data = open('tests/' + self.topology + '/test2a.json')
	tests = json.load(json_data)
	random.shuffle(tests)

	json_data = open('dpctl/' + self.topology + '/new.json')
        ofcommands_list = json.load(json_data)

	results_folder = "results/" + self.topology + "/test2" 

	Ofertie.runTestSets( network, tests, ofcommands_list, self, results_folder )
        
        Ofertie.killProcess( network, 'h2', iperf_pid )
        Ofertie.finished( network )

    def nottest3( self ):
	print >> sys.stderr, "Test 3: Test to see how maximum segment size behave on IPv4 and IPv6 pre and post OpenFlow modifications"
        network = Ofertie.setupNetwork( self.topology )
	iperf_pid = Ofertie.doIperf3Server( network, 'h2' )

	json_data = open('tests/' + self.topology + '/test3.json')
        tests = json.load(json_data)
        random.shuffle(tests)

        json_data = open('dpctl/' + self.topology + '/general.json')
        ofcommands_list = json.load(json_data)
	
        results_folder = "results/" + self.topology + "/test3"

        Ofertie.runTestSets( network, tests, ofcommands_list, self, results_folder )

        Ofertie.killProcess( network, 'h2', iperf_pid )
        Ofertie.finished( network )


if __name__ == '__main__':
    unittest.main()

