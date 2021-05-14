import boto3
import os
from error import ApiError
from utils import _extract_query, _process_api_error, _success_response


def get_s3_signed_url(event, context):
    try:
        s3_client = boto3.client('s3')
        user_id = _extract_query(event)['user_id']

        s3_name = os.environ.get('S3_BUCKET')
        signedRequest = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': s3_name, 'Key': "images/" + user_id, 'ContentType': 'jpeg'})

        return _success_response({
            'signedRequest': signedRequest,
            'url': f'https://{s3_name}.s3-eu-west-1.amazonaws.com/images/{user_id}'
        })
    except ApiError as e:
        return _process_api_error(e)
