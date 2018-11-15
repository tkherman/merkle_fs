from __future__ import print_function
import sys
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

class MerkleNode:
    def __init__(self):
        self.cksum = None
        self.name = None
        self.prev_version = None
        self.next_version = None
        self.parent_nodde = None
        self.is_dir = None
        self.s3_ref = list()
        self.dir_info = list()
        self.mod_time = None
        self.mod_user = None

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

    print(item)

    # Create MerkleNode object
    mNode = MerkleNode()
    mNode.cksum = cksum
    mNode.name = item.get('name', None)
    mNode.prev_version = item.get('prev_version', None)
    mNode.next_version = item.get('next_version', None)
    mNode.is_dir = item.get('is_dir', None)
	mNode.parent_node = item.get('parent_node', None)
    mNode.s3_ref = item.get('s3_ref', None)
    mNode.dir_info = item.get('dir_info', None)
    mNode.mod_time = item.get('mod_time', None)
    mNode.mod_user = item.get('mod_user', None)


    return mNode

def fetchNodeByName(fs):
	root_table = dynamodb.Table('root_pointers')
	try:
		response = root_table.get_item(
			Key={
				'name': fs
			}
		)
	except ClientError as e:
		return None
	
	root_item = response.get('Item')
	
	if not root_item:
		return None
	
	root_ptr = item.get('name', None)

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
	
	#TODO - traverse fs_table filesystem to find the correct node
	
