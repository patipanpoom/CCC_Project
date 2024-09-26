## Ingesting Twitter Data into Elasticsearch

### Twitter Preprocessing
1. Place the original Twitter dataset in the "twitter" repository.
2. Execute `twitter_local_processing.py` to preprocess the dataset.
3. After preprocessing, the processed files will be saved in chunks in the "twitter_data_chunk" repository.

### Twitter Ingestion
1. Run `ingest_parent.py` to create a new index named "twitter" in Elasticsearch and ingest the parent Twitter data.
2. Execute `ingest_child.py` to ingest all Twitter child data.

### Twitter Update Mapping SA3
1. Use Kibana Maps to ingest SA3 GeoJson data
2. Run `twitter_map_sa3.py` to update the Twitter index with SA3 code mapping.

This readme provides a step-by-step guide for ingesting Twitter data into Elasticsearch, including preprocessing steps and ingestion procedures.
