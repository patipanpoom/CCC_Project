# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import unittest
import requests

class TestCrashEnd2End(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        cls.base_url = 'http://127.0.0.1:9090/'

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def request(self, endpoint):
        url = self.base_url + endpoint
        response = self.session.get(url)
        return response.json()

    def test_crash_sample(self):
        response = self.request('crashes/sample/10')

        self.assertEqual(len(response), 10)
        self.assertIn("geometry", response[0])
        self.assertIn("properties", response[0])
        self.assertIn("sa2", response[0])
        self.assertIn("health_risks", response[0])
        self.assertEqual(response[0]["geometry"]["type"], "Point")

    def test_crash_aggregation_simple(self):
        response = self.request('crashes/by/sa2')

        self.assertEqual(len(response), 432)
        self.assertIn("count", response[0])
        self.assertIn("sa2.properties.sa2_main11.keyword", response[0])

    def test_crash_aggregation_nested(self):
        response = self.request('crashes/by/sa2/avg/health_risks.alcohol_cons_2_rate_3_11_7_13')

        self.assertEqual(len(response), 432)
        self.assertIn("count", response[0])
        self.assertIn("health_risks.alcohol_cons_2_rate_3_11_7_13", response[0])
        self.assertIn("sa2.properties.sa2_main11.keyword", response[0])

    def test_sa2_geometry(self):
        response = self.request('sa2/geometry')

        self.assertEqual(len(response), 440)
        self.assertIn("geometry", response[0])
        self.assertEqual(response[0]["geometry"]["type"], "MultiPolygon")

if __name__ == '__main__':
    unittest.main()
