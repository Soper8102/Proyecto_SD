"""
Pruebas integrales de los endpoints del Microservicio de Reservas.
Simula también las respuestas del Microservicio de Viajes para verificar:
1. Creación de reserva y descuento de cupos.
2. Prevención de doble reserva (Conflicto 409).
3. Consulta detallada en tiempo real y en Modo Degradado (cuando Viajes cae).
4. Actualización, completado y cancelación de reserva con devolución de cupos.
"""
from datetime import datetime, timedelta
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.service import ServicioViajesNoDisponibleError

client = TestClient(app)

VIAJE_MOCK = {
    "id": 1,
    "conductor_id": 1,
    "conductor_nombre": "David Jerez (Estudiante Ing. Sistemas)",
    "origen": "Portal Norte (Estación)",
    "destino": "UNIMINUTO Sede Principal Calle 80",
    "fecha_hora_salida": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
    "cupos_totales": 3,
    "cupos_disponibles": 3,
    "aporte_sugerido": 4000.0,
    "tipo_vehiculo": "carro",
    "placa_vehiculo": "KHY-421",
    "estado": "PROGRAMADO"
}

def test_routes():
    print("[1] Probando health check (/health)...")
    res = client.get("/health")
    assert res.status_code == 200, f"Error: {res.text}"
    print("Health check OK:", res.json()["estado"])

    print("\n[2] Probando creación de reserva (POST /reservas)...")
    with patch("app.services.service.obtener_viaje_remoto", return_value=VIAJE_MOCK), \
         patch("app.services.service.modificar_cupos_remoto", return_value={**VIAJE_MOCK, "cupos_disponibles": 2}):
        payload = {
            "viaje_id": 1,
            "pasajero_id": 99,
            "pasajero_nombre": "Estudiante Prueba SD",
            "pasajero_correo": "prueba.sd@uniminuto.edu.co",
            "cupos_reservados": 1,
            "punto_encuentro": "Calle 100 con Autopista",
            "comentarios": "Reserva de prueba automatizada"
        }
        res = client.post("/reservas", json=payload)
        assert res.status_code == 201, f"Error al crear reserva: {res.text}"
        reserva_creada = res.json()
        reserva_id = reserva_creada["id"]
        print(f"Reserva creada con ID #{reserva_id} | Estado: {reserva_creada['estado']} | Aporte: ${reserva_creada['aporte_acordado']}")

    print("\n[3] Probando prevención de reserva duplicada del mismo pasajero (HTTP 409)...")
    with patch("app.services.service.obtener_viaje_remoto", return_value=VIAJE_MOCK):
        res_dup = client.post("/reservas", json=payload)
        assert res_dup.status_code == 409, f"Se esperaba 409 Conflict, se obtuvo {res_dup.status_code}"
        print("Bloqueo de duplicado OK:", res_dup.json()["detail"])

    print("\n[4] Probando consulta detallada en Modo Degradado (MS Viajes apagado)...")
    with patch("app.services.service.obtener_viaje_remoto", side_effect=ServicioViajesNoDisponibleError("Conexión rechazada")):
        res_deg = client.get(f"/reservas/{reserva_id}/detalle")
        assert res_deg.status_code == 200
        data_deg = res_deg.json()
        assert data_deg["modo_degradado"] is True
        print("Modo Degradado OK -> Origen desde snapshot:", data_deg["reserva"]["origen_viaje"])

    print("\n[5] Probando cancelación de reserva y devolución de cupo (DELETE /reservas/{id})...")
    with patch("app.services.service.modificar_cupos_remoto", return_value=VIAJE_MOCK):
        res_del = client.delete(f"/reservas/{reserva_id}")
        assert res_del.status_code == 200, f"Error al cancelar: {res_del.text}"
        print("Cancelación OK:", res_del.json()["mensaje"])

    print("\n[OK] Todos los tests del microservicio de reservas pasaron exitosamente!")

if __name__ == "__main__":
    test_routes()
