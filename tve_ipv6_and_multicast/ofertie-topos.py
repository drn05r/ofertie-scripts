"""ofertie-topos.py

Topologies for testing OFERTIE network scenarios

"""

import os
import sys
from mininet.topo import Topo
from mininet.node import Node

class BasicIPv6( Topo ):
    "Topology with 2 hosts and 2 switches connected end-to-end."

    def __init__( self ):
        "Creating Topology OFERTIE 1 (2 hosts, 2 switches)"

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        firstHost = self.addHost( 'h1' )
        secondHost = self.addHost( 'h2' )

        firstSwitch = self.addSwitch( 's1' )
        secondSwitch = self.addSwitch( 's2' )

        # Add links
        self.addLink( firstHost, firstSwitch, 1, 1 )
        self.addLink( firstSwitch, secondSwitch, 2, 1 )
        self.addLink( secondSwitch, secondHost, 2, 1 )


class BasicIPv6Multicast( Topo):
    "Topology with 4 hosts and 2 switches.  Host 1 and 2 are connected to the first switch, which is also connected to the second swutch which connects the remaining two hosts"
    def __init__( self ):
        "Creating Topology OFERTIE 4 (4 hosts, 2 switches)"

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        firstHost = self.addHost( 'h1' )
        secondHost = self.addHost( 'h2' )
        thirdHost = self.addHost( 'h3' )
	fourthHost = self.addHost( 'h4' )
	
	firstSwitch = self.addSwitch( 's1' )
        secondSwitch = self.addSwitch( 's2' )

        self.addLink( firstHost, firstSwitch, 1, 1 )
        self.addLink( secondHost, firstSwitch, 1, 2 )
        self.addLink( firstSwitch, secondSwitch, 3, 1 )
        self.addLink( secondSwitch, thirdHost, 2, 1 )
        self.addLink( secondSwitch, fourthHost, 3, 1 )
	

class ComplexIPv6( Topo ):
    "Topology with 3 hosts and 4 switches.  The first host connects to the first and second switches.  The third hosts connects to the second and third switches both of which connect to the second host.  The first switch connects to the fourth switch which then connects to the second host"

    def __init__( self ):
        "Creating Topology OFERTIE 4 (3 hosts, 4 switches)"

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        firstHost = self.addHost( 'h1' )
        secondHost = self.addHost( 'h2' )
        thirdHost = self.addHost( 'h3' )

        firstSwitch = self.addSwitch( 's1' )
        secondSwitch = self.addSwitch( 's2' )
        thirdSwitch = self.addSwitch( 's3' )
        fourthSwitch = self.addSwitch( 's4' )

        # Add links
        self.addLink( firstHost, firstSwitch, 1, 1 )
	self.addLink( firstHost, secondSwitch, 2, 1 )
	self.addLink( firstSwitch, fourthSwitch, 2, 1 )
        self.addLink( thirdHost, secondSwitch, 1, 2 )
        self.addLink( thirdHost, thirdSwitch, 2, 1 )
# self.addLink( secondSwitch, fourthSwitch, 3, 2)
	self.addLink( secondSwitch, secondHost, 4, 1)
	self.addLink( thirdSwitch, secondHost, 2, 2)
	self.addLink( fourthSwitch, secondHost, 3, 3)

class Loopback( Topo ):
    "Loopback topology"

    def __init__( self ):
        "Creating Loopback topology (3 hosts, 3 switches)"

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        firstHost = self.addHost( 'h1' )
        secondHost = self.addHost( 'h2' )
        thirdHost = self.addHost( 'h3' )

	firstSwitch = self.addSwitch( 's1' )
	secondSwitch = self.addSwitch( 's2' )
	thirdSwitch = self.addSwitch( 's3' )
	
	self.addLink( firstHost, firstSwitch, 1, 1 )
	self.addLink( firstSwitch, secondHost, 2, 1 )
	self.addLink( secondHost, secondSwitch, 2, 1 )
	self.addLink( secondSwitch, thirdHost, 2, 1 )
	self.addLink( thirdHost, thirdSwitch, 2, 1 )
	self.addLink( thirdSwitch, firstHost, 2, 2 )


topos = { 'basicIPv6': ( lambda: BasicIPv6() ), 'basicIPv6Multicast': ( lambda: BasicIPv6Multicast() ), 'complexIPv6': ( lambda: ComplexIPv6() ), 'loopback': ( lambda: Loopback() ) }

