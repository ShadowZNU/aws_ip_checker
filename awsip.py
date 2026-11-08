import urllib.request
import json
import ipaddress
import sys
from functools import lru_cache


@lru_cache(maxsize=1)
def download_aws_ip_set():
    """Downloads the AWS IP range JSON file (once, then cached)."""

    # URL of the AWS IP range JSON file
    aws_ip_range_url = "https://ip-ranges.amazonaws.com/ip-ranges.json"

    # Download the JSON file
    with urllib.request.urlopen(aws_ip_range_url) as url:
        aws_ip_range_data = json.load(url)

    return aws_ip_range_data["prefixes"]


def find_aws_ip(aws_ip_range_data, ip_to_find):
    """Finds the AWS IP ranges that contain the given IP address."""
    ip = ipaddress.ip_address(ip_to_find)
    prefixes = []
    for prefix in aws_ip_range_data:
        network = ipaddress.ip_network(prefix["ip_prefix"])
        if ip in network:
            result = dict(prefix)  # copie : on ne modifie pas les données en cache
            result["number_of_IP"] = (
                2 ** (32 - int(prefix["ip_prefix"].split("/")[1])) - 2
            )
            result["first_network_address"] = str(network.network_address + 1)
            result["last_network_address"] = str(network.broadcast_address - 1)
            prefixes.append(result)
    return prefixes


def check_ip_list(aws_ip_range_data, ips):
    """Checks if all IPs are AWS IPs and if they share a common AWS range."""
    results = []
    common = None
    for ip in ips:
        ranges = find_aws_ip(aws_ip_range_data, ip)
        results.append({"ip": ip, "is_aws": bool(ranges)})
        cidrs = {r["ip_prefix"] for r in ranges}
        common = cidrs if common is None else common & cidrs

    return {
        "results": results,
        "all_aws": all(r["is_aws"] for r in results),
        "same_network": bool(common),
        "common_ranges": sorted(common),
    }


if __name__ == "__main__":
    # python awsip.py <ip>              -> plages AWS de l'IP
    # python awsip.py <ip1> <ip2> ...   -> vérification de la liste
    ips = sys.argv[1:]
    if not ips:
        sys.exit("Usage : python awsip.py <ip> [<ip> ...]")

    if len(ips) == 1:
        output = find_aws_ip(download_aws_ip_set(), ips[0])
    else:
        output = check_ip_list(download_aws_ip_set(), ips)

    sys.stdout.write(json.dumps(output, indent=2))