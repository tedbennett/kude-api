import urllib3
from urllib.parse import urlencode
import json
import os
import time
import boto3

from error import ApiError
from utils import (
    _extract_path_param,
    _extract_body,
    _extract_query,
    _get_user,
    _success_response,
    _process_api_error,
    _parse_song,
    _parse_songs
)

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("kude-users")


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


def _get_code_credentials(code):
    http = urllib3.PoolManager()
    encoded_args = urlencode({
        'grant_type': 'authorization_code',
        'code': code,
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

    if 'access_token' not in data or 'refresh_token' not in data or 'expires_in' not in data:
        raise ApiError('Failed to get spotify credentials', 500)

    return (data['access_token'], data['refresh_token'], data['expires_in'])


def _refresh_credentials(refresh_token):
    http = urllib3.PoolManager()
    encoded_args = urlencode({
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': '1e6ef0ef377c443e8ebf714b5b77cad7',
        'client_secret': os.environ.get('SPOTIFY_SECRET')
    })

    res = http.request(
        'POST',
        f'https://accounts.spotify.com/api/token?{encoded_args}',
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    data = json.loads(res.data.decode('utf-8'))

    if 'access_token' not in data or 'expires_in' not in data:
        raise ApiError('Failed to get spotify credentials', 500)

    return (data['access_token'], data['expires_in'])


def _get_spotify_profile(access_token):
    http = urllib3.PoolManager()
    res = http.request(
        'GET',
        'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    data = json.loads(res.data.decode('utf-8'))

    if 'product' not in data:
        raise ApiError('Failed to find spotify profile', 404)

    return data['product'] == 'premium'


def _add_song_to_queue(access_token, uri):
    http = urllib3.PoolManager()
    res = http.request(
        'POST',
        f'https://api.spotify.com/v1/me/player/queue?uri={uri}',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    if res.status != 204:
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

    return _parse_song(data['item'])


# Lambda functions
def authorise_spotify(event, context):
    try:
        user_id = _extract_path_param(event, "user_id")
        body = _extract_body(event)

        _get_user(user_id, users_table)

        if "code" not in body:
            raise ApiError("Invalid body")

        access_token, refresh_token, expires_in = _get_code_credentials(body['code'])

        expires_at = str(int(expires_in + time.time()))

        if not _get_spotify_profile(access_token):
            raise ApiError("Spotify account is not premium", 403)

        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET access_token=:a, refresh_token=:r, expires_at=:e, host=:h',
            ExpressionAttributeValues={
                ":a": access_token,
                ":r": refresh_token,
                ":e": expires_at,
                ':h': True
            }
        )

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def logout_spotify(event, context):
    try:
        user_id = _extract_path_param(event, "user_id")
        _get_user(user_id, users_table)

        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET access_token=:a, refresh_token=:r, expires_at=:e, host=:h',
            ExpressionAttributeValues={
                ":a": None,
                ":r": None,
                ":e": None,
                ':h': False
            }
        )

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def search_spotify(event, context):
    try:
        query = _extract_query(event)['query']

        token = _get_client_credentials()
        http = urllib3.PoolManager()
        res = http.request(
            'GET',
            f'https://api.spotify.com/v1/search?q={query}&type=track&limit=10',
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        data = json.loads(res.data.decode('utf-8'))

        songs = _parse_songs(data)

        return _success_response(songs)

    except ApiError as e:
        return _process_api_error(e)
