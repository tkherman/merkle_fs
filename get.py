from __future__ import print_function
import boto3
from botocore.exceptions import ClientError

from MerkleNode import MerkleNode, fetch_node, get_merkle_node_by_name

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
s3 = boto3.resource('s3')

def GET(fs, src_path, dest_path, version=None):
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

	# Locate node corresponding to file
	root_node = fetch_node(fs, root_cksum)
	visited_nodes = []
	_,file_node = get_merkle_node_by_name(fs, root_node, src_path.lstrip('/').split('/'), visited_nodes)

	if not file_node:
		return "File {} does not exist".format(src_path)

	# Get file from s3
	s3.meta.client.download_file(s3_bucket, file_node.cksum, dest_path)
	return "Downloaded {} to {}".format(src_path, dest_path)
