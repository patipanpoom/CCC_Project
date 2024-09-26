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

DATASET_PATH = './crash_alc_data/formatted_crash_data.json'

def create_index(client):
    client.indices.create(
        index = "crash_data",
        body = {
            "settings": {
                "number_of_shards": 2,
                "index.default_pipeline": "crash_merge_datetime"
            },
            "mappings": {
                "properties": {
                    "geometry": {
                        "type": "geo_point"
                    },
                    "properties": {
                    "properties": {
                        "ACCIDENT_DATE": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "ACCIDENT_NO": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "ACCIDENT_TIME": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "ACCIDENT_TYPE": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "BICYCLIST": {
                        "type": "long"
                        },
                        "DAY_OF_WEEK": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "DCA_CODE": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "DEG_URBAN_NAME": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "DIVIDED": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "DRIVER": {
                        "type": "long"
                        },
                        "FATALITY": {
                        "type": "long"
                        },
                        "FEMALES": {
                        "type": "long"
                        },
                        "HEAVYVEHICLE": {
                        "type": "long"
                        },
                        "INJ_OR_FATAL": {
                        "type": "long"
                        },
                        "LATITUDE": {
                        "type": "float"
                        },
                        "LGA_NAME": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "LIGHT_CONDITION": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "LONGITUDE": {
                        "type": "float"
                        },
                        "MALES": {
                        "type": "long"
                        },
                        "MOTORCYCLE": {
                        "type": "long"
                        },
                        "MOTORCYCLIST": {
                        "type": "long"
                        },
                        "NODE_ID": {
                        "type": "long"
                        },
                        "NODE_TYPE": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "NONINJURED": {
                        "type": "long"
                        },
                        "NO_OF_VEHICLES": {
                        "type": "long"
                        },
                        "OLD_DRIVER_75_AND_OVER": {
                        "type": "long"
                        },
                        "OLD_PED_65_AND_OVER": {
                        "type": "long"
                        },
                        "OTHERINJURY": {
                        "type": "long"
                        },
                        "PASSENGER": {
                        "type": "long"
                        },
                        "PASSENGERVEHICLE": {
                        "type": "long"
                        },
                        "PEDESTRIAN": {
                        "type": "long"
                        },
                        "PED_CYCLIST_13_18": {
                        "type": "long"
                        },
                        "PED_CYCLIST_5_12": {
                        "type": "long"
                        },
                        "PILLION": {
                        "type": "long"
                        },
                        "POLICE_ATTEND": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "PT_VEHICLE": {
                        "type": "long"
                        },
                        "RMA": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "ROAD_GEOMETRY": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "RUN_OFFROAD": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "SERIOUSINJURY": {
                        "type": "long"
                        },
                        "SEVERITY": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "SPEED_ZONE": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "SRNS": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "STAT_DIV_NAME": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                            }
                        }
                        },
                        "TOTAL_PERSONS": {
                        "type": "long"
                        },
                        "UNKNOWN": {
                        "type": "long"
                        },
                        "VICGRID_X": {
                        "type": "float"
                        },
                        "VICGRID_Y": {
                        "type": "float"
                        },
                        "YOUNG_DRIVER_18_25": {
                        "type": "long"
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
        client=client, index="crash_data", actions=generate_actions(),
    ):
        if not ok:
            failed += 1
            print(response)
        else:
            success += 1

    print(f"{success} documents indexed")

if __name__ == "__main__":
    main()
