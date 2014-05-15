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
from oftestutils import Oftutils
from time import sleep
from mininet.util import quietRun

class BasicIPv6MulticastTest1( unittest.TestCase ):

    test_name = "test1"
    output_type = "machine"
    output_destination = "file"
    topology = "basicIPv6Multicast"
    basepath = str(os.path.normpath(rootdir))
    iperf_type="iperf"
    iperf_server = "h2 h3 h4"

    def test1( self ):
        print >> sys.stderr, "Test 1: Test IPv4/IPv6 UDP to multiple servers in parallel at different rates and then use OpenFlow stop IPv6 traffic to some hosts."
        network = Oftutils.setupNetwork( self.topology, self.basepath )

        test_file = os.path.normpath(os.path.join( self.basepath, 'config', 'iperf', self.topology, 'test1.json' ))
        json_data = open(test_file)
        tests = json.load(json_data)
        random.shuffle(tests)

        ofcommands_file = os.path.normpath(os.path.join( self.basepath, 'config', 'dpctl', self.topology, 'test1.json' ))
        json_data = open(ofcommands_file)
        ofcommands_list = json.load(json_data)

        results_folder = os.path.normpath(os.path.join( self.basepath, 'results', self.topology, "test1" ))

        Oftutils.runTestSets( network, tests, ofcommands_list, self, results_folder )
        Oftutils.finished( network )


if __name__ == '__main__':
    unittest.main()

