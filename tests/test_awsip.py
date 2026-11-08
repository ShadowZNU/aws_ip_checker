import io
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import awsip  # noqa: E402

FAKE_PREFIXES = [
    {"ip_prefix": "3.5.140.0/22", "region": "ap-northeast-2", "service": "AMAZON",
     "network_border_group": "ap-northeast-2"},
    {"ip_prefix": "3.5.140.0/22", "region": "ap-northeast-2", "service": "S3",
     "network_border_group": "ap-northeast-2"},
    {"ip_prefix": "3.5.0.0/16", "region": "us-east-1", "service": "AMAZON",
     "network_border_group": "us-east-1"},
]


# ---------- find_aws_ip ----------

def test_find_aws_ip_trouve_toutes_les_plages():
    ranges = awsip.find_aws_ip(FAKE_PREFIXES, "3.5.140.10")
    assert [(r["ip_prefix"], r["service"]) for r in ranges] == [
        ("3.5.140.0/22", "AMAZON"),
        ("3.5.140.0/22", "S3"),
        ("3.5.0.0/16", "AMAZON"),
    ]


def test_find_aws_ip_calcule_premiere_derniere_et_nombre():
    r = awsip.find_aws_ip(FAKE_PREFIXES, "3.5.140.10")[0]
    assert r["number_of_IP"] == 1022
    assert r["first_network_address"] == "3.5.140.1"
    assert r["last_network_address"] == "3.5.143.254"


def test_find_aws_ip_non_aws_renvoie_liste_vide():
    assert awsip.find_aws_ip(FAKE_PREFIXES, "8.8.8.8") == []


def test_find_aws_ip_ne_modifie_pas_les_donnees():
    awsip.find_aws_ip(FAKE_PREFIXES, "3.5.140.10")
    assert "number_of_IP" not in FAKE_PREFIXES[0]


def test_find_aws_ip_ip_invalide_leve_une_erreur():
    with pytest.raises(ValueError):
        awsip.find_aws_ip(FAKE_PREFIXES, "abc")


# ---------- check_ip_list ----------

def test_check_list_meme_reseau():
    res = awsip.check_ip_list(FAKE_PREFIXES, ["3.5.140.10", "3.5.143.200"])
    assert res["all_aws"] is True
    assert res["same_network"] is True
    assert res["common_ranges"] == ["3.5.0.0/16", "3.5.140.0/22"]


def test_check_list_aws_mais_reseaux_differents_en_partie():
    # 3.5.1.1 est dans le /16 mais pas dans le /22
    res = awsip.check_ip_list(FAKE_PREFIXES, ["3.5.140.10", "3.5.1.1"])
    assert res["all_aws"] is True
    assert res["common_ranges"] == ["3.5.0.0/16"]


def test_check_list_avec_ip_non_aws():
    res = awsip.check_ip_list(FAKE_PREFIXES, ["3.5.140.10", "8.8.8.8"])
    assert res["results"] == [
        {"ip": "3.5.140.10", "is_aws": True},
        {"ip": "8.8.8.8", "is_aws": False},
    ]
    assert res["all_aws"] is False
    assert res["same_network"] is False
    assert res["common_ranges"] == []


def test_check_list_une_seule_ip():
    res = awsip.check_ip_list(FAKE_PREFIXES, ["3.5.140.10"])
    assert res["same_network"] is True


# ---------- download_aws_ip_set (cache) ----------

def test_download_est_mis_en_cache(monkeypatch):
    calls = []

    def fake_urlopen(url):
        calls.append(url)
        return io.BytesIO(json.dumps({"prefixes": FAKE_PREFIXES}).encode())

    monkeypatch.setattr(awsip.urllib.request, "urlopen", fake_urlopen)
    awsip.download_aws_ip_set.cache_clear()

    assert awsip.download_aws_ip_set() == FAKE_PREFIXES
    awsip.download_aws_ip_set()
    assert len(calls) == 1  # un seul téléchargement

    awsip.download_aws_ip_set.cache_clear()