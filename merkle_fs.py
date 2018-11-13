from __future__ import print_function
import sys

#TODO
def usage():
	print('usage')
	exit(1)

#TODO
def LS(dirname):
	print('LS on {}'.format(dirname))

#TODO
def GET(fname):
	print('GET {}'.format(fname))

#TODO
def RM(fname):
	print('RM {}'.format(fname))

#TODO
def MKDIR(dirname):
	print('MKDIR {}'.format(dirname))

#TODO
def RMDIR(dirname):
	print('RMDIR {}'.format(dirname))

#TODO
def PUT(local_fname, mfs_f_loc):
	print('PUT {} from local to {} on mfs'.format(local_fname, mfs_f_loc))

#TODO
def MV(source, dest):
	print('MV {} to {} on mfs'.format(source, dest))

#TODO
def CP(source, dest):
	print('CP {} to {} on mfs'.format(source, dest))

def parseArgs():
	if len(sys.argv) < 3:
		usage()
	if sys.argv[1] == 'LS':
		LS(sys.argv[2])
	elif sys.argv[1] == 'GET':
		GET(sys.argv[2])
	elif sys.argv[1] == 'RM':
		RM(sys.argv[2])
	elif sys.argv[1] == 'MKDIR':
		MKDIR(sys.argv[2])
	elif sys.argv[1] == 'RMDIR':
		RMDIR(sys.argv[2])
	elif len(sys.argv) > 3:
		if sys.argv[1] == 'PUT':
			PUT(sys.argv[2], sys.argv[3])
		elif sys.argv[1] == 'MV':
			MV(sys.argv[2], sys.argv[3])
		elif sys.argv[1] == 'CP':
			CP(sys.argv[2], sys.argv[3])
		else:
			usage()
	else:
		usage()

if __name__ == '__main__':
	parseArgs()
