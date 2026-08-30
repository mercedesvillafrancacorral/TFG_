
" Test de integración que verifica el endpoint de configuración actual de la FPGA referente a DFX "

def test_list_configurations_returns_200_with_known_configs(dfx_client):
    response = dfx_client.get("/dfx/list_avaible_configurations")
    assert response.status_code == 200
    assert response.json()["configs"] == ["normal", "dfx_dinamica_vlan"]


def test_get_current_configuration_returns_none_initially(dfx_client):
    response = dfx_client.get("/dfx/current_configuration")
    assert response.status_code == 200
    assert response.json() == {
        "message": "No hay ninguna configuración válida cargada actualmente.",
        "current_config": None,
        "is_dfx": None,
    }

def test_get_current_configuration_reflects_dfx_mode_after_load(dfx_client):
    dfx_client.post("/dfx/load_configuration/dfx_dinamica_vlan")

    response = dfx_client.get("/dfx/current_configuration")
    assert response.status_code == 200
    body = response.json()
    assert body["current_config"] == "dfx_dinamica_vlan"
    assert body["is_dfx"] is True


def test_get_current_configuration_reflects_static_mode_after_load(dfx_client):
    dfx_client.post("/dfx/load_configuration/normal")

    response = dfx_client.get("/dfx/current_configuration")
    assert response.json()["is_dfx"] is False


def test_load_unknown_configuration_returns_404(dfx_client):
    response = dfx_client.post("/dfx/load_configuration/no_existe")
    assert response.status_code == 404


def test_load_configuration_returns_500_on_programmer_failure(dfx_client_with_failure):
    response = dfx_client_with_failure.post("/dfx/load_configuration/config_falla")
    assert response.status_code == 500
    assert "fallo simulado" in response.json()["detail"]


def test_load_configuration_warns_when_link_not_ready(dfx_client_link_not_ready):
    response = dfx_client_link_not_ready.post("/dfx/load_configuration/normal")
    assert response.status_code == 200
    assert "retry in a few seconds" in response.json()["message"]