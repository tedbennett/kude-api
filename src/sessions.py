import urllib3
import boto3
import json

def get_session(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Got Session!')
    }

def get_session_by_key(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Got Session by Key!')
    }

def create_session(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Create session!')
    }

def update_session(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Update session!')
    }

def delete_session(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Delete session!')
    }
