# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function joins the twitter and sa3 datasets
based on an intersection query of their geometry.
"""
import base64
import warnings

from elasticsearch8 import Elasticsearch, AuthenticationException
from elasticsearch8.helpers import bulk

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
                                   password),
                        timeout=30, 
                        retry_on_timeout=True
                    )

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


def get_twitter(es: Elasticsearch) -> dict:
    """
    Retrieves all twitter groupby sa3_code_2021 and agg sentiment documents from Elasticsearch.
    """
    twitter_response = es.search(
        index="twitter",
        body = {
            "aggs": {
                "group_by_sa3_code_2021": {
                    "terms": {
                        "field": "sa3_code_2021",
                        "size": 10000
                    },
                    "aggs": {
                        "average_sentiment": {
                            "avg": {
                                "field": "sentiment"
                            }
                        }
                    }
                }
            }
        }
    )
    hits = twitter_response["aggregations"]["group_by_sa3_code_2021"]["buckets"]
    return {hit['key']: {'average_sentiment': hit['average_sentiment']['value'], 'twitter_count':hit['doc_count']} for hit in hits}


def get_school_sa3(es: Elasticsearch) -> dict:
    """
    Retrieves sudo highest education documents from Elasticsearch.
    """
    size = es.count(index="school_sa3")["count"]

    school_sa3_response = es.search(
        index="school_sa3",
        size=size,
    )

    hits = school_sa3_response["hits"]["hits"]
    return {hit['_source']['sa3_code_2021']: {key:value for key,value in hit['_source'].items() if key != 'sa3_code_2021'} for hit in hits}

def get_person_age_sex_sa3(es: Elasticsearch) -> dict:
    """
    Retrieves sudo population documents from Elasticsearch.
    """
    size = es.count(index="person_age_sex_sa3")["count"]

    person_age_sex_sa3_response = es.search(
        index="person_age_sex_sa3",
        size=size,
    )

    hits = person_age_sex_sa3_response["hits"]["hits"]
    return {hit['_source']['sa3_code_2021']: {key:value for key,value in hit['_source'].items() if key != 'sa3_code_2021'} for hit in hits}

def get_age_personal_income_sa3(es: Elasticsearch) -> dict:
    """
    Retrieves sudo personal income documents from Elasticsearch.
    """
    size = es.count(index="age_personal_income_sa3")["count"]

    age_personal_income_sa3_response = es.search(
        index="age_personal_income_sa3",
        size=size,
    )

    hits = age_personal_income_sa3_response["hits"]["hits"]
    return {hit['_source']['sa3_code_2021']: {key:value for key,value in hit['_source'].items() if key != 'sa3_code_2021'} for hit in hits}
    
def main():
    # pylint: disable=duplicate-code
    """f
    Main function to join the twitter and sudo sa3 datasets.
    Method : GET
    :return:
    """
    es = setup_connection()

    twitter = get_twitter(es)
    school_sa3 = get_school_sa3(es)
    person_age_sex_sa3 = get_person_age_sex_sa3(es)
    age_personal_income_sa3 = get_age_personal_income_sa3(es)
    join_data = []
    for sa3_code_2021, value in school_sa3.items():
        out = {}
        out["sa3_code_2021"] = sa3_code_2021
        if sa3_code_2021 in twitter:
            out["average_sentiment"] = twitter[sa3_code_2021]['average_sentiment']
            out['twitter_count'] = twitter[sa3_code_2021]['twitter_count']
        out['school_sa3'] = value
        out['person_age_sex_sa3'] = person_age_sex_sa3[sa3_code_2021]
        out['age_personal_income_sa3'] = age_personal_income_sa3[sa3_code_2021]
        join_data.append(out)

    bulk(
        client=es,
        index="sa3_join",
        actions=join_data
    )
    return "ok"

if __name__ == "__main__":
    main()