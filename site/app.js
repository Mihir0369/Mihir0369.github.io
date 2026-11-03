(function () {
  var P = window.PROFILE, list = window.PROJECTS;

  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }

  // Profile
  (function () {
    var b = document.getElementById("brand"), parts = P.name.split(" ");
    var m = document.createElement("span"); m.className = "mono"; m.textContent = (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
    var n = document.createElement("span"); n.textContent = P.name;
    b.textContent = ""; b.appendChild(m); b.appendChild(n);
  })();
  document.getElementById("headline").textContent = P.headline;
  document.getElementById("intro").textContent = P.intro;
  document.getElementById("email").href = P.email;
  ["linkedin", "nav-linkedin"].forEach(function (id) { var l = document.getElementById(id); l.href = P.linkedin; l.target = "_blank"; l.rel = "noopener noreferrer"; });
  var rs = document.getElementById("resume");
  if (P.resume) rs.href = P.resume; else rs.remove();
  document.getElementById("tools").textContent = P.tools;
  var certs = document.getElementById("certs");
  P.certs.forEach(function (c) {
    certs.appendChild(c.url ? Object.assign(el("a", { "class": "chip", href: c.url, target: "_blank", rel: "noopener" }, c.label)) : el("span", { "class": "chip" }, c.label));
  });

  // Headline findings: every project's headline, empty ones shown as placeholders
  var stats = document.getElementById("stats");
  list.forEach(function (p) {
    var s = el("div", { "class": "stat" });
    var empty = p.headline.value == null;
    s.appendChild(el("div", { "class": "big" + (empty ? " empty" : "") }, empty ? "to fill in" : p.headline.value));
    s.appendChild(el("div", { "class": "label" }, p.headline.label));
    stats.appendChild(s);
  });

  // Filters and cards
  var sectors = ["All"].concat(list.map(function (p) { return p.sector; }).filter(function (v, i, a) { return a.indexOf(v) === i; }));
  var filters = document.getElementById("filters"), grid = document.getElementById("grid"), active = "All";

  function renderGrid() {
    grid.innerHTML = "";
    list.filter(function (p) { return active === "All" || p.sector === active; }).forEach(function (p) {
      var a = el("a", { "class": "card", href: "case.html?id=" + encodeURIComponent(p.id) });
      a.appendChild(el("div", { "class": "meta" }, p.sector + " · " + p.area));
      a.appendChild(el("h3", {}, p.title));
      a.appendChild(el("p", {}, p.summary));
      if (!p.found.length) a.appendChild(el("span", { "class": "draft" }, "Draft: findings to add"));
      var tl = el("div", { "class": "tagline" });
      tl.appendChild(el("span", { "class": "tag real" }, p.provenance + " data"));
      p.tools.slice(0, 3).forEach(function (t) { tl.appendChild(el("span", { "class": "tag" }, t)); });
      a.appendChild(tl);
      grid.appendChild(a);
    });
  }
  sectors.forEach(function (s) {
    var b = el("button", { type: "button", "aria-pressed": s === "All" ? "true" : "false" }, s);
    b.addEventListener("click", function () {
      active = s;
      Array.prototype.forEach.call(filters.children, function (c) { c.setAttribute("aria-pressed", c === b ? "true" : "false"); });
      renderGrid();
    });
    filters.appendChild(b);
  });
  renderGrid();
})();
