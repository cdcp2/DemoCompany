import re
import logging
import unicodedata
from collections import defaultdict

logger = logging.getLogger(__name__)

TITLES = {"mr", "mrs", "ms", "miss", "dr", "dra", "prof", "sr", "sra", "srta"}
SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}


def generate_emails(users: list, domain: str) -> None:
    """
    Generates corporate email addresses for a list of users and adds them
    in‑place under the key 'corporate_email'. Handles duplicates by appending
    an incremental number to the username.

    Args:
        users: List of user dictionaries. Each must contain the 'name' key.
        domain: Email domain to append (e.g., '@democompany.com').

    Returns:
        None
    """
    counter = defaultdict(int)

    for user in users:
        full_name = user.get("name")
        if not isinstance(full_name, str) or not full_name.strip():
            logger.warning("Usuario sin nombre, omitiendo generación de correo.")
            user["corporate_email"] = ""
            continue

        try:
            base = generate_base(full_name)
        except ValueError:
            logger.warning("Nombre sin partes utilizables, omitiendo generación de correo.")
            user["corporate_email"] = ""
            continue
        count = counter[base]
        email = f"{base}{count if count > 0 else ''}{domain}"
        counter[base] += 1
        user["corporate_email"] = email


def generate_base(full_name: str) -> str:
    """
    Creates the base username from the full name, taking the first
    letter of the first name and the last name, all lowercase and cleaned.

    Args:
        full_name: Person's full name (e.g., "John Doe").

    Returns:
        String with the base username (e.g., "jdoe").
    """
    parts = full_name.strip().split()
    while parts and parts[0].lower().rstrip(".") in TITLES:
        parts.pop(0)
    while len(parts) > 1 and parts[-1].lower().rstrip(".") in SUFFIXES:
        parts.pop()
    if not parts:
        raise ValueError("El nombre no contiene partes utilizables.")
    first_name = parts[0]
    last_name = parts[-1] if len(parts) > 1 else ""
    clean_first = clean_username_part(first_name)
    clean_last = clean_username_part(last_name)
    if clean_first and clean_last:
        return clean_first[0] + clean_last
    elif clean_first:
        return clean_first
    else:
        raise ValueError("El nombre no contiene letras utilizables.")


def clean_username_part(text: str) -> str:
    """
    Cleans a string by converting to lowercase and removing any non‑alphabetic characters.

    Args:
        text: String to clean.

    Returns:
        Cleaned string containing only lowercase letters.
    """
    normalized = unicodedata.normalize("NFKD", text)
    return re.sub(r'[^a-z]', '', normalized.lower())
