import boto3
from error import ApiError
from utils import _extract_body, _process_api_error, _success_response


def get_s3_signed_url(event, context):
    try:
        s3_client = boto3.client('s3')
        body = _extract_body(event)

        if 'user_id' not in body:
            raise ApiError('No user id provided', 400)

        response = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': "kude", 'Key': "images/" + body['user_id']})

        return _success_response(response)
    except ApiError as e:
        return _process_api_error(e)
