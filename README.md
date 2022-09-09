"# oci-cloudnative" 

Pasarse a WSL2
---
fn start -d
fn stop
fn start --log-level DEBUG

Crear carpeta vacia

Saber en que contexto estamos
fn list context
fn use context default
fn list apps

export APP=appfjmd
export FUNCT=funcfjmd

fn create app $APP

fn init --runtime python $FUNCT

cd $FUNCT

<Verificar archivos creados>

fn deploy --verbose --app $APP --local

docker image ls|grep -i $FUNCT

fn invoke $APP $FUNCT

echo -n '{"name":"FranciscoMoreno"}'|fn invoke $APP $FUNCT application/json

Mirar el consumo desde el Docker Desktop

fn inspect function $APP $FUNCT

fn inspect function $APP $FUNCT|jq .id|sed -e 's/^"//' -e 's/"$//' > TempFile
export C=$(cat TempFile)
rm TempFile

curl -X "POST" -H "Content-Type: application/json" -d '{"name":"FranciscoMoreno"}' http://localhost:8080/invoke/$C

----
Revisamos los valores de configuracion del contexto por medio de 
cat $HOME/.fn/contexts/<NombreContexto>.yaml
cat $HOME/.fn/contexts/prod.yaml
cat $HOME/.fn/contexts/default.yaml

Cambiamos el contexto
fn use context prod

fn deploy --verbose --app $APP

Ir a la consola a crear la nueva aplicacion, verificar las redes

fn inspect function $APP $FUNCT
fn inspect function $APP $FUNCT|jq .annotations

fn invoke $APP $FUNCT
echo -n '{"name":"FranciscoMoreno"}'|fn invoke $APP $FUNCT application/json

Hacer el cambio de contexto y mirar el Docker Desktop

No se permite la llamada desde un externo sino se publica o se enlaza desde un Evento
fn inspect function $APP $FUNCT|jq .id|sed -e 's/^"//' -e 's/"$//' > TempFile
export C=$(cat TempFile)
rm TempFile
oci fn function invoke --function-id $C --file "-" --body ""
oci fn function invoke --function-id $C --file "-" --body '{"name":"FranciscoMoreno"}'



Se va a la carpeta de event-count y se miran los archivos
Se cambio los logs

export APPOCI=NombreFunction
fn deploy --verbose --app $APPOCI
curl -X POST https://gdrundpiuzmsbixodzrvx3hk4u.apigateway.us-ashburn-1.oci.customer-oci.com/example/event-count
curl -X GET https://gdrundpiuzmsbixodzrvx3hk4u.apigateway.us-ashburn-1.oci.customer-oci.com/example/event-count
curl -k -X GET https://fn.ocidemo.online/example/event-count

Mirar los logs, recordar buscar el Log Group que se llama Default Group y luego, el NombreFunction_invoke
https://cloud.oracle.com/logging/logs?region=us-ashburn-1



---
Finalmente, hacemos la prueba con el ejemplo de Terraform

