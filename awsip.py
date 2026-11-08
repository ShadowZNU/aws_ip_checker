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


sys.stdout.write(json.dumps(find_aws_ip(download_aws_ip_set(), sys.argv[1]), indent=2))