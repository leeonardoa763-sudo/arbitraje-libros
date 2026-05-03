from __future__ import annotations

import secrets

from fastapi.security import HTTPBasicCredentials


def verify_credentials(
    credentials: HTTPBasicCredentials,
    *,
    expected_username: str,
    expected_password: str,
) -> bool:
    """Compara credenciales con tiempo constante para prevenir timing attacks.

    Args:
        credentials: Credenciales recibidas en el header HTTP Basic.
        expected_username: Nombre de usuario correcto (de Settings).
        expected_password: Contraseña correcta (de Settings).

    Returns:
        True si ambas credenciales son correctas.
    """
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        expected_username.encode("utf-8"),
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        expected_password.encode("utf-8"),
    )
    return correct_username and correct_password
