(function () {
  var P = window.PROFILE, b = document.getElementById("brand"), parts = P.name.split(" ");
  b.textContent = "";
  var m = document.createElement("span"); m.className = "mono"; m.setAttribute("aria-hidden", "true"); m.textContent = (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
  var n = document.createElement("span"); n.textContent = P.name;
  var s = document.createElement("small"); s.textContent = "BI Developer · Toronto"; n.appendChild(s);
  b.appendChild(m); b.appendChild(n);
  var menu = document.getElementById("menu");
  document.getElementById("burger").addEventListener("click", function () { menu.classList.toggle("open"); });
})();
