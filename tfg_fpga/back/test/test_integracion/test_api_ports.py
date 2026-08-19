"Test de integración que verifica el recorrido completo de un request"

def test_get_ports_returns_200_with_configured_ports(client):
    response= client.get("/ports")
    assert response.status_code == 200
    assert response.json() == {"ports": [0, 1, 2, 3]}
def test_get_counters_returns_200_for_valid_port(client):
    response = client.get("/ports/0/counters")
    assert response.status_code == 200
    assert response.json()["rx_port_in_frames"] == 0

def test_get_counters_returns__invalid_port(client):

    response = client.get("/ports/8/counters")
    assert response.status_code == 400

def test_configure_generator_bandwidth_returns_200_and_counter(client):
    response = client.post(
        "/ports/0/generator/0/bandwidth",
        json={"enabled": True, "length": 64, "bandwidth_gbps": 1.0},
    )

    assert response.status_code == 200
    assert response.json()["counter"] > 0
def test_configure_generator_bandwidth_invalid_target(client):
    response = client.post(
        "/ports/0/generator/99/bandwidth",
        json={"enabled": True, "length": 64, "bandwidth_gbps": 1.0},
    )

    assert response.status_code == 400

def test_configure_mux_returns_400_for_invalid_rx_mode(client):
    response = client.post(
        "/ports/0/mux",
        json={"rx_mux": "not_a_mode", "tx_mux": None},
    )

    assert response.status_code == 400