# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function joins the crash and sa2 datasets based on an intersection query of their geometry.
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


def crash_sa2_join_config(k):
    # pylint: disable=duplicate-code
    """
    :param k: Key value for the configuration.
    :return: value of the key.
    """
    with open(f"/configs/default/crash-sa2-join-data/{k}", "r", encoding="utf-8") as f:
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


def get_sa2s(es: Elasticsearch) -> dict:
    """
    Retrieves all sa2 documents from Elasticsearch without the geometry field.
    """
    size = es.count(index="sa2_data")["count"]

    sa2_response = es.search(
        index="sa2_data",
        size=size,
        _source={
            "excludes": ["geometry"]
        }
    )

    hits = sa2_response["hits"]["hits"]
    return {document["_id"]: document["_source"] for document in hits}


def get_health_risks(es: Elasticsearch) -> dict:
    """
    Retrieves all health risk documents from Elasticsearch.
    """
    size = es.count(index="health_risks_data")["count"]

    health_risks_response = es.search(
        index="health_risks_data",
        size=size,
    )

    hits = health_risks_response["hits"]["hits"]
    return {str(document["_source"]["area_code"]): document["_source"] for document in hits}


def get_crashes_inside_sa2(es: Elasticsearch, sa2_id: str):
    """
    Retrieves all crashes with a geopoint that intersects with the geometry of the given sa2.
    """
    page_size = int(crash_sa2_join_config("CRASHES_PAGE_SIZE"))

    crashes_initial_response = es.search(
        index="crash_data",
        query={
            "bool": {
                "filter": {
                    "geo_shape": {
                        "geometry": {
                            "indexed_shape": {
                                "index": "sa2_data",
                                "id": sa2_id,
                                "path": "geometry"
                            }
                        }
                    }
                }
            }
        },
        size=page_size,
        scroll="1m"
    )

    scroll_id = crashes_initial_response["_scroll_id"]
    documents = crashes_initial_response["hits"]["hits"]

    while True:
        crashes_scroll_response = es.scroll(scroll_id=scroll_id)
        scroll_documents = crashes_scroll_response["hits"]["hits"]
        documents.extend(scroll_documents)

        if len(scroll_documents) < page_size:
            break

    es.clear_scroll(scroll_id=scroll_id)

    return [document["_source"] for document in documents]


def create_joined_index(es: Elasticsearch):
    """
    Creates or recreates a new Elasticsearch index to store the joined crash and sa2 dataset.
    """
    if es.indices.exists(index="crash_sa2_joined"):
        es.indices.delete(index="crash_sa2_joined")

    es.indices.create(
        index="crash_sa2_joined",
        mappings={
            "properties": {
                "geometry": {
                    "type": "geo_point"
                }
            }
        }
    )


def upload_crashes_joined(es: Elasticsearch, crashes: list, sa2: dict, health_risks: dict):
    """
    Bulk uploads a list of crash documents joined with a specified sa2 document to the new index.
    """
    documents = [{**crash, **{"sa2": sa2}, **{"health_risks": health_risks}} for crash in crashes]

    bulk(
        client=es,
        index="crash_sa2_joined",
        actions=documents
    )


def main():
    """
    Main function to spatially join the crash and sa2 datasets.
    """
    es = setup_connection()

    sa2s = get_sa2s(es)
    sa2_health_risks = get_health_risks(es)
    create_joined_index(es)

    for sa2_id, sa2 in sa2s.items():
        crashes = get_crashes_inside_sa2(es, sa2_id)

        sa2_code = sa2["properties"]["sa2_main11"]
        health_risks = sa2_health_risks.get(sa2_code)

        upload_crashes_joined(es, crashes, sa2, health_risks)

    return "ok"
