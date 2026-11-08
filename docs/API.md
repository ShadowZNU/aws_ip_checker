# Contrat API – AWS IP Checker

- Format : JSON. IPv4 uniquement.
- Erreur : code HTTP 400 + `{"error": "message lisible"}`

## Objet Range (une plage AWS, = sortie du script de base)

```json
{
  "ip_prefix": "3.5.140.0/22",
  "region": "ap-northeast-2",
  "service": "S3",
  "network_border_group": "ap-northeast-2",
  "number_of_IP": 1022,
  "first_network_address": "3.5.140.1",
  "last_network_address": "3.5.143.254"
}
```

Une même plage peut apparaître plusieurs fois (une par service : AMAZON, S3, EC2…).

## GET /

Page HTML.

## Feature 1 – GET /api/lookup?ip=<ip>

L'IP appartient-elle à AWS ?

200 :
```json
{
  "ip": "3.5.140.10",
  "is_aws": true,
  "ranges": [ Range, ... ]
}
```
IP non-AWS → `"is_aws": false, "ranges": []` (toujours 200).

400 : paramètre `ip` absent ou IP invalide.

## Feature 2 – POST /api/check-list

Les IPs sont-elles toutes AWS ? Sont-elles dans le même réseau AWS ?

Body :
```json
{ "ips": ["3.5.140.10", "3.5.141.2"] }
```

200 :
```json
{
  "results": [
    { "ip": "3.5.140.10", "is_aws": true },
    { "ip": "3.5.141.2",  "is_aws": true }
  ],
  "all_aws": true,
  "same_network": true,
  "common_ranges": ["3.5.140.0/22"]
}
```
- `same_network` : vrai si au moins une plage AWS contient **toutes** les IPs.
- `common_ranges` : ces plages (sans doublon), `[]` sinon.

400 : `ips` absent, vide, ou contenant une IP invalide.