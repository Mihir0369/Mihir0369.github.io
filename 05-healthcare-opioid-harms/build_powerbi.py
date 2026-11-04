"""Generate the Power BI project (PBIP: TMDL model + PBIR report) for the opioid and stimulant harms case study.

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
NAME = "opioid-harms"
MODEL_DIR = os.path.join(OUT, NAME + ".SemanticModel")
REPORT_DIR = os.path.join(OUT, NAME + ".Report")
DEF = os.path.join(REPORT_DIR, "definition")
RES = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources")
TMDL = os.path.join(MODEL_DIR, "definition")
MODEL_FOLDER = os.path.join(HERE, "model")          # the CSVs the model reads (parameter ModelFolder)
THEME_NAME = "OpioidHarmsPortfolio.json"

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
for d in (os.path.join(TMDL, "tables"), os.path.join(TMDL, "cultures"), RES, os.path.join(DEF, "pages"), os.path.join(DEF, "bookmarks")):
    os.makedirs(d, exist_ok=True)


def tag(name):  # stable lineage tags
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "opioid-harms/" + name))


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

annotation PBI_QueryOrder = ["fact_year","fact_quarter","fact_age","ModelFolder"]

annotation __PBI_TimeIntelligenceEnabled = 1

annotation PBI_ProTooling = ["DevMode"]

ref table fact_year
ref table fact_quarter
ref table fact_age
ref table Date
ref table _Measures
ref table Dim_Source
ref table Dim_Substance
ref table Dim_Region
ref table Dim_Age
ref table Dim_Sex
ref table Dim_HeatYear

ref cultureInfo en-US
""")
write(os.path.join(TMDL, "cultures", "en-US.tmdl"), "cultureInfo en-US\n")
write(os.path.join(TMDL, "expressions.tmdl"),
      'expression ModelFolder = "%s" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]\n'
      "\tlineageTag: %s\n\n\tannotation PBI_ResultType = Text\n" % (MODEL_FOLDER.replace("/", "\\"), tag("param")))

REL = [("year_to_date", "fact_year.YearStart", "Date.Date"), ("year_to_source", "fact_year.source", "Dim_Source.Source"),
       ("year_to_substance", "fact_year.substance", "Dim_Substance.Substance"), ("year_to_region", "fact_year.region", "Dim_Region.Region"),
       ("quarter_to_date", "fact_quarter.quarter_start", "Date.Date"), ("quarter_to_source", "fact_quarter.source", "Dim_Source.Source"),
       ("quarter_to_substance", "fact_quarter.substance", "Dim_Substance.Substance"), ("quarter_to_region", "fact_quarter.region", "Dim_Region.Region"),
       ("age_to_date", "fact_age.YearStart", "Date.Date"), ("age_to_source", "fact_age.source", "Dim_Source.Source"),
       ("age_to_substance", "fact_age.substance", "Dim_Substance.Substance"), ("age_to_region", "fact_age.region", "Dim_Region.Region"),
       ("age_to_agegroup", "fact_age.age_group", "Dim_Age.'Age group'"), ("age_to_sex", "fact_age.sex", "Dim_Sex.Sex")]
write(os.path.join(TMDL, "relationships.tmdl"), "\n".join(
    "relationship %s\n\tfromColumn: %s\n\ttoColumn: %s\n" % r for r in REL))


def col(name, dtype, fmt=None, hidden=True, extra=""):
    lines = ["\tcolumn %s" % (name if name.replace("_", "").isalnum() else "'%s'" % name),
             "\t\tdataType: %s" % dtype]
    if hidden:
        lines.append("\t\tisHidden")
    if fmt:
        lines.append("\t\tformatString: %s" % fmt)
    lines += ["\t\tlineageTag: %s" % tag("col/" + name + extra), "\t\tsummarizeBy: none", "\t\tsourceColumn: %s" % name, ""]
    return "\n".join(lines)


def csv_table(tname, fname, columns, add_year_start=False):
    """columns: [(name, dtype, mtype)]; add_year_start adds a date column from the integer `year` column."""
    cols = "\n".join(col(n, dt, "General Number" if dt in ("double", "int64") else None) for n, dt, _ in columns)
    types = ", ".join('{"%s", %s}' % (n, mt) for n, _, mt in columns)
    m = ['let',
         '    Source = Csv.Document(File.Contents(ModelFolder & "\\%s"), [Delimiter = ",", Columns = %d, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),' % (fname, len(columns)),
         '    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),',
         '    Typed = Table.TransformColumnTypes(Promoted, {%s}, "en-US")%s' % (types, "," if add_year_start else "")]
    extra_col = ""
    if add_year_start:
        m.append('    AddDate = Table.AddColumn(Typed, "YearStart", each #date([year], 1, 1), type date)')
        extra_col = "\n" + col("YearStart", "dateTime", "Long Date", True) + "\n\t\tannotation UnderlyingDateTimeDataType = Date\n"
    m += ["in", "    " + ("AddDate" if add_year_start else "Typed")]
    body = "\n".join("\t\t\t\t" + x for x in m)
    write(os.path.join(TMDL, "tables", tname + ".tmdl"),
          "table %s\n\tlineageTag: %s\n\n%s%s\n\tpartition %s = m\n\t\tmode: import\n\t\tsource =\n%s\n\n\tannotation PBI_ResultType = Table\n"
          % (tname, tag("table/" + tname), cols, extra_col, tname, body))


T, N, I = "type text", "type number", "Int64.Type"
csv_table("fact_year", "fact_harms_year.csv",
          [("source", "string", T), ("substance", "string", T), ("region", "string", T), ("year", "int64", I), ("number", "double", N),
           ("number_status", "string", T), ("crude_rate", "double", N), ("rate_status", "string", T), ("partial_period", "int64", I)],
          add_year_start=True)
csv_table("fact_quarter", "fact_harms_quarter.csv",
          [("source", "string", T), ("substance", "string", T), ("region", "string", T), ("quarter_start", "dateTime", "type date"),
           ("number", "double", N), ("number_status", "string", T)])
csv_table("fact_age", "fact_age_sex.csv",
          [("source", "string", T), ("substance", "string", T), ("region", "string", T), ("year", "int64", I), ("age_group", "string", T),
           ("sex", "string", T), ("number", "double", N), ("number_status", "string", T), ("partial_period", "int64", I)],
          add_year_start=True)


def calc_table(tname, columns, source, extra_props=""):
    cols = "\n".join(c for c in columns)
    write(os.path.join(TMDL, "tables", tname + ".tmdl"),
          "table %s\n\tlineageTag: %s\n%s\n%s\n\tpartition %s = calculated\n\t\tmode: import\n\t\tsource =\n%s\n"
          % (tname, tag("table/" + tname), extra_props, cols, tname, "\n".join("\t\t\t\t" + x for x in source.split("\n"))))


def ccol(name, dtype=None, fmt=None, hidden=False, sort=None, key=False, category=None):
    q = name if name.replace("_", "").isalnum() else "'%s'" % name
    lines = ["\tcolumn %s" % q]
    if key: lines.append("\t\tisKey")
    if dtype: lines.append("\t\tdataType: %s" % dtype)
    if hidden: lines.append("\t\tisHidden")
    if fmt: lines.append("\t\tformatString: %s" % fmt)
    if category: lines.append("		dataCategory: %s" % category)
    lines += ["\t\tlineageTag: %s" % tag("ccol/" + name + str(sort)), "\t\tsummarizeBy: none", "\t\tsourceColumn: [%s]" % name]
    if sort: lines.append("\t\tsortByColumn: '%s'" % sort)
    return "\n".join(lines) + "\n"


def datatable(rows, cols):
    """cols: [(name, type)], rows: list of tuples"""
    head = ",\n".join('    "%s", %s' % c for c in cols)
    body = ",\n".join("        { " + ", ".join(('"%s"' % v) if isinstance(v, str) else str(v) for v in r) + " }" for r in rows)
    return "DATATABLE (\n%s,\n    {\n%s\n    }\n)" % (head, body)


calc_table("Date", [ccol("Date", "dateTime", "Long Date", key=True), ccol("Year", "int64", "0"), ccol("Year Label", sort="Year"),
                    ccol("Quarter", sort="Quarter Number"), ccol("Quarter Number", "int64", "0", hidden=True)],
           'ADDCOLUMNS (\n    CALENDAR ( DATE ( 2016, 1, 1 ), DATE ( 2026, 3, 31 ) ),\n    "Year", YEAR ( [Date] ),\n'
           '    "Year Label", IF ( YEAR ( [Date] ) = 2026, "2026 (Jan to Mar)", FORMAT ( YEAR ( [Date] ), "0" ) ),\n'
           '    "Quarter", YEAR ( [Date] ) & " Q" & QUARTER ( [Date] ),\n    "Quarter Number", YEAR ( [Date] ) * 10 + QUARTER ( [Date] )\n)',
           "\tdataCategory: Time\n")

SOURCES = ["Deaths", "Hospital stays", "Emergency department visits", "EMS responses"]
calc_table("Dim_Source", [ccol("Source", sort="Sort Order"), ccol("Sort Order", "int64", "0", hidden=True)],
           datatable([(s_, i + 1) for i, s_ in enumerate(SOURCES)], [("Source", "STRING"), ("Sort Order", "INTEGER")]))
calc_table("Dim_Substance", [ccol("Substance", sort="Sort Order"), ccol("Sort Order", "int64", "0", hidden=True)],
           datatable([("Opioids", 1), ("Stimulants", 2)], [("Substance", "STRING"), ("Sort Order", "INTEGER")]))
REGIONS = [("Canada", "Canada", "", 0, 0), ("British Columbia", "Province", "BC", 2, 1), ("Alberta", "Province", "AB", 2, 2),
           ("Saskatchewan", "Province", "SK", 2, 3), ("Manitoba", "Province", "MB", 2, 4), ("Ontario", "Province", "ON", 2, 5),
           ("Quebec", "Province", "QC", 2, 6), ("New Brunswick", "Province", "NB", 2, 7), ("Nova Scotia", "Province", "NS", 3, 7),
           ("Prince Edward Island", "Province", "PE", 3, 8), ("Newfoundland and Labrador", "Province", "NL", 2, 8),
           ("Yukon", "Territory", "YT", 1, 1), ("Northwest Territories", "Territory", "NT", 1, 2), ("Nunavut", "Territory", "NU", 1, 3),
           ("Territories", "Territories combined", "", 0, 0), ("Northern and rural Manitoba", "EMS area", "", 0, 0),
           ("Winnipeg, Manitoba", "EMS area", "", 0, 0), ("Whitehorse, Yukon", "EMS area", "", 0, 0),
           ("Yellowknife, Northwest Territories", "EMS area", "", 0, 0)]
ROW_LABEL = {0: "", 1: "North", 2: "Provinces", 3: "Atlantic"}
calc_table("Dim_Region", [ccol("Region", sort="Sort Order"), ccol("Region Type"), ccol("Tile Code"), ccol("Tile Row Label", sort="Tile Row"), ccol("Tile Row", "int64", "0", hidden=True),
                          ccol("Tile Col", "int64", "0", hidden=True), ccol("Sort Order", "int64", "0", hidden=True)],
           datatable([(r, t_, c_, ROW_LABEL[tr], tr, tc, i + 1) for i, (r, t_, c_, tr, tc) in enumerate(REGIONS)],
                     [("Region", "STRING"), ("Region Type", "STRING"), ("Tile Code", "STRING"), ("Tile Row Label", "STRING"), ("Tile Row", "INTEGER"), ("Tile Col", "INTEGER"), ("Sort Order", "INTEGER")]))
AGES = ["0 to 19 years", "20 to 29 years", "30 to 39 years", "40 to 49 years", "50 to 59 years", "60 years or more"]
calc_table("Dim_Age", [ccol("Age group", sort="Sort Order"), ccol("Sort Order", "int64", "0", hidden=True)],
           datatable([(a_, i + 1) for i, a_ in enumerate(AGES)], [("Age group", "STRING"), ("Sort Order", "INTEGER")]))
calc_table("Dim_Sex", [ccol("Sex", sort="Sort Order"), ccol("Sort Order", "int64", "0", hidden=True)],
           datatable([("Female", 1), ("Male", 2)], [("Sex", "STRING"), ("Sort Order", "INTEGER")]))

HEAT_YEARS = [(str(y_), y_) for y_ in range(2018, 2026)] + [("2026 Q1", 2026)]
calc_table("Dim_HeatYear", [ccol("Heat Year", sort="Heat Year Number"), ccol("Heat Year Number", "int64", "0", hidden=True)],
           datatable(HEAT_YEARS, [("Heat Year", "STRING"), ("Heat Year Number", "INTEGER")]))

# ---------------------------------------------------------------- measures
# Every count measure returns the Canada figure when no region is selected, so a region is never double counted.
SCOPE = "ISFILTERED ( Dim_Region )"


def scoped(expr):
    return "VAR scoped = %s RETURN IF ( scoped, %s, CALCULATE ( %s, Dim_Region[Region] = \"Canada\" ) )" % (SCOPE, expr, expr)


FY = "REMOVEFILTERS ( Date ), fact_year[year] = y"


def peak_set(prefix, src, label):
    """Latest full year, peak, peak year and change for opioid counts in Canada for one source."""
    flt = 'Dim_Source[Source] = "%s", Dim_Substance[Substance] = "Opioids"' % src
    yrs = "CALCULATETABLE ( VALUES ( fact_year[year] ), REMOVEFILTERS ( Date ), fact_year[partial_period] = 0 )"
    return [
        (prefix + " LFY", "VAR y = [Latest Full Year] RETURN CALCULATE ( [Count], %s, %s )" % (FY, flt), "#,0"),
        (prefix + " Peak", "VAR yrs = %s RETURN MAXX ( yrs, CALCULATE ( [Count], REMOVEFILTERS ( Date ), %s ) )" % (yrs, flt), "#,0"),
        (prefix + " Peak Year", "VAR yrs = %s VAR t = ADDCOLUMNS ( yrs, \"v\", CALCULATE ( [Count], REMOVEFILTERS ( Date ), %s ) ) RETURN MAXX ( TOPN ( 1, t, [v], DESC ), fact_year[year] )" % (yrs, flt), "0"),
        (prefix + " vs Peak %", "DIVIDE ( [%s LFY] - [%s Peak], [%s Peak] )" % (prefix, prefix, prefix), "+0.00%;-0.00%;0.00%"),
    ]


def qyoy(prefix, src):
    q = 'REMOVEFILTERS ( Date ), Dim_Source[Source] = "%s", Dim_Substance[Substance] = "Opioids"' % src
    return [(prefix + " Latest Quarter YoY %",
             "VAR q = [Latest Quarter] VAR cur = CALCULATE ( [Quarter Count], %s, fact_quarter[quarter_start] = q ) "
             "VAR py = CALCULATE ( [Quarter Count], %s, fact_quarter[quarter_start] = EDATE ( q, -12 ) ) RETURN DIVIDE ( cur - py, py )" % (q, q), "+0.00%;-0.00%;0.00%")]


def by_src(src):
    return 'Dim_Source[Source] = "%s", Dim_Substance[Substance] = "Opioids"' % src


MEASURES = [
    # base counts (scoped to a region, Canada by default)
    ("Count", scoped("SUM ( fact_year[number] )"), "#,0"),
    ("Rate per 100k", scoped("MAX ( fact_year[crude_rate] )"), "0.0"),
    ("Quarter Count", scoped("SUM ( fact_quarter[number] )"), "#,0"),
    ("Age Sex Count", scoped("SUM ( fact_age[number] )"), "#,0"),
    # slicer defaults: with nothing chosen the report shows deaths, opioids
    ("Sel Source", 'SELECTEDVALUE ( Dim_Source[Source], "Deaths" )', None),
    ("Sel Substance", 'SELECTEDVALUE ( Dim_Substance[Substance], "Opioids" )', None),
    ("Latest Full Year", "CALCULATE ( MAX ( fact_year[year] ), REMOVEFILTERS (), fact_year[partial_period] = 0 )", "0"),
    ("Default Year", "2024", "0"),
    ("Focus Year", "SELECTEDVALUE ( 'Date'[Year], [Default Year] )", "0"),
    ("Focus Year Label", 'VAR y = [Focus Year] RETURN IF ( y = 2026, "2026 (Jan to Mar)", FORMAT ( y, "0" ) )', None),
    ("Showing Short", '"Showing: " & [Sel Source] & ", " & LOWER ( [Sel Substance] )', None),
    ("Showing Text", '"Showing: " & [Sel Source] & ", " & LOWER ( [Sel Substance] ) & ", " & [Focus Year Label]', None),
    ("Count Sel", "VAR s = [Sel Source] VAR sub = [Sel Substance] RETURN CALCULATE ( [Count], Dim_Source[Source] = s, Dim_Substance[Substance] = sub )", "#,0"),
    ("Rate Sel", "VAR s = [Sel Source] VAR sub = [Sel Substance] RETURN CALCULATE ( [Rate per 100k], Dim_Source[Source] = s, Dim_Substance[Substance] = sub )", "0.0"),
    ("Count (Focus Year)", "VAR y = [Focus Year] VAR s = [Sel Source] VAR sub = [Sel Substance] RETURN CALCULATE ( [Count], REMOVEFILTERS ( Date ), fact_year[year] = y, Dim_Source[Source] = s, Dim_Substance[Substance] = sub )", "#,0"),
    ("Rate (Focus Year)", "VAR y = [Focus Year] VAR s = [Sel Source] VAR sub = [Sel Substance] RETURN CALCULATE ( [Rate per 100k], REMOVEFILTERS ( Date ), fact_year[year] = y, Dim_Source[Source] = s, Dim_Substance[Substance] = sub )", "0.0"),
    ("Value Status", "VAR y = [Focus Year] VAR s = [Sel Source] VAR sub = [Sel Substance] RETURN CALCULATE ( IF ( COUNTROWS ( fact_year ) = 0, BLANK (), SELECTEDVALUE ( fact_year[number_status] ) ), REMOVEFILTERS ( Date ), fact_year[year] = y, Dim_Source[Source] = s, Dim_Substance[Substance] = sub )", None),
    ("Rate Available Text", 'VAR s = [Sel Source] RETURN IF ( s = "EMS responses", "PHAC publishes no rate for EMS responses, so this page shows counts only.", "Crude rate per 100,000 population, not age-adjusted." )', None),
    # quarters
    ("Latest Quarter", "CALCULATE ( MAX ( fact_quarter[quarter_start] ), REMOVEFILTERS ( Date ) )", "mmm yyyy"),
    ("Latest Quarter Text", 'VAR q = [Latest Quarter] RETURN YEAR ( q ) & " Q" & ROUNDUP ( MONTH ( q ) / 3, 0 )', None),
    ("Quarter Count Sel", "VAR s = [Sel Source] VAR sub = [Sel Substance] RETURN CALCULATE ( [Quarter Count], Dim_Source[Source] = s, Dim_Substance[Substance] = sub )", "#,0"),
    ("Latest Quarter Count", "VAR q = [Latest Quarter] RETURN CALCULATE ( [Quarter Count Sel], REMOVEFILTERS ( Date ), fact_quarter[quarter_start] = q )", "#,0"),
    ("Prior Year Quarter Count", "VAR q = [Latest Quarter] RETURN CALCULATE ( [Quarter Count Sel], REMOVEFILTERS ( Date ), fact_quarter[quarter_start] = EDATE ( q, -12 ) )", "#,0"),
    ("Quarter YoY %", "DIVIDE ( [Latest Quarter Count] - [Prior Year Quarter Count], [Prior Year Quarter Count] )", "+0.00%;-0.00%;0.00%"),
    ("Peak Quarter Count", "CALCULATE ( MAXX ( VALUES ( fact_quarter[quarter_start] ), [Quarter Count Sel] ), REMOVEFILTERS ( Date ) )", "#,0"),
    ("Peak Quarter", "VAR t = ADDCOLUMNS ( CALCULATETABLE ( VALUES ( fact_quarter[quarter_start] ), REMOVEFILTERS ( Date ) ), \"v\", [Quarter Count Sel] ) RETURN MINX ( TOPN ( 1, t, [v], DESC ), fact_quarter[quarter_start] )", "mmm yyyy"),
    ("Peak Quarter Text", '"Highest quarter was " & FORMAT ( [Peak Quarter], "mmm yyyy" )', None),
    ("Trend Headline", '[Showing Short] & ". " & [Latest Quarter Text] & " is " & FORMAT ( [Quarter YoY %], "+0.00%;-0.00%" ) & " vs a year earlier."', None),
    ("Latest Full Year Count", "VAR y = [Latest Full Year] RETURN CALCULATE ( [Count Sel], REMOVEFILTERS ( Date ), fact_year[year] = y )", "#,0"),
    ("Latest Full Year Text", '"Full year " & [Latest Full Year]', None),
]
MEASURES += peak_set("Opioid Deaths", "Deaths", "deaths")
MEASURES += peak_set("Opioid Hosp", "Hospital stays", "hospital stays")
MEASURES += peak_set("Opioid ED", "Emergency department visits", "emergency department visits")
MEASURES += peak_set("Opioid EMS", "EMS responses", "EMS responses")
MEASURES += qyoy("Deaths", "Deaths") + qyoy("Hosp", "Hospital stays") + qyoy("ED", "Emergency department visits") + qyoy("EMS", "EMS responses")
MEASURES += [
    ("Deaths Peak Text", '"Peak was " & FORMAT ( [Opioid Deaths Peak], "#,0" ) & " in " & [Opioid Deaths Peak Year]', None),
    ("Deaths LFY Text", '"Full year " & [Latest Full Year] & ". Peak was " & FORMAT ( [Opioid Deaths Peak], "#,0" ) & " in " & [Opioid Deaths Peak Year]', None),
    ("Other Peaks Text", '"Hospital stays " & FORMAT ( [Opioid Hosp vs Peak %], "+0.00%;-0.00%" ) & ", ED visits " & FORMAT ( [Opioid ED vs Peak %], "+0.00%;-0.00%" )', None),
    ("EMS Peak Text", '"Peak was " & FORMAT ( [Opioid EMS Peak], "#,0" ) & " in " & [Opioid EMS Peak Year]', None),
    ("Hosp per Death", "DIVIDE ( [Opioid Hosp LFY], [Opioid Deaths LFY] )", "0.00"),
    ("Hosp per Death 2016", 'DIVIDE ( CALCULATE ( [Count], REMOVEFILTERS ( Date ), fact_year[year] = 2016, ' + by_src("Hospital stays") + ' ), CALCULATE ( [Count], REMOVEFILTERS ( Date ), fact_year[year] = 2016, ' + by_src("Deaths") + ' ) )', "0.00"),
    ("Hosp per Death Text", '"It was " & FORMAT ( [Hosp per Death 2016], "0.00" ) & " in 2016"', None),
    ("EMS Quarter Note", '[Latest Quarter Text] & ": " & FORMAT ( [EMS Latest Quarter YoY %], "+0.00%;-0.00%" ) & " vs a year ago"', None),
    # four measures side by side (opioids)
    ("Opioid Count", 'CALCULATE ( [Count], Dim_Substance[Substance] = "Opioids" )', "#,0"),
    ("Deaths (Opioids)", "CALCULATE ( [Count], %s )" % by_src("Deaths"), "#,0"),
    ("Hospital stays (Opioids)", "CALCULATE ( [Count], %s )" % by_src("Hospital stays"), "#,0"),
    ("ED Visits (Opioids)", "CALCULATE ( [Count], %s )" % by_src("Emergency department visits"), "#,0"),
    ("EMS Responses (Opioids)", "CALCULATE ( [Count], %s )" % by_src("EMS responses"), "#,0"),
    ("Index 2019", "IF ( MAX ( fact_year[partial_period] ) = 1, BLANK (), DIVIDE ( [Opioid Count], CALCULATE ( [Opioid Count], REMOVEFILTERS ( Date ), fact_year[year] = 2019 ) ) * 100 )", "0"),
    ("Hosp per Death (Year)", "DIVIDE ( [Hospital stays (Opioids)], [Deaths (Opioids)] )", "0.00"),
    ("Burden Headline", '"Since the 2023 peak: deaths " & FORMAT ( [Opioid Deaths vs Peak %], "+0.00%;-0.00%" ) & ", hospital stays " & FORMAT ( [Opioid Hosp vs Peak %], "+0.00%;-0.00%" ) & ", EMS responses " & FORMAT ( [Opioid EMS vs Peak %], "+0.00%;-0.00%" ) & "." ', None),
    # who
    ("Age Count (Focus Year)", "VAR y = [Focus Year] VAR s = [Sel Source] VAR sub = [Sel Substance] RETURN CALCULATE ( [Age Sex Count], REMOVEFILTERS ( Date ), fact_age[year] = y, Dim_Source[Source] = s, Dim_Substance[Substance] = sub )", "#,0"),
    ("Male Share", 'DIVIDE ( CALCULATE ( [Age Count (Focus Year)], Dim_Sex[Sex] = "Male" ), [Age Count (Focus Year)] )', "0.00%"),
    ("Age 30 to 49 Share", 'DIVIDE ( CALCULATE ( [Age Count (Focus Year)], Dim_Age[Age group] IN { "30 to 39 years", "40 to 49 years" } ), [Age Count (Focus Year)] )', "0.00%"),
    ("Heat Count", "VAR y = SELECTEDVALUE ( Dim_HeatYear[Heat Year Number] ) VAR s = [Sel Source] VAR sub = [Sel Substance] RETURN CALCULATE ( [Age Sex Count], REMOVEFILTERS ( Date ), fact_age[year] = y, Dim_Source[Source] = s, Dim_Substance[Substance] = sub )", "#,0"),
    ("Tile Max", "CALCULATE ( MAXX ( FILTER ( ALL ( Dim_Region ), Dim_Region[Tile Row] > 0 ), [Rate (Focus Year)] ), ALL ( Dim_Region ) )", "0.0"),
    ("Tile Label", 'VAR code = SELECTEDVALUE ( Dim_Region[Tile Code], "" ) VAR r = [Rate (Focus Year)] RETURN IF ( code = "", BLANK (), code & IF ( ISBLANK ( r ), "  n/a", "  " & FORMAT ( r, "0.0" ) ) )', None),
    ("Tile Fill", 'VAR code = SELECTEDVALUE ( Dim_Region[Tile Code], "" ) VAR r = [Rate (Focus Year)] VAR k = DIVIDE ( r, [Tile Max] ) RETURN IF ( code = "", BLANK (), IF ( ISBLANK ( r ), "#E3E3E3", SWITCH ( TRUE (), k < 0.2, "#E4ECF3", k < 0.4, "#A9C3D9", k < 0.6, "#5F8FB5", k < 0.8, "#2D5F8A", "#1B3A5C" ) ) )', None),
    ("Tile Font", 'VAR code = SELECTEDVALUE ( Dim_Region[Tile Code], "" ) VAR r = [Rate (Focus Year)] VAR k = DIVIDE ( r, [Tile Max] ) RETURN IF ( code = "", BLANK (), IF ( ISBLANK ( r ), "#8A8A8A", IF ( k < 0.4, "#1F2D3D", "#FFFFFF" ) ) )', None),
    ("Tile Extremes", 'VAR t = FILTER ( ADDCOLUMNS ( FILTER ( ALL ( Dim_Region ), Dim_Region[Tile Row] > 0 ), "r", [Rate (Focus Year)] ), NOT ISBLANK ( [r] ) ) VAR hi = TOPN ( 1, t, [r], DESC ) VAR lo = TOPN ( 1, t, [r], ASC ) RETURN IF ( COUNTROWS ( t ) = 0, "No rates for this selection.", "Highest: " & MAXX ( hi, Dim_Region[Region] ) & " (" & FORMAT ( MAXX ( hi, [r] ), "0.0" ) & "). Lowest: " & MAXX ( lo, Dim_Region[Region] ) & " (" & FORMAT ( MAXX ( lo, [r] ), "0.0" ) & ")." )', None),
    ("Canada Rate", 'CALCULATE ( [Rate (Focus Year)], Dim_Region[Region] = "Canada" )', "0.0"),
    ("Canada Rate Sub", '"Only the places that report"', None),
    ("Highest Rate", 'VAR t = FILTER ( ADDCOLUMNS ( FILTER ( ALL ( Dim_Region ), Dim_Region[Tile Row] > 0 ), "r", [Rate (Focus Year)] ), NOT ISBLANK ( [r] ) ) RETURN IF ( COUNTROWS ( t ) = 0, BLANK (), MAXX ( t, [r] ) )', "0.0"),
    ("Highest Region", 'VAR t = FILTER ( ADDCOLUMNS ( FILTER ( ALL ( Dim_Region ), Dim_Region[Tile Row] > 0 ), "r", [Rate (Focus Year)] ), NOT ISBLANK ( [r] ) ) RETURN IF ( COUNTROWS ( t ) = 0, "No rates for this selection", MAXX ( TOPN ( 1, t, [r], DESC ), Dim_Region[Region] ) )', None),
    ("Lowest Rate", 'VAR t = FILTER ( ADDCOLUMNS ( FILTER ( ALL ( Dim_Region ), Dim_Region[Tile Row] > 0 ), "r", [Rate (Focus Year)] ), NOT ISBLANK ( [r] ) ) RETURN IF ( COUNTROWS ( t ) = 0, BLANK (), MINX ( t, [r] ) )', "0.0"),
    ("Lowest Region", 'VAR t = FILTER ( ADDCOLUMNS ( FILTER ( ALL ( Dim_Region ), Dim_Region[Tile Row] > 0 ), "r", [Rate (Focus Year)] ), NOT ISBLANK ( [r] ) ) RETURN IF ( COUNTROWS ( t ) = 0, "No rates for this selection", MAXX ( TOPN ( 1, t, [r], ASC ), Dim_Region[Region] ) )', None),
    ("Regions With Rate", 'VAR t = FILTER ( ADDCOLUMNS ( FILTER ( ALL ( Dim_Region ), Dim_Region[Tile Row] > 0 ), "r", [Rate (Focus Year)] ), NOT ISBLANK ( [r] ) ) RETURN COUNTROWS ( t )', "0"),
    ("Regions With Rate Sub", '"of the provinces and territories"', None),
    ("Canada Rate Text", 'VAR c = CALCULATE ( [Rate (Focus Year)], Dim_Region[Region] = "Canada" ) RETURN IF ( ISBLANK ( c ), "Canada: no rate is published for this source.", "Canada: " & FORMAT ( c, "0.0" ) & " per 100,000, counting only the places that report." )', None),
    ("Heat Max", "CALCULATE ( MAXX ( CROSSJOIN ( ALL ( Dim_Age[Age group] ), ALL ( Dim_HeatYear[Heat Year] ) ), [Heat Count] ), ALL ( Dim_Age ), ALL ( Dim_HeatYear ) )", "#,0"),
    ("Heat Fill", 'VAR v = [Heat Count] VAR k = DIVIDE ( v, [Heat Max] ) RETURN IF ( ISBLANK ( v ), BLANK (), SWITCH ( TRUE (), k < 0.1, "#FFF4DC", k < 0.25, "#FBD9A0", k < 0.45, "#F4B860", k < 0.7, "#E08A1E", "#B85C00" ) )', None),
    ("Heat Font", 'VAR v = [Heat Count] VAR k = DIVIDE ( v, [Heat Max] ) RETURN IF ( ISBLANK ( v ), BLANK (), IF ( k < 0.45, "#1F2D3D", "#FFFFFF" ) )', None),
    ("Coverage Status", 'CALCULATE ( IF ( COUNTROWS ( fact_year ) = 0, "Not in file", SELECTEDVALUE ( fact_year[number_status] ) ), REMOVEFILTERS ( Date ), fact_year[year] = 2024, Dim_Substance[Substance] = "Opioids" )', None),
    ("Coverage Fill", 'SWITCH ( [Coverage Status], "Reported", "#CFE6EA", "Suppressed", "#FBE3B3", "Not available", "#E3E3E3", "#FFFFFF" )', None),
    ("Coverage Font", 'SWITCH ( [Coverage Status], "Not in file", "#B5B5B5", "Not available", "#6B6B6B", "#1F2D3D" )', None),
    ("Age Count Sel", "VAR s = [Sel Source] VAR sub = [Sel Substance] RETURN CALCULATE ( [Age Sex Count], Dim_Source[Source] = s, Dim_Substance[Substance] = sub )", "#,0"),
    ("Age Share of Total", "DIVIDE ( [Age Count (Focus Year)], [Count (Focus Year)] )", "0.00%"),
    ("Share of Group", "DIVIDE ( [Age Count (Focus Year)], CALCULATE ( [Age Count (Focus Year)], REMOVEFILTERS ( Dim_Age ), REMOVEFILTERS ( Dim_Sex ) ) )", "0.00%"),
    ("Who Headline", '[Showing Text] & ". About " & FORMAT ( [Male Share], "0.00%" ) & " are male and " & FORMAT ( [Age 30 to 49 Share], "0.00%" ) & " are aged 30 to 49."', None),
    ("Data Through Text", '"Counts to " & [Latest Quarter Text] & "  |  Latest full year " & [Latest Full Year] & "  |  2026 is January to March only"', None),
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


def reset_button(x, y, w, h, z):
    return button("reset", x, y, w, h, "Reset filters", z, {"show": boolean(True), "type": s("Bookmark"), "bookmark": s("reset_filters")}, NAVY, "#FFFFFF", None, "Reset all filters")


def fill(color, selector=None):
    d = {"properties": {"fill": {"solid": {"color": s(color)}}}}
    if selector: d["selector"] = selector
    return d


def gradient(measure, lo, hi):
    return {"solid": {"color": {"expr": {"FillRule": {"Input": mea(measure), "FillRule": {"linearGradient2": {
        "min": {"color": {"Literal": {"Value": "'" + lo + "'"}}}, "max": {"color": {"Literal": {"Value": "'" + hi + "'"}}}, "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'noColor'"}}}}}}}}}}


def field_color(measure):
    return {"solid": {"color": {"expr": mea(measure)}}}


def by_value(table, column, value_literal):
    return {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": col(table, column), "Right": {"Literal": {"Value": value_literal}}}}}]}


def header(title, sub):
    return [textbox("hdr", 0, 0, 1280, 104, [
        [run("PORTFOLIO PROJECT  ·  REAL DATA: PUBLIC HEALTH AGENCY OF CANADA, 2016 TO 2026", 8, "#F2C078", True)],
        [run(title, 22, "#FFFFFF", True)], [run(sub, 10, "#E4ECF3")]], 0, p=(18, 24, 8, 24))]   # no page buttons: readers use the page tabs


FOOT = "Data: PHAC, Opioid- and Stimulant-related Harms in Canada (Open Government Licence - Canada). No individual records."


def footer(H):
    y = H - 34
    return [textbox("foot", 20, y, 760, 26, [[run(FOOT, 8, INK2)]], 9000, p=(2, 0, 2, 0)),
            card("through", 780, y, 480, 26, "Data Through Text", None, 9001, font=(8, INK2), p=(2, 0, 2, 0))]


# ---------------------------------------------------------------- background images
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


FX = [20, 440, 860]
CARD_X = [20, 335, 650, 965]; CARD_W = 295; ICONS = ["bars", "check", "clock", "warn"]
ST_H, TR_H, PR_H, BU_H, WH_H, QU_H = 790, 1360, 1130, 1040, 1060, 715


def frow(y): return [("card", x, y, 400, 110) for x in FX]


def krow(y, h=125): return [("card", x, y, CARD_W, h) for x in CARD_X] + [("icon", x + CARD_W - 12 - 26, y + 10, ic, 0) for x, ic in zip(CARD_X, ICONS)]


def facts(y, items, z0=200):
    return [card("fact%d" % i, FX[i], y, 400, 110, vm, label, z0 + i, sub="=" + sm if sm else None, font=(16, NAVY) if is_text else None, p=(10, 18, 6, 18))
            for i, (label, vm, sm, is_text) in enumerate(items)]


def block(name, x, y, w, h, head, bullets, z):
    return textbox(name, x, y, w, h, [[run(head, 12, INK, True)]] + [[run("•  " + b, 9.5, INK2)] for b in bullets], z, p=(16, 18, 10, 18))


def kcards(y, items, z0=300):
    return [card("k%d" % i, CARD_X[i], y, CARD_W, 110, m, lab, z0 + i, sub=sub) for i, (m, lab, sub) in enumerate(items)]


SRC_X, SUB_X, YR_X, REG_X = 20, 230, 440, 650


def fbox(n, x, y, head, big, txt, z):
    """One of the three finding boxes used on every analysis page: heading, key number, one or two sentences."""
    return textbox("f%d" % n, x, y, 400, 150, [[run(head, 12, NAVY, True)], [run(big, 22, "#C77700", True)], [run(txt, 10.5, INK2)]], z, p=(10, 16, 6, 16))


def findings(y, items):
    return [fbox(i + 1, 20 + 420 * i, y, h, b, t, 820 + i) for i, (h, b, t) in enumerate(items)]


def footnote(y, text, z=800):
    return textbox("note", 20, y, 1240, 50, [[run("Footnote: ", 9, INK, True), run(text, 9, INK2)]], z, p=(8, 16, 4, 18))


FP = [("panel", 20, 0, 400, 150), ("panel", 440, 0, 400, 150), ("panel", 860, 0, 400, 150)]


def fpanels(y): return [(k, x, y, w, h) for k, x, _, w, h in FP]


bg("canvas_start.png", ST_H, [("tint", 20, 120, 1100, 64)] + krow(200, 110) + [("panel", 20, 335, 610, 170), ("panel", 650, 335, 610, 170), ("panel", 20, 525, 610, 130), ("panel", 650, 525, 610, 130), ("warn", 20, 675, 1240, 50)])
bg("canvas_trend.png", TR_H, [("panel", 20, 120, 250, 64), ("panel", 280, 120, 280, 64), ("tint", 570, 120, 550, 64)] + krow(200, 110) +
   [("panel", 20, 330, 1240, 330), ("panel", 20, 680, 760, 400), ("panel", 800, 680, 460, 400)] + fpanels(1100) + [("warn", 20, 1270, 1240, 50)])
bg("canvas_prov.png", PR_H, [("panel", 20, 120, 250, 64), ("panel", 280, 120, 280, 64), ("panel", 570, 120, 230, 64), ("tint", 810, 120, 310, 64)] + krow(200, 110) +
   [("panel", 20, 330, 580, 520), ("panel", 620, 330, 640, 520)] + fpanels(870) + [("warn", 20, 1040, 1240, 50)])
bg("canvas_burden.png", BU_H, [("panel", 20, 120, 300, 64), ("tint", 340, 120, 780, 64)] + krow(200, 110) +
   [("panel", 20, 330, 610, 430), ("panel", 650, 330, 610, 430)] + fpanels(780) + [("warn", 20, 950, 1240, 50)])
bg("canvas_quality.png", QU_H, [("panel", 20, 130, 720, 540), ("panel", 760, 130, 500, 300), ("panel", 760, 445, 500, 225)])
bg("canvas_who.png", WH_H, [("panel", 20, 120, 230, 64), ("panel", 260, 120, 260, 64), ("panel", 530, 120, 230, 64), ("panel", 770, 120, 260, 64), ("panel", 1040, 120, 140, 64)] + krow(200, 110) +
   [("panel", 20, 330, 740, 380), ("panel", 20, 720, 740, 60), ("panel", 780, 330, 480, 450)] + fpanels(800) + [("warn", 20, 970, 1240, 50)])

pages = {}

# ---- Start here
st = header("Opioid and stimulant harms in Canada: what has changed since 2016?", "Start here: the headline numbers, what they mean, and what I would do about them.")
st += [reset_button(1140, 132, 120, 40, 150),
       textbox("q", 20, 120, 1100, 64, [[run("The question:  ", 10, INK, True),
            run("Which harm measures are falling, which are not, and where is the burden greatest, so a public health team knows where to plan?", 10, INK2)]], 100, p=(12, 18, 8, 18))]
st += kcards(200, [("Opioid Deaths LFY", "Opioid deaths, latest full year", "=Deaths LFY Text"),
                   ("Opioid Deaths vs Peak %", "Deaths against the peak", "=Other Peaks Text"),
                   ("Opioid EMS vs Peak %", "EMS against the peak", "=EMS Quarter Note"),
                   ("Hosp per Death", "Hospital stays per death", "=Hosp per Death Text")])
st += [block("finds", 20, 335, 610, 170, "What the data shows", [
           "Opioid deaths are 29.43% below the 2023 peak (8,083 to 5,704), but EMS responses are only 7.84% below theirs. The measures do not fall together.",
           "Rates vary widely: in 2024 British Columbia had 35.7 deaths per 100,000, Ontario 14.0 and Quebec 3.4.",
           "Around 71.64% of deaths are men, and 52.58% are aged 30 to 49."], 300),
       block("recs", 650, 335, 610, 170, "What I would do", [
           "Track EMS responses and emergency department visits next to deaths: deaths alone understate the ongoing burden.",
           "Start with the high-rate places (British Columbia, Yukon, Manitoba, Alberta, Saskatchewan: 22 to 36 per 100,000 in 2024), using the same year for every place.",
           "Aim outreach at men aged 30 to 49, the largest group. These are proposals for discussion, not clinical advice."], 310),
       block("how", 20, 525, 610, 130, "How to use this report", [
           "Use the page tabs. Four measures compares the sources; Trend, Provinces and Who go deeper.",
           "Data quality shows who reports what and what I did about missing values.",
           "With nothing chosen, pages show deaths and opioids, and Provinces and Who show 2024. Reset filters clears the slicers."], 320),
       block("about", 650, 525, 610, 130, "About the data and model", [
           "Source: Public Health Agency of Canada, Opioid- and Stimulant-related Harms in Canada (data updated September 2026). Counts and rates only, no individual records.",
           "The file is a flattened export of website charts; I rebuilt it as three fact tables and six dimensions.",
           "2026 covers January to March only, so full years end at 2025."], 400),
       footnote(675, "a Canada total only adds up the places that report. Hospital stays leave out Quebec, and emergency department visits cover 7 of 13 provinces and territories. A suppressed or missing value is never shown as zero.", 500)]
st += footer(ST_H)
pages["start"] = dict(name="Start here", H=ST_H, img="canvas_start.png", visuals=st)

# ---- Trend
tr = header("Counts rose sharply in 2020 and have eased since the 2023 peak", "Quarterly counts for one source and one substance, with the yearly totals underneath.")
tr += [slicer("src", 20, 120, 250, 64, "Dim_Source", "Source", "Source (none = Deaths)", 100, sync="Source"),
       slicer("sub", 280, 120, 280, 64, "Dim_Substance", "Substance", "Substance (none = Opioids)", 101, sync="Substance"),
       reset_button(1140, 132, 120, 40, 150),
       card("headline", 570, 120, 550, 64, "Trend Headline", None, 200, font=(10, NAVY), p=(10, 18, 8, 18))]
tr += kcards(200, [("Latest Quarter Count", "Latest quarter", "=Latest Quarter Text"), ("Quarter YoY %", "Against a year earlier", None),
                   ("Peak Quarter Count", "Highest quarter", "=Peak Quarter Text"), ("Latest Full Year Count", "Latest full year", "=Latest Full Year Text")])
tr += [chart("line", 20, 330, 1240, 330, "lineChart", {"Category": [C("Date", "Date", "Quarter")], "Y": [M("Quarter Count Sel", "Count")]}, 400,
             "Quarterly count, Canada", "Canada here means the places that report for this source. Pick a source and substance above.",
             "Line chart of quarterly counts", objects={"categoryAxis": [{"properties": {"axisType": s("Scalar")}}]}),
       chart("cols", 20, 680, 760, 400, "columnChart", {"Category": [C("Date", "Year Label", "Year")], "Y": [M("Count Sel", "Count")]}, 500,
             "Yearly count", "2026 covers January to March only and is shown in grey.", "Column chart of yearly counts",
             objects={"dataPoint": [fill(NAVY), fill(GREY, by_value("Date", "Year Label", "'2026 (Jan to Mar)'"))]}, labels=True),
       chart("tbl", 800, 680, 460, 400, "tableEx", {"Values": [C("Date", "Year Label", "Year"), M("Count Sel", "Count"), M("Rate Sel", "Rate per 100,000")]}, 600,
             "Yearly count and rate", "EMS has no published rate, so that column stays blank for EMS responses.", "Table of yearly counts and rates",
             objects={"total": [{"properties": {"totals": boolean(False)}}]})]
tr += findings(1100, [("01 · The 2020 jump", "+71.68%", "Opioid deaths rose from 3,602 in 2019 to 6,184 in 2020, the sharpest rise in the series (deaths and opioids chosen)."),
                      ("02 · The peak", "8,083", "Deaths peaked at 8,083 in 2023 and were 5,704 in 2025, 29.43% below the peak."),
                      ("03 · Read with care", "Q1 only", "2026 covers January to March only, so full years end at 2025 and 2026 is shown in grey.")])
tr += [footnote(1270, "counts are for the source and substance chosen above. Canada means only the places that report, and a missing value is never shown as zero.", 810)]
tr += footer(TR_H)
pages["trend"] = dict(name="Trend", H=TR_H, img="canvas_trend.png", visuals=tr)

# ---- Provinces
pv = header("Rates differ several times over between provinces", "The rate per 100,000 for one year, with suppressed and missing values labelled, never shown as zero.")
pv += [slicer("src", 20, 120, 250, 64, "Dim_Source", "Source", "Source (none = Deaths)", 100, sync="Source"),
       slicer("sub", 280, 120, 280, 64, "Dim_Substance", "Substance", "Substance (none = Opioids)", 101, sync="Substance"),
       slicer("yr", 570, 120, 230, 64, "Date", "Year Label", "Year (none = 2024)", 102, sync="Year"), reset_button(1140, 132, 120, 40, 150),
       card("headline", 810, 120, 310, 64, "Showing Text", None, 200, font=(11, NAVY), p=(10, 18, 8, 18))]
pv += kcards(200, [("Canada Rate", "Canada rate per 100,000", "=Canada Rate Sub"), ("Highest Rate", "Highest rate", "=Highest Region"),
                   ("Lowest Rate", "Lowest rate", "=Lowest Region"), ("Regions With Rate", "Regions with a rate", "=Regions With Rate Sub")])
pv += [chart("map", 30, 330, 560, 340, "pivotTable", {"Rows": [C("Dim_Region", "Tile Row Label", "Group")], "Columns": [C("Dim_Region", "Tile Col", "Column")], "Values": [M("Tile Label", "Rate per 100,000")]}, 300,
             "Rate per 100,000: tile map of Canada", "=Rate Available Text", "Tile map of Canada: each province or territory is a tile shaded by its rate",
             objects={"values": [{"properties": {"backColor": field_color("Tile Fill"), "fontColor": field_color("Tile Font"), "fontSize": num(20)},
                                  "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": "_Measures.Tile Label"}}],
                      "grid": [{"properties": {"rowPadding": num(26), "gridVertical": boolean(False), "gridHorizontal": boolean(False)}}],
                      "subTotals": [{"properties": {"rowSubtotals": boolean(False), "columnSubtotals": boolean(False)}}],
                      "columnHeaders": [{"properties": {"fontColor": solid("#FFFFFF"), "backColor": solid("#FFFFFF")}}],
                      "rowHeaders": [{"properties": {"fontColor": solid("#FFFFFF"), "backColor": solid("#FFFFFF")}}]}),
       textbox("legend", 30, 676, 560, 56, [[run("Lighter = lower rate    ", 9, INK2), run("■ ", 12, "#E4ECF3"), run("■ ", 12, "#A9C3D9"), run("■ ", 12, "#5F8FB5"), run("■ ", 12, "#2D5F8A"), run("■ ", 12, "#1B3A5C"),
                                          run("  darker = higher rate    ", 9, INK2), run("■ ", 12, "#E3E3E3"), run("n/a = not reported", 9, INK2)],
                                         [run("Tiles sit roughly where each province is. Colours compare tiles on this page.", 9, INK2)]], 350, p=(6, 14, 8, 14)),
       card("canada", 30, 736, 560, 40, "Canada Rate Text", None, 360, font=(11, NAVY), p=(10, 14, 8, 14)),
       card("extremes", 30, 782, 560, 40, "Tile Extremes", None, 361, font=(11, NAVY), p=(10, 14, 8, 14)),
       chart("tbl", 620, 330, 640, 520, "tableEx", {"Values": [C("Dim_Region", "Region"), M("Count (Focus Year)", "Count"), M("Rate (Focus Year)", "Rate per 100,000"), M("Value Status", "Status")]}, 400,
             "Count, rate and status by region", "Status shows Suppressed or Not available. Regions with no data are left out.",
             "Table of counts, rate and reporting status by region", sort=(mea("Rate (Focus Year)"), "Descending"),
             objects={"total": [{"properties": {"totals": boolean(False)}}]})]
pv += findings(870, [("01 · The highest rates", "35.7", "In 2024 British Columbia had 35.7 deaths per 100,000, then Yukon 29.4, Manitoba 25.0 and Alberta 24.4."),
                     ("02 · The lowest rates", "3.4", "Quebec had 3.4 and Ontario 14.0 per 100,000 in 2024: British Columbia's rate is more than ten times Quebec's."),
                     ("03 · Read with care", "2024 first", "Some 2025 values look provisional (Ontario deaths -37.49%, Quebec +93.14%), so the page opens on 2024.")])
pv += [footnote(1040, "rates are crude, not age-adjusted, and reporting differs by province, so use the ranking to ask questions, not to judge. The Canada rate only adds up the places that report.", 810)]
pv += footer(PR_H)
pages["provinces"] = dict(name="Provinces", H=PR_H, img="canvas_prov.png", visuals=pv)

# ---- Four measures
bu = header("Deaths have fallen faster than ambulance calls", "Opioid deaths, hospital stays, emergency department visits and EMS responses for Canada, side by side.")
bu += [slicer("reg", 20, 120, 300, 64, "Dim_Region", "Region", "Region (blank = Canada)", 100, mode="Dropdown"), reset_button(1140, 132, 120, 40, 150),
       card("headline", 340, 120, 780, 64, "Burden Headline", None, 200, font=(10, NAVY), p=(10, 18, 8, 18))]
bu += kcards(200, [("Deaths Latest Quarter YoY %", "Deaths vs a year earlier", "=Latest Quarter Text"),
                   ("Hosp Latest Quarter YoY %", "Hospital stays vs a year earlier", "=Latest Quarter Text"),
                   ("ED Latest Quarter YoY %", "ED visits vs a year earlier", "=Latest Quarter Text"),
                   ("EMS Latest Quarter YoY %", "EMS responses vs a year earlier", "=Latest Quarter Text")])
bu += [chart("idx", 20, 330, 610, 430, "lineChart", {"Category": [C("Date", "Year")], "Y": [M("Index 2019", "Index (2019 = 100)")], "Series": [C("Dim_Source", "Source")]}, 300,
             "Opioid counts, indexed to 2019", "Each line starts at 100 in 2019. Full years only.", "Line chart of opioid counts indexed to 2019 by source",
             objects={"legend": [{"properties": {"show": boolean(True), "position": s("Bottom")}}], "categoryAxis": [{"properties": {"axisType": s("Scalar")}}]}),
       chart("tbl", 650, 330, 610, 430, "tableEx", {"Values": [C("Date", "Year Label", "Year"), M("Deaths (Opioids)", "Deaths"), M("Hospital stays (Opioids)", "Hospital stays"),
                                                             M("ED Visits (Opioids)", "ED visits"), M("EMS Responses (Opioids)", "EMS responses"), M("Hosp per Death (Year)", "Stays per death")]}, 400,
             "Opioid counts by year", "ED visits and hospital stays cover only the places that report each year.", "Table of opioid counts by year and source",
             objects={"total": [{"properties": {"totals": boolean(False)}}]})]
bu += findings(780, [("01 · Against the peak", "-29.43%", "Opioid deaths are 29.43% below their 2023 peak, hospital stays 21.75% and ED visits 28.51% below theirs, but EMS responses only 7.84%."),
                     ("02 · The latest quarter", "+60.93%", "In 2026 Q1 EMS responses were 60.93% above a year earlier and hospital stays 13.55% above, while deaths were 5.31% below."),
                     ("03 · Read with care", "Direction", "The four sources count different things and cover different places, so compare their direction, not their size.")])
bu += [footnote(950, "the sources count a death, a hospital stay, a visit and an ambulance call. The EMS rise in 2026 comes mostly from British Columbia and Winnipeg and may reflect how services record calls.", 810)]
bu += footer(BU_H)
pages["burden"] = dict(name="Four measures", H=BU_H, img="canvas_burden.png", visuals=bu)

# ---- Who
wh = header("Seven in ten deaths are men, and half are aged 30 to 49", "Counts by age group and sex for one source, substance and year.")
wh += [slicer("src", 20, 120, 230, 64, "Dim_Source", "Source", "Source (none = Deaths)", 100, sync="Source"),
       slicer("sub", 260, 120, 260, 64, "Dim_Substance", "Substance", "Substance (none = Opioids)", 101, sync="Substance"),
       slicer("yr", 530, 120, 230, 64, "Date", "Year Label", "Year (none = 2024)", 102, sync="Year"),
       slicer("reg", 770, 120, 260, 64, "Dim_Region", "Region", "Region (blank = Canada)", 103), reset_button(1050, 132, 120, 40, 150)]
wh += kcards(200, [("Male Share", "Male share", "=Showing Text"), ("Age 30 to 49 Share", "Aged 30 to 49", "=Showing Text"),
                   ("Age Share of Total", "With age and sex shown", None), ("Age Count (Focus Year)", "Deaths or cases shown", "=Showing Text")])
wh += [chart("heat", 20, 330, 740, 380, "pivotTable", {"Rows": [C("Dim_Age", "Age group")], "Columns": [C("Dim_HeatYear", "Heat Year", "Year")], "Values": [M("Heat Count", "Count")]}, 300,
             "Heat map: count by age group and year", "Darker means more. All years for the chosen source and substance. 2026 Q1 is January to March only.",
             "Matrix of counts by age group and year",
             objects={"values": [{"properties": {"backColor": field_color("Heat Fill"), "fontColor": field_color("Heat Font"), "fontSize": num(15)},
                                  "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": "_Measures.Heat Count"}}],
                      "grid": [{"properties": {"rowPadding": num(7)}}],
                      "columnHeaders": [{"properties": {"fontSize": num(14)}}], "rowHeaders": [{"properties": {"fontSize": num(14)}}],
                      "subTotals": [{"properties": {"rowSubtotals": boolean(False), "columnSubtotals": boolean(False)}}]}),
       textbox("insight", 20, 720, 740, 60, [[run("What it shows:  ", 9.5, INK, True), run("every age group roughly doubled from 2019 to 2021, ages 30 to 39 are highest in every year, and counts have fallen since 2023.", 9.5, INK2)]], 310, p=(12, 16, 6, 16)),
       chart("tbl", 780, 330, 480, 450, "tableEx", {"Values": [C("Dim_Age", "Age group"), C("Dim_Sex", "Sex"), M("Age Count (Focus Year)", "Count"), M("Share of Group", "Share of total")]}, 400,
             "Count and share by age group and sex", "Blank means suppressed or not available, not zero.", "Table of counts and shares by age group and sex",
             objects={"total": [{"properties": {"totals": boolean(False)}}]})]
wh += findings(800, [("01 · Men", "71.64%", "In 2024, 71.64% of opioid deaths were men (deaths and opioids chosen)."),
                     ("02 · Aged 30 to 49", "52.58%", "52.58% of opioid deaths in 2024 were aged 30 to 49, the largest group."),
                     ("03 · Read with care", "98.73%", "The age and sex split covers 98.73% of 2024 deaths and 91.09% of 2025. The rest is suppressed.")])
wh += [footnote(970, "PHAC suppresses small counts, so age and sex cells add up to less than the total. Smaller regions show many blank cells. Sex is reported as male or female only.", 810)]
wh += footer(WH_H)
pages["who"] = dict(name="Who", H=WH_H, img="canvas_who.png", visuals=wh)


# ---- Data quality
dq = header("Before any analysis: what each number in the file means", "Who reports what, how much is missing, and what I did about it.")
dq += [chart("cov", 20, 130, 720, 540, "pivotTable", {"Rows": [C("Dim_Region", "Region")], "Columns": [C("Dim_Source", "Source")], "Values": [M("Coverage Status", "Status")]}, 300,
             "Who reports what: opioid counts, 2024", "Teal = reported, amber = suppressed (small count), grey = not available, white = not in this source.",
             "Matrix showing which regions report which source",
             objects={"values": [{"properties": {"backColor": field_color("Coverage Fill"), "fontColor": field_color("Coverage Font"), "fontSize": num(10)},
                                  "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": "_Measures.Coverage Status"}}],
                      "grid": [{"properties": {"rowPadding": num(3)}}],
                      "subTotals": [{"properties": {"rowSubtotals": boolean(False), "columnSubtotals": boolean(False)}}]}),
       block("found", 760, 130, 500, 300, "What I found in the file and what I did", [
           "34,890 rows and 39 columns, with English and French copies of every label. It is a chart export, not a table, so I rebuilt it as three tables (yearly, quarterly, age and sex).",
           "62.08% of values are numbers (5.11% are real zeros), 24.82% are blank (not available) and 13.09% are suppressed. I keep each kind separate and never show missing as zero.",
           "A Canada total adds up only the places that report: hospital stays leave out Quebec and emergency department visits cover 7 of 13 provinces and territories.",
           "Quarters add up to as much as 1.57% less than the published year, so I never build a year from quarters.",
           "2026 covers January to March only. Some 2025 values look provisional (Ontario deaths -37.49%, Quebec +93.14%), so I compare provinces on 2024.",
           "Checks: no duplicate keys, Canada totals reconciled to the places that report, and every headline number checked against a separate Python calculation."], 400),
       block("terms", 760, 445, 500, 225, "Terms in plain language", [
           "Crude rate: cases per 100,000 people living in that place, not adjusted for age.",
           "Suppressed: the agency hides small counts to protect privacy, so the true value is unknown, not zero.",
           "Not available: the source does not publish this value for that place or period.",
           "Hospital stay: a patient admitted to hospital. Emergency department visit: seen in the emergency room. EMS response: an ambulance call.",
           "Index (2019 = 100): each value divided by that source's 2019 value, so sources of different size can be compared.",
           "Provisional: the newest figures can be revised, so treat the latest year with care."], 410)]
dq += footer(QU_H)
pages["quality"] = dict(name="Data quality", H=QU_H, img="canvas_quality.png", visuals=dq)


# ---------------------------------------------------------------- theme
def sol(c): return {"solid": {"color": c}}


theme = {"name": "Opioid Harms Portfolio", "dataColors": [NAVY, TEAL, AMBER, GREY, "#6B4C7A", "#B23A48", "#4F6D7A", LIGHT],
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
                                                 "pageOrder": ["start", "burden", "trend", "provinces", "who", "quality"], "activePageName": "start"})
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
    "options": {"suppressActiveSection": True, "suppressDisplay": True}, "explorationState": {"version": "1.3", "activeSection": "trend", "sections": sections}})
wjson(os.path.join(DEF, "bookmarks", "bookmarks.json"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json", "items": [{"name": "reset_filters"}]})
print("built", {k: len(v["visuals"]) for k, v in pages.items()}, "measures:", len(MEASURES))
