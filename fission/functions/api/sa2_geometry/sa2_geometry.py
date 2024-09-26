# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function provides an api to download the whole sa2 dataset including geometry.
The format of the response is easily convertible to geojson.
"""
import base64
import json
import warnings

from elasticsearch8 import Elasticsearch, AuthenticationException

warnings.filterwarnings("ignore")

AGGREGATION_MAX_SIZE = 2147483647


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


def get_geometry(es: Elasticsearch) -> dict:
    """
    Retrieves all sa2 documents from the Elasticsearch index.
    """
    size = es.count(index="sa2_data")["count"]

    sa2_response = es.search(
        index="sa2_data",
        size=size,
    )

    return [document["_source"] for document in sa2_response["hits"]["hits"]]


def main():
    """
    Main function to retrieve all sa2 documents.
    """
    es = setup_connection()
    geometry = get_geometry(es)

    return json.dumps(geometry)
