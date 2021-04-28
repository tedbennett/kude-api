import boto3
import json

table = boto3.resource('dynamo-db').Table('kude-connections')


def on_join(event, context):
    connection_id = event['requestContext']['connectionId']
    if 'body' not in event:
        return
    body = json.loads(event['body'])
    if body['type'] != 'join':
        return
    session_id = body['session_id']

    table.put_item(
        Item={
            "connection_id": connection_id,
            'session_id': session_id
        }
    )


def on_disconnect(event, context):
    connection_id = event['requestContext']['connectionId']
    table.delete_item(Key={"connection_id": connection_id})
