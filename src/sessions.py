from boto3.dynamodb.conditions import Attr
import time
import uuid


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
from spotify import _add_song_to_queue, _get_currently_playing


def get_session(event, context):
    try:
        session_id = _extract_path_param(event, "session_id")
        table = _get_table('sessions')
        session = _get_session(session_id, table)

        return _success_response(session)

    except ApiError as e:
        return _process_api_error(e)


def get_session_by_key(event, context):
    try:
        session_key = _extract_path_param(event, "session_key")
        table = _get_table('sessions')
        response = table.scan(
            FilterExpression=Attr('key').eq(session_key)
        )
        if "Item" not in response:
            raise ApiError("User not found", 404)

        return _success_response(response["Item"])

    except ApiError as e:
        return _process_api_error(e)


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
                'key': str(uuid.uuid4().hex[:6]).upper(),
                'host': body['user_id'],
                "name": body["name"],
                "members": [body["user_id"]],
                "queue": [],
                "currently_playing": None,
                "created_at": str(int(time.time())),
                "updated_at": str(int(time.time()))
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
    try:
        session_id = _extract_path_param(event, "session_id")
        body = _extract_body(event)
        table = _get_table('sessions')
        session = _get_session(session_id, table)

        if "user_id" not in body:
            raise ApiError("Invalid body")

        if "members" not in session:
            raise ApiError("Invalid session", 500)

        _update_table(table, session_id, {
            "members": list(set(session["members"].append(body['user_id']))),
        })

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def remove_member_from_session(event, context):
    try:
        session_id = _extract_path_param(event, "session_id")
        body = _extract_body(event)
        table = _get_table('sessions')
        session = _get_session(session_id, table)

        if "user_id" not in body:
            raise ApiError("Invalid body")

        if "members" not in session:
            raise ApiError("Invalid session", 500)

        _update_table(table, session_id, {
            "members": session["members"].remove(body['user_id']),
        })

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def add_song_to_session_queue(event, context):
    try:
        session_id = _extract_path_param(event, "session_id")
        body = _extract_body(event)
        table = _get_table('sessions')
        session = _get_session(session_id, table)

        if "song" not in body:
            raise ApiError("Invalid body")

        if "queue" not in session or "access_token" not in session:
            raise ApiError("Invalid session", 500)

        _add_song_to_queue(session['access_token'], body['song']['id'])

        _update_table(table, session_id, {
            "queue": session["queue"].append(body['song']),
        })

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def update_now_playing(event, context):
    try:
        session_id = _extract_path_param(event, "session_id")
        table = _get_table('sessions')
        session = _get_session(session_id, table)

        if "updated_at" not in session or "access_token" not in session or "currently_playing" not in session:
            raise ApiError("Invalid session", 500)

        if session["updated_at"] + 90 > time.time():
            return _success_response()

        currently_playing_song = _get_currently_playing(session["access_token"])

        currently_playing = [i for i, el in enumerate(session['songs']) if el['id'] == currently_playing_song['uri']]

        if len(currently_playing) == 0 or currently_playing[0] <= session["currently_playing"]:
            return _success_response()

        _update_table(table, session_id, {
            "currently_playing": str(currently_playing),
        })

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)
