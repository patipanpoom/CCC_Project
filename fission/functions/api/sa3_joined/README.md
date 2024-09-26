zip -jr fission/functions/api/sa3_joined/joined.zip \
fission/functions/api/sa3_joined/

(
cd fission
fission route create --spec --name data-joined-by-sa3 --function data-joined-by-sa3 \
--method GET \
--url '/sa3-joined/all'
)

`
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
`
fission spec apply --specdir fission/specs --wait 

curl "http://localhost:9090/sa3-joined/all"
38
