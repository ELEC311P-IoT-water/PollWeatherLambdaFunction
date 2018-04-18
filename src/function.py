import logging, os, json, boto3
import requests
from requests import Response
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_yesterday() -> str:
    return datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')

def get_today() -> str:
    return datetime.strftime(datetime.now(), '%Y-%m-%d')

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

def convertToDict(string: str) -> dict:
    return json.loads(string)

def makeReq( apikey: str
           , lat: str
           , lon: str
           ) -> Response:
    logger.debug("url: {}".format(url))
    headers = {"Accept: application/json"}
    yesterday = get_yesterday()
    today = get_today()
    payload = { "lat": lat
              , "lon": lon
              , "start_date": yesterday
              , "end_date": today
              , "key": apikey }
    return requests.get( "https://api.weatherbit.io/v2.0/history/daily"
                       , params = payload
                       )

def putS3(bucket: str, key: str, data: str) -> dict:
    s3 = boto3.resource("s3")
    obj = s3.Object(bucket, key)
    data = json.dumps(data)
    return obj.put(Body = data)

def get_bucket() -> dict:
    return os.environ["bucket"]

def lambda_handler(event, context):
    lat = event["lat"]
    lon = event["lon"]
    secret_manager_content = convertToDict(get_apikey())
    apikey = secret_manager_content["WeatherbitApikey"]
    logger.debug("lat: {0}, lon: {1}, key: {2}".format(lat, lon, apikey))
    resp = makeReq(apikey, lat, lon)
    if resp.status_code == 200:
        bucket = get_bucket()
        key = get_yesterday()
        resp = putS3(bucket, key, resp.json())
    return resp
