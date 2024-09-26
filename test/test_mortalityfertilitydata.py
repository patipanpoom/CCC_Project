# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This module contains the test cases for the mortality fertility data API module.
"""
import unittest

from unittest.mock import patch, MagicMock
from test.mockconfig import mock_shared_url, mock_shared_secret
from flask import Flask
from fission.functions.api.mortalityfertilitydata import mortalityfertilitydata






class TestMortalityFertilityData(unittest.TestCase):
    """
    This class contains the test cases for the mortality fertility data API module.
    """

    source = {"_source": ["area_code",
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
                          "dths_tot75"]}

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

    @patch('fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.current_app')
    @patch("fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.config")
    @patch("fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.secret")
    def test_get_sudo_data_default_geo_point(self, mock_secret,
                                             mock_shared_config, mock_current_app):
        """
        Test the get_epa_data function with default dates.
        :param mock_current_app:
        :return:
        """
        with self.app_context:
            mock_shared_config.side_effect = mock_shared_url(key="ES_URL")
            mock_secret.side_effect = mock_shared_secret(key="username")

            # Mock Elasticsearch connection and logger
            mock_es = MagicMock()
            mock_current_app.logger = MagicMock()
            mortalityfertilitydata.get_sudo_data(mock_es)

            # Check if the query is constructed correctly
            expected_query = {
                "size": 10000,
                "query": {
                    "match_all": {}
                },
                "_source": self.source["_source"]
            }
            mock_current_app.logger.info.assert_called_once_with(f"Query: {expected_query}")
            mock_es.search.assert_called_once_with(index='mortality-fertility-data',
                                                   body=expected_query)

    @patch('fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.current_app')
    @patch("fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.config")
    @patch("fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.secret")
    def test_get_sudo_data_custom_geo_point(self, mock_secret,
                                            mock_config, mock_current_app):
        """
        Test the get_epa_data function with custom dates.
        :param mock_current_app:
        :return:
        """
        with self.app_context:
            mock_config.side_effect = lambda k: "https://es:9200"
            mock_secret.side_effect = lambda k: "dummy-secret"

            # Mock Elasticsearch connection and logger
            mock_es = MagicMock()
            mock_current_app.logger = MagicMock()
            # Call the function with default dates
            geo_point = {"type": "point", "coordinates": [float(145.4), float(-37.8)]}
            mortalityfertilitydata.get_sudo_data(mock_es, geo_point)

            # Check if the query is constructed correctly
            expected_query = {
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
                }, "_source": self.source["_source"]
            }
            mock_current_app.logger.info.assert_called_once_with(f"Query: {expected_query}")
            mock_es.search.assert_called_once_with(index='mortality-fertility-data',
                                                   body=expected_query)

    @patch('fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.get_sudo_data')
    @patch('fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.current_app')
    @patch('fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.request')
    @patch("fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.config")
    @patch("fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.secret")
    @patch("fission.functions.api.mortalityfertilitydata.mortalityfertilitydata.setup_connection")
    def test_mortalityfertilitydata_main(self, mock_setup_connection, mock_secret,
                                         mock_config, mock_request, mock_current_app,
                                         mock_get_sudo_data):
        """
        Test the epadata main function.
        :return:
        """
        mock_request.headers = {}
        mock_config.side_effect = mock_shared_url(key="ES_URL")
        mock_secret.side_effect = mock_shared_secret(key="username")

        mock_current_app.logger = MagicMock()
        mock_get_sudo_data.return_value = {"hits": {"hits":
                                                        [{"_source":
                                                              {"area_code": "dummy-area-code"}}]}}
        mortalityfertilitydata.main()
        mock_setup_connection.assert_called()
        mock_current_app.logger.info.assert_called_with("Getting data without geo_point")
        mock_get_sudo_data.assert_called_with(mock_setup_connection())

        # Test case: both start date and end date provided
        mock_request.headers = {'X-Fission-Params-Lat': '145.4',
                                'X-Fission-Params-Long': '-37.8'}
        lat = mock_request.headers['X-Fission-Params-Lat']
        long = mock_request.headers['X-Fission-Params-Long']
        geo_point = {"type": "point", "coordinates": [float(long), float(lat)]}
        mortalityfertilitydata.main()
        mock_setup_connection.assert_called()
        mock_current_app.logger.info.assert_called_with("Getting data with geo_point")
        mock_get_sudo_data.assert_called_with(mock_setup_connection(), geo_point)


if __name__ == '__main__':
    unittest.main()
