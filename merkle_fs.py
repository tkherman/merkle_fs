from __future__ import print_function
import sys

from put import PUT
from mkdir import MKDIR
from ls import LS
from get import GET
from cp import CP
from rm import RM
from mv import MV

def usage():
	usg_msg = """
	Invalid arguments
	usage: merkle_fs [OPERATION]
	The Command can be one of the following:
		PUT     fs src_path dest_path
		GET     fs src_path dest_path [version cksum]
		CP      fs src_path dest_path
		MKDIR   fs path
		LS      fs path
		RM      fs path
		MV      fs src_path dest_path
    """
	print(usg_msg)
	exit(1)


def parseArgs():
	if len(sys.argv) < 2:
		usage()
	if sys.argv[1] == 'PUT' and len(sys.argv) == 5:
		print(PUT(sys.argv[2], sys.argv[3], sys.argv[4]))
	elif sys.argv[1] == 'MKDIR' and len(sys.argv) == 4:
		print(MKDIR(sys.argv[2], sys.argv[3]))
	elif sys.argv[1] == 'LS' and len(sys.argv) == 4:
		LS(sys.argv[2], sys.argv[3])
	elif sys.argv[1] == 'LS' and len(sys.argv) == 5:
		LS(sys.argv[2], sys.argv[3], sys.argv[4])
	elif sys.argv[1] == 'GET' and len(sys.argv) == 5:
		GET(sys.argv[2], sys.argv[3], sys.argv[4])
	elif sys.argv[1] == 'GET' and len(sys.argv) == 6:
		GET(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
	elif sys.argv[1] == 'CP' and len(sys.argv) == 5:
		print(CP(sys.argv[2], sys.argv[3], sys.argv[4]))
	elif sys.argv[1] == 'RM' and len(sys.argv) == 4:
		print(RM(sys.argv[2], sys.argv[3]))
	elif sys.argv[1] == 'MV' and len(sys.argv) == 5:
		print(MV(sys.argv[2], sys.argv[3], sys.argv[4]))
	else:
		usage()

if __name__ == '__main__':
	parseArgs()
