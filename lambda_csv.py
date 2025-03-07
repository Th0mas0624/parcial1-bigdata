import os
import datetime
from bs4 import BeautifulSoup
import csv
import boto3

INPUT_BUCKET = "landing-casas-lambda1"
OUTPUT_BUCKET = "casas-final-lambda2"

# Crear carpeta de salida si no existe
s3 = boto3.client("s3")


def process_html():
    today = datetime.date.today().strftime("%Y-%m-%d")
    output_file = f"/tmp/casas_data_{today}.csv"
    csv_data = []
    
    response = s3.list_objects_v2(Bucket=INPUT_BUCKET)
    if "Contents" in response:
        page_number = 0
        for obj in sorted(response["Contents"], key=lambda x: x["Key"]):
            file_name = obj["Key"]
            if file_name.endswith(".html") and today in file_name:
                page_number += 1

                 # Leer el archivo directamente desde S3
                html_obj = s3.get_object(Bucket=INPUT_BUCKET, Key=file_name)
                html_content = html_obj["Body"].read().decode("utf-8")

    
                soup = BeautifulSoup(html_content, "html.parser")
                listings_container = soup.find("div", class_="listings__cards notSponsored")
                listings = listings_container.find_all("a", class_="listing listing-card") if listings_container else []
    
                for listing in listings:
                    barrio = listing.get("data-location", "N/A")
                    valor = listing.get("data-price", "N/A")
                    habitaciones = listing.get("data-rooms", "N/A")
                    banos_tag = listing.find("p", {"data-test": "bathrooms"})
                    banos = banos_tag.text.strip() if banos_tag else "N/A"
                    metros = listing.get("data-floorarea", "N/A")
                    
                    csv_data.append([today, page_number, barrio, valor, habitaciones, banos, metros])
    
    # Si el archivo ya existe, añadir los datos en vez de sobrescribirlo
    if csv_data:
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["FechaDescarga", "Pagina", "Barrio", "Valor", "NumHabitaciones", "NumBanos", "mts2"])
            writer.writerows(csv_data)
    
        s3.upload_file(output_file, OUTPUT_BUCKET, f"casas_data_{today}.csv")
        print(f"CSV guardado en s3://{OUTPUT_BUCKET}/casas_data_{today}.csv")
        
    return {"status": "ok"}

def lambda_handler(event, context):
    """Punto de entrada de Lambda."""
    return process_html()
    
# Ejecutar el procesamiento local
if __name__ == "__main__":
    process_html()
