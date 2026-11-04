(function () {
  var P = window.PROFILE;
  // Only finished case studies are shown; unfinished ones (no findings yet) stay off the homepage.
  var list = window.PROJECTS.filter(function (p) { return p.found && p.found.length; });

  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }
  function shot(p) { var s = p.shots && p.shots[p.hero != null ? p.hero : 0]; return s ? s.file : null; }
  function href(p) { return "case.html?id=" + encodeURIComponent(p.id); }

  // brand
  var b = document.getElementById("brand"), parts = P.name.split(" ");
  b.textContent = "";
  b.appendChild(el("span", { "class": "mono" }, (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase()));
  var nm = el("span", {}, P.name); nm.appendChild(el("small", {}, "DATA · INSIGHTS · BUSINESS IMPACT")); b.appendChild(nm);

  // links
  document.getElementById("email").href = P.email;
  ["linkedin", "linkedin2"].forEach(function (id) { var l = document.getElementById(id); l.href = P.linkedin; l.target = "_blank"; l.rel = "noopener noreferrer"; });
  var rs = document.getElementById("resume");
  if (P.resume) rs.href = P.resume; else rs.remove();
  document.getElementById("burger").addEventListener("click", function () { document.getElementById("menu").classList.toggle("open"); });
  Array.prototype.forEach.call(document.querySelectorAll("#menu a"), function (a) { a.addEventListener("click", function () { document.getElementById("menu").classList.remove("open"); }); });

  // pills: certifications and tools
  // The featured case, cards, pills and About list are also written into index.html by build_home.py,
  // so they show without JavaScript. Only fill a block here if it is still empty.
  function empty(id) { return !document.getElementById(id).children.length && !document.getElementById(id).textContent.trim(); }
  var pills = document.getElementById("pills");
  if (empty("pills")) {
    P.certs.forEach(function (c) { pills.appendChild(el("a", { "class": "pill cert", href: c.url || "#", target: "_blank", rel: "noopener" }, "✓ Microsoft " + c.label.split(" ")[0])); });
    ["Power BI · DAX", "SQL · Python", "Microsoft Fabric"].forEach(function (x) { pills.appendChild(el("span", { "class": "pill" }, x)); });
  }

  // featured: Toronto 311 if present, else the first project
  var feat = list.filter(function (p) { return p.id === "toronto-311"; })[0] || list[0];
  var rest = list.filter(function (p) { return p !== feat; });

  var shell = document.getElementById("shell"), img = document.getElementById("shell-img");
  shell.href = href(feat); img.src = shot(feat); img.alt = "Power BI report: " + feat.title;

  if (empty("feature")) {
  var f = document.getElementById("feature");
  var copy = el("div", { "class": "copy" });
  copy.appendChild(el("div", { "class": "industry" }, "Featured case study · " + feat.sector));
  copy.appendChild(el("h3", {}, feat.title));
  copy.appendChild(el("p", {}, feat.summary));
  var res = el("div", { "class": "result" });
  res.appendChild(el("b", {}, feat.headline.value + " " + feat.headline.label));
  res.appendChild(el("small", {}, "Real data · " + feat.source));
  copy.appendChild(res);
  var tg = el("div", { "class": "tags2" });
  feat.tools.forEach(function (t) { tg.appendChild(el("span", { "class": "tag2" }, t)); });
  copy.appendChild(tg);
  var ln = el("div", { "class": "links2" });
  ln.appendChild(el("a", { "class": "tlink", href: href(feat) }, "Explore case study ↗"));
  ln.appendChild(el("a", { "class": "tlink sec2", href: "https://github.com/Mihir0369/portfolio_website/tree/main/" + feat.repo, target: "_blank", rel: "noopener" }, "GitHub source ↗"));
  copy.appendChild(ln);
  var art = el("div", { "class": "art" });
  var fi = el("img", { src: shot(feat), alt: "Power BI report page: " + feat.title, loading: "lazy" });
  art.appendChild(fi);
  f.appendChild(copy); f.appendChild(art);
  }

  // other case studies
  if (empty("grid")) {
  var grid = document.getElementById("grid");
  rest.forEach(function (p, i) {
    var a = el("a", { "class": "pcard", href: href(p) });
    var th = el("div", { "class": "pthumb t" + (i % 3) });
    th.appendChild(el("img", { src: shot(p), alt: "Power BI report page: " + p.title, loading: "lazy" }));
    a.appendChild(th);
    var c = el("div", { "class": "copy" });
    c.appendChild(el("div", { "class": "industry" }, p.sector + " · " + p.area));
    c.appendChild(el("h3", {}, p.title));
    c.appendChild(el("p", {}, p.summary));
    var t = el("div", { "class": "tags2" });
    p.tools.slice(0, 3).forEach(function (x) { t.appendChild(el("span", { "class": "tag2" }, x)); });
    c.appendChild(t);
    c.appendChild(el("span", { "class": "tlink" }, "Explore case study ↗"));
    a.appendChild(c); grid.appendChild(a);
  });
  }
  if (empty("count")) document.getElementById("count").textContent = "Showing " + list.length + " finished case studies · " + (window.PROJECTS.length - list.length) + " in development";

  // about list
  if (empty("alist")) {
  var al = document.getElementById("alist");
  [["Data & reporting experience", "Elevara Digital · Impact Zero · Scalezix Technologies"],
   ["Microsoft Certified: Power BI Data Analyst Associate", "PL-300 certification"],
   ["Microsoft Certified: Fabric Analytics Engineer Associate", "DP-600 certification"],
   ["Graduate Certificate, Business Insights and Analytics", "Humber Polytechnic, Toronto"]].forEach(function (r) {
    var d = el("div", { "class": "aitem" }); d.appendChild(el("b", {}, r[0])); d.appendChild(el("span", {}, r[1])); al.appendChild(d);
  });
  }
})();
