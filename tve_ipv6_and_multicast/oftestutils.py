import unittest
import pexpect
import os
import re
import sys
import uuid
import json
import pprint
import traceback
from time import sleep
from mininet.util import quietRun

class Oftutils():

    prompt = 'mininet>'
    startup_sleep = 10
    rule_change_sleep = 5

    @staticmethod
    def setupNetwork( topo, basepath ):
        network = Oftutils.createShell( topo, basepath )
        Oftutils.configureNetwork( network, topo, basepath )
        return network

    @staticmethod
    def createShell( topo, basepath ):
        print >> sys.stderr, "Creating Mininet shell for "+topo
        topofile = os.path.normpath(os.path.join( basepath, 'ofertie-topos.py' ))
        p = pexpect.spawn( 'mn --custom %s --topo %s --mac --switch user --controller remote' % ( topofile, topo ) )
        p.expect( Oftutils.prompt )
        print >> sys.stderr, "Sleeping for " + str(Oftutils.startup_sleep) + " seconds to allow the OpenFlow controller to learn the network"
        sleep(Oftutils.startup_sleep)
        return p

    @staticmethod
    def getTopologyIPHostMap( basepath, topo ):
        topo_filename = os.path.normpath(os.path.join( basepath, 'config', 'topo', topo+".json" ))
        topo_file = open(topo_filename, 'r')
        topo_data = json.load(topo_file)
        iphostmap = {}
        for host in topo_data['hosts']:
            for interface_name, interface in host['interfaces'].iteritems():
                if 'ipv4' in interface:
                    iphostmap[interface['ipv4']] = host['name']
                if 'ipv6' in interface:
                    iphostmap[interface['ipv6']] = host['name']
        return iphostmap

    @staticmethod
    def getIPsForHost( ip_host_map, host_wanted ):
      ips = []
      for ip, host in ip_host_map.iteritems():
        if host_wanted == host:
          ips.append(ip)
      return ips

    @staticmethod
    def expectline( p, command ):
        p.sendline( command )
        p.expect( [pexpect.TIMEOUT, Oftutils.prompt], timeout=60 )
	return p.before.split( '\n' )

    @staticmethod
    def configureNetwork( p, topo, basepath ):
        print >> sys.stderr, "Setting up "+topo+" network topology"

        # vconfig commands
        vconfig_filename = os.path.normpath(os.path.join( basepath, 'config', 'vconfig', topo + ".json" ))
        if os.path.isfile(vconfig_filename):
            json_vconfig_data = open(vconfig_filename)
            vconfig_commands = json.load(json_vconfig_data)
            for cmd in vconfig_commands:
                command =  cmd['host'] + " vconfig add " + cmd['interface'] + " " + cmd['vlan']
                #print >> sys.stderr, command
                Oftutils.expectline( p, command )

        # ifconfig commands
        ifconfig_filename = os.path.normpath(os.path.join( basepath, 'config', 'ifconfig', topo + ".json" ))
	if os.path.isfile(ifconfig_filename):
            json_ifconfig_data = open(ifconfig_filename)
            ifconfig_commands = json.load(json_ifconfig_data)
            for cmd in ifconfig_commands:
	        command =  cmd['host'] + " ifconfig " + cmd['interface'] + " " + cmd['action'] + " " + cmd['address_netmask'] + " up"
                #print >> sys.stderr, command
	        Oftutils.expectline( p, command )

        # route commands
        route_filename = os.path.normpath(os.path.join( basepath, 'config', 'route', topo + ".json" ))
        if os.path.isfile(route_filename):
            json_route_data = open(os.path.normpath(os.path.join( basepath, 'config', 'route', topo + ".json" )))
	    route_commands = json.load(json_route_data)
            for cmd in route_commands:
                command =  cmd['host'] + " route -A " + cmd['family'] + " " + cmd['action'] + " " + cmd['address'] + " dev " + cmd['interface']
                #print >> sys.stderr, command
                Oftutils.expectline( p, command )

	# initial dpctl commands
	init_file = os.path.normpath(os.path.join( basepath, 'dpctl', topo, 'init.json' ))
	if os.path.isfile(init_file):
	    json_data = open( init_file )
            ofcommands = json.load(json_data)
            for ofcommand in ofcommands:
                Oftutils.applyDpctl(p, ofcommand['switch'], ofcommand['command_type'], 'add', ofcommand['arguments'])
        
    @staticmethod
    def getMultipleIfconfigs( p, switch, interfaces ):
        results = ""
        for interface in interfaces:
            Oftutils.expectline( p, switch + ' ifconfig ' + interface )
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
            Oftutils.expectline( p, switch + ' ifconfig ' + interface )
            regex = re.compile('RX bytes.*')
            bytes_in_out = regex.findall( p.before )
            results += interface + ": " + bytes_in_out[ 0 ] + "\n"
        results += "\n"
	return results

    @staticmethod
    def doPing( p, source, dest, args='', count=10 ):
      return Oftutils.doPingGeneric( p, 'ping', source, dest, count, args )

    @staticmethod
    def doPing6( p, source, dest, args='', count=10 ):
      return Oftutils.doPingGeneric( p, 'ping6', source, dest, count, args )

    @staticmethod
    def doPingGeneric( p, ping_type, source, dest, count, args='' ):
        command = source + " " + ping_type + " -c " + str(count) + " " + args + " " + dest
        lines = Oftutils.expectline( p, command )
        results = Ping()
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
    def applyDpctl( p, switch, command_type, action, args ):
      command = switch + " dpctl unix:/tmp/" + switch + " " + command_type + " cmd=" + action + "," + args
      print >> sys.stderr, "COMMAND: " + command 
      p.sendline( command )
      p.expect( Oftutils.prompt )

    @staticmethod
    def doDpctl( p, switch, ofcommand, args ):
      command = switch + " dpctl unix:/tmp/" + switch + " " + ofcommand + " " + args
      command = command.strip()
      print >> sys.stderr, "COMMAND: " + command
      p.sendline( command )
      p.expect( Oftutils.prompt )
    
    @staticmethod
    def getNewTempFile( directory, file_prefix="" ):
      filename = os.path.normpath(os.path.join(directory, file_prefix+uuid.uuid4().hex))
      while os.path.isfile(filename):
        filename = os.path.normpath(os.path.join(directory, file_prefix+uuid.uuid4().hex))
      return filename
   
    @staticmethod
    def getIperfTempDir(subdir = "", project="ofsoftswitch13-testing"):
      directory = os.path.join( os.path.sep, "tmp", project,  "iperf" ) 
      if ( subdir != "" ):
        directory = os.path.join( directory, subdir )
      if not os.path.exists(directory):
        os.makedirs(directory)
        os.chown(directory,1001,1001)
      return directory

    @staticmethod 
    def doIperf3( p, host, connect_to, temp_subdir="", args="", time=10, port=5001 ):
      directory = Oftutils.getIperfTempDir(temp_subdir)
      filename = Oftutils.getNewTempFile( directory, host+"_client_" )
      command = host + " iperf3 -f m -i 0 -J -c " + connect_to + " -p " + str(port) + " -t " + str(time) + " " + args + " | tail -n +2 | sed '/^\[/d' | sed 's/-nan/0/g' > " + filename
      #print >> sys.stderr, "IPERF-C: "+command
      lines = Oftutils.expectline( p, command )
      return filename

    @staticmethod
    def doIperf3Debug( p, host, connect_to, args="", port=5001 ):
      command = host + " iperf3 -f m -i 0 -t 10 -J -c " + connect_to + " -p " + str(port) + " " + args
      command = command.strip()
      lines = Oftutils.expectline( p, command )
      for line in lines:
        print line
      
    @staticmethod
    def doIperf3Server( p, host, temp_subdir, args="", port=5001 ):
      print >> sys.stderr, "Starting iperf3 server on host " + host + " on port " + str(port)
      directory = Oftutils.getIperfTempDir(temp_subdir)
      filename = Oftutils.getNewTempFile( directory, host+"_server_" )
      command = host + " iperf3 -s -J -p " + str(port) + " " + args + " | sed 's/-nan/0/g' > " + filename + " &"
      pid_match = "iperf3 -s -J -p " + str(port)
      command = command.strip()
      #print >> sys.stderr, "IPERF-S: "+command
      lines = Oftutils.expectline( p, command )
      pid = Oftutils.getPid( p, host, pid_match )
      return { "filename":filename, "pid":pid }

    @staticmethod
    def doIperf( p, host, dests_list, dests_map, temp_subdir, args="", time=10, port=5001 ):
      filenames = {}
      dests = dests_list.split(' ')
      num_dests = len(dests)
      dest_num = 0
      for dest in dests:
        directory = Oftutils.getIperfTempDir(temp_subdir)
        dest_num = dest_num + 1
        dest_name = dest
        if dest in dests_map:
          dest_name = dests_map[dest]
        filenames[dest_name] = Oftutils.getNewTempFile( directory, host+"_client_" )
        command = host + " iperf -f m -i 20 -c " + dest + " -p " + str(port) + " -t " + str(time) + " " + args + " > " + filenames[dest_name] + " &"
        #print >> sys.stderr, "IPERF-C: "+command
        lines = Oftutils.expectline( p, command )
      sleep(time+5)
      return filenames

    @staticmethod
    def doIperfServer( p, host, test, temp_subdir, args="", port=5001 ):
      if len(test['ipv6']) > 0:
        port_type = "IPv6"
      else:
        port_type = "IPv4"
      if len(test['udp']) > 0:
        port_type = port_type + " UDP"
      else:
        port_type = port_type + " TCP"
      if len(test['mcast_grp']) > 0:
        port_type = port_type + " Multicast"
      else:
        port_type = port_type + " Unicast"
      print >> sys.stderr, "Starting iperf server on host " + host + " on " + port_type + " port " + str(port)
      directory = Oftutils.getIperfTempDir(temp_subdir)
      filename = Oftutils.getNewTempFile( directory, host+"_server_" )
      command = host + " iperf -f m -i 20 "+test['ipv6']+" -s "+test['udp']+" "+test['mcast_grp']+" -p "+str(port)+" "+args+" > "+filename+" &"
      #print >> sys.stderr, "IPERF-S: "+command
      lines = Oftutils.expectline( p, command )
      pid = Oftutils.getPid( p, host, filename )
      return { "filename":filename, "pid":pid }

    @staticmethod
    def killProcess( p, host, pid ):
      command = host + " kill -9 " + pid
      Oftutils.expectline( p, command )

    @staticmethod
    def killProcessType( p, host, process_type ):
      command = host + " killall -9 " + process_type
      Oftutils.expectline( p, command )

    @staticmethod
    def getIperfResults( client_filenames, server_filenames, ip_host_map, udp = "", result_types = ["bandwidth", "throughput", "cpu_usage"] ):
      client_packets_list = {}
      for server_ip, client_filename in client_filenames.iteritems():
        with open(client_filename, 'r') as client_fh:
          try:
            for line in client_fh:
              if re.search("Sent", line):
                values = re.findall(r"[\d\.]+", line)
                client_packets_list[server_ip] = int(values[1])
                break
            client_fh.close()
          except:
            print >> sys.stderr, "Could not fully process iperf client file: "+client_filename
      if udp == '-u':
        resultset = { 'bandwidth':[], 'throughput':{ 'megabytes':[], 'packets':[], 'lost_packets':[], 'jitter':[] }}
      else:
        resultset = { 'bandwidth':[], 'throughput':{ 'megabytes':[], 'packets':[], 'lost_packets':[], 'retransmits':[] }}
      for server_name, server_filename in server_filenames.iteritems():
        with open(server_filename, 'r') as server_fh:
          print >> sys.stderr, "Scanning iperf server file for "+server_name+": "+server_filename
          try:
            #print >> sys.stderr, "Getting server IPs for "+server_name
            server_ips = Oftutils.getIPsForHost(ip_host_map, server_name)
            client_packets = 0
            for server_ip in server_ips:
              if server_ip in client_packets_list:
                client_packets = client_packets_list[server_ip]
            matched_line = 0
            for line in server_fh:
              if re.search("Mbits/sec", line):
                matched_line = 1
                values = re.findall(r"[\d\.]+", line)
                #print >> sys.stderr, line
                #print.pprint(values)
                resultset['bandwidth'].append(float(values[4]))
                if udp == '-u':
                  resultset['throughput']['megabytes'].append(float(values[3]))
                  resultset['throughput']['packets'].append(int(values[7]))
                  resultset['throughput']['lost_packets'].append(int(values[6]))
                  resultset['throughput']['jitter'].append(float(values[5]))
                else:
                  resultset['throughput']['megabytes'].append(float(values[3]))
                  resultset['throughput']['packets'].append(int(values[7]))
                  resultset['throughput']['lost_packets'].append(int(values[6]))
                  resultset['throughput']['retransmits'].append(int(values[5]))
                break
            server_fh.close()
            if matched_line == 0: 
              #print >> sys.stderr, "no match"
              resultset['bandwidth'].append(0)
              resultset['throughput']['megabytes'].append(0)
              resultset['throughput']['packets'].append(client_packets)
              resultset['throughput']['lost_packets'].append(client_packets)
              if udp == '-u':
                resultset['throughput']['jitter'].append(0)
              else:
                resultset['throughput']['retransmits'].append(client_packets)
          except:
            print >> sys.stderr, "Could not process "+server_filename
	    print >> sys.stderr, '-'*60
            traceback.print_exc(file=sys.stderr)
            print >> sys.stderr, '-'*60
            message = "error - No valid Iperf "+server_name+" server output file generated for this test at " + server_filename
            return {'error': message}
      results = {'error': ''}
      if 'bandwidth' in result_types:
        results['bandwidth'] = sum(resultset['bandwidth'])
      if 'throughput' in result_types:
        results['throughput'] = {}
	results['throughput']['lost_percent'] = 100
        if sum(resultset['throughput']['packets']) != 0:
          results['throughput']['lost_percent'] = 100 * sum(resultset['throughput']['lost_packets']) / sum(resultset['throughput']['packets'])
        if udp == '-u':
          results['throughput']['jitter'] = 0
          if len(resultset['throughput']['jitter']) > 0:
            results['throughput']['jitter'] = sum(resultset['throughput']['jitter']) / len(resultset['throughput']['jitter'])
        else:
          results['throughput']['retransmits'] = sum(resultset['throughput']['retransmits'])
      if 'cpu_usage' in result_types:
        results['cpu_usage'] = {}
        results['cpu_usage']['host_total'] = 0
        results['cpu_usage']['remote_total'] = 0
      return results      

    @staticmethod
    def getIperf3Results( filename, udp = "", result_types = ["bandwidth", "throughput", "cpu_usage"] ):
      print >> sys.stderr, "Reading file: "+filename
      with open(filename, 'r') as filehandle:
        try:
          jsondata = json.load(filehandle)
        except:
          message = "error - No valid JSON results file generated for this test at " + filename
          print >> sys.stderr, "Could not open file: "+filename
          return {'error': message}
      if 'error' in jsondata:
        return jsondata
      results = {'error': ''}
      if 'bandwidth' in result_types:
        results['bandwidth'] = 0
        if len(jsondata['end']['streams']) < 2:
          if udp == "-u":
            stream = jsondata['end']['streams'][0]['udp']
          else:
            stream = jsondata['end']['streams'][0]['receiver']
        else:
          if udp == "-u": 
            stream = jsondata['end']['sum']
          else:
            stream = jsondata['end']['sum_received']
        pprint.pprint(stream)
        if 'lost_percent' in stream:
          #print >> sys.stderr, "8 * "+str(stream['bytes'])+" * ( 100 - "+str(stream['lost_percent'])+" ) / ( "+str(stream['end'])+" - "+str(stream['start'])+" ) / 100 / 1000000"
          results['bandwidth'] = 8 * stream['bytes'] * ( 100 - stream['lost_percent'] ) / ( stream['end'] - stream['start'] ) / 100 / 1000000
        else:
          results['bandwidth'] = stream['bits_per_second'] / 1000000
      if 'throughput' in result_types:
        results['throughput'] = {}
        if len(jsondata['end']['streams']) < 2:
          if udp == "-u":
            results['throughput']['megabytes'] = jsondata['end']['streams'][0]['udp']['bytes'] / 1000000
            results['throughput']['packets'] = jsondata['end']['streams'][0]['udp']['packets']
            results['throughput']['lost_packets'] = jsondata['end']['streams'][0]['udp']['lost_packets']
            results['throughput']['lost_percent'] = jsondata['end']['streams'][0]['udp']['lost_percent']
            results['throughput']['jitter'] = jsondata['end']['streams'][0]['udp']['jitter_ms']
          else:
            sent_bytes = jsondata['end']['streams'][0]['sender']['bytes']
            results['throughput']['megabytes'] = jsondata['end']['streams'][0]['sender']['bytes'] / 1000000
            received_bytes = jsondata['end']['streams'][0]['receiver']['bytes']
            if 'retransmits' in jsondata['end']['streams'][0]['sender']:
              results['throughput']['retransmits'] = jsondata['end']['streams'][0]['sender']['retransmits'] 
        else:
          if udp == "-u":
            results['throughput']['megabytes'] = jsondata['end']['sum']['bytes'] / 1000000
            results['throughput']['packets'] = jsondata['end']['sum']['packets']
            results['throughput']['lost_packets'] = jsondata['end']['sum']['lost_packets']
            results['throughput']['lost_percent'] = jsondata['end']['sum']['lost_percent']
            results['throughput']['jitter'] = jsondata['end']['sum']['jitter_ms']
          else:
            sent_bytes = jsondata['end']['sum_sent']['bytes']
            results['throughput']['megabytes'] = jsondata['end']['sum_sent']['bytes'] / 1000000
            received_bytes = jsondata['end']['sum_received']['bytes'] / 1000000	
            if 'retransmits' in jsondata['end']['sum_sent']:
              results['throughput']['retransmits'] = jsondata['end']['sum_sent']['retransmits']
        if udp == "":
          results['throughput']['lost_megabytes'] = ( sent_bytes - received_bytes ) / 1000000
          results['throughput']['lost_percent'] = ( sent_bytes - received_bytes ) / sent_bytes * 100
      if 'cpu_usage' in result_types:
        results['cpu_usage'] = jsondata['end']['cpu_utilization_percent']
      return results

    @staticmethod
    def printResults(output_type, output_destination, test, udp, results):
      if 'bandwidth' not in results:
        results['bandwidth'] = 0
        results['throughput'] = {}
        results['throughput']['lost_percent'] = 0;
        if udp == '-u':
          results['throughput']['jitter'] = 0
	else:
          results['throughput']['retransmits'] = 0
	results['cpu_usage'] = {}
	results['cpu_usage']['host_total'] = 0
        results['cpu_usage']['remote_total'] = 0 
      if output_type == "human":
         Oftutils.printResultsHumanReadable(test, results, output_destination)
      else:
         Oftutils.printResultsMachineReadable(test, results, output_destination)

    @staticmethod
    def printResultsHumanReadable(test, results, output_destination):
      print >> output_destination, "Tested: " + test
      print >> output_destination, "  Data rate: " + str(results['bandwidth']) + "Mb/s"
      print >> output_destination, "  Data lost: " + str(results['throughput']['lost_percent']) + "%"
      if 'retransmits' in results['throughput']:
          print >> output_destination, "  Data restransmits: " + str(results['throughput']['retransmits'])
      else:
          print >> output_destination, "  Data jitter: " + str(results['throughput']['jitter']) + "ms" 
      print >> output_destination, "  Host total CPU usage: " + str(results['cpu_usage']['host_total']) + "%"
      print >> output_destination, "  Remote total CPU usage: " + str(results['cpu_usage']['remote_total']) + "%"

    @staticmethod
    def printResultsMachineReadable(test, results, output_destination):
      if 'retransmits' in results['throughput']:
        print >> output_destination, '"' + test + '",' + str(results['bandwidth']) + ',' + str(results['throughput']['lost_percent']) + ',' + str(results['throughput']['retransmits']) + ',' + str(results['cpu_usage']['host_total']) + ',' + str(results['cpu_usage']['remote_total'])
      else:
        print >> output_destination, '"' + test + '",' + str(results['bandwidth']) + ',' + str(results['throughput']['lost_percent']) + ',' + str(results['throughput']['jitter']) + ',' + str(results['cpu_usage']['host_total']) + ',' + str(results['cpu_usage']['remote_total'])

    @staticmethod
    def runTestSet(p, tests, tester, ip_host_map, output_destination, set_name="Baseline"):
      if tester.output_type == "human":
        print >> output_destination, set_name
      else:
        print >> output_destination, "\"" + set_name + "\""
      for test in tests:
        temp_subdir = os.path.join(tester.topology, tester.test_name, re.sub(r"[\W]", "_", set_name).lower(), re.sub(r"[\W]", "_", test['name']).lower())
        print >> sys.stderr, "Testing: "+ test['name']
	arguments = test['arguments'].split(' ')
        test['ipv6'] = ""
        test['udp'] = ""
        test['mcast_grp'] = ""
        if '-V' in arguments:
          test['ipv6'] = "-V"
	if '-u' in arguments:
          test['udp'] = "-u"
	if 'multicast' in test.keys() and test['multicast'] == "yes":
          test['mcast_grp'] = "-B "+test['destination']
	iperf_servers = tester.iperf_server.split(' ')
	iperf_pids = {}
	if (tester.iperf_type == "iperf"):
          server_filenames = {}
          for iperf_server in iperf_servers:
            iperf_server_info = Oftutils.doIperfServer( p, iperf_server, test, temp_subdir )
            iperf_pids[iperf_server] = iperf_server_info['pid']
            server_filenames[iperf_server] = iperf_server_info['filename']
          client_filenames = Oftutils.doIperf(p, test['host'], test['destination'], ip_host_map, temp_subdir, test['arguments'])
          sleep(5)
          Oftutils.killProcessType( p, iperf_servers[0], tester.iperf_type )
          sleep(5)
	  results = Oftutils.getIperfResults(client_filenames, server_filenames, ip_host_map, test['udp'])
        else:
          server_filenames = {}
          tester.iperf_type = "iperf3"
          for iperf_server in iperf_servers:
            iperf_server_info = Oftutils.doIperf3Server( p, iperf_server, temp_subdir )
            iperf_pids[iperf_server] = iperf_server_info['pid']
            server_filenames[iperf_server] = iperf_server_info['filename']
          filename = Oftutils.doIperf3(p, test['host'], test['destination'], temp_subdir, test['arguments'])
          sleep(5)
          Oftutils.killProcessType( p, iperf_servers[0], tester.iperf_type )
          sleep(5)
	  results = Oftutils.getIperf3Results(server_filenames[iperf_servers[0]], test['udp'])
	if results['error'] != "":
	  print >> sys.stderr, "WARNING: No iperf data generated.  This may be intentional for this particular test or it may be an error."	
	Oftutils.printResults(tester.output_type, output_destination, test['name'], test['udp'], results) 

    @staticmethod
    def runTestSets(p, tests, ofcommands_list, tester, results_directory = "/tmp/"):
      ip_host_map = Oftutils.getTopologyIPHostMap( tester.basepath, tester.topology )
      #pprint.pprint(ip_host_map)
      if tester.output_destination != "sys.stdout":
        if not os.path.exists(results_directory):
          os.makedirs(results_directory)        
        output_destination = open(results_directory + "/" + uuid.uuid4().hex + ".csv" , 'w')
      else:
        output_destination = tester.output_destination
      Oftutils.runTestSet( p, tests, tester, ip_host_map, output_destination )
      last_ofcommands = {}
      for ofcommands in ofcommands_list:
        if len(last_ofcommands) > 0 and len(last_ofcommands['commands']) > 0:
          print >> sys.stderr, "Removing OpenFlow commands for: " + last_ofcommands['name']
          for ofcommand in last_ofcommands['commands']:
            Oftutils.applyDpctl(p, ofcommand['switch'], ofcommand['command_type'], 'del', ofcommand['arguments'])
        print >> sys.stderr, "Applying OpenFlow commands for: " + ofcommands['name']
        for ofcommand in ofcommands['commands']:
          Oftutils.applyDpctl(p, ofcommand['switch'], ofcommand['command_type'], 'add', ofcommand['arguments'])
        print >> sys.stderr, "Sleeping for " + str(Oftutils.rule_change_sleep) + " seconds to ensure OpenFlow commands have been applied."
        sleep(Oftutils.rule_change_sleep)
        Oftutils.runTestSet( p, tests, tester, ip_host_map, output_destination, ofcommands['name'] )
        last_ofcommands = ofcommands
  
 
    @staticmethod
    def getPid( p, host, cmdline ):
      command = host + " ps aux | grep \"" + cmdline + "\" | grep -v grep | tail -n 1 | awk 'BEGIN{FS=\"[\t ]+\"}{print $2}'" 
      lines = Oftutils.expectline( p, command )
      return lines[-2]

    @staticmethod 
    def finished( p ):
       print >> sys.stderr, "Finished with Mininet shell"
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

