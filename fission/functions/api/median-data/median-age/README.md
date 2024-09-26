zip -jr fission/functions/api/median-data/median-age/median-age.zip \
fission/functions/api/median-data/median-age/

(
cd fission
fission route create --spec --name median-age-by-sa3 --function median-age-by-sa3 \
--method GET \
--url '/median/age/sa3/{SA3Code:[0-9]+}'
)

`
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
`
fission spec apply --specdir fission/specs --wait 

curl "http://localhost:9090/median/age/sa3/12101"
38
