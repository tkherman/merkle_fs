from __future__ import print_function
from datetime import datetime
import time
import sys

from put import PUT
from mkdir import MKDIR
from ls import LS
from get import GET
from cp import CP
from rm import RM
from mv import MV

fs = 'benchmark'
m_logfile = '.benchmark_results/m_benchmark_log.csv'
p_logfile = '.benchmark_results/p_benchmark_log.csv'
g_logfile = '.benchmark_results/g_benchmark_log.csv'
file_to_put = 'LICENSE' 
get_path = '/tmp/lcns'
get_path1 = '/tmp/lcns1'
dirname = '/test'
test_incs = 5
max_depth = 51

def formatTimeDelta(t1, t2):
	delta = t2 - t1
	time = delta.seconds + 1.*delta.microseconds/1e6
	return time



# loop to create nested directory structure
# -test
#	-test
#	  -test
# ...
mf = open(m_logfile, 'w+')
pf = open(p_logfile, 'w+')
gf = open(g_logfile, 'w+')
curr_dirpath = dirname
for k in range(max_depth):
	# time mkdir
	start = datetime.now()
	MKDIR(fs, curr_dirpath)
	end = datetime.now()
	time_res = formatTimeDelta(start, end)
	mf.write("{}, {}\n".format(k, time_res))
	
	if not k % test_incs:
		# time put
		start = datetime.now()
		put_loc = '{}/{}'.format(curr_dirpath, file_to_put) 
		PUT(fs, file_to_put, put_loc)
		end = datetime.now()
		time_res = formatTimeDelta(start, end)
		pf.write("{}, {}\n".format(k, time_res))
		
		# untimed GET to load into cache
		GET(fs, put_loc, get_path) 
		
		# time get
		start = datetime.now()
		GET(fs, put_loc, get_path) 
		end = datetime.now()
		time_res = formatTimeDelta(start, end)
		gf.write("{}, {}\n".format(k, time_res))

	print(k)
	curr_dirpath += dirname
