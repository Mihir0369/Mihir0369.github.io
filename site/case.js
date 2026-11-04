(function () {
  var P = window.PROFILE, list = window.PROJECTS;
  var id = new URLSearchParams(location.search).get("id");
  var p = list.filter(function (x) { return x.id === id; })[0];
  var main = document.getElementById("main");
  var host = main;
  (function () { var l = document.getElementById("nav-linkedin"); l.href = P.linkedin; l.target = "_blank"; l.rel = "noopener noreferrer"; })();
  (function () {
    var b = document.getElementById("brand"), parts = P.name.split(" ");
    var m = document.createElement("span"); m.className = "mono"; m.textContent = (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
    var n = document.createElement("span"); n.textContent = P.name;
    b.textContent = ""; b.appendChild(m); b.appendChild(n);
  })();

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
    s.appendChild(content); host.appendChild(s); return s;
  }
  function ul(items) { var u = el("ul"); items.forEach(function (t) { u.appendChild(el("li", {}, t)); }); return u; }
  function slot(text) { return el("div", { "class": "slot" }, text); }
  function fmt(v, suffix, dec) {
    if (suffix) return Number(v).toFixed(dec == null ? 1 : dec) + suffix;
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
      if (!opts) return;
      if (chart.config.type === "doughnut") {
        var dctx = chart.ctx, vals = chart.data.datasets[0].data;
        var tot = vals.reduce(function (a, b) { return a + b; }, 0);
        dctx.save(); dctx.textAlign = "center"; dctx.textBaseline = "middle";
        chart.getDatasetMeta(0).data.forEach(function (arc, i) {
          var pos = arc.tooltipPosition();
          dctx.fillStyle = i === 0 ? "#FFFFFF" : cv("--text", "#1F2D3D");
          dctx.font = '700 18px "Segoe UI", system-ui, sans-serif';
          dctx.fillText((100 * vals[i] / tot).toFixed(1) + "%", pos.x, pos.y - 10);
          dctx.font = '400 13px "Segoe UI", system-ui, sans-serif';
          dctx.fillText(Number(vals[i]).toLocaleString("en-CA"), pos.x, pos.y + 12);
        });
        dctx.restore();
        return;
      }
      if (!opts.show) return;
      var ctx = chart.ctx; ctx.save();
      ctx.fillStyle = cv("--text", "#1F2D3D"); ctx.font = '600 12px "Segoe UI", system-ui, sans-serif';
      var horizontal = chart.options.indexAxis === "y";
      chart.getDatasetMeta(0).data.forEach(function (bar, i) {
        var v = chart.data.datasets[0].data[i];
        var t = fmt(v, opts.suffix, opts.decimals);
        if (horizontal) { ctx.textAlign = "left"; ctx.textBaseline = "middle"; ctx.fillText(t, bar.x + 6, bar.y); }
        else { ctx.textAlign = "center"; ctx.textBaseline = "bottom"; ctx.fillText(t, bar.x, bar.y - 5); }
      });
      ctx.restore();
    }
  };

  function viz(c, host, bare) {
    var box = bare ? host : el("div", { "class": "viz" });
    if (c.title && !bare) box.appendChild(el("div", { "class": "viz-title" }, c.title));
    var type = c.type || "bar";
    var horizontal = type === "bar" && c.orient !== "v";
    var n = c.labels.length;
    var h = bare ? 400 : type === "line" ? 300 : type === "doughnut" ? 270 : horizontal ? Math.max(200, n * (c.datasets ? 62 : 38) + 70) : 280;
    var holder = el("div", { "class": "chartbox", style: "height:" + h + "px" });
    var canvas = el("canvas", { role: "img", "aria-label": c.title || "chart" });
    holder.appendChild(canvas); box.appendChild(holder); if (!bare) host.appendChild(box);
    if (!window.Chart) { holder.appendChild(slot("Chart library did not load (offline?).")); return; }

    var data, options;
    var grid = { color: COL.line };
    if (type === "doughnut") {
      data = { labels: c.labels, datasets: [{ data: c.values, backgroundColor: [COL.amber, COL.light], borderWidth: 0 }] };
      options = { maintainAspectRatio: false, cutout: "55%", plugins: { valueLabels: { show: true }, legend: { position: "bottom" },
        tooltip: { callbacks: { label: function (x) { return " " + x.label + ": " + fmt(x.raw) + " (" + (100 * x.raw / c.values.reduce(function (a, b) { return a + b; }, 0)).toFixed(1) + "%)"; } } } } };
    } else {
      var grouped = !!c.datasets;
      var yearCols = [COL.light, "#5F7C99", COL.navy];
      var datasets = grouped
        ? c.datasets.map(function (d, i) {
            var lc = d.color || [COL.navy, COL.teal, COL.amber][i % 3];
            return type === "line"
              ? { label: d.label, data: d.values, borderColor: lc, backgroundColor: lc, borderWidth: 3, pointRadius: 0, tension: 0.2, spanGaps: false }
              : { label: d.label, data: d.values, backgroundColor: d.color || yearCols[i % 3], borderWidth: 0 };
          })
        : [{ data: c.values, borderWidth: type === "line" ? 3 : 0, tension: 0.25, pointRadius: type === "line" ? 2 : 0,
             borderColor: COL.navy,
             backgroundColor: c.highlight != null ? c.values.map(function (v, i) { return (Array.isArray(c.highlight) ? c.highlight.indexOf(i) >= 0 : i === c.highlight) ? COL.amber : COL.grey; }) : COL.navy }];
      var valAxis = { beginAtZero: true, grid: grid, title: { display: !!c.unit, text: c.unit || "" },
        ticks: { maxTicksLimit: 8, callback: function (v) { return c.suffix ? (c.decimals != null && c.decimals > 0 ? Number(v).toFixed(c.decimals) : v) + c.suffix : Number(v).toLocaleString("en-CA"); } } };
      var catAxis = { grid: { display: false }, ticks: { autoSkip: type === "line", maxTicksLimit: type === "line" ? 12 : undefined,
        callback: function (v) { var l = this.getLabelForValue(v); return horizontal ? wrap(l, 26) : l; } } };
      data = { labels: c.labels, datasets: datasets };
      options = { maintainAspectRatio: false, indexAxis: horizontal ? "y" : "x",
        layout: { padding: { right: horizontal && !grouped ? 48 : 8, top: !horizontal && type === "bar" ? 18 : 0 } },
        plugins: { legend: { display: grouped, position: "bottom" }, valueLabels: { show: type === "bar" && !grouped && !c.noLabels, suffix: c.suffix, decimals: c.decimals },
          tooltip: { callbacks: { label: function (x) { return " " + (x.dataset.label ? x.dataset.label + ": " : "") + fmt(x.raw, c.suffix, c.decimals); } } } },
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

  /* Story layout: facts, report, findings, chapters, recommendations, method */

  /* bold key numbers (percentages, figures with commas or decimals) and key terms */
  var TERMS = ["fatal share", "injury collisions", "no traffic control", "No traffic control", "curved roads", "single-vehicle", "safety device", "collision ID", "C_CASE", "what-if", "parks, forestry and environment", "Parks, Forestry and Environment", "parks and forestry", "dead-wildlife pick-up", "Dead-wildlife pick-up", "missed recycling pick-up", "general pruning", "tree removal", "Taxonomy Era", "snow types", "closed date", "renamed request types", "Renamed request types", "star schema", "47 DAX measures", "unquoted comma"];
  var RICH = new RegExp("(" + TERMS.map(function (t) { return t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }).join("|") + "|\\d[\\d,]*\\.\\d+%?|\\d{1,3}(?:,\\d{3})+|\\d+(?:\\.\\d+)?%|\\d+(?:\\.\\d+)? pts)", "g");
  function rich(node, text) {
    var parts = String(text).split(RICH);
    parts.forEach(function (s, i) {
      if (!s) return;
      if (i % 2 === 1) node.appendChild(el("b", {}, s)); else node.appendChild(document.createTextNode(s));
    });
    return node;
  }


  /* DAX colouring on the light code panel: functions and keywords bold navy, variables teal, strings green */
  var DAX_TOKEN = /("(?:[^"]|"")*")|\b(VAR|RETURN|DESC|ASC|TRUE|FALSE)\b|\b([A-Z][A-Z0-9.]*)(?=\s*\()|\b([A-Za-z_]\w*)\b/g;
  function dax(host, code) {
    var vars = {}; code.replace(/\bVAR\s+([A-Za-z_]\w*)/g, function (m, v) { vars[v] = true; });
    var last = 0, m;
    function put(txt, cls) { if (!txt) return; if (cls) host.appendChild(el("span", { "class": cls }, txt)); else host.appendChild(document.createTextNode(txt)); }
    DAX_TOKEN.lastIndex = 0;
    while ((m = DAX_TOKEN.exec(code))) {
      put(code.slice(last, m.index));
      if (m[1]) put(m[1], "dx-str");
      else if (m[2]) put(m[2], "dx-kw");
      else if (m[3]) put(m[3], "dx-fn");
      else put(m[4], vars[m[4]] ? "dx-var" : "");
      last = DAX_TOKEN.lastIndex;
    }
    put(code.slice(last));
  }
  function renderStory() {
    var S = p.story || {
      dek: p.summary,
      meta: [{ k: "Data", v: p.source + " (" + p.provenance.toLowerCase() + ")" }, { k: "Tools", v: p.tools.join(", ") }]
    };
    function div(cls, parent, text) { var d = el("div", cls ? { "class": cls } : {}, text); if (parent) parent.appendChild(d); return d; }
    function sec(cls, title) { var s = el("section", { "class": cls }); if (title) s.appendChild(el("h2", {}, title)); main.appendChild(s); return s; }

    var h = sec("case-head s-head");
    var cr = div("crumbs", h);
    cr.appendChild(el("a", { href: "index.html#work" }, "Work")); cr.appendChild(document.createTextNode(" / " + p.sector));
    h.appendChild(el("span", { "class": "tag" }, p.sector + " \u00b7 " + p.area));
    h.appendChild(el("h1", {}, p.title));
    h.appendChild(el("p", { "class": "dek" }, S.dek));
    if (S.bottom) { var bl = rich(el("p", { "class": "bottom" }), S.bottom); bl.insertBefore(el("b", { "class": "bl" }, "Bottom line: "), bl.firstChild); h.appendChild(bl); }
    h.appendChild(p.kpis ? cardRow(p.kpis, "kpis", true)
      : cardRow([{ label: p.headline.label, value: p.headline.value == null ? "to fill in" : p.headline.value, sub: "Headline result", icon: "bars" }], "kpis one", true));
    var mr = div("meta-row", h);
    S.meta.forEach(function (m) {
      var sp = el("span"); sp.appendChild(el("b", {}, m.k + ": "));
      if (m.links) { m.links.forEach(function (l, li) { if (li) sp.appendChild(document.createTextNode(" \u00b7 ")); sp.appendChild(el("a", { href: l.href, target: "_blank", rel: "noopener noreferrer" }, l.v)); }); }
      else if (m.href) { var ml = el("a", { href: m.href, target: "_blank", rel: "noopener noreferrer" }, m.v); sp.appendChild(ml); } else sp.appendChild(document.createTextNode(m.v));
      mr.appendChild(sp);
    });
    if (S.toc && S.chapters) {
      var jp = div("jump", h); jp.appendChild(el("b", {}, "Jump to: "));
      S.chapters.forEach(function (c, ci) { jp.appendChild(el("a", { href: "#ch-" + ci }, c.n.replace(" \u00b7 ", " "))); });
    }

    var r = sec("s-pbi");
    var rh = div("pbi-head", r);
    var rl = div("", rh);
    rl.appendChild(el("h2", {}, "Power BI report"));
    rl.appendChild(el("p", {}, "Exported from Power BI Desktop. Select a page to view it full size."));
    var ps = div("pbi-stats", rh);
    (p.stats || []).forEach(function (s) { var d = div("pst", ps); d.appendChild(el("span", {}, s.label)); d.appendChild(el("b", {}, s.value)); });
    r.appendChild(p.shots && p.shots.length ? gallery() : slot("Power BI report screenshots: to add once the report is built."));
    var pf = div("pbi-foot", r);
    var chp = div("chips", pf);
    (S.chips || (p.techniques || []).slice(0, 7)).forEach(function (t) { chp.appendChild(el("span", { "class": "chip" }, t)); });
    var dls = div("dls", pf);
    (p.downloads || []).forEach(function (d, i) { dls.appendChild(el("a", { "class": "btn " + (i ? "primary" : "ghost"), href: d.file, download: "" }, d.label)); });
    if (p.downloads) r.appendChild(el("p", { "class": "pbi-note" }, "Open the .pbip file in Power BI Desktop (free). The model, DAX measures and report pages are all editable."));

    var kf = sec("s-tldr", "Key findings");
    var fnd = S.findings || p.found || [];
    if (fnd.length) { var ol = el("ol"); fnd.forEach(function (t) { ol.appendChild(rich(el("li"), t)); }); kf.appendChild(ol); }
    else kf.appendChild(slot("Findings to fill in after the analysis: 3 to 5 findings, each with a number and its sample size."));
    if (S.terms) { var tm = rich(el("p", { "class": "terms" }), S.terms); tm.insertBefore(el("b", { "class": "tl" }, "Terms: "), tm.firstChild); kf.appendChild(tm); }

    if (!S.chapters) {
      var an = sec("s-block", "Analysis");
      an.appendChild(slot("Chapters to fill in: each one a claim, two short paragraphs and one chart."));
    }
    (S.chapters || []).forEach(function (ch, ci) {
      var cs = sec("s-chapter"); cs.id = "ch-" + ci;
      var tx = div("text", cs);
      div("n", tx, ch.n);
      tx.appendChild(el("h2", {}, ch.title));
      ch.paras.forEach(function (t) { tx.appendChild(rich(el("p"), t)); });
      if (ch.note) tx.appendChild(rich(el("p", { "class": "note" }), ch.note));
      var vc = div("s-viz", cs);
      var vis = p.chapters[ch.ch].visuals.map(function (v) { return v.ref != null ? charts[v.ref] : v; });
      var title = div("vt", vc);
      var seg = null;
      if (vis.length > 1) { var ctl = div("ctl", vc); seg = div("seg", ctl); }
      var holder = div("cv-host", vc);
      div("src", vc, ch.src);
      function show(i) {
        var old = holder.querySelector("canvas");
        if (old && window.Chart && Chart.getChart(old)) Chart.getChart(old).destroy();
        holder.innerHTML = "";
        title.textContent = vis[i].title;
        viz(vis[i], holder, true);
        if (seg) Array.prototype.forEach.call(seg.children, function (b, j) { b.setAttribute("aria-pressed", j === i ? "true" : "false"); });
      }
      if (seg) vis.forEach(function (v, i) {
        var b = el("button", { type: "button", "aria-pressed": "false" }, ch.tabs[i]);
        b.addEventListener("click", function () { show(i); });
        seg.appendChild(b);
      });
      show(0);
    });

    var rc = sec("s-block", "Recommendations");
    var recs = S.recs || (p.recommend || []).map(function (t) { return { text: t }; });
    var rg = div("s-recs", rc);
    if (!recs.length) rc.appendChild(slot("Recommendations to fill in: 2 to 3 actions, each with who should act and what to measure."));
    recs.forEach(function (x) {
      var d = div("rec", rg);
      if (x.who) div("who", d, x.who);
      if (x.title) d.appendChild(el("h3", {}, x.title));
      d.appendChild(rich(el("p"), x.text));
      if (x.measure) div("m", d, x.measure);
    });
    if (S.recNote) rc.appendChild(el("p", { "class": "pbi-note" }, S.recNote));
    if (S.next && S.next.length) {
      var nx = div("next-steps", rc); nx.appendChild(el("div", { "class": "nlabel" }, "What I would do next"));
      var nl = el("ol"); S.next.forEach(function (t) { nl.appendChild(rich(el("li"), t)); }); nx.appendChild(nl);
    }

    var mt = sec("s-block", "Data, model and method");
    var pl = div("pipeline", mt);
    var pipe = S.pipeline || (p.approach || []).map(function (t, i) { return { i: "0" + (i + 1) + " \u00b7 STEP", s: t }; });
    pipe.forEach(function (x) {
      var d = div("step", pl);
      div("i", d, x.i); if (x.b) d.appendChild(el("b", {}, x.b)); d.appendChild(rich(el("span"), x.s));
    });
    var bg = div("build-grid", mt);
    if (p.model && p.model.measures) {
      var p1 = div("panel dax-panel", bg);
      p1.appendChild(el("h3", {}, "Core measures (from the model)"));
      var pre = el("pre", { "class": "code dax" });
      p.model.measures.forEach(function (m, i) {
        if (i) pre.appendChild(document.createTextNode("\n\n"));
        pre.appendChild(el("span", { "class": "dx-name" }, m.name + " ="));
        pre.appendChild(document.createTextNode("\n"));
        dax(pre, m.dax);
      });
      p1.appendChild(pre);
    } else { bg.className += " solo"; }
    var p2 = div("panel", bg);
    p2.appendChild(el("h3", {}, "Limits of this analysis"));
    var lu = el("ul");
    p.limits.forEach(function (t) { lu.appendChild(rich(el("li"), t)); });
    p2.appendChild(lu);

    var idx = list.indexOf(p);
    var prev = list[(idx - 1 + list.length) % list.length], next = list[(idx + 1) % list.length];
    var nv = el("nav", { "class": "next-nav", "aria-label": "More case studies" });
    [[prev, "\u2190 Previous", ""], [next, "Next \u2192", " r"]].forEach(function (x) {
      var a2 = el("a", { href: "case.html?id=" + x[0].id, "class": x[2] ? "r" : "" });
      a2.appendChild(el("span", {}, x[1]));
      a2.appendChild(document.createTextNode(x[0].title));
      nv.appendChild(a2);
    });
    main.appendChild(nv);
  }
  renderStory(); return;

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

  /* ---- concise recruiter view, then the full analysis folded away */
  var more = null;
  if (p.brief) {
    var B = p.brief;
    host = main;
    main.appendChild(el("section", { "class": "kpi-block" })).appendChild(cardRow(p.kpis, "kpis", true));

    var kf = el("ol", { "class": "kf" });
    B.findings.forEach(function (t) { kf.appendChild(el("li", {}, t)); });
    section("What I found", kf, "tldr");

    var rb = el("div");
    rb.appendChild(gallery());
    if (p.downloads) {
      var dl0 = el("div", { "class": "downloads" });
      p.downloads.forEach(function (d) {
        var bx = el("div", { "class": "dl" });
        bx.appendChild(el("a", { "class": "btn primary", href: d.file, download: "" }, d.label));
        dl0.appendChild(bx);
      });
      rb.appendChild(dl0);
    }
    section("The Power BI report", rb, "pbi");

    var sk = el("div", { "class": "skills" });
    B.skills.forEach(function (s) {
      var d = el("div", { "class": "skill" });
      d.appendChild(el("h3", {}, s.skill));
      d.appendChild(el("p", {}, s.proof));
      sk.appendChild(d);
    });
    section("Skills this project shows", sk);

    var hp = el("div", { "class": "help" });
    B.help.forEach(function (s) {
      var d = el("div", { "class": "helpcard" });
      d.appendChild(el("h3", {}, s.title));
      d.appendChild(el("p", {}, s.text));
      hp.appendChild(d);
    });
    section("How I can help your team", hp);

    more = el("details", { "class": "more" });
    more.appendChild(el("summary", {}, "See the full analysis: method, charts, model and limits"));
    if (/[?&]full=1/.test(location.search)) more.setAttribute("open", "");
    main.appendChild(more);
    host = more;
  }

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
    if (p.downloads && !p.brief) {
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
    host.appendChild(bs);
  }

  /* ---- KPI and finding cards, like the report's Overview page */
  if (p.kpis && !p.brief) {
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
    host.appendChild(sp);
  } else {
    section("The question", el("p", {}, p.question));
    section("The data", el("p", {}, p.data + " Source: " + p.source + "."));
  }

  /* ---- Power BI report screenshots */
  function gallery() {
    var gal = el("div", { "class": "shots" });
    var wrap = null;
    if (p.hero != null) {
      wrap = el("div", { "class": "gal-wrap" });
      gal.className = "shots thumbs";
    }
    p.shots.forEach(function (s, si) {
      var big = wrap && si === p.hero;
      var fig = el("figure", { "class": "shot" + (big ? " shot-main" : "") });
      var img = el("img", { src: s.file, alt: s.caption, loading: big ? "eager" : "lazy" });
      img.addEventListener("error", function () { img.replaceWith(slot("Screenshot not added yet: save it as site/" + s.file)); });
      var open = el("a", { href: s.file, target: "_blank", rel: "noopener", title: "Open full size" });
      open.appendChild(img);
      fig.appendChild(open);
      fig.appendChild(el("figcaption", {}, big ? s.caption + " (click to enlarge)" : s.caption));
      if (big) wrap.appendChild(fig); else gal.appendChild(fig);
    });
    if (wrap) { wrap.appendChild(el("p", { "class": "gal-label" }, "All report pages")); wrap.appendChild(gal); return wrap; }
    return gal;
  }
  if (!p.brief && p.shots && p.shots.length) section("The Power BI report", gallery(), "pbi");

  /* ---- key findings */
  if (p.brief) {
    /* handled above */
  } else if (p.found.length) {
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
      host.appendChild(box);
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
    host.appendChild(ms);
  }

  section("Limits of this analysis", ul(p.limits));

  var repo = el("p", {});
  repo.appendChild(document.createTextNode("Code, SQL and the method write-up: "));
  repo.appendChild(el("a", { href: "https://github.com/Mihir0369/portfolio_website/tree/main/" + p.repo, target: "_blank", rel: "noopener" }, p.repo + "/ on GitHub"));
  repo.appendChild(document.createTextNode("."));
  host = main;
  section("Code and method", repo);
})();
