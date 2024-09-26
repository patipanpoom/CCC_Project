# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import json

input_path = './crash_alc_data/VICTORIAN_ROAD_CRASH_DATA.geojson'

with open(input_path, 'r') as f:
    input_data = json.load(f)

with open('./formatted_crash_data.json', 'w') as f:
    json.dump(input_data['features'], f)