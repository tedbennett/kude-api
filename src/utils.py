import urllib3
import boto3
import json

def get_s3_signed_url(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Got s3!')
    }

def search_spotify(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Got s3!')
    }