"""Generate the Power BI report (PBIR) for the Toronto 311 case study.

Only the report is generated here; the semantic model (TMDL) in ./powerbi is edited directly and left as it is.
Run from the repository root:  python 03-government-311/build_report.py
Re-running overwrites the report pages, the background images and the Reset filters bookmark.
"""
import json
import os
import shutil

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "powerbi")
NAME = "toronto-311"
REPORT_DIR = os.path.join(OUT, NAME + ".Report")
DEF = os.path.join(REPORT_DIR, "definition")
RES = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources")
THEME_NAME = "Toronto311Portfolio.json"

for d in (os.path.join(DEF, "pages"), os.path.join(DEF, "bookmarks"), RES):
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def wjson(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


NAVY, INK, INK2, PAPER = "#1B3A5C", "#1F2D3D", "#4A5B6C", "#F6F4EF"
TEAL, AMBER, GREY, LIGHT = "#2A7F8E", "#C77700", "#8A9BAE", "#C9D3DC"
TINT, WARN_TINT, LINE = "#E4ECF3", "#FBF1D9", "#D9E2E8"

def lit(v): return {"expr": {"Literal": {"Value": v}}}
def s(v): return lit("'" + v.replace("'", "''") + "'")
def num(v): return lit(f"{float(v)}D")
def boolean(v): return lit("true" if v else "false")
def col(t, c): return {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": c}}
def mea(c): return {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": c}}


def proj(f, t, c, name=None):
    d = {"field": f, "queryRef": f"{t}.{c}", "nativeQueryRef": c}
    if name: d["displayName"] = name
    return d


def C(t, c, name=None): return proj(col(t, c), t, c, name)
def M(c, name=None): return proj(mea(c), "_Measures", c, name)


SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json"


def clear_box():
    return {"background": [{"properties": {"show": boolean(False)}}], "border": [{"properties": {"show": boolean(False)}}],
            "dropShadow": [{"properties": {"show": boolean(False)}}]}


def container(name, x, y, w, h, vis, z, title=None, sub=None, alt=None, extra=None):
    vco = clear_box()
    if title:
        vco["title"] = [{"properties": {"show": boolean(True), "text": s(title)}}]
    if sub:
        txt = mea(sub[1:]) if sub.startswith("=") else None
        vco["subTitle"] = [{"properties": {"show": boolean(True), "text": {"expr": txt} if txt else s(sub)}}]
    if alt:
        vco["general"] = [{"properties": {"altText": s(alt)}}]
    extra = dict(extra or {})
    fc = extra.pop("filterConfig", None)
    vco.update(extra)
    vis["visualContainerObjects"] = vco
    out = {"$schema": SCHEMA, "name": name, "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z}, "visual": vis}
    if fc: out["filterConfig"] = fc
    return out


def pad(d, t, r, b, l):
    d["visual"]["visualContainerObjects"]["padding"] = [{"properties": {"top": num(t), "right": num(r), "bottom": num(b), "left": num(l)}}]
    return d


def run(t, size, color, bold=False):
    st = {"fontSize": f"{size}pt", "color": color}
    if bold: st["fontWeight"] = "bold"
    return {"value": t, "textStyle": st}


def textbox(name, x, y, w, h, paras, z, p=(8, 14, 8, 14), alt=None):
    vis = {"visualType": "textbox", "drillFilterOtherVisuals": True,
           "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": r} for r in paras]}}]}}
    return pad(container(name, x, y, w, h, vis, z, alt=alt), *p)


def card(name, x, y, w, h, m, label, z, sub=None, font=None, p=(10, 8, 8, 12)):
    vis = {"visualType": "card", "drillFilterOtherVisuals": True, "query": {"queryState": {"Values": {"projections": [M(m)]}}}}
    vis["objects"] = {"labels": [{"properties": {"labelDisplayUnits": num(1)}}]}
    if font:
        vis["objects"] = {"labels": [{"properties": {"fontSize": num(font[0]), "color": {"solid": {"color": s(font[1])}}, "labelDisplayUnits": num(1)}}]}
    d = container(name, x, y, w, h, vis, z, title=label, sub=sub, alt=f"Card: {label or m}")
    if not label: d["visual"]["visualContainerObjects"]["title"] = [{"properties": {"show": boolean(False)}}]
    return pad(d, *p)


def slicer(name, x, y, w, h, t, c, label, z, sync=None, mode="Dropdown"):
    vis = {"visualType": "slicer", "drillFilterOtherVisuals": True, "query": {"queryState": {"Values": {"projections": [C(t, c)]}}},
           "objects": {"data": [{"properties": {"mode": s(mode)}}], "header": [{"properties": {"show": boolean(True), "text": s(label)}}]}}
    if sync: vis["syncGroup"] = {"groupName": sync, "fieldChanges": True, "filterChanges": True}
    d = container(name, x, y, w, h, vis, z, alt=f"{label} slicer")
    d["visual"]["visualContainerObjects"]["title"] = [{"properties": {"show": boolean(False)}}]
    return pad(d, 4, 10, 4, 10)


def chart(name, x, y, w, h, vt, roles, z, title, sub, alt, sort=None, labels=False, objects=None, extra=None):
    q = {"queryState": {r: {"projections": pr} for r, pr in roles.items()}}
    if sort:
        q["sortDefinition"] = {"sort": [{"field": sort[0], "direction": sort[1]}], "isDefaultSort": False}
    vis = {"visualType": vt, "drillFilterOtherVisuals": True, "query": q}
    obj = dict(objects or {})
    if labels: obj["labels"] = [{"properties": {"show": boolean(True), "labelDisplayUnits": num(1)}}]
    if obj: vis["objects"] = obj
    return container(name, x, y, w, h, vis, z, title=title, sub=sub, alt=alt, extra=extra)


D0 = {"id": "default"}
def solid(c): return {"solid": {"color": s(c)}}


def button(name, x, y, w, h, label, z, link, fill_c, text_c, outline_c=None, alt=None):
    link = dict(link); link["tooltip"] = s(label)
    ol = [{"properties": {"show": boolean(bool(outline_c))}}] + (
        [{"properties": {"lineColor": solid(outline_c), "weight": num(1)}, "selector": D0}] if outline_c else [])
    objects = {"icon": [{"properties": {"shapeType": s("blank")}, "selector": D0}],
               "text": [{"properties": {"show": boolean(True)}}, {"properties": {"text": s(label), "fontColor": solid(text_c), "fontSize": num(10), "bold": boolean(True)}, "selector": D0}],
               "fill": [{"properties": {"show": boolean(True)}}, {"properties": {"fillColor": solid(fill_c), "transparency": num(0)}, "selector": D0}],
               "outline": ol}
    vco = clear_box(); vco["visualLink"] = [{"properties": link}]; vco["general"] = [{"properties": {"altText": s(alt or label)}}]
    return {"$schema": SCHEMA, "name": name, "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z},
            "visual": {"visualType": "actionButton", "drillFilterOtherVisuals": True, "objects": objects, "visualContainerObjects": vco}}




def reset_button(x, y, w, h, z):
    return button("reset", x, y, w, h, "Reset filters", z, {"show": boolean(True), "type": s("Bookmark"), "bookmark": s("reset_filters")}, NAVY, "#FFFFFF", None, "Reset all filters")


def fill(color, selector=None):
    d = {"properties": {"fill": {"solid": {"color": s(color)}}}}
    if selector: d["selector"] = selector
    return d


def by_value(table, column, value_literal):
    return {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": col(table, column), "Right": {"Literal": {"Value": value_literal}}}}}]}




S = 4


def icon(d, x, y, kind):
    R = 13                                    # circle radius in page pixels (was 18)
    cx, cy, r = (x + R) * S, (y + R) * S, R * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TINT)
    k = S * R / 18.0; n = NAVY
    def L(pts, wd=2): d.line([(cx + px * k, cy + py * k) for px, py in pts], fill=n, width=max(2, int(wd * k)), joint="curve")
    if kind == "bars":
        for i, hh in enumerate((8, 13, 18)): d.rectangle([cx + (-9 + i * 7) * k, cy + (9 - hh) * k, cx + (-5 + i * 7) * k, cy + 9 * k], fill=n)
    elif kind == "check": L([(-9, 0), (-3, 7), (9, -7)], 3)
    elif kind == "clock":
        d.ellipse([cx - 10 * k, cy - 10 * k, cx + 10 * k, cy + 10 * k], outline=n, width=max(2, int(2 * k))); L([(0, -6), (0, 0), (5, 3)])
    elif kind == "warn":
        d.polygon([(cx, cy - 10 * k), (cx + 11 * k, cy + 9 * k), (cx - 11 * k, cy + 9 * k)], outline=n, width=max(2, int(2 * k)))
        L([(0, -3), (0, 3)]); d.ellipse([cx - k, cy + 5 * k, cx + k, cy + 7 * k], fill=n)


def bg(name, H, boxes):
    im = Image.new("RGB", (1280 * S, H * S), PAPER)
    d = ImageDraw.Draw(im)
    def rect(x, y, w, h, c): d.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], fill=c)
    rect(0, 0, 1280, 104, NAVY); rect(0, 104, 1280, 3, "#F2C078")
    for kind, x, y, w, h in boxes:
        if kind == "card": rect(x, y, w, h, "#FFFFFF"); rect(x, y, w, 4, NAVY)
        elif kind == "icon": icon(d, x, y, w)
        elif kind == "panel": rect(x, y, w, h, "#FFFFFF")
        elif kind == "tint": rect(x, y, w, h, TINT)
        elif kind == "warn": rect(x, y, w, h, WARN_TINT); rect(x, y, 5, h, AMBER)
    rect(20, H - 40, 1240, 1, LINE)
    im.resize((1280 * 2, H * 2), Image.LANCZOS).save(os.path.join(RES, name), optimize=True)




def header(title, sub):
    return [textbox("hdr", 0, 0, 1280, 104, [
        [run("PORTFOLIO PROJECT  ·  REAL DATA: CITY OF TORONTO OPEN DATA, 2023 TO 2025", 8, "#F2C078", True)],
        [run(title, 22, "#FFFFFF", True)], [run(sub, 10, "#E4ECF3")]], 0, p=(18, 24, 8, 24))]   # no page buttons: readers use the page tabs


FOOT = "Data: City of Toronto Open Data, 311 Service Requests (Open Government Licence - Toronto). No close date in the data. Not an official City report."


def footer(H):
    y = H - 34
    return [textbox("foot", 20, y, 800, 26, [[run(FOOT, 8, INK2)]], 9000, p=(2, 0, 2, 0)),
            card("through", 820, y, 440, 26, "Data Through", None, 9001, font=(8, INK2), p=(2, 0, 2, 0))]


CARD_X = [20, 335, 650, 965]; CARD_W = 295; ICONS = ["bars", "check", "clock", "warn"]
ST_H, OV_H, OC_H, TY_H, DT_H, QU_H = 800, 940, 1270, 1130, 1130, 745


def krow(y, h=110): return [("card", x, y, CARD_W, h) for x in CARD_X] + [("icon", x + CARD_W - 12 - 26, y + 10, ic, 0) for x, ic in zip(CARD_X, ICONS)]


def cards4(y, items, z0=300):
    """Four number cards with icons: (label, measure, subtitle measure, text card?)."""
    return [card("k%d" % i, CARD_X[i], y, CARD_W, 110, mm, lab, z0 + i, sub=("=" + sm) if sm else None, font=(14 if txt is True else txt, NAVY) if txt else None, p=(10, 18, 6, 18))
            for i, (lab, mm, sm, txt) in enumerate(items)]


def fbox(n, x, y, head, big, txt, z):
    """One of the three finding boxes used on every analysis page: heading, key number, one or two sentences."""
    return textbox("f%d" % n, x, y, 400, 150, [[run(head, 12, NAVY, True)], [run(big, 22, "#C77700", True)], [run(txt, 10.5, INK2)]], z, p=(10, 16, 6, 16))


def findings(y, items):
    return [fbox(i + 1, 20 + 420 * i, y, h, b, t, 820 + i) for i, (h, b, t) in enumerate(items)]


def footnote(y, text, z=800):
    return textbox("note", 20, y, 1240, 50, [[run("Footnote: ", 9, INK, True), run(text, 9, INK2)]], z, p=(8, 16, 4, 18))


def block(name, x, y, w, h, head, bullets, z):
    return textbox(name, x, y, w, h, [[run(head, 12, INK, True)]] + [[run("•  " + b, 9.5, INK2)] for b in bullets], z, p=(16, 18, 10, 18))


def fpanels(y): return [("panel", x, y, 400, 150) for x in (20, 440, 860)]


YEAR_FILTER = {"filter": {"Version": 2, "From": [{"Name": "d", "Entity": "Date", "Type": 0}], "Where": [{"Condition": {"In": {"Expressions": [
    {"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": "Year"}}], "Values": [[{"Literal": {"Value": "2025L"}}]]}}}]}}


def year_slicer(x, w, label="Year (default 2025)"):
    d = slicer("yr", x, 120, w, 64, "Date", "Year", label, 100, sync="Year")
    d["visual"]["objects"]["general"] = [{"properties": {"filter": YEAR_FILTER}}]
    d["visual"]["query"]["queryState"]["Values"]["projections"][0]["active"] = True
    return d


def topn(entity, prop, measure, n):
    return {"filterConfig": {"filters": [{"name": "topn", "field": {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}, "type": "TopN",
            "filter": {"Version": 2, "From": [{"Name": "subquery", "Expression": {"Subquery": {"Query": {"Version": 2, "From": [{"Name": "d", "Entity": entity, "Type": 0}, {"Name": "_", "Entity": "_Measures", "Type": 0}],
                       "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": prop}, "Name": "field"}],
                       "OrderBy": [{"Direction": 2, "Expression": {"Measure": {"Expression": {"SourceRef": {"Source": "_"}}, "Property": measure}}}], "Top": n}}}, "Type": 2},
                       {"Name": "d", "Entity": entity, "Type": 0}],
                       "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": prop}}], "Table": {"SourceRef": {"Source": "subquery"}}}}}]}}]}}


ROW1 = [("panel", 20, 120, 300, 64), ("tint", 340, 120, 780, 64)]
bg("canvas_start.png", ST_H, [("tint", 20, 120, 1100, 64)] + krow(200) + [("panel", 20, 335, 610, 170), ("panel", 650, 335, 610, 170), ("panel", 20, 525, 610, 150), ("panel", 650, 525, 610, 150), ("warn", 20, 695, 1240, 50)])
bg("canvas_overview.png", OV_H, ROW1 + krow(200) + [("panel", 20, 330, 1240, 330)] + fpanels(680) + [("warn", 20, 850, 1240, 50)])
bg("canvas_outcomes.png", OC_H, [("panel", 20, 120, 300, 64), ("tint", 340, 120, 780, 64)] + krow(200) + [("panel", 20, 330, 610, 340), ("panel", 650, 330, 610, 340), ("panel", 20, 690, 1240, 300)] + fpanels(1010) + [("warn", 20, 1180, 1240, 50)])
bg("canvas_types.png", TY_H, [("panel", 20, 120, 220, 64), ("panel", 260, 120, 250, 64), ("panel", 530, 120, 300, 64), ("tint", 850, 120, 270, 64)] + krow(200) + [("panel", 20, 330, 610, 520), ("panel", 650, 330, 610, 520)] + fpanels(870) + [("warn", 20, 1040, 1240, 50)])
bg("canvas_detail.png", DT_H, [("panel", 90, 120, 220, 64), ("tint", 330, 120, 790, 64)] + krow(200) + [("panel", 20, 330, 610, 520), ("panel", 650, 330, 610, 520)] + fpanels(870) + [("warn", 20, 1040, 1240, 50)])
bg("canvas_quality.png", QU_H, [("panel", 20, 130, 720, 230), ("panel", 20, 375, 720, 330), ("panel", 760, 130, 500, 300), ("panel", 760, 445, 500, 260)])

pages = {}
DIV_COLORS = [fill(GREY), fill(AMBER, by_value("Dim_Division", "Division", "'Parks, Forestry & Environment'"))]

# ---- Start here
st = header("Toronto 311: where do requests go unresolved?", "Start here: the question, the headline numbers, and how to use this report.")
st += [reset_button(1140, 132, 120, 40, 150),
       textbox("q", 20, 120, 1100, 64, [[run("The question:  ", 10, INK, True),
            run("Where does the city leave requests unresolved, and what is behind the growth in 311 demand?", 10, INK2)]], 100, p=(14, 18, 8, 18))]
st += cards4(200, [("Growth in requests", "Start Growth %", "Start Growth Text", False), ("Parks & forestry open", "Start Parks Open %", "Start Parks Sub", False),
                   ("Requests on renamed types", "Start Renamed %", "Start Renamed Sub", False), ("Requests, 2023 to 2025", "Start Total Requests", "Start Total Text", False)])
st += [block("finds", 20, 335, 610, 170, "What the data shows", [
           "Requests grew 14.47% in 2025, to 500,269, but type names changed that year, so growth by type is not comparable.",
           "Parks, Forestry & Environment has 49.45% of its 2025 requests recorded as open, against 1.37% to 6.60% in every other division.",
           "58.17% of 2025 requests sit under type names that are new since January 2025."], 300),
       block("recs", 650, 335, 610, 170, "What I would do", [
           "Audit the old open parks and forestry requests and publish expected waits for pruning and tree removal.",
           "Add a closed date to the open dataset so time to close can be measured.",
           "Publish a mapping table whenever request types are renamed, so year-over-year comparisons stay possible."], 310),
       block("how", 20, 525, 610, 150, "How to use this report", [
           "Use the page tabs. Overview shows demand per month; Outcomes compares divisions; Request types shows what residents ask for.",
           "On Outcomes, right-click a division bar and choose Drill through, then Division detail, to see its request types.",
           "The Year filter carries across pages (it opens on 2025). Reset filters clears every slicer."], 320),
       block("about", 650, 525, 610, 150, "About the data and model", [
           "Source: City of Toronto Open Data, 311 Service Requests, 2023 to 2025: 1,351,594 requests, summarised to 295,239 monthly rows.",
           "Star schema: one fact table of monthly counts, with Date, Division, Request type and Status dimensions.",
           "There is no close date. Open means status Open or In Progress when the data was taken."], 400),
       footnote(695, "the data has no close date, so I report request status as of the data snapshot, not how long requests took. An open status can mean a real backlog or a status that was never updated.", 500)]
st += footer(ST_H)
pages["start"] = dict(name="Start here", H=ST_H, img="canvas_start.png", visuals=st)

# ---- Overview
ov = header("Toronto 311: demand is rising, and some requests stay open", "1.35 million customer-initiated requests, 2023 to 2025, and what happened to them.")
ov += [year_slicer(20, 300), reset_button(1140, 132, 120, 40, 150), card("headline", 340, 120, 780, 64, "Headline", None, 200, font=(11, NAVY), p=(10, 18, 8, 18))]
ov += cards4(200, [("Requests", "Requests", "Requests vs PY", False), ("Resolved", "Resolved %", "Of Year Sub", False),
                   ("Recorded as open", "Open %", "Of Year Sub", False), ("Parks & forestry open", "Parks Open %", "Parks Open vs Rest", False)])
ov += [chart("line", 20, 330, 1240, 330, "lineChart", {"Category": [C("Date", "Month")], "Series": [C("Date", "Year")], "Y": [M("Requests")]}, 400,
             "Requests per month", "The selected year by month. Reset filters to compare all three years.", "Line chart of requests per month",
             objects={"legend": [{"properties": {"show": boolean(True), "position": s("Bottom")}}]})]
ov += findings(680, [("01 · Demand", "+14.47%", "Requests rose from 437,043 in 2024 to 500,269 in 2025. The busiest month was February 2025, with 53,707."),
                     ("02 · The February spike", "53,707", "February 2025 had 53,707 requests against 24,871 a year earlier, and 19,876 of them were snow types that only exist from January 2025."),
                     ("03 · Read with care", "Labels changed", "Type names changed in January 2025, so the rise cannot be split into more problems and new labels.")])
ov += [footnote(850, "requests per month cover every status. Open means status Open or In Progress at the data snapshot. The Year slicer opens on 2025, and the headline and cards follow it.", 810)]
ov += footer(OV_H)
pages["overview"] = dict(name="Overview", H=OV_H, img="canvas_overview.png", visuals=ov)

# ---- Outcomes
oc = header("Half of parks and forestry requests are recorded as open", "Share of requests by outcome, by division. Use the year filter to compare years.")
oc += [year_slicer(20, 300), reset_button(1140, 132, 120, 40, 150), card("headline", 340, 120, 780, 64, "Outcomes Headline", None, 200, font=(10, NAVY), p=(10, 18, 8, 18))]
oc += cards4(200, [("Highest open share", "Top Open %", "Top Open Div Name", False), ("Lowest open share", "Low Open %", "Low Open Div Name", False),
                   ("Largest division", "Largest Division", "Largest Division Text", 11), ("Cancelled", "Cancelled %", "Of Year Sub", False)])
oc += [chart("bar", 20, 330, 610, 340, "clusteredBarChart", {"Category": [C("Dim_Division", "Division")], "Y": [M("Open %")]}, 400,
             "Recorded as open, by division", "Parks, forestry and environment stands apart from every other division.", "Bar chart of the share of requests recorded as open by division",
             sort=(mea("Open %"), "Descending"), labels=True, objects={"dataPoint": DIV_COLORS}),
       chart("stack", 650, 330, 610, 340, "hundredPercentStackedBarChart", {"Category": [C("Dim_Division", "Division")], "Series": [C("Dim_Status", "Status")], "Y": [M("Requests")]}, 500,
             "Outcome mix by division", "Most divisions resolve nine in ten requests.", "Stacked bar chart of the outcome mix by division",
             objects={"legend": [{"properties": {"show": boolean(True), "position": s("Top")}}],
                      "dataPoint": [fill(TEAL, by_value("Dim_Status", "Status", "'Resolved'")), fill(AMBER, by_value("Dim_Status", "Status", "'Open'")),
                                    fill(GREY, by_value("Dim_Status", "Status", "'Cancelled'")), fill(LIGHT, by_value("Dim_Status", "Status", "'Unknown'"))]}),
       chart("tbl", 20, 690, 1240, 300, "tableEx", {"Values": [C("Dim_Division", "Division"), M("Requests"), M("Resolved %"), M("Cancelled %"), M("Open %")]}, 600,
             "Division scorecard", "Volume and outcome shares for the selected year. Right-click a division on the bar chart and choose Drill through.", "Table of requests and outcome shares by division")]
oc += findings(1010, [("01 · Parks and forestry", "49.45%", "Parks, Forestry & Environment has 18,597 of its 37,611 requests in 2025 recorded as open. Every other division is between 1.37% and 6.60%."),
                     ("02 · Not a new spike", "44.66%", "The same division was 44.66% open in 2023 and 51.52% in 2024, so the gap is not new."),
                     ("03 · Read with care", "Open at snapshot", "Open means status Open or In Progress when the data was taken. With no close date, it cannot tell a real backlog from a status nobody updated.")])
oc += [footnote(1180, "open means status Open or In Progress at the data snapshot. The data cannot tell a genuine backlog from a status that was never updated, because it has no close date.", 810)]
oc += footer(OC_H)
pages["outcomes"] = dict(name="Outcomes", H=OC_H, img="canvas_outcomes.png", visuals=oc)

# ---- Request types
ty = header("What people ask 311 for, and a naming change to watch", "Largest request types for the selected year, era and division.")
ty += [year_slicer(20, 220, "Year (default 2025)"), slicer("era", 260, 120, 250, 64, "Dim_ServiceType", "Taxonomy Era", "Taxonomy era", 101),
       slicer("div", 530, 120, 300, 64, "Dim_Division", "Division", "Division", 102), reset_button(1140, 132, 120, 40, 150),
       card("headline", 850, 120, 270, 64, "Types Headline Short", None, 200, font=(9, NAVY), p=(8, 12, 6, 12))]
ty += cards4(200, [("Largest request type", "Top Type", "Top Type Text", True), ("Cancelled", "Cancelled %", "Of Year Sub", False),
                   ("Most-cancelled type", "Cancel Peak %", "Cancel Types Sub", False), ("Type names in both periods", "Types In Both %", "Types In Both Short", False)])
ty += [chart("bar", 20, 330, 610, 520, "clusteredBarChart", {"Category": [C("Dim_ServiceType", "Service Type")], "Y": [M("Requests")]}, 400,
             "Top request types", "The 15 largest request types for the selection.", "Bar chart of the largest request types",
             sort=(mea("Requests"), "Descending"), labels=True, objects={"dataPoint": [fill(NAVY)]}, extra=topn("Dim_ServiceType", "Service Type", "Requests", 15)),
       chart("tbl", 650, 330, 610, 520, "tableEx", {"Values": [C("Dim_ServiceType", "Service Type"), M("Requests"), M("Cancelled %"), M("Open %")]}, 500,
             "Request types in detail", "The 15 largest types. Some are cancelled far more often than others.", "Table of request types with requests, cancelled share and open share",
             sort=(mea("Requests"), "Descending"), objects={"total": [{"properties": {"totals": boolean(False)}}]}, extra=topn("Dim_ServiceType", "Service Type", "Requests", 15))]
ty += findings(870, [("01 · The largest type", "24,448", "Residential Bin Lid Damaged is the largest request type in 2025, with 24,448 requests (4.89% of all)."),
                     ("02 · Cancellations", "57.16%", "A yard-waste type with 1,055 requests is the most cancelled. Among larger types, dead-wildlife pick-up is cancelled 38.84% of the time."),
                     ("03 · Names changed", "34.26%", "Only 284 of 829 type names (34.26%) appear in both 2023-24 and 2025, so compare type counts only within a period.")])
ty += [footnote(1040, "in January 2025, 255 request type names changed or were introduced, covering 58.17% of 2025 requests. Compare type counts only within 2023 to 2024, or within 2025.", 810)]
ty += footer(TY_H)
pages["types"] = dict(name="Request types", H=TY_H, img="canvas_types.png", visuals=ty)

# ---- Division detail (drill through from Outcomes)
dt = header("Division detail: which request types stay open", "Drill through from the Outcomes page to see one division's request types.")
dt += [button("back", 20, 128, 56, 48, "← Back", 120, {"show": boolean(True), "type": s("Back")}, NAVY, "#FFFFFF", None, "Back to the previous page"),
       year_slicer(90, 220, "Year"), reset_button(1140, 132, 120, 40, 150),
       card("seldiv", 330, 120, 790, 64, "Selected Division", None, 200, font=(12, NAVY), p=(10, 18, 8, 18))]
dt += cards4(200, [("Most open requests", "Top Open Type", "Top Open Type Text", True), ("Highest open share", "Open Type Peak %", "Open Type Peak Text", False),
                   ("Open requests", "Open", "Open Total Text", False), ("Recorded as open", "Open %", "Of Year Sub", False)])
dt += [chart("bar", 20, 330, 610, 520, "clusteredBarChart", {"Category": [C("Dim_ServiceType", "Service Type")], "Y": [M("Open")]}, 400,
             "Open requests by type", "The 15 request types with the most open requests in this division.", "Bar chart of open requests by request type",
             sort=(mea("Open"), "Descending"), labels=True, objects={"dataPoint": [fill(AMBER)]}, extra=topn("Dim_ServiceType", "Service Type", "Open", 15)),
       chart("tbl", 650, 330, 610, 520, "tableEx", {"Values": [C("Dim_ServiceType", "Service Type"), M("Requests"), M("Open"), M("Open %")]}, 500,
             "Request types in this division", "The 15 types with the most open requests.", "Table of request types in this division",
             sort=(mea("Open"), "Descending"), objects={"total": [{"properties": {"totals": boolean(False)}}]}, extra=topn("Dim_ServiceType", "Service Type", "Open", 15))]
dt += findings(870, [("01 · How to get here", "Drill through", "On the Outcomes page, right-click a division bar and choose Drill through, then Division detail."),
                     ("02 · What it shows", "Open by type", "Which request types account for the open requests in the division you picked, and how large each open share is."),
                     ("03 · Read with care", "Snapshot", "Open means status Open or In Progress when the data was taken. A type with few requests can show a high open share, so check the counts.")])
dt += [footnote(1040, "the page shows one division at a time and follows the Year filter. Open means status Open or In Progress at the data snapshot, not a confirmed backlog.", 810)]
dt += footer(DT_H)
pages["detail"] = dict(name="Division detail", H=DT_H, img="canvas_detail.png", visuals=dt, display="FitToWidth",
                       props={"type": "Drillthrough", "visibility": "HiddenInViewMode",
                              "filterConfig": {"filters": [{"name": "f_division", "field": col("Dim_Division", "Division"), "type": "Categorical"}]},
                              "pageBinding": {"name": "bind_detail", "type": "Drillthrough", "parameters": [{"name": "Param_Division", "boundFilter": "f_division", "fieldExpr": col("Dim_Division", "Division")}]}})

# ---- Data quality
dq = header("Before any analysis: what each number in the file means", "What the file contains, what changed in 2025, and what I did about it.")
dq += [chart("years", 20, 130, 720, 230, "tableEx", {"Values": [C("Date", "Year"), M("Requests"), M("Resolved %"), M("Cancelled %"), M("Open %")]}, 300,
             "What each year contains", "Requests and outcome shares by year, for every division.", "Table of requests and outcome shares by year"),
       chart("eras", 20, 375, 720, 330, "tableEx", {"Values": [C("Dim_ServiceType", "Taxonomy Era", "Type name period"), M("Era Types", "Type names"), M("Requests"), M("Era Share", "Share of requests")]}, 400,
             "Request type names by period", "Names that exist in only one period make year-over-year comparisons by type invalid.", "Table of type names and requests by naming period"),
       block("found", 760, 130, 500, 300, "What I found in the file and what I did", [
           "The extract has 1,351,594 requests. About 8% of the raw rows were broken by an unquoted comma in a text field, so I repaired them before counting.",
           "There is no close date. Open means status Open or In Progress when the data was taken, not a confirmed backlog, and time to close cannot be measured.",
           "Type names changed in January 2025: 255 names appear only in 2025 and cover 58.17% of that year's requests. Growth by type is not comparable across the boundary.",
           "Statuses are grouped into Resolved, Cancelled, Open and Unknown. The model counts 254 renamed types, not 255, because two spellings differ only by case.",
           "Checks: totals, yearly counts and open share by division match the SQL queries."], 500),
       block("terms", 760, 445, 500, 260, "Terms in plain language", [
           "311: Toronto's city line for non-emergency service requests.",
           "Open: status Open or In Progress when the data was taken.",
           "Division: the city department that handles the request.",
           "Taxonomy era: whether a request type name existed before January 2025, only after it, or in both periods.",
           "Customer-initiated: requests residents and businesses made, not work the city started itself."], 510)]
dq += footer(QU_H)
pages["quality"] = dict(name="Data quality", H=QU_H, img="canvas_quality.png", visuals=dq)


# ---------------------------------------------------------------- theme
def sol(c): return {"solid": {"color": c}}


theme = {"name": "Toronto 311 Portfolio", "dataColors": [NAVY, TEAL, AMBER, GREY, "#6B4C7A", "#B23A48", "#4F6D7A", LIGHT],
         "background": "#FFFFFF", "foreground": INK, "tableAccent": NAVY, "foregroundNeutralSecondary": INK2, "backgroundLight": TINT,
         "good": TEAL, "neutral": AMBER, "bad": "#B23A48", "maximum": NAVY, "center": "#8FA9C2", "minimum": TINT,
         "textClasses": {"callout": {"fontFace": "Segoe UI", "fontSize": 28, "color": NAVY}, "title": {"fontFace": "Segoe UI", "fontSize": 12, "color": INK},
                         "header": {"fontFace": "Segoe UI", "fontSize": 11, "color": INK}, "label": {"fontFace": "Segoe UI", "fontSize": 10, "color": INK2}},
         "visualStyles": {
             "*": {"*": {"background": [{"show": False}], "border": [{"show": False}], "dropShadow": [{"show": False}],
                         "padding": [{"top": 14, "bottom": 12, "left": 16, "right": 16}],
                         "title": [{"show": True, "fontColor": sol(INK), "fontFamily": "Segoe UI", "fontSize": 12, "alignment": "left"}],
                         "subTitle": [{"show": True, "fontColor": sol(INK2), "fontFamily": "Segoe UI", "fontSize": 9}],
                         "categoryAxis": [{"gridlineShow": False, "labelColor": sol(INK2), "fontFamily": "Segoe UI", "showAxisTitle": False}],
                         "valueAxis": [{"gridlineShow": True, "gridlineColor": sol(LINE), "gridlineStyle": "solid", "labelColor": sol(INK2), "fontFamily": "Segoe UI", "showAxisTitle": False}],
                         "legend": [{"labelColor": sol(INK2), "fontFamily": "Segoe UI", "fontSize": 9}],
                         "labels": [{"color": sol(INK), "fontFamily": "Segoe UI", "fontSize": 9}], "lineStyles": [{"strokeWidth": 3}]}},
             "page": {"*": {"background": [{"color": sol(PAPER), "transparency": 0}], "outspace": [{"color": sol(PAPER)}]}},
             "card": {"*": {"labels": [{"color": sol(NAVY), "fontSize": 26, "fontFamily": "Segoe UI"}], "categoryLabels": [{"show": False}]}},
             "tableEx": {"*": {"grid": [{"gridVertical": False, "gridHorizontal": True, "gridHorizontalColor": sol(LINE), "rowPadding": 5, "outlineColor": sol(LINE)}],
                               "columnHeaders": [{"fontColor": sol(NAVY), "backColor": sol(TINT), "fontFamily": "Segoe UI", "fontSize": 9}],
                               "values": [{"fontColorPrimary": sol(INK), "backColorPrimary": sol("#FFFFFF"), "fontColorSecondary": sol(INK), "backColorSecondary": sol("#FFFFFF"), "fontFamily": "Segoe UI", "fontSize": 9}],
                               "total": [{"fontColor": sol(INK), "backColor": sol(TINT)}]}},
             "slicer": {"*": {"items": [{"fontColor": sol(INK), "background": sol("#FFFFFF"), "fontFamily": "Segoe UI", "fontSize": 10}], "header": [{"fontColor": sol(INK2)}]}}}}
wjson(os.path.join(RES, THEME_NAME), theme)

# ---------------------------------------------------------------- report files
images = sorted({p["img"] for p in pages.values() if p["img"]})
wjson(os.path.join(DEF, "report.json"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.0.0/schema.json",
    "themeCollection": {"customTheme": {"name": THEME_NAME, "type": "RegisteredResources", "reportVersionAtImport": {"visual": "1.8.0", "report": "2.0.0", "page": "1.3.0"}}},
    "settings": {"useStylableVisualContainerHeader": True, "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True},
    "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources", "items":
        [{"name": THEME_NAME, "path": THEME_NAME, "type": "CustomTheme"}] + [{"name": n, "path": n, "type": "Image"} for n in images]}]})
wjson(os.path.join(DEF, "version.json"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
wjson(os.path.join(DEF, "pages", "pages.json"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
                                                 "pageOrder": ["start", "overview", "outcomes", "types", "detail", "quality"], "activePageName": "start"})

for pid, pg in pages.items():
    pdir = os.path.join(DEF, "pages", pid); os.makedirs(pdir, exist_ok=True)
    objs = {"outspace": [{"properties": {"color": solid(PAPER)}}]}
    img = pg["img"]
    objs["background"] = [{"properties": {"image": {"image": {"name": s(img), "url": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": img}}}, "scaling": s("Fit")}}, "transparency": num(0.0)}}]
    page = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json", "name": pid, "displayName": pg["name"],
            "displayOption": pg.get("display", "FitToWidth"), "height": pg["H"], "width": 1280, "objects": objs}
    page.update(pg.get("props", {}))
    wjson(os.path.join(pdir, "page.json"), page)
    for v in pg["visuals"]:
        vd = os.path.join(pdir, "visuals", v["name"]); os.makedirs(vd, exist_ok=True)
        wjson(os.path.join(vd, "visual.json"), v)

sections = {}
for pid, pg in pages.items():
    sl = {v["name"]: {"singleVisual": {"visualType": "slicer"}} for v in pg["visuals"] if v["visual"].get("visualType") == "slicer"}
    if sl: sections[pid] = {"visualContainers": sl}
wjson(os.path.join(DEF, "bookmarks", "reset_filters.bookmark.json"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/1.4.0/schema.json", "name": "reset_filters", "displayName": "Reset filters",
    "options": {"suppressActiveSection": True, "suppressDisplay": True}, "explorationState": {"version": "1.3", "activeSection": "overview", "sections": sections}})
wjson(os.path.join(DEF, "bookmarks", "bookmarks.json"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json", "items": [{"name": "reset_filters"}]})
print("built", {k: len(v["visuals"]) for k, v in pages.items()})
