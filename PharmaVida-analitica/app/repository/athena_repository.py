import time
import boto3
import os


def ejecutar_en_athena(query: str):
    """
    Ejecuta una consulta SQL en AWS Athena y devuelve los resultados parseados.
    La configuración (credenciales, región, base de datos y ubicación de resultados)
    se toma desde las variables de entorno definidas en el archivo .env.
    """

    # Inicializar cliente de Athena
    athena = boto3.client(
        "athena",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN")
    )

    # Parámetros obtenidos del entorno
    database = os.getenv("ATHENA_DATABASE")
    output_location = os.getenv("ATHENA_OUTPUT_LOCATION")
    workgroup = os.getenv("ATHENA_WORKGROUP", "primary")

    if not database or not output_location:
        return {
            "error": "Faltan variables de entorno: ATHENA_DATABASE o ATHENA_OUTPUT_LOCATION"
        }

    try:
        # Ejecutar consulta
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": database},
            ResultConfiguration={
                "OutputLocation": output_location,
                "EncryptionConfiguration": {"EncryptionOption": "SSE_S3"}
            },
            WorkGroup=workgroup
        )

        execution_id = response["QueryExecutionId"]
        print(f"🚀 Ejecutando consulta en Athena (ID: {execution_id})")

        # Esperar hasta que la ejecución termine
        status = "RUNNING"
        while status in ["RUNNING", "QUEUED"]:
            time.sleep(1)
            result = athena.get_query_execution(QueryExecutionId=execution_id)
            status = result["QueryExecution"]["Status"]["State"]

        if status == "FAILED":
            reason = result["QueryExecution"]["Status"]["StateChangeReason"]
            print(f"❌ Error en Athena: {reason}")
            return {"error": f"La consulta falló: {reason}"}

        # Si fue exitosa, obtener los resultados
        data = athena.get_query_results(QueryExecutionId=execution_id)
        print(f"✅ Consulta completada con {len(data['ResultSet']['Rows']) - 1} filas.")
        return parsear_resultados(data)

    except Exception as e:
        print(f"⚠️ Excepción al ejecutar Athena: {e}")
        return {"error": str(e)}


def parsear_resultados(data):
    """
    Convierte el resultado de Athena (formato JSON) en una lista de diccionarios legibles.
    """
    rows = data["ResultSet"]["Rows"]
    headers = [col["VarCharValue"] for col in rows[0]["Data"]]
    registros = []

    for row in rows[1:]:
        valores = [col.get("VarCharValue", None) for col in row["Data"]]
        registros.append(dict(zip(headers, valores)))

    return registros
