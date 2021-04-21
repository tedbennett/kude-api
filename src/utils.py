import urllib3
import boto3
import json

def get_s3(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Got s3!')
    }