"""Build the static site from projects.js and evidence.js:
  - index.html: Hero > Impact > Projects > About > Skills > Experience > Contact
  - one crawlable page per finished project: <id>.html (with its own title, description, canonical and social tags)
  - case.html (legacy link) redirects to the project page; sitemap.xml
Run from the site folder after editing projects.js:  python build_evidence.py && python build_home.py"""
from layout import *
import json, os, re, datetime

BASE_URL = BASE
n_done, n_dev = len(L), len(ALL) - len(L)
IMPL = {  # one short business implication per card, taken from the recommendations on each case page
    "toronto-311": "Audit open-status records before reading them as a backlog.",
    "household-credit": "Test the 18-month lag before building lending targets on it.",
    "collision-risk": "Track the fatal share, not only the collision count.",
    "substance-harms": "Report all four measures together, with each source's coverage.",
}
QUESTION = {  # short card heading; the full question is on the case page
    "toronto-311": "Which 311 requests are recorded as open, and are the numbers comparable year to year?",
    "household-credit": "At what lag is credit growth most associated with earlier rate changes?",
    "collision-risk": "When and where do Canadian roads turn deadly?",
    "substance-harms": "Are opioid harms falling, or only some measures of them?",
}
HOME = {  # one result line per project card (all values already published on the case page)
    "toronto-311": "49.45% of 2025 parks, forestry and environment requests are recorded as open, against 1.37% to 6.60% in every other division",
    "household-credit": "Strongest negative association between rate changes and credit growth at an 18-month lag (correlation -0.52); observational, not causal",
    "collision-risk": "Among recorded fatal and injury collisions, the fatal share was 3.41% overnight against 1.52% by day (2.24x); not a per-trip risk",
    "substance-harms": "Opioid deaths fell 29.43% and EMS responses 7.84% from the 2023 peak to 2025. These are separately reported Canada totals, and each source covers different places",
}


def img_main(path):
    return path[:-4] + ".webp"


def img_sm(path):
    return path[:-4] + "-sm.webp"


def dims(path):
    from PIL import Image
    w, h = Image.open(path[:-4] + ".webp").size
    return w, h


def home_shots(p):
    sh = p["shots"]
    hero = p["hero"] if p.get("hero") is not None else 0
    idx = [hero] + [i for i in (0, len(sh) - 1) if i != hero]
    return [sh[i] for i in sorted(set(idx))][:3], sh[hero]


SHORT = {"toronto-311": "Toronto 311", "household-credit": "Household credit", "collision-risk": "Collision safety", "substance-harms": "Opioid harms"}


def card(p, n=0):
    thumbs, first = home_shots(p)
    w, h = dims(first["file"])
    tabs = "".join(
        '<button class="pv-tab" type="button" role="tab" id="tab-%s-%d" aria-selected="%s" tabindex="%s" aria-controls="pv-%s" data-src="%s" data-cap="%s" aria-label="%s" title="%s"><img src="%s" alt="" width="76" height="48" loading="lazy" decoding="async"></button>'
        % (p["id"], i, "true" if s is first else "false", "0" if s is first else "-1", p["id"], E(img_main(s["file"])), E(s["caption"]), E(s["caption"]), E(s["caption"]), E(img_sm(s["file"])))
        for i, s in enumerate(thumbs))
    return ('<article class="proj" id="proj-%s"><div class="copy"><div class="industry">%s &middot; %s &middot; %s</div>'
            '<dl class="qa"><div><dt>Business question</dt><dd class="q">%s</dd></div><div><dt>Key finding</dt><dd class="result">%s</dd></div>'
            '<div><dt>Business implication</dt><dd>%s</dd></div><div><dt>Skills demonstrated</dt><dd class="tags">%s</dd></div></dl>'
            '<div class="btns"><a class="btn impact" href="%s">Case study &#8599;</a>'
            '<a class="btn" href="https://github.com/Mihir0369/Mihir0369.github.io/tree/main/%s" target="_blank" rel="noopener">GitHub &#8599;</a></div></div>'
            '<div class="pv"><div id="pv-%s" role="tabpanel"><a class="pv-link" href="%s" title="Open the full case study"><img class="pv-main" src="%s" width="%d" height="%d" alt="Power BI report page: %s" loading="lazy" decoding="async"></a></div>'
            '<div class="pv-cap" aria-live="polite">%s</div><div class="pv-tabs" role="tablist" aria-label="%s report pages">%s</div></div></article>') % (
        p["id"], "%02d" % n, E(p["sector"]), E(p["area"]), E(QUESTION[p["id"]]), E(HOME[p["id"]]), E(IMPL[p["id"]]), "".join('<span class="tag2">%s</span>' % E(s.strip()[:1].upper() + s.strip()[1:]) for s in p["skills"].split(",")[:4]), href(p), p["repo"],
        p["id"], href(p), E(img_main(first["file"])), w, h, E(first["caption"]), E(first["caption"]), E(p["problem"]), tabs)


CHIPS = {
    "Data Analyst": ["SQL", "Power BI", "KPI definitions", "Data reconciliation"],
    "Data Analyst Intern": ["$400K+ pipeline covered", "50% faster deal tracking", "35% better follow-up"],
    "Jr Reporting Analyst": ["30% potential savings", "22 hrs a week saved", "Power BI", "Excel Power Query"],
}


def xp(x):
    if x["role"] == "Peer Tutor":
        return ('<article class="job compact"><div class="job-top"><h3>%s <small>&middot; %s</small></h3><span class="when">%s</span></div>'
                '<p>Delivered Excel, Power BI and statistics workshops and one-to-one support, explaining data modelling, regression and hypothesis testing in accessible language.</p></article>') % (E(x["role"]), E(x["org"]), E(x["when"]))

    def res(r):
        return '<div class="nq">%s</div>' % E(r) if r == "Not quantified" else "<div>%s</div>" % E(r)
    rows = "".join('<div class="xrow"><div>%s</div><div>%s</div>%s</div>' % (E(a), E(d), res(r)) for a, d, r in x["items"])
    return ('<article class="job"><div class="job-top"><h3>%s <small>&middot; %s</small></h3><span class="when">%s</span></div>'
            '<div class="jchips">%s</div><div class="xhead"><span>Action</span><span>Deliverable</span><span>Result</span></div>%s</article>') % (E(x["role"]), E(x["org"]), E(x["when"]), "".join('<span class="tag2">%s</span>' % E(c) for c in CHIPS.get(x["role"], [])), rows)


certs = "".join(
    '<div class="cert2"><span class="code">%s</span><div><b>%s</b><span>Microsoft Certified</span></div><a class="btn small" href="%s" target="_blank" rel="noopener">Verify &#8599;</a></div>'
    % (E(c["label"].split(" ")[0]), E(c["label"].split(" ", 1)[1]), E(c["url"])) for c in P["certs"])
stack = "".join('<div class="scard"><h3>%s</h3><div class="tags2">%s</div></div>' % (E(t), tags(xs)) for t, xs in P["stack"])
traits = "".join('<div class="trait"><i>%02d</i><b>%s</b><span>%s</span></div>' % (i + 1, E(a), E(b)) for i, (a, b) in enumerate(S["traits"]))
impact = "".join('<div class="cell"><strong>%s</strong><span>%s</span><em>%s</em></div>' % (E(a), E(b), E(c)) for a, b, c, d in S["impact"])
proof = "".join('<a class="chip-c" href="%s" target="_blank" rel="noopener" title="Verify on Microsoft Learn" aria-label="Microsoft %s certification, verify on Microsoft Learn">&#10003; %s &#8599;</a>' % (E(c["url"]), E(c["label"].split(" ")[0]), E(c["label"].split(" ")[0])) for c in P["certs"])

FRONT, BACK = "images/03-outcomes.webp", "images/cr-2-when.webp"
FW, FH = dims("images/03-outcomes.png")
BW, BH = dims("images/cr-2-when.png")
PHOTO = '<img src="images/mihir.jpg" alt="Mihir Jasani, data analyst" width="116" height="116">' if os.path.exists("images/mihir.jpg") else ""

main = """
    <section class="hero2" id="home">
      <div class="wrap2 hero-g">
        <div class="hcopy">
          <div class="ident">
            <div class="portrait"><span class="mono-big">MJ</span>%(photo)s</div>
            <div>
              <div class="hname">Mihir Jasani</div>
              <div class="role"><b>Data Analyst</b> at Elevara Digital, Toronto</div>
            </div>
          </div>
          <h1>From messy data to <em>clear business decisions.</em></h1>
          <p class="lead">I build reliable Power BI reporting and SQL-powered analysis. I clean and reconcile the data, then turn it into dashboards that teams can understand, trust and act on.</p>
          <div class="skillline">Power BI &middot; DAX &middot; SQL &middot; Python &middot; Microsoft Fabric</div>
          <div class="acts">
            <a class="btn impact" href="#projects">Explore my Project work &#8599;</a>
            <a class="btn" id="resume" href="downloads/Mihir-Jasani-Resume.pdf" target="_blank" rel="noopener">View Resume (PDF) &#8599;</a>
            <a class="btn" id="email0" href="%(mailto)s">Email me</a>
            <a class="btn" id="linkedin" href="%(linkedin)s" target="_blank" rel="noopener noreferrer">LinkedIn &#8599;</a>
          </div>
          <div class="trust"><span class="avail"><i></i>Open to Data, BI &amp; Reporting roles &middot; Toronto</span>%(proof)s</div>
        </div>
        <a class="hshot" href="toronto-311.html" aria-label="Open the Toronto 311 case study">
          <span class="win">
            <span class="wbar"><span class="dots"><i></i><i></i><i></i></span><b>Featured case study &middot; Toronto 311</b></span>
            <img src="%(front)s" width="%(fw)d" height="%(fh)d" alt="Power BI report from the Toronto 311 case study: share of requests recorded as open by division" fetchpriority="high" decoding="async">
            <span class="wover"><span class="wbtn">View case study &#8599;</span><small>Executive summary, SQL, data model and all report pages</small></span>
          </span>
        </a>
      </div>
    </section>

    <section class="impact2" id="impact">
      <div class="wrap2">
        <div class="ihead">
          <div><div class="eyebrow2">01 / Results</div><h2>Results I have delivered</h2></div>
        </div>
        <div class="igrid">
          %(impact)s
        </div>
      </div>
    </section>

    <section class="sec" id="work">
      <div class="wrap2">
        <div class="sec-head"><div><div class="eyebrow2">02 / Project work</div><h2>Real data. Real questions.<br>Clear, defensible findings.</h2></div></div>
        <nav class="pnav" id="projects" aria-label="Jump to a project"><span>Jump to</span>%(pnav)s</nav>
        %(projects)s
        <div class="mini-foot"><span>Showing %(nd)d finished case studies &middot; %(nv)d in development</span><a class="btn small" target="_blank" rel="noopener" href="https://github.com/Mihir0369/Mihir0369.github.io">View GitHub repository &#8599;</a></div>
      </div>
    </section>

    <section class="sec alt" id="about">
      <div class="wrap2 about2">
        <div>
          <div class="eyebrow2">03 / About and approach</div>
          <h2>I turn messy data into decisions people can trust.</h2>
          <p>%(about)s</p>
          <div class="acts"><a class="btn impact" href="downloads/Mihir-Jasani-Resume.pdf" target="_blank" rel="noopener">View Resume (PDF) &#8599;</a><a class="btn" href="%(mailto)s">Email me</a></div>
        </div>
        <div class="traits">%(traits)s</div>
      </div>
    </section>

    <section class="sec" id="skills">
      <div class="wrap2">
        <div class="sec-head"><div><div class="eyebrow2">04 / Tech stack and certifications</div><h2>The tools behind the work.</h2></div></div>
        <div class="glabel">Certifications</div>
        <div class="certs">%(certs)s</div>
        <div class="glabel">Tools</div>
        <div class="stack">%(stack)s</div>
        <div class="glabel">Education</div>
        <div class="edu2"><div><b>Graduate Certificate, Business Insights and Analytics</b><span>Humber Polytechnic, Toronto</span></div><div><b>B.Tech, Information Technology</b><span>P.P. Savani University</span></div></div>
      </div>
    </section>

    <section class="sec alt" id="experience">
      <div class="wrap2">
        <div class="sec-head"><div><div class="eyebrow2">05 / Experience</div><h2>What I did, what I delivered, what it changed.</h2></div></div>
        %(exp)s
      </div>
    </section>

    <section class="contact2 on-dark" id="contact">
      <div class="wrap2 in">
        <div>
          <div class="eyebrow2">LET'S WORK TOGETHER</div>
          <h2>Need someone who can turn reporting complexity into clarity?</h2>
          <p>Based in Toronto, Ontario. Open to Data Analyst, BI Analyst, Reporting Analyst and related roles in Canada.</p>
          <p class="cemail"><a href="%(mailto)s">%(emailtext)s</a></p>
        </div>
        <div class="cbtns">
          <a class="btn impact" id="email" href="%(mailto)s">Email me &#8599;</a>
          <a class="btn" href="downloads/Mihir-Jasani-Resume.pdf" target="_blank" rel="noopener">View Resume (PDF) &#8599;</a>
          <a class="btn" id="linkedin2" href="%(linkedin)s" target="_blank" rel="noopener noreferrer">LinkedIn &#8599;</a>
        </div>
      </div>
    </section>""" % dict(emailtext=E(P["email"].replace("mailto:", "")), front=FRONT, back=BACK, fw=FW, fh=FH, bw=BW, bh=BH, mailto=E(P["email"]), linkedin=E(P["linkedin"]), photo=PHOTO, proof=proof, impact=impact, about=E(S["about"]), traits=traits, stack=stack, certs=certs,
                         exp="".join(xp(x) for x in P["experienceStory"]), projects="".join(card(p, i + 1) for i, p in enumerate(L)), pnav="".join('<a href="#proj-%s">%s</a>' % (p["id"], E(SHORT[p["id"]])) for p in L), nd=n_done, nv=n_dev)

ld = {"@context": "https://schema.org", "@type": "Person", "name": P["name"], "jobTitle": "Data Analyst", "address": {"@type": "PostalAddress", "addressLocality": "Toronto", "addressRegion": "ON", "addressCountry": "CA"},
      "sameAs": [P["linkedin"]], "knowsAbout": ["Power BI", "DAX", "SQL", "Python", "Microsoft Fabric", "Data analysis"]}
itemlist = {"@context": "https://schema.org", "@type": "ItemList", "name": "Case studies", "itemListElement": [
    {"@type": "ListItem", "position": i + 1, "name": p["problem"], "description": p["summary"], "url": BASE_URL + href(p)} for i, p in enumerate(L)]}
jsonld = "".join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in (ld, itemlist))

SKIP = '<a class="skip" href="#content">Skip to main content</a>'
page = """<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mihir Jasani | Data Analyst (Power BI, SQL, Fabric) | Toronto</title>
  <meta name="description" content="Mihir Jasani, Toronto-based data analyst (Power BI PL-300, Microsoft Fabric DP-600). Four completed case studies on Canadian public data: Toronto 311, household credit, collision safety and opioid harms.">
  <link rel="canonical" href="%(base)s">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Mihir Jasani | Data Analyst (Power BI, SQL, Fabric) | Toronto">
  <meta property="og:description" content="Four completed Power BI case studies on Canadian public data, each with SQL checks, documented DAX and stated limits.">
  <meta property="og:url" content="%(base)s">
  <meta property="og:image" content="%(base)simages/social-card.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Mihir Jasani, data analyst in Toronto: Power BI, SQL and Microsoft Fabric">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="%(base)simages/social-card.png">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="buttons.css">
  <link rel="stylesheet" href="home.css">
  <link rel="stylesheet" href="pages.css">
  <link rel="stylesheet" href="unify.css">
  %(jsonld)s
</head>
<body class="home">
  %(skip)s
  %(header)s

  <main id="content">%(main)s
  </main>

  %(footer)s

  <script src="projects.js"></script>
  <script src="app.js"></script>
</body>
</html>
""" % dict(base=BASE_URL, jsonld=jsonld, main=main, header=header(), footer=footer(), skip=SKIP)
open("index.html", "w", encoding="utf-8").write(page)

# ---------------------------------------------------------------- one crawlable page per finished project
EV = json.loads(open("evidence.js", encoding="utf-8").read().split("window.EVIDENCE = ", 1)[1].rstrip().rstrip(";"))


def meta(p, k):
    for m in p.get("story", {}).get("meta", []):
        if m["k"] == k:
            return m.get("v", "")
    return ""


def first_shot(p):
    return p["shots"][p["hero"] if p.get("hero") is not None else 0]["file"]


def actions(p):
    z = next((d for d in p.get("downloads", []) if d["file"].endswith(".zip")), None)
    b = '<a class="btn impact" href="#report">View report</a><a class="btn" href="#sql">View SQL</a><a class="btn" href="#model">View data model</a>'
    if z:
        b += '<a class="btn" href="%s" download>Download Power BI project</a>' % E(z["file"])
    return '<div class="actions">%s</div>' % b


def case_main(p):
    s = p["story"]
    rec = (s["recs"][0]["title"] + ". " + s["recs"][0]["text"]) if s.get("recs") else p["recommend"][0]
    ex = [("Business problem", p["question"]), ("Dataset and scope", ". ".join(x for x in (meta(p, "Data"), meta(p, "Scope")) if x) + "."),
          ("My contribution", meta(p, "My role")), ("Key finding", p["headline"]["value"] + " " + p["headline"]["label"]),
          ("Recommended business action", rec), ("Limitations", " ".join(p["limits"][:2]))]
    rows = "".join('<div class="er"><b>%s</b><span>%s</span></div>' % (E(a), E(b)) for a, b in ex)
    cov = "".join('<div class="er"><b>%s</b><span>%s</span></div>' % (E(a), E(b)) for a, b in EV["coverage"][p["id"]])
    return ('<section class="case-head s-head"><div class="crumbs"><a href="index.html#projects">Projects</a> / %s</div><span class="tag">%s &middot; %s</span>'
            '<h1>%s</h1><p class="dek">%s</p><p class="bottom"><b class="bl">Bottom line: </b>%s</p></section>'
            '%s<section class="s-exec"><h2>Executive summary</h2><div class="exec">%s</div></section>'
            '<section class="s-tldr"><h2>Key findings</h2><ol>%s</ol></section>'
            '<section class="s-block"><h2>Data coverage</h2><div class="coverage">%s</div></section>'
            '<section class="s-block"><h2>Limits of this analysis</h2><ul>%s</ul></section>') % (
        E(p["sector"]), E(p["sector"]), E(p["area"]), E(p["title"]), E(s["dek"]), E(s["bottom"]), actions(p), rows,
        "".join("<li>%s</li>" % E(f) for f in s.get("findings", p["found"])), cov, "".join("<li>%s</li>" % E(l) for l in p["limits"]))


SEO_TITLE = {
    "toronto-311": "Toronto 311: Which Requests Stay Open?",
    "household-credit": "Rate Moves and Household Credit Growth",
    "collision-risk": "When Do Canadian Roads Turn Deadly?",
    "substance-harms": "Are Opioid Harms Really Falling?",
}


def case_page(p):
    desc = (p["problem"] + ". " + HOME[p["id"]] + ".")[:300]
    title = SEO_TITLE.get(p["id"], p["problem"]) + " | Mihir Jasani"
    url = BASE_URL + href(p)
    img = BASE_URL + first_shot(p)
    return """<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>%(title)s</title>
  <meta name="description" content="%(desc)s">
  <link rel="canonical" href="%(url)s">
  <meta property="og:type" content="article">
  <meta property="og:title" content="%(title)s">
  <meta property="og:description" content="%(desc)s">
  <meta property="og:url" content="%(url)s">
  <meta property="og:image" content="%(img)s">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="buttons.css">
  <link rel="stylesheet" href="theme.css">
  <link rel="stylesheet" href="pages.css">
  <link rel="stylesheet" href="unify.css">
</head>
<body class="inner">
  %(skip)s
  %(header)s
  <main class="wrap case" id="content"><div id="main">%(main)s</div></main>
  %(footer)s
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
  <script src="projects.js"></script>
  <script src="evidence.js"></script>
  <script>window.CASE_ID = "%(id)s";</script>
  <script src="case.js"></script>
  <script src="nav.js"></script>
</body>
</html>
""" % dict(title=E(title), desc=E(desc), url=url, img=img, skip=SKIP, header=header("index.html"), footer=footer("index.html"), main=case_main(p), id=p["id"])


for p in L:
    open(href(p), "w", encoding="utf-8").write(case_page(p))

# legacy case.html?id=... redirects to the project page
open("case.html", "w", encoding="utf-8").write("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Case study | Mihir Jasani</title><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><link rel="canonical" href="%sindex.html#projects">
<script>var m = new URLSearchParams(location.search).get("id"); var ok = %s; location.replace(ok.indexOf(m) > -1 ? m + ".html" : "index.html#projects");</script></head>
<body><p>Redirecting to the <a href="index.html#projects">projects</a>.</p></body></html>
""" % (BASE_URL, json.dumps([p["id"] for p in L])))

open("404.html", "w", encoding="utf-8").write("""<!doctype html>
<html lang="en" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found | Mihir Jasani</title><meta name="robots" content="noindex">
<link rel="icon" href="%(b)sfavicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="%(b)sstyles.css"><link rel="stylesheet" href="%(b)sbuttons.css"><link rel="stylesheet" href="%(b)shome.css"><link rel="stylesheet" href="%(b)spages.css"></head>
<body class="home"><main id="content" style="max-width:640px;margin:12vh auto;padding:0 20px;text-align:center">
<div class="eyebrow2" style="justify-content:center">404</div>
<h1>That page does not exist.</h1>
<p>The link may be old or mistyped. These pages are live:</p>
<p><a class="btn impact" href="%(b)sindex.html">Home</a> <a class="btn" href="%(b)sindex.html#projects">Case studies</a></p>
</main></body></html>
""" % dict(b=BASE_URL))

urls = [""] + [href(p) for p in L]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'] + ["  <url><loc>%s%s</loc></url>" % (BASE_URL, u) for u in urls] + ["</urlset>"]
open("sitemap.xml", "w", encoding="utf-8").write(chr(10).join(sm) + chr(10))
print("built: index + %d project pages (%d in development)" % (n_done, n_dev))
