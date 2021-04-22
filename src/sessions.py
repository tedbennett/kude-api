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
    print(json.loads(event))
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

def add_member_to_session(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Add Member to Session!')
    }

def remove_member_from_session(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Remove Member from Session!')
    }

def add_song_to_session_queue(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Add Song to Session Queue!')
    }

def update_now_playing(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Update Now Playing!')
    }