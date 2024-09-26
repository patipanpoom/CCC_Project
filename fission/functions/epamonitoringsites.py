# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function is used to get the air monitoring site from the EPA API.
"""
import base64
import json
import uuid
from datetime import datetime

from flask import current_app
import requests


def config(k):
    """

    :param k: Key value for the configuration.
    :return: value of the key.
    """
    with open(f"/configs/default/shared-data/{k}", "r", encoding="utf-8") as f:
        return f.read()


def secret(k):
    # pylint: disable=duplicate-code
    """
    :param k: Key value for the secret.
    :return: value of the key.
    """
    with open(f"/secrets/default/epa-secret/{k}", "r", encoding="utf-8") as f:
        return base64.b64decode(f.read()).decode("utf-8")


def main():
    """
    Main function to get the air monitoring site from the EPA API.
    """
    header = {
        "X-TransactionID": uuid.uuid4().hex,
        "X-SessionID": uuid.uuid4().hex,
        "X-CreationTime": datetime.now().isoformat(),
        "X-InitialOperation": "GET",
        "Cache-Control": "no-cache",
        "X-API-Key": secret("EPA_API_KEY"),
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    }
    try:
        api_url = config("EPA_BASE_URL") + "parameters?environmentalSegment=air"
        response = requests.request("GET", api_url, headers=header, timeout=10)
        # kafka_url = config("KAFKA_BASE_URL") + "airquality"
        if response.status_code == 200:
            data = json.dumps(response.json())
            current_app.logger.info(
                f"Request status: {response.status_code} - {response.text}"
            )
            for record in json.loads(data)["records"]:
                data = {}
                data["siteid"] = record["siteID"]
                data["sitename"] = record["siteName"]
                data["geo"] = ",".join(map(str, record["geometry"]["coordinates"]))
                data["timestamp"] = datetime.now().isoformat()
                data["siteHealthAdvices"] = (
                    record["siteHealthAdvices"][0]
                    if "siteHealthAdvices" in record
                    else {}
                )
                if "parameters" in record:
                    if record["parameters"][0]["name"] == "SO2":
                        data["so2"] = record["parameters"][0]["timeSeriesReadings"][
                            0
                        ]["readings"][0]
                    if record["parameters"][0]["name"] == "PM2.5":
                        data["pm2p5"] = record["parameters"][0]["timeSeriesReadings"][
                            0
                        ]["readings"][0]
                    if record["parameters"][0]["name"] == "PM10":
                        data["pm10"] = record["parameters"][0]["timeSeriesReadings"][
                            0
                        ]["readings"][0]
                    if record["parameters"][0]["name"] == "NO2":
                        data["no2"] = record["parameters"][0]["timeSeriesReadings"][
                            0
                        ]["readings"][0]
                else:
                    data["so2"] = {}
                    data["pm2p5"] = {}
                    data["pm10"] = {}
                    data["no2"] = {}

                res = requests.post(
                    url="http://router.fission/enqueue/airquality",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(data),
                    timeout=20,
                )

                if res.status_code != 201:
                    current_app.logger.error(f"Error: {res.status_code}")
                else:
                    current_app.logger.info(f"Kafka response: {res.text}")
            return json.dumps("OK")
        current_app.logger.error(
            f"Request status: {response.status_code} - {response.text}"
        )
        return None
    except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
    ) as e:
        current_app.logger.exception(f"Error: {e}")
        return None
