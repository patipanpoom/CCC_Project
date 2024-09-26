# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This module contains the test cases for the weather data API module.
"""
import unittest

from unittest import mock
from unittest.mock import patch, MagicMock
from test.mockconfig import mock_shared_url, mock_shared_secret
from flask import Flask
from fission.functions.api.weatherdata import weatherdata






class TestWeatherData(unittest.TestCase):
    """
    This class contains the test cases for the weatherdata API module.
    """

    def setUp(self):
        """
        Set up the test.
        :return:
        """
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app.test_request_context().push()

    def tearDown(self):
        """
        Tear down the test.
        :return:
        """

    @patch('fission.functions.api.weatherdata.weatherdata.datetime')
    @patch('fission.functions.api.weatherdata.weatherdata.current_app')
    @patch("fission.functions.api.weatherdata.weatherdata.shared_config")
    @patch("fission.functions.api.weatherdata.weatherdata.secret")
    def test_get_weather_data_default_dates(self, mock_secret,
                                            mock_shared_config, mock_current_app,
                                            mock_datetime):
        """
        Test the get_epa_data function with default dates.
        :param mock_current_app:
        :param mock_datetime:
        :return:
        """
        with self.app_context:
            # Mock current date
            mock_shared_config.side_effect = lambda k: "https://es:9200"
            mock_secret.side_effect = lambda k: "dummy-secret"
            mock_datetime.now.return_value.strftime.return_value = "2024-05-10"

            # Mock Elasticsearch connection and logger
            mock_es = MagicMock()
            mock_current_app.logger = MagicMock()
            # Call the function with default dates
            weatherdata.get_weather_data(mock_es)

            # Check if the query is constructed correctly
            expected_query = {
                "query": {"match_all": {}}
            }
            mock_current_app.logger.info.assert_called_once_with(f"Query: {expected_query}")
            # mock_es.search = MagicMock(return_value=mock.ANY)
            mock_es.search.assert_called_once_with(index='weather',
                                                   body=expected_query,
                                                   aggregations=mock.ANY)

    @patch('fission.functions.api.weatherdata.weatherdata.current_app')
    @patch("fission.functions.api.weatherdata.weatherdata.shared_config")
    @patch("fission.functions.api.weatherdata.weatherdata.secret")
    def test_get_weather_data_custom_dates(self, mock_secret,
                                           mock_shared_config, mock_current_app):
        """
        Test the get_epa_data function with custom dates.
        :param mock_current_app:
        :return:
        """
        with self.app_context:
            mock_shared_config.side_effect = lambda k: "https://es:9200"
            mock_secret.side_effect = lambda k: "dummy-secret"
            start_date = "2024-05-01"
            end_date = "2024-05-30"

            # Mock Elasticsearch connection and logger
            mock_es = MagicMock()
            mock_current_app.logger = MagicMock()
            # Call the function with default dates
            weatherdata.get_weather_data(mock_es, start_date, end_date)

            # Check if the query is constructed correctly
            expected_query = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": f"{start_date}T00:00:00",
                            "lte": f"{end_date}T23:59:59"
                        }
                    }
                }
            }
            mock_current_app.logger.info.assert_called_once_with(f"Query: {expected_query}")
            # mock_es.search = MagicMock(return_value=mock.ANY)
            mock_es.search.assert_called_once_with(index='weather', body=expected_query,
                                                   aggregations=mock.ANY)

    @patch('fission.functions.api.weatherdata.weatherdata.get_weather_data')
    @patch('fission.functions.api.weatherdata.weatherdata.current_app')
    @patch('fission.functions.api.weatherdata.weatherdata.request')
    @patch("fission.functions.api.weatherdata.weatherdata.shared_config")
    @patch("fission.functions.api.weatherdata.weatherdata.secret")
    @patch("fission.functions.api.weatherdata.weatherdata.setup_connection")
    def test_weatherdata_main(self, mock_setup_connection, mock_secret,
                              mock_shared_config, mock_request, mock_current_app,
                              mock_get_weather_data):
        """
        Test the epadata main function.
        :return:
        """
        mock_request.headers = {}
        mock_shared_config.side_effect = mock_shared_url(key="ES_URL")
        mock_secret.side_effect = mock_shared_secret(key="username")

        mock_current_app.logger = MagicMock()
        # Test case: start date provided
        mock_get_weather_data.return_value = {'hits': {'hits': []}, 'aggregations': {}}
        weatherdata.main()
        mock_setup_connection.assert_called()
        mock_current_app.logger.info.assert_called_with("Start date not provided")
        mock_get_weather_data.assert_called_with(mock_setup_connection(), None, None)

        # Test case: end date provided
        mock_request.headers = {'X-Fission-Params-EndDate': '2024-01-31'}
        weatherdata.main()
        mock_setup_connection.assert_called()
        mock_get_weather_data.assert_called_with(mock_setup_connection(), None, '2024-01-31')

        # Test case: both start date and end date provided
        mock_request.headers = {'X-Fission-Params-StartDate': '2024-01-01',
                                'X-Fission-Params-EndDate': '2024-01-31'}
        weatherdata.main()
        mock_setup_connection.assert_called()
        mock_get_weather_data.assert_called_with(mock_setup_connection(),
                                                 '2024-01-01', '2024-01-31')


if __name__ == '__main__':
    unittest.main()
