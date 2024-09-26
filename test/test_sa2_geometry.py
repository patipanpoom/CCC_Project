# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import json
import unittest
from unittest.mock import patch, MagicMock
from fission.functions.api.sa2_geometry.sa2_geometry import get_geometry, main

class TestSA2Geometry(unittest.TestCase):
    def setUp(self):
        self.mock_es = MagicMock()
        self.mock_es.count.return_value = {"count": 2}
        self.mock_es.search.return_value = {
            "hits": {
                "hits": [
                    {"_source": {"id": "1", "name": "Area 1"}},
                    {"_source": {"id": "2", "name": "Area 2"}}
                ]
            }
        }

    def test_get_geometry(self):
        geometry = get_geometry(self.mock_es)
        self.assertEqual(len(geometry), 2)
        self.assertEqual(geometry[0]['id'], '1')
        self.mock_es.count.assert_called_once()
        self.mock_es.search.assert_called_once()

    @patch('fission.functions.api.sa2_geometry.sa2_geometry.setup_connection')
    def test_main(self, mock_setup_connection):
        mock_setup_connection.return_value = self.mock_es

        response = json.loads(main())
        self.assertIn({'id': '1', 'name': 'Area 1'}, response)
        self.assertIn({'id': '2', 'name': 'Area 2'}, response)

if __name__ == '__main__':
    unittest.main()
