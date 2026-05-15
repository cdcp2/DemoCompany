import logging
import requests

logger = logging.getLogger(__name__)


def fetch_users(api_url: str) -> list | None:
    """
    Obtiene la lista de usuarios desde la API.

    Args:
        api_url: URL del endpoint que devuelve datos en formato JSON.

    Returns:
        Lista de diccionarios con los datos de los usuarios, o None si ocurre un error.
    """
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            logger.error("El JSON recibido no es una lista de usuarios.")
            return None
        logger.info(f"Se obtuvieron {len(data)} registros desde la API.")
        return data
    except requests.exceptions.Timeout:
        logger.error("La solicitud a la API excedió el tiempo de espera.")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Error de conexión al contactar la API.")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error inesperado en la solicitud: {e}")
        return None
    except ValueError as e:
        logger.error(f"Respuesta JSON no válida: {e}")
        return None