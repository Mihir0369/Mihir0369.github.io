(function () {
  var P = window.PROFILE;
  // brand
  var b = document.getElementById("brand"), parts = P.name.split(" ");
  b.textContent = "";
  var m = document.createElement("span"); m.className = "mono"; m.textContent = (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
  var n = document.createElement("span"); n.textContent = P.name;
  var s = document.createElement("small"); s.textContent = "DATA \u00b7 INSIGHTS \u00b7 BUSINESS IMPACT"; n.appendChild(s);
  b.appendChild(m); b.appendChild(n);

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
    links.forEach(function (a) { var s = document.getElementById(a.getAttribute("href").slice(1)); if (s && s.getBoundingClientRect().top <= 120) cur = a; });
    setActive(cur.getAttribute("href"));
  }
  window.addEventListener("scroll", spy, { passive: true });
  links.forEach(function (a) { a.addEventListener("click", function () { setActive(a.getAttribute("href")); }); });
  spy();

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
