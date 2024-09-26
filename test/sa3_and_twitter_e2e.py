# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)



import unittest, requests, json, time



class HTTPSession:
    def __init__(self, protocol, hostname, port):
        self.session = requests.session()
        self.base_url = f'{protocol}://{hostname}:{port}'

    def get(self, path):
        return self.session.get(f'{self.base_url}{path}')

    def post(self, path, data):
        return self.session.post(f'{self.base_url}{path}', json=data)

    def put(self, path, data):
        return self.session.put(f'{self.base_url}{path}', json=data)

    def delete(self, path):
        return self.session.delete(f'{self.base_url}{path}')
class TestEnd2End(unittest.TestCase):
    def test_median_data(self):
        r = test_request.get('/median/age/sa3/12101')
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["median_age_persons"], 38)

        r = test_request.get('/median/income/sa3/12101')
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["median_tot_prsnl_inc_weekly"], 1255)

    def test_highest_education(self):
        r = test_request.get('/highest-level-of-schooling/sa3/12101')
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["f_hghst_yr_schl_ns_tot"], 2113)
        self.assertIn("avg_education", body)
        self.assertIn("male", body["avg_education"])
        self.assertIn("female", body["avg_education"])
        self.assertIn("person", body["avg_education"])

    # def test_twitter_by_sa3(self):
    #     r = test_request.get('/twitter/avgsentiment/sa3/12101')
    #     self.assertEqual(r.status_code, 200)
    #     body = r.json()
    #     self.assertEqual(body["avg_sentiment"]["value"], 0.06070880082808435)
        
    #     r = test_request.get('/twitter/avgsentiment/sa3/12101/start/2021-09-17/end/2021-09-25')
    #     self.assertEqual(r.status_code, 200)
    #     body = r.json()
    #     self.assertEqual(body["avg_sentiment"]["value"], 0.08320281751961871)
    
    def test_age_by_sex(self):
        r = test_request.get('/age-by-sex/sa3/12101')
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["age_75_84_c21_p"], 5474)





if __name__ == '__main__':

    test_request = HTTPSession('http', 'localhost', 9090)
    unittest.main()
