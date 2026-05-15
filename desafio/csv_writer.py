import csv
import logging

logger = logging.getLogger(__name__)


def write_csv(rows: list, filename: str) -> None:
    """
    Writes the processed data to a CSV file with the required headers.

    Args:
        rows: List of lists containing the data for each user. Each inner list must
              follow the order: full name, phone, original email, company, city, 
              corporate email.
        filename: Name of the output CSV file.

    Returns:
        None
    """
    headers = [
        "Nombre completo",
        "Teléfono",
        "Correo electrónico original",
        "Empresa para la cual trabaja",
        "Ciudad",
        "Correo corporativo generado"
    ]

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        logger.info(f"CSV file '{filename}' successfully generated with {len(rows)} records.")
    except IOError as e:
        logger.error(f"Failed to write CSV file '{filename}': {e}")