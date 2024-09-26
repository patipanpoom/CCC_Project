# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
Test file for testing the weather harvester function.
"""
import json
import unittest
from unittest.mock import patch, MagicMock

from flask import Flask

from fission.functions import wharvester


class TestWeatherHarvester(unittest.TestCase):
    """
    Test class for the weather harvester function.
    """

    def setUp(self):
        """
        Set up the test.
        :return:
        """
        app = Flask(__name__)
        self.app_context = app.app_context()
        self.app_context.push()
        wharvester.Observations = ["94839"]

    def tearDown(self):
        """
        Tear down the test.
        :return:
        """
        self.app_context.pop()

    @patch("fission.functions.wharvester.requests.post")
    @patch("fission.functions.wharvester.requests.get")
    @patch("fission.functions.wharvester.config")
    def test_wharvester(self, mock_config, mock_get, mock_post):
        """
        Test the weather harvester function.
        """
        # Mock the response from the BOM API.
        with self.app_context:
            mock_config.side_effect = lambda k: "https://www.bom.gov.au/fwo/"
            mock_get.return_value = MagicMock()
            mock_get.return_value.json.return_value = {
                "observations": {
                    "data": [
                        {
                            "wmo": 94839,
                            "name": "Test location",
                            "lat": -33.86,
                            "lon": 151.21,
                            "local_date_time_full": "20210412150000",
                            "air_temp": 23.0,
                            "dewpt": 15.0,
                            "rel_hum": 60,
                            "vis_km": 10,
                            "weather": "Clear",
                            "wind_dir": "N",
                            "wind_spd_kmh": 20,
                            "cloud": "Clear",
                            "rain_trace": "0.0"
                        }
                    ]
                }
            }

            expected_data = {
                "siteid": 94839,
                "sitename": "Test location",
                "geo": "-33.86,151.21",
                "timestamp": "2021-04-12T15:00:00Z",
                "airtemp": "23.0",
                "dewpt": "15.0",
                "realhum": "60",
                "vis": 10,
                "weather": "Clear",
                "winddir": "N",
                "windspd": 20,
                "cloud": "Clear",
                "raintrace": "0.0"
            }

            mock_post.return_value = MagicMock(status_code=201)
            result = wharvester.main()

            # Assertions
            self.assertEqual(result, "OK")

            # Check if config function is called with the expected URL
            mock_config.assert_called_once_with("BOM_BASE_URL")

            mock_get.assert_called_once_with("https://www.bom.gov.au/fwo/94839.json",
                                             timeout=10)

            mock_post.assert_called_once_with(
                url="http://router.fission/enqueue/weather",
                headers={"Content-Type": "application/json"},
                data=json.dumps(expected_data),
                timeout=10,
            )

    @patch("fission.functions.wharvester.config")
    @patch("fission.functions.wharvester.requests.get")
    def test_wharvester_exception(self, mock_get, mock_config):
        """
        Test the weather harvester function when an exception is raised.
        """
        # Mock the response from the BOM API.
        with self.app_context:
            mock_config.side_effect = lambda k: "https://www.bom.gov.au/fwo/"
            mock_get.return_value.json.side_effect = Exception("Test exception")
            result = wharvester.main()

            # Assertions
            self.assertEqual(result, "OK")
            mock_get.assert_called_with("https://www.bom.gov.au/fwo/94839.json", timeout=10)


if __name__ == "__main__":
    unittest.main()
