zip -jr fission/functions/api/median-data/median-income/median-income.zip \
fission/functions/api/median-data/median-income/

(
cd fission
fission route create --spec --name median-income-by-sa3 --function median-income-by-sa3 \
--method GET \
--url '/median/income/sa3/{SA3Code:[0-9]+}'
)

`
(
cd fission
fission package create --spec --name median-income-by-sa3 \
--sourcearchive ./functions/api/median-data/median-income/median-income.zip \
--env python \
--buildcmd './build.sh'

fission fn create --spec --name median-income-by-sa3 \
--pkg median-income-by-sa3 \
--env python \
--configmap shared-data \
--secret es-secret \
--entrypoint "median-income.main"
)
`
fission spec apply --specdir fission/specs --wait && curl "http://localhost:9090/median/income/sa3/12101"


1,255
