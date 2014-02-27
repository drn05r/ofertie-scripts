import unittest
import pexpect
import os
import re
import sys
from time import sleep
from mininet.util import quietRun

class Ofertie():

    prompt = 'mininet>'

    @staticmethod
    def getToposFilePath():
        topofile = os.path.dirname( os.path.realpath( __file__ ) )
        topofile = os.path.join( topofile, 'ofertie-topos.py' )
        topofile = os.path.normpath( topofile )
        return topofile

    @staticmethod
    def createShell( topo ):
        print "Creating Mininet shell for "+topo
        topofile = Ofertie.getToposFilePath()
        p = pexpect.spawn( 'mn --custom %s --topo %s --mac --switch user --controller remote' % ( topofile, topo ) )
        p.expect( Ofertie.prompt )
        print "Sleeping for 10 seconds to allow network to initialize"
        sleep(10)
        return p

    @staticmethod
    def expectline( p, command ):
        p.sendline( command )
        p.expect( Ofertie.prompt )

    @staticmethod
    def configureNetwork( p, topo ):
        print "Setting up "+topo
        if topo == 'basicIPv6':
            Ofertie.expectline( p, 'h1 ifconfig h1-eth1 add fd10:0:0::1/48 up' )
            Ofertie.expectline( p, 'h2 ifconfig h2-eth1 add fd10:0:0::2/48 up' )
        elif topo == 'basicIPv6Multicast':
            Ofertie.expectline( p, 'h1 ifconfig h1-eth2 10.0.0.3 netmask 255.255.255.0 up' )
            Ofertie.expectline( p, 'h1 ifconfig h1-eth1 add fd10:0:0::1/48 up' )
            Ofertie.expectline( p, 'h2 ifconfig h2-eth1 add fd10:0:0::2/48 up' )
            Ofertie.expectline( p, 'h1 ifconfig h1-eth2 add fd10:0:0::3/48 up' )
        elif topo == 'complexIPv6':
            Ofertie.expectline( p, 'h1 ifconfig h1-eth1 add fd10:0:0::1/48 up' )
            Ofertie.expectline( p, 'h2 ifconfig h2-eth1 add fd10:0:0::2/48 up' )

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

    @staticmethod
    def getMultipleIfconfigs( p, switch, interfaces ):
        results = ""
        for interface in interfaces:
            Ofertie.expectline( p, switch + ' ifconfig ' + interface )
	    regex = re.compile( r"(^.*(inet|Ethernet).*$)", re.MULTILINE )
            ifconflines = regex.findall ( p.before )
            for line in ifconflines:
                results += line[0].strip() + "\n"
            results += "\n"
	return results

    @staticmethod
    def getMultipleIfconfigIOs( p, switch, interfaces ):
        results = ""
        for interface in interfaces:
            Ofertie.expectline( p, switch + ' ifconfig ' + interface )
            regex = re.compile('RX bytes.*')
            bytes_in_out = regex.findall( p.before )
            results += interface + ": " + bytes_in_out[ 0 ] + "\n"
        results += "\n"
	return results

    @staticmethod
    def doPing( p, source, dest, count, args='' ):
      return Ofertie.doPingGeneric( p, 'ping', source, dest, count, args )

    @staticmethod
    def doPing6( p, source, dest, count, args='' ):
      return Ofertie.doPingGeneric( p, 'ping6', source, dest, count, args )

    @staticmethod
    def doPingGeneric( p, ping_type, source, dest, count, args='' ):
        command = source + " " + ping_type + " -c " + str(count) + " " + args + " " + dest
        Ofertie.expectline( p, command )
        lines = p.before.split( '\n' )
        results = Ping();
        if len(lines) < 4:
          return results
	regex_int = re.compile('[0-9]+');
	pkts = regex_int.findall(lines[-3])
        results = Ping();
        results.pkts_tran = int(pkts[0])
        results.pkts_recv = int(pkts[1])
        if len(pkts) == 4:
          results.pkts_err = int(pkts[2])
          results.pkts_loss_pct = int(pkts[3])
        else:
          results.pkts_loss_pct = int(pkts[2])
        regex_float = re.compile('[0-9]+\.?[0-9]*');          
        rtt = regex_float.findall(lines[-2])
	if len(rtt) == 4:
          results.rtt_min = float(rtt[0])
          results.rtt_max = float(rtt[1])
          results.rtt_avg = float(rtt[2])
          results.rtt_dev = float(rtt[3])
        return results


    @staticmethod 
    def finished( p ):
	print "Finished with Mininet shell"
	p.sendline( 'exit' )
	p.wait()


class Ping():

  def __init__(self):
    self.pkts_tran = 0
    self.pkts_recv = 0
    self.pkts_err = 0
    self.pkts_loss_pct = 0
    self.rtt_min = 0.0
    self.rtt_max = 0.0
    self.rtt_avg = 0.0
    self.rtt_dev = 0.0

  def _setPktsTran(self, pkts_tran=None):
        self._pkts_tran = pkts_tran

  def _getPktsTran(self):
        return self._pkts_tran

  def _setPktsRecv(self, pkts_recv=None):
        self._pkts_recv = pkts_recv

  def _getPktsRecv(self):
        return self._pkts_recv

  def _setPktsErr(self, pkts_err=None):
        self._pkts_err = pkts_err

  def _getPktsErr(self):
        return self._pkts_err

  def _setPktsLossPct(self, pkts_loss_pct=None):
        self._pkts_loss_pct = pkts_loss_pct

  def _getPktsLossPct(self):
        return self._pkts_loss_pct

  def _setRttMin(self, rtt_min=None):
        self._rtt_min = rtt_min

  def _getRttMin(self):
        return self._rtt_min

  def _setRttMax(self, rtt_ax=None):
        self._rtt_max = rtt_max

  def _getRttMax(self):
        return self._rtt_max

  def _setRttAvg(self, rtt_avg=None):
        self._rtt_avg = rtt_avg

  def _getRttAvg(self):
        return self._rtt_avg

  def _setRttDev(self, rtt_dev=None):
        self._rtt_dev = rtt_dev

  def _getRttDev(self):
        return self._rtt_dev

  pkts_tran = property(_getPktsTran, _setPktsTran)
  pkts_recv = property(_getPktsRecv, _setPktsRecv)
  pkts_err = property(_getPktsErr, _setPktsErr)
  pkts_loss_pct = property(_getPktsLossPct, _setPktsLossPct)
  rtt_min = property(_getRttMin, _setRttMin)
  rtt_max = property(_getRttMax, _setRttMax)
  rtt_avg = property(_getRttAvg, _setRttAvg)
  rtt_dev = property(_getRttDev, _setRttDev)

