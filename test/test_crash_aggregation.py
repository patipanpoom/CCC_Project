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
from flask import Flask
from fission.functions.api.crash_aggregation.crash_aggregation import get_aggregation, parse_aggregation_bucket, main

class TestCrashAggregation(unittest.TestCase):
    def setUp(self):
        self.es_mock = MagicMock()
        self.aggregations = [('avg', 'field1'), ('sum', 'field2')]

    def test_get_aggregation_success(self):
        self.es_mock.search.return_value = {
            "aggregations": {
                "by": {
                    "buckets": [
                        {
                            "key": "bucket1",
                            "doc_count": 10,
                            "field1": {"value": 5},
                            "field2": {"value": 15}
                        },
                        {
                            "key": "bucket2",
                            "doc_count": 20,
                            "field1": {"value": 7},
                            "field2": {"value": 25}
                        }
                    ]
                }
            }
        }

        expected = [
            {'count': 10, 'field1': 5, 'field2': 15, 'my_field': 'bucket1'},
            {'count': 20, 'field1': 7, 'field2': 25, 'my_field': 'bucket2'}
        ]

        with patch('fission.functions.api.crash_aggregation.crash_aggregation.Elasticsearch', return_value=self.es_mock):
            result = get_aggregation(self.es_mock, 'my_field', self.aggregations)
            self.assertEqual(result, expected)

    def test_parse_aggregation_bucket(self):
        bucket = {
            "key": "bucket1",
            "doc_count": 10,
            "field1": {"value": 5},
            "field2": {"value": 25}
        }
        by_field = "my_field"
        result = parse_aggregation_bucket(bucket, by_field, self.aggregations)
        self.assertEqual(result, {'count': 10, 'field1': 5, 'field2': 25, 'my_field': 'bucket1'})

    @patch('fission.functions.api.crash_aggregation.crash_aggregation.setup_connection')
    def test_main(self, setup_connection_mock):
        app = Flask(__name__)
        with app.test_request_context(headers={
            'X-Fission-Params-By-Field': 'sa2',
            'X-Fission-Params-Aggregation': 'avg',
            'X-Fission-Params-Aggregation-Field': 'field1',
            'X-Fission-Params-With-Aggregation': 'sum',
            'X-Fission-Params-With-Aggregation-Field': 'field2'
        }):
            es_mock = MagicMock()
            setup_connection_mock.return_value = es_mock

            es_mock.search.return_value = {
                "aggregations": {
                    "by": {
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                        "buckets": [
                            {
                                "key": 1234,
                                "doc_count": 50,
                                "field1": {
                                    "value": 5.5
                                },
                                "field2": {
                                    "value": 110
                                }
                            },
                            {
                                "key": 5678,
                                "doc_count": 50,
                                "field1": {
                                    "value": 6.5
                                },
                                "field2": {
                                    "value": 150
                                }
                            }
                        ]
                    }
                }
            }

            response = json.loads(main())
            self.assertEqual(response, [
                {"field1": 5.5, "field2": 110, "count": 50, "sa2.properties.sa2_main11.keyword": 1234},
                {"field1": 6.5, "field2": 150, "count": 50, "sa2.properties.sa2_main11.keyword": 5678}
            ])

if __name__ == '__main__':
    unittest.main()
