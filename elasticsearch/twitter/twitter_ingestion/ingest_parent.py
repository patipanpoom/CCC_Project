# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import os 
import pandas as pd
from elasticsearch import Elasticsearch as ES
from elasticsearch.helpers import streaming_bulk

# Function to generate actions for bulk indexing
def generate_actions(map_site_bbox_list):
    for record in map_site_bbox_list:
        bbox = record["geo"]
        doc = {
            "point": {
                "lat": (bbox[1] + bbox[3]) / 2,
                "lon": (bbox[0] + bbox[2]) / 2
            },
        }
        doc["relation_type"] = {"name": "site_name"}
        yield {
            "_index": "twitter",
            "_source": doc,
            "_routing": "site_name",
            "_id": record["site_name"]
        }

def main():
    # Directory containing the generated JSON files
    directory = '../twitter_data_chunk/'
    dfs = []

    # Loop through each JSON file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            # Read JSON file into a DataFrame
            df = pd.read_json(file_path, dtype=False)
            # Append the DataFrame to the list
            dfs.append(df)

    # Concatenate all DataFrames into one
    combined_df = pd.concat(dfs, ignore_index=True)

    map_site_bbox = {}
    uniq_site_names = combined_df['site_name'].unique()

    for _, row in combined_df.iterrows():
        map_site_bbox[row['site_name']] = row['geo']
        if len(uniq_site_names) == len(map_site_bbox):
            break

    map_site_bbox_list = [{'site_name': key, 'geo': value} for key, value in map_site_bbox.items()]
    
    client = ES(
        "https://127.0.0.1:9200",
        verify_certs=False,
        basic_auth=("elastic", "elastic"),
        timeout=30, 
        retry_on_timeout=True
    )

    # Create index with mapping data types
    index_body = {
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "sentiment": {"type": "float"},
                "point": {"type": "geo_point"},
                "text": {"type": "text"},
                "sa3_code_2021": {"type": "keyword"},
                "relation_type": {
                    "type": "join",
                    "relations": {
                        "site_name": "twitter"
                    }
                }
            }
        }
    }
    # Ingest new index base on mapping above
    client.indices.create(index="twitter", body=index_body, ignore=400)  # Ignore if index already exists

    success, failed = 0, 0
    for ok, response in streaming_bulk(
        client=client, index="twitter", actions=generate_actions(map_site_bbox_list),
    ):
        if not ok:
            failed += 1
            print(response)
        else:
            success += 1

    print(f"{success} documents indexed")

if __name__ == "__main__":
    main()