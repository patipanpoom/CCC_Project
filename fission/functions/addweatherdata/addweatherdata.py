# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function is used to add observations to the Elasticsearch index.
"""
import base64

from elasticsearch8 import Elasticsearch
from flask import current_app, request


def config(k):
    # pylint: disable=duplicate-code
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
    with open(f"/secrets/default/es-secret/{k}", "r", encoding="utf-8") as f:
        return base64.b64decode(f.read()).decode("utf-8")


def main():
    # pylint: disable=duplicate-code
    """
    Main function to add weather observations to the Elasticsearch index.
    :return:
    """
    username = secret('username')
    password = secret('password')
    client = Elasticsearch(
        config('ES_URL'),
        verify_certs=False,
        basic_auth=(username, password),
    )

    record = request.get_json(force=True)
    current_app.logger.info(f"Observations to add:  {record}")

    res = client.index(
        index="weather",
        id=str(record["siteid"]) + "-" + record["timestamp"],
        body=record,
    )
    current_app.logger.info(f'Index response: {res["result"]}')
    current_app.logger.info(
        f'Indexed observation {record["siteid"]}-{record["timestamp"]}'
    )

    return "ok"
