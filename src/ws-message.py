import boto3
import os
from boto3.dynamodb.conditions import Key

client = boto3.client('apigatewaymanagementapi',
                      endpoint_url=os.environ.get('WEBSOCKET_URL'))
table = boto3.resource('dynamo-db').Table('kude-connections')


def send_session_update(session_id):

    response = table.query(
        KeyConditionExpression=Key('session_id').eq(session_id)
    )

    connection_ids = list(map(lambda x: x["connection_id"], response["Items"]))
    print(connection_ids)
