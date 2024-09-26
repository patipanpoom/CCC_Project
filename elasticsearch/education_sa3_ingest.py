# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import os
import re
import json
from elasticsearch import Elasticsearch as ES
from elasticsearch.helpers import streaming_bulk, bulk

# File path
DATASET_FOLDER = './sudo/SA3-G16A_Highest_Year_of_School_Completed_by_Age_by_Sex/'

DATA_PATTERN = r'^[a-zA-Z]+\d+\.json'

def generate_actions():
    for filename in os.listdir(DATASET_FOLDER):
        if re.match(DATA_PATTERN, filename):
            file_path = os.path.join(DATASET_FOLDER, filename)
            with open(file_path, mode='r') as f:
                input_data = json.load(f)

            for record in input_data["features"]:
                doc = record["properties"]
                yield doc

def main():

    client = ES(
        "https://127.0.0.1:9200",
        verify_certs=False,
        basic_auth=("elastic", "elastic"),
    )

    # Create index with mapping data types
    index_body = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
    }
    client.indices.create(index="school_sa3", body=index_body, ignore=400)  # Ignore if index already exists
    
    success, failed = 0, 0
    for ok, response in streaming_bulk(
        client=client, index="school_sa3", actions=generate_actions(),
    ):
        if not ok:
            failed += 1
            print(response)
        else:
            success += 1

    print(f"{success} documents indexed")

if __name__ == "__main__":
    main()