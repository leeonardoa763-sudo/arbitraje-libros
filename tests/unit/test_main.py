from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests del endpoint GET /health."""

    @pytest.mark.unit
    def test_returns_ok(self, client: TestClient) -> None:
        """Verifica que el healthcheck retorna status ok con HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @pytest.mark.unit
    def test_no_auth_required(self, client: TestClient) -> None:
        """Verifica que /health no requiere autenticación (Railway lo pinguea sin auth)."""
        response = client.get("/health")
        assert response.status_code == 200


class TestVersionEndpoint:
    """Tests del endpoint GET /version."""

    @pytest.mark.unit
    def test_returns_version_and_env(self, client: TestClient) -> None:
        """Verifica que /version retorna version y env correctos."""
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "0.1.0"
        assert data["env"] == "development"

    @pytest.mark.unit
    def test_no_auth_required(self, client: TestClient) -> None:
        """Verifica que /version no requiere autenticación."""
        response = client.get("/version")
        assert response.status_code == 200


class TestDashboardAuth:
    """Tests de autenticación en endpoints protegidos."""

    @pytest.mark.unit
    def test_dashboard_requires_auth(self, client: TestClient) -> None:
        """Verifica que el dashboard devuelve 401 sin credenciales."""
        response = client.get("/", auth=None)
        assert response.status_code == 401

    @pytest.mark.unit
    def test_dashboard_wrong_credentials(self, client: TestClient) -> None:
        """Verifica que credenciales incorrectas devuelven 401."""
        response = client.get("/", auth=("wrong_user", "wrong_pass"))
        assert response.status_code == 401

    @pytest.mark.unit
    def test_dashboard_correct_credentials(self, client: TestClient) -> None:
        """Verifica que credenciales correctas permiten acceso al dashboard."""
        response = client.get("/", auth=("testuser", "testpassword"))
        assert response.status_code == 200
