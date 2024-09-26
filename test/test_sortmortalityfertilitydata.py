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
import pdb
import unittest

from unittest.mock import patch, MagicMock, Mock

from fission.functions.api.sortmortalityfertilitydata.sortmortalityfertilitydata import main
from test.mockconfig import mock_shared_url, mock_shared_secret
from flask import Flask
from fission.functions.api.sortmortalityfertilitydata import sortmortalityfertilitydata


class TestMortalityFertilityData(unittest.TestCase):
    """
    This class contains the test cases for the sorted mortality fertility data API module.
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
        self.client = self.app.test_client()
        # self.app = Flask(__name__)
        # self.app.add_url_rule('/', 'main', main, methods=['GET', 'OPTIONS'])
        # self.client = self.app.test_client()
        # self.app.testing = True

    def tearDown(self):
        """
        Tear down the test.
        :return:
        """

    @patch('fission.functions.api.sortmortalityfertilitydata.sortmortalityfertilitydata.setup_connection')
    @patch('fission.functions.api.sortmortalityfertilitydata.sortmortalityfertilitydata.get_sorted_results')
    @patch('fission.functions.api.sortmortalityfertilitydata.sortmortalityfertilitydata.request')
    def test_get_request_success(self, mock_request, mock_get_sorted_results, mock_setup_connection):
        # Mock Elasticsearch connection and response
        mock_es = Mock()
        mock_setup_connection.return_value = mock_es
        mock_request.headers = {}
        mock_get_sorted_results.return_value = {
            'hits': {
                'hits': [
                    {'_source': {'attribute': 'value1'}},
                    {'_source': {'attribute': 'value2'}}
                ]
            }
        }

        mock_request.headers = {
            'X-Fission-Params-Attribute': 'dth_bst_00'
        }
        mock_request.method = 'GET'
        sortmortalityfertilitydata.main()

        mock_setup_connection.assert_called()
        mock_get_sorted_results.assert_called_with(mock_setup_connection(), 'dth_bst_00')

    @patch('fission.functions.api.sortmortalityfertilitydata.sortmortalityfertilitydata.setup_connection')
    @patch('fission.functions.api.sortmortalityfertilitydata.sortmortalityfertilitydata.request')
    def test_get_request_invalid_attribute(self, mock_request, mock_setup_connection):
        # Mock Elasticsearch connection and response
        mock_es = Mock()
        mock_setup_connection.return_value = mock_es
        mock_request.headers = {}
        mock_request.headers = {
            'X-Fission-Params-Attribute': 'invalid_attribute'
        }
        mock_request.method = 'GET'
        pdb.set_trace()
        response = sortmortalityfertilitydata.main()

        self.assertEqual(response[1], 400)


if __name__ == '__main__':
    unittest.main()
