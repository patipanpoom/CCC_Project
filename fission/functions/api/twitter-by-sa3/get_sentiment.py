# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function provides an api to retrieve the twitter sentiment data
 from the Elasticsearch server.
"""
import logging, json
from datetime import datetime
from elasticsearch8 import Elasticsearch, AuthenticationException
from flask import current_app, request
from string import Template
import base64

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

date_expr = Template('''{
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "sa3_code_2021": "${sa3_code}"
                                }
                            }, 
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": "${start_date}T00:00:00",
                                        "lte": "${end_date}T23:59:59"
                                    }
                                }
                            }
                        ]
                    }
                }''')

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
    # try:
    #     current_app.logger.info(f"username: {secret('username')}, "
    #                             f"password: {secret('password')}")
    # except Exception as e:
    #     current_app.logger.error(f"Error: {e}")
    es = Elasticsearch(es_url,
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


def get_twitter_sentiment(es, sa3_code=None, start_date=None, end_date=None):
    # pylint: disable=duplicate-code
    """
    Get the Avg weather data from the Elasticsearch server.
    :param es: Elasticsearch connection object
    :param lga_code: LGA Code
    :param date: date
    :return: res: JSON response from the Elasticsearch server
    """
    if start_date is not None and end_date is not None:
        query = date_expr.substitute(sa3_code=sa3_code, start_date=start_date, end_date=end_date)
    else:
        query = sa3_expr.substitute(sa3_code=sa3_code)

    current_app.logger.info(f"Query: {query}")
    res = es.search(
        index='twitter',
        query=json.loads(query),
        aggregations={
            "avg_sentiment" : {
                "avg": {
                    "field": "sentiment"
                    }
            }
        }
    )
    return res


@current_app.route('/twitter/avgsentiment/sa3', methods=['GET'])
def main():
    """
    Main function to retrieve the avg sentiment data.
    Method : GET
    :return:
    """
    current_app.logger.setLevel("INFO")
    try:
        sa3_code = request.headers['X-Fission-Params-SA3Code']
    except KeyError:
        current_app.logger.info("SA3 Code not provided")
        sa3_code = None

    try:
        start_date = request.headers['X-Fission-Params-StartDate']
        end_date = request.headers['X-Fission-Params-EndDate']
    except KeyError:
        current_app.logger.info("Date not provided")
        start_date = None
        end_date = None
    es = setup_connection()
    data = get_twitter_sentiment(es, sa3_code, start_date, end_date)
    return json.dumps(data["aggregations"])
