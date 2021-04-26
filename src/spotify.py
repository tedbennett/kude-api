import urllib3
from urllib.parse import urlencode
import json
import os
import time


from error import ApiError
from utils import (
    _extract_path_param,
    _extract_body,
    _extract_query,
    _get_user,
    _get_table,
    _success_response,
    _process_api_error,
    _update_table,
    _parse_songs
)


def _get_client_credentials():
    http = urllib3.PoolManager()
    encoded_args = urlencode({
        'grant_type': 'client_credentials',
        'client_id': '1e6ef0ef377c443e8ebf714b5b77cad7',
        'client_secret': os.environ.get('SPOTIFY_SECRET')
    })
    res = http.request(
        'POST',
        f'https://accounts.spotify.com/api/token?{encoded_args}',
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    data = json.loads(res.data.decode('utf-8'))

    if 'access_token' not in data:
        raise ApiError('Failed to get spotify credentials', 500)

    return data['access_token']


def _add_song_to_queue(access_token, uri):
    http = urllib3.PoolManager()
    res = http.request(
        'POST',
        f'https://api.spotify.com/v1/me/player/queue?uri={uri}',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    if res.data is None:
        raise ApiError('Active device not found', 404)

    data = json.loads(res.data.decode('utf-8'))
    if 'error' in data:
        raise ApiError('Active device not found', 404)

    return


def _get_currently_playing(access_token):
    http = urllib3.PoolManager()
    res = http.request(
        'GET',
        'https://api.spotify.com/v1/me/player/currently-playing',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    if res.data is None:
        raise ApiError('Active device not found', 404)

    data = json.loads(res.data.decode('utf-8'))

    if 'item' not in data:
        raise ApiError('Active device not found', 404)

    return _parse_songs(data['item'])


# Lambda functions
def authorise_spotify(event, context):
    try:
        user_id = _extract_path_param(event, "user_id")
        body = _extract_body(event)

        table = _get_table('users')
        _get_user(user_id, table)

        if "code" not in body:
            raise ApiError("Invalid body")

        http = urllib3.PoolManager()
        encoded_args = urlencode({
            'grant_type': 'authorization_code',
            'code': body['code'],
            'redirect_uri': 'queued://oauth-callback/',
            'client_id': '1e6ef0ef377c443e8ebf714b5b77cad7',
            'client_secret': os.environ.get('SPOTIFY_SECRET')
        })
        res = http.request(
            'POST',
            f'https://accounts.spotify.com/api/token?{encoded_args}',
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        data = json.loads(res.data.decode('utf-8'))

        if 'access_token' not in data:
            raise ApiError('Failed to get spotify credentials', 500)

        _update_table(table, user_id, {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": str(int(data['expires_in'] + time.time()))
        })

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def logout_spotify(event, context):
    try:
        user_id = _extract_path_param(event, "user_id")
        table = _get_table('users')
        _get_user(user_id, table)

        _update_table(table, user_id, {
            "access_token": None,
            "refresh_token": None,
            "expires_at": None
        })

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def search_spotify(event, context):
    try:
        query = _extract_query('query')

        token = _get_client_credentials()
        http = urllib3.PoolManager()
        res = http.request(
            'POST',
            f'https://api.spotify.com/v1/search?q={query}&type=track&limit=10',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Bearer {token}'
            }
        )

        songs = _parse_songs(res)

        return _success_response(songs)

    except ApiError as e:
        return _process_api_error(e)
