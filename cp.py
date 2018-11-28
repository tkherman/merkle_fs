from __future__ import print_function
import boto3
import datetime
import getpass
import copy as _cp
import sys

from MerkleNode import *

if len(sys.argv) < 2:
	print('must include region (us-east-X) as first argument')
	exit(1)
region = sys.argv[1]
dynamodb = boto3.resource('dynamodb', region_name='us-east-{}'.format(region))
s3 = boto3.resource('s3')

def CP(fs, orig_filepath, dest_filepath):
	if orig_filepath == dest_filepath:
		print("CP: {} and {} are identical (not copied)".format(orig_filepath, dest_filepath))
		return "unsuccessful"

	# Fetch root node for fs
	success, msg = fetch_fs_root_node(fs)
	if success:
		s3_bucket, root_cksum = msg
	else:
		print("Error: {}".format(msg))
		return "unsuccessful"
	root_node = fetch_node(fs, root_cksum)

	# Get node of original file
	orig_filepath_list = orig_filepath.strip().lstrip('/').split('/')
	if not len(orig_filepath_list):
		orig_node = root_node
	else:
		ot = []
		_, orig_node = get_merkle_node_by_name(fs, root_node, orig_filepath_list, ot)

	#TODO - note:	potential optimization would be to store the directory node for the
	#				original file as well because if copying to the same directory this
	#				would save queries to DynamoDB

	# Get node of new directory file is to be placed in
	new_filepath_list = dest_filepath.strip().lstrip('/').split('/')
	nodes_traversed = []
	if not len(new_filepath_list):
		print("Error: cannot overwrite root directory")
		return "unsuccessful"
	dirpath = new_filepath_list[:-1]
	if not len(dirpath):
		dir_node = root_node
		nodes_traversed.append(root_node)
	else:
		nodes_traversed, dir_node = get_merkle_node_by_name(fs, root_node, dirpath, nodes_traversed)
	if not dir_node:
		print("Error finding destination file {}".format(dest_filepath))
		return "unsuccessful"

	# Check if the file already exists
	for sub_f in dir_node.dir_info[1:]:
		if sub_f[0] == new_filepath_list[-1]:
			print(sub_f[0], new_filepath_list[-1])
			print("CP: cannot overwrite files -- please RM before proceeding if this is an intended operation")
			return "unsuccessful"
	
	# Create MerkleNode for copied node 
	newNode = _cp.deepcopy(orig_node)
	newNode.cksum = calculate_newloc_cksum(newNode.cksum, dest_filepath)
	newNode.mod_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
	newNode.mod_user = getpass.getuser()
	newNode.name = new_filepath_list[-1]

	# Insert into DB
	if not insert_node(fs, newNode):
		print("Failed to update DB")
		return "unsuccessful"
	
	# NOTE - do not have to duplicate in S3 because we don't remove anything from S3
	# TODO - if we add garbage collection this behavior might have to change
	copy_source = {
		'Bucket': s3_bucket,
		'Key': orig_node.cksum
	}
	s3.meta.client.copy(copy_source, s3_bucket, newNode.cksum)

	#TODO - figure out issues with bubbling up
	#CONTINUE HERE ###################
	# Bubble up and create new node for all ancestors
	curr_cksum = bubble_up(fs, newNode, nodes_traversed)
	
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

print(CP("dev2", "NEWTEST2", "test_dir1/NEWTEST.txt"))
