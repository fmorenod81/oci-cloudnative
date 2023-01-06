README.md

## DEMO AUTOESCALAMIENTO OKE
Ultima Actualizacion: 5-Enero-2023

- [DEMO AUTOESCALAMIENTO OKE](#demo-autoescalamiento-oke)
  - [Kubernetes Sencillo](#kubernetes-sencillo)
  - [Horizontal Autopodscaler](#horizontal-autopodscaler)
  - [Cluster Autoscaler](#cluster-autoscaler)

### Kubernetes Sencillo
Primero, crear el Kubernetes usando el Quick Create Cluster, siguiendo https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengcreatingclusterusingoke_topic-Using_the_Console_to_create_a_Quick_Cluster_with_Default_Settings.htm#create-quick-cluster

  

Usar Kubernetes API Endpoint como Public, Kubernetes Worker Nodes como Private y Number of Nodes a 1. El resto de las configuraciones puede ser dejadas como valores por defecto. Toma alrededor de 10 mins.

  

Luego, se ingresa al Cluster desde el Cloud Shell, siguiendo https://www.oracle.com/webfolder/technetwork/tutorials/obe/oci/oke-cloudshell/index.html hasta el paso 4.

  

Se pueden lanzar estos comandos para probar funcionalidad

  
`kubectl get nodes`

```console
NAME STATUS ROLES AGE VERSION
10.0.10.37 Ready node 16m v1.24.1
```
`kubectl get pods --all-namespaces`

```console
NAMESPACE NAME READY STATUS RESTARTS AGE
kube-system coredns-746957c9c6-mh8qn 1/1 Running 0 24m
kube-system csi-oci-node-6r6bq 1/1 Running 1 (14m ago) 16m
kube-system kube-dns-autoscaler-6f789cfb88-qjvvc 1/1 Running 0 24m
kube-system kube-flannel-ds-pjjsf 1/1 Running 1 (14m ago) 16m
kube-system kube-proxy-kd9p2 1/1 Running 0 16m
kube-system proxymux-client-5h55j 1/1 Running 0 16m
```

`kubectl create -f ngninx-service.yml`

```console
deployment.apps/nginx created
service/nginx created
```

`kubectl get pods --all-namespaces`

```console
NAMESPACE NAME READY STATUS RESTARTS AGE
default nginx-78878bf58d-7hcxd 1/1 Running 0 117s
default nginx-78878bf58d-glxvn 1/1 Running 0 117s
kube-system coredns-746957c9c6-mh8qn 1/1 Running 0 24m
kube-system csi-oci-node-6r6bq 1/1 Running 1 (15m ago) 17m
kube-system kube-dns-autoscaler-6f789cfb88-qjvvc 1/1 Running 0 24m
kube-system kube-flannel-ds-pjjsf 1/1 Running 1 (15m ago) 17m
kube-system kube-proxy-kd9p2 1/1 Running 0 17m
kube-system proxymux-client-5h55j 1/1 Running 0 17m
```

`kubectl get svc --all-namespaces`

```console
NAMESPACE NAME TYPE CLUSTER-IP EXTERNAL-IP PORT(S) AGE
default kubernetes ClusterIP 10.96.0.1 <none> 443/TCP,12250/TCP 26m
default nginx LoadBalancer 10.96.75.15 132.226.37.80 80:32688/TCP 2m35s
kube-system kube-dns ClusterIP 10.96.5.5 <none> 53/UDP,53/TCP,9153/TCP 25m
```

  

Tomar la informacion del External-IP

  
`curl 132.226.37.80`

  

```html
<!DOCTYPE  html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
.....

```

  
`kubectl delete -f ngninx-service.yml`

```console
deployment.apps "nginx" deleted
service "nginx" deleted
```

### Horizontal Autopodscaler

  

Adaptado de https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengdeployingmetricsserver.htm#Deploying_Kubernetes_Metrics_Server_Using_Kubectl y de https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/

  
  
  

Si sale Not Found al usar
`kubectl get deployment metrics-server -n kube-system`

```

Error from server (NotFound): deployments.apps "metrics-server" not found

```

  

Estos cambios se toman de https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengdeployingmetricsserver.htm#Deploying_Kubernetes_Metrics_Server_Using_Kubectl y la ultima version Metrics Server se toma de de https://github.com/kubernetes-sigs/metrics-server/releases; para este caso, la ultima version es la v0.6.2

  
`kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.6.2/components.yaml`

```console
serviceaccount/metrics-server created
clusterrole.rbac.authorization.k8s.io/system:aggregated-metrics-reader created
clusterrole.rbac.authorization.k8s.io/system:metrics-server created
rolebinding.rbac.authorization.k8s.io/metrics-server-auth-reader created
clusterrolebinding.rbac.authorization.k8s.io/metrics-server:system:auth-delegator created
clusterrolebinding.rbac.authorization.k8s.io/system:metrics-server created
service/metrics-server created
deployment.apps/metrics-server created
apiservice.apiregistration.k8s.io/v1beta1.metrics.k8s.io created
```

  

Volver a lanzar
`kubectl get deployment metrics-server -n kube-system`

```console
NAME READY UP-TO-DATE AVAILABLE AGE
metrics-server 1/1 1 1 40s
```

  
  
`kubectl apply -f https://k8s.io/examples/application/php-apache.yaml`

```
deployment.apps/php-apache created
service/php-apache created
```

  

Primero se mira si ya existe un hpa

  
`kubectl get hpa`

  

sino se procede a borrar

`kubectl delete hpa php-apache`

```console
horizontalpodautoscaler.autoscaling "php-apache" deleted
```

  
`kubectl autoscale deployment php-apache --cpu-percent=50 --min=1 --max=10`

```
horizontalpodautoscaler.autoscaling/php-apache autoscaled
```

Se comprueba
  
`kubectl get hpa`

```
NAME REFERENCE TARGETS MINPODS MAXPODS REPLICAS AGE
php-apache Deployment/php-apache 0%/50% 1 10 1 67s
```
  

En otra cloud shell, se lanza un script que genera stress en la carga

`kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://php-apache; done"`

```console
OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK......
.....
```

Se vuelve al cloud shell inicial, y se lanza
`kubectl get hpa --watch`

```console
NAME REFERENCE TARGETS MINPODS MAXPODS REPLICAS AGE
php-apache Deployment/php-apache 0%/50% 1 10 1 113s
php-apache Deployment/php-apache 196%/50% 1 10 1 2m45s
php-apache Deployment/php-apache 247%/50% 1 10 4 3m1s
php-apache Deployment/php-apache 105%/50% 1 10 5 3m16s
php-apache Deployment/php-apache 63%/50% 1 10 5 3m31s
php-apache Deployment/php-apache 64%/50% 1 10 5 3m46s
....
```

  

Se vuelve a la pantalla del stress, y se presiona Ctrl+C y Enter

```console
OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!OK!^C
E0105 14:10:33.861290 12591 v2.go:105] EOF
pod "load-generator" deleted
pod default/load-generator terminated (Error)
```

  

Se vuelve a la pantalla de cloud shell inicial, y se mira como se empieza a bajar la carga y las replicas. Toma alrededor de 5 mins para que se baje la carga.

```console
php-apache Deployment/php-apache 52%/50% 1 10 7 5m46s
php-apache Deployment/php-apache 28%/50% 1 10 7 6m1s
php-apache Deployment/php-apache 8%/50% 1 10 7 6m17s
php-apache Deployment/php-apache 0%/50% 1 10 7 6m32s
php-apache Deployment/php-apache 0%/50% 1 10 7 10m
php-apache Deployment/php-apache 0%/50% 1 10 4 11m
php-apache Deployment/php-apache 0%/50% 1 10 2 11m
php-apache Deployment/php-apache 0%/50% 1 10 1 11m
```

  
  
  

### Cluster Autoscaler 

Se toma de https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengusingclusterautoscaler.htm#Using_the_Kubernetes_Cluster_Autoscaler

  

Para ello es importante conocer el compartment (ocid y nombre) donde esta el cluster de Kubernetes,

  

Obtener el id del Comparment, https://cloud.oracle.com/identity/compartments

  

Crear el DynamicGroup

  

Ejemplo en mi caso, el compartment es el ocid1.compartment.oc1..aaaaaaaaliz2p7sbg55m7hbkqpks2p2wqhjqlgp7pyuubyykh2qbwzcbiwoa

Por tanto, tengo que crear el DynamicGroup en https://cloud.oracle.com/sfo/identity/dynamicgroups
`
ALL {instance.compartment.id = 'ocid1.compartment.oc1..aaaaaaaaliz2p7sbg55m7hbkqpks2p2wqhjqlgp7pyuubyykh2qbwzcbiwoa'}
`
Con un nombre acme-oke-cluster-autoscaler-dyn-grp

  

Crear la Politica

  

Desde la raiz del Compartment, se crea la politica en https://cloud.oracle.com/identity/policies

Con un nombre acme-oke-cluster-autoscaler-dyn-grp-policy

  

Crear el archivos Cluster Autoscaler configuration

  

Se copia el archivo desde https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengusingclusterautoscaler.htm#Using_the_Kubernetes_Cluster_Autoscaler

Modificando reemplazando:

  

{{ image tag }} por la region y por la version de Kubernetes en mi caso seria 1.24.0-5, por tanto la imagen seria la
`
iad.ocir.io/oracle/oci-cluster-autoscaler:1.24.0-5
`
  

{{ node pool ocid 1 }} por la ocid del pool ocid, en mi caso seria

ocid1.nodepool.oc1.iad.aaaaaaaaqbqrtatiyfslpelwtsgveivou56x3thwrx7me3mfnnvtnsl6qpfa

  

Borrar la TODA linea que dice {{ node pool ocid 1 }}

  

Finalmente se despliegue el archivo de configuracion en el cluster
`kubectl apply -f cluster-autoscaler.yaml`

```console
serviceaccount/cluster-autoscaler created
clusterrole.rbac.authorization.k8s.io/cluster-autoscaler created
role.rbac.authorization.k8s.io/cluster-autoscaler created
clusterrolebinding.rbac.authorization.k8s.io/cluster-autoscaler created
rolebinding.rbac.authorization.k8s.io/cluster-autoscaler created
deployment.apps/cluster-autoscaler created

```

  
`kubectl create -f nginx-autoscaler.yaml`

```console
deployment.apps/nginx-deployment created
```

`kubectl scale deployment nginx-deployment --replicas=100`

```
deployment.apps/nginx-deployment scaled
```

  
`kubectl get deployment nginx-deployment --watch`

```
NAME READY UP-TO-DATE AVAILABLE AGE
nginx-deployment 28/100 100 28 10m
nginx-deployment 29/100 100 29 11m
nginx-deployment 30/100 100 30 11m
nginx-deployment 31/100 100 31 11m
```

  
  
`kubectl get nodes`

```console
NAME STATUS ROLES AGE VERSION
10.0.10.37 Ready node 4h12m v1.24.1
```
```shell
francisco_@cloudshell:~ (us-ashburn-1)$ kubectl get nodes

NAME STATUS ROLES AGE VERSION
10.0.10.37 Ready node 4h13m v1.24.1
10.0.10.47 NotReady <none> 23s v1.24.1
```
```shell
francisco_@cloudshell:~ (us-ashburn-1)$ kubectl get nodes
NAME STATUS ROLES AGE VERSION
10.0.10.37 Ready node 4h13m v1.24.1
10.0.10.47 NotReady <none> 46s v1.24.1
10.0.10.59 NotReady <none> 15s v1.24.1
```
```shell
francisco_@cloudshell:~ (us-ashburn-1)$ kubectl get nodes
NAME STATUS ROLES AGE VERSION
10.0.10.37 Ready node 4h15m v1.24.1
10.0.10.47 Ready node 2m20s v1.24.1
10.0.10.59 Ready node 109s v1.24.1
```