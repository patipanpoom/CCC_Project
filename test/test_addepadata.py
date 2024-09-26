# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
Test the Add EPA Data function.
"""
import unittest
from unittest.mock import patch, MagicMock

from flask import Flask
from fission.functions.addepadata import addepadata


class TestAddEPAData(unittest.TestCase):
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

    @patch("fission.functions.addepadata.addepadata.secret")
    @patch("fission.functions.addepadata.addepadata.config")
    @patch("fission.functions.addepadata.addepadata.request")
    @patch("fission.functions.addepadata.addepadata.Elasticsearch")
    def test_addepadata(self, mock_es, mock_request, mock_config, mock_secret):
        """
        Test the add epa data function.
        :return:
        """
        mock_config.side_effect = lambda k: "https://es:9200"
        mock_secret.side_effect = lambda k: "dummy-secret"
        # Mock the Elasticsearch client
        mock_client = MagicMock()
        mock_es.return_value = mock_client
        mock_request.get_json = MagicMock(return_value={
            "siteid": "dummy-siteid",
            "timestamp": "dummy-timestamp",
        })
        result = addepadata.main()

        mock_client.index.assert_called_once_with(
            index="epadata",
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
