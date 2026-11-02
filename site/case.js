(function () {
  var P = window.PROFILE, list = window.PROJECTS;
  var id = new URLSearchParams(location.search).get("id");
  var p = list.filter(function (x) { return x.id === id; })[0];
  var main = document.getElementById("main");
  document.getElementById("brand").textContent = P.name;

  var root = document.documentElement;
  try { var saved = localStorage.getItem("theme"); if (saved) root.setAttribute("data-theme", saved); } catch (e) {}
  document.getElementById("theme").addEventListener("click", function () {
    var dark = root.getAttribute("data-theme") === "dark" ||
      (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
    var next = dark ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("theme", next); } catch (e) {}
  });

  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }
  function section(title, content, cls) {
    var s = el("section", cls ? { "class": cls } : {});
    if (title) s.appendChild(el("h2", {}, title));
    s.appendChild(content); main.appendChild(s); return s;
  }
  function ul(items) { var u = el("ul"); items.forEach(function (t) { u.appendChild(el("li", {}, t)); }); return u; }
  function slot(text) { return el("div", { "class": "slot" }, text); }

  function drawChart(c, host) {
    var box = el("div", { "class": "chartbox", style: "height:320px" });
    var canvas = el("canvas", { role: "img", "aria-label": c.title });
    box.appendChild(canvas); host.appendChild(box);
    if (!window.Chart) return;
    var css = getComputedStyle(root);
    var color = css.getPropertyValue("--accent").trim() || "#1f6f5c";
    new Chart(canvas, {
      type: c.type || "bar",
      data: { labels: c.labels, datasets: [{ data: c.values, backgroundColor: color, borderColor: color, pointRadius: 2 }] },
      options: { maintainAspectRatio: false, indexAxis: c.type === "line" ? "x" : "y", plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true, ticks: { maxTicksLimit: 10 } }, y: { beginAtZero: true, title: { display: !!c.unit && c.type === "line", text: c.unit || "" } } } }
    });
  }

  if (!p) { main.appendChild(el("p", {}, "Case study not found.")); return; }
  document.title = p.title;
  var charts = p.charts || (p.chart ? [p.chart] : []);

  /* ---- head */
  var head = el("section", { "class": "case-head" });
  head.appendChild(el("a", { "class": "back", href: "index.html#work" }, "← All case studies"));
  head.appendChild(el("div", { "class": "eyebrow" }, p.sector + " · " + p.area));
  head.appendChild(el("h1", {}, p.title));
  head.appendChild(el("p", { "class": "intro" }, p.summary));
  var tl = el("div", { "class": "tagline" });
  tl.appendChild(el("span", { "class": "tag real" }, p.provenance + " data"));
  p.tools.forEach(function (t) { tl.appendChild(el("span", { "class": "tag" }, t)); });
  head.appendChild(tl);
  var empty = p.headline.value == null;
  var stat = el("div", { "class": "stat hero-stat" });
  stat.appendChild(el("div", { "class": "big" + (empty ? " empty" : "") }, empty ? "to fill in" : p.headline.value));
  stat.appendChild(el("div", { "class": "label" }, p.headline.label));
  head.appendChild(stat);
  main.appendChild(head);

  /* ---- question and data */
  section("The question", el("p", {}, p.question));
  section("The data", el("p", {}, p.data + " Source: " + p.source + "."));

  /* ---- Power BI report screenshots */
  if (p.shots && p.shots.length) {
    var gal = el("div", { "class": "shots" });
    p.shots.forEach(function (s) {
      var fig = el("figure", { "class": "shot" });
      var img = el("img", { src: s.file, alt: s.caption, loading: "lazy" });
      img.addEventListener("error", function () {
        var ph = slot("Screenshot not added yet: save it as site/" + s.file);
        img.replaceWith(ph);
      });
      fig.appendChild(img);
      fig.appendChild(el("figcaption", {}, s.caption));
      gal.appendChild(fig);
    });
    section("The Power BI report", gal, "pbi");
  }

  /* ---- key findings */
  if (p.found.length) {
    var grid = el("ol", { "class": "kf" });
    p.found.forEach(function (t) { grid.appendChild(el("li", {}, t)); });
    section("Key findings", grid, "tldr");
  } else {
    section("What I found", slot("To fill in after you run the analysis: 3 to 5 findings, each with a number and its sample size."));
  }

  /* ---- chapters (one finding each), else plain charts */
  if (p.chapters && p.chapters.length) {
    p.chapters.forEach(function (ch, i) {
      var box = el("div", { "class": "chapter" + (ch.warn ? " warn" : "") });
      box.appendChild(el("div", { "class": "n" }, String(i + 1).padStart(2, "0")));
      var body = el("div", { "class": "chapter-body" });
      body.appendChild(el("h2", {}, ch.title));
      body.appendChild(el("p", {}, ch.text));
      if (ch.chart != null && charts[ch.chart]) {
        body.appendChild(el("div", { "class": "chart-title" }, charts[ch.chart].title));
        drawChart(charts[ch.chart], body);
      }
      box.appendChild(body);
      main.appendChild(box);
    });
  } else {
    charts.forEach(function (c) { var h = el("div"); drawChart(c, h); section(c.title, h); });
  }

  /* ---- recommendations */
  if (p.recommend.length) {
    var rec = el("div", { "class": "recs" });
    p.recommend.forEach(function (t, i) {
      var c = el("div", { "class": "rec" });
      c.appendChild(el("span", { "class": "rn" }, String(i + 1)));
      c.appendChild(el("p", {}, t));
      rec.appendChild(c);
    });
    section("What I would recommend", rec);
  } else {
    section("What I would recommend", slot("To fill in: 2 to 3 actions someone could take, tied to the findings above."));
  }

  /* ---- data, model and method */
  section("What I did", ul(p.approach));
  if (p.model) {
    var m = el("div", { "class": "model" });
    var tbl = el("table");
    var hr = el("tr"); ["Table", "Role", "Contents"].forEach(function (h) { hr.appendChild(el("th", {}, h)); });
    tbl.appendChild(hr);
    p.model.tables.forEach(function (t) {
      var r = el("tr"); r.appendChild(el("td", {}, t.name)); r.appendChild(el("td", {}, t.role)); r.appendChild(el("td", {}, t.rows)); tbl.appendChild(r);
    });
    m.appendChild(tbl);
    m.appendChild(el("h3", {}, "Key measures"));
    p.model.measures.forEach(function (x) {
      var d = el("div", { "class": "measure" });
      d.appendChild(el("strong", {}, x.name));
      d.appendChild(el("code", {}, x.dax));
      m.appendChild(d);
    });
    if (p.model.note) m.appendChild(el("p", { "class": "note" }, p.model.note));
    section("Model and measures", m);
  }
  section("Limits of this analysis", ul(p.limits));

  var repo = el("p", {});
  repo.appendChild(document.createTextNode("Code, SQL and the method write-up: "));
  var link = el("a", { href: "https://github.com/Mihir0369/portfolio_website/tree/main/" + p.repo, target: "_blank", rel: "noopener" }, p.repo + "/ on GitHub");
  repo.appendChild(link);
  repo.appendChild(document.createTextNode("."));
  section("Reproduce it", repo);
})();
