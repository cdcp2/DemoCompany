import logging
import sys
import os
from dotenv import load_dotenv

from fetch_data import fetch_users
from email_gen import generate_emails
from csv_writer import write_csv

load_dotenv()

API_URL = os.getenv("API_URL", "https://jsonplaceholder.typicode.com/users")
DOMAIN = os.getenv("DOMAIN", "@democompany.com")
CSV_FILENAME = os.getenv("CSV_FILENAME", "contratistas.csv")
LOG_FILENAME = os.getenv("LOG_FILENAME", "proceso.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler(sys.stdout)
    ]
)


def main() -> None:
    """Orchestrates the full process: fetch, process, and export to CSV."""
    logging.info("Inicio del proceso.")

    users = fetch_users(API_URL)
    if users is None:
        logging.error("No se pudieron obtener los datos de la API. Proceso abortado.")
        sys.exit(1)

    total_obtenidos = len(users)
    logging.info(f"Total de registros obtenidos desde el endpoint: {total_obtenidos}")

    try:
        generate_emails(users, DOMAIN)
        users = [user for user in users if user.get("corporate_email")]
        total_procesados = len(users)
        logging.info(f"Total de registros procesados correctamente: {total_procesados}")
        logging.info(f"Total de registros omitidos: {total_obtenidos - total_procesados}")
    except Exception as e:
        logging.error(f"Error durante la generación de correos: {e}")
        sys.exit(1)

    rows = []
    for u in users:
        nombre = u.get("name", "Sin nombre")
        telefono = u.get("phone", "N/A")
        email_original = u.get("email", "Sin email")
        empresa = u.get("company", {}).get("name", "Sin empresa")
        ciudad = u.get("address", {}).get("city", "Sin ciudad")
        email_corp = u.get("corporate_email", "")

        rows.append([nombre, telefono, email_original, empresa, ciudad, email_corp])

    try:
        write_csv(rows, CSV_FILENAME)
    except OSError:
        sys.exit(1)

    logging.info("Proceso finalizado.")


if __name__ == "__main__":
    main()
