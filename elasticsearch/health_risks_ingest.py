# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import json
from elasticsearch import Elasticsearch as ES
from elasticsearch.helpers import streaming_bulk

DATASET_PATH = './crash_alc_data/sa2_health_risks/sa2_health_risks_data.json'

def generate_actions():
    with open(DATASET_PATH, mode='r') as f:
        input_data = json.load(f)

    for record in input_data["features"]:
        doc = record["properties"]
        doc["_id"] = record['id'][39:]
        yield doc



def main():

    client = ES(
        "https://127.0.0.1:9200",
        verify_certs=False,
        basic_auth=("elastic", "elastic"),
    )

    success, failed = 0, 0
    for ok, response in streaming_bulk(
        client=client, index="health_risks_data", actions=generate_actions(),
    ):
        if not ok:
            failed += 1
            print(response)
        else:
            success += 1

    print(f"{success} documents indexed")

if __name__ == "__main__":
    main()
