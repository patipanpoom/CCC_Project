zip -jr fission/functions/api/level-of-schooling/level-of-schooling.zip \
fission/functions/api/level-of-schooling/

(
cd fission
fission route create --spec --name level-of-schooling-by-sa3 --function level-of-schooling-by-sa3 \
--method GET \
--url '/highest-level-of-schooling/sa3/{SA3Code:[0-9]+}'
)

`
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
`
fission spec apply --specdir fission/specs --wait 

curl "http://localhost:9090/highest-level-of-schooling/sa3/12101"

