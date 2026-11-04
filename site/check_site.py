"""Quality checks for the generated site. Run from the site folder:
    python check_site.py             internal checks (links, assets, ids, meta tags, projects, sitemap, downloads)
    python check_site.py --external  also request every external link (resume host, GitHub, certifications)
Exit code 1 if anything fails, so it can gate deployment."""
import glob, json, os, re, subprocess, sys, urllib.request, urllib.error
from html.parser import HTMLParser

errors, notes = [], []
err = lambda m: errors.append(m)
data = json.loads(subprocess.check_output(["node", "-e", "global.window={};require('./projects.js');console.log(JSON.stringify(window))"], text=True, encoding="utf-8"))
PROJ, PROF = data["PROJECTS"], data["PROFILE"]
DONE = [p for p in PROJ if p.get("found")]
BASE = "https://mihir0369.github.io/portfolio_website/"
JS_ANCHORS = {"report", "coverage", "sql"}  # added by case.js in the browser


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.srcs, self.metas, self.h1, self.title, self._t, self.noalt = [], [], [], {}, 0, "", False, 0
        self.canon = None

    def handle_starttag(self, tag, a):
        a = dict(a)
        if "id" in a: self.ids.append(a["id"])
        if tag == "a" and "href" in a: self.links.append(a["href"])
        if tag in ("img", "script", "source") and a.get("src"): self.srcs.append(a["src"])
        if tag == "link" and a.get("href"):
            if a.get("rel") == "canonical": self.canon = a["href"]
            else: self.srcs.append(a["href"])
        if tag == "img" and "alt" not in a: self.noalt += 1
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k: self.metas[k] = a.get("content", "")
        if tag == "h1": self.h1 += 1
        if tag == "title": self._t = True

    def handle_endtag(self, tag):
        if tag == "title": self._t = False

    def handle_data(self, d):
        if self._t: self.title += d


pages = {}
for f in sorted(glob.glob("*.html")):
    pg = Page(); pg.feed(open(f, encoding="utf-8").read()); pages[f] = pg
    raw = open(f, encoding="utf-8").read()
    for bad in ("index.htmlindex.html", "undefined", "NaN", "[object"):
        if bad in raw: err("%s contains %r" % (f, bad))

# required tags, h1, duplicate ids, image alt
for f, pg in pages.items():
    if f == "case.html": continue  # redirect stub
    if not pg.title.strip(): err("%s: no <title>" % f)
    for k in ("description", "og:title", "og:description", "og:url"):
        if not pg.metas.get(k): err("%s: missing meta %s" % (f, k))
    if not pg.canon: err("%s: missing canonical" % f)
    if pg.h1 != 1: err("%s: expected one <h1>, found %d" % (f, pg.h1))
    dup = {i for i in pg.ids if pg.ids.count(i) > 1}
    if dup: err("%s: duplicate ids %s" % (f, sorted(dup)))
    if pg.noalt: err("%s: %d <img> without alt" % (f, pg.noalt))
titles = [pg.title for f, pg in pages.items() if f != "case.html"]
if len(set(titles)) != len(titles): err("page titles are not unique")

# links and assets
ext = set()
for f, pg in pages.items():
    for u in pg.links + pg.srcs:
        if u.startswith(("http://", "https://")): ext.add(u); continue
        if u.startswith(("mailto:", "tel:", "data:", "javascript:")): continue
        path, _, frag = u.partition("#")
        path = path.split("?")[0] or f
        if not os.path.exists(path): err("%s: missing file %s" % (f, u)); continue
        if frag and path.endswith(".html"):
            tgt = pages.get(path)
            if tgt and frag not in tgt.ids and not (frag in JS_ANCHORS and path != "index.html"): err("%s: anchor #%s not found in %s" % (f, frag, path))

# projects: page, images (png, webp, thumbnail), downloads, sitemap
sm = open("sitemap.xml", encoding="utf-8").read()
if BASE not in sm: err("sitemap missing home")
for p in DONE:
    page = p["id"] + ".html"
    if page not in pages: err("no page for project %s" % p["id"]); continue
    if BASE + page not in sm: err("sitemap missing %s" % page)
    if not p.get("problem") or not p.get("features") or not p.get("skills"): err("%s: needs problem, features, skills" % p["id"])
    for s in p["shots"]:
        for q in (s["file"], s["file"][:-4] + ".webp", s["file"][:-4] + "-sm.webp"):
            if not os.path.exists(q): err("%s: missing image %s" % (p["id"], q))
    for d in p.get("downloads", []):
        if not os.path.exists(d["file"]): err("%s: missing download %s" % (p["id"], d["file"]))
        elif os.path.getsize(d["file"]) < 1000: err("%s: download looks empty %s" % (p["id"], d["file"]))
        if d["file"].endswith(".zip"):
            import zipfile
            try:
                names = zipfile.ZipFile(d["file"]).namelist()
                if not any(n.lower().endswith("readme.md") or n.lower().endswith(".pbip") for n in names): err("%s: zip lacks README or .pbip: %s" % (p["id"], d["file"]))
            except Exception as e:
                err("%s: bad zip %s (%s)" % (p["id"], d["file"], e))
    if not os.path.isdir(os.path.join("..", p["repo"])): err("%s: repo folder %s not found" % (p["id"], p["repo"]))
    idx = pages["index.html"]
    if page not in idx.links: err("index.html does not link to %s" % page)
if not os.path.exists(PROF["resume"]): err("resume file missing: %s" % PROF["resume"])
if PROF["resume"] not in pages["index.html"].links: err("index.html does not link the resume")
for c in PROF["certs"]:
    if c["url"] not in pages["index.html"].links: err("certification link missing on index.html: %s" % c["label"])

# external links (optional)
if "--external" in sys.argv:
    for c in PROF["certs"]: ext.add(c["url"])
    for u in sorted(ext):
        if "cdnjs" in u: continue
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (site-check)"})
        try:
            r = urllib.request.urlopen(req, timeout=20); code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            code = str(e)[:60]
        ok = isinstance(code, int) and code < 400
        if "linkedin.com" in u and code in (999, 403): notes.append("manual check (LinkedIn blocks scripts): %s" % u); continue
        (notes if ok else errors).append("%s %s" % (code, u))

print("pages checked:", ", ".join(pages))
for n in notes: print("  ok/note:", n)
if errors:
    print("\nFAILED (%d):" % len(errors))
    for e in errors: print("  -", e)
    sys.exit(1)
print("\nAll checks passed.")
