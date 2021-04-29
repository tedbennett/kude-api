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


def _get_readable_session(session):
    return {
        **session,
        'created_at': int(session['created_at']) * 1000,
        'currently_playing': int(session['currently_playing']) if session['currently_playing'] is not None else None
    }


def _parse_song(song):
    return {
        "id": song["uri"],
        'name': song['name'],
        'album': song['album']['name'],
        'artist': song['artists'][0]['name'],
        'image_url': song['album']['images'][0]["url"]
    }


def _parse_songs(json):
    try:
        return list(map(
            lambda x: _parse_song(x),
            json["tracks"]['items']))
    except Exception:
        raise ApiError('Could not read Spotify response')
