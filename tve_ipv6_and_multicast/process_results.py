#!/usr/bin/python
import os
import sys
import csv
import pprint
import string
import numpy

basepath = str(os.path.normpath(os.path.dirname(os.path.realpath( __file__ ))))
results_path = os.path.normpath(os.path.join( basepath, 'results', sys.argv[1], sys.argv[2] ))
results_files = [ os.path.join(results_path, f) for f in os.listdir(results_path) if os.path.isfile(os.path.join(results_path,f)) ]
results = {}
for results_file in results_files:
    with open(results_file, 'rb') as file_handle:
        reader = csv.reader(file_handle)
	rows = []
        for row in reader:
            rows.append(row)
        n = 0
        while n < len(rows):
            if len(rows[n]) == 1:
                subset_name = rows[n][0].replace(" ", "_")
                if subset_name not in results:
                   results[subset_name] = {}
                n = n + 1
            while n < len(rows) and len(rows[n]) > 1:
                test_name = rows[n][0].replace(" ", "_")
		if test_name not in results[subset_name]:
                    results[subset_name][test_name] = {}
                if 'bandwidth' not in results[subset_name][test_name]:
                   results[subset_name][test_name]['bandwidth'] = {}
		   results[subset_name][test_name]['bandwidth']['values'] = []
                results[subset_name][test_name]['bandwidth']['values'].append(float(rows[n][1]))
                if 'packet_loss_percentage' not in results[subset_name][test_name]:
                   results[subset_name][test_name]['packet_loss_percentage'] = {}
                   results[subset_name][test_name]['packet_loss_percentage']['values'] = []
                results[subset_name][test_name]['packet_loss_percentage']['values'].append(float(rows[n][2]))
		if 'jitter_retransmits' not in results[subset_name][test_name]:
                   results[subset_name][test_name]['jitter_retransmits'] = {}
                   results[subset_name][test_name]['jitter_retransmits'] ['values'] = []
                results[subset_name][test_name]['jitter_retransmits']['values'].append(float(rows[n][3]))
                if 'cpu_usage_local' not in results[subset_name][test_name]:
                   results[subset_name][test_name]['cpu_usage_local'] = {}
                   results[subset_name][test_name]['cpu_usage_local']['values'] = []
                results[subset_name][test_name]['cpu_usage_local']['values'].append(float(rows[n][4]))
                if 'cpu_usage_remote' not in results[subset_name][test_name]:
                   results[subset_name][test_name]['cpu_usage_remote'] = {}
                   results[subset_name][test_name]['cpu_usage_remote']['values'] = []
                results[subset_name][test_name]['cpu_usage_remote']['values'].append(float(rows[n][5]))
                n = n + 1

for (r, result) in results.items():
    for (t, test) in result.items():
        for (f, field) in test.items():
           results[r][t][f]['average'] = numpy.average(field['values'])
	   results[r][t][f]['std'] = numpy.std(field['values'])
	   results[r][t][f]['max'] = max(field['values'])
           results[r][t][f]['min'] = min(field['values'])

pprint.pprint(results)    
