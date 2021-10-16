"""Funzioni di utilità generale"""

import re


def shorten_text(text, max_len):
    """Tronca il testo alla lunghezza data, aggiungendo 2 punti di sopsensione

    Args:
        text (str): testo da troncare
        max_len (int): massima lunghezza del testo finale
            (compresi i 2 punti di sospensione)

    Returns:
        str: una stringa lunga al più 'max_len' caratteri
    """
    text = str(text)
    return (text[:max_len-2] + '..') if len(text) > max_len else text


def valid_email(email):
    """Verifica la validità sintattia di una mail

    Args:
        email (str): email da validare

    Returns:
        bool: restituisce True se la mail è valida
    """

    EMAIL_REGEX = r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    pattern = re.compile(EMAIL_REGEX)
    return bool(pattern.match(email))
