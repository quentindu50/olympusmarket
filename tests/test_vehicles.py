def test_create_vehicle(client, auth_headers):
    response = client.post("/api/vehicles", json={
        "license_plate": "BB-123-CC",
        "transport_type": "vsl",
        "brand": "Peugeot",
        "model": "Expert",
        "year": 2022,
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data["transport_type"] == "vsl"


def test_create_vehicle_invalid_type(client, auth_headers):
    response = client.post("/api/vehicles", json={
        "license_plate": "ZZ-999-ZZ",
        "transport_type": "boat",
    }, headers=auth_headers)
    assert response.status_code == 400


def test_list_vehicles(client, auth_headers, sample_vehicle):
    response = client.get("/api/vehicles", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()) >= 1


def test_filter_available_vehicles(client, auth_headers, sample_vehicle):
    response = client.get("/api/vehicles?available=true", headers=auth_headers)
    assert response.status_code == 200


def test_update_mileage(client, auth_headers, sample_vehicle):
    response = client.put(f"/api/vehicles/{sample_vehicle}/mileage",
                          json={"mileage": 50000}, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["mileage"] == 50000.0
