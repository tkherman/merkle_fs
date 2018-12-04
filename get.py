from __future__ import print_function
from botocore.exceptions import ClientError
from shutil import copyfile
import boto3
import os
import tempfile

from MerkleNode import MerkleNode, fetch_node, get_merkle_node_by_name

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
s3 = boto3.resource('s3')

def GET(fs, src_path, dest_path):
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
	root_cksum = response['Item']['root_cksums'][-1]

	# Locate node corresponding to file
	root_node = fetch_node(fs, root_cksum)
	visited_nodes = []
	_,file_node = get_merkle_node_by_name(fs, root_node, src_path.lstrip('/').split('/'), visited_nodes)

	if not file_node:
		return "File {} does not exist".format(src_path)

	### Get file from s3 or from cache
	# Check if the file is in cache
	cache_dir = tempfile.gettempdir() + "/merkle_fs_data_blocks"
	if not os.path.isdir(cache_dir):
		try:
			os.mkdir(cache_dir)
		except:
			print("Unable to create cache directory")

	cache_block_path = "{}/{}".format(cache_dir, file_node.cksum)
	if not os.path.exists(cache_block_path):
		s3.meta.client.download_file(s3_bucket, file_node.cksum, cache_block_path)

	try:
		copyfile(cache_block_path, dest_path)
	except:
		print("Unable to get file from {}".format(cache_dir))

	return "Downloaded {} to {}".format(src_path, dest_path)
