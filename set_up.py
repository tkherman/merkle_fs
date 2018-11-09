from __future__ import print_function
import boto3
import sys

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def create_fs(namespace):
    # Create a table for metadata merkle tree
    table = dynamodb.create_table(
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

    print("Metadata table status:", table.table_status)

if __name__ == "__main__":
    namespace = sys.argv[1]

    create_fs(namespace)
