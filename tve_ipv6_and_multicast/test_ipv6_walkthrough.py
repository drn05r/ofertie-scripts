#!/usr/bin/env python

import unittest
import pexpect
import os
import re
import sys
from time import sleep
from mininet.util import quietRun

class IPv6Testing( unittest.TestCase ):

    prompt = 'mininet>'

    @staticmethod
    def getPacketsReceived(output):
	lines = output.split( '\n' )
	if len(lines) > 3:
            regex = re.compile('(\d+) received')
            packets = regex.findall( lines[ -3 ] )
            if len(packets) > 0:
                return int(packets[ 0 ])
	    sys.stderr.write("ERROR: Expected line does not contain number of packets received")
	sys.stderr.write("ERROR: output provided is not from a ping command.")
        return 0		

    def testTopo1( self ):
        "Test OFERTIE topology 1"
        custom = os.path.dirname( os.path.realpath( __file__ ) )
        custom = os.path.join( custom, 'ofertie-topos.py' )
        custom = os.path.normpath( custom )
        p = pexpect.spawn( 'mn --custom %s --topo topo1 --mac --switch user --controller remote' % custom )
	p.expect( self.prompt )
	sleep(10)
	p.sendline( 'h1 ifconfig h1-eth0 add fd10:0:0::1/48 up' )
        p.expect( self.prompt )
	p.sendline( 'h2 ifconfig h2-eth0 add fd10:0:0::2/48 up' )
        p.expect( self.prompt )
	p.sendline( 'h1 ping -c 10 h2' )
        p.expect( self.prompt )
	packets = IPv6Testing.getPacketsReceived(p.before)
        self.assertGreater( packets,  0, 'Received ' + str(packets) + ' for h1 ping -c 10 h2' )
	print "SUCCESS: Received " + str(packets) + " for h1 ping6 -c 10 h2"
	p.sendline( 'h1 ping6 -c 10 fd10:0:0::2' )
	p.expect( self.prompt )
	packets = IPv6Testing.getPacketsReceived(p.before)
	self.assertGreater( packets, 0, 'Received ' + str(packets) + ' for h1 ping6 -c 10 fd10:0:0::2' )
	print "SUCCESS: Received " + str(packets) + " for h1 ping6 -c 10 fd10:0:0::2"
	p.sendline( 's1 dpctl unix:/tmp/s1 meter-mod cmd=add,flags=1,meter=1 drop:rate=20' )
        p.expect( self.prompt )
	p.sendline( 's1 dpctl unix:/tmp/s1 flow-mod table=0,cmd=add eth_type=0x86dd meter:1 apply:output=2' )
	p.expect( self.prompt )
	print "Modified flow for switch s1 to significantly rate limit IPv6 packets."
	sleep(5)
	p.sendline( 'h1 ping -c 10 h2' )
        p.expect( self.prompt )
	packets = IPv6Testing.getPacketsReceived(p.before)
        self.assertGreater( packets, 0, 'Received ' + str(packets) + ' for h1 ping -c 10 h2' )
	print "SUCCESS: Received " + str(packets) + " for h1 ping -c 10 h2"
	p.sendline( 'h1 ping6 -c 10 fd10:0:0::2' )
	p.expect( self.prompt )
	packets = IPv6Testing.getPacketsReceived(p.before)
        self.assertEqual( packets, 0, 'Received ' + str(packets) + ' for h1 ping6 -c 10 fd10:0:0::2' )
	print "SUCCESS: Received " + str(packets) + " for h1 ping6 -c 10 fd10:0:0::2"
	p.sendline( 'exit' )
        p.wait()

if __name__ == '__main__':
    unittest.main()

