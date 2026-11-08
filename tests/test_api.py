import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import awsip  # noqa: E402
from app import app  # noqa: E402

FAKE_PREFIXES = [
    {"ip_prefix": "3.5.140.0/22", "region": "ap-northeast-2", "service": "AMAZON",
     "network_border_group": "ap-northeast-2"},
    {"ip_prefix": "3.5.140.0/22", "region": "ap-northeast-2", "service": "S3",
     "network_border_group": "ap-northeast-2"},
]


@pytest.fixture
def client(monkeypatch):
    # pas de réseau : on remplace le téléchargement par les fausses données
    monkeypatch.setattr(awsip, "download_aws_ip_set", lambda: FAKE_PREFIXES)
    return app.test_client()


# ---------- GET /api/lookup ----------

def test_lookup_ip_aws(client):
    r = client.get("/api/lookup?ip=3.5.140.10")
    data = r.get_json()
    assert r.status_code == 200
    assert data["ip"] == "3.5.140.10"
    assert data["is_aws"] is True
    assert len(data["ranges"]) == 2


def test_lookup_ip_non_aws(client):
    r = client.get("/api/lookup?ip=8.8.8.8")
    assert r.status_code == 200
    assert r.get_json() == {"ip": "8.8.8.8", "is_aws": False, "ranges": []}


@pytest.mark.parametrize("url", [
    "/api/lookup",            # paramètre absent
    "/api/lookup?ip=",        # vide
    "/api/lookup?ip=abc",     # invalide
    "/api/lookup?ip=::1",     # IPv6 refusée
])
def test_lookup_erreurs(client, url):
    r = client.get(url)
    assert r.status_code == 400
    assert "error" in r.get_json()


# ---------- POST /api/check-list ----------

def test_check_list_ok(client):
    r = client.post("/api/check-list", json={"ips": ["3.5.140.10", " 3.5.141.2 "]})
    assert r.status_code == 200
    assert r.get_json() == {
        "results": [
            {"ip": "3.5.140.10", "is_aws": True},
            {"ip": "3.5.141.2", "is_aws": True},
        ],
        "all_aws": True,
        "same_network": True,
        "common_ranges": ["3.5.140.0/22"],
    }


def test_check_list_ip_non_aws(client):
    data = client.post("/api/check-list", json={"ips": ["3.5.140.10", "8.8.8.8"]}).get_json()
    assert data["all_aws"] is False
    assert data["same_network"] is False


@pytest.mark.parametrize("body", [
    {},                         # pas de clé ips
    {"ips": []},                # liste vide
    {"ips": ["", "  "]},        # que des vides
    {"ips": "3.5.140.10"},      # pas une liste
    ["3.5.140.10"],             # body qui n'est pas un objet
])
def test_check_list_liste_absente_ou_vide(client, body):
    r = client.post("/api/check-list", json=body)
    assert r.status_code == 400


def test_check_list_body_pas_json(client):
    r = client.post("/api/check-list", data="pas du json")
    assert r.status_code == 400


def test_check_list_ip_invalide(client):
    r = client.post("/api/check-list", json={"ips": ["3.5.140.10", "zz"]})
    assert r.status_code == 400
    assert "zz" in r.get_json()["error"]

# ---------- GET / ----------

def test_page_accueil(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"AWS IP Checker" in r.data