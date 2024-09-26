# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This module contains shared mock objects and behaviors for use in unit tests.
"""
from unittest.mock import MagicMock


# Shared mock behaviors
def mock_shared_url(key):
    """
    Mock the shared URL.
    :param key:
    :return:
    """
    return "https://dummyurl:9200"


def mock_shared_secret(key):
    """
    Mock the shared secret.
    :param key:
    :return:
    """
    return "dummy-secret"


# Mocks for Flask objects
mock_request = MagicMock()
mock_current_app = MagicMock()
