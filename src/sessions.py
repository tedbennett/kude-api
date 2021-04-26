from boto3.dynamodb.conditions import Attr
import time
import uuid


from error import ApiError
from utils import (
    _extract_path_param,
    _extract_body,
    _get_user,
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
        session_key = _extract_path_param(event, "key")
        table = _get_table('sessions')
        response = table.scan(
            FilterExpression=Attr('key').eq(session_key)
        )
        if "Items" not in response or len(response["Items"]) == 0:
            raise ApiError("Session not found", 404)

        return _success_response(response["Items"][0])

    except ApiError as e:
        return _process_api_error(e)


def create_session(event, context):
    try:
        body = _extract_body(event)
        table = _get_table('sessions')

        if 'session_name' not in body or 'user_id' not in body:
            raise ApiError('Invalid body')

        users_table = _get_table('users')
        host = _get_user(body['user_id'], users_table)

        if "access_token" not in host or host["access_token"] is None:
            raise ApiError("Invalid session host", 400)

        new_id = str(uuid.uuid1())
        table.put_item(
            Item={
                "session_id": new_id,
                'key': str(uuid.uuid4().hex[:6]).upper(),
                'host': body['user_id'],
                "session_name": body["session_name"],
                "members": [body["user_id"]],
                "queue": [],
                "currently_playing": None,
                "created_at": str(int(time.time())),
                "updated_at": str(int(time.time()))
            }
        )

        _update_table(users_table, {'user_id': body['user_id']}, {
            "session": new_id
        })

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

        _update_table(table, {'session_id': session_id}, {
            "session_name": body["session_name"]
        })

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def delete_session(event, context):
    try:
        session_id = _extract_path_param(event, "session_id")
        table = _get_table('sessions')
        session = _get_session(session_id, table)
        users_table = _get_table('users')

        for member in session["members"]:
            _update_table(users_table, {'user_id': member}, {'session': None})

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
        user_id = body['user_id']

        users_table = _get_table('users')
        _get_user(user_id, users_table)

        if "members" not in session:
            raise ApiError("Invalid session", 500)

        if user_id in session["members"]:
            return _success_response()

        table.update_item(
            Key={'session_id': session_id},
            UpdateExpression='SET members = list_append(members, :m)',
            ExpressionAttributeValues={
                ':m': [user_id]
            }
        )

        _update_table(users_table, {'user_id': user_id}, {
            "session": session_id
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

        try:
            index = session["members"].index(body["user_id"])
        except ValueError:
            raise ApiError("User not found", 404)

        table.update_item(
            Key={'session_id': session_id},
            UpdateExpression=f'REMOVE members[{index}]'
        )

        users_table = _get_table('users')

        _update_table(users_table, {'user_id': body["user_id"]}, {
            "session": None
        })

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def add_song_to_session_queue(event, context):
    try:
        session_id = _extract_path_param(event, "session_id")
        body = _extract_body(event)

        if "song" not in body:
            raise ApiError("Invalid body")

        table = _get_table('sessions')
        session = _get_session(session_id, table)

        if "host" not in session:
            raise ApiError("Invalid host", 500)

        users_table = _get_table('users')
        host = _get_user(session['host'], users_table)

        if "access_token" not in host or host["access_token"] is None:
            raise ApiError("Invalid session", 500)

        _add_song_to_queue(host['access_token'], body['song']['id'])

        table.update_item(
            Key={'session_id': session_id},
            UpdateExpression='SET queue = list_append(queue, :s)',
            ExpressionAttributeValues={
                ':s': [body["song"]]
            }
        )

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

        _update_table(table, {'session_id': session_id}, {
            "currently_playing": str(currently_playing),
        })

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)
