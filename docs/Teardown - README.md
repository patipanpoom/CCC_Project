
## Removal of the software stack

## Fission removal

```shell
export FISSION_VERSION='1.20.0'

for e in $(kubectl get function -o=name) ; do
    kubectl delete ${e}
done

for e in $(kubectl get package -o=name) ; do
    kubectl delete ${e}
done

for e in $(kubectl get environment -o=name) ; do
    kubectl delete ${e}
done

for crd in $(kubectl get crd --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}' | grep fission) ; do
    kubectl delete crd ${crd}
done

helm uninstall fission --namespace fission

for p in $(kubectl get pods -o=name) ; do
    kubectl delete ${p}
done

for p in $(kubectl get kafkatopic -n kafka -o=name) ; do
    kubectl delete ${p} -n kafka
done

kubectl delete -k "github.com/fission/fission/crds/v1?ref=v${FISSION_VERSION}"
helm uninstall keda --namespace keda
helm uninstall kafka-ui
kubectl delete kafka my-cluster --namespace kafka
helm uninstall kafka --namespace kafka
```

### ElasticSearch Cluster Removal

```shell
helm uninstall kibana -n elastic
helm uninstall elasticsearch -n elastic
```

### Kubernetes Cluster Removal

```shell
openstack port delete $(openstack port show -f value -c id elastic-bastion)
openstack coe cluster delete elastic
openstack server delete bastion
```

Wait until the volumes became `available` and delete them:
```shell
openstack volume list -f value -c ID | xargs -i openstack volume delete {}
```

Remove the `elastic-ssh` security group:
```shell
openstack security group delete $(openstack security group show -f value -c id elastic-ssh)
```
