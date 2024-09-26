# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function retrieves the Mortality Fertility data from the Elasticsearch server.
"""
import base64
import warnings
from flask import current_app, request, jsonify
from elasticsearch8 import Elasticsearch, AuthenticationException

warnings.filterwarnings("ignore")


def config(k):
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
    es_url = config("ES_URL")
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


def get_sudo_data(es, geo_point=None):
    """
    Get the Mortality Fertility data from the Elasticsearch server.
    :param es: Elasticsearch connection object
    :param geo_point: Geo point to filter the data
    :return: res: JSON response from the Elasticsearch server
    """
    query = {}
    if geo_point is not None:
        query = {
            "query": {
                "bool": {
                    "must": [{
                        "geo_shape":
                            {
                                "geometry": {
                                    "shape": geo_point,
                                    "relation": "intersects"
                                }}
                    }]
                }
            },
            "_source": ["area_code",
                        "area_name",
                        "M0_tfr_184",
                        "geometry",
                        "dth_bst_00",
                        "dth_cop_05",
                        "dth_dia_10",
                        "dths_can15",
                        "dths_cer20",
                        "dths_cir25",
                        "dths_col30",
                        "dths_ext35",
                        "dths_f_040",
                        "dths_isc45",
                        "dths_lun50",
                        "dths_m_055",
                        "dths_res60",
                        "dths_rti65",
                        "dths_sui70",
                        "dths_tot75"]
        }
    else:
        query = {
            "size": 10000,
            "query": {
                "match_all": {}
            },
            "_source": ["area_code",
                        "area_name",
                        "M0_tfr_184",
                        "geometry",
                        "dth_bst_00",
                        "dth_cop_05",
                        "dth_dia_10",
                        "dths_can15",
                        "dths_cer20",
                        "dths_cir25",
                        "dths_col30",
                        "dths_ext35",
                        "dths_f_040",
                        "dths_isc45",
                        "dths_lun50",
                        "dths_m_055",
                        "dths_res60",
                        "dths_rti65",
                        "dths_sui70",
                        "dths_tot75"]
        }

    current_app.logger.info(f"Query: {query}")
    res = es.search(index='mortality-fertility-data', body=query)
    return res


def main():
    """
    Main function to retrieve the Mortality fertility data.
    Method : GET
    :return:
    """
    current_app.logger.setLevel("INFO")
    try:
        lat = request.headers['X-Fission-Params-Lat']
        long = request.headers['X-Fission-Params-Long']
        # Define the geo_point if provided
        geo_point = {"type": "point", "coordinates": [float(long), float(lat)]}
    except KeyError:
        geo_point = None

    try:
        es = setup_connection()
        if geo_point is not None:
            current_app.logger.info("Getting data with geo_point")
            data = get_sudo_data(es, geo_point)
        else:
            current_app.logger.info("Getting data without geo_point")
            data = get_sudo_data(es)

        response = jsonify(data['hits']['hits'])
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

        return response
    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
