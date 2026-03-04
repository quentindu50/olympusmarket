def test_create_patient(client, auth_headers):
    response = client.post("/api/patients", json={
        "first_name": "Marie",
        "last_name": "Curie",
        "phone": "0698765432",
        "has_ald": True,
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data["first_name"] == "Marie"
    assert data["has_ald"] is True


def test_create_patient_missing_name(client, auth_headers):
    response = client.post("/api/patients", json={"first_name": "NoLastName"}, headers=auth_headers)
    assert response.status_code == 400


def test_list_patients(client, auth_headers, sample_patient):
    response = client.get("/api/patients", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()) >= 1


def test_search_patients(client, auth_headers, sample_patient):
    response = client.get("/api/patients?q=Dupont", headers=auth_headers)
    assert response.status_code == 200
    results = response.get_json()
    assert any(p["last_name"] == "Dupont" for p in results)


def test_get_patient(client, auth_headers, sample_patient):
    response = client.get(f"/api/patients/{sample_patient}", headers=auth_headers)
    assert response.status_code == 200


def test_update_patient(client, auth_headers, sample_patient):
    response = client.put(f"/api/patients/{sample_patient}", json={"phone": "0600000000"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["phone"] == "0600000000"
