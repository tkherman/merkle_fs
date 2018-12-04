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

def LS(fs, dir_path, version=None):
	# Fetch root node for fs
	root_ptrs_table = dynamodb.Table('root_pointers')
	try:
		response = root_ptrs_table.get_item(
			Key={
				'name': fs
			}
		)
	except ClientError as e:
		return e.response['Error']['Message']

	if not response.get('Item'):
		return "Namespace {} does not exist".format(fs)

	s3_bucket = response['Item']['bucket_name']
	if version != None:
		if version in response['Item']['root_cksums']:
			root_cksum = version
		else:
			return "Version cksum {} is invalid".format(version)
	else:
		root_cksum = response['Item']['root_cksums'][-1]

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
