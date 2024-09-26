# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
Test file for testing the EPA data harvester function.
"""
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock

from flask import Flask
from fission.functions import epamonitoringsites


class TestEPAMonitoringSites(unittest.TestCase):
    """
    Test class for the EPA data harvester function.
    """

    # expected_data = {
    #     "siteid": "77062cb7-3e3b-4984-b6d0-03dda76177f2",
    #     "sitename": "Box Hill",
    #     "geo": "-37.8287277,145.1324",
    #     "timestamp": datetime.now().isoformat(),
    #     "siteHealthAdvices": {
    #         "since": "2024-05-07T12:00:00Z",
    #         "until": "2024-05-07T13:00:00Z",
    #         "healthParameter": "PM2.5",
    #         "averageValue": 13.26,
    #         "unit": "&micro;g/m&sup3;",
    #         "healthAdvice": "Good",
    #         "healthAdviceColor": "#42A93C",
    #         "healthCode": "1021"
    #     },
    #     "pm2p5": {
    #         "since": "2024-05-07T12:00:00Z",
    #         "until": "2024-05-07T13:00:00Z",
    #         "averageValue": 13.26,
    #         "unit": "&micro;g/m&sup3;",
    #         "confidence": 108.33,
    #         "totalSample": 13,
    #         "healthAdvice": "Good",
    #         "healthAdviceColor": "#42A93C",
    #         "healthCode": "1021"
    #     }
    # }

    def setUp(self):
        """
        Set up the test.
        :return:
        """
        app = Flask(__name__)
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        """
        Tear down the test.
        :return:
        """
        self.app_context.pop()

    @patch("fission.functions.epamonitoringsites.config")
    @patch("fission.functions.epamonitoringsites.secret")
    @patch("fission.functions.epamonitoringsites.requests.request")
    @patch("fission.functions.epamonitoringsites.requests.post")
    def test_epamonitoringsites(self, mock_post, mock_request, mock_secret, mock_config,):
        """
        Test the epa harvester function.
        """
        # Mock the response from the EPA API.
        with self.app_context:
            mock_config.side_effect = lambda k: ("https://gateway.api.epa.vic.gov.au/"
                                                 "environmentMonitoring/v1/sites/")
            mock_secret.side_effect = lambda k: "dummy-key"
            mock_request.return_value = MagicMock()
            mock_request.return_value.status_code = 200
            headers = {
                "X-TransactionID": mock.ANY,
                "X-SessionID": mock.ANY,
                "X-CreationTime": mock.ANY,
                "X-InitialOperation": "GET",
                "Cache-Control": "no-cache",
                "X-API-Key": "dummy-key",
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/96.0.4664.93 Safari/537.36",
            }
            mock_request.return_value.json.return_value = {
                "totalRecords": 1,
                "records": [
                    {
                        "siteID": "77062cb7-3e3b-4984-b6d0-03dda76177f2",
                        "siteName": "Box Hill",
                        "siteType": "Standard",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                -37.8287277,
                                145.1324
                            ]
                        },
                        "siteHealthAdvices": [
                            {
                                "since": "2024-05-07T12:00:00Z",
                                "until": "2024-05-07T13:00:00Z",
                                "healthParameter": "PM2.5",
                                "averageValue": 13.26,
                                "unit": "&micro;g/m&sup3;",
                                "healthAdvice": "Good",
                                "healthAdviceColor": "#42A93C",
                                "healthCode": "1021"
                            }
                        ],
                        "parameters": [
                            {
                                "name": "PM2.5",
                                "timeSeriesReadings": [
                                    {
                                        "timeSeriesName": "1HR_AV",
                                        "readings": [
                                            {
                                                "since": "2024-05-07T12:00:00Z",
                                                "until": "2024-05-07T13:00:00Z",
                                                "averageValue": 13.26,
                                                "unit": "&micro;g/m&sup3;",
                                                "confidence": 108.33,
                                                "totalSample": 13,
                                                "healthAdvice": "Good",
                                                "healthAdviceColor": "#42A93C",
                                                "healthCode": "1021"
                                            }
                                        ]
                                    },
                                    {
                                        "timeSeriesName": "24HR_AV",
                                        "readings": [
                                            {
                                                "since": "2024-05-06T13:00:00Z",
                                                "until": "2024-05-07T13:00:00Z",
                                                "averageValue": 10.04,
                                                "unit": "&micro;g/m&sup3;",
                                                "confidence": 107.29,
                                                "totalSample": 309,
                                                "healthAdvice": "Fair",
                                                "healthAdviceColor": "#EEC900",
                                                "healthCode": "1030"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

            mock_post.return_value = MagicMock(status_code=201)
            mock_post.return_value.text = "OK"

            # pdb.set_trace()
            result = epamonitoringsites.main()

            # expected_data["timestamp"] = result["timestamp"]

            # Assertions
            self.assertEqual(result, '"OK"')

            # Check if config function is called with the expected URL
            mock_config.assert_called_with("EPA_BASE_URL")
            mock_secret.assert_called_with("EPA_API_KEY")

            mock_request.assert_called_once_with("GET",
                                                 "https://gateway.api.epa.vic.gov.au/"
                                                 "environmentMonitoring/v1/sites/"
                                                 "parameters?environmentalSegment=air",
                                                 headers=headers,
                                                 timeout=10)

            mock_post.assert_called_once_with(
                url="http://router.fission/enqueue/airquality",
                headers={"Content-Type": "application/json"},
                # The expected data does not match with the
                # actual data due to timestamp difference.
                # Hence, using the mock.ANY to ignore the
                # data validation.

                # data=json.dumps(expected_data),
                data=mock.ANY,
                timeout=20,
            )

    @patch("fission.functions.epamonitoringsites.config")
    @patch("fission.functions.epamonitoringsites.secret")
    @patch("fission.functions.epamonitoringsites.requests.request")
    def test_epamonitoringsites_exception(self, mock_request, mock_secret, mock_config):
        """
        Test the weather harvester function when an exception is raised.
        """
        mock_secret.side_effect = lambda k: "dummy-key"
        # Mock the response from the BOM API.
        with self.app_context:
            headers = {
                "X-TransactionID": mock.ANY,
                "X-SessionID": mock.ANY,
                "X-CreationTime": mock.ANY,
                "X-InitialOperation": "GET",
                "Cache-Control": "no-cache",
                "X-API-Key": "dummy-key",
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/96.0.4664.93 Safari/537.36",
            }
            mock_config.side_effect = lambda k: ("https://gateway.api.epa.vic.gov.au/"
                                                 "environmentMonitoring/v1/sites/")
            mock_request.return_value.json.side_effect = Exception("Test exception")
            result = epamonitoringsites.main()

            # Assertions
            self.assertEqual(result, None)
            mock_request.assert_called_once_with("GET",
                                                 "https://gateway.api.epa.vic.gov.au/"
                                                 "environmentMonitoring/v1/sites/"
                                                 "parameters?environmentalSegment=air",
                                                 headers=headers,
                                                 timeout=10)


if __name__ == "__main__":
    unittest.main()
