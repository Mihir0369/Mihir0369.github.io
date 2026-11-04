"""Build index.html from projects.js (story flow: hero, about, impact, skills, experience, project work, contact).
Everything is written as plain HTML so search engines and text-only readers see it without JavaScript.
Run from the site folder after editing projects.js:  python build_home.py"""
from layout import *
import json, re


def xp(x):
    if x["role"] == "Peer Tutor":
        return ('<article class="job compact"><div class="job-top"><h3>%s <small>&middot; %s</small></h3><span class="when">%s</span></div>'
                '<p>Ran Excel, Power BI and statistics workshops and one-to-one support, explaining data modelling, regression and hypothesis testing in plain language.</p></article>') % (E(x["role"]), E(x["org"]), E(x["when"]))
    rows = "".join('<div class="xrow"><div>%s</div><div>%s</div></div>' % (E(w), E(i)) for w, i in x["items"])
    return ('<article class="job"><div class="job-top"><h3>%s <small>&middot; %s</small></h3><span class="when">%s</span></div>'
            '<div class="xhead"><span>What I did</span><span>Impact</span></div>%s</article>') % (E(x["role"]), E(x["org"]), E(x["when"]), rows)


certs = "".join(
    '<div class="cert2"><span class="code">%s</span><div><b>%s</b><span>Microsoft Certified</span></div><a class="btn small" href="%s" target="_blank" rel="noopener">Verify &#8599;</a></div>'
    % (E(c["label"].split(" ")[0]), E(c["label"].split(" ", 1)[1]), E(c["url"])) for c in P["certs"])
NOTES = ["Used in all four case studies and at work", "SQL checks and Python loaders behind every project", "DP-600 certified; case study 4 is in development"]
stack = "".join('<div class="scard"><h3>%s</h3><div class="tags2">%s</div><p class="note">%s</p></div>' % (E(t), tags(xs), E(NOTES[i])) for i, (t, xs) in enumerate(P["stack"]))
traits = "".join('<div class="trait"><b>%s</b><span>%s</span></div>' % (E(a), E(b)) for a, b in S["traits"])
impact = "".join('<div class="cell"><strong>%s</strong><span>%s</span><em>%s</em></div>' % (E(a), E(b), E(c)) for a, b, c in S["impact"])
n_done, n_dev = len(L), len(ALL) - len(L)
proof = "".join('<a class="pill cert" href="%s" target="_blank" rel="noopener">&#10003; Microsoft %s <small>verify</small></a>' % (E(c["url"]), E(c["label"].split(" ")[0])) for c in P["certs"])
proof += '<span class="pill">%d end-to-end case studies on real public data</span><span class="pill">Every project downloadable on GitHub</span>' % n_done

main = """
    <section class="hero2" id="home">
      <div class="wrap2 hero-c">
        <div class="portrait"><span class="mono-big">MJ</span><img src="images/mihir.jpg" alt="Mihir Jasani, data analyst" onerror="this.remove()"></div>
        <div class="hello">Hello, I'm <strong>Mihir Jasani</strong></div>
        <div class="role"><b>Data Analyst</b> &middot; Power BI &middot; SQL &middot; Microsoft Fabric</div>
        <div class="avail"><i></i>Toronto, Canada &middot; Open to Data, BI and Reporting Analyst roles</div>
        <h1>From messy data to <em>clear business decisions.</em></h1>
        <p class="lead">I build reliable Power BI reporting and SQL-powered analysis. I clean and reconcile the data, then turn it into dashboards that teams can understand, trust and act on.</p>
        <div class="acts">
          <a class="btn impact" href="#work">Explore my Project work &#8599;</a>
          <a class="btn" id="resume" href="downloads/Mihir-Jasani-Resume.pdf" download>Download Resume (PDF)</a>
          <a class="btn" id="linkedin" href="#" target="_blank" rel="noopener noreferrer">LinkedIn &#8599;</a>
        </div>
        <div class="proof">%(proof)s</div>
      </div>
    </section>

    <section class="sec alt" id="about">
      <div class="wrap2 about2">
        <div>
          <div class="eyebrow2">01 / About me</div>
          <h2>I turn messy data into decisions people can trust.</h2>
          <p>%(about)s</p>
          
        </div>
        <div class="traits">%(traits)s</div>
      </div>
    </section>

    <section class="impact2" id="impact">
      <div class="wrap2 in">
        <div class="intro">02 / Results I have delivered.<span>From my analyst roles. The case studies below use public data only.</span></div>
        %(impact)s
      </div>
    </section>

    <section class="sec" id="skills">
      <div class="wrap2">
        <div class="sec-head"><div><div class="eyebrow2">03 / Tech stack and certifications</div><h2>The tools behind the work.</h2></div>
          <p>Verified Microsoft credentials, and the stack I use day to day.</p></div>
        <div class="stack">%(stack)s</div>
        <div class="certs">%(certs)s</div>
        <div class="edu2"><div><b>Graduate Certificate, Business Insights and Analytics</b><span>Humber Polytechnic, Toronto</span></div><div><b>B.Tech, Information Technology</b><span>P.P. Savani University</span></div></div>
      </div>
    </section>

    <section class="sec alt" id="experience">
      <div class="wrap2">
        <div class="sec-head"><div><div class="eyebrow2">04 / Experience</div><h2>What I did, and what it changed.</h2></div>
          <p>Each duty is paired with the impact it had for the project or company.</p></div>
        %(exp)s
      </div>
    </section>

    <section class="sec" id="work">
      <div class="wrap2">
        <div class="sec-head"><div><div class="eyebrow2">05 / Project work</div><h2>Real data. Real questions.<br>Clear, defensible findings.</h2></div>
          <p>Each case study starts with the problem it solves. Click a small tab to preview every report page.</p></div>
        %(projects)s
        <div class="mini-foot"><span>Showing %(nd)d finished case studies &middot; %(nv)d in development</span><a class="btn small" target="_blank" rel="noopener" href="https://github.com/Mihir0369/portfolio_website">View GitHub repository &#8599;</a></div>
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
          <a class="btn impact" id="email" href="#">Email me &#8599;</a>
          <a class="btn" href="downloads/Mihir-Jasani-Resume.pdf" download>Resume (PDF)</a>
          <a class="btn" id="linkedin2" href="#" target="_blank" rel="noopener noreferrer">LinkedIn &#8599;</a>
        </div>
      </div>
    </section>""" % dict(proof=proof, about=E(S["about"]), traits=traits, impact=impact, stack=stack, certs=certs,
                         exp="".join(xp(x) for x in P["experienceStory"]), projects="".join(project(p) for p in L), nd=n_done, nv=n_dev)

ld = {"@context": "https://schema.org", "@type": "Person", "name": P["name"], "jobTitle": "Data Analyst", "address": {"@type": "PostalAddress", "addressLocality": "Toronto", "addressRegion": "ON", "addressCountry": "CA"},
      "sameAs": [P["linkedin"]], "knowsAbout": ["Power BI", "DAX", "SQL", "Python", "Microsoft Fabric", "Data analysis"]}
itemlist = {"@context": "https://schema.org", "@type": "ItemList", "name": "Case studies", "itemListElement": [
    {"@type": "ListItem", "position": i + 1, "name": p["problem"], "description": p["summary"], "url": BASE + href(p)} for i, p in enumerate(L)]}
jsonld = "".join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in (ld, itemlist))

page = """<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mihir Jasani | Data Analyst (Power BI, SQL, Fabric) | Toronto</title>
  <meta name="description" content="Mihir Jasani, Toronto-based data analyst (Power BI PL-300, Microsoft Fabric DP-600). Four completed case studies on Canadian public data: Toronto 311, collision risk, household credit and opioid harms.">
  <link rel="canonical" href="%(base)s">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Mihir Jasani | Data Analyst &amp; Business Intelligence">
  <meta property="og:description" content="Four completed Power BI case studies on Canadian public data: city services, collision risk, household credit and opioid harms.">
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
  %(header)s

  <main>%(main)s
  </main>

  %(footer)s

  <script src="projects.js"></script>
  <script src="app.js"></script>
</body>
</html>
""" % dict(base=BASE, jsonld=jsonld, main=main, header=header(), footer=footer())
open("index.html", "w", encoding="utf-8").write(page)
print("built:", n_done, "finished,", n_dev, "in development")

# case page: same header and footer
c = open("case.html", encoding="utf-8").read()
c = re.sub(r'<header class="site">.*?</header>', lambda m: header("index.html"), c, flags=re.S)
c = re.sub(r'<footer.*?</footer>', lambda m: footer(), c, flags=re.S)
open("case.html", "w", encoding="utf-8").write(c)
urls = [""] + [href(p) for p in L]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'] + ["  <url><loc>%s%s</loc></url>" % (BASE, u) for u in urls] + ["</urlset>"]
open("sitemap.xml", "w", encoding="utf-8").write(chr(10).join(sm) + chr(10))
