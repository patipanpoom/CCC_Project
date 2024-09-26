# Installation instructions for Jupyter notebooks

Run the following command to install Jupyter notebooks:

```bash
export JH_VERSION="3.3.7"
kubectl create namespace jupyter
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update
helm upgrade --cleanup-on-fail \
  --install jupyterhub jupyterhub/jupyterhub\
  --version=${JS_VERSION} \
  --namespace jupyter \
  --values jupyter/config.yaml
```

### Installation info

- Kubernetes namespace: jupyter
- Helm release name:    jupyterhub
- Helm chart version:   3.3.7
- JupyterHub version:   4.1.5
- Hub pod packages:     See https://github.com/jupyterhub/zero-to-jupyterhub-k8s/blob/3.3.7/images/hub/requirements.txt

### Followup links

- Documentation:  https://z2jh.jupyter.org
- Help forum:     https://discourse.jupyter.org
- Social chat:    https://gitter.im/jupyterhub/jupyterhub
- Issue tracking: https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues

### Post-installation checklist

- Verify that created Pods enter a Running state:

```bash
kubectl --namespace=jupyter get pod
```
  If a pod is stuck with a Pending or ContainerCreating status, diagnose with:

```bash
kubectl --namespace=jupyter describe pod <name of pod>
```
 If a pod keeps restarting, diagnose with:

```bash
kubectl --namespace=jupyter logs --previous <name of pod>
```
- Verify an external IP is provided for the k8s Service proxy-public.

```bash
kubectl --namespace=jupyter get service proxy-public
```
  If the external ip remains <pending>, diagnose with:

  ```bash
  kubectl --namespace=jupyter describe service proxy-public
  ```

- Verify web based access:

  You have not configured a k8s Ingress resource so you need to access the k8s
  Service proxy-public directly.

  If your computer is outside the k8s cluster, you can port-forward traffic to
  the k8s Service proxy-public with kubectl to access it from your
  computer.
```bash
  kubectl --namespace=jupyter port-forward service/proxy-public 8080:http
```

  Try insecure HTTP access: http://localhost:8080


Once the Jupyter notebook is up and running, upload the Jupyter-notebook in this directory to the hub and run all code block to interact with the jupyter notebook and visualisations.
