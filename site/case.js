(function () {
  var P = window.PROFILE, list = window.PROJECTS;
  var id = new URLSearchParams(location.search).get("id");
  var p = list.filter(function (x) { return x.id === id; })[0];
  var main = document.getElementById("main");
  document.getElementById("brand").textContent = P.name;

  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }
  function add(parent, child) { parent.appendChild(child); return child; }
  function section(title, content, cls) {
    var s = el("section", cls ? { "class": cls } : {});
    if (title) s.appendChild(el("h2", {}, title));
    s.appendChild(content); main.appendChild(s); return s;
  }
  function ul(items) { var u = el("ul"); items.forEach(function (t) { u.appendChild(el("li", {}, t)); }); return u; }
  function slot(text) { return el("div", { "class": "slot" }, text); }
  function fmt(v, suffix) {
    if (suffix) return (Math.round(v * 10) / 10).toFixed(1) + suffix;
    return Number(v).toLocaleString("en-CA");
  }
  function wrap(label, n) {
    var words = String(label).split(" "), lines = [], cur = "";
    words.forEach(function (w) {
      if ((cur + " " + w).trim().length > n && cur) { lines.push(cur); cur = w; } else { cur = (cur + " " + w).trim(); }
    });
    if (cur) lines.push(cur);
    return lines;
  }

  /* ---------- small icons for the cards (own drawings, same set as the report) */
  var ICONS = {
    bars: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><rect x="4" y="12" width="4" height="8" fill="currentColor"/><rect x="10" y="7" width="4" height="13" fill="currentColor"/><rect x="16" y="3" width="4" height="17" fill="currentColor"/></svg>',
    check: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    clock: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M12 7v5.5l3.5 2" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    warn: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M12 3.5L22 20H2z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M12 10v4.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="17.2" r="1.3" fill="currentColor"/></svg>'
  };

  /* ---------- charts */
  var css = getComputedStyle(document.documentElement);
  function cv(name, dflt) { return css.getPropertyValue(name).trim() || dflt; }
  var COL = { navy: cv("--accent", "#1B3A5C"), amber: cv("--amber", "#C77700"), grey: cv("--grey", "#8A9BAE"), teal: cv("--teal", "#2A7F8E"),
              muted: cv("--muted", "#4A5B6C"), line: cv("--line", "#D9E2E8"), light: "#C9D3DC" };
  if (window.Chart) { Chart.defaults.font.family = '"Segoe UI", system-ui, sans-serif'; Chart.defaults.color = COL.muted; }

  var valueLabels = {
    id: "valueLabels",
    afterDatasetsDraw: function (chart, args, opts) {
      if (!opts || !opts.show) return;
      var ctx = chart.ctx; ctx.save();
      ctx.fillStyle = cv("--text", "#1F2D3D"); ctx.font = '600 12px "Segoe UI", system-ui, sans-serif';
      var horizontal = chart.options.indexAxis === "y";
      chart.getDatasetMeta(0).data.forEach(function (bar, i) {
        var v = chart.data.datasets[0].data[i];
        var t = fmt(v, opts.suffix);
        if (horizontal) { ctx.textAlign = "left"; ctx.textBaseline = "middle"; ctx.fillText(t, bar.x + 6, bar.y); }
        else { ctx.textAlign = "center"; ctx.textBaseline = "bottom"; ctx.fillText(t, bar.x, bar.y - 5); }
      });
      ctx.restore();
    }
  };

  function viz(c, host) {
    var box = el("div", { "class": "viz" });
    if (c.title) box.appendChild(el("div", { "class": "viz-title" }, c.title));
    var type = c.type || "bar";
    var horizontal = type === "bar" && c.orient !== "v";
    var n = c.labels.length;
    var h = type === "line" ? 300 : type === "doughnut" ? 270 : horizontal ? Math.max(200, n * (c.datasets ? 62 : 38) + 70) : 280;
    var holder = el("div", { "class": "chartbox", style: "height:" + h + "px" });
    var canvas = el("canvas", { role: "img", "aria-label": c.title || "chart" });
    holder.appendChild(canvas); box.appendChild(holder); host.appendChild(box);
    if (!window.Chart) { holder.appendChild(slot("Chart library did not load (offline?).")); return; }

    var data, options;
    var grid = { color: COL.line };
    if (type === "doughnut") {
      data = { labels: c.labels, datasets: [{ data: c.values, backgroundColor: [COL.amber, COL.light], borderWidth: 0 }] };
      options = { maintainAspectRatio: false, cutout: "62%", plugins: { legend: { position: "bottom" },
        tooltip: { callbacks: { label: function (x) { return " " + x.label + ": " + fmt(x.raw) + " (" + (100 * x.raw / c.values.reduce(function (a, b) { return a + b; }, 0)).toFixed(1) + "%)"; } } } } };
    } else {
      var grouped = !!c.datasets;
      var yearCols = [COL.light, "#5F7C99", COL.navy];
      var datasets = grouped
        ? c.datasets.map(function (d, i) { return { label: d.label, data: d.values, backgroundColor: d.color || yearCols[i % 3], borderWidth: 0 }; })
        : [{ data: c.values, borderWidth: type === "line" ? 3 : 0, tension: 0.25, pointRadius: type === "line" ? 2 : 0,
             borderColor: COL.navy,
             backgroundColor: c.highlight != null ? c.values.map(function (v, i) { return i === c.highlight ? COL.amber : COL.grey; }) : COL.navy }];
      var valAxis = { beginAtZero: true, grid: grid, title: { display: !!c.unit, text: c.unit || "" },
        ticks: { maxTicksLimit: 8, callback: function (v) { return c.suffix ? v + c.suffix : Number(v).toLocaleString("en-CA"); } } };
      var catAxis = { grid: { display: false }, ticks: { autoSkip: type === "line", maxTicksLimit: type === "line" ? 12 : undefined,
        callback: function (v) { var l = this.getLabelForValue(v); return horizontal ? wrap(l, 26) : l; } } };
      data = { labels: c.labels, datasets: datasets };
      options = { maintainAspectRatio: false, indexAxis: horizontal ? "y" : "x",
        layout: { padding: { right: horizontal && !grouped ? 48 : 8, top: !horizontal && type === "bar" ? 18 : 0 } },
        plugins: { legend: { display: grouped, position: "bottom" }, valueLabels: { show: type === "bar" && !grouped, suffix: c.suffix },
          tooltip: { callbacks: { label: function (x) { return " " + (x.dataset.label ? x.dataset.label + ": " : "") + fmt(x.raw, c.suffix); } } } },
        scales: horizontal ? { x: valAxis, y: catAxis } : { x: catAxis, y: valAxis } };
    }
    new Chart(canvas, { type: type, data: data, options: options, plugins: [valueLabels] });
  }

  /* ---------- cards */
  function card(k, withIcon) {
    var c = el("div", { "class": "kpi" });
    var top = add(c, el("div", { "class": "kpi-top" }));
    var txt = add(top, el("div"));
    txt.appendChild(el("div", { "class": "kpi-label" }, k.label));
    if (k.sub) txt.appendChild(el("div", { "class": "kpi-sub" }, k.sub));
    if (withIcon && k.icon && ICONS[k.icon]) { var ic = add(top, el("span", { "class": "kpi-icon", "aria-hidden": "true" })); ic.innerHTML = ICONS[k.icon]; }
    c.appendChild(el("div", { "class": "kpi-value" }, k.value));
    return c;
  }
  function cardRow(items, cls, withIcon) {
    var r = el("div", { "class": cls });
    items.forEach(function (k) { r.appendChild(card(k, withIcon)); });
    return r;
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
  if (!p.kpis) {
    var empty = p.headline.value == null;
    var stat = el("div", { "class": "stat hero-stat" });
    stat.appendChild(el("div", { "class": "big" + (empty ? " empty" : "") }, empty ? "to fill in" : p.headline.value));
    stat.appendChild(el("div", { "class": "label" }, p.headline.label));
    head.appendChild(stat);
  }
  main.appendChild(head);

  /* ---- report build facts: stats strip and technique chips */
  if (p.stats) {
    var bs = el("section", { "class": "build" });
    bs.appendChild(el("div", { "class": "viz-title" }, "How the report is built"));
    var sr = el("div", { "class": "stats" });
    p.stats.forEach(function (s) {
      var d = el("div", { "class": "st" });
      d.appendChild(el("b", {}, s.value));
      d.appendChild(el("span", {}, s.label));
      if (s.sub) d.appendChild(el("small", {}, s.sub));
      sr.appendChild(d);
    });
    bs.appendChild(sr);
    if (p.downloads) {
      var dl = el("div", { "class": "downloads" });
      p.downloads.forEach(function (d) {
        var box = el("div", { "class": "dl" });
        box.appendChild(el("a", { "class": "btn primary", href: d.file, download: "" }, d.label));
        box.appendChild(el("p", {}, d.note));
        dl.appendChild(box);
      });
      bs.appendChild(dl);
    }
    if (p.techniques) {
      var ch = el("div", { "class": "chips" });
      p.techniques.forEach(function (t) { ch.appendChild(el("span", { "class": "chip" }, t)); });
      bs.appendChild(ch);
    }
    main.appendChild(bs);
  }

  /* ---- KPI and finding cards, like the report's Overview page */
  if (p.kpis) {
    var kwrap = el("section", { "class": "kpi-block" });
    kwrap.appendChild(cardRow(p.kpis, "kpis", true));
    if (p.facts) kwrap.appendChild(cardRow(p.facts, "facts", false));
    main.appendChild(kwrap);
  }

  /* ---- question and data (two columns: text left, visual right) */
  if (p.glance) {
    var sp = el("section", { "class": "split" });
    var left = add(sp, el("div", { "class": "split-text" }));
    left.appendChild(el("h2", {}, "The question"));
    left.appendChild(el("p", {}, p.question));
    left.appendChild(el("h2", {}, "The data"));
    left.appendChild(el("p", {}, p.data + " Source: " + p.source + "."));
    var right = add(sp, el("div", { "class": "split-visual" }));
    right.appendChild(el("div", { "class": "viz-title" }, "The data at a glance"));
    right.appendChild(cardRow(p.glance.map(function (g) { return { label: g.label, value: g.value }; }), "glance", false));
    main.appendChild(sp);
  } else {
    section("The question", el("p", {}, p.question));
    section("The data", el("p", {}, p.data + " Source: " + p.source + "."));
  }

  /* ---- Power BI report screenshots */
  if (p.shots && p.shots.length) {
    var gal = el("div", { "class": "shots" });
    p.shots.forEach(function (s) {
      var fig = el("figure", { "class": "shot" });
      var img = el("img", { src: s.file, alt: s.caption, loading: "lazy" });
      img.addEventListener("error", function () { img.replaceWith(slot("Screenshot not added yet: save it as site/" + s.file)); });
      var open = el("a", { href: s.file, target: "_blank", rel: "noopener", title: "Open full size" });
      open.appendChild(img);
      fig.appendChild(open);
      fig.appendChild(el("figcaption", {}, s.caption + " (click to enlarge)"));
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

  /* ---- chapters: explanation left, visuals right */
  if (p.chapters && p.chapters.length) {
    p.chapters.forEach(function (ch, i) {
      var box = el("div", { "class": "chapter split" + (ch.warn ? " warn" : "") });
      var txt = add(box, el("div", { "class": "split-text chapter-body" }));
      txt.appendChild(el("div", { "class": "n" }, String(i + 1).padStart(2, "0")));
      txt.appendChild(el("h2", {}, ch.title));
      txt.appendChild(el("p", {}, ch.text));
      if (ch.stat) {
        var m = add(txt, el("div", { "class": "kpi mini" }));
        m.appendChild(el("div", { "class": "kpi-value" }, ch.stat.value));
        m.appendChild(el("div", { "class": "kpi-label" }, ch.stat.label));
      }
      var vis = add(box, el("div", { "class": "split-visual" }));
      var specs = ch.visuals || (ch.chart != null ? [{ ref: ch.chart }] : []);
      specs.forEach(function (v) { viz(v.ref != null ? charts[v.ref] : v, vis); });
      main.appendChild(box);
    });
  } else {
    charts.forEach(function (c) { var h = el("div"); viz(c, h); section(c.title, h); });
  }

  /* ---- impact: who acts, what changes, what to track */
  if (p.impact && p.impact.length) {
    var imp = el("div", { "class": "recs impact" });
    p.impact.forEach(function (x, i) {
      var c = el("div", { "class": "rec" });
      c.appendChild(el("span", { "class": "rn" }, String(i + 1)));
      var b = el("div");
      b.appendChild(el("p", {}, x.action));
      var m = el("p", { "class": "rec-meta" });
      m.appendChild(el("strong", {}, "Who: ")); m.appendChild(document.createTextNode(x.owner));
      m.appendChild(el("br"));
      m.appendChild(el("strong", {}, "Track: ")); m.appendChild(document.createTextNode(x.track));
      b.appendChild(m);
      c.appendChild(b);
      imp.appendChild(c);
    });
    if (p.impactNote) imp.appendChild(el("p", { "class": "note" }, p.impactNote));
    section("Impact: what should change", imp);
  } else if (p.recommend.length) {
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

  section("What I did", ul(p.approach));

  /* ---- pitfalls and decisions */
  if (p.pitfalls && p.pitfalls.length) {
    var pf = el("div", { "class": "recs pitfalls" });
    p.pitfalls.forEach(function (x) {
      var c = el("div", { "class": "rec" });
      var b = el("div");
      b.appendChild(el("h3", {}, x.title));
      b.appendChild(el("p", {}, x.text));
      c.appendChild(b);
      pf.appendChild(c);
    });
    section("Pitfalls and decisions", pf);
  }

  /* ---- live report or walkthrough, shown only when a link exists */
  if (p.embed) {
    var fr = el("iframe", { src: p.embed, title: p.title + " live report", loading: "lazy", allowfullscreen: "true" });
    fr.className = "embed";
    section("Live report", fr);
  } else if (p.walkthrough) {
    var vf = el("iframe", { src: p.walkthrough, title: p.title + " walkthrough", loading: "lazy", allowfullscreen: "true" });
    vf.className = "embed";
    section("Walkthrough", vf);
  }

  /* ---- model: explanation left, star schema right */
  if (p.model) {
    var ms = el("section", { "class": "split model" });
    var ml = add(ms, el("div", { "class": "split-text" }));
    ml.appendChild(el("h2", {}, "Model and measures"));
    if (p.model.intro) ml.appendChild(el("p", {}, p.model.intro));
    ml.appendChild(el("h3", {}, "Key measures"));
    p.model.measures.forEach(function (x) {
      var d = el("div", { "class": "measure" });
      d.appendChild(el("strong", {}, x.name));
      d.appendChild(el("code", {}, x.dax));
      ml.appendChild(d);
    });
    if (p.model.note) ml.appendChild(el("p", { "class": "note" }, p.model.note));

    var mr = add(ms, el("div", { "class": "split-visual" }));
    mr.appendChild(el("div", { "class": "viz-title" }, "Star schema"));
    var fact = p.model.tables.filter(function (t) { return t.role === "Fact"; })[0];
    var dims = p.model.tables.filter(function (t) { return t.role !== "Fact"; });
    var star = add(mr, el("div", { "class": "star" }));
    var pos = ["top", "right", "bottom", "left"];
    add(star, el("div", { "class": "sd fact" })).innerHTML = "<b>" + fact.name + "</b><small>" + (fact.short || "fact table") + "</small>";
    dims.slice(0, 4).forEach(function (d, i) {
      add(star, el("div", { "class": "sd dim " + pos[i] })).innerHTML = "<b>" + d.name + "</b><small>" + (d.short || d.rows) + "</small>";
    });
    main.appendChild(ms);
  }

  section("Limits of this analysis", ul(p.limits));

  var repo = el("p", {});
  repo.appendChild(document.createTextNode("Code, SQL and the method write-up: "));
  repo.appendChild(el("a", { href: "https://github.com/Mihir0369/portfolio_website/tree/main/" + p.repo, target: "_blank", rel: "noopener" }, p.repo + "/ on GitHub"));
  repo.appendChild(document.createTextNode("."));
  section("Reproduce it", repo);
})();
