import uuid
import json

from error import ApiError
from utils import (
    _extract_path_param,
    _extract_body,
    _get_table,
    _get_session,
    _success_response,
    _process_api_error,
    _update_table
)


def get_session(event, context):
    try:
        session_id = _extract_path_param(event, "session_id")
        table = _get_table('sessions')
        session = _get_session(session_id, table)

        return _success_response(session)

    except ApiError as e:
        return _process_api_error(e)


def get_session_by_key(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Got Session by Key!')
    }


def create_session(event, context):
    try:
        body = _extract_body(event)
        table = _get_table('sessions')

        if 'name' not in body or 'user_id' not in body:
            raise ApiError('Invalid body')

        new_id = str(uuid.uuid1())
        table.put_item(
            Item={
                "session_id": new_id,
                'key': str(uuid.uuid4().hex[:6]),
                'host': body['user_id'],
                "name": body["name"],
                "members": [body["user_id"]],
                "queue": [],
            }
        )

        return _success_response({"session_id": new_id})

    except ApiError as e:
        return _process_api_error(e)


def update_session(event, context):
    try:
        session_id = _extract_path_param(event, "session_id")
        body = _extract_body(event)
        table = _get_table('sessions')
        _get_session(session_id, table)

        if "session_name" not in body:
            raise ApiError("Invalid body")

        _update_table(table, session_id, {
            "session_name": body["session_name"],
            "image_url": body["image_url"] if "image_url" in body else None
        })

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def delete_session(event, context):
    try:
        session_id = _extract_path_param(event, "session_id")
        table = _get_table('sessions')

        table.delete_item(Key={"session_id": session_id})

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


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
