"""Testes da API do Scuba Dive Log.

Cena "teste falhando" da demo: mude o nome do app em app/main.py (rota "/")
ou quebre o cálculo de avg_rating em diver_stats e faça push. A etapa de
testes do Dockerfile falha e nenhuma imagem é publicada.
"""


def test_root_identifica_o_app(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["app"] == "Scuba Dive Log"


def test_cria_e_lista_mergulhador(client):
    resp = client.post("/divers", json={"name": "Ana", "cert_level": "Advanced"})
    assert resp.status_code == 200
    diver = resp.json()
    assert diver["id"] > 0

    nomes = [d["name"] for d in client.get("/divers").json()]
    assert "Ana" in nomes


def test_mergulho_exige_mergulhador_existente(client):
    site = client.post("/sites", json={"name": "Laje de Santos"}).json()
    resp = client.post(
        "/dives",
        json={
            "date": "2026-01-10T09:00:00",
            "diver_id": 99999,
            "site_id": site["id"],
            "duration_min": 40,
            "max_depth_m": 18.0,
        },
    )
    assert resp.status_code == 404


def test_estatisticas_do_mergulhador(client):
    diver = client.post("/divers", json={"name": "Bruno"}).json()
    site = client.post("/sites", json={"name": "Arraial do Cabo"}).json()

    mergulhos = [
        {"duration_min": 40, "max_depth_m": 18.0, "tank_pressure_end_bar": 50, "rating": 4},
        {"duration_min": 50, "max_depth_m": 22.0, "tank_pressure_end_bar": 70, "rating": 5},
    ]
    for m in mergulhos:
        resp = client.post(
            "/dives",
            json={
                "date": "2026-02-01T10:00:00",
                "diver_id": diver["id"],
                "site_id": site["id"],
                "tank_pressure_start_bar": 200,
                **m,
            },
        )
        assert resp.status_code == 200

    stats = client.get(f"/divers/{diver['id']}/stats").json()
    assert stats["total_dives"] == 2
    assert stats["total_bottom_time_min"] == 90
    assert stats["avg_max_depth_m"] == 20.0
    assert stats["avg_gas_consumed_bar"] == 140.0
    assert stats["avg_rating"] == 4.5
