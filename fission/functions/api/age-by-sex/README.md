zip -jr fission/functions/api/age-by-sex/age-by-sex.zip \
fission/functions/api/age-by-sex/

(
cd fission
fission route create --spec --name age-by-sex-by-sa3 --function age-by-sex-by-sa3 \
--method GET \
--url '/age-by-sex/sa3/{SA3Code:[0-9]+}'
)

`
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
`
fission spec apply --specdir fission/specs --wait 

curl "http://localhost:9090/age-by-sex/sa3/12101"
38
