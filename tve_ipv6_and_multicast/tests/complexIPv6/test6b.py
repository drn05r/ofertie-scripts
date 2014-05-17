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

class ComplexIPv6Test6b( unittest.TestCase ):

    test_name = "test6b"
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

    def test6b( self ):
        print >> sys.stderr, "Test 6b: Test traffic with a vlan tag"
        network = Oftutils.setupNetwork( self.topology, self.basepath )

        test_file = os.path.normpath(os.path.join( self.basepath, 'config', 'iperf', self.topology, 'test6.json' ))
        json_data = open(test_file)
        tests = json.load(json_data)
        random.shuffle(tests)

        ofcommands_file = os.path.normpath(os.path.join( self.basepath, 'config', 'dpctl', self.topology, 'test6.json' ))
        json_data = open(ofcommands_file)
        ofcommands_list = json.load(json_data)

        Oftutils.expectline( network, "s2 dpctl unix:/tmp/s2 meter-mod cmd=add,flags=1,meter=10 drop:rate=5000");
        Oftutils.expectline( network, "s2 dpctl unix:/tmp/s2 flow-mod cmd=add,table=0 in_port=2 meter:10 apply:output=4");

        results_folder = os.path.normpath(os.path.join( self.basepath, 'results', self.topology, "test6b" ))
        Oftutils.runTestSets( network, tests, ofcommands_list, self, results_folder )

        Oftutils.finished( network )


if __name__ == '__main__':
    unittest.main()

