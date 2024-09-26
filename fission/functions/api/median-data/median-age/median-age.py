# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function provides an api to retrieve the median age data by sa3
 from the Elasticsearch server.
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
    
# SA3 Search Query template
sa3_expr = Template('''{
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "sa3_code_2021": "${sa3_code}"
                                }
                            }
                        ]
                    }
                }''')

# Set max_size to the max allowed by the elastic search API
MAX_SIZE = 10000

def get_median_age_all(es):
    """
    Function queries the age_personal_income_sa3 index to retrieve 
    all median age data separated by SA3.

    :param es: Elastic Search connection object
    :return res: response from elastic search query

    """
    query= '''
            {
            "match_all" : {}
            }
            '''
    current_app.logger.info(f"Query: {query}")
    res = es.search(
        index='age_personal_income_sa3',
        query=json.loads(query),
        source=['median_age_persons']
        size=MAX_SIZE
    )
    return res
def get_median_age(es, sa3_code=None):
    # pylint: disable=duplicate-code
    """
    Get the corresponding median age data of the provided sa3
    from the Elasticsearch server.
    :param es: Elasticsearch connection object
    :param sa3_code: SA3 Code
    :return: res: JSON response from the Elasticsearch server
    """

    if sa3_code is not None:
        query = sa3_expr.substitute(sa3_code=sa3_code)

    current_app.logger.info(f"Query: {query}")
    res = es.search(
        index='age_personal_income_sa3',
        query=json.loads(query),
        source=['median_age_persons']
    )
    return res


@current_app.route('/median/age', methods=['GET'])
def main():
    """
    Main function to retrieve the median age data.
    Method : GET
    :return:
    """
    # current_app.logger.setLevel("INFO")
    try:
        sa3_code = request.headers['X-Fission-Params-SA3Code']
    except KeyError:
        current_app.logger.info("SA3 Code not provided")
        sa3_code = None
    es = setup_connection()
    if sa3_code == "all":
        data = get_median_age_all(es)
    else:
        data = get_median_age(es, sa3_code)
    return json.dumps(data["hits"]["hits"][0]["_source"])
