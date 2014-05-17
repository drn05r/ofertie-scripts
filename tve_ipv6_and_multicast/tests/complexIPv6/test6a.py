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

class ComplexIPv6Test6a( unittest.TestCase ):

    test_name = "test6a"
    output_type = "machine"
    output_destination = "file"
    topology = "complexIPv6"
    basepath = str(os.path.normpath(rootdir))
    iperf_type = 'iperf3'
    iperf_server = 'h2'
    iperf_bg_server = 'h2'
    iperf_bg_server_ip = '10.0.102.2'
    iperf_bg_client = 'h3'
    iperf_bg_traffic = ""

    def test6a( self ):
        print >> sys.stderr, "Test 6a: Test traffic with a vlan tag"
        network = Oftutils.setupNetwork( self.topology, self.basepath )

        test_file = os.path.normpath(os.path.join( self.basepath, 'config', 'iperf', self.topology, 'test6.json' ))
        json_data = open(test_file)
        tests = json.load(json_data)
        random.shuffle(tests)

        ofcommands_file = os.path.normpath(os.path.join( self.basepath, 'config', 'dpctl', self.topology, 'test6.json' ))
        json_data = open(ofcommands_file)
        ofcommands_list = json.load(json_data)

        results_folder = os.path.normpath(os.path.join( self.basepath, 'results', self.topology, "test6a" ))
        Oftutils.runTestSets( network, tests, ofcommands_list, self, results_folder )

        Oftutils.finished( network )


if __name__ == '__main__':
    unittest.main()

