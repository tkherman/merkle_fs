from __future__ import print_function
import sys
import boto3
import hashlib
import datetime

client = boto3.client('dynamodb', region_name='us-east-1')

def create_fs(namespace):
    # Create a table for metadata merkle tree
    table = client.create_table(
        TableName=namespace,
        KeySchema=[
            {
                'AttributeName': 'cksum',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'cksum',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    print("Creating table...")

    # Initialize table with empty root directory hash
    waiter = client.get_waiter('table_exists')
    waiter.wait(TableName=namespace)
    hasher = hashlib.sha256()

    print("Table successfully created")
    response = client.put_item(
        TableName=namespace,
        Item={
            'cksum': {
                'S': hasher.hexdigest()
            },
            'name': {
                'S': 'root'
            },
            'is_dir': {
                'BOOL': True
            },
            'mod_time': {
                'S': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            },
            'mod_user': {
                'S': 'admin'
            }
        }
    )

    # Create S3 bucket

    # Add fs to root_pointers table

if __name__ == "__main__":
    namespace = sys.argv[1]

    create_fs(namespace)
