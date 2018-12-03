from __future__ import print_function
import boto3
import hashlib
import datetime
import getpass

from MerkleNode import *

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
s3 = boto3.resource('s3')

def MKDIR(fs, new_dirpath):
	# Fetch root node for fs
	success, msg = fetch_fs_root_node(fs)
	if success:
		s3_bucket, root_cksum = msg
	else:
		print("Error: {}".format(msg))
		return "unsuccessful"

	# Get node of directory the new directory is to be placed in
	nodes_traversed = []
	root_node = fetch_node(fs, root_cksum)
	dirpath_list = new_dirpath.strip().lstrip('/').split('/')
	if len(dirpath_list) > 1:
		dirlist = dirpath_list[:-1]
		nodes_traversed,dir_node = get_merkle_node_by_name(fs, root_node, dirlist, nodes_traversed)
	else:
		dir_node = root_node
		nodes_traversed.append(root_node)

	print(nodes_traversed)

	# Check if directory already exists
	for sub_f in dir_node.dir_info[1:]:
		if sub_f[0] == dirpath_list[-1]:
			print("Error: directory already exists")
			return("unsuccessful")

	# Create MerkleNode object for new directory node
	newNode = MerkleNode()
	newNode.cksum = calculate_dir_cksum(dirpath_list)
	newNode.name = dirpath_list[-1]
	newNode.is_dir = True
	newNode.dir_info = [new_dirpath]
	newNode.mod_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
	newNode.mod_user = getpass.getuser()


	curr_cksum = insert_new_node_bubble_up(fs, newNode, nodes_traversed)
	update_root_pointers_table(fs, curr_cksum)

	return "successful"
