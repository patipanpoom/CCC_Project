# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
Health function to check the health of the Elasticsearch cluster.
"""

import requests
from flask import request, current_app


def main():
    """
    Main function to get the health of the Elasticsearch cluster.
    :return:
    """
    current_app.logger.info(f"Received request: ${request.headers}")
    r = requests.get(
        "https://elasticsearch-master.elastic.svc.cluster.local:9200/_cluster/health",
        verify=False,
        auth=("elastic", "elastic"),
        timeout=30,
    )
    current_app.logger.info(f"Status ES request: {r.status_code}")
    return r.json()
