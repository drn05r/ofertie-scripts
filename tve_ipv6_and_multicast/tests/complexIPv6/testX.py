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

class ComplexIPv6TestX( unittest.TestCase ):

    output_type = "machine"
    output_destination = "file"
    topology = "complexIPv6"
    basepath = str(os.path.normpath(rootdir))

    def testX( self ):
        print >> sys.stderr, "Test X: A test for X"
        network = Ofertie.setupNetwork( self.topology, self.basepath )
        iperf_pid = Ofertie.doIperf3Server( network, 'h2' )

        test_file = os.path.normpath(os.path.join( self.basepath, 'tests', self.topology, 'testX.json' ))
        json_data = open(test_file)
        tests = json.load(json_data)
        random.shuffle(tests)

        ofcommands_file = os.path.normpath(os.path.join( self.basepath, 'dpctl', self.topology, 'testX.json' ))
        json_data = open(ofcommands_file)
        ofcommands_list = json.load(json_data)

        results_folder = os.path.normpath(os.path.join( self.basepath, 'results', self.topology, "testX" ))

        Ofertie.runTestSets( network, tests, ofcommands_list, self, results_folder )

        Ofertie.killProcess( network, 'h2', iperf_pid )
        Ofertie.finished( network )


if __name__ == '__main__':
    unittest.main()

