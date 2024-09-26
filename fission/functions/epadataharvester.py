# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
Data harvester file for the EPA data.
"""

import json
import uuid
from datetime import datetime

import requests
from flask import current_app, request


def config(k):
    # pylint: disable=duplicate-code
    """

    :param k: Key value for the configuration.
    :return: value of the key.
    """
    with open(f"/configs/default/shared-data/{k}", "r", encoding="utf-8") as f:
        return f.read()


def main():
    # pylint: disable=duplicate-code
    """
    Main function to get the data from the EPA API.
    :return:
    """
    header = {
        "X-TransactionID": uuid.uuid4().hex,
        "X-SessionID": uuid.uuid4().hex,
        "X-CreationTime": datetime.now().isoformat(),
        "X-InitialOperation": "GET",
        "Cache-Control": "no-cache",
        "X-API-Key": config("EPA_API_KEY"),
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    }

    current_app.logger.info(f"Sites to get data from:  {request.get_json(force=True)}")

    for site_id in request.get_json(force=True):
        api_url = config("EPA_BASE_URL") + site_id
        current_app.logger.info(f"Getting data for site: {site_id}")
        try:
            response = requests.request("GET", api_url, headers=header, timeout=10)
            if response.status_code == 200:
                data = json.dumps(response.json())
                current_app.logger.info(
                    f"Request status: {response.status_code} - " f"{response.text}"
                )
                return data
            current_app.logger.error(
                f"Request status: {response.status_code} - " f"{response.text}"
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
