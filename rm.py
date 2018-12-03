from __future__ import print_function
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
s3 = boto3.resource('s3')

from MerkleNode import *

def RM(fs, path):
	if path == "/":
		print("Cannot remove root directory")
		return "unsuccessful"

	# Fetch root node for fs
	success, msg = fetch_fs_root_node(fs)
	if success:
		s3_bucket, root_cksum = msg
	else:
		print('Error: {}'.format(msg))
		return "unsuccessful"

	# Get node of directory the file/subdirectory is in
	nodes_traversed = []
	root_node = fetch_node(fs, root_cksum)
	path_list = path.lstrip('/').split('/')
	if len(path_list) > 1:
		dirpath = path_list[:-1]
		nodes_traversed, dir_node = get_merkle_node_by_name(fs, root_node, dirpath, nodes_traversed)
	else:
		dir_node = root_node
		nodes_traversed.append(root_node)

	if not dir_node:
		print("Error: {} cannot be found".format(path))
		return "unsuccessful"


	# Create new MerkleNode for the dir_node
	newNode = MerkleNode()
	newNode.name = dir_node.name
	newNode.is_dir = dir_node.is_dir
	newNode.mod_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
	newNode.mod_user = getpass.getuser()

	# Remove file/directory to be deleted from dir_info
	dir_info = dir_node.dir_info
	index_to_remove = 0
	for i in range(1, len(dir_info)):
		sub_f = dir_info[i]
		if sub_f[0] == path_list[-1]: # found file
			index_to_remove = i
			break


	if not index_to_remove: # the file couldn't be found so no action further
		print("Error: {} cannot be found".format(path))
		return "unsuccessful"

	del dir_info[index_to_remove]

	# Update dir_info and cksum
	newNode.dir_info = dir_info
	newNode.cksum = calculate_dir_cksum(dir_info)


	# Insert to DB
	curr_cksum = insert_new_node_bubble_up(fs, newNode, nodes_traversed[:-1])

	update_root_pointers_table(fs, curr_cksum)
