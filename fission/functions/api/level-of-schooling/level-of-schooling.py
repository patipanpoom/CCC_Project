# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function provides an api to retrieve the median income or age sa3 data
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


def get_education(es, sa3_code=None):
    # pylint: disable=duplicate-code
    """
    Get the Avg weather data from the Elasticsearch server.
    :param es: Elasticsearch connection object
    :param sa3_code: SA3 Code
    :return: res: JSON response from the Elasticsearch server
    """

    if sa3_code is not None:
        query = sa3_expr.substitute(sa3_code=sa3_code)

    current_app.logger.info(f"Query: {query}")
    res = es.search(
        index='school_sa3',
        query=json.loads(query),
    )
    return res


@current_app.route('/level-of-schooling/', methods=['GET'])
def main():
    """
    Main function to retrieve the avg weather data.
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
    
    data = get_education(es, sa3_code)

    num_persons = data["hits"]["hits"][0]["_source"]["p_y12e_tot"] + \
        data["hits"]["hits"][0]["_source"]["p_y11e_tot"] + \
        data["hits"]["hits"][0]["_source"]["p_y10e_tot"] + \
        data["hits"]["hits"][0]["_source"]["p_y9e_tot"]
    
    avg_person = (12 * data["hits"]["hits"][0]["_source"]["p_y12e_tot"]/num_persons) + \
        (11 * data["hits"]["hits"][0]["_source"]["p_y11e_tot"]/num_persons) + \
        (10 * data["hits"]["hits"][0]["_source"]["p_y10e_tot"]/num_persons) + \
        (9 * data["hits"]["hits"][0]["_source"]["p_y9e_tot"]/num_persons) 

    num_males = data["hits"]["hits"][0]["_source"]["m_y12e_tot"] + \
        data["hits"]["hits"][0]["_source"]["m_y11e_tot"] + \
        data["hits"]["hits"][0]["_source"]["m_y10e_tot"] + \
        data["hits"]["hits"][0]["_source"]["m_y9e_tot"] + \
        data["hits"]["hits"][0]["_source"]["m_y8b_tot"] + \
        data["hits"]["hits"][0]["_source"]["m_dngts_tot"]
    
    avg_male = (12 * data["hits"]["hits"][0]["_source"]["m_y12e_tot"]/num_males) + \
        (11 * data["hits"]["hits"][0]["_source"]["m_y11e_tot"]/num_males) + \
        (10 * data["hits"]["hits"][0]["_source"]["m_y10e_tot"]/num_males) + \
        (9 * data["hits"]["hits"][0]["_source"]["m_y9e_tot"]/num_males) + \
        (8 * data["hits"]["hits"][0]["_source"]["m_y8b_tot"]/num_males) + \
        (0 * data["hits"]["hits"][0]["_source"]["m_dngts_tot"]/num_males)
    
    num_females = data["hits"]["hits"][0]["_source"]["f_y12e_tot"] + \
        data["hits"]["hits"][0]["_source"]["f_y11e_tot"] + \
        data["hits"]["hits"][0]["_source"]["f_y10e_tot"] + \
        data["hits"]["hits"][0]["_source"]["f_y9e_tot"] + \
        data["hits"]["hits"][0]["_source"]["f_y8b_tot"] + \
        data["hits"]["hits"][0]["_source"]["f_dngts_tot"]
    
    avg_female = (12 * data["hits"]["hits"][0]["_source"]["f_y12e_tot"]/num_females) + \
        (11 * data["hits"]["hits"][0]["_source"]["f_y11e_tot"]/num_females) + \
        (10 * data["hits"]["hits"][0]["_source"]["f_y10e_tot"]/num_females) + \
        (9 * data["hits"]["hits"][0]["_source"]["f_y9e_tot"]/num_females) + \
        (8 * data["hits"]["hits"][0]["_source"]["f_y8b_tot"]/num_females) + \
        (0 * data["hits"]["hits"][0]["_source"]["f_dngts_tot"]/num_females)
    data["hits"]["hits"][0]["_source"]["avg_education"] = {"male" : avg_male, "female": avg_female, "person": avg_person}
    return json.dumps(data["hits"]["hits"][0]["_source"])
