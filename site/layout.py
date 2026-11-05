"""Shared pieces for the generated pages: data, header, footer, page shell, project card."""
import html, json, subprocess

E = lambda s: html.escape(str(s), quote=True)
BASE = "https://mihir0369.github.io/"
data = json.loads(subprocess.check_output(["node", "-e", "global.window={};require('./projects.js');console.log(JSON.stringify(window))"], text=True, encoding="utf-8"))
P, ALL = data["PROFILE"], data["PROJECTS"]
S = P["story"]
L = [p for p in ALL if p.get("found")]
order = ["toronto-311", "household-credit", "collision-risk", "substance-harms"]
L.sort(key=lambda p: order.index(p["id"]) if p["id"] in order else 99)
href = lambda p: p["id"] + ".html"
tags = lambda xs: "".join('<span class="tag2">%s</span>' % E(t) for t in xs)

NAV = [("Home", "home"), ("Impact", "impact"), ("Projects", "projects"), ("About", "about"), ("Skills", "skills"), ("Experience", "experience")]


def header(prefix=""):
    links = "".join('<a href="%s#%s">%s</a>' % (prefix, h, n) for n, h in NAV)
    return ('<header class="site"><div class="wrap2"><a class="brand" href="index.html" id="brand"></a>'
            '<nav class="menu" id="menu" aria-label="Main navigation">%s<a class="btn impact small" href="%s#contact">Let&#39;s connect &#8599;</a></nav>'
            '<button class="burger" id="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="menu">&#9776;</button></div></header>') % (links, prefix)


def footer(prefix=""):
    return ('<footer class="foot"><div class="wrap2 fbot"><span>&copy; 2026 Mihir Jasani &middot; Data sources are credited on each case study. No employer or client data is used on this site.</span>'
            '<nav class="flinks" aria-label="Footer links"><a href="https://github.com/Mihir0369/Mihir0369.github.io" target="_blank" rel="noopener">GitHub</a><a href="https://www.linkedin.com/in/mihir-jasani/" target="_blank" rel="noopener">LinkedIn</a><a href="%s">Back to top &#8593;</a></nav>'
            '<b>Clean data. Clear decisions.</b></div></footer>') % ("#home" if not prefix else "#content")
