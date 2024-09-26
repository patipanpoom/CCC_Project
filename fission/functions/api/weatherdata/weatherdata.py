# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function provides an api to retrieve the weather data
 from the Elasticsearch server.
"""
import base64
import json
import warnings
from datetime import datetime

from elasticsearch8 import Elasticsearch, AuthenticationException
from flask import current_app, request

warnings.filterwarnings("ignore")


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


def get_weather_data(es, start_date=None,
                     end_date=None):
    # pylint: disable=duplicate-code
    """
    Get the Avg weather data from the Elasticsearch server.
    :param es: Elasticsearch connection object
    :param start_date: start date
    :param end_date: end date
    :return: res: JSON response from the Elasticsearch server
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is not None:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": f"{start_date}T00:00:00",
                        "lte": f"{end_date}T23:59:59"
                    }
                }
            }
        }
    else:
        query = {
            "query": {
                "match_all": {}
            }
        }
    agg_query = {
        "sites": {
            "terms": {
                "size": 10000,  # pylint: disable=duplicate-code
                "field": "siteid"
            },
            "aggs": {
                "site_info": {
                    "top_hits": {
                        "size": 1,
                        "_source": ["siteid", "sitename", "geo"]
                    }
                },
                "daily_avg_temp": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "day"
                    },
                    "aggs": {
                        "avg_temp": {
                            "avg": {
                                "field": "airtemp.float"
                            }
                        }
                    }
                }
            }
        }
    }

    current_app.logger.info(f"Query: {query}")
    res = es.search(
        index='weather',
        body=query,
        aggregations=agg_query
    )
    return res


def main():
    """
    Main function to retrieve the avg weather data.
    Method : GET
    :return:
    """
    current_app.logger.setLevel("INFO")
    try:
        start_date = request.headers['X-Fission-Params-StartDate']
    except KeyError:
        current_app.logger.info("Start date not provided")
        start_date = None
    try:
        end_date = request.headers['X-Fission-Params-EndDate']
    except KeyError:
        end_date = None

    try:
        es = setup_connection()
        data = get_weather_data(es, start_date, end_date)
        json_data = {
            "hits": data['hits']['hits'],
            "aggregations": data['aggregations']
        }
        return json.dumps(json_data)
    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return json.dumps({"error": f"Error: {e}"}), 500
