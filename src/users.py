import urllib3
import boto3
import json

def get_user(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Got User!')
    }

def create_user(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Create user!')
    }

def update_user(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Update user!')
    }

def delete_user(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Delete user!')
    }

def authorise_spotify(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Authorise Spotify!')
    }

def logout_spotify(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Logout Spotify!')
    }