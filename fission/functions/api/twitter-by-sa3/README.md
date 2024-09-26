zip -jr fission/functions/api/twitter-by-sa3/twitter-by-sa3.zip \
fission/functions/api/twitter-by-sa3/

(
cd fission
fission route create --spec --name twitter-by-sa3 --function twitter-by-sa3 \
--method GET \
--url '/twitter/avgsentiment/sa3/{SA3Code:[0-9]+}'

fission route create --spec --name twitter-by-sa3-and-date --function twitter-by-sa3 \
--method GET \
--url '/twitter/avgsentiment/sa3/{SA3Code:[0-9]+}/start/{StartDate:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/end/{EndDate:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}'
)



(
cd fission
fission package create --spec --name twitter-by-sa3 \
--sourcearchive ./functions/api/twitter-by-sa3/twitter-by-sa3.zip \
--env python \
--buildcmd './build.sh'

fission fn create --spec --name twitter-by-sa3 \
--pkg twitter-by-sa3 \
--env python \
--configmap shared-data \
--secret es-secret \
--entrypoint "get_sentiment.main"
)
`
fission spec apply --specdir fission/specs --wait

curl "http://localhost:9090/twitter/avgsentiment/sa3/12101"
curl "http://localhost:9090/twitter/avgsentiment/sa3/12101/start/2021-09-17/end/2021-09-25"
