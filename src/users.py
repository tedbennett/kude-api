import urllib3
import boto3
import json

def get_user(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Got User!')
    }
