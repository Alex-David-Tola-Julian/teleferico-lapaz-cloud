from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    """
    Test simple para verificar que la configuración base está respondiendo.
    En una app real sin ruta raíz (/), probamos el endpoint de configuración en su lugar.
    """
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    
    # Verificamos que la estructura JSON básica sea la esperada
    assert "fecha_min" in data
    assert "fecha_max" in data
    assert "lineas_disp" in data
    assert isinstance(data["lineas_disp"], list)

def test_cloud_status():
    """
    Verifica que el status general del backend y los datos respondan correctamente.
    """
    response = client.get("/api/cloud-status")
    assert response.status_code == 200
    data = response.json()
    
    assert "data_source" in data
    assert "total_registros" in data
    assert "total_lineas" in data
    assert type(data["total_registros"]) is int
