# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import json
import unittest
from flask import Flask
from unittest.mock import patch, MagicMock
from fission.functions.api.crash_sample.crash_sample import get_crash_sample, main

class TestCrashSample(unittest.TestCase):
    def setUp(self):
        self.mock_es = MagicMock()
        self.mock_es.search.return_value = {
            "hits": {
                "hits": [
                    {"_source": {"field1": "value1"}},
                    {"_source": {"field2": "value2"}}
                ]
            }
        }

    def test_get_crash_sample(self):
        size = 2
        data = get_crash_sample(self.mock_es, size)
        self.assertEqual(len(data["hits"]["hits"]), 2)
        self.mock_es.search.assert_called_once()

    @patch('fission.functions.api.crash_sample.crash_sample.setup_connection')
    def test_main(self, mock_setup_connection):
        mock_setup_connection.return_value = self.mock_es
        app = Flask(__name__)

        with app.test_request_context(headers={'X-Fission-Params-Size': '2'}):
            response = json.loads(main())
            self.assertIn({'field1': 'value1'}, response)
            self.assertIn({'field2': 'value2'}, response)

if __name__ == '__main__':
    unittest.main()
