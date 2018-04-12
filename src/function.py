import logging
import os
from typing import List, Dict
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_apikey() -> str:
    secret_name = "iot/prod/weatherkey"
    endpoint_url = "https://secretsmanager.eu-central-1.amazonaws.com"
    region_name = "eu-central-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        endpoint_url=endpoint_url
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.info("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            logger.info("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            logger.info("The request had invalid params:", e)
        raise e
    else:
        # Decrypted secret using the associated KMS CMK
        # Depending on whether the secret was a string or binary,
        # one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            binary_secret_data = get_secret_value_response['SecretBinary']
            return str(binary_secret_data)
    raise Exception("Couldn't get Secret Value")


def lambda_handler(event, context):
    lat = event["lat"]
    lon = event["lon"]
    apikey = get_apikey()
    resp = "lat: {0}, lon: {1}, key: {2}".format(lat, lon, apikey)
    return resp
