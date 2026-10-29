import pytest

BASE = "/api/v1"


def test_auth_required(client):
    client.headers.pop("Authorization")
    for method, url in [
        ("get", f"{BASE}/applications"),
        ("post", f"{BASE}/applications"),
        ("get", f"{BASE}/applications/1"),
        ("patch", f"{BASE}/applications/1"),
        ("get", f"{BASE}/borrowers/1042/applications"),
        ("post", f"{BASE}/applications/1/predictions"),
    ]:
        r = getattr(client, method)(url)
        assert r.status_code == 401, url
        assert isinstance(r.json()["detail"], str)


def test_create_application(client):
    r = client.post(f"{BASE}/applications", json={"borrower_id": 1042, "amount_usd": 1500, "term_months": 12})
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending"
    assert body["amount_usd"] == 1500 and body["borrower_id"] == 1042
    assert r.headers["location"].endswith(f"{BASE}/applications/{body['id']}")


@pytest.mark.parametrize(
    "body",
    [
        {"borrower_id": 1042, "amount_usd": 99, "term_months": 12},
        {"borrower_id": 1042, "amount_usd": 5001, "term_months": 12},
        {"borrower_id": 1042, "amount_usd": 1500, "term_months": 5},
        {"borrower_id": 1042, "amount_usd": 1500},
        {"borrower_id": 9999, "amount_usd": 1500, "term_months": 12},
    ],
)
def test_create_application_invalid(client, body):
    r = client.post(f"{BASE}/applications", json=body)
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], str)


def test_get_application(client, make_application):
    app = make_application()
    r = client.get(f"{BASE}/applications/{app['id']}")
    assert r.status_code == 200
    assert r.json() == app


def test_get_application_missing(client):
    r = client.get(f"{BASE}/applications/424242")
    assert r.status_code == 404
    assert r.json() == {"detail": "Application not found"}


def test_list_filters(client, make_application):
    a = make_application(borrower_id=1042)
    b = make_application(borrower_id=1043)
    client.patch(f"{BASE}/applications/{b['id']}", json={"status": "approved"})

    ids = lambda r: [i["id"] for i in r.json()["items"]]
    assert ids(client.get(f"{BASE}/applications")) == [a["id"], b["id"]]
    assert ids(client.get(f"{BASE}/applications", params={"status": "approved"})) == [b["id"]]
    assert ids(client.get(f"{BASE}/applications", params={"province": "Kampong Cham"})) == [a["id"]]
    assert client.get(f"{BASE}/applications", params={"status": "bogus"}).status_code == 422
    assert client.get(f"{BASE}/applications", params={"limit": 101}).status_code == 422


def test_list_pagination(client, make_application):
    created = [make_application()["id"] for _ in range(5)]
    r = client.get(f"{BASE}/applications", params={"limit": 2})
    body = r.json()
    assert [i["id"] for i in body["items"]] == created[:2]
    assert body["next_cursor"] == str(created[1])

    r = client.get(f"{BASE}/applications", params={"limit": 2, "after": body["next_cursor"]})
    assert [i["id"] for i in r.json()["items"]] == created[2:4]

    r = client.get(f"{BASE}/applications", params={"limit": 2, "after": created[3]})
    body = r.json()
    assert [i["id"] for i in body["items"]] == created[4:]
    assert body["next_cursor"] is None


def test_update_status(client, make_application):
    app = make_application()
    r = client.patch(f"{BASE}/applications/{app['id']}", json={"status": "approved"})
    assert r.status_code == 200
    assert r.json()["status"] == "approved"


def test_update_status_errors(client, make_application):
    app = make_application()
    url = f"{BASE}/applications/{app['id']}"
    assert client.patch(f"{BASE}/applications/424242", json={"status": "approved"}).status_code == 404
    assert client.patch(url, json={"status": "bogus"}).status_code == 422
    assert client.patch(url, json={"status": "pending"}).status_code == 422
    client.patch(url, json={"status": "rejected"})
    r = client.patch(url, json={"status": "approved"})
    assert r.status_code == 409
    assert isinstance(r.json()["detail"], str)


def test_borrower_applications(client, make_application):
    a = make_application(borrower_id=1042)
    make_application(borrower_id=1043)
    r = client.get(f"{BASE}/borrowers/1042/applications")
    assert r.status_code == 200
    assert [i["id"] for i in r.json()] == [a["id"]]
    assert client.get(f"{BASE}/borrowers/9999/applications").status_code == 404


def test_create_prediction(client, make_application):
    app = make_application()
    r = client.post(f"{BASE}/applications/{app['id']}/predictions")
    assert r.status_code == 201
    body = r.json()
    assert body["application_id"] == app["id"]
    assert 0 <= body["default_probability"] <= 1
    assert body["model_version"]


def test_create_prediction_missing(client):
    r = client.post(f"{BASE}/applications/424242/predictions")
    assert r.status_code == 404
    assert r.json() == {"detail": "Application not found"}


def test_health(client):
    r = client.get("/health")  # no auth needed
    assert r.status_code in (200, 503)
    body = r.json()
    assert set(body) == {"status", "database", "scoring_server", "model_version"}
    assert body["database"] is True
