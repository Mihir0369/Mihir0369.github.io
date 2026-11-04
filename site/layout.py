"""Shared pieces for the generated pages: data, header, footer, page shell, project card."""
import html, json, subprocess

E = lambda s: html.escape(str(s), quote=True)
BASE = "https://mihir0369.github.io/portfolio_website/"
data = json.loads(subprocess.check_output(["node", "-e", "global.window={};require('./projects.js');console.log(JSON.stringify(window))"], text=True, encoding="utf-8"))
P, ALL = data["PROFILE"], data["PROJECTS"]
S = P["story"]
L = [p for p in ALL if p.get("found")]
order = ["toronto-311", "household-credit", "collision-risk", "substance-harms"]
L.sort(key=lambda p: order.index(p["id"]) if p["id"] in order else 99)
href = lambda p: "case.html?id=" + p["id"]
tags = lambda xs: "".join('<span class="tag2">%s</span>' % E(t) for t in xs)

NAV = [("Home", "home"), ("About", "about"), ("Impact", "impact"), ("Skills", "skills"), ("Experience", "experience"), ("Projects", "work")]


def header(prefix=""):
    links = "".join('<a href="%s#%s">%s</a>' % (prefix, h, n) for n, h in NAV)
    return ('<header class="site"><div class="wrap2"><a class="brand" href="%sindex.html" id="brand"></a>'
            '<nav class="menu" id="menu" aria-label="Main navigation">%s<a class="btn impact small" href="%s#contact">Let&#39;s connect &#8599;</a></nav>'
            '<button class="burger" id="burger" aria-label="Toggle menu">&#9776;</button></div></header>') % (prefix, links, prefix)


def footer(prefix=""):
    return ('<footer class="foot"><div class="wrap2 fbot"><span>&copy; 2026 Mihir Jasani &middot; Data sources are credited on each case study. No employer or client data is used on this site.</span>'
            '<b>Clean data. Clear decisions.</b></div></footer>')


def project(p):
    shots = p["shots"]
    first = shots[p["hero"] if p.get("hero") is not None else 0]
    tabs = "".join(
        '<button class="pv-tab" type="button" role="tab" aria-selected="%s" data-src="%s" data-cap="%s" aria-label="%s" title="%s"><img src="%s" alt="" loading="lazy"></button>'
        % ("true" if s is first else "false", E(s["file"]), E(s["caption"]), E(s["caption"]), E(s["caption"]), E(s["file"])) for s in shots)
    return ('<article class="proj"><div class="copy"><div class="industry">%s &middot; %s</div><h3>%s</h3>'
            '<div class="result">%s %s</div><ul class="feat">%s</ul><div class="tags2">%s</div>'
            '<div class="btns"><a class="btn impact" href="%s">Explore case study &#8599;</a>'
            '<a class="btn" href="https://github.com/Mihir0369/portfolio_website/tree/main/%s" target="_blank" rel="noopener">GitHub source &#8599;</a></div></div>'
            '<div class="pv"><a class="pv-link" href="%s" title="Open the full case study"><img class="pv-main" src="%s" alt="Power BI report page: %s"></a><div class="pv-cap">%s</div>'
            '<div class="pv-tabs" role="tablist" aria-label="Report pages">%s</div></div></article>') % (
        E(p["sector"]), E(p["area"]), E(p["problem"]), E(p["headline"]["value"]), E(p["headline"]["label"]),
        "".join("<li>%s</li>" % E(f) for f in p["features"]), tags(p["tools"]), href(p), p["repo"], href(p), E(first["file"]), E(p["title"]), E(first["caption"]), tabs)
