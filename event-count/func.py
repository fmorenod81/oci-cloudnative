import io
import json
import pymssql
import logging

from fdk import response

def handler(ctx, data: io.BytesIO=None):

    conn = pymssql.connect(server="150.136.145.231",port=1444, user = "sa", password = "DockerCon!!!", database="BulletinBoard")
    logging.getLogger().info("Inicio de Ejecucion de Logueo - Sura - 8 Sept 10 pm")
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM Events')
    row = cursor.fetchone()
    
    data = {
        "eventCount": row[0]
    }
    conn.close()

    logging.getLogger().info("Fin de Ejecucion de Logueo - Sura - 8 Sept 10 pm")
    return response.Response(
        ctx, response_data=json.dumps(data),
        headers={"Content-Type": "application/json"}
    )
