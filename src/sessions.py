import urllib3
import boto3
import json

def get_session(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Got Session!')
    }
