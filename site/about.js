(function () {
  var P = window.PROFILE, main = document.getElementById("main");
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  function link(text, href, ext) { var a = el("a", null, text); a.href = href; if (ext) { a.target = "_blank"; a.rel = "noopener noreferrer"; } return a; }

  var b = document.getElementById("brand"), parts = P.name.split(" ");
  var m = el("span", "mono", (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase());
  b.textContent = ""; b.appendChild(m); b.appendChild(el("span", null, P.name));
  var nl = document.getElementById("nav-linkedin"); nl.href = P.linkedin; nl.target = "_blank"; nl.rel = "noopener noreferrer";
  document.title = "About | " + P.name;

  main.appendChild(el("div", "eyebrow", "About"));
  main.appendChild(el("h1", null, P.name));
  P.about.forEach(function (t) { main.appendChild(el("p", "lead", t)); });

  main.appendChild(el("h2", null, "About this portfolio"));
  main.appendChild(el("p", "lead", P.aboutPortfolio));

  if (P.experience && P.experience.length) {
    main.appendChild(el("h2", null, "Experience"));
    P.experience.forEach(function (x) {
      var d = el("div", "xp");
      d.appendChild(el("div", "when", x.when)); d.appendChild(el("h3", null, x.role));
      d.appendChild(el("div", "org", x.org)); d.appendChild(el("p", null, x.text));
      main.appendChild(d);
    });
  }

  var grid = el("div", "about-grid");
  var l = el("div"), r = el("div");

  l.appendChild(el("h3", null, "Certifications"));
  P.certs.forEach(function (c) {
    var row = el("div", "cert");
    var code = c.label.split(" ")[0];
    row.appendChild(el("span", "badge", code.replace("-", "")));
    var t = el("div"); t.appendChild(el("b", null, c.label.replace(code + " ", "")));
    t.appendChild(el("div", "org", "Microsoft · " + code));
    row.appendChild(t);
    if (c.url) row.appendChild(link("Verify ↗", c.url, true));
    l.appendChild(row);
  });
  l.appendChild(el("h3", null, "Education"));
  var ul = el("ul"); P.education.forEach(function (e) { ul.appendChild(el("li", null, e)); }); l.appendChild(ul);

  r.appendChild(el("h3", null, "Contact"));
  var cu = el("ul");
  var li = el("li"); li.appendChild(link(P.email.replace("mailto:", ""), P.email)); cu.appendChild(li);
  li = el("li"); li.appendChild(link("LinkedIn", P.linkedin, true)); cu.appendChild(li);
  cu.appendChild(el("li", null, P.location));
  if (P.resume) { li = el("li"); li.appendChild(link("Download resume (PDF)", P.resume)); cu.appendChild(li); }
  r.appendChild(cu);
  r.appendChild(el("h3", null, "Tools"));
  var tu = el("ul");
  P.toolGroups.forEach(function (g) { var i = el("li"); i.appendChild(el("b", null, g[0])); i.appendChild(document.createTextNode(": " + g[1])); tu.appendChild(i); });
  r.appendChild(tu);

  grid.appendChild(l); grid.appendChild(r); main.appendChild(grid);
})();
