from __future__ import print_function
import boto3
import hashlib
import datetime
import getpass

from MerkleNode import MerkleNode, fetch_node, get_merkle_node_by_name, insert_node, calculate_dir_cksum, fetch_fs_root_node, bubble_up

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
		dirlist = dirpath_list[1:]
		dir_node = get_merkle_node_by_name(fs, root_node, dirlist, nodes_traversed)
	else:
		dir_node = root_node
		nodes_traversed.append(root_node)

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

	# Insert to DB
	if not insert_node(fs, newNode):
		return "Failed to update DB"

	# Bubble up and create new nodes for all ancestors
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
