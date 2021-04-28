import uuid
import boto3

from error import ApiError
from utils import (
    _extract_path_param,
    _extract_body,
    _get_user,
    _success_response,
    _process_api_error
)

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("kude-users")


def get_user(event, context):
    try:
        user_id = _extract_path_param(event, "user_id")
        user = _get_user(user_id, users_table)

        return _success_response(user)

    except ApiError as e:
        return _process_api_error(e)


def create_user(event, context):
    try:
        body = _extract_body(event)

        new_id = str(uuid.uuid1())
        users_table.put_item(
            Item={
                "user_id": new_id,
                "user_name": body["user_name"] if "user_name" in body else None,
                "image_url": body["image_url"] if "image_url" in body else None,
                "host": False
            }
        )

        return _success_response(new_id)

    except ApiError as e:
        return _process_api_error(e)


def update_user(event, context):
    try:
        user_id = _extract_path_param(event, "user_id")
        body = _extract_body(event)
        _get_user(user_id, users_table)

        if "user_name" not in body or "image_url" not in body:
            raise ApiError("Invalid body")

        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET user_name = :u, image_url = :i',
            ExpressionAttributeValues={
                ':u': body["user_name"],
                ':i': body["image_url"]
            }
        )

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)


def delete_user(event, context):
    try:
        user_id = _extract_path_param(event, "user_id")

        users_table.delete_item(Key={"user_id": user_id})

        return _success_response()

    except ApiError as e:
        return _process_api_error(e)
