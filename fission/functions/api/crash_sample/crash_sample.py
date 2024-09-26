# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function provides an api to take random samples of the crash dataset.
"""
import base64
import json
import warnings

from elasticsearch8 import Elasticsearch, AuthenticationException
from flask import request

warnings.filterwarnings("ignore")

MAX_QUERY_SIZE = 10_000

def shared_config(k):
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


def setup_connection() -> Elasticsearch:
    # pylint: disable=duplicate-code
    """
    Set up the connection to the Elasticsearch server.
    :return: es: Elasticsearch connection object
    """
    # Disable SSL Certificate Verification
    es_url = shared_config("ES_URL")
    username = secret('username')
    password = secret('password')

    es = Elasticsearch([es_url],
                       verify_certs=False,
                       basic_auth=(username,
                                   password))

    # Set up the connection to the Elasticsearch server
    try:
        es.info()
        print("Connected to ES")
        return es
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except AuthenticationException as e:
        print(f"Error: {e}")
        return None


def get_crash_sample(es: Elasticsearch, size: int) -> dict:
    """
    Gets a random sample of the crash dataset with size specified by the size parameter.
    """
    response = es.search(
        index="crash_sa2_joined",
        query={
            "function_score": {
                "random_score": {}
            }
        },
        size=size
    )

    return response


def main():
    """
    Main function for the crash sampling endpoint.
    """
    sample_size = int(request.headers['X-Fission-Params-Size'])

    if sample_size > MAX_QUERY_SIZE:
        return json.dumps({
            "error": f"Provided sample size {sample_size} is too large. Limit is {MAX_QUERY_SIZE}"
        }), 400

    es = setup_connection()
    data = get_crash_sample(es, sample_size)

    hits = data["hits"]["hits"]
    return json.dumps([document["_source"] for document in hits])
