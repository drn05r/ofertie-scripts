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
        self.addLink( secondSwitch, fourthSwitch, 3, 2)
	self.addLink( secondSwitch, secondHost, 4, 1)
	self.addLink( thirdSwitch, secondHost, 2, 2)
	self.addLink( fourthSwitch, secondHost, 3, 3)


class ComplexLoopIPv6( Topo ):
    "Complex IPv6 Topology with a Loop"

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
	fourthSwitch = self.addSwitch( 's4' )
		

	self.addLink( firstHost, firstSwitch, 1, 3 )
	self.addLink( firstSwitch, secondSwitch, 2, 1 )
	self.addLink( secondSwitch, thirdSwitch, 2, 1 )
	self.addLink( thirdSwitch, fourthSwitch, 2, 1 )
	self.addLink( fourthSwitch, firstSwitch, 2, 1 )
	self.addLink( secondHost, thirdSwitch, 1, 3 )
	self.addLink( thirdHost, secondSwitch, 1, 3 )

class OfertieTest( Topo ):
    "OFERTIE Test"

    def __init__( self ):
        "Creating sandpit topology for testing out stuff"

	 # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
#	firstHost = self.addHost( 'h1', ip="10.0.1.1" )
#	secondHost = self.addHost( 'h1', ip="10.0.1.2" )
        firstHost = self.addHost( 'h1', ip="fd10:0:0::1/48" )
        secondHost = self.addHost( 'h2', ip="fd10:0:0::2/48" )

	firstSwitch = self.addSwitch( 's1' )
        secondSwitch = self.addSwitch( 's2' )

        # Add links
        self.addLink( firstHost, firstSwitch, 1, 1 )
        self.addLink( firstSwitch, secondSwitch, 2, 1 )
        self.addLink( secondSwitch, secondHost, 2, 1 )


topos = { 'basicIPv6': ( lambda: BasicIPv6() ), 'basicIPv6Multicast': ( lambda: BasicIPv6Multicast() ), 'complexIPv6': ( lambda: ComplexIPv6() ), 'complexLoopIPv6': ( lambda: ComplexLoopIPv6() ), 'ofertieTest': ( lambda: OfertieTest() ) }

