import boto3
import json

from error import ApiError


# Responses
def _success_response(body=None):
    if body is None:
        return {"statusCode": 200}

    return {"statusCode": 200, "body": json.dumps(body)}


def _process_api_error(error):
    return {
        "statusCode": error.status_code,
        "body": json.dumps({"error": error.message}),
    }


# Request helper functions
def _extract_path_param(event, key):
    if "pathParameters" in event and event["pathParameters"][key] is not None:
        return event["pathParameters"][key]
    else:
        raise ApiError("Invalid path param")


def _extract_body(event):
    if "body" in event:
        return json.loads(event["body"])
    else:
        raise ApiError("Invalid body")


def _extract_query(event):
    if "queryStringParameters" in event:
        return event["queryStringParameters"]
    else:
        raise ApiError("Invalid query")


# Dynamo helper functions
def _update_table(table, user_id, values):
    expression = 'SET'
    attribute_values = {}
    i = 0
    for key, value in values.items():
        expression += f' {key} = :val{i},'
        attribute_values[f':val{i}'] = value
        i += 1
    expression = expression[:-1]

    table.update_item(
        Key={'user_id': user_id},
        UpdateExpression=expression,
        ExpressionAttributeValues=attribute_values
    )


def _get_table(name):
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(f"kude-{name}")  # pylint: disable=no-member


# User helper functions
def _get_user(user_id, table):
    response = table.get_item(Key={"user_id": user_id})
    if "Item" in response:
        return response["Item"]
    raise ApiError("User not found", 404)


# Session helper functions
def _get_session(session_id, table):
    response = table.get_item(Key={"session_id": session_id})
    if "Item" in response:
        return response["Item"]
    raise ApiError("Session not found", 404)


def _parse_songs(json):
    try:
        return list(map(
            lambda x: {
                "id": x["uri"],
                'name': x['name'],
                'album': x['album']['name'],
                'artist': x['artists'][0]['name'],
                'image_url': x['album']['images'][0].url
            },
            json["data"]["tracks"]))
    except Exception:
        raise ApiError('Could not read Spotify response')
