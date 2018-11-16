from __future__ import print_function
import boto3
import hashlib
import datetime
import os.path
import getpass

from MerkleNode import MerkleNode, fetch_node, get_merkle_node_by_name, insert_node

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.resource('s3')

def calculate_cksum(src_filepath):
    hasher = hashlib.sha256()
    with open(src_filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)

    return hasher.hexdigest()

def PUT(fs, src_filepath, dest_filepath):
    if not os.path.isfile(src_filepath):
        return "{} is not a local file".format(src_filepath)

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
    root_cksum = response['Item']['cksum']

    # Get node of directory the file is to be placed in
    node_traversed = []
    root_node = fetch_node(fs, root_cksum)
    dest_filepath = dest_filepath.lstrip('/').split('/')
    if len(dest_filepath) > 1:
        dirpath = dest_filepath[:-1]
        dir_node = get_merkle_node_by_name(fs, root_node, dest_filepath)
    else:
        dir_node = root_node

    # Check if file already exist
    original_fnode = None
    for sub_f in dir_node.dir_info[1:]:
        if sub_f[0] == dest_filepath[-1]:
            original_fnode = fetch_node(fs, sub_f[1])

    # Create MerkleNode object for new node
    newNode = MerkleNode()
    newNode.cksum = calculate_cksum(src_filepath)
    newNode.name = dest_filepath[-1]
    if original_fnode:
        newNode.prev_version = original_fnode.cksum
    newNode.is_dir = False
    newNode.mod_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    newNode.mod_user = getpass.getuser()

    if not insert_node(fs, newNode):
        return "Failed to update DB"

    # Place actual file to S3 with name==cksum
    s3.meta.client.upload_file(src_filepath, s3_bucket, newNode.cksum)

    # Bubble up and create new node for all ancestors

print(PUT("testfstwo", "README.md", "/README.md"))
