# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function provides an api to retrieve joined SA3 data retrieved from SUDO
from the Elasticsearch server. These include median age, median weekly income, 
highest level of schooling and Age by Sex population data 
"""
import logging, json
from datetime import datetime
from elasticsearch8 import Elasticsearch, AuthenticationException
from flask import current_app, request
from string import Template
import base64


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


def setup_connection():
    # pylint: disable=duplicate-code
    """
    Set up the connection to the Elasticsearch server.
    :return: es: Elasticsearch connection object
    """
    # Disable SSL Certificate Verification
    es_url = shared_config("ES_URL")
    username = secret('username')
    password = secret('password')

    client = Elasticsearch(es_url,
                       verify_certs=False,
                       basic_auth=(username,
                                   password))

    # Set up the connection to the Elasticsearch server
    try:
        # client.info()
        print("Connected to ES")
        return client
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except AuthenticationException as e:
        print(f"Error: {e}")
        return None

MAX_SIZE = 10000
def get_joined_data(es):
    # pylint: disable=duplicate-code
    """
    Get the joined SA3 data from the Elasticsearch server.
    :param es: Elasticsearch connection object

    :return: res: JSON response from the Elasticsearch server
    """
    query= '''{
            "match_all" : {}
        }'''
    current_app.logger.info(f"Fetching all data")
    res = es.search(
        index='sa3_join',
        query=json.loads(query),
        size=MAX_SIZE
    )
    return res


@current_app.route('/sa3-joined/all', methods=['GET'])
def main():
    """
    Main function to retrieve all joined SA3 data.
    Method : GET
    :return:
    """
    # current_app.logger.setLevel("INFO")
   
    es = setup_connection()
    data = get_joined_data(es)
    output = ([record["_source"] for record in data["hits"]["hits"]])
    return json.dumps(output)

if __name__ == "__main__":
    main()