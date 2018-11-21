from __future__ import print_function
import boto3
import hashlib

from MerkleNode import MerkleNode, fetch_node, get_merkle_node_by_name, fetch_fs_root_node

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
s3 = boto3.resource('s3')

def LS(fs, dir_path):
	# fetch fs root node
	success, msg = fetch_fs_root_node(fs)
	if success:
		s3_bucket, root_cksum = msg
	else:
		print('Error: {}'.format(msg))
		exit(1)
	
	#find dir/file to be listed
	root_node = fetch_node(fs, root_cksum)
	dir_path = dir_path.rstrip().lstrip('/').split('/')
	if len(dir_path) > 1:
		dir_node = get_merkle_node_by_name(fs, root_node, dir_path)
	else:
		dir_node = root_node
	
	#return files in directory
	if dir_node.is_dir:
		return dir_node.dir_info
	return dir_node.name

if __name__=='__main__':
	result = LS('dev2', '/test_dir1')
	names = [info[0] for info in result[1:]]
	print(names)
