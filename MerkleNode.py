from __future__ import print_function
import sys
import boto3
import getpass
import hashlib
import datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

class MerkleNode:
	def __init__(self):
		self.cksum = None
		self.name = None
		self.is_dir = None
		self.dir_info = None
		self.mod_time = None
		self.mod_user = None

	def print_info(self):
		print("cksum:		{}".format(self.cksum))
		print("name:		{}".format(self.name))
		print("is_dir:		{}".format(self.is_dir))
		print("dir_info:	{}".format(self.dir_info))
		print("mod_time:	{}".format(self.mod_time))
		print("mod_user:	{}".format(self.mod_user))

# Return None if cannot fetch node from table
def fetch_node(fs, cksum):
	fs_table = dynamodb.Table(fs)

	try:
		response = fs_table.get_item(
			Key={
				'cksum': cksum
			}
		)
	except ClientError as e:
		return None

	item = response.get('Item')

	if not item:
		return None

	# Create MerkleNode object
	mNode = MerkleNode()
	mNode.cksum = cksum
	mNode.name = item.get('name', None)
	mNode.is_dir = item.get('is_dir', None)
	mNode.dir_info = item.get('dir_info', None)
	mNode.mod_time = item.get('mod_time', None)
	mNode.mod_user = item.get('mod_user', None)


	return mNode


# Insert the new node into DB
def insert_node(fs, mNode):
	fs_table = dynamodb.Table(fs)

	try:
		response = fs_table.put_item(
			Item={
				'cksum': mNode.cksum,
				'name': mNode.name,
				'is_dir': mNode.is_dir,
				'dir_info': mNode.dir_info,
				'mod_time': mNode.mod_time,
				'mod_user': mNode.mod_user
			}
		)
	except ClientError as e:
		return False

	return True

# calculate cksum of new file
def calculate_cksum(src_filepath, dest_filepath):
	hasher = hashlib.sha256()
	hasher.update(dest_filepath)
	hasher.update("********") #TODO - eventually make this a random hash
	with open(src_filepath, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hasher.update(chunk)

	return hasher.hexdigest()

# calculate cksum of copied/moved file
def calculate_newloc_cksum(orig_cksum, dest_filepath):
	hasher = hashlib.sha256()
	hasher.update("{}********{}".format(dest_filepath, orig_cksum))
	return hasher.hexdigest()

# Take dir_info list and return cksum of directory
def calculate_dir_cksum(dir_info):
	hasher = hashlib.sha256()
	hasher.update(dir_info[0])

	if len(dir_info) == 1:
		return hasher.hexdigest()

	for sub_info in dir_info[1:]:
		hasher.update(sub_info[0])
		hasher.update(sub_info[1])

	return hasher.hexdigest()


def get_merkle_node_by_name(fs, curr_node, path_list, nodes_traversed):
	nodes_traversed.append(curr_node)
	
	if not curr_node.is_dir:
		return None

	for sub_f in curr_node.dir_info[1:]:
		if sub_f[0] == path_list[0]:
			if len(path_list) == 1:
				dest_node = fetch_node(fs, sub_f[1])
				nodes_traversed.append(dest_node)
				return nodes_traversed, dest_node
			return get_merkle_node_by_name(fs, fetch_node(fs, sub_f[1]), path_list[1:], nodes_traversed)

	# Incorrect path
	return None

def fetch_fs_root_node(fs):
	root_ptrs_table = dynamodb.Table('root_pointers')
	success = False
	try:
		response = root_ptrs_table.get_item(
			Key={
				'name': fs
			}
		)
		success = True
		if not response.get('Item'):
			retmsg = "Namespace {} does not exist".format(fs)
		else:
			s3_bucket = response['Item']['bucket_name']
			root_cksum = response['Item']['root_cksums'][-1]
			retmsg = (s3_bucket, root_cksum)
	except ClientError as e:
		retmsg = e.response['Error']['Message']

	return success, retmsg
	
# Bubble up and create new node for all ancestors
def bubble_up(fs, newNode, nodes_traversed):
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

		insert_node(fs, new_aNode)

		curr_fname = new_aNode.name
		curr_cksum = new_aNode.cksum
	return curr_cksum
