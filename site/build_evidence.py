"""Build evidence for the case pages from the real project files:
  - verbatim SQL excerpts from each project's sql/analysis.sql
  - a star-schema diagram (SVG) drawn from each semantic model's relationships.tmdl
  - data-coverage blocks and DAX explanations
Writes evidence.js and images/model-<id>.svg.  Run from the site folder: python build_evidence.py"""
import html, json, os, re, datetime

ROOT = os.path.abspath("..")
E = lambda s: html.escape(str(s), quote=True)
GH = "https://github.com/Mihir0369/portfolio_website/blob/main/"

PROJECTS = {
    "toronto-311": {"dir": "03-government-311", "model": "toronto-311"},
    "household-credit": {"dir": "01-banking-household-credit", "model": "household-credit"},
    "collision-risk": {"dir": "02-insurance-collision-risk", "model": "collision-risk"},
    "substance-harms": {"dir": "05-healthcare-opioid-harms", "model": "opioid-harms"},
}

# (header prefix in analysis.sql, short name, why this query)
SQL = {
    "toronto-311": [
        ("-- q5_division_scorecard", "Division scorecard (2025)", "Conditional counts inside one GROUP BY give the resolved, cancelled and open share for each division in a single pass. It supports the finding that one division records about half its requests as open."),
        ("-- q14_taxonomy_change", "Request-type names that changed in 2025", "A CTE counts each request type before and in 2025, then flags types that exist only in 2025. It supports the warning that growth by request type is not comparable across January 2025."),
        ("-- q10_data_quality", "Data-quality check", "One pass counts missing created dates, divisions, wards and types, and unknown statuses, so the data-quality page can state what the file lacks."),
    ],
    "household-credit": [
        ("-- 1. Rates: yearly averages", "Rates, yearly averages", "Aggregates monthly policy, prime and 5-year mortgage rates into yearly averages, to sanity-check the rates table before it is modelled."),
        ("-- 5. Data-quality checks", "Data-quality check", "Counts months and missing prime and mortgage values, so gaps are known before any lag is tested."),
    ],
    "collision-risk": [
        ("-- 4. Night", "Night against day", "A CASE expression splits collisions into night and day, and SUM over a boolean counts fatal ones. It reproduces the 3.41% against 1.52% fatal share. The denominator is recorded collisions, not traffic volume."),
        ("-- 9. Does the safety-device gap", "Safety-device gap by age band", "Conditional aggregation by age band, limited to drivers and passengers with a known age, tests whether the no-device gap survives within every band instead of being an age effect."),
        ("-- 11. Data checks", "Integrity checks", "Compares collisions with distinct collision IDs and uses a NOT IN subquery to find people with no matching collision, the same checks the model enforces."),
    ],
    "substance-harms": [
        ("-- 3. Key check", "Uniqueness check", "A GROUP BY with HAVING COUNT(*) > 1 returns any duplicated key. It should return zero rows before the tables are modelled."),
        ("-- 4. Who reports?", "Who reports each source", "Counts the jurisdictions with a published opioid number in 2024, by source, and lists them with GROUP_CONCAT. It shows that a Canada total only adds up the places that report."),
        ("-- 5. Does Canada equal", "Canada against the sum of its parts", "Compares each source's Canada value with the sum of its listed regions, and shows where they differ because the Canada total includes extra places. This is why coverage is stated on the report."),
    ],
}

WHY = {
    "Credit $B (Latest)": "Pins a card to the latest month with CALCULATE, so it does not move with the date filter.",
    "Credit YoY %": "Year-over-year growth with SAMEPERIODLASTYEAR. Returns blank, not a misleading number, when either year is missing.",
    "Mortgage Share (Latest)": "A ratio with DIVIDE and a category filter: context changed with CALCULATE.",
    "Prime Chg 12m (Lagged)": "Shifts the date filter back by the slicer's lag with DATEADD, so any lag from 0 to 24 months can be tested.",
    "Strongest Lag": "Ranks the precomputed correlations by absolute value with TOPN and returns the lag with the strongest association.",
    "Fatal Share": "Fatal collisions divided by recorded fatal and injury collisions. The denominator is recorded collisions, not traffic volume.",
    "Night Fatal Share": "Reuses Fatal Share with a day-part filter: one definition, many slices.",
    "Heat Share": "Blanks heat-map cells with fewer than 100 collisions, so small samples do not look like patterns.",
    "Fatal Index": "Fatal collisions as a percentage of the same period last year (100 = no change), using SAMEPERIODLASTYEAR.",
    "Scn Avoided": "Illustrative scenario arithmetic: fatal collisions x (1 - safer share / current share) x assumed share of the gap closed. An assumption, not an observed outcome.",
    "Times Avg": "A group's fatality rate divided by the average person's rate.",
    "Open %": "Requests with status Open divided by all requests, the report's central measure.",
    "Requests PY": "Prior-year requests with SAMEPERIODLASTYEAR, the base for year-over-year growth.",
    "Requests YoY %": "Growth against the prior year, built on Requests PY with DIVIDE to avoid divide-by-zero.",
    "Parks Open %": "Pins Open % to one division with CALCULATE, so the card stays fixed when other filters change.",
    "Open Type Peak %": "Finds the request type with the highest open rate among types with at least 100 requests (FILTER and TOPN), so tiny types do not win.",
    "Count": "Uses ISFILTERED to show the Canada total unless a region is chosen.",
    "Rate (Focus Year)": "Rate per 100,000 for a chosen year, source and substance, ignoring the date filter with REMOVEFILTERS.",
    "Opioid Deaths Peak": "Highest yearly opioid death count among complete years, excluding the partial 2026 period.",
    "Coverage Status": "Shows whether a place reported, was suppressed or is missing, so blanks are explained, not shown as zero.",
    "Tile Fill": "Chooses the tile-map colour from the rate, grey when missing, so missing values are never drawn as low.",
}

COVERAGE = {
    "toronto-311": [
        ("Source organization", "City of Toronto Open Data: 311 Service Requests, Customer Initiated"),
        ("Covered period", "2023 to 2025 (data through December 2025)"),
        ("Grain", "One row per service request: 1,351,594 requests, 7 divisions, 829 request types"),
        ("Denominator", "Requests in the selected year. Open rate = requests with status Open or In Progress divided by all requests"),
        ("Exclusions and repairs", "Rows damaged in the source CSV were repaired during cleaning; the data-quality page lists them"),
        ("Known limitations", "No close date, so open means open at the data snapshot, not a confirmed backlog. Request-type names changed in January 2025, so growth by type is not comparable across the break"),
    ],
    "household-credit": [
        ("Source organization", "Bank of Canada (Valet API) and Statistics Canada tables 36-10-0639, 38-10-0238 and 11-10-0065"),
        ("Covered period", "January 2010 to August 2026 (202 months of rates, 66 quarters of debt service)"),
        ("Grain", "Monthly (rates, credit by category) and quarterly (debt service); weekly rates are rolled up to the last weekly value of each month"),
        ("Denominator", "Credit growth is year over year on household credit balances. Debt service is a share of household income"),
        ("Exclusions and gaps", "Auto loans start in 2016. Credit-card and personal-loan growth spikes in 2011 to 2014 look like reclassifications"),
        ("Known limitations", "Market-level data with no customer records. Sources differ in frequency and release schedule, and the lag result is observational"),
    ],
    "collision-risk": [
        ("Source organization", "Transport Canada, National Collision Database (accessed November 2026)"),
        ("Covered period", "Calendar years 2019 and 2020"),
        ("Grain", "Person-level rows grouped into collisions: 185,772 collisions, 330,576 vehicles and 463,630 people"),
        ("Denominator", "Recorded fatal and injury collisions. There are no traffic volumes or kilometres driven, so shares are not per-trip risk"),
        ("Exclusions", "7,416 dummy rows removed. Property-damage-only collisions are not in the file, and there are no insurance claims"),
        ("Known limitations", "2020 was a pandemic year. Safety-device use is unknown for 21.99% of records, and unknown means left blank by police or not supplied by that jurisdiction"),
    ],
    "substance-harms": [
        ("Source organization", "Public Health Agency of Canada, Opioid- and Stimulant-related Harms in Canada, Health Infobase (accessed November 2026)"),
        ("Covered period", "2016 to Q1 2026, yearly and quarterly. 2026 is a partial year"),
        ("Grain", "Aggregated counts and rates by province or territory, year and quarter, for four sources: deaths, hospital stays, emergency department visits and EMS responses"),
        ("Denominator", "Counts, with crude rates per 100,000 that are not age-adjusted"),
        ("Exclusions and coverage", "Small counts are suppressed. Hospital stays leave out Quebec, emergency department visits cover 7 of 13 provinces and territories, and a Canada total only adds up the places that report"),
        ("Known limitations", "Provinces report differently, and some 2025 provincial values look provisional, so provinces are compared on 2024"),
    ],
}


def sql_block(path, header):
    lines = open(path, encoding="utf-8").read().split("\n")
    i = next(k for k, l in enumerate(lines) if l.startswith(header))
    out = []
    for l in lines[i:]:
        if not l.strip() and out:
            break
        out.append(l)
    return "\n".join(out)


def model_svg(mdir):
    base = os.path.join(ROOT, mdir, "powerbi")
    sm = next(d for d in os.listdir(base) if d.endswith(".SemanticModel"))
    txt = open(os.path.join(base, sm, "definition", "relationships.tmdl"), encoding="utf-8").read()
    rels = re.findall(r"fromColumn:\s*(.+?)\.(?:'[^']*'|[^\s.]+)\s*\n\s*toColumn:\s*(.+?)\.", txt)
    rels = [(a.strip("'"), b.strip("'")) for a, b in rels]
    frm = {a for a, b in rels}
    to = {b for a, b in rels}
    facts = sorted(f for f in frm if f not in to)
    dims = sorted(t for t in to if t not in facts)
    # "Date" is the shared dimension: put it first
    dims.sort(key=lambda t: (t != "Date", t))
    per = 6 if len(dims) > 8 else max(len(dims), 1)
    rows = [dims[i:i + per] for i in range(0, len(dims), per)]
    W = max(900, max(len(r) for r in rows) * 150 + 60)
    top = rows[:max(1, (len(rows) + 1) // 2)]
    bot = rows[len(top):]
    BW, BH = 136, 34
    pos = {}
    y = 40
    for r in top:
        x0 = (W - len(r) * (BW + 14)) / 2
        for k, t in enumerate(r):
            pos[t] = (x0 + k * (BW + 14), y)
        y += BH + 26
    fy = y + 30
    x0 = (W - len(facts) * (BW + 80)) / 2
    for k, t in enumerate(facts):
        pos[t] = (x0 + k * (BW + 80), fy)
    y = fy + BH + 60
    for r in bot:
        x0 = (W - len(r) * (BW + 14)) / 2
        for k, t in enumerate(r):
            pos[t] = (x0 + k * (BW + 14), y)
        y += BH + 26
    H = y + 20
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-label="Star-schema diagram drawn from the model relationships">' % (W, H),
         '<rect width="100%" height="100%" fill="#fff"/>']
    for a, b in rels:
        if a in pos and b in pos:
            ax, ay = pos[a][0] + BW / 2, pos[a][1] + BH / 2
            bx, by = pos[b][0] + BW / 2, pos[b][1] + BH / 2
            s.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#B6C0C6" stroke-width="1.2"/>' % (ax, ay, bx, by))
    for t, (x, y) in pos.items():
        fact = t in facts
        s.append('<rect x="%.0f" y="%.0f" width="%d" height="%d" rx="6" fill="%s" stroke="%s"/>' % (x, y, BW, BH, "#142C43" if fact else "#EDF1EF", "#142C43" if fact else "#C9D3D0"))
        label = t if len(t) <= 20 else t[:19] + "…"
        s.append('<text x="%.0f" y="%.0f" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="700" fill="%s">%s</text>' % (x + BW / 2, y + 21, "#E8A342" if fact else "#18344C", E(label)))
    s.append('<text x="12" y="%d" font-family="Segoe UI,Arial,sans-serif" font-size="11" fill="#65727B">Fact tables (dark) and dimensions (light), drawn from relationships.tmdl: %d relationships.</text>' % (H - 6, len(rels)))
    s.append("</svg>")
    return "\n".join(s), len(rels), facts


ev = {"sql": {}, "why": WHY, "coverage": {}, "model": {}}
for pid, cfg in PROJECTS.items():
    path = os.path.join(ROOT, cfg["dir"], "sql", "analysis.sql")
    ev["sql"][pid] = {"file": GH + cfg["dir"] + "/sql/analysis.sql",
                      "items": [{"name": n, "why": w, "sql": sql_block(path, h)} for h, n, w in SQL[pid]]}
    ev["coverage"][pid] = COVERAGE[pid]
    svg, nrel, facts = model_svg(cfg["dir"])
    open("images/model-%s.svg" % pid, "w", encoding="utf-8").write(svg)
    ev["model"][pid] = {"img": "images/model-%s.svg" % pid, "rels": nrel, "facts": facts,
                        "src": GH + cfg["dir"] + "/powerbi/"}
# last_updated.txt is edited by hand when the content changes, so the generated files stay stable between builds
ev["built"] = open("last_updated.txt", encoding="utf-8").read().strip() if os.path.exists("last_updated.txt") else datetime.date.today().strftime("%B %Y")
open("evidence.js", "w", encoding="utf-8").write("// Generated by build_evidence.py from the real project files. Do not edit by hand.\nwindow.EVIDENCE = " + json.dumps(ev, indent=1, ensure_ascii=False) + ";\n")
print("evidence built:", {k: len(v["items"]) for k, v in ev["sql"].items()}, {k: v["rels"] for k, v in ev["model"].items()})
