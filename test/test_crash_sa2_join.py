# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import unittest
from unittest.mock import patch, MagicMock
from fission.functions.crash_sa2_join.crash_sa2_join import get_sa2s, get_health_risks, get_crashes_inside_sa2, create_joined_index, upload_crashes_joined

class TestFissionLambdaFunction(unittest.TestCase):
    @patch('fission.functions.crash_sa2_join.crash_sa2_join.Elasticsearch')
    def test_get_sa2s(self, mock_es):
        mock_es_instance = MagicMock()
        mock_es.return_value = mock_es_instance
        mock_es_instance.count.return_value = {"count": 1}
        mock_es_instance.search.return_value = {
            "hits": {
                "hits": [
                    {"_id": "1", "_source": {"name": "SA2 Name"}}
                ]
            }
        }

        es = mock_es()
        result = get_sa2s(es)

        self.assertEqual(result, {"1": {"name": "SA2 Name"}})

    @patch('fission.functions.crash_sa2_join.crash_sa2_join.Elasticsearch')
    def test_get_health_risks(self, mock_es):
        mock_es_instance = MagicMock()
        mock_es.return_value = mock_es_instance
        mock_es_instance.count.return_value = {"count": 1}
        mock_es_instance.search.return_value = {
            "hits": {
                "hits": [
                    {"_source": {"area_code": "123", "risk": "High"}}
                ]
            }
        }

        es = mock_es()
        result = get_health_risks(es)

        self.assertEqual(result, {"123": {"area_code": "123", "risk": "High"}})

    @patch('fission.functions.crash_sa2_join.crash_sa2_join.crash_sa2_join_config')
    @patch('fission.functions.crash_sa2_join.crash_sa2_join.Elasticsearch')
    def test_get_crashes_inside_sa2(self, mock_es, mock_config):
        mock_config.return_value = "10"
        mock_es_instance = MagicMock()
        mock_es.return_value = mock_es_instance
        
        mock_es_instance.search.return_value = {
            "_scroll_id": "dummy_scroll_id",
            "hits": {
                "hits": [
                    {"_source": {"crash_id": "1"}}
                ]
            }
        }
        mock_es_instance.scroll.return_value = {
            "hits": {
                "hits": []
            }
        }

        es = mock_es()
        result = get_crashes_inside_sa2(es, "sa2_id_dummy")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"crash_id": "1"})
        mock_es_instance.clear_scroll.assert_called_once()

    @patch('fission.functions.crash_sa2_join.crash_sa2_join.Elasticsearch')
    def test_create_joined_index(self, mock_es):
        mock_es_instance = MagicMock()
        mock_es.return_value = mock_es_instance

        es = mock_es()
        create_joined_index(es)

        mock_es_instance.indices.delete.assert_called_with(index="crash_sa2_joined")
        mock_es_instance.indices.create.assert_called()

    @patch('fission.functions.crash_sa2_join.crash_sa2_join.bulk')
    @patch('fission.functions.crash_sa2_join.crash_sa2_join.Elasticsearch')
    def test_upload_crashes_joined(self, mock_es, mock_bulk):
        mock_es_instance = MagicMock()
        mock_es.return_value = mock_es_instance

        crashes = [{"crash_id": "1"}]
        sa2 = {"sa2_id": "dummy_sa2_id"}
        health_risks = {"risk": "High"}
        upload_crashes_joined(mock_es(), crashes, sa2, health_risks)

        mock_bulk.assert_called_once()
        _, kwargs = mock_bulk.call_args
        self.assertEqual(kwargs['index'], "crash_sa2_joined")
        self.assertTrue(isinstance(kwargs['actions'][0], dict))

if __name__ == '__main__':
    unittest.main()
