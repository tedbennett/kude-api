import boto3
import os
import json
from boto3.dynamodb.conditions import Attr

from utils import _get_session

api_gateway = boto3.client('apigatewaymanagementapi',
                           endpoint_url=os.environ.get('WEBSOCKET_URL'))
connections_table = boto3.resource('dynamodb').Table('kude-connections')
sessions_table = boto3.resource('dynamodb').Table('kude-sessions')


def send_session_update(event, context):
    if 'session_id' not in event:
        return {'statusCode': 500}
    session_id = event['session_id']
    response = connections_table.scan(
        FilterExpression=Attr('session_id').eq(session_id)
    )

    connection_ids = list(map(lambda x: x["connection_id"], response["Items"]))
    session = _get_session(session_id, sessions_table)

    for connection_id in connection_ids:
        api_gateway.post_to_connection(json.dumps(session), ConnectionId=connection_id)

    return {'statusCode': 200}
