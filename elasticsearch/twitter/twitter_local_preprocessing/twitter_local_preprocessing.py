# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

import os
import orjson
import json
import math

# This function convert json string to json object
def line2json(line):
    line = line.strip()
    try:
        if line[-1] == ',':
            line = line[:-1]
            twitter = orjson.loads(line)
            return twitter
    except :
        return None

# This function use for read file by chunk
def seek_file_handling(file_name, start_pointer, end_pointer):
    filtered_twits = []
    with open(file_name, 'r', errors='replace') as file:
        file.seek(start_pointer)
        
        # Read line by line until reaching end_pointer or end of file
        while True:
            if end_pointer != -1 and file.tell() >= end_pointer:
                break
            
            line = file.readline()
            if not line:
                break  # End of file
            
            twitter = line2json(line)
            if twitter:
                try:
                    doc_data = twitter.get('doc', {}).get('data', {})
                    created_at_str = doc_data.get('created_at', '')
                    
                    # Check if created_at field is not empty
                    if created_at_str:
                        filtered_twit = {}
                        filtered_twit['timestamp'] = created_at_str
                        filtered_twit['sentiment'] = float(doc_data['sentiment'])
                        filtered_twit['site_name'] = twitter['doc']['includes']['places'][0]['full_name']
                        filtered_twit['geo'] = twitter['doc']['includes']['places'][0]['geo']['bbox']
                        filtered_twit['text'] = twitter.get('value').get('text')
                        filtered_twits.append(filtered_twit)
                except Exception as e:
                    # Handle exceptions gracefully
                    pass

    return filtered_twits

# This function use for write json file
def write_json_file(filtered_twits, output_file):
    with open(output_file, 'w') as file:
        json.dump(filtered_twits, file)

  
def main():
    file_name = "twitter-100gb.json"
    output_file = "./twitter_data_chunk/filtered_tweets"
    file_size = os.path.getsize(file_name)
    batch_size = math.floor(file_size / 20)
    start_pointer = 0
    end_pointer = start_pointer + batch_size
    filtered_twits = []
    num = 0
    
    while True:
        if start_pointer > file_size:
            break
        filtered_twits_batch = seek_file_handling(file_name, start_pointer, end_pointer)
        start_pointer =  start_pointer + batch_size
        end_pointer = start_pointer + batch_size
        filtered_twits.extend(filtered_twits_batch)
        write_json_file(filtered_twits_batch, output_file + str(num) +".json")
        num += 1
        print(str((100*start_pointer/file_size)))
    print(len(filtered_twits))
    

if __name__ == "__main__":
    main()