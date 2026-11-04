"""Pre-render the homepage content (featured case, project cards, About list, certificates) into index.html,
so search engines and text-only readers see it without running JavaScript.
Run from the site folder after editing projects.js:  python build_home.py
app.js leaves these blocks alone when they are already filled."""
import html, json, re, subprocess

E = lambda s: html.escape(str(s), quote=True)
data = json.loads(subprocess.check_output(["node", "-e", "global.window={};require('./projects.js');console.log(JSON.stringify(window))"], text=True, encoding="utf-8"))
P, ALL = data["PROFILE"], data["PROJECTS"]
L = [p for p in ALL if p.get("found")]
feat = next((p for p in L if p["id"] == "toronto-311"), L[0])
rest = [p for p in L if p is not feat]
shot = lambda p: p["shots"][p["hero"] if p.get("hero") is not None else 0]["file"]
href = lambda p: "case.html?id=" + p["id"]

def tags(p, n=None):
    return "".join('<span class="tag2">%s</span>' % E(t) for t in (p["tools"][:n] if n else p["tools"]))

feature = ('<div class="copy"><div class="industry">Featured case study &middot; %s</div><h3>%s</h3><p>%s</p>'
           '<div class="result"><b>%s %s</b><small>Real data &middot; %s</small></div><div class="tags2">%s</div>'
           '<div class="links2"><a class="tlink" href="%s">Explore case study &#8599;</a>'
           '<a class="tlink sec2" href="https://github.com/Mihir0369/portfolio_website/tree/main/%s" target="_blank" rel="noopener">GitHub source &#8599;</a></div></div>'
           '<div class="art"><img src="%s" alt="Power BI report page: %s" loading="lazy"></div>') % (
    E(feat["sector"]), E(feat["title"]), E(feat["summary"]), E(feat["headline"]["value"]), E(feat["headline"]["label"]),
    E(feat["source"]), tags(feat), href(feat), feat["repo"], E(shot(feat)), E(feat["title"]))

cards = "".join(
    '<a class="pcard" href="%s"><div class="pthumb t%d"><img src="%s" alt="Power BI report page: %s" loading="lazy"></div>'
    '<div class="copy"><div class="industry">%s &middot; %s</div><h3>%s</h3><p>%s</p><div class="tags2">%s</div>'
    '<span class="tlink">Explore case study &#8599;</span></div></a>' % (
        href(p), i % 3, E(shot(p)), E(p["title"]), E(p["sector"]), E(p["area"]), E(p["title"]), E(p["summary"]), tags(p, 3))
    for i, p in enumerate(rest))

n_done = len(L)
n_dev = len(ALL) - n_done
count = "Showing %d finished case studies &middot; %d in development" % (n_done, n_dev)

pills = "".join('<a class="pill cert" href="%s" target="_blank" rel="noopener">&#10003; Microsoft %s</a>' % (E(c.get("url") or "#"), E(c["label"].split(" ")[0])) for c in P["certs"])
pills += "".join('<span class="pill">%s</span>' % t for t in ["Power BI &middot; DAX", "SQL &middot; Python", "Microsoft Fabric"])

about = "".join('<div class="aitem"><b>%s</b><span>%s</span></div>' % (E(a), E(b)) for a, b in [
    ("Data & reporting experience", "Elevara Digital · Impact Zero · Scalezix Technologies"),
    ("Microsoft Certified: Power BI Data Analyst Associate", "PL-300 certification"),
    ("Microsoft Certified: Fabric Analytics Engineer Associate", "DP-600 certification"),
    ("Graduate Certificate, Business Insights and Analytics", "Humber Polytechnic, Toronto")])

ld = {"@context": "https://schema.org", "@type": "Person", "name": P["name"], "jobTitle": "Data Analyst", "address": {"@type": "PostalAddress", "addressLocality": "Toronto", "addressRegion": "ON", "addressCountry": "CA"},
      "sameAs": [P["linkedin"]], "knowsAbout": ["Power BI", "DAX", "SQL", "Python", "Microsoft Fabric", "Data analysis"]}
itemlist = {"@context": "https://schema.org", "@type": "ItemList", "name": "Case studies", "itemListElement": [
    {"@type": "ListItem", "position": i + 1, "name": p["title"], "description": p["summary"], "url": "https://mihir0369.github.io/portfolio_website/" + href(p)} for i, p in enumerate([feat] + rest)]}
jsonld = "".join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in (ld, itemlist))

t = open("index.html", encoding="utf-8").read()

def block(name, inner):
    global t
    pat = re.compile(r"<!--%s-->.*?<!--/%s-->" % (name, name), re.S)
    new = "<!--%s-->%s<!--/%s-->" % (name, inner, name)
    assert pat.search(t), name
    t = pat.sub(lambda m: new, t)

block("feature", feature)
block("cards", cards)
block("count", count)
block("pills", pills)
block("about", about)
block("jsonld", jsonld)
t = re.sub(r'(<img id="shell-img")[^>]*>', '<img id="shell-img" src="%s" alt="Power BI report: %s">' % (E(shot(feat)), E(feat["title"])), t)
t = re.sub(r'(<a class="shell" id="shell" href=")[^"]*"', r'\g<1>%s"' % href(feat), t)
open("index.html", "w", encoding="utf-8").write(t)
print("built:", n_done, "finished,", n_dev, "in development")
