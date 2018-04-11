import logging
import os
from typing import List, Dict

def lambda_handler(event, context):
    lat = event["lat"]
    lon = event["lon"]
    apikey = os.environ["apikey"]
    resp = "lat: {0}, lon: {1}, key: {2}".format(lat, lon, apikey)
    return resp
