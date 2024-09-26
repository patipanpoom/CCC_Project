zip -jr fission/functions/api/sa3-data/sa3-data.zip \
fission/functions/api/sa3-data/

(
cd fission
fission route create --spec --name get-sa3-geojson --function get-sa3-geojson \
--method GET \
--url '/get-sa3-geojson'
)

`
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
`
fission spec apply --specdir fission/specs --wait
curl "http://localhost:9090/get-sa3-geojson"


1,255
