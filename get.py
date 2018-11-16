from __future__ import print_function
import boto3
from botocore.exceptions import ClientError

from MerkleNode import MerkleNode, fetch_node, get_merkle_node_by_name

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.resource('s3')

def GET(fs, file_path):
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

    # Locate node corresponding to file
    root_node = fetch_node(fs, root_cksum)
    file_node = get_merkle_node_by_name(fs, root_node, file_path.lstrip('/').split('/'))

    if not file_node:
        return "File {} does not exist".format(file_path)

    # Get file from s3
    s3.meta.client.download_file(s3_bucket, file_node.cksum, file_path.split('/')[-1])
    return "Downloaded {} to {}".format(file_path, file_path.split('/')[-1])

print (GET('testfs', '/second_dir/file2.txt'))
