"""Build the static site from projects.js and evidence.js:
  - index.html: Hero > Impact > Projects > About > Skills > Experience > Contact
  - one crawlable page per finished project: <id>.html (with its own title, description, canonical and social tags)
  - case.html (legacy link) redirects to the project page; sitemap.xml
Run from the site folder after editing projects.js:  python build_evidence.py && python build_home.py"""
from layout import *
import json, os, re, datetime

BASE_URL = BASE
n_done, n_dev = len(L), len(ALL) - len(L)
IMPL = {  # business implication per card, taken from the recommendations on each case page
    "toronto-311": "Audit the open-status records before treating them as a backlog, and publish a closed date and a request-type mapping.",
    "household-credit": "Test the 18-month lag before setting lending targets around it, and add arrears data to test repayment pressure.",
    "collision-risk": "Track the fatal share, not only the count. Use night, single-vehicle and uncontrolled-road patterns as a watch list, not as risk per trip.",
    "substance-harms": "Report deaths, hospital stays, emergency visits and EMS responses together, and state which places each source covers.",
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


def card(p):
    thumbs, first = home_shots(p)
    w, h = dims(first["file"])
    tabs = "".join(
        '<button class="pv-tab" type="button" role="tab" id="tab-%s-%d" aria-selected="%s" tabindex="%s" aria-controls="pv-%s" data-src="%s" data-cap="%s" aria-label="%s" title="%s"><img src="%s" alt="" width="76" height="48" loading="lazy" decoding="async"></button>'
        % (p["id"], i, "true" if s is first else "false", "0" if s is first else "-1", p["id"], E(img_main(s["file"])), E(s["caption"]), E(s["caption"]), E(s["caption"]), E(img_sm(s["file"])))
        for i, s in enumerate(thumbs))
    return ('<article class="proj"><div class="copy"><div class="industry">%s &middot; %s</div>'
            '<dl class="qa"><div><dt>Business question</dt><dd class="q">%s</dd></div><div><dt>Key finding</dt><dd class="result">%s</dd></div>'
            '<div><dt>Business implication</dt><dd>%s</dd></div><div><dt>Skills demonstrated</dt><dd>%s</dd></div></dl>'
            '<div class="btns"><a class="btn impact" href="%s">Case study &#8599;</a>'
            '<a class="btn" href="https://github.com/Mihir0369/portfolio_website/tree/main/%s" target="_blank" rel="noopener">GitHub &#8599;</a></div></div>'
            '<div class="pv"><div id="pv-%s" role="tabpanel"><a class="pv-link" href="%s" title="Open the full case study"><img class="pv-main" src="%s" width="%d" height="%d" alt="Power BI report page: %s" loading="lazy" decoding="async"></a></div>'
            '<div class="pv-cap" aria-live="polite">%s</div><div class="pv-tabs" role="tablist" aria-label="%s report pages">%s</div></div></article>') % (
        E(p["sector"]), E(p["area"]), E(p["problem"]), E(HOME[p["id"]]), E(IMPL[p["id"]]), E(p["skills"]), href(p), p["repo"],
        p["id"], href(p), E(img_main(first["file"])), w, h, E(first["caption"]), E(first["caption"]), E(p["problem"]), tabs)


def xp(x):
    if x["role"] == "Peer Tutor":
        return ('<article class="job compact"><div class="job-top"><h3>%s <small>&middot; %s</small></h3><span class="when">%s</span></div>'
                '<p>Delivered Excel, Power BI and statistics workshops and one-to-one support, explaining data modelling, regression and hypothesis testing in accessible language.</p></article>') % (E(x["role"]), E(x["org"]), E(x["when"]))

    def res(r):
        return '<div class="nq">%s</div>' % E(r) if r == "Not quantified" else "<div>%s</div>" % E(r)
    rows = "".join('<div class="xrow"><div>%s</div><div>%s</div>%s</div>' % (E(a), E(d), res(r)) for a, d, r in x["items"])
    return ('<article class="job"><div class="job-top"><h3>%s <small>&middot; %s</small></h3><span class="when">%s</span></div>'
            '<div class="xhead"><span>Action</span><span>Deliverable</span><span>Result</span></div>%s</article>') % (E(x["role"]), E(x["org"]), E(x["when"]), rows)


certs = "".join(
    '<div class="cert2"><span class="code">%s</span><div><b>%s</b><span>Microsoft Certified</span></div><a class="btn small" href="%s" target="_blank" rel="noopener">Verify &#8599;</a></div>'
    % (E(c["label"].split(" ")[0]), E(c["label"].split(" ", 1)[1]), E(c["url"])) for c in P["certs"])
NOTES = ["Used in all four case studies and at work", "SQL checks and Python loaders behind every project", "DP-600 certified; case study 4 is in development"]
stack = "".join('<div class="scard"><h3>%s</h3><div class="tags2">%s</div><p class="note">%s</p></div>' % (E(t), tags(xs), E(NOTES[i])) for i, (t, xs) in enumerate(P["stack"]))
traits = "".join('<div class="trait"><b>%s</b><span>%s</span></div>' % (E(a), E(b)) for a, b in S["traits"])
impact = "".join('<div class="cell"><strong>%s</strong><span>%s</span><em>%s</em><small>%s</small></div>' % (E(a), E(b), E(c), E(d)) for a, b, c, d in S["impact"])
proof = "".join('<a class="pill cert" href="%s" target="_blank" rel="noopener">&#10003; Microsoft %s <small>verify</small></a>' % (E(c["url"]), E(c["label"].split(" ")[0])) for c in P["certs"])
proof += '<span class="pill">%d end-to-end case studies on real public data</span><span class="pill">Every project downloadable on GitHub</span>' % n_done

PHOTO = '<img src="images/mihir.jpg" alt="Mihir Jasani, data analyst" width="168" height="168">' if os.path.exists("images/mihir.jpg") else ""

main = """
    <section class="hero2" id="home">
      <div class="wrap2 hero-c">
        <div class="portrait"><span class="mono-big">MJ</span>%(photo)s</div>
        <div class="hello">Hello, I'm <strong>Mihir Jasani</strong></div>
        <div class="role"><b>Data Analyst</b> &middot; Power BI &middot; SQL &middot; Microsoft Fabric</div>
        <div class="avail"><i></i>Toronto, Canada &middot; Open to Data, BI and Reporting Analyst roles</div>
        <h1>From messy data to <em>clear business decisions.</em></h1>
        <p class="lead">I build reliable Power BI reporting and SQL-powered analysis. I clean and reconcile the data, then turn it into dashboards that teams can understand, trust and act on.</p>
        <div class="acts">
          <a class="btn impact" href="#work">Explore my Project work &#8599;</a>
          <a class="btn" id="resume" href="downloads/Mihir-Jasani-Resume.pdf" download>Download Resume (PDF)</a>
          <a class="btn" id="email0" href="%(mailto)s">Email me</a>
          <a class="btn" id="linkedin" href="%(linkedin)s" target="_blank" rel="noopener noreferrer">LinkedIn &#8599;</a>
        </div>
        <div class="proof">%(proof)s</div>
      </div>
    </section>

    <section class="impact2" id="impact">
      <div class="wrap2">
        <div class="in">
          <div class="intro">01 / Results I have delivered.<span>From my analyst roles. The case studies below use public data only.</span></div>
          %(impact)s
        </div>
        <p class="inote">%(inote)s</p>
      </div>
    </section>

    <section class="sec" id="work">
      <div class="wrap2">
        <div class="sec-head"><div><div class="eyebrow2">02 / Project work</div><h2>Real data. Real questions.<br>Clear, defensible findings.</h2></div>
          <p>Each case study starts with the problem it solves. Open one for the executive summary, data coverage, SQL checks and the full report.</p></div>
        %(projects)s
        <div class="mini-foot"><span>Showing %(nd)d finished case studies &middot; %(nv)d in development</span><a class="btn small" target="_blank" rel="noopener" href="https://github.com/Mihir0369/portfolio_website">View GitHub repository &#8599;</a></div>
      </div>
    </section>

    <section class="sec alt" id="about">
      <div class="wrap2 about2">
        <div>
          <div class="eyebrow2">03 / About and approach</div>
          <h2>I turn messy data into decisions people can trust.</h2>
          <p>%(about)s</p>
        </div>
        <div class="traits">%(traits)s</div>
      </div>
    </section>

    <section class="sec" id="skills">
      <div class="wrap2">
        <div class="sec-head"><div><div class="eyebrow2">04 / Tech stack and certifications</div><h2>The tools behind the work.</h2></div>
          <p>Verified Microsoft credentials, and the stack I use day to day.</p></div>
        <div class="stack">%(stack)s</div>
        <div class="certs">%(certs)s</div>
        <div class="edu2"><div><b>Graduate Certificate, Business Insights and Analytics</b><span>Humber Polytechnic, Toronto</span></div><div><b>B.Tech, Information Technology</b><span>P.P. Savani University</span></div></div>
      </div>
    </section>

    <section class="sec alt" id="experience">
      <div class="wrap2">
        <div class="sec-head"><div><div class="eyebrow2">05 / Experience</div><h2>What I did, what I delivered, what it changed.</h2></div>
          <p>Each duty shows the action, the deliverable and the result. Where a result was not measured, it says so.</p></div>
        %(exp)s
      </div>
    </section>

    <section class="contact2 on-dark" id="contact">
      <div class="wrap2 in">
        <div>
          <div class="eyebrow2">LET'S WORK TOGETHER</div>
          <h2>Need someone who can turn reporting complexity into clarity?</h2>
          <p>Based in Toronto, Ontario. Open to Data Analyst, BI Analyst, Reporting Analyst and related roles in Canada.</p>
        </div>
        <div class="cbtns">
          <a class="btn impact" id="email" href="%(mailto)s">Email me &#8599;</a>
          <a class="btn" href="downloads/Mihir-Jasani-Resume.pdf" download>Resume (PDF)</a>
          <a class="btn" id="linkedin2" href="%(linkedin)s" target="_blank" rel="noopener noreferrer">LinkedIn &#8599;</a>
        </div>
      </div>
    </section>""" % dict(mailto=E(P["email"]), linkedin=E(P["linkedin"]), photo=PHOTO, proof=proof, impact=impact, inote=E(S["impactNote"]), about=E(S["about"]), traits=traits, stack=stack, certs=certs,
                         exp="".join(xp(x) for x in P["experienceStory"]), projects="".join(card(p) for p in L), nd=n_done, nv=n_dev)

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
  <meta property="og:image" content="%(base)simages/03-outcomes.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="buttons.css">
  <link rel="stylesheet" href="home.css">
  <link rel="stylesheet" href="pages.css">
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
    return ('<section class="case-head s-head"><div class="crumbs"><a href="index.html#work">Projects</a> / %s</div><span class="tag">%s &middot; %s</span>'
            '<h1>%s</h1><p class="dek">%s</p><p class="bottom"><b class="bl">Bottom line: </b>%s</p></section>'
            '%s<section class="s-exec"><h2>Executive summary</h2><div class="exec">%s</div></section>'
            '<section class="s-tldr"><h2>Key findings</h2><ol>%s</ol></section>'
            '<section class="s-block"><h2>Data coverage</h2><div class="coverage">%s</div></section>'
            '<section class="s-block"><h2>Limits of this analysis</h2><ul>%s</ul></section>') % (
        E(p["sector"]), E(p["sector"]), E(p["area"]), E(p["title"]), E(s["dek"]), E(s["bottom"]), actions(p), rows,
        "".join("<li>%s</li>" % E(f) for f in s.get("findings", p["found"])), cov, "".join("<li>%s</li>" % E(l) for l in p["limits"]))


def case_page(p):
    desc = (p["problem"] + ". " + HOME[p["id"]] + ".")[:300]
    title = p["problem"] + " | Mihir Jasani"
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
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="buttons.css">
  <link rel="stylesheet" href="theme.css">
  <link rel="stylesheet" href="pages.css">
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
""" % dict(title=E(title), desc=E(desc), url=url, img=img, skip=SKIP, header=header("index.html"), footer=footer(), main=case_main(p), id=p["id"])


for p in L:
    open(href(p), "w", encoding="utf-8").write(case_page(p))

# legacy case.html?id=... redirects to the project page
open("case.html", "w", encoding="utf-8").write("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Case study | Mihir Jasani</title><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><link rel="canonical" href="%sindex.html#work">
<script>var m = new URLSearchParams(location.search).get("id"); var ok = %s; location.replace(ok.indexOf(m) > -1 ? m + ".html" : "index.html#work");</script></head>
<body><p>Redirecting to the <a href="index.html#work">projects</a>.</p></body></html>
""" % (BASE_URL, json.dumps([p["id"] for p in L])))

urls = [""] + [href(p) for p in L]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'] + ["  <url><loc>%s%s</loc></url>" % (BASE_URL, u) for u in urls] + ["</urlset>"]
open("sitemap.xml", "w", encoding="utf-8").write(chr(10).join(sm) + chr(10))
print("built: index + %d project pages (%d in development)" % (n_done, n_dev))
