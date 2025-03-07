import requests
import os
import datetime
import time
import boto3

S3_BUCKET = "landing-casas-lambda1"
s3_client = boto3.client("s3")
lambda_client = boto3.client("lambda")  # Cliente de AWS Lambda

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.google.com/",
}

def invoke_lambda2():
    """
    Invoca la función lambda2 después de completar la descarga de HTML.
    """
    lambda_name = "parcial1-bigdata-lambda2"  # Nombre en AWS Lambda

    try:
        response = lambda_client.invoke(
            FunctionName=lambda_name,
            InvocationType="Event"  # Asíncrono
        )
        print(f"Lambda2 invocada con éxito: {response}")
    except Exception as e:
        print(f"Error al invocar Lambda2: {str(e)}")

def download_pages():
    url_base = "https://casas.mitula.com.co/find?operationType=sell&propertyType=mitula_studio_apartment&geoId=mitula-CO-poblacion-0000014156&text=Bogot%C3%A1%2C++%28Cundinamarca%29&page="
    today = datetime.date.today().strftime("%Y-%m-%d")

    for i in range(1, 11):  # Descargar las 10 primeras páginas
        url = url_base + str(i)
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            file_name = f"{today}-page-{i}.html"
            file_path = f"/tmp/{file_name}"  # Guardar temporalmente en Lambda
            
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(response.text)

            # Subir a S3
            s3_client.upload_file(file_path, S3_BUCKET, file_name)
            print(f"Guardado en S3: s3://{S3_BUCKET}/{file_name}")
        else:
            print(f"Error al descargar {url}: {response.status_code}")
    
        time.sleep(3)
        
    print("Descarga completada. Invocando lambda2...")
    invoke_lambda2()  # Llamar a Lambda2 después de completar la descarga

    return {"status": "ok"}

# Ejecutar la función
if __name__ == "__main__":
    download_pages()
