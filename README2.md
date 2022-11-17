1. Tener acceso a un tenant OCI que no este en capa gratuita
2. Ser usuario administrador de ese tenant 
3. Crear un auth token para ese usuario https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm
4. Crear un repositorio publico en su compartment del tenat
 https://cloud.oracle.com/registry/containers
Por ejemplo, myapp/<iniciales>
----
Lanzar el Cloud Shell

export APP=appfjmd

export FUNCT=funcfjmd

docker version

fn version

docker image prune --all --force

fn list context

fn use context us-ashburn-1

fn update context oracle.compartment-id ocid1.compartment.oc1..
aaaaaaaa4ewy3s376yq5xuvtpwe5nvksw6qjif2qwtor2vjaqcsmd5sw47fq

fn update context oracle.compartment-id <AutomaticamenteGeneraElCompartment>

fn update context registry <region_code>.ocir.io/<os_ns>/<nombre_app>

fn update context registry iad.ocir.io/idy4hyfbs31o/$APP

docker login -u 'idy4hyfbs31o/oracleidentitycloudservice/francisco.m.moreno' iad.ocir.io

docker login -u '<os_ns>/oracleidentitycloudservice/<usuario>' <region_code>.ocir.io

Y aqui se pone el Auth Token

lppg.F.ov2[6L2Vr)fFF

fn list apps

----

Generamos variables de entorno para dejar parametros fijos

~~~~

fn create app $APP

fn create app $APP --annotation oracle.com/oci/subnetIds='["ocid1.subnet.oc1.iad.aaaaaaaacynxpkfcrmloaqv5skh64sm4af5gpdjbebttisno2n6qyondjx3a"]'

fn create app $APP --annotation oracle.com/oci/subnetIds='["<subnet-ocid>"]'

rm -rf $FUNCT

fn init --runtime python $FUNCT

cd $FUNCT
~~~~

Verificar archivos creados

~~~~
oci artifacts container repository create --compartment-id ocid1.compartment.oc1..aaaaaaaa4ewy3s376yq5xuvtpwe5nvksw6qjif2qwtor2vjaqcsmd5sw47fq --display-name $APP/$FUNCT --is-public true 

fn deploy --verbose --app $APP

docker image ls|grep -i $FUNCT

fn invoke $APP $FUNCT

echo -n '{"name":"FranciscoMoreno"}'|fn invoke $APP $FUNCT application/json

fn inspect function $APP $FUNCT

fn inspect function $APP $FUNCT|jq .id|sed -e 's/^"//' -e 's/"$//' 

