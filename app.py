import ipaddress

from flask import Flask, jsonify, render_template, request

import awsip

app = Flask(__name__)


def is_valid_ipv4(value):
    try:
        ipaddress.IPv4Address(value)
        return True
    except ValueError:
        return False


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/lookup")
def lookup():
    ip = request.args.get("ip", "").strip()
    if not is_valid_ipv4(ip):
        return jsonify({"error": f"IP invalide ou manquante : '{ip}'"}), 400

    ranges = awsip.find_aws_ip(awsip.download_aws_ip_set(), ip)
    return jsonify({"ip": ip, "is_aws": bool(ranges), "ranges": ranges})


@app.post("/api/check-list")
def check_list():
    body = request.get_json(silent=True)
    raw = body.get("ips") if isinstance(body, dict) else None
    if not isinstance(raw, list):
        raw = []
    ips = [str(ip).strip() for ip in raw if str(ip).strip()]
    if not ips:
        return jsonify({"error": "La liste 'ips' est vide ou absente"}), 400

    invalid = [ip for ip in ips if not is_valid_ipv4(ip)]
    if invalid:
        return jsonify({"error": f"IP invalides : {', '.join(invalid)}"}), 400

    return jsonify(awsip.check_ip_list(awsip.download_aws_ip_set(), ips))


if __name__ == "__main__":
    app.run(debug=True)