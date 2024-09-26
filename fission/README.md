# Use of YAML specifications to deploy functions using Fission

**Make sure you're currently in the root directory of the repository. The following command will deploy the function to Fission:**

```bash
(
  cd fission
  fission specs init
) 
```

Let's start by creating the specs for the python and Node.js environments

```bash
(
cd fission
fission env create --spec --name python --image fission/python-env --builder fission/python-builder
fission env create --spec --name nodejs --image fission/node-env --builder fission/node-builder
)  
```

Functions uses the shared-data config map to dynamically retrieve the configuration values.
You can review the config map in the `fission/specs/shared-data.yaml` file.

```bash
kubectl apply -f ./fission/specs/shared-data.yaml
kubectl apply -f ./fission/specs/es-secret.yaml
kubectl apply -f ./fission/specs/epa-secret.yaml
kubectl get configmaps shared-data -o yaml

```

Create the kafka topics

```bash
kubectl apply -f fission/topics/airmonitoringsites.yaml --namespace kafka
kubectl apply -f fission/topics/airquality.yaml --namespace kafka
kubectl apply -f fission/topics/weather.yaml --namespace kafka
kubectl apply -f fission/topics/errors.yaml --namespace kafka
```

To list all the topics 
```bash
kubectl get kafkatopic -n kafka
```

Create necessary data harvester functions
```bash
(
  cd fission
  fission function create --spec --name epamonitoringsites --env python --code ./functions/epamonitoringsites.py --configmap shared-data --secret epa-secret
  fission route create --spec --url /epamonitoringsites --function epamonitoringsites --name epamonitoringsites --createingress
  fission function create --spec --name wharvester --env python --code ./functions/wharvester.py --configmap shared-data
  fission route create --spec --url /wharvester --function wharvester --name wharvester --createingress
  
)
(
  cd ./fission/functions/enqueue
  zip -r enqueue.zip .
  mv enqueue.zip ../
)

(
  cd fission
  fission package create --spec --sourcearchive ./functions/enqueue.zip \
    --env python \
    --name enqueue \
    --buildcmd './build.sh'

  fission function create --spec --name enqueue \
    --pkg enqueue \
    --env python \
    --configmap shared-data \
    --secret es-secret \
    --entrypoint "enqueue.main"
)
(
  cd ./fission/functions/addepadata
  zip -r addepadata.zip .
  mv addepadata.zip ../
)

(
  cd fission
  fission package create --spec --sourcearchive ./functions/addepadata.zip \
    --env python \
    --name addepadata \
    --buildcmd './build.sh'

  fission function create --spec --name addepadata \
    --pkg addepadata \
    --env python \
    --entrypoint "addepadata.main"
)

(
  cd ./fission/functions/addweatherdata
  zip -r addweatherdata.zip .
  mv addweatherdata.zip ../
)

(
  cd fission
  fission package create --spec --sourcearchive ./functions/addweatherdata.zip \
    --env python \
    --name addweatherdata \
    --buildcmd './build.sh'

  fission function create --spec --name addweatherdata \
    --pkg addweatherdata \
    --env python \
    --configmap shared-data \
    --secret es-secret \
    --entrypoint "addweatherdata.main"
)
```

Create necessary analysis functions
```bash
kubectl apply -f ./fission/specs/crash-sa2-join-data.yaml

(
  cd fission/functions/crash_sa2_join
  zip -r crash_sa2_join.zip .
  mv crash_sa2_join.zip ../
)

fission package update --sourcearchive ./fission/functions/crash_sa2_join.zip \
  --env python \
  --name crash-sa2-join \
  --buildcmd './build.sh'

fission fn update --name crash-sa2-join \
  --pkg crash-sa2-join \
  --env python \
  --entrypoint "crash_sa2_join.main" \
  --configmap shared-data \
  --configmap crash-sa2-join-data \
  --secret es-secret \
  --fntimeout 600
```

Create necessary data apis functions

```bash
(
  cd ./fission/functions/api/mortalityfertilitydata
  zip -r mortalityfertilitydata.zip .
  mv mortalityfertilitydata.zip ../
)
  
(
  cd fission
  fission package create --spec --sourcearchive ./functions/api/mortalityfertilitydata.zip \
    --env python \
    --name mortalityfertilitydata \
    --buildcmd './build.sh'

  fission function create --spec --name mortalityfertilitydata \
    --pkg mortalityfertilitydata \
    --env python \
    --configmap shared-data \
    --secret es-secret \
    --entrypoint "mortalityfertilitydata.main"
)
  
(
  cd fission
  
  fission route create --spec --name mfdata --function mortalityfertilitydata \
    --method GET \
    --url '/mortalityfertilitydata' \
    --createingress

  fission route create --spec --name mfgeopointdata --function mortalityfertilitydata \
    --method GET \
    --url '/mortalityfertilitydata/lat/{lat:[0-9.-]*}/long/{long:[0-9.-]*}' \
    --createingress
)
  
(
  cd ./fission/functions/api/sortmortalityfertilitydata
  zip -r sortmortalityfertilitydata.zip .
  mv sortmortalityfertilitydata.zip ../
)
  
(
  cd fission
  fission package create --spec --sourcearchive ./functions/api/sortmortalityfertilitydata.zip \
    --env python \
    --name sortmortalityfertilitydata \
    --buildcmd './build.sh'

  fission function create --spec --name sortmortalityfertilitydata \
    --pkg sortmortalityfertilitydata \
    --env python \
    --configmap shared-data \
    --secret es-secret \
    --entrypoint "sortmortalityfertilitydata.main"
)
  
(
  cd fission

  fission route create --spec --name mfsortdata --function sortmortalityfertilitydata \
    --method GET \
    --url '/sortmortalityfertilitydata/attribute/{attribute:[a-zA-Z.-_]*}' \
    --createingress
)

(
  cd ./fission/functions/api/weatherdata
  zip -r weatherdata.zip .
  mv weatherdata.zip ../
)
  
(
  cd fission
  fission package create --spec --sourcearchive ./functions/api/weatherdata.zip \
    --env python \
    --name getweatherdata \
    --buildcmd './build.sh'

  fission function create --spec --name getweatherdata \
    --pkg getweatherdata \
    --env python \
    --configmap shared-data \
    --secret es-secret \
    --entrypoint "weatherdata.main"
)

(
  cd fission
  fission route create --spec --name aggweatherdata --function getweatherdata \
    --method GET \
    --url '/getweatherdata' \
    --createingress
    
  fission route create --spec --name weatherdatastart --function getweatherdata \
    --method GET \
    --url '/getweatherdata/startdate/{Startdate:[0-9-]*}' \
    --createingress

  fission route create --spec --name weatherdatastartend --function getweatherdata \
    --method GET \
    --url '/getweatherdata/startdate/{Startdate:[0-9-]*}/enddate/{Enddate:[0-9-]*}' \
    --createingress
)
  
(
  cd ./fission/functions/api/epadata
  zip -r epadata.zip .
  mv epadata.zip ../
)
  
(
  cd fission
  fission package create --spec --sourcearchive ./functions/api/epadata.zip \
    --env python \
    --name getepadata \
    --buildcmd './build.sh'

  fission function create --spec --name getepadata \
    --pkg getepadata \
    --env python \
    --configmap shared-data \
    --secret es-secret \
    --entrypoint "epadata.main"
)

(
  cd fission
  fission route create --spec --name aggepadata --function getepadata \
    --method GET \
    --url '/getepadata' \
    --createingress
    
  fission route create --spec --name epadatastart --function getepadata \
    --method GET \
    --url '/getepadata/startdate/{Startdate:[0-9-]*}' \
    --createingress

  fission route create --spec --name epadatastartend --function getepadata \
    --method GET \
    --url '/getepadata/startdate/{Startdate:[0-9-]*}/enddate/{Enddate:[0-9-]*}' \
    --createingress
)

fission route create --spec --url /sa2/geometry \
  --function sa2-geometry \
  --name sa2-geometry \
  --createingress

(
  cd fission/functions/api/sa2_geometry
  zip -r sa2_geometry.zip .
  mv sa2_geometry.zip ../
)

(
  fission package create --spec --sourcearchive ./fission/functions/api/sa2_geometry.zip \
    --env python \
    --name sa2-geometry \
    --buildcmd './build.sh'

  fission fn create --spec --name sa2-geometry \
    --pkg sa2-geometry \
    --env python \
    --entrypoint "sa2_geometry.main" \
    --configmap shared-data \
    --secret es-secret
)

fission route create --spec --url /crashes/sample/{size} \
  --function crash-sample \
  --name crash-sample \
  --createingress

(
  cd fission/functions/api/crash_sample
  zip -r crash_sample.zip .
  mv crash_sample.zip ../
)

(
  fission package update --spec --sourcearchive ./fission/functions/api/crash_sample.zip \
    --env python \
    --name crash-sample \
    --buildcmd './build.sh'

  fission fn update --spec --name crash-sample \
    --pkg crash-sample \
    --env python \
    --entrypoint "crash_sample.main" \
    --configmap shared-data \
    --secret es-secret
)

(
  fission route create --spec --url /crashes/by/{by-field} \
    --function crashes-aggregation \
    --name crashes-aggregation \
    --createingress

  fission route create --spec --url /crashes/by/{by-field}/{aggregation}/{aggregation-field} \
    --function crashes-aggregation \
    --name crashes-aggregation-nested \
    --createingress

  fission route create --spec --url /crashes/by/{by-field}/{aggregation}/{aggregation-field}/with/{with-aggregation}/{with-aggregation-field} \
    --function crashes-aggregation \
    --name crashes-aggregation-nested-with \
    --createingress
)

(
  cd fission/functions/api/crashes_aggregation
  zip -r crashes_aggregation.zip .
  mv crashes_aggregation.zip ../
)

(
  fission package update --spec --sourcearchive ./fission/functions/api/crashes_aggregation.zip \
    --env python \
    --name crashes-aggregation \
    --buildcmd './build.sh'

  fission fn update --spec --name crashes-aggregation \
    --pkg crashes-aggregation \
    --env python \
    --entrypoint "crashes_aggregation.main" \
    --configmap shared-data \
    --secret es-secret \
    --fntimeout 600
)
```

## Create spec files for SUDO SA3 data APIs

**SA3 joined data**

```bash
zip -jr fission/functions/api/sa3_joined/joined.zip \
fission/functions/api/sa3_joined/

(
cd fission
fission route create --spec --name data-joined-by-sa3 --function data-joined-by-sa3 \
--method GET \
--url '/sa3-joined/all'
)


(
cd fission
fission package create --spec --name data-joined-by-sa3 \
--sourcearchive ./functions/api/sa3_joined/joined.zip \
--env python \
--buildcmd './build.sh'

fission fn create --spec --name data-joined-by-sa3 \
--pkg data-joined-by-sa3 \
--env python \
--configmap shared-data \
--secret es-secret \
--entrypoint "sa3-joined.main"
)
```

**SA3 geometry data**
```bash
zip -jr fission/functions/api/sa3-data/sa3-data.zip \
fission/functions/api/sa3-data/

(
cd fission
fission route create --spec --name get-sa3-geojson --function get-sa3-geojson \
--method GET \
--url '/get-sa3-geojson'
)


(
cd fission
fission package create --spec --name get-sa3-geojson \
--sourcearchive ./functions/api/sa3-data/sa3-data.zip \
--env python \
--buildcmd './build.sh'

fission fn create --spec --name get-sa3-geojson \
--pkg get-sa3-geojson \
--env python \
--configmap shared-data \
--secret es-secret \
--entrypoint "get_sa3_geo.main"
)
```

**Median Age SA3 data
```bash

zip -jr fission/functions/api/median-data/median-age/median-age.zip \
fission/functions/api/median-data/median-age/

(
cd fission
fission route create --spec --name median-age-by-sa3 --function median-age-by-sa3 \
--method GET \
--url '/median/age/sa3/{SA3Code:[0-9]+}'
)


(
cd fission
fission package create --spec --name median-age-by-sa3 \
--sourcearchive ./functions/api/median-data/median-age/median-age.zip \
--env python \
--buildcmd './build.sh'

fission fn create --spec --name median-age-by-sa3 \
--pkg median-age-by-sa3 \
--env python \
--configmap shared-data \
--secret es-secret \
--entrypoint "median-age.main"
)
```

**median income sa3 data**
```bash
zip -jr fission/functions/api/median-income/median-income.zip \
fission/functions/api/median-income/

(
cd fission
fission route create --spec --name median-income --function median-income \
--method GET \
--url '/median-income/{LGACode:[0-9]+}'
)


(
cd fission
fission package create --spec --name median-income \
--sourcearchive ./functions/api/median-income/median-income.zip \
--env python \
--buildcmd './build.sh'

fission fn create --spec --name median-income \
--pkg median-income \
--env python \
--configmap shared-data \
--entrypoint "median-income.main"
)
```

**level of schooling sa3 data**
```bash
zip -jr fission/functions/api/level-of-schooling/level-of-schooling.zip \
fission/functions/api/level-of-schooling/

(
cd fission
fission route create --spec --name level-of-schooling-by-sa3 --function level-of-schooling-by-sa3 \
--method GET \
--url '/highest-level-of-schooling/sa3/{SA3Code:[0-9]+}'
)


(
cd fission
fission package create --spec --name level-of-schooling-by-sa3 \
--sourcearchive ./functions/api/level-of-schooling/level-of-schooling.zip \
--env python \
--buildcmd './build.sh'

fission fn create --spec --name level-of-schooling-by-sa3 \
--pkg level-of-schooling-by-sa3 \
--env python \
--configmap shared-data \
--secret es-secret \
--entrypoint "level-of-schooling.main"
)
```

**age by sex sa3 data**
```bash
zip -jr fission/functions/api/age-by-sex/age-by-sex.zip \
fission/functions/api/age-by-sex/

(
cd fission
fission route create --spec --name age-by-sex-by-sa3 --function age-by-sex-by-sa3 \
--method GET \
--url '/age-by-sex/sa3/{SA3Code:[0-9]+}'
)


(
cd fission
fission package create --spec --name age-by-sex-by-sa3 \
--sourcearchive ./functions/api/age-by-sex/age-by-sex.zip \
--env python \
--buildcmd './build.sh'

fission fn create --spec --name age-by-sex-by-sa3 \
--pkg age-by-sex-by-sa3 \
--env python \
--configmap shared-data \
--secret es-secret \
--entrypoint "age-by-sex.main"
)
```

Verify the specs

```bash
(
  cd fission
  fission spec validate
)
```

Provided no error, let's apply the specs

```bash
fission spec apply --specdir fission/specs --wait
```

Before you test the function from your local machine, you need to port-forward the Fission router to your local machine
execute the following command in a new terminal window.
```bash
kubectl port-forward service/router -n fission 9090:80
```

To verify the function logs

```bash
fission function log -f --name <function_name>
```

Test the function
```bash
curl "http://127.0.0.1:9090/epamonitoringsites" | jq '.'
```

Add the http triggers

```bash
(
  cd fission
  
  fission timer create --spec --name epamonitoringsites-trigger --function epamonitoringsites --cron "@every 1h"
  fission timer create --spec --name wharvester-trigger --function wharvester --cron "@every 30m"

  fission httptrigger create --spec --name enqueue --url "/enqueue/{topic}" --method POST --function enqueue

  fission mqtrigger create --name add-epa-observations \
    --spec\
    --function addepadata \
    --mqtype kafka \
    --mqtkind keda \
    --topic airmonitoringsites \
    --errortopic errors \
    --maxretries 3 \
    --metadata bootstrapServers=my-cluster-kafka-bootstrap.kafka.svc:9092 \
    --metadata consumerGroup=my-group \
    --cooldownperiod=30 \
    --pollinginterval=5
    
  fission mqtrigger create --name add-weather-observations \
    --spec\
    --function addweatherdata \
    --mqtype kafka \
    --mqtkind keda \
    --topic weather \
    --errortopic errors \
    --maxretries 3 \
    --metadata bootstrapServers=my-cluster-kafka-bootstrap.kafka.svc:9092 \
    --metadata consumerGroup=my-group \
    --cooldownperiod=30 \
    --pollinginterval=5
)
```