# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function retrieves the sorted Mortality Fertility data
from the Elasticsearch server.
"""
import base64
import warnings
from flask import current_app, request, jsonify, make_response
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


def get_sorted_results(es, attribute: str):
    """
    Get the sorted results based on the user provided parameter.
    :param es: Elasticsearch connection object
    :param attribute: User provided parameter
    :return: JSON response from the Elasticsearch server
    """
    current_app.logger.info(f"Attribute: {attribute}")
    query = {
        "size": 7,
        "sort": [
            {
                attribute: {
                    "order": "desc"
                }
            }
        ],
        "_source": [
            "area_code",
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
            "dths_tot75"
        ],
        "query": {
            "match_all": {}
        }
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
    if request.method == 'OPTIONS':
        current_app.logger.info("OPTIONS Request")
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response
    elif request.method == 'GET':
        current_app.logger.info("GET Request")
        try:
            whitelist_attributes = ["dth_bst_00",
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
            attribute = request.headers['X-Fission-Params-Attribute']
            # verify the attribute is in the list of attributes
            if attribute not in whitelist_attributes:
                raise KeyError
            else:
                es = setup_connection()
                data = get_sorted_results(es, attribute)
                response = jsonify(data['hits']['hits'])
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
        except KeyError:
            current_app.logger.error("No matching attribute found in the request headers")
            return jsonify({"Error": "No matching attribute found in the request headers"}), 400
        except Exception as e:
            current_app.logger.error(f"Error: {e}")
            return jsonify({"Error": "Internal Server Error"}), 500
