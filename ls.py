from __future__ import print_function
import boto3
import hashlib

from MerkleNode import MerkleNode, fetch_node, get_merkle_node_by_name, fetch_fs_root_node

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
s3 = boto3.resource('s3')

def format_node_info(node):
	is_dir = None
	if node.is_dir:
		is_dir = "d"
	else:
		is_dir = "-"

	node_info = "{} {:<12} {:<16} {:<20}".format(is_dir, node.mod_user, node.mod_time.replace('T', ' '), node.name)
	return node_info

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
	if dir_path == "/":
		node = root_node
	else:
		dir_path_list = dir_path.rstrip().lstrip('/').split('/')
		_,node = get_merkle_node_by_name(fs, root_node, dir_path_list, list())

	if node == None:
		print("{} doesn't exist".format(dir_path))

	# If the node is a file, list the file
	if not node.is_dir:
		print(format_node_info(node))
		return
	# else, list info on a files/subdirectories within the directory
	else:
		dir_info = node.dir_info[1:] # first element is just the path name to directory
		for info_pair in dir_info:
			child_node = fetch_node(fs, info_pair[1])
			print(format_node_info(child_node))
