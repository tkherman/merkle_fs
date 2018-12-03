from __future__ import print_function
import boto3
import hashlib
import datetime
import os.path
import getpass

from MerkleNode import *

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
s3 = boto3.resource('s3')

def PUT(fs, src_filepath, dest_filepath):
	if not os.path.isfile(src_filepath):
		return "{} is not a local file".format(src_filepath)

	# Fetch root node for fs
	success, msg = fetch_fs_root_node(fs)
	if success:
		s3_bucket, root_cksum = msg
	else:
		print('Error: {}'.format(msg))
		return("unsuccessful")

	# Get node of directory the file is to be placed in
	nodes_traversed = []
	root_node = fetch_node(fs, root_cksum)
	dest_filepath_list = dest_filepath.lstrip('/').split('/')
	if len(dest_filepath_list) > 1:
		dirpath = dest_filepath_list[:-1]
		nodes_traversed, dir_node = get_merkle_node_by_name(fs, root_node, dirpath, nodes_traversed)
	else:
		dir_node = root_node
		nodes_traversed.append(root_node)

	# Create MerkleNode object for new node
	newNode = MerkleNode()
	newNode.cksum = calculate_cksum(src_filepath, dest_filepath)
	newNode.name = dest_filepath_list[-1]
	newNode.is_dir = False
	newNode.dir_info = None
	newNode.mod_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
	newNode.mod_user = getpass.getuser()

	# Insert to DB
	curr_cksum = insert_new_node_bubble_up(fs, newNode, nodes_traversed)

	# Place actual file to S3 with name==cksum
	s3.meta.client.upload_file(src_filepath, s3_bucket, newNode.cksum)

	update_root_pointers_table(fs, curr_cksum)

	return "successful"
