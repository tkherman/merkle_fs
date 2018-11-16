from __future__ import print_function
import boto3

from MerkleNode import MerkleNode, fetch_node, get_file_node

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.resource('s3')

def PUT(fs, src_filepath, dest_filepath):
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
