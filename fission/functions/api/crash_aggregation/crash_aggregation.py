# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function provides an api to make custom aggregations of the joined crash and sa2 datasets.
"""
import base64
import json
import warnings

from elasticsearch8 import Elasticsearch, AuthenticationException
from flask import request

warnings.filterwarnings("ignore")

AGGREGATION_MAX_SIZE = 2147483647
AGGREGATIONS = [
    "avg",
    "max",
    "min",
    "boxplot",
    "extended_stats",
    "percentiles",
    "stats",
    "sum",
    "value_count",
]

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


def get_aggregation(es: Elasticsearch, by_field: str, aggregations: list) -> dict:
    """
    Sends an aggregation query to the joined crash and sa2 index based on the parameters supplied.
    The dataset will first be grouped by the field specified with the by_field parameter.
    Optionally, further aggregations can be made within these groupings as specified by list of
    aggregation/term pairs given in the aggregations parameter.
    """
    aggregations_query = {
        "by": {
            "terms": {
                "field": by_field,
                "size": AGGREGATION_MAX_SIZE
            }
        }
    }

    if aggregations:
        aggregations_query["by"]["aggs"] = \
            {field: {aggregation: {"field": field}} for aggregation, field in aggregations}

    response = es.search(
        index="crash_sa2_joined",
        aggregations=aggregations_query
    )

    buckets = response["aggregations"]["by"]["buckets"]
    return [parse_aggregation_bucket(bucket, by_field, aggregations) for bucket in buckets]


def parse_aggregation_bucket(bucket: dict, by_field: str, aggregations: list) -> dict:
    """
    This function parses the bucket dictionaries returned by the aggregation query into
    a flatter structure without unnecessary data.
    """
    output = {field: bucket[field]["value"] for _, field in aggregations}
    output["count"] = bucket["doc_count"]
    output[by_field] = bucket["key"]

    return output


def get_mapping(es: Elasticsearch) -> dict:
    """
    Gets the mapping of the crash_sa2_joined index.
    """
    response = es.indices.get_mapping(
        index="crash_sa2_joined",
    )

    return response["crash_sa2_joined"]["mappings"]


def extract_fields(mapping, prefix=""):
    """
    Extracts the terms from a mapping dict. Nested terms are joined by periods into a single string.
    """
    terms = []
    for key, value in mapping.items():
        if "properties" in value:
            new_prefix = f"{prefix}{key}." if prefix else f"{key}."
            terms.extend(extract_fields(value["properties"], new_prefix))
        else:
            terms.append(f"{prefix}{key}")

    return terms


def main():
    """
    Main function for the crash aggregation endpoint.
    """
    by_field = request.headers.get('X-Fission-Params-By-Field')
    if by_field == "sa2":
        by_field = "sa2.properties.sa2_main11.keyword"

    aggregations = []

    aggregation = request.headers.get('X-Fission-Params-Aggregation')
    field = request.headers.get('X-Fission-Params-Aggregation-Field')
    if aggregation and field:
        aggregations.append((aggregation, field))

    with_aggregation = request.headers.get('X-Fission-Params-With-Aggregation')
    with_field = request.headers.get('X-Fission-Params-With-Aggregation-Field')
    if with_aggregation and with_field:
        aggregations.append((with_aggregation, with_field))

    for aggregation, _ in aggregations:
        if aggregation not in AGGREGATIONS:
            return json.dumps({
                "error": f"Unknown aggregation type {aggregation}"
            }), 400

    es = setup_connection()
    mapping = get_mapping(es)
    fields = extract_fields(mapping["properties"])

    for _, field in aggregations:
        if field not in fields:
            return json.dumps({
                "error": f"Unknown mapping field {field}"
            }), 400

    data = get_aggregation(es, by_field, aggregations)
    return json.dumps(data)
