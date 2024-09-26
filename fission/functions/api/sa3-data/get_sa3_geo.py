# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function provides an api to retrieve the sa3 geometry
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

MAX_SIZE = 10000
# GEOJSON template object 
geojson_temp = Template('''
                        {
                        "id": "${index}",
                        "type": "Feature", 
                        "properties": ${props}, 
                        "geometry": ${geometry}
                        }
                        ''')

def get_sa3_geojson(es):
    # pylint: disable=duplicate-code
    """
    Get the SA3 Geometry data from the Elasticsearch server.
    :param es: Elasticsearch connection object
    :return: res: GEOJSON representation of SA3 geometries.
    """

    query = '''
            {
            "match_all": {}
            }
        '''
            
    res = es.search(
        index='sa3',
        query=json.loads(query),
        size=10000
    )
    data = res
    start = "["
    for i, record in enumerate(data["hits"]["hits"]):
        geometry = json.dumps(record["_source"]["geometry"])
        del record["_source"]["geometry"]
        props = json.dumps(record["_source"])
        start += geojson_temp.substitute(index=i, props=props, geometry=geometry)
        if i != len(data["hits"]["hits"]) - 1:
            start += ','
    start += "]"
    return json.loads(start)



def main():
    """
    Main function to retrieve the SA3 geometry
    Method : GET
    :return:
    """
    # current_app.logger.setLevel("INFO")
    es = setup_connection()
    data = get_sa3_geojson(es)
    return json.dumps(data)

