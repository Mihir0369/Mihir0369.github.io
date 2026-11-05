(function () {
  var P = window.PROFILE;
  // brand
  var b = document.getElementById("brand"), parts = P.name.split(" ");
  b.textContent = "";
  var n = document.createElement("span"); n.textContent = P.name;
  var s = document.createElement("small"); s.textContent = "DATA \u00b7 INSIGHTS \u00b7 BUSINESS IMPACT"; n.appendChild(s);
  b.appendChild(n);

  // contact links
  ["email", "email0", "linkedin", "linkedin2"].forEach(function (id) { var l = document.getElementById(id); if (l) l.href = id.indexOf("email") === 0 ? P.email : P.linkedin; });

  // menu: aria-expanded, Escape to close, focus back to the button
  var menu = document.getElementById("menu"), burger = document.getElementById("burger");
  function setMenu(open) {
    menu.classList.toggle("open", open);
    burger.setAttribute("aria-expanded", open ? "true" : "false");
    burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }
  burger.addEventListener("click", function () { setMenu(!menu.classList.contains("open")); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && menu.classList.contains("open")) { setMenu(false); burger.focus(); } });
  Array.prototype.forEach.call(menu.querySelectorAll("a"), function (a) { a.addEventListener("click", function () { setMenu(false); }); });

  // highlight the nav link of the section in view (by scroll position)
  var links = Array.prototype.slice.call(menu.querySelectorAll("a[href^='#']:not(.btn)"));
  function setActive(h) { links.forEach(function (a) { var on = a.getAttribute("href") === h; a.classList.toggle("active", on); if (on) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current"); }); }
  function spy() {
    if (!links.length) return;
    var cur = links[0];
    links.forEach(function (a) { var id = a.getAttribute("href").slice(1); if (id === "projects") id = "work"; var s = document.getElementById(id); if (s && s.getBoundingClientRect().top <= 120) cur = a; });
    setActive(cur.getAttribute("href"));
  }
  window.addEventListener("scroll", spy, { passive: true });
  links.forEach(function (a) { a.addEventListener("click", function () { setActive(a.getAttribute("href")); }); });
  spy();



  // "Projects" links scroll to the jump bar, so the first project is fully in view under the header
  var jb = document.querySelector(".pnav");
  function toProjects(smooth) {
    // measure the first project card, not the sticky jump bar: the bar moves to the bottom of the section once you scroll past it
    var card = document.querySelector(".proj");
    if (!jb || !card) return;
    var headerH = parseFloat(getComputedStyle(document.querySelector("header.site")).height) || 76;
    var gap = parseFloat(getComputedStyle(jb).marginBottom) || 22;
    var y = card.getBoundingClientRect().top + window.scrollY - (headerH + 6 + jb.offsetHeight + gap);
    window.scrollTo({ top: Math.max(0, y), behavior: smooth ? "smooth" : "instant" });
  }

  Array.prototype.forEach.call(document.querySelectorAll('a[href="#projects"], a[href="#work"]'), function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); history.pushState(null, "", "#projects"); toProjects(true); });
  });
  // arriving from another page (index.html#projects): the browser scrolls to the bar natively; re-apply once the page has settled
  if (location.hash === "#projects" || location.hash === "#work") {
    [0, 150, 500].forEach(function (ms) { setTimeout(function () { if (window.scrollY < 40 || ms) toProjects(false); }, ms); });
  }

  // project jump bar: mark the project in view
  var pl = Array.prototype.slice.call(document.querySelectorAll(".pnav a"));
  if (pl.length) {
    var bar = document.querySelector(".pnav");
    var markProject = function () {
      var line = bar.getBoundingClientRect().bottom + 40, cur = null;   // a project is "current" once its top passes just under the sticky bar
      pl.forEach(function (a) { var s = document.getElementById(a.getAttribute("href").slice(1)); if (s) { var r = s.getBoundingClientRect(); if (r.top <= line && r.bottom > line) cur = a; } });
      pl.forEach(function (a) { if (a === cur) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current"); });
    };
    window.addEventListener("scroll", markProject, { passive: true }); markProject();
  }

  // project report tabs: click or arrow keys / Home / End; the selected tab swaps the preview
  Array.prototype.forEach.call(document.querySelectorAll(".proj"), function (card) {
    var main = card.querySelector(".pv-main"), cap = card.querySelector(".pv-cap");
    var tabs = Array.prototype.slice.call(card.querySelectorAll(".pv-tab"));
    function select(t, focus) {
      tabs.forEach(function (x) { var on = x === t; x.setAttribute("aria-selected", on ? "true" : "false"); x.tabIndex = on ? 0 : -1; });
      main.src = t.getAttribute("data-src"); cap.textContent = t.getAttribute("data-cap");
      if (focus) t.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t, false); });
      t.addEventListener("keydown", function (e) {
        var k = e.key, j = -1;
        if (k === "ArrowRight" || k === "ArrowDown") j = (i + 1) % tabs.length;
        else if (k === "ArrowLeft" || k === "ArrowUp") j = (i - 1 + tabs.length) % tabs.length;
        else if (k === "Home") j = 0; else if (k === "End") j = tabs.length - 1;
        if (j > -1) { e.preventDefault(); select(tabs[j], true); }
      });
    });
  });
})();
