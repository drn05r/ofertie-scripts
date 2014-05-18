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

class complexIPv6Test8( unittest.TestCase ):

    test_name = "test8"
    output_type = "machine"
    output_destination = "file"
    topology = "complexIPv6"
    basepath = str(os.path.normpath(rootdir))
    iperf_type="iperf"
    iperf_server = "h2 h3 h4"

    def test8( self ):
        print >> sys.stderr, "Test 8: Test IPv4/IPv6 UDP Multicast at different rates and then use OpenFlow stop IPv6 traffic to some hosts."
        network = Oftutils.setupNetwork( self.topology, self.basepath )

        test_file = os.path.normpath(os.path.join( self.basepath, 'config', 'iperf', self.topology, 'test8.json' ))
        json_data = open(test_file)
        tests = json.load(json_data)
        random.shuffle(tests)
        tests.insert(0, {"name":"INIT", "host":"h1", "destination":"ff1e::4321", "arguments":"-V -u -T 32 -b 1M", "multicast":"yes"})

        ofcommands_file = os.path.normpath(os.path.join( self.basepath, 'config', 'dpctl', self.topology, 'test8.json' ))
        json_data = open(ofcommands_file)
        ofcommands_list = json.load(json_data)

        results_folder = os.path.normpath(os.path.join( self.basepath, 'results', self.topology, "test8" ))

        Oftutils.runTestSets( network, tests, ofcommands_list, self, results_folder )
        Oftutils.finished( network )


if __name__ == '__main__':
    unittest.main()

