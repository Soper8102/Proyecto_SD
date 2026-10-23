from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_routes():
    print("[1] Probando health check...")
    res = client.get("/health")
    assert res.status_code == 200, f"Error: {res.text}"
    print("Health check OK:", res.json())

    print("\n[2] Probando GET / (Listar viajes)...")
    res = client.get("/")
    assert res.status_code == 200, f"Error: {res.text}"
    viajes = res.json()
    print(f"Viajes encontrados: {len(viajes)}")
    assert len(viajes) > 0

    print("\n[3] Probando filtro por origen...")
    res = client.get("/?origen=Norte")
    assert res.status_code == 200
    print(f"Viajes con origen Norte: {len(res.json())}")

    print("\n[4] Probando detalle de viaje por ID (ID 1)...")
    res = client.get("/viajes/1")
    assert res.status_code == 200
    v1 = res.json()
    print("Detalle:", v1["origen"], "->", v1["destino"], "| Cupos:", v1["cupos_disponibles"])

    print("\n[5] Probando descuento de cupo (PATCH /viajes/1/cupos con delta=-1)...")
    cupos_antes = v1["cupos_disponibles"]
    res = client.patch("/viajes/1/cupos", json={"delta_cupos": -1})
    assert res.status_code == 200
    v1_actualizado = res.json()
    print(f"Cupos actualizados de {cupos_antes} a {v1_actualizado['cupos_disponibles']}")
    assert v1_actualizado["cupos_disponibles"] == cupos_antes - 1

    print("\n[6] Restaurando cupo con delta=+1...")
    res = client.patch("/viajes/1/cupos", json={"delta_cupos": 1})
    assert res.status_code == 200
    print("Cupo restaurado a:", res.json()["cupos_disponibles"])

    print("\n[OK] Todos los tests del microservicio de viajes pasaron exitosamente!")

if __name__ == "__main__":
    test_routes()
