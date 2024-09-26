# Ingesting the SUDO data into elastic Search

Since SUDO does not offer public apis to access the data, we have to download the data from the SUDO website and ingest it into the elastic search manually. Following are the steps to ingest the data into elastic search.

If you're using macOS, you can install the `gdal` library using Homebrew:
```bash
brew install gdal
```
If you're using Linux, you can install the `gdal` library using the following command:
```bash
sudo apt-get install gdal-bin
```
It may take a few minutes to complete the installation

Make sure you're connected to the elasticsearch cluster. Port forward to connect to the elastic search
```bash
kubectl port-forward service/elasticsearch-master -n elastic 9200:9200
```

Port forward to connect to Kibana
```bash
kubectl port-forward service/kibana-kibana -n elastic 5601:5601
```
Once you have the gdal installed and the shape data downloaded from SUDO. verify your connection to Elasticsearch using the `ogrinfo`

```bash
ogrinfo --config GDAL_HTTP_UNSAFESSL YES ES:https://elastic:elastic@localhost:9200
```


You can run the following command to generate the mapping file.

```bash
ogr2ogr --config GDAL_HTTP_UNSAFESSL YES -lco INDEX_NAME=sudo-mortality-fertility-data -lco NOT_ANALYZED_FIELDS={ALL} -lco WRITE_MAPPING=./sudo/mortality_fertility_mapping.json ES:https://elastic:elastic@localhost:9200 ./sudo/sla11_prematuremortality__sla11_fertility-.shp
```

We can edit our mapping.json file in a text editor to fine-tune some of the settings. Then we can use our customized mapping when ingesting our shapefile by specifying the path to our customized mapping.

```bash
ogr2ogr --config GDAL_HTTP_UNSAFESSL YES -lco INDEX_NAME=mortality-fertility-data -lco OVERWRITE_INDEX=YES -lco MAPPING=./sudo/mortality_fertility_mapping.json ES:https://elastic:elastic@localhost:9200 ./sudo/sla11_prematuremortality__sla11_fertility-.shp
```

Create the index in elastic search

```bash
curl -XPUT -k 'https://127.0.0.1:9200/epadata' \
   --user 'elastic:elastic' \
   --header 'Content-Type: application/json' \
   --data '{
    "settings": {
        "index": {
            "number_of_shards": 3,
            "number_of_replicas": 1
        }
    },
    "mappings": {
        "properties": {
            "siteid": {
                "type": "keyword"
            },
            "sitename": {
                "type": "text"
            },
            "timestamp": {
                "type": "date"
            },
            "geo": {
                "type": "geo_point"
            },
            "siteHealthAdvices": {
                "type": "object"
            },
            "so2": {
                "type": "object"
            },
            "co": {
                "type": "object"
            },
            "pm2p5": {
                "type": "object"
            },
            "pm10": {
                "type": "object"
            },
            "no2": {
                "type": "object"
            }
        }
    }
}'  | jq '.'

curl -XPUT -k 'https://127.0.0.1:9200/weather' \
   --user 'elastic:elastic' \
   --header 'Content-Type: application/json' \
   --data '{
    "settings": {
        "index": {
            "number_of_shards": 3,
            "number_of_replicas": 1
        }
    },
    "mappings": {
        "properties": {
            "siteid": {
                "type": "keyword"
            },
            "sitename": {
                "type": "text"
            },
            "timestamp": {
                "type": "date"
            },
            "geo": {
                "type": "geo_point"
            },
            "airtemp": {
                "type": "text"
            },
            "dewpt": {
                "type": "text"
            },
            "realhum": {
                "type": "text"
            },
            "vis": {
                "type": "text"
            },
            "weather": {
                "type": "text"
            },
            "winddir": {
                "type": "text"
            },
            "windspd": {
                "type": "text"
            },
            "cloud": {
                "type": "text"
            },
            "raintrace": {
                "type": "text"
            }
        }
    }
}'  | jq '.'
```



