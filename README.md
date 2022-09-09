# oci-cloudnative
Francisco Moreno Diaz -  `francisco.m.moreno@oracle.com`


|   FECHAS     |        TEMAS/LABORATORIO                       |
|--------------|------------------------------------------------|
|  12 Agosto   | Desarrollo de aplicaciones Nativa (Kubernetes) |
| 9 Septiembre | Desarrollo de aplicaciones Nativa (Serverless) |
| 11 Noviembre | IaC - Automatizacion de Infrastructura         |
|--------------|------------------------------------------------|


---
## Comandos para ejecutar el laboratorio ##

### Laboratorio Serverless

Cumplir los requisitos (Detallados en https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsconfiguringclient.htm):
* Tener Docker instalados, ejemplo, Windows usar el Docker Desktop con WSL 2, https://docs.docker.com/desktop/windows/wsl/
* Tener el Fn Server Instalado, https://fnproject.io/tutorials/install/
* Tener el OCI CLI instalado y configurado, https://docs.oracle.com/es-ww/iaas/Content/API/SDKDocs/cliconfigure.htm
* Tener un Auth Token para Docker, https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsgenerateauthtokens.htm#Generate_an_Auth_Token_to_Enable_Login_to_Oracle_Cloud_Infrastructure_Registry


Los siguientes comandos funcionan en **WSL2** o en una consola Linux


Iniciar o detener el Fn Server
Tiene que estar funcionando para los comandos.
~~~~
fn start -d
fn stop
fn start --log-level DEBUG
~~~~

Se va a iniciar haciendo un ejemplo sencillo (Hello World!) y despues lo desplegamos en OCI.

Saber en que contexto estamos y pasarnos a un contexto local
~~~~
fn list context
fn use context default
fn list apps
~~~~

Generamos variables de entorno para dejar parametros fijos
~~~~
export APP=appfjmd
export FUNCT=funcfjmd
~~~~

Creamos una aplicacion y luego, un esquema simple usando el FDK de Python.
~~~~
fn create app $APP
fn init --runtime python $FUNCT
cd $FUNCT
~~~~

Verificar archivos creados

~~~~
fn deploy --verbose --app $APP --local
docker image ls|grep -i $FUNCT
fn invoke $APP $FUNCT
echo -n '{"name":"FranciscoMoreno"}'|fn invoke $APP $FUNCT application/json
~~~~

Mirar el consumo desde el Docker Desktop

~~~~
fn inspect function $APP $FUNCT
fn inspect function $APP $FUNCT|jq .id|sed -e 's/^"//' -e 's/"$//' > TempFile
export C=$(cat TempFile)
rm TempFile
~~~~

~~~~
curl -X "POST" -H "Content-Type: application/json" -d '{"name":"FranciscoMoreno"}' http://localhost:8080/invoke/$C
~~~~


----


Revisamos los valores de configuracion del contexto por medio de

~~~~
cat $HOME/.fn/contexts/<NombreContexto>.yaml
cat $HOME/.fn/contexts/prod.yaml
cat $HOME/.fn/contexts/default.yaml
~~~~

Cambiamos el contexto

~~~~
fn use context prod
fn deploy --verbose --app $APP
~~~~

Ir a la consola a crear la nueva aplicacion, verificar las redes

~~~~

fn inspect function $APP $FUNCT
fn inspect function $APP $FUNCT|jq .annotations
fn invoke $APP $FUNCT
echo -n '{"name":"FranciscoMoreno"}'|fn invoke $APP $FUNCT application/json
~~~~

Hacer el cambio de contexto y mirar el Docker Desktop

No se permite la llamada desde un externo sino se publica o se enlaza desde un Evento

https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsinvokingfunctions.htm

~~~~
fn inspect function $APP $FUNCT|jq .id|sed -e 's/^"//' -e 's/"$//' > TempFile
export C=$(cat TempFile)
rm TempFile
oci fn function invoke --function-id $C --file "-" --body ""
oci fn function invoke --function-id $C --file "-" --body '{"name":"FranciscoMoreno"}'
~~~~


Se va a la carpeta de event-count y se miran los archivos

Se cambio los logs

~~~~
export APPOCI=NombreFunction
fn deploy --verbose --app $APPOCI
curl -X POST https://gdrundpiuzmsbixodzrvx3hk4u.apigateway.us-ashburn-1.oci.customer-oci.com/example/event-count
curl -X GET https://gdrundpiuzmsbixodzrvx3hk4u.apigateway.us-ashburn-1.oci.customer-oci.com/example/event-count
curl -k -X GET https://fn.ocidemo.online/example/event-count
~~~~

Mirar los logs, recordar buscar el Log Group que se llama Default Group y luego, el NombreFunction_invoke

~~~~
https://cloud.oracle.com/logging/logs?region=us-ashburn-1
~~~~



Finalmente, hacemos la prueba con el ejemplo de Terraform

Antes de hacerlo es necesario ir a 