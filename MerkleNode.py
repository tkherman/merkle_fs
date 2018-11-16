from __future__ import print_function
import sys
import boto3
import hashlib
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

class MerkleNode:
    def __init__(self):
        self.cksum = None
        self.name = None
        self.prev_version = None
        self.next_version = None
        self.parent_node = None
        self.is_dir = None
        self.s3_ref = None
        self.dir_info = None
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

    # Create MerkleNode object
    mNode = MerkleNode()
    mNode.cksum = cksum
    mNode.name = item.get('name', None)
    mNode.prev_version = item.get('prev_version', None)
    mNode.next_version = item.get('next_version', None)
    mNode.parent_node = item.get('parent_node', None)
    mNode.is_dir = item.get('is_dir', None)
    mNode.s3_ref = item.get('s3_ref', None)
    mNode.dir_info = item.get('dir_info', None)
    mNode.mod_time = item.get('mod_time', None)
    mNode.mod_user = item.get('mod_user', None)


    return mNode


# Update the next_version on the existing node
def update_node_next_version(fs, cksum, next_vers_cksum):
    fs_table = dynamodb.Table(fs)

    try:
        response = fs_table.update_item(
            Key={
                'cksum': cksum
            },
            AttributeUpdates={
                'next_version': {
                    'Value': next_vers_cksum,
                    'Action': 'PUT'
                }
            }
        )
    except ClientError as e:
        return False

    return True


# Insert the new node into DB
def insert_node(fs, mNode):
    fs_table = dynamodb.Table(fs)

    try:
        response = fs_table.put_item(
            Item={
                'cksum': mNode.cksum,
                'name': mNode.name,
                'prev_version': mNode.prev_version,
                'next_version': mNode.next_version,
                'is_dir': mNode.is_dir,
                'dir_info': mNode.dir_info,
                'mod_time': mNode.mod_time,
                'mod_user': mNode.mod_user
            }
        )
    except ClientError as e:
        return False

    return True

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


def get_merkle_node_by_name(fs, curr_node, path_list, node_traversed=None):
    if node_traversed:
        node_traversed.append(curr_node)

    if not curr_node.is_dir:
        return None

    for sub_f in curr_node.dir_info[1:]:
        if sub_f[0] == path_list[0]:
            if len(path_list) == 1:
                return fetch_node(fs, sub_f[1])
            return get_merkle_node_by_name(fs, fetch_node(fs, sub_f[1]), path_list[1:])

    # Incorrect path
    return None
