"""Generate the Power BI project (PBIP: TMDL model + PBIR report) for the household-credit case study.

Run after build_model_data.py (it reads the CSVs in ./model). Output goes to ./powerbi.
Re-running overwrites the model and report files in ./powerbi, so edit this script, not the output,
unless you have finished laying the report out by hand in Power BI Desktop.
"""
import json
import os
import shutil
import uuid

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "powerbi")
NAME = "household-credit"
MODEL_DIR = os.path.join(OUT, NAME + ".SemanticModel")
REPORT_DIR = os.path.join(OUT, NAME + ".Report")
DEF = os.path.join(REPORT_DIR, "definition")
RES = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources")
TMDL = os.path.join(MODEL_DIR, "definition")
MODEL_FOLDER = os.path.join(HERE, "model")          # the CSVs the model reads (parameter ModelFolder)
THEME_NAME = "HouseholdCreditPortfolio.json"

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
for d in (os.path.join(TMDL, "tables"), os.path.join(TMDL, "cultures"), RES, os.path.join(DEF, "pages"), os.path.join(DEF, "bookmarks")):
    os.makedirs(d, exist_ok=True)


def tag(name):  # stable lineage tags
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "household-credit/" + name))


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def wjson(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


# =====================================================================================
# SEMANTIC MODEL
# =====================================================================================
write(os.path.join(MODEL_DIR, "definition.pbism"), json.dumps(
    {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
     "version": "4.2", "settings": {}}, indent=2))
wjson(os.path.join(MODEL_DIR, ".platform"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "SemanticModel", "displayName": NAME}, "config": {"version": "2.0", "logicalId": tag("model")}})
write(os.path.join(TMDL, "database.tmdl"), "database\n\tcompatibilityLevel: 1606\n")
write(os.path.join(TMDL, "model.tmdl"), """model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-CA
\tdiscourageImplicitMeasures
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation PBI_QueryOrder = ["fact_credit","fact_rates","fact_debt","lag_correlation","ModelFolder"]

annotation __PBI_TimeIntelligenceEnabled = 1

annotation PBI_ProTooling = ["DevMode"]

ref table fact_credit
ref table fact_rates
ref table fact_debt
ref table lag_correlation
ref table Date
ref table _Measures
ref table Dim_Category
ref table Dim_DebtMeasure
ref table LagSteps

ref cultureInfo en-US
""")
write(os.path.join(TMDL, "cultures", "en-US.tmdl"), "cultureInfo en-US\n")
write(os.path.join(TMDL, "expressions.tmdl"),
      'expression ModelFolder = "%s" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]\n'
      "\tlineageTag: %s\n\n\tannotation PBI_ResultType = Text\n" % (MODEL_FOLDER.replace("/", "\\"), tag("param")))
write(os.path.join(TMDL, "relationships.tmdl"), """relationship credit_to_date
\tfromColumn: fact_credit.MonthStart
\ttoColumn: Date.Date

relationship credit_to_category
\tfromColumn: fact_credit.category
\ttoColumn: Dim_Category.Category

relationship rates_to_date
\tfromColumn: fact_rates.MonthStart
\ttoColumn: Date.Date

relationship debt_to_date
\tfromColumn: fact_debt.quarter_start
\ttoColumn: Date.Date

relationship debt_to_measure
\tfromColumn: fact_debt.debt_measure
\ttoColumn: Dim_DebtMeasure.'Debt measure'
""")


def col(name, dtype, fmt=None, hidden=True, extra=""):
    lines = ["\tcolumn %s" % (name if name.replace("_", "").isalnum() else "'%s'" % name),
             "\t\tdataType: %s" % dtype]
    if hidden:
        lines.append("\t\tisHidden")
    if fmt:
        lines.append("\t\tformatString: %s" % fmt)
    lines += ["\t\tlineageTag: %s" % tag("col/" + name + extra), "\t\tsummarizeBy: none", "\t\tsourceColumn: %s" % name, ""]
    return "\n".join(lines)


def csv_table(tname, fname, columns, add_date=None):
    """columns: [(name, dtype, mtype)]  add_date: (source month column, new name)"""
    cols = "\n".join(col(n, dt, "General Number" if dt in ("double", "int64") else None) for n, dt, _ in columns)
    types = ", ".join('{"%s", %s}' % (n, mt) for n, _, mt in columns)
    m = ['let',
         '    Source = Csv.Document(File.Contents(ModelFolder & "\\%s"), [Delimiter = ",", Columns = %d, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),' % (fname, len(columns)),
         '    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),',
         '    Typed = Table.TransformColumnTypes(Promoted, {%s}, "en-US")%s' % (types, "," if add_date else "")]
    extra_col = ""
    if add_date:
        src, new = add_date
        m.append('    AddDate = Table.AddColumn(Typed, "%s", each Date.FromText([%s] & "%s"), type date)' % (new, src, "-01" if src == "month" else ""))
        extra_col = "\n" + col(new, "dateTime", "Long Date", True) + "\n\t\tannotation UnderlyingDateTimeDataType = Date\n"
    m += ["in", "    " + ("AddDate" if add_date else "Typed")]
    body = "\n".join("\t\t\t\t" + x for x in m)
    write(os.path.join(TMDL, "tables", tname + ".tmdl"),
          "table %s\n\tlineageTag: %s\n\n%s%s\n\tpartition %s = m\n\t\tmode: import\n\t\tsource =\n%s\n\n\tannotation PBI_ResultType = Table\n"
          % (tname, tag("table/" + tname), cols, extra_col, tname, body))


T, N, I = "type text", "type number", "Int64.Type"
csv_table("fact_credit", "fact_credit_monthly.csv",
          [("month", "string", T), ("category", "string", T), ("balance_millions", "double", N), ("yoy_pct", "double", N)],
          add_date=("month", "MonthStart"))
csv_table("fact_rates", "fact_rates_monthly.csv",
          [("month", "string", T), ("overnight", "double", N), ("prime", "double", N), ("mortgage_1y", "double", N),
           ("mortgage_3y", "double", N), ("mortgage_5y", "double", N), ("overnight_chg_12m", "double", N),
           ("prime_chg_12m", "double", N), ("mortgage_5y_chg_12m", "double", N)], add_date=("month", "MonthStart"))
csv_table("fact_debt", "fact_debt_service.csv",
          [("quarter_start", "dateTime", "type date"), ("debt_measure", "string", T), ("ratio_pct", "double", N)])
csv_table("lag_correlation", "lag_correlation.csv",
          [("lag_months", "int64", I), ("correlation", "double", N), ("n", "int64", I)])


def calc_table(tname, columns, source, extra_props=""):
    cols = "\n".join(c for c in columns)
    write(os.path.join(TMDL, "tables", tname + ".tmdl"),
          "table %s\n\tlineageTag: %s\n%s\n%s\n\tpartition %s = calculated\n\t\tmode: import\n\t\tsource =\n%s\n"
          % (tname, tag("table/" + tname), extra_props, cols, tname, "\n".join("\t\t\t\t" + x for x in source.split("\n"))))


def ccol(name, dtype=None, fmt=None, hidden=False, sort=None, key=False):
    q = name if name.replace("_", "").isalnum() else "'%s'" % name
    lines = ["\tcolumn %s" % q]
    if key: lines.append("\t\tisKey")
    if dtype: lines.append("\t\tdataType: %s" % dtype)
    if hidden: lines.append("\t\tisHidden")
    if fmt: lines.append("\t\tformatString: %s" % fmt)
    lines += ["\t\tlineageTag: %s" % tag("ccol/" + name + str(sort)), "\t\tsummarizeBy: none", "\t\tsourceColumn: [%s]" % name]
    if sort: lines.append("\t\tsortByColumn: '%s'" % sort)
    return "\n".join(lines) + "\n"


calc_table("Date", [ccol("Date", "dateTime", "Long Date", key=True), ccol("Year", "int64", "0"), ccol("Month Number", "int64", "0"),
                    ccol("Month", sort="Month Number"), ccol("Year Month"), ccol("Quarter", sort="Quarter Number"),
                    ccol("Quarter Number", "int64", "0", hidden=True)],
           'ADDCOLUMNS (\n    CALENDAR ( DATE ( 2010, 1, 1 ), DATE ( 2026, 10, 31 ) ),\n    "Year", YEAR ( [Date] ),\n'
           '    "Month Number", MONTH ( [Date] ),\n    "Month", FORMAT ( [Date], "mmm" ),\n    "Year Month", FORMAT ( [Date], "yyyy-mm" ),\n'
           '    "Quarter", YEAR ( [Date] ) & " Q" & QUARTER ( [Date] ),\n    "Quarter Number", YEAR ( [Date] ) * 10 + QUARTER ( [Date] )\n)',
           "\tdataCategory: Time\n")
CATS = ["Total household credit", "Mortgage loans", "Non-mortgage loans", "Credit cards", "Lines of credit",
        "Home equity lines of credit", "Personal loans", "Auto loans"]
calc_table("Dim_Category", [ccol("Category", sort="Sort Order"), ccol("Sort Order", "int64", "0", hidden=True)],
           'DATATABLE (\n    "Category", STRING,\n    "Sort Order", INTEGER,\n    {\n' +
           ",\n".join('        { "%s", %d }' % (c, i + 1) for i, c in enumerate(CATS)) + "\n    }\n)")
DS = ["Total debt service ratio", "Mortgage debt service ratio", "Non-mortgage debt service ratio"]
calc_table("Dim_DebtMeasure", [ccol("Debt measure", sort="Sort Order"), ccol("Sort Order", "int64", "0", hidden=True)],
           'DATATABLE (\n    "Debt measure", STRING,\n    "Sort Order", INTEGER,\n    {\n' +
           ",\n".join('        { "%s", %d }' % (c, i + 1) for i, c in enumerate(DS)) + "\n    }\n)")
calc_table("LagSteps", [ccol("Lag Months", "int64", "0")], 'SELECTCOLUMNS ( GENERATESERIES ( 0, 24, 1 ), "Lag Months", [Value] )')

# ---------------------------------------------------------------- measures
PEAK_CREDIT_FILTER = 'REMOVEFILTERS ( \'Date\' ), fact_credit[category] = "Total household credit"'
MEASURES = [
    # credit
    ("Credit $B", "DIVIDE ( SUM ( fact_credit[balance_millions] ), 1000 )", "#,0.0"),
    ("Credit Latest Month", "MAX ( fact_credit[MonthStart] )", "mmm yyyy"),
    ("Credit $B (Latest)", "VAR m = [Credit Latest Month] RETURN CALCULATE ( [Credit $B], fact_credit[MonthStart] = m )", "#,0.0"),
    ("Credit $B (Year Ago)", "VAR m = [Credit Latest Month] RETURN CALCULATE ( [Credit $B], REMOVEFILTERS ( 'Date' ), fact_credit[MonthStart] = EDATE ( m, -12 ) )", "#,0.0"),
    ("Credit YoY % (Latest)", "DIVIDE ( [Credit $B (Latest)] - [Credit $B (Year Ago)], [Credit $B (Year Ago)] )", "0.0%"),
    ("Credit YoY %", "VAR cur = [Credit $B] VAR py = CALCULATE ( [Credit $B], SAMEPERIODLASTYEAR ( 'Date'[Date] ) ) RETURN IF ( ISBLANK ( cur ) || ISBLANK ( py ), BLANK (), DIVIDE ( cur - py, py ) )", "0.0%"),
    ("Total Credit $B (Latest)", 'CALCULATE ( [Credit $B (Latest)], Dim_Category[Category] = "Total household credit" )', "#,0.0"),
    ("Total Credit $T (Latest)", "DIVIDE ( [Total Credit $B (Latest)], 1000 )", '"$"0.0"T"'),
    ("Total Credit YoY %", 'CALCULATE ( [Credit YoY %], Dim_Category[Category] = "Total household credit" )', "0.0%"),
    ("Mortgage Credit YoY %", 'CALCULATE ( [Credit YoY %], Dim_Category[Category] = "Mortgage loans" )', "0.0%"),
    ("Non-mortgage Credit YoY %", 'CALCULATE ( [Credit YoY %], Dim_Category[Category] = "Non-mortgage loans" )', "0.0%"),
    ("Total Credit YoY % (Latest)", 'CALCULATE ( [Credit YoY % (Latest)], Dim_Category[Category] = "Total household credit" )', "0.0%"),
    ("Non-mortgage YoY % (Latest)", 'CALCULATE ( [Credit YoY % (Latest)], Dim_Category[Category] = "Non-mortgage loans" )', "0.0%"),
    ("Mortgage Share (Latest)", 'DIVIDE ( CALCULATE ( [Credit $B (Latest)], Dim_Category[Category] = "Mortgage loans" ), [Total Credit $B (Latest)] )', "0.0%"),
    ("Share of Total %", "DIVIDE ( [Credit $B (Latest)], [Total Credit $B (Latest)] )", "0.0%"),
    ("Credit Latest Text", '"As of " & FORMAT ( [Credit Latest Month], "mmm yyyy" )', None),
    ("Credit Peak YoY", "CALCULATE ( MAX ( fact_credit[yoy_pct] ), %s ) / 100" % PEAK_CREDIT_FILTER, "0.0%"),
    ("Credit Peak Month", "CALCULATE ( MINX ( TOPN ( 1, FILTER ( fact_credit, fact_credit[category] = \"Total household credit\" ), fact_credit[yoy_pct], DESC ), fact_credit[MonthStart] ), REMOVEFILTERS ( 'Date' ) )", "mmm yyyy"),
    ("Credit Peak Text", '"Peak growth was " & FORMAT ( [Credit Peak YoY], "0.0%" ) & " in " & FORMAT ( [Credit Peak Month], "mmm yyyy" )', None),
    ("Credit Headline", '"Household credit is $" & FORMAT ( [Total Credit $T (Latest)], "0.0" ) & " trillion and growing " & FORMAT ( [Total Credit YoY % (Latest)], "0.0%" ) & " a year, down from a " & FORMAT ( [Credit Peak YoY], "0.0%" ) & " peak."', None),
    # rates
    ("Prime Rate", "AVERAGE ( fact_rates[prime] )", "0.00"),
    ("Overnight Rate", "AVERAGE ( fact_rates[overnight] )", "0.00"),
    ("5Y Mortgage Rate", "AVERAGE ( fact_rates[mortgage_5y] )", "0.00"),
    ("Rates Latest Month", "MAX ( fact_rates[MonthStart] )", "mmm yyyy"),
    ("Prime Latest", "VAR m = [Rates Latest Month] RETURN CALCULATE ( [Prime Rate], fact_rates[MonthStart] = m )", "0.00"),
    ("Overnight Latest", "VAR m = [Rates Latest Month] RETURN CALCULATE ( [Overnight Rate], fact_rates[MonthStart] = m )", "0.00"),
    ("5Y Mortgage Latest", "VAR m = [Rates Latest Month] RETURN CALCULATE ( [5Y Mortgage Rate], fact_rates[MonthStart] = m )", "0.00"),
    ("Spread Latest", "[5Y Mortgage Latest] - [Prime Latest]", "+0.00;-0.00;0.00"),
    ("Rates Latest Text", '"As of " & FORMAT ( [Rates Latest Month], "mmm yyyy" )', None),
    ("Spread Text", 'FORMAT ( ABS ( [Spread Latest] ), "0.00" ) & IF ( [Spread Latest] >= 0, " pts above prime", " pts below prime" )', None),
    ("Prime Peak", "CALCULATE ( MAX ( fact_rates[prime] ), REMOVEFILTERS ( 'Date' ) )", "0.00"),
    ("Prime Peak Month", "CALCULATE ( MINX ( TOPN ( 1, fact_rates, fact_rates[prime], DESC ), fact_rates[MonthStart] ), REMOVEFILTERS ( 'Date' ) )", "mmm yyyy"),
    ("Prime Peak Text", '"Peak was " & FORMAT ( [Prime Peak], "0.00" ) & "% in " & FORMAT ( [Prime Peak Month], "mmm yyyy" )', None),
    ("Rates Headline", '"The prime rate is " & FORMAT ( [Prime Latest], "0.00" ) & "%, down from a peak of " & FORMAT ( [Prime Peak], "0.00" ) & "% in " & FORMAT ( [Prime Peak Month], "mmm yyyy" ) & "."', None),
    # debt service
    ("Debt Service Ratio", "AVERAGE ( fact_debt[ratio_pct] )", '0.0"%"'),
    ("DSR Peak", 'CALCULATE ( MAX ( fact_debt[ratio_pct] ), REMOVEFILTERS ( \'Date\' ), fact_debt[debt_measure] = "Total debt service ratio" )', '0.0"%"'),
    ("DSR Latest", 'VAR q = MAX ( fact_debt[quarter_start] ) RETURN CALCULATE ( [Debt Service Ratio], fact_debt[quarter_start] = q, fact_debt[debt_measure] = "Total debt service ratio" )', '0.0"%"'),
    ("DSR Text", '"As of " & FORMAT ( MAX ( fact_debt[quarter_start] ), "mmm yyyy" ) & ". Peak was " & FORMAT ( [DSR Peak], "0.0" ) & "%."', None),
    # lag
    ("Selected Lag", "SELECTEDVALUE ( LagSteps[Lag Months], 18 )", "0"),
    ("Prime Chg 12m", "AVERAGE ( fact_rates[prime_chg_12m] )", "+0.00;-0.00;0.00"),
    ("Prime Chg 12m (Lagged)", "VAR k = [Selected Lag] RETURN CALCULATE ( [Prime Chg 12m], DATEADD ( 'Date'[Date], -k, MONTH ) )", "+0.00;-0.00;0.00"),
    ("Correlation", "AVERAGE ( lag_correlation[correlation] )", "0.00"),
    ("Selected Lag Corr", "VAR k = [Selected Lag] RETURN CALCULATE ( [Correlation], lag_correlation[lag_months] = k )", "0.00"),
    ("Strongest Lag", 'VAR t = ADDCOLUMNS ( ALL ( lag_correlation ), "a", ABS ( lag_correlation[correlation] ) ) RETURN MAXX ( TOPN ( 1, t, [a], DESC ), lag_correlation[lag_months] )', "0"),
    ("Strongest Corr", 'VAR t = ADDCOLUMNS ( ALL ( lag_correlation ), "a", ABS ( lag_correlation[correlation] ) ) RETURN MAXX ( TOPN ( 1, t, [a], DESC ), lag_correlation[correlation] )', "0.00"),
    ("Strongest Lag Text", '[Strongest Lag] & " months"', None),
    ("Strongest Corr Text", '"Correlation " & FORMAT ( [Strongest Corr], "0.00" ) & ": credit growth slows after rate rises"', None),
    ("Selected Lag Text", '[Selected Lag] & " months"', None),
    ("Selected Lag Sub", '"Credit growth vs prime rate, " & [Selected Lag] & " months earlier"', None),
    ("Lag Headline", '"Credit growth responds most to a rate change after about " & [Strongest Lag] & " months. Use the lag selector to compare other lags."', None),
    ("Data Through Text", '"Credit to " & FORMAT ( CALCULATE ( MAX ( fact_credit[MonthStart] ), REMOVEFILTERS ( \'Date\' ) ), "mmm yyyy" ) & "  |  Rates to " & FORMAT ( CALCULATE ( MAX ( fact_rates[MonthStart] ), REMOVEFILTERS ( \'Date\' ) ), "mmm yyyy" ) & "  |  Debt service to " & FORMAT ( CALCULATE ( MAX ( fact_debt[quarter_start] ), REMOVEFILTERS ( \'Date\' ) ), "mmm yyyy" )', None),
]
mt = ["table _Measures", "\tlineageTag: %s" % tag("table/_Measures"), ""]
for n, expr, fmt in MEASURES:
    q = n if n.replace("_", "").isalnum() else "'%s'" % n
    mt.append("\tmeasure %s = %s" % (q, expr))
    if fmt: mt.append("\t\tformatString: %s" % ('"' + fmt.replace('"', '""') + '"' if '"' in fmt else fmt))
    mt += ["\t\tlineageTag: %s" % tag("m/" + n), ""]
write(os.path.join(TMDL, "tables", "_Measures.tmdl"), "\n".join(mt) + "\n")

# =====================================================================================
# REPORT
# =====================================================================================
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
    if extra: vco.update(extra)
    vis["visualContainerObjects"] = vco
    return {"$schema": SCHEMA, "name": name, "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z}, "visual": vis}


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
    if font:
        vis["objects"] = {"labels": [{"properties": {"fontSize": num(font[0]), "color": {"solid": {"color": s(font[1])}}}}]}
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
    if labels: obj["labels"] = [{"properties": {"show": boolean(True)}}]
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


NAV = [("start", "Start here"), ("rates", "Rates"), ("credit", "Credit"), ("lag", "Rate lag")]


def nav(active, z=1000):
    pos = [(1012, 20), (1138, 20), (1012, 60), (1138, 60)]
    out = []
    for i, ((pid, lab), (x, y)) in enumerate(zip(NAV, pos)):
        on = pid == active
        link = {"show": boolean(True), "type": s("PageNavigation"), "navigationSection": s(pid)}
        out.append(button("nav_" + pid, x, y, 118, 32, lab, z + i, link, "#FFFFFF" if on else "#2D5278", NAVY if on else "#FFFFFF",
                          "#FFFFFF" if on else "#7F9BB8", alt="Go to " + lab + (" (current page)" if on else "")))
    return out


def reset_button(x, y, w, h, z):
    return button("reset", x, y, w, h, "Reset filters", z, {"show": boolean(True), "type": s("Bookmark"), "bookmark": s("reset_filters")}, NAVY, "#FFFFFF", None, "Reset all filters")


def fill(color, selector=None):
    d = {"properties": {"fill": {"solid": {"color": s(color)}}}}
    if selector: d["selector"] = selector
    return d


def by_value(table, column, value_literal):
    return {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": col(table, column), "Right": {"Literal": {"Value": value_literal}}}}}]}


def header(title, sub, active):
    out = [textbox("hdr", 0, 0, 1280, 104, [
        [run("PORTFOLIO PROJECT  ·  REAL DATA: BANK OF CANADA AND STATISTICS CANADA, 2010 TO 2026", 8, "#F2C078", True)],
        [run(title, 22, "#FFFFFF", True)], [run(sub, 10, "#E4ECF3")]], 0, p=(18, 24, 8, 24))]
    return out   # no page-navigation buttons: readers use the page tabs


FOOT = "Data: Bank of Canada Valet API; Statistics Canada tables 36-10-0639, 38-10-0238, 11-10-0065. Market-level data, not customer data."


def footer(H):
    y = H - 34
    return [textbox("foot", 20, y, 700, 26, [[run(FOOT, 8, INK2)]], 9000, p=(2, 0, 2, 0)),
            card("through", 720, y, 540, 26, "Data Through Text", None, 9001, font=(8, INK2), p=(2, 0, 2, 0))]


# ---------------------------------------------------------------- background images
S = 4


def icon(d, x, y, kind):
    cx, cy, r = (x + 18) * S, (y + 18) * S, 18 * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TINT)
    k = S; n = NAVY
    def L(pts, wd=2): d.line([(cx + px * k, cy + py * k) for px, py in pts], fill=n, width=wd * S, joint="curve")
    if kind == "bars":
        for i, hh in enumerate((8, 13, 18)): d.rectangle([cx + (-9 + i * 7) * k, cy + (9 - hh) * k, cx + (-5 + i * 7) * k, cy + 9 * k], fill=n)
    elif kind == "check": L([(-9, 0), (-3, 7), (9, -7)], 3)
    elif kind == "clock":
        d.ellipse([cx - 10 * k, cy - 10 * k, cx + 10 * k, cy + 10 * k], outline=n, width=2 * S); L([(0, -6), (0, 0), (5, 3)])
    elif kind == "warn":
        d.polygon([(cx, cy - 10 * k), (cx + 11 * k, cy + 9 * k), (cx - 11 * k, cy + 9 * k)], outline=n, width=2 * S)
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


FX = [20, 440, 860]
CARD_X = [20, 335, 650, 965]; CARD_W = 295; ICONS = ["bars", "check", "clock", "warn"]
ST_H, RT_H, CR_H, LG_H = 780, 830, 1080, 1110


def frow(y): return [("card", x, y, 400, 110) for x in FX]


def krow(y, h=125): return [("card", x, y, CARD_W, h) for x in CARD_X] + [("icon", x + CARD_W - 12 - 36, y + 14, ic, 0) for x, ic in zip(CARD_X, ICONS)]


bg("canvas_start.png", ST_H, [("tint", 20, 120, 1240, 64)] + [("card", x, 200, 400, 150) for x in FX] +
   [("panel", 20, 370, 610, 260), ("panel", 650, 370, 610, 260), ("warn", 20, 650, 1240, 70)])
bg("canvas_rates.png", RT_H, [("panel", 20, 120, 300, 64), ("tint", 340, 120, 780, 64)] + krow(195) +
   [("panel", 20, 340, 1240, 330), ("warn", 20, 690, 1240, 70)])
bg("canvas_credit.png", CR_H, [("panel", 20, 120, 300, 64), ("tint", 340, 120, 780, 64)] + krow(195) +
   [("panel", 20, 340, 610, 340), ("panel", 650, 340, 610, 340), ("panel", 20, 700, 1240, 330)])
bg("canvas_lag.png", LG_H, [("panel", 20, 120, 300, 64), ("tint", 340, 120, 780, 64)] + frow(195) +
   [("panel", 20, 325, 610, 360), ("panel", 650, 325, 610, 360), ("panel", 20, 705, 1240, 270), ("warn", 20, 995, 1240, 70)])

pages = {}


def facts(y, items, z0=200):
    return [card("fact%d" % i, FX[i], y, 400, 110, vm, label, z0 + i, sub="=" + sm, font=(16, NAVY) if is_text else None, p=(10, 18, 6, 18))
            for i, (label, vm, sm, is_text) in enumerate(items)]


def finding(i, x, label, measure, sub, text, text_font=None):
    return [card("find%d" % i, x, 204, 400, 100, measure, label, 200 + i, sub="=" + sub, font=text_font, p=(10, 18, 6, 18)),
            textbox("findtxt%d" % i, x, 304, 400, 46, [[run(text, 9.5, INK2)]], 220 + i, p=(0, 18, 6, 18))]


def block(name, x, y, w, h, head, bullets, z):
    return textbox(name, x, y, w, h, [[run(head, 12, INK, True)]] + [[run("•  " + b, 9.5, INK2)] for b in bullets], z, p=(16, 18, 10, 18))


# ---- Start here
st = header("Household credit and interest rates: how fast does borrowing respond?", "Start here: the question, three findings, and how to use this report.", "start")
st += [textbox("q", 20, 120, 1240, 64, [[run("The question:  ", 10, INK, True),
            run("When the Bank of Canada moves rates, how long before household borrowing and debt-service pressure change?", 10, INK2)]], 100, p=(14, 18, 8, 18)),
       *finding(1, 20, "Household credit growth", "Total Credit YoY % (Latest)", "Credit Peak Text", "Growth has slowed from its 2022 peak as rates rose."),
       *finding(2, 440, "Prime rate now", "Prime Latest", "Prime Peak Text", "The prime rate moved up fast in 2022 and 2023, then eased.", None),
       *finding(3, 860, "Strongest lag", "Strongest Lag Text", "Strongest Corr Text", "The exact lag depends on the method, so read it as about 1.5 years.", (16, NAVY)),
       block("how", 20, 370, 610, 260, "How to use this report", [
           "Use the page tabs (bottom in Desktop, left in the Service) to move between pages.",
           "Rates: the policy rate, prime rate and 5-year mortgage rate over time.",
           "Credit: how household credit and each category has grown. ",
           "Rate lag: pick a lag in months; the scatter and the correlation update.",
           "Reset filters clears every slicer. The Year filter carries across pages."], 300),
       block("about", 650, 370, 610, 260, "About the data and model", [
           "Sources: Bank of Canada Valet API and Statistics Canada tables 36-10-0639, 38-10-0238 and 11-10-0065.",
           "Market-level data only: no customer or account records, and no delinquency data.",
           "Star schema: monthly credit and rate facts, quarterly debt service, and Date, Category and Debt measure dimensions.",
           "Credit runs to Aug 2026, rates to Oct 2026 and debt service to Apr 2026, so each chart shows its own end date."], 400),
       textbox("limit", 20, 650, 1240, 70, [[run("Main limit:  ", 10, INK, True),
            run("rates and credit both trend, so the lag is descriptive and not proof of cause. The strongest lag is about 18 months using the 12-month change in the "
                "prime rate, and about 8 months using the rate level.", 10, INK2)]], 500, p=(12, 18, 8, 22))]
st += footer(ST_H)
pages["start"] = dict(name="Start here", H=ST_H, img="canvas_start.png", visuals=st)

# ---- Rates
rt = header("Rates rose fast in 2022 and 2023, then eased", "The Bank of Canada policy rate, prime rate and 5-year mortgage rate, monthly.", "rates")
rt += [slicer("yr", 20, 120, 300, 64, "Date", "Year", "Year", 100, sync="Year"), reset_button(1140, 132, 120, 40, 150),
       card("headline", 340, 120, 780, 64, "Rates Headline", None, 200, font=(13, NAVY), p=(10, 18, 8, 18))]
for i, (m, lab, sub) in enumerate([("Prime Latest", "Prime rate (%)", "=Rates Latest Text"), ("5Y Mortgage Latest", "5-year mortgage rate (%)", "=Spread Text"),
                                   ("Overnight Latest", "Policy rate (%)", "=Rates Latest Text"), ("Prime Peak", "Highest prime rate since 2010 (%)", "=Prime Peak Text")]):
    rt.append(card("k%d" % i, CARD_X[i], 195, CARD_W, 125, m, lab, 300 + i, sub=sub))
rt += [chart("line", 20, 340, 1240, 330, "lineChart", {"Category": [C("Date", "Date", "Month")], "Y": [M("Overnight Rate", "Policy rate"), M("Prime Rate", "Prime rate"), M("5Y Mortgage Rate", "5-year mortgage rate")]}, 400,
             "Policy, prime and mortgage rates by month", "Prime follows the policy rate closely; the mortgage rate moves with a smaller gap.",
             "Line chart of the policy rate, prime rate and 5-year mortgage rate by month",
             objects={"legend": [{"properties": {"show": boolean(True), "position": s("Bottom")}}], "categoryAxis": [{"properties": {"axisType": s("Scalar")}}]}),
       textbox("note", 20, 690, 1240, 70, [[run("Read with care: ", 9, INK, True),
            run("rates are shown to two decimals because that is how they are published. Prime and mortgage rates are weekly series, so each month shows the last weekly value.", 9, INK2)]], 500, p=(10, 16, 6, 18))]
rt += footer(RT_H)
pages["rates"] = dict(name="Rates", H=RT_H, img="canvas_rates.png", visuals=rt)

# ---- Credit
cr = header("Household credit growth has slowed from its 2022 peak", "Balances and year-over-year growth, seasonally adjusted, for the total and each credit category.", "credit")
cr += [slicer("yr", 20, 120, 300, 64, "Date", "Year", "Year", 100, sync="Year"), reset_button(1140, 132, 120, 40, 150),
       card("headline", 340, 120, 780, 64, "Credit Headline", None, 200, font=(12, NAVY), p=(10, 18, 8, 18))]
for i, (m, lab, sub) in enumerate([("Total Credit $T (Latest)", "Household credit", "=Credit Latest Text"), ("Total Credit YoY % (Latest)", "Growth vs a year earlier", "=Credit Peak Text"),
                                   ("Mortgage Share (Latest)", "Mortgages' share of credit", None), ("Non-mortgage YoY % (Latest)", "Non-mortgage loan growth", None)]):
    cr.append(card("k%d" % i, CARD_X[i], 195, CARD_W, 125, m, lab, 300 + i, sub=sub))
cr += [chart("line", 20, 340, 610, 340, "lineChart", {"Category": [C("Date", "Date", "Month")], "Y": [M("Total Credit YoY %", "Total"), M("Mortgage Credit YoY %", "Mortgages"), M("Non-mortgage Credit YoY %", "Non-mortgage loans")]}, 400,
             "Credit growth by month", "Year-over-year growth for the total, mortgages and other loans.", "Line chart of year-over-year credit growth",
             objects={"legend": [{"properties": {"show": boolean(True), "position": s("Bottom")}}], "categoryAxis": [{"properties": {"axisType": s("Scalar")}}]}),
       chart("bar", 650, 340, 610, 340, "clusteredBarChart", {"Category": [C("Dim_Category", "Category")], "Y": [M("Credit YoY % (Latest)", "Growth vs a year earlier")]}, 500,
             "Latest growth, by category", "Credit cards grow fastest; auto loans and personal loans barely grow.", "Bar chart of latest year-over-year growth by credit category",
             sort=(mea("Credit YoY % (Latest)"), "Descending"), labels=True,
             objects={"dataPoint": [fill(GREY), fill(AMBER, by_value("Dim_Category", "Category", "'Total household credit'"))]}),
       chart("tbl", 20, 700, 1240, 330, "tableEx", {"Values": [C("Dim_Category", "Category"), M("Credit $B (Latest)", "Balance ($B)"), M("Credit YoY % (Latest)", "Growth vs a year earlier"), M("Credit $B (Year Ago)", "Balance a year earlier ($B)")]}, 600,
             "Category scorecard", "Latest balance, a year earlier and growth. Categories overlap (mortgages are part of the total), so balances do not add up.",
             "Table of credit balance, growth and share by category", sort=(mea("Credit $B (Latest)"), "Descending"),
             objects={"total": [{"properties": {"totals": boolean(False)}}]})]
cr += footer(CR_H)
pages["credit"] = dict(name="Credit", H=CR_H, img="canvas_credit.png", visuals=cr)

# ---- Rate lag
lg = header("Credit growth slows about 18 months after rates rise", "Compare credit growth with the prime-rate change a chosen number of months earlier.", "lag")
lg += [slicer("lag", 20, 120, 300, 64, "LagSteps", "Lag Months", "Lag in months", 100, mode="Dropdown"), reset_button(1140, 132, 120, 40, 150),
       card("headline", 340, 120, 780, 64, "Lag Headline", None, 200, font=(11, NAVY), p=(10, 18, 8, 18))]
lg += facts(195, [("Correlation at the selected lag", "Selected Lag Corr", "Selected Lag Sub", False),
                  ("Strongest lag", "Strongest Lag Text", "Strongest Corr Text", True),
                  ("Debt service ratio, latest", "DSR Latest", "DSR Text", False)])
lg += [chart("scatter", 20, 325, 610, 360, "scatterChart", {"Category": [C("Date", "Year Month")], "X": [M("Prime Chg 12m (Lagged)", "Prime-rate change, 12 months (pts), earlier")], "Y": [M("Total Credit YoY %", "Credit growth")]}, 300,
             "Credit growth against an earlier rate change", "Each dot is a month. Change the lag to see the pattern shift.", "Scatter of credit growth against the earlier prime-rate change"),
       chart("cols", 650, 325, 610, 360, "columnChart", {"Category": [C("lag_correlation", "lag_months", "Lag (months)")], "Y": [M("Correlation")]}, 400,
             "Correlation by lag", "Negative means credit growth is lower after rates rise. The strongest value is highlighted.", "Column chart of correlation by lag in months",
             objects={"categoryAxis": [{"properties": {"axisType": s("Categorical")}}], "dataPoint": [fill(GREY), fill(AMBER, by_value("lag_correlation", "lag_months", "18L"))]}),
       chart("dsr", 20, 705, 1240, 270, "lineChart", {"Category": [C("fact_debt", "quarter_start", "Quarter")], "Y": [M("Debt Service Ratio")], "Series": [C("Dim_DebtMeasure", "Debt measure")]}, 500,
             "Debt service ratio by quarter", "Share of household income going to debt payments, seasonally adjusted at annual rates.", "Line chart of debt service ratios by quarter",
             objects={"legend": [{"properties": {"show": boolean(True), "position": s("Bottom")}}], "categoryAxis": [{"properties": {"axisType": s("Scalar")}}]}),
       textbox("note", 20, 995, 1240, 70, [[run("Limit: ", 9, INK, True),
            run("correlation is not causation: rates, inflation and the economy all move together. Credit growth and the rate change both trend, and the 12-month windows overlap, "
                "so treat the lag as a pattern and not a precise delay.", 9, INK2)]], 600, p=(10, 16, 6, 18))]
lg += footer(LG_H)
pages["lag"] = dict(name="Rate lag", H=LG_H, img="canvas_lag.png", visuals=lg)


# ---------------------------------------------------------------- theme
def sol(c): return {"solid": {"color": c}}


theme = {"name": "Household Credit Portfolio", "dataColors": [NAVY, TEAL, AMBER, GREY, "#6B4C7A", "#B23A48", "#4F6D7A", LIGHT],
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
    "settings": {"useStylableVisualContainerHeader": True, "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True, "useEnhancedTooltips": True},
    "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources", "items":
        [{"name": THEME_NAME, "path": THEME_NAME, "type": "CustomTheme"}] + [{"name": n, "path": n, "type": "Image"} for n in images]}]})
wjson(os.path.join(DEF, "version.json"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
wjson(os.path.join(DEF, "pages", "pages.json"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
                                                 "pageOrder": ["start", "rates", "credit", "lag"], "activePageName": "start"})
wjson(os.path.join(REPORT_DIR, "definition.pbir"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
                                                    "version": "4.0", "datasetReference": {"byPath": {"path": "../%s.SemanticModel" % NAME}}})
wjson(os.path.join(REPORT_DIR, ".platform"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
                                              "metadata": {"type": "Report", "displayName": NAME}, "config": {"version": "2.0", "logicalId": tag("report")}})
wjson(os.path.join(OUT, NAME + ".pbip"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json", "version": "1.0",
                                          "artifacts": [{"report": {"path": NAME + ".Report"}}], "settings": {"enableAutoRecovery": True}})

for pid, pg in pages.items():
    pdir = os.path.join(DEF, "pages", pid); os.makedirs(pdir, exist_ok=True)
    objs = {"outspace": [{"properties": {"color": solid(PAPER)}}]}
    if pg["img"]:
        img = pg["img"]
        objs["background"] = [{"properties": {"image": {"image": {"name": s(img), "url": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": img}}}, "scaling": s("Fit")}}, "transparency": num(0.0)}}]
    else:
        objs["background"] = [{"properties": {"color": solid("#FFFFFF"), "transparency": num(0.0)}}]
    objs.update(pg.get("extra_objs", {}))
    page = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json", "name": pid, "displayName": pg["name"],
            "displayOption": pg.get("display", "FitToWidth"), "height": pg["H"], "width": pg.get("W", 1280), "objects": objs}
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
    "options": {"suppressActiveSection": True, "suppressDisplay": True}, "explorationState": {"version": "1.3", "activeSection": "rates", "sections": sections}})
wjson(os.path.join(DEF, "bookmarks", "bookmarks.json"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json", "items": [{"name": "reset_filters"}]})
print("built", {k: len(v["visuals"]) for k, v in pages.items()}, "measures:", len(MEASURES))
