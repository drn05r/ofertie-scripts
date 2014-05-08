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

class BasicIPv6TestX( unittest.TestCase ):

    output_type = "machine"
    output_destination = "file"
    topology = "basicIPv6"
    basepath = str(os.path.normpath(rootdir))

    def testX( self ):
        print >> sys.stderr, "Test X: A test for X"
        network = Oftutils.setupNetwork( self.topology, self.basepath )
        iperf_pid = Oftutils.doIperf3Server( network, 'h2' )

        test_file = os.path.normpath(os.path.join( self.basepath, 'config', 'iperf', self.topology, 'testX.json' ))
        json_data = open(test_file)
        tests = json.load(json_data)
        random.shuffle(tests)

        ofcommands_file = os.path.normpath(os.path.join( self.basepath, 'config', 'dpctl', self.topology, 'testX.json' ))
        json_data = open(ofcommands_file)
        ofcommands_list = json.load(json_data)

        results_folder = os.path.normpath(os.path.join( self.basepath, 'results', self.topology, "testX" ))

        Oftutils.runTestSets( network, tests, ofcommands_list, self, results_folder )

        Oftutils.killProcess( network, 'h2', iperf_pid )
        Oftutils.finished( network )


if __name__ == '__main__':
    unittest.main()

