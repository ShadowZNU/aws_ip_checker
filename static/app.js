function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function showError(container, message) {
  container.replaceChildren(el("p", message, "badge badge-error"));
}

function showLoading(container) {
  container.replaceChildren(el("p", "Chargement…", "muted"));
}

// Appelle l'API et renvoie le JSON, ou lève une erreur avec le message du back.
async function callApi(url, options) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Erreur ${response.status}`);
  }
  return data;
}

function makeTable(headers, rows) {
  const table = el("table");
  const headRow = el("tr");
  headers.forEach((h) => headRow.appendChild(el("th", h)));
  table.appendChild(el("thead")).appendChild(headRow);

  const body = el("tbody");
  rows.forEach((cells) => {
    const tr = el("tr");
    cells.forEach((c) => tr.appendChild(c instanceof Node ? wrapTd(c) : el("td", String(c))));
    body.appendChild(tr);
  });
  table.appendChild(body);
  return table;
}

function wrapTd(node) {
  const td = el("td");
  td.appendChild(node);
  return td;
}

function badge(ok, yes, no) {
  return el("span", ok ? yes : no, ok ? "badge badge-ok" : "badge badge-no");
}

// ---------- Feature 1 : une IP ----------

const lookupForm = document.getElementById("lookup-form");
const lookupInput = document.getElementById("lookup-ip");
const lookupResult = document.getElementById("lookup-result");

lookupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const ip = lookupInput.value.trim();
  showLoading(lookupResult);

  try {
    const data = await callApi(`/api/lookup?ip=${encodeURIComponent(ip)}`);
    renderLookup(data);
  } catch (err) {
    showError(lookupResult, err.message);
  }
});

function renderLookup(data) {
  const title = el("p", `${data.ip} : `);
  title.appendChild(badge(data.is_aws, "IP AWS", "Pas une IP AWS"));
  lookupResult.replaceChildren(title);

  if (!data.is_aws) return;

  const rows = data.ranges.map((r) => [
    r.ip_prefix,
    r.region,
    r.service,
    r.first_network_address,
    r.last_network_address,
    r.number_of_IP.toLocaleString("fr-FR"),
  ]);
  lookupResult.appendChild(
    makeTable(["Plage", "Région", "Service", "Première IP", "Dernière IP", "Nombre d'IPs"], rows),
  );
}

// ---------- Feature 2 : liste d'IPs ----------

const listForm = document.getElementById("list-form");
const listInput = document.getElementById("list-ips");
const listResult = document.getElementById("list-result");

listForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  // accepte retours à la ligne, virgules, points-virgules et espaces
  const ips = listInput.value.split(/[\s,;]+/).filter((s) => s !== "");
  showLoading(listResult);

  try {
    const data = await callApi("/api/check-list", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ips }),
    });
    renderList(data);
  } catch (err) {
    showError(listResult, err.message);
  }
});

function renderList(data) {
  const summary = el("div", undefined, "summary");

  const line1 = el("p", "Toutes les IPs sont AWS : ");
  line1.appendChild(badge(data.all_aws, "Oui", "Non"));

  const line2 = el("p", "Même réseau AWS : ");
  line2.appendChild(badge(data.same_network, "Oui", "Non"));

  summary.append(line1, line2);

  if (data.same_network) {
    summary.appendChild(el("p", `Plage(s) commune(s) : ${data.common_ranges.join(", ")}`, "muted"));
  }

  const rows = data.results.map((r) => [r.ip, badge(r.is_aws, "AWS", "Non AWS")]);
  listResult.replaceChildren(summary, makeTable(["IP", "Statut"], rows));
}