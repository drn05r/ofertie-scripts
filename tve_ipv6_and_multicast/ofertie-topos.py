"""ofertie-topos.py

Topologies for testing OFERTIE network scenarios

"""

from mininet.topo import Topo

class Topo0( Topo ):
    "Topology with 2 hosts and 1 switch connected end-to-end."

    def __init__( self ):
        "Creating Topology OFERTIE 0 (2 hosts, 1 switch)"

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        firstHost = self.addHost( 'h1' )
        secondHost = self.addHost( 'h2' )

        firstSwitch = self.addSwitch( 's1' )

	self.addLink( firstHost, firstSwitch )
        self.addLink( firstSwitch, secondHost )


class Topo1( Topo ):
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
        self.addLink( firstHost, firstSwitch )
        self.addLink( firstSwitch, secondSwitch )
        self.addLink( secondSwitch, secondHost )


class Topo2( Topo ):
    "Topology with 2 hosts and 3 switches. Host 1 connected via two switches to third switch that is connected to host 2."

    def __init__( self ):
        "Creating Topology OFERTIE 2 (2 hosts, 3 switches)"

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        firstHost = self.addHost( 'h1' )
        secondHost = self.addHost( 'h2' )

        firstSwitch = self.addSwitch( 's1' )
        secondSwitch = self.addSwitch( 's2' )
        thirdSwitch = self.addSwitch( 's3' )

        # Add links
        self.addLink( firstHost, firstSwitch )
        self.addLink( firstHost, secondSwitch )
        self.addLink( firstSwitch, thirdSwitch )
        self.addLink( secondSwitch, thirdSwitch )
        self.addLink( thirdSwitch, secondHost )


class Topo3( Topo ):
    "Topology with 3 hosts and 5 switches completely interconnected."

    def __init__( self ):
        "Creating Topology OFERTIE 3 (3 hosts, 5 switches)"

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
        fifthSwitch = self.addSwitch( 's5' )

        # Add links
        self.addLink( firstHost, firstSwitch )
        self.addLink( firstHost, thirdSwitch )
        self.addLink( secondHost, firstSwitch )
        self.addLink( secondHost, secondSwitch )
        self.addLink( firstSwitch, secondSwitch )
#       self.addLink( firstSwitch, thirdSwitch )
#       self.addLink( firstSwitch, fourthSwitch )
#       self.addLink( firstSwitch, fifthSwitch )
        self.addLink( secondSwitch, thirdSwitch )
#       self.addLink( secondSwitch, fourthSwitch )
#       self.addLink( secondSwitch, fifthSwitch )
        self.addLink( thirdSwitch, fourthSwitch )
#       self.addLink( thirdSwitch, fifthSwitch )
        self.addLink( fourthSwitch, fifthSwitch )
        self.addLink( fourthSwitch, thirdHost )
        self.addLink( fifthSwitch, thirdHost )

topos = { 'topo0': ( lambda: Topo0() ), 'topo1': ( lambda: Topo1() ), 'topo2': ( lambda: Topo2() ), 'topo3': ( lambda: Topo3() ) }

