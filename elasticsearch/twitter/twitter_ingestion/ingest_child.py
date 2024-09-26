# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import os
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

# Function to read a JSON file and return its contents
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to generate actions for bulk indexing
def generate_actions(file_name):
    with open(file_name, mode='r') as f:
        filtered_twits_batch = json.load(f)

    for filtered_twit in filtered_twits_batch:
        doc = {
            "timestamp": filtered_twit['timestamp'],
            "sentiment": filtered_twit['sentiment'],
            "text": filtered_twit['text'],
            "relation_type": {
                "name": "twitter",
                "parent": filtered_twit['site_name']
            }
        }
        yield {
            "_index": "twitter",
            "_source": doc,
            "_routing": "site",
        }
        
def main():
    # Directory containing the generated JSON files
    directory = '../twitter_data_chunk/'

    client = Elasticsearch(
        "https://127.0.0.1:9200",
        verify_certs=False,
        http_auth=("elastic", "elastic"),
        timeout=30, 
        retry_on_timeout=True
    )
    
    success, failed = 0, 0

    # Loop through each JSON file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)

            # Use streaming_bulk to ingest the documents from the file
            for ok, response in streaming_bulk(
                client=client,
                index="twitter",
                actions=generate_actions(file_path),
            ):
                if not ok:
                    failed += 1
                    print(f"Failed to index document: {response}")
                else:
                    success += 1

    print(f"{success} documents indexed successfully")
    print(f"{failed} documents failed to index")

if __name__ == "__main__":
    main()
