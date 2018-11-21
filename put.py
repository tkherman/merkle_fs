from __future__ import print_function
import boto3
import hashlib
import datetime
import os.path
import getpass

from MerkleNode import MerkleNode, fetch_node, get_merkle_node_by_name, insert_node, calculate_dir_cksum, fetch_fs_root_node
from utilities import *

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
		exit(1)

	# Get node of directory the file is to be placed in
	nodes_traversed = []
	root_node = fetch_node(fs, root_cksum)
	dest_filepath = dest_filepath.lstrip('/').split('/')
	if len(dest_filepath) > 1:
		dirpath = dest_filepath[:-1]
		dir_node = get_merkle_node_by_name(fs, root_node, dirpath, nodes_traversed)
	else:
		dir_node = root_node
		nodes_traversed.append(root_node)

	# Check if file already exist
	original_fnode = None
	for sub_f in dir_node.dir_info[1:]:
		if sub_f[0] == dest_filepath[-1]:
			original_fnode = fetch_node(fs, sub_f[1])

	# Create MerkleNode object for new node
	newNode = MerkleNode()
	newNode.cksum = calculate_cksum(src_filepath)
	newNode.name = dest_filepath[-1]
	newNode.is_dir = False
	newNode.dir_info = None
	newNode.mod_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
	newNode.mod_user = getpass.getuser()

	if not insert_node(fs, newNode):
		return "Failed to update DB"

	# Place actual file to S3 with name==cksum
	s3.meta.client.upload_file(src_filepath, s3_bucket, newNode.cksum)

	# Bubble up and create new node for all ancestors
	curr_fname = newNode.name
	curr_cksum = newNode.cksum
	for ancestor_node in reversed(nodes_traversed):
		new_aNode = MerkleNode()
		new_aNode.name = ancestor_node.name
		new_aNode.is_dir = ancestor_node.is_dir

		# Generate new dir_info
		new_dir_info = ancestor_node.dir_info
		existing_node_found = False
		if not len(new_dir_info) == 1: # there are sub files/directories inside
			for sub_f in new_dir_info:
				if sub_f[0] == curr_fname:
					sub_f[1] = curr_cksum
					existing_node_found = True
					break
		if not existing_node_found:
			new_dir_info.append([curr_fname, curr_cksum])
		new_aNode.dir_info = new_dir_info
		new_aNode.cksum = calculate_dir_cksum(new_dir_info)
		new_aNode.mod_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
		new_aNode.mod_user = getpass.getuser()

		new_aNode.print_info()
		insert_node(fs, new_aNode)

		curr_fname = new_aNode.name
		curr_cksum = new_aNode.cksum

	# curr_fname and curr_cksum should contain root / cksum,
	# Update root_pointers table
	root_pointers_table = dynamodb.Table('root_pointers')
	response = root_pointers_table.update_item(
		Key={
			'name': fs
		},
		UpdateExpression='SET root_cksums = list_append(root_cksums, :i)',
		ExpressionAttributeValues={
			':i': [curr_cksum]
		},
	)

	return "successful"


print(PUT("dev", "go_irish.txt", "/goirish5.txt"))
