# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
Test module for the Add Weather Data function.
"""
import unittest
from unittest.mock import patch, MagicMock
from test.mockconfig import mock_shared_secret, mock_shared_url
from flask import Flask
from fission.functions.addweatherdata import addweatherdata




class TestAddWeatherData(unittest.TestCase):
    """
    Test class for the Add Weather Data function.
    """

    def setUp(self):
        """
        Set up the test.
        :return:
        """
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app.test_request_context().push()
        # self.app_context.push()

    def tearDown(self):
        """
        Tear down the test.
        :return:
        """
        # self.app_context.pop()
        # self.app.test_request_context().pop()

    @patch("fission.functions.addweatherdata.addweatherdata.secret")
    @patch("fission.functions.addweatherdata.addweatherdata.config")
    @patch("fission.functions.addweatherdata.addweatherdata.request")
    @patch("fission.functions.addweatherdata.addweatherdata.Elasticsearch")
    def test_addweatherdata(self, mock_es, mock_request, mock_config, mock_secret):
        """
        Test the add weather data function.
        :return:
        """
        mock_config.side_effect = mock_shared_url(key="elasticsearch_url")
        mock_secret.side_effect = mock_shared_secret(key="username")
        # Mock the Elasticsearch client
        mock_client = MagicMock()
        mock_es.return_value = mock_client

        mock_request.get_json = MagicMock(return_value={
            "siteid": "dummy-siteid",
            "timestamp": "dummy-timestamp",
        })
        result = addweatherdata.main()

        mock_client.index.assert_called_once_with(
            index="weather",
            id="dummy-siteid-dummy-timestamp",
            body={
                "siteid": "dummy-siteid",
                "timestamp": "dummy-timestamp"
            }
        )
        # Assert the result
        self.assertEqual(result, "ok")


if __name__ == "__main__":
    unittest.main()
