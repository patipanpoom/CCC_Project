# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
This function update sa3_code in twitter index
based on mapping nearest sa3 polygon with twitter corrdinates
"""
import warnings
from elasticsearch8 import Elasticsearch, AuthenticationException

warnings.filterwarnings("ignore")

def setup_connection() -> Elasticsearch:
    # pylint: disable=duplicate-code
    """
    Set up the connection to the Elasticsearch server.
    :return: es: Elasticsearch connection object
    """
    # Disable SSL Certificate Verification
    username = 'elastic'
    password = 'elastic'
    es = Elasticsearch(["https://localhost:9200/"],
                        verify_certs=False,
                        basic_auth=(username,
                                   password),
                        timeout=30, 
                        retry_on_timeout=True
                    )

    # Set up the connection to the Elasticsearch server
    try:
        es.info()
        print("Connected to ES")
        return es
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except AuthenticationException as e:
        print(f"Error: {e}")
        return None


def get_twitter(es: Elasticsearch, page_size: int = 1000) -> dict:
    """
    Retrieves documents from Elasticsearch with pagination support using scrolling.
    """
    scroll_timeout = "1m"  # Set the scroll timeout (e.g., "1m" for 1 minute)
    # Perform the initial search request to initiate scrolling
    initial_search_response = es.search(
        index="twitter",
        scroll=scroll_timeout,
        body={
            "query": {
                "match": {
                    "relation_type": "site_name"
                }
            },
            "size": page_size 
        }
    )
    # Initialize the list to store all documents
    all_documents = []
    # Extract the initial batch of hits from the search response
    hits = initial_search_response['hits']['hits']
    all_documents.extend(hits)
    # Get the scroll ID to continue scrolling
    scroll_id = initial_search_response['_scroll_id']
    # Perform scrolling to retrieve remaining documents
    while hits:
        scroll_response = es.scroll(scroll_id=scroll_id, scroll=scroll_timeout)
        hits = scroll_response['hits']['hits']
        # Extend the list of all documents with the new batch of hits
        all_documents.extend(hits)
    # Clear the scroll context
    es.clear_scroll(scroll_id=scroll_id)
    return all_documents

# This function use elasticsearch analysis to get the map sa3_code by (lat,lon)
def search_sa3_by_location(es, lat, lon, index_name):
    # Elasticsearch query
    query = {
        "query": {
            "bool": {
                "must": {"match_all": {}},
                "filter": {
                    "geo_distance": {
                        "distance": "1km",
                        "geometry": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                }
            }
        }
    }
    # Execute the query
    response = es.search(index=index_name, body=query, size=1)
    return response['hits']['hits']

# This function update all child in index base on specify arguments
def update_child_documents_by_query(es, index, parent_type, parent_id, field_name, new_value):
    # Define the update by query request body
    update_query = {
        "query": {
            "has_parent": {
                "parent_type": parent_type,
                "query": {
                    "term": {
                        "_id": parent_id
                    }
                }
            }
        },
        "script": {
            "source": f"ctx._source['{field_name}'] = '{new_value}'",
            "lang": "painless"
        }
    }
    try:
        # Perform the update by query
        es.update_by_query(index=index, body=update_query)
        return True
    except Exception as e:
        print(f"Error updating documents by query: {e}")
        return False


def main():
    es = setup_connection()
    twitter_parent = get_twitter(es)
    for i,twit in enumerate(twitter_parent):
        # Get twitter coordinates
        lat = twit['_source']['point']['lat']
        lon = twit['_source']['point']['lon']
        # Search nearest sa3_code for twitter's coordinates
        rows_within_polygon = search_sa3_by_location(es, lat, lon, "sa3")
        # If coordinates in sa3 then update twitter
        if len(rows_within_polygon) > 0:
            print(i, "/",len(twitter_parent))
            sa3_code = rows_within_polygon[0]['_source']['SA3_CODE21']
            update_child_documents_by_query(es, "twitter", "site_name", twit['_id'], "sa3_code_2021", sa3_code)
    return "ok"

if __name__ == "__main__":
    main()