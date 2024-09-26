# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import ijson
from elasticsearch import Elasticsearch as ES
from elasticsearch.helpers import streaming_bulk

DATASET_PATH = './crash_alc_data/formatted_sa2_data.json'


def create_index(client):
    client.indices.create(
        index = "sa2_data",
        body = {
            "settings": {"number_of_shards": 2},
            "mappings": {
                "properties": {
                "bbox": {
                    "type": "float"
                },
                "geometry": {
                    "type": "geo_shape"
                },
                "geometry_name": {
                    "type": "text",
                    "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                    }
                },
                "id": {
                    "type": "text",
                    "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                    }
                },
                "properties": {
                    "properties": {
                    "albers_sqm": {
                        "type": "float"
                    },
                    "gcc_code11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "gcc_name11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "ogc_fid": {
                        "type": "long"
                    },
                    "sa2_5dig11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "sa2_main11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "sa2_name11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "sa3_code11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "sa3_name11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "sa4_code11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "sa4_name11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "ste_code11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    },
                    "ste_name11": {
                        "type": "text",
                        "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                        }
                    }
                    }
                },
                "type": {
                    "type": "text",
                    "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                    }
                }
                }
            }
        },
        ignore=400,
    )

def generate_actions():
    with open(DATASET_PATH, 'r') as f:
        array_items = ijson.items(f, 'item')
        count = 0
        for item in array_items:
            doc = item
            doc['_id'] = str(count)
            count += 1
            yield doc


def main():

    client = ES(
        "https://127.0.0.1:9200",
        verify_certs=False,
        basic_auth=("elastic", "elastic"),
    )
    
    create_index(client)

    success, failed = 0, 0
    for ok, response in streaming_bulk(
        client=client, index="sa2_data", actions=generate_actions(),
    ):
        if not ok:
            failed += 1
            print(response)
        else:
            success += 1

    print(f"{success} documents indexed")

if __name__ == "__main__":
    main()
