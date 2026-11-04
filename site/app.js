(function () {
  var P = window.PROFILE;
  // brand
  var b = document.getElementById("brand"), parts = P.name.split(" ");
  b.textContent = "";
  var m = document.createElement("span"); m.className = "mono"; m.textContent = (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
  var n = document.createElement("span"); n.textContent = P.name;
  var s = document.createElement("small"); s.textContent = "DATA · INSIGHTS · BUSINESS IMPACT"; n.appendChild(s);
  b.appendChild(m); b.appendChild(n);

  // contact links
  ["email", "linkedin", "linkedin2"].forEach(function (id) { var l = document.getElementById(id); if (l) l.href = id === "email" ? P.email : P.linkedin; });

  // menu
  var menu = document.getElementById("menu");
  document.getElementById("burger").addEventListener("click", function () { menu.classList.toggle("open"); });
  Array.prototype.forEach.call(menu.querySelectorAll("a"), function (a) { a.addEventListener("click", function () { menu.classList.remove("open"); }); });

  // highlight the nav link of the section in view (by scroll position)
  var links = Array.prototype.slice.call(menu.querySelectorAll("a[href^='#']:not(.btn)"));
  function setActive(h) { links.forEach(function (a) { a.classList.toggle("active", a.getAttribute("href") === h); }); }
  function spy() {
    if (!links.length) return;
    var cur = links[0];
    links.forEach(function (a) { var s = document.getElementById(a.getAttribute("href").slice(1)); if (s && s.getBoundingClientRect().top <= 120) cur = a; });
    setActive(cur.getAttribute("href"));
  }
  window.addEventListener("scroll", spy, { passive: true });
  links.forEach(function (a) { a.addEventListener("click", function () { setActive(a.getAttribute("href")); }); });
  spy();

  // project report tabs: click a small thumbnail to preview that page
  Array.prototype.forEach.call(document.querySelectorAll(".proj"), function (card) {
    var main = card.querySelector(".pv-main"), cap = card.querySelector(".pv-cap");
    var tabs = card.querySelectorAll(".pv-tab");
    Array.prototype.forEach.call(tabs, function (t) {
      t.addEventListener("click", function () {
        Array.prototype.forEach.call(tabs, function (x) { x.setAttribute("aria-selected", x === t ? "true" : "false"); });
        main.src = t.getAttribute("data-src"); cap.textContent = t.getAttribute("data-cap");
      });
    });
  });
})();
