(function () {
  var P = window.PROFILE, main = document.getElementById("main");
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  function link(text, href, ext) { var a = el("a", null, text); a.href = href; if (ext) { a.target = "_blank"; a.rel = "noopener noreferrer"; } return a; }

  var b = document.getElementById("brand"), parts = P.name.split(" ");
  var m = el("span", "mono", (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase());
  b.textContent = ""; b.appendChild(m); b.appendChild(el("span", null, P.name));
  var nl = document.getElementById("nav-linkedin"); nl.href = P.linkedin; nl.target = "_blank"; nl.rel = "noopener noreferrer";
  document.title = "About | " + P.name;

  var layout = el("div", "about-layout"), left = el("div", "about-main"), side = el("aside", "about-side");
  left.appendChild(el("div", "eyebrow", "About"));
  left.appendChild(el("h1", null, P.name));
  P.about.forEach(function (t) { left.appendChild(el("p", "lead", t)); });

  left.appendChild(el("h2", null, "About this portfolio"));
  left.appendChild(el("p", "lead", P.aboutPortfolio));

  if (P.experience && P.experience.length) {
    left.appendChild(el("h2", null, "Experience"));
    P.experience.forEach(function (x) {
      var d = el("div", "xp");
      d.appendChild(el("div", "when", x.when)); d.appendChild(el("h3", null, x.role));
      d.appendChild(el("div", "org", x.org)); var ul = el("ul", "xp-list"); [].concat(x.text).forEach(function (t) { ul.appendChild(el("li", null, t)); }); d.appendChild(ul);
      left.appendChild(d);
    });
  }

  function card(title) { var c = el("div", "side-card"); c.appendChild(el("h3", null, title)); side.appendChild(c); return c; }

  var c1 = card("Contact");
  var cu = el("ul", "plain");
  var li = el("li"); li.appendChild(link(P.email.replace("mailto:", ""), P.email)); cu.appendChild(li);
  li = el("li"); li.appendChild(link(P.linkedin.replace("https://www.", ""), P.linkedin, true)); cu.appendChild(li);
  cu.appendChild(el("li", null, P.location));
  c1.appendChild(cu);
  if (P.resume) { var rb = link("Download resume (PDF)", P.resume); rb.className = "btn primary"; c1.appendChild(rb); }

  var c2 = card("Certifications");
  P.certs.forEach(function (c) {
    var row = el("div", "cert");
    var code = c.label.split(" ")[0];
    row.appendChild(el("span", "badge", code.replace("-", "")));
    var t = el("div"); t.appendChild(el("b", null, c.label.replace(code + " ", "")));
    t.appendChild(el("div", "org", "Microsoft · " + code));
    row.appendChild(t);
    if (c.url) { var v = link("Verify ↗", c.url, true); v.className = "vbtn"; row.appendChild(v); }
    c2.appendChild(row);
  });

  var c3 = card("Tools");
  var tu = el("ul", "plain");
  P.toolGroups.forEach(function (g) { var i = el("li"); i.appendChild(el("b", null, g[0])); i.appendChild(document.createTextNode(": " + g[1])); tu.appendChild(i); });
  c3.appendChild(tu);

  var c4 = card("Education");
  var eu = el("ul", "plain"); P.education.forEach(function (e) { eu.appendChild(el("li", null, e)); }); c4.appendChild(eu);

  layout.appendChild(left); layout.appendChild(side); main.appendChild(layout);
})();
