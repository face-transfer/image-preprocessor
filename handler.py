import datetime
import json
import os
from io import BytesIO

import boto3
import PIL
from PIL import Image


def resized_image_url(resized_key, bucket, region):
    return f"https://s3-{region}.amazonaws.com/{bucket}/{resized_key}"


def resize_image(bucket_name, key, size):
    size_split = size.split('x')
    s3 = boto3.resource('s3')
    obj = s3.Object(
        bucket_name=bucket_name,
        key=key,
    )
    obj_body = obj.get()['Body'].read()

    img = Image.open(BytesIO(obj_body))
    img = img.resize(
        (int(size_split[0]), int(size_split[1])), PIL.Image.ANTIALIAS
    )
    buffer = BytesIO()
    img.save(buffer, 'png')
    buffer.seek(0)

    resized_key = f"{size}_{key}"
    obj = s3.Object(
        bucket_name=bucket_name,
        key=resized_key,
    )
    obj.put(Body=buffer, ContentType='image/png')

    region = os.environ["AWS_REGION"]
    return resized_image_url(
        resized_key, bucket_name, region
    )


def call(event, context):
    key = "69999.png"
    size = "100x100"

    bucket = os.environ["BUCKET"]

    result_url = resize_image(bucket, key, size)

    response = {
        "statusCode": 301,
        "body": "",
        "headers": {
            "location": result_url
        }
    }

    return response
