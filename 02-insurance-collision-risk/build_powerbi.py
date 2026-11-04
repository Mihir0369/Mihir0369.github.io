"""Generate the Power BI project (PBIP: TMDL model + PBIR report) for the collision-risk case study.

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
NAME = "collision-risk"
MODEL_DIR = os.path.join(OUT, NAME + ".SemanticModel")
REPORT_DIR = os.path.join(OUT, NAME + ".Report")
DEF = os.path.join(REPORT_DIR, "definition")
RES = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources")
TMDL = os.path.join(MODEL_DIR, "definition")
MODEL_FOLDER = os.path.join(HERE, "model")          # the CSVs the model reads (parameter ModelFolder)
THEME_NAME = "CollisionRiskPortfolio.json"

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
for d in (os.path.join(TMDL, "tables"), os.path.join(TMDL, "cultures"), RES, os.path.join(DEF, "pages"), os.path.join(DEF, "bookmarks")):
    os.makedirs(d, exist_ok=True)


def tag(name):  # stable lineage tags
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "collision-risk/" + name))


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def wjson(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


# =====================================================================================
# SEMANTIC MODEL: a star schema (two fact tables, fifteen dimensions, a date table),
# two field parameters, a calculation group and a measures table.
# =====================================================================================
write(os.path.join(MODEL_DIR, "definition.pbism"), json.dumps(
    {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
     "version": "4.2", "settings": {}}, indent=2))
wjson(os.path.join(MODEL_DIR, ".platform"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "SemanticModel", "displayName": NAME}, "config": {"version": "2.0", "logicalId": tag("model")}})
write(os.path.join(TMDL, "database.tmdl"), "database\n\tcompatibilityLevel: 1606\n")

DIM_TABLES = ["Dim_Hour", "Dim_Weekday", "Dim_Severity", "Dim_Weather", "Dim_RoadSurface", "Dim_RoadAlignment", "Dim_RoadLayout", "Dim_TrafficControl",
              "Dim_CollisionType", "Dim_RoadUser", "Dim_Safety", "Dim_AgeBand", "Dim_Sex", "Dim_Vehicle", "Dim_PersonSeverity"]
model_refs = ["fact_collision", "fact_person", "Date"] + DIM_TABLES + ["'Time Comparison'", "DQ_Field", "Scenario", "Uptake", "_Measures"]
write(os.path.join(TMDL, "model.tmdl"), """model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-CA
\tdiscourageImplicitMeasures
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation PBI_QueryOrder = ["fact_collision","fact_person","ModelFolder"]

annotation __PBI_TimeIntelligenceEnabled = 1

annotation PBI_ProTooling = ["DevMode"]

%s

ref cultureInfo en-US
""" % "\n".join("ref table " + t for t in model_refs))
write(os.path.join(TMDL, "cultures", "en-US.tmdl"), "cultureInfo en-US\n")
write(os.path.join(TMDL, "expressions.tmdl"),
      'expression ModelFolder = "%s" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]\n'
      "\tlineageTag: %s\n\n\tannotation PBI_ResultType = Text\n" % (MODEL_FOLDER.replace("/", "\\"), tag("param")))

REL = [("collision_to_date", "fact_collision.month_start", "Date.Date"),
       ("collision_to_weekday", "fact_collision.weekday_key", "Dim_Weekday.'Weekday Key'"),
       ("collision_to_hour", "fact_collision.hour_key", "Dim_Hour.'Hour Key'"),
       ("collision_to_severity", "fact_collision.severity_key", "Dim_Severity.'Severity Key'"),
       ("collision_to_weather", "fact_collision.weather_key", "Dim_Weather.'Weather Key'"),
       ("collision_to_surface", "fact_collision.surface_key", "Dim_RoadSurface.'Surface Key'"),
       ("collision_to_alignment", "fact_collision.alignment_key", "Dim_RoadAlignment.'Alignment Key'"),
       ("collision_to_layout", "fact_collision.layout_key", "Dim_RoadLayout.'Layout Key'"),
       ("collision_to_traffic", "fact_collision.traffic_key", "Dim_TrafficControl.'Traffic Key'"),
       ("collision_to_type", "fact_collision.type_key", "Dim_CollisionType.'Type Key'"),
       ("person_to_collision", "fact_person.collision_id", "fact_collision.collision_id"),
       ("person_to_age", "fact_person.age_key", "Dim_AgeBand.'Age Key'"),
       ("person_to_user", "fact_person.user_key", "Dim_RoadUser.'User Key'"),
       ("person_to_safety", "fact_person.safety_key", "Dim_Safety.'Safety Key'"),
       ("person_to_sex", "fact_person.sex_key", "Dim_Sex.'Sex Key'"),
       ("person_to_vehicle", "fact_person.vehicle_key", "Dim_Vehicle.'Vehicle Key'"),
       ("person_to_severity", "fact_person.person_severity_key", "Dim_PersonSeverity.'Person Severity Key'")]
write(os.path.join(TMDL, "relationships.tmdl"), "\n".join("relationship %s\n\tfromColumn: %s\n\ttoColumn: %s\n" % r for r in REL))


def q(name):
    return name if name.replace("_", "").isalnum() else "'%s'" % name


def col(name, dtype, fmt=None, hidden=True, extra="", sort=None):
    lines = ["\tcolumn %s" % q(name), "\t\tdataType: %s" % dtype]
    if hidden:
        lines.append("\t\tisHidden")
    if fmt:
        lines.append("\t\tformatString: %s" % fmt)
    lines += ["\t\tlineageTag: %s" % tag("col/" + name + extra), "\t\tsummarizeBy: none", "\t\tsourceColumn: %s" % name]
    if sort:
        lines.append("\t\tsortByColumn: %s" % q(sort))
    lines.append("")
    return "\n".join(lines)


def m_csv(fname, ncols, types, rename=None):
    """Power Query for a CSV: read, promote headers, set types, optionally rename columns."""
    steps = ['let',
             '    Source = Csv.Document(File.Contents(ModelFolder & "\\%s"), [Delimiter = ",", Columns = %d, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),' % (fname, ncols),
             '    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),',
             '    Typed = Table.TransformColumnTypes(Promoted, {%s}, "en-US")' % ", ".join('{"%s", %s}' % t for t in types)]
    last = "Typed"
    if rename:
        steps[-1] += ","
        steps.append('    Renamed = Table.RenameColumns(Typed, {%s})' % ", ".join('{"%s", "%s"}' % r for r in rename))
        last = "Renamed"
    steps += ["in", "    " + last]
    return "\n".join("\t\t\t\t" + x for x in steps)


def write_table(tname, cols, partition_m, extra_blocks="", props=""):
    write(os.path.join(TMDL, "tables", tname + ".tmdl"),
          "table %s\n\tlineageTag: %s\n%s\n%s\n%s\tpartition %s = m\n\t\tmode: import\n\t\tsource =\n%s\n\n\tannotation PBI_ResultType = Table\n"
          % (q(tname), tag("table/" + tname), props, cols, extra_blocks, q(tname), partition_m))


def hierarchy(name, levels):
    out = ["\thierarchy %s" % q(name), "\t\tlineageTag: %s" % tag("h/" + name)]
    for lv in levels:
        out += ["\t\tlevel %s" % q(lv), "\t\t\tlineageTag: %s" % tag("h/" + name + "/" + lv), "\t\t\tcolumn: %s" % q(lv)]
    return "\n".join(out) + "\n\n"


def dim(tname, fname, cols, hier=None, sorts=None):
    """cols: [(csv column, display name, dtype)]; the first is the integer key and is hidden."""
    sorts = sorts or {}
    text = "\n".join(col(disp, dt, "0" if dt == "int64" else None, hidden=(i == 0), sort=sorts.get(disp)) for i, (_, disp, dt) in enumerate(cols))
    types = [(c_, "Int64.Type" if dt == "int64" else "type text") for c_, _, dt in cols]
    write_table(tname, text, m_csv(fname, len(cols), types, rename=[(c_, d_) for c_, d_, _ in cols]), extra_blocks=hierarchy(*hier) if hier else "")


dim("Dim_Hour", "dim_hour.csv", [("hour_key", "Hour Key", "int64"), ("hour_label", "Hour Label", "string"), ("day_part", "Day Part", "string")],
    hier=("Hour Hierarchy", ["Day Part", "Hour Label"]), sorts={"Hour Label": "Hour Key"})
dim("Dim_Weekday", "dim_weekday.csv", [("weekday_key", "Weekday Key", "int64"), ("weekday", "Weekday", "string"), ("week_part", "Week Part", "string")], sorts={"Weekday": "Weekday Key"})
dim("Dim_Severity", "dim_severity.csv", [("severity_key", "Severity Key", "int64"), ("severity", "Severity", "string")])
dim("Dim_Weather", "dim_weather.csv", [("weather_key", "Weather Key", "int64"), ("weather", "Weather", "string"), ("weather_group", "Weather Group", "string")],
    hier=("Weather Hierarchy", ["Weather Group", "Weather"]))
dim("Dim_RoadSurface", "dim_surface.csv", [("surface_key", "Surface Key", "int64"), ("road_surface", "Road Surface", "string"), ("surface_group", "Surface Group", "string")],
    hier=("Surface Hierarchy", ["Surface Group", "Road Surface"]))
dim("Dim_RoadAlignment", "dim_alignment.csv", [("alignment_key", "Alignment Key", "int64"), ("road_alignment", "Road Alignment", "string"), ("alignment_group", "Alignment Group", "string")],
    hier=("Alignment Hierarchy", ["Alignment Group", "Road Alignment"]))
dim("Dim_RoadLayout", "dim_layout.csv", [("layout_key", "Layout Key", "int64"), ("road_layout", "Road Layout", "string"), ("layout_group", "Layout Group", "string")],
    hier=("Layout Hierarchy", ["Layout Group", "Road Layout"]))
dim("Dim_TrafficControl", "dim_traffic.csv", [("traffic_key", "Traffic Key", "int64"), ("traffic_control", "Traffic Control", "string")])
dim("Dim_CollisionType", "dim_collision_type.csv", [("type_key", "Type Key", "int64"), ("collision_type", "Collision Type", "string"), ("collision_group", "Collision Group", "string")],
    hier=("Collision Hierarchy", ["Collision Group", "Collision Type"]))
dim("Dim_RoadUser", "dim_road_user.csv", [("user_key", "User Key", "int64"), ("road_user", "Road User", "string")])
dim("Dim_Safety", "dim_safety.csv", [("safety_key", "Safety Key", "int64"), ("safety_device", "Safety Device", "string"), ("protection", "Protection", "string")],
    hier=("Protection Hierarchy", ["Protection", "Safety Device"]))
dim("Dim_AgeBand", "dim_age_band.csv", [("age_key", "Age Key", "int64"), ("age_band", "Age Band", "string")], sorts={"Age Band": "Age Key"})
dim("Dim_Sex", "dim_sex.csv", [("sex_key", "Sex Key", "int64"), ("sex", "Sex", "string")])
dim("Dim_Vehicle", "dim_vehicle.csv", [("vehicle_key", "Vehicle Key", "int64"), ("vehicle_type", "Vehicle Type", "string"), ("vehicle_group", "Vehicle Group", "string")],
    hier=("Vehicle Hierarchy", ["Vehicle Group", "Vehicle Type"]))
dim("Dim_PersonSeverity", "dim_person_severity.csv", [("person_severity_key", "Person Severity Key", "int64"), ("person_severity", "Person Severity", "string")])

# ---- fact tables: keys and counts only
FACT_C = [("collision_id", "string"), ("year", "int64"), ("month_start", "date"), ("weekday_key", "int64"), ("hour_key", "int64"), ("severity_key", "int64"), ("weather_key", "int64"),
          ("surface_key", "int64"), ("alignment_key", "int64"), ("layout_key", "int64"), ("traffic_key", "int64"), ("type_key", "int64"),
          ("vehicles", "int64"), ("people", "int64"), ("killed", "int64"), ("injured", "int64")]
write_table("fact_collision", "\n".join(col(n, "dateTime" if dt == "date" else dt, "Long Date" if dt == "date" else ("0" if dt == "int64" else None)) for n, dt in FACT_C),
            m_csv("fact_collision.csv", len(FACT_C), [(n, "type date" if dt == "date" else ("Int64.Type" if dt == "int64" else "type text")) for n, dt in FACT_C]))
FACT_P = [("collision_id", "string"), ("age", "int64"), ("age_key", "int64"), ("user_key", "int64"), ("safety_key", "int64"), ("sex_key", "int64"), ("vehicle_key", "int64"), ("person_severity_key", "int64")]
write_table("fact_person", "\n".join(col(n, dt, "0" if dt == "int64" else None) for n, dt in FACT_P),
            m_csv("fact_person.csv", len(FACT_P), [(n, "Int64.Type" if dt == "int64" else "type text") for n, dt in FACT_P]))


def calc_table(tname, columns, source, extra_props=""):
    cols = "\n".join(c for c in columns)
    write(os.path.join(TMDL, "tables", tname + ".tmdl"),
          "table %s\n\tlineageTag: %s\n%s\n%s\n\tpartition %s = calculated\n\t\tmode: import\n\t\tsource =\n%s\n"
          % (q(tname), tag("table/" + tname), extra_props, cols, q(tname), "\n".join("\t\t\t\t" + x for x in source.split("\n"))))


def ccol(name, dtype=None, fmt=None, hidden=False, sort=None, key=False):
    lines = ["\tcolumn %s" % q(name)]
    if key: lines.append("\t\tisKey")
    if dtype: lines.append("\t\tdataType: %s" % dtype)
    if hidden: lines.append("\t\tisHidden")
    if fmt: lines.append("\t\tformatString: %s" % fmt)
    lines += ["\t\tlineageTag: %s" % tag("ccol/" + name + str(sort)), "\t\tsummarizeBy: none", "\t\tsourceColumn: [%s]" % name]
    if sort: lines.append("\t\tsortByColumn: '%s'" % sort)
    return "\n".join(lines) + "\n"


def datatable(rows, cols):
    head = ",\n".join('    "%s", %s' % c for c in cols)
    body = ",\n".join("        { " + ", ".join(('"%s"' % v) if isinstance(v, str) else str(v) for v in r) + " }" for r in rows)
    return "DATATABLE (\n%s,\n    {\n%s\n    }\n)" % (head, body)


calc_table("Date", [ccol("Date", "dateTime", "Long Date", key=True), ccol("Year", "int64", "0"), ccol("Year Label"), ccol("Month Number", "int64", "0"),
                    ccol("Month", sort="Month Number"), ccol("Year Month")],
           'ADDCOLUMNS (\n    CALENDAR ( DATE ( 2019, 1, 1 ), DATE ( 2020, 12, 31 ) ),\n    "Year", YEAR ( [Date] ),\n    "Year Label", FORMAT ( YEAR ( [Date] ), "0" ),\n'
           '    "Month Number", MONTH ( [Date] ),\n    "Month", FORMAT ( [Date], "mmm" ),\n    "Year Month", FORMAT ( [Date], "yyyy-mm" )\n)',
           "\tdataCategory: Time\n")
DQ_FIELDS = ["Collision type", "Traffic control", "Road alignment", "Road surface", "Weather", "Time of day", "Safety device", "Age band"]
calc_table("DQ_Field", [ccol("Field", sort="Sort Order"), ccol("Sort Order", "int64", "0", hidden=True)],
           datatable([(f_, i + 1) for i, f_ in enumerate(DQ_FIELDS)], [("Field", "STRING"), ("Sort Order", "INTEGER")]))


# ---- field parameters: the reader picks the breakdown and the measure
def field_parameter(tname, items):
    """items: [(label, DAX reference passed to NAMEOF)]"""
    rows = ",\n".join('\t\t\t\t    ("%s", NAMEOF ( %s ), %d)' % (lab, ref, i) for i, (lab, ref) in enumerate(items))
    write(os.path.join(TMDL, "tables", tname + ".tmdl"), """table '%(t)s'
\tlineageTag: %(a)s

\tcolumn '%(t)s'
\t\tlineageTag: %(b)s
\t\tsummarizeBy: none
\t\tsourceColumn: [Value1]
\t\tsortByColumn: '%(t)s Order'

\t\trelatedColumnDetails
\t\t\tgroupByColumn: '%(t)s Fields'

\tcolumn '%(t)s Fields'
\t\tisHidden
\t\tlineageTag: %(c)s
\t\tsummarizeBy: none
\t\tsourceColumn: [Value2]
\t\tsortByColumn: '%(t)s Order'

\t\textendedProperty ParameterMetadata =
\t\t\t\t{
\t\t\t\t  "version": 3,
\t\t\t\t  "kind": 2
\t\t\t\t}

\tcolumn '%(t)s Order'
\t\tisHidden
\t\tformatString: 0
\t\tlineageTag: %(d)s
\t\tsummarizeBy: sum
\t\tsourceColumn: [Value3]

\tpartition '%(t)s' = calculated
\t\tmode: import
\t\tsource =
\t\t\t\t{
%(rows)s
\t\t\t\t}
""" % {"t": tname, "a": tag("table/" + tname), "b": tag(tname + "/1"), "c": tag(tname + "/2"), "d": tag(tname + "/3"), "rows": rows})


PARAM_FIELDS = [("Traffic control", "'Dim_TrafficControl'[Traffic Control]"), ("Road surface", "'Dim_RoadSurface'[Road Surface]"),
                ("Road alignment", "'Dim_RoadAlignment'[Road Alignment]"), ("Weather", "'Dim_Weather'[Weather]"), ("Road layout", "'Dim_RoadLayout'[Road Layout]"),
                ("Collision group", "'Dim_CollisionType'[Collision Group]"), ("Time of day", "'Dim_Hour'[Day Part]"), ("Weekday or weekend", "'Dim_Weekday'[Week Part]")]

calc_table("Scenario", [ccol("Intervention"), ccol("Key", "int64", "0", hidden=True)],
           datatable([("Add traffic control", 1), ("Treat curved roads", 2), ("Night as safe as midday", 3)], [("Intervention", "STRING"), ("Key", "INTEGER")]))
calc_table("Uptake", [ccol("Uptake", "double", "0%")], 'SELECTCOLUMNS ( GENERATESERIES ( 0, 1, 0.1 ), "Uptake", ROUND ( [Value], 1 ) )')

# ---- calculation group: a time comparison that works on any measure
_PY = "CALCULATE ( SELECTEDMEASURE (), SAMEPERIODLASTYEAR ( 'Date'[Date] ) )"
write(os.path.join(TMDL, "tables", "Time Comparison.tmdl"), """table 'Time Comparison'
\tlineageTag: %(a)s

\tcalculationGroup

\t\tcalculationItem Current = SELECTEDMEASURE ()
\t\t\tordinal: 0

\t\tcalculationItem 'Prior year' = %(py)s
\t\t\tordinal: 1

\t\tcalculationItem 'Change vs prior year' = IF ( ISBLANK ( %(py)s ), BLANK (), SELECTEDMEASURE () - %(py)s )
\t\t\tordinal: 2

\t\tcalculationItem '%% change' = IF ( ISBLANK ( %(py)s ), BLANK (), DIVIDE ( SELECTEDMEASURE () - %(py)s, %(py)s ) )
\t\t\tordinal: 3
\t\t\tformatStringDefinition = "+0.00%%;-0.00%%;0.00%%"

\tcolumn 'Time Comparison'
\t\tdataType: string
\t\tlineageTag: %(b)s
\t\tsummarizeBy: none
\t\tsourceColumn: Name
\t\tsortByColumn: Ordinal

\tcolumn Ordinal
\t\tdataType: int64
\t\tformatString: 0
\t\tisHidden
\t\tlineageTag: %(c)s
\t\tsummarizeBy: sum
\t\tsourceColumn: Ordinal

\tpartition 'Time Comparison' = calculationGroup
\t\tmode: import
""" % {"a": tag("table/TimeComparison"), "b": tag("tc/1"), "c": tag("tc/2"), "py": _PY})

# ---------------------------------------------------------------- measures
UNK = "Unknown or not reported"
NIGHT = 'Dim_Hour[Day Part] = "Night (10 pm to 6 am)"'
KNOWN_DAY = 'NOT ( Dim_Hour[Day Part] IN { "Night (10 pm to 6 am)", "%s" } )' % UNK
OCC = 'Dim_RoadUser[Road User] IN { "Driver", "Passenger" }'
UNRESTRAINED = 'Dim_Safety[Safety Device] = "No safety device used"'
RESTRAINED = 'Dim_Safety[Safety Device] = "Safety device used"'
RISKY = 'FILTER ( ADDCOLUMNS ( FILTER ( ALL ( Dim_Hour[Hour Key] ), Dim_Hour[Hour Key] > 0 && [Collisions] >= 500 ), "s", [Fatal Share] ), NOT ISBLANK ( [s] ) )'


def yr(expr, y):
    return "CALCULATE ( %s, REMOVEFILTERS ( 'Date' ), fact_collision[year] = %d )" % (expr, y)


MEASURES = [
    ("Collisions", "COUNTROWS ( fact_collision )", "#,0"),
    ("Fatal Collisions", 'CALCULATE ( [Collisions], Dim_Severity[Severity] = "Fatal" )', "#,0"),
    ("Injury Collisions", 'CALCULATE ( [Collisions], Dim_Severity[Severity] = "Injury" )', "#,0"),
    ("Fatal Share", "DIVIDE ( [Fatal Collisions], [Collisions] )", "0.00%"),
    ("Overall Fatal Share", "CALCULATE ( [Fatal Share], REMOVEFILTERS () )", "0.00%"),
    ("Share vs Average", "DIVIDE ( [Fatal Share], [Overall Fatal Share] )", '0.00"×"'),
    ("People Killed", "SUM ( fact_collision[killed] )", "#,0"),
    ("People Injured", "SUM ( fact_collision[injured] )", "#,0"),
    ("People Involved", "COUNTROWS ( fact_person )", "#,0"),
    ("Collisions Sub", 'FORMAT ( [Fatal Collisions], "#,0" ) & " fatal, " & FORMAT ( [Injury Collisions], "#,0" ) & " injury"', None),
    ("Fatal Sub", '"All-collision average is " & FORMAT ( [Overall Fatal Share], "0.00%" )', None),
    # time of day and week
    ("Heat Share", "IF ( SELECTEDVALUE ( Dim_Hour[Hour Key], 0 ) = 0, BLANK (), IF ( [Collisions] >= 100, [Fatal Share], BLANK () ) )", "0.00%"),
    ("Heat Index", "DIVIDE ( [Heat Share], [Overall Fatal Share] )", "0.00"),
    ("Heat Fill", 'VAR k = [Heat Index] RETURN IF ( ISBLANK ( k ), BLANK (), SWITCH ( TRUE (), k < 0.75, "#FFF4DC", k < 1.5, "#FBD9A0", k < 2.5, "#F4B860", k < 4, "#E08A1E", "#B85C00" ) )', None),
    ("Heat Font", 'VAR k = [Heat Index] RETURN IF ( ISBLANK ( k ), BLANK (), IF ( k < 2.5, "#1F2D3D", "#FFFFFF" ) )', None),
    ("Riskiest Hour Key", "VAR t = %s RETURN CALCULATE ( MAXX ( TOPN ( 1, t, [s], DESC ), Dim_Hour[Hour Key] ), REMOVEFILTERS ( Dim_Hour ) )" % RISKY, "0"),
    ("Riskiest Hour Share", "VAR t = %s RETURN CALCULATE ( MAXX ( TOPN ( 1, t, [s], DESC ), [s] ), REMOVEFILTERS ( Dim_Hour ) )" % RISKY, "0.00%"),
    ("Riskiest Hour Label", "VAR k = [Riskiest Hour Key] RETURN LOOKUPVALUE ( Dim_Hour[Hour Label], Dim_Hour[Hour Key], k )", None),
    ("Riskiest Hour Text", '"At " & [Riskiest Hour Label] & ". Average is " & FORMAT ( [Overall Fatal Share], "0.00%" )', None),
    ("Night Fatal Share", "CALCULATE ( [Fatal Share], %s )" % NIGHT, "0.00%"),
    ("Day Fatal Share", "CALCULATE ( [Fatal Share], %s )" % KNOWN_DAY, "0.00%"),
    ("Night Collision Share", "DIVIDE ( CALCULATE ( [Collisions], %s ), CALCULATE ( [Collisions], Dim_Hour[Hour Key] <> 0 ) )" % NIGHT, "0.00%"),
    ("Night Fatal Collision Share", "DIVIDE ( CALCULATE ( [Fatal Collisions], %s ), CALCULATE ( [Fatal Collisions], Dim_Hour[Hour Key] <> 0 ) )" % NIGHT, "0.00%"),
    ("Night Sub", '"Day (6 am to 10 pm) is " & FORMAT ( [Day Fatal Share], "0.00%" )', None),
    ("Night Share Sub", '"From " & FORMAT ( [Night Collision Share], "0.00%" ) & " of all collisions"', None),
    ("When Headline", '"Fatal collisions peak between midnight and 5 am: " & FORMAT ( [Night Fatal Share], "0.00%" ) & " at night against " & FORMAT ( [Day Fatal Share], "0.00%" ) & " by day."', None),
    ("Night Times Day", "DIVIDE ( [Night Fatal Share], [Day Fatal Share] )", '0.00"×"'),
    ("Day Sub", '"6 am to 10 pm, " & FORMAT ( CALCULATE ( [Collisions], %s ), "#,0" ) & " collisions"' % KNOWN_DAY, None),
    ("Night Times Sub", '"Night is " & FORMAT ( [Night Times Day], "0.00" ) & " times as likely to be fatal"', None),
    ("Hour Bar Color", 'IF ( SELECTEDVALUE ( Dim_Hour[Day Part] ) = "Night (10 pm to 6 am)", "#C77700", "#7A93AB" )', None),
    # time intelligence: 2020 against 2019, month by month
    ("Collisions Dated", "IF ( ISBLANK ( MAX ( 'Date'[Date] ) ), BLANK (), [Collisions] )", "#,0"),
    ("Fatal Share Dated", "IF ( ISBLANK ( MAX ( 'Date'[Date] ) ), BLANK (), [Fatal Share] )", "0.00%"),
    ("Collisions PY", "CALCULATE ( [Collisions], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )", "#,0"),
    ("Collisions YoY Change", "IF ( ISBLANK ( [Collisions PY] ), BLANK (), [Collisions] - [Collisions PY] )", "+#,0;-#,0;0"),
    ("Collisions YoY %", "IF ( ISBLANK ( [Collisions PY] ), BLANK (), DIVIDE ( [Collisions] - [Collisions PY], [Collisions PY] ) )", "+0.00%;-0.00%;0.00%"),
    ("Collisions 2019", yr("[Collisions]", 2019), "#,0"),
    ("Collisions 2020", yr("[Collisions]", 2020), "#,0"),
    ("Fatal 2019", yr("[Fatal Collisions]", 2019), "#,0"),
    ("Fatal 2020", yr("[Fatal Collisions]", 2020), "#,0"),
    ("Collisions Change", "DIVIDE ( [Collisions 2020] - [Collisions 2019], [Collisions 2019] )", "+0.00%;-0.00%;0.00%"),
    ("Fatal Change", "DIVIDE ( [Fatal 2020] - [Fatal 2019], [Fatal 2019] )", "+0.00%;-0.00%;0.00%"),
    ("Fatal Share 2019", yr("[Fatal Share]", 2019), "0.00%"),
    ("Fatal Share 2020", yr("[Fatal Share]", 2020), "0.00%"),
    ("Fatal Index", "VAR py = CALCULATE ( [Fatal Collisions], SAMEPERIODLASTYEAR ( 'Date'[Date] ) ) RETURN IF ( ISBLANK ( py ) || ISBLANK ( MAX ( 'Date'[Date] ) ), BLANK (), DIVIDE ( [Fatal Collisions], py ) * 100 )", "0"),
    ("Injury Index", "VAR py = CALCULATE ( [Injury Collisions], SAMEPERIODLASTYEAR ( 'Date'[Date] ) ) RETURN IF ( ISBLANK ( py ) || ISBLANK ( MAX ( 'Date'[Date] ) ), BLANK (), DIVIDE ( [Injury Collisions], py ) * 100 )", "0"),
    ("Coll Change Sub", 'FORMAT ( [Collisions 2019], "#,0" ) & " in 2019 to " & FORMAT ( [Collisions 2020], "#,0" ) & " in 2020"', None),
    ("Fatal Change Sub", 'FORMAT ( [Fatal 2019], "#,0" ) & " in 2019 to " & FORMAT ( [Fatal 2020], "#,0" ) & " in 2020"', None),
    ("Fatal Share 2020 Sub", '"Up " & FORMAT ( ( [Fatal Share 2020] - [Fatal Share 2019] ) * 100, "0.00" ) & " percentage points from " & FORMAT ( [Fatal Share 2019], "0.00%" ) & " in 2019"', None),
    ("Injury 2019", yr("[Injury Collisions]", 2019), "#,0"),
    ("Injury 2020", yr("[Injury Collisions]", 2020), "#,0"),
    ("Injury Change", "DIVIDE ( [Injury 2020] - [Injury 2019], [Injury 2019] )", "+0.00%;-0.00%;0.00%"),
    ("Collisions Diff", "[Collisions 2020] - [Collisions 2019]", "+#,0;-#,0;0"),
    ("Injury Share Of Decline", "DIVIDE ( [Injury 2019] - [Injury 2020], [Collisions 2019] - [Collisions 2020] )", "0.00%"),
    ("Decline Sub", '"Injury collisions account for " & FORMAT ( [Injury Share Of Decline], "0.00%" ) & " of the " & FORMAT ( [Collisions 2019] - [Collisions 2020], "#,0" ) & " fewer collisions"', None),
    ("Injury Diff", "[Injury 2020] - [Injury 2019]", "+#,0;-#,0;0"),
    ("Fatal Diff", "[Fatal 2020] - [Fatal 2019]", "+#,0;-#,0;0"),
    ("Injury Decline Sub", 'FORMAT ( [Injury Share Of Decline], "0.00%" ) & " of the total decrease"', None),
    ("Fatal Decline Sub", 'FORMAT ( DIVIDE ( [Fatal 2019] - [Fatal 2020], [Collisions 2019] - [Collisions 2020] ), "0.00%" ) & " of the total decrease"', None),
    ("Sev Color", 'IF ( SELECTEDVALUE ( Dim_Severity[Severity] ) = "Fatal", "#C77700", "#1B3A5C" )', None),
    ("Level 100", "IF ( ISBLANK ( [Injury Index] ), BLANK (), 100 )", "0"),
    ("Pandemic Text", '"All collisions " & FORMAT ( [Collisions Change], "+0.00%;-0.00%" )', None),
    ("Pandemic Headline", '"Recorded collisions fell " & FORMAT ( ABS ( [Collisions Change] ), "0.00%" ) & " in 2020: injury collisions fell " & FORMAT ( ABS ( [Injury Change] ), "0.00%" ) & " and fatal collisions only " & FORMAT ( ABS ( [Fatal Change] ), "0.00%" ) & "."', None),
    # conditions: a what-if scenario
    ("Uptake Value", "SELECTEDVALUE ( Uptake[Uptake], 0.25 )", "0%"),
    ("Scn Collisions", 'VAR k = SELECTEDVALUE ( Scenario[Key] ) RETURN SWITCH ( k, 1, CALCULATE ( [Collisions], Dim_TrafficControl[Traffic Control] = "No control" ), 2, CALCULATE ( [Collisions], Dim_RoadAlignment[Alignment Group] = "Curved" ), 3, CALCULATE ( [Collisions], Dim_Hour[Day Part] = "Night (10 pm to 6 am)" ) )', "#,0"),
    ("Scn Fatal Now", 'VAR k = SELECTEDVALUE ( Scenario[Key] ) RETURN SWITCH ( k, 1, CALCULATE ( [Fatal Collisions], Dim_TrafficControl[Traffic Control] = "No control" ), 2, CALCULATE ( [Fatal Collisions], Dim_RoadAlignment[Alignment Group] = "Curved" ), 3, CALCULATE ( [Fatal Collisions], Dim_Hour[Day Part] = "Night (10 pm to 6 am)" ) )', "#,0"),
    ("Scn Rate Now", 'VAR k = SELECTEDVALUE ( Scenario[Key] ) RETURN SWITCH ( k, 1, CALCULATE ( [Fatal Share], Dim_TrafficControl[Traffic Control] = "No control" ), 2, CALCULATE ( [Fatal Share], Dim_RoadAlignment[Alignment Group] = "Curved" ), 3, CALCULATE ( [Fatal Share], Dim_Hour[Day Part] = "Night (10 pm to 6 am)" ) )', "0.00%"),
    ("Scn Rate Safer", 'VAR k = SELECTEDVALUE ( Scenario[Key] ) RETURN SWITCH ( k, 1, CALCULATE ( [Fatal Share], Dim_TrafficControl[Traffic Control] = "Signals" ), 2, CALCULATE ( [Fatal Share], Dim_RoadAlignment[Alignment Group] = "Straight" ), 3, CALCULATE ( [Fatal Share], Dim_Hour[Day Part] = "Midday (10 am to 4 pm)" ) )', "0.00%"),
    ("Scn Avoided", "[Scn Fatal Now] * ( 1 - DIVIDE ( [Scn Rate Safer], [Scn Rate Now] ) ) * [Uptake Value]", "#,0"),
    ("Scn Share", "DIVIDE ( [Scn Avoided], [Fatal Collisions] )", "0.00%"),
    ("Top Lever Avoided", "MAXX ( VALUES ( Scenario[Key] ), [Scn Avoided] )", "#,0"),
    ("Top Lever Name", "MAXX ( TOPN ( 1, VALUES ( Scenario[Intervention] ), [Scn Avoided], DESC ), Scenario[Intervention] )", None),
    ("Top Lever Share", "DIVIDE ( [Top Lever Avoided], [Fatal Collisions] )", "0.00%"),
    ("Top Lever Sub", '"Lever: " & [Top Lever Name]', None),
    ("Top Share Sub", '"of all " & FORMAT ( [Fatal Collisions], "#,0" ) & " fatal collisions in the period"', None),
    ("Uptake Sub", '"Share of the gap closed. Change it with the dropdown."', None),
    ("Scenario Headline", '"Closing " & FORMAT ( [Uptake Value], "0%" ) & " of the gap: " & LOWER ( [Top Lever Name] ) & " could avoid about " & FORMAT ( [Top Lever Avoided], "#,0" ) & " fatal collisions (" & FORMAT ( [Top Lever Share], "0.00%" ) & ")."', None),
    ("Head-on Share of Fatal", 'DIVIDE ( CALCULATE ( [Fatal Collisions], Dim_CollisionType[Collision Type] = "Head-on" ), [Fatal Collisions] )', "0.00%"),
    ("Single Vehicle Share of Fatal", 'DIVIDE ( CALCULATE ( [Fatal Collisions], Dim_CollisionType[Collision Group] = "Single vehicle" ), [Fatal Collisions] )', "0.00%"),
    # people
    ("People Avg Rate", "CALCULATE ( [Person Fatality Rate], REMOVEFILTERS ( Dim_RoadUser ), REMOVEFILTERS ( Dim_AgeBand ), REMOVEFILTERS ( Dim_Safety ), REMOVEFILTERS ( Dim_Vehicle ), REMOVEFILTERS ( Dim_Sex ) )", "0.00%"),
    ("Times Avg", "DIVIDE ( [Person Fatality Rate], [People Avg Rate] )", '0.00"×"'),
    ("Times Avg Color", 'VAR x = [Times Avg] RETURN IF ( ISBLANK ( x ), BLANK (), IF ( x >= 1.5 && [People Involved] >= 5000, "#C77700", "#8A9BAE" ) )', None),
    ("Occ Times Avg", "DIVIDE ( [Occupant Fatality Rate], [Restrained Rate] )", '0.00"×"'),
    ("Occ Times Color", 'VAR x = [Occ Times Avg] RETURN IF ( ISBLANK ( x ), BLANK (), IF ( x >= 1.5, "#C77700", "#8A9BAE" ) )', None),
    ("Person Deaths", 'CALCULATE ( COUNTROWS ( fact_person ), Dim_PersonSeverity[Person Severity] = "Fatality" )', "#,0"),
    ("Person Fatality Rate", "DIVIDE ( [Person Deaths], [People Involved] )", "0.00%"),
    ("Occupant Fatality Rate", "CALCULATE ( [Person Fatality Rate], %s )" % OCC, "0.00%"),
    ("Unrestrained Rate", "CALCULATE ( [Person Fatality Rate], %s, %s )" % (OCC, UNRESTRAINED), "0.00%"),
    ("Restrained Rate", "CALCULATE ( [Person Fatality Rate], %s, %s )" % (OCC, RESTRAINED), "0.00%"),
    ("Unrestrained Multiple", "DIVIDE ( [Unrestrained Rate], [Restrained Rate] )", '0.00"×"'),
    ("Unrestrained People", "CALCULATE ( [People Involved], %s, %s )" % (OCC, UNRESTRAINED), "#,0"),
    ("Unrestrained Sub", '"Occupants, no safety device used: " & FORMAT ( [Unrestrained People], "#,0" ) & " people, " & FORMAT ( [Unrestrained Deaths], "#,0" ) & " deaths"', None),
    ("Unrestrained Deaths", "CALCULATE ( [Person Deaths], %s, %s )" % (OCC, UNRESTRAINED), "#,0"),
    ("Restrained People", "CALCULATE ( [People Involved], %s, %s )" % (OCC, RESTRAINED), "#,0"),
    ("Restrained Deaths", "CALCULATE ( [Person Deaths], %s, %s )" % (OCC, RESTRAINED), "#,0"),
    ("Restrained Sub", '"Occupants, safety device used: " & FORMAT ( [Restrained People], "#,0" ) & " people, " & FORMAT ( [Restrained Deaths], "#,0" ) & " deaths"', None),
    ("Multiple Sub", '"Observed ratio, not adjusted for other factors"', None),
    ("People Headline", '"Occupants with no safety device used die " & FORMAT ( [Unrestrained Multiple], "0.00" ) & " times as often, and motorcyclists and pedestrians are the most exposed."', None),
    # data quality
    ("Unknown Share (Field)", 'SWITCH ( SELECTEDVALUE ( DQ_Field[Field] ), "Collision type", DIVIDE ( CALCULATE ( [Collisions], Dim_CollisionType[Type Key] = 0 ), [Collisions] ), '
                              '"Traffic control", DIVIDE ( CALCULATE ( [Collisions], Dim_TrafficControl[Traffic Key] = 0 ), [Collisions] ), '
                              '"Road alignment", DIVIDE ( CALCULATE ( [Collisions], Dim_RoadAlignment[Alignment Key] = 0 ), [Collisions] ), '
                              '"Road surface", DIVIDE ( CALCULATE ( [Collisions], Dim_RoadSurface[Surface Key] = 0 ), [Collisions] ), '
                              '"Weather", DIVIDE ( CALCULATE ( [Collisions], Dim_Weather[Weather Key] = 0 ), [Collisions] ), '
                              '"Time of day", DIVIDE ( CALCULATE ( [Collisions], Dim_Hour[Hour Key] = 0 ), [Collisions] ), '
                              '"Safety device", DIVIDE ( CALCULATE ( [People Involved], Dim_Safety[Safety Key] = 0 ), [People Involved] ), '
                              '"Age band", DIVIDE ( CALCULATE ( [People Involved], Dim_AgeBand[Age Key] = 0 ), [People Involved] ) )', "0.00%"),
    ("Data Through Text", '"Collisions from Jan 2019 to Dec 2020  |  Police-reported fatal and injury collisions only"', None),
]
mt = ["table _Measures", "\tlineageTag: %s" % tag("table/_Measures"), ""]
for n, expr, fmt in MEASURES:
    mt.append("\tmeasure %s = %s" % (q(n), expr))
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
        vco["title"] = [{"properties": {"show": boolean(True), "text": {"expr": mea(title[1:])} if title.startswith("=") else s(title)}}]
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
ST_H, TR_H, PR_H, BU_H, WH_H, QU_H = 790, 1150, 870, 880, 910, 715


def frow(y): return [("card", x, y, 400, 110) for x in FX]


def krow(y, h=125): return [("card", x, y, CARD_W, h) for x in CARD_X] + [("icon", x + CARD_W - 12 - 26, y + 10, ic, 0) for x, ic in zip(CARD_X, ICONS)]


def facts(y, items, z0=200):
    return [card("fact%d" % i, FX[i], y, 400, 110, vm, label, z0 + i, sub="=" + sm if sm else None, font=(16, NAVY) if is_text else None, p=(10, 18, 6, 18))
            for i, (label, vm, sm, is_text) in enumerate(items)]


def block(name, x, y, w, h, head, bullets, z):
    return textbox(name, x, y, w, h, [[run(head, 12, INK, True)]] + [[run("•  " + b, 9.5, INK2)] for b in bullets], z, p=(16, 18, 10, 18))


def kcards(y, items, z0=300):
    return [card("k%d" % i, CARD_X[i], y, CARD_W, 125, m, lab, z0 + i, sub=sub) for i, (m, lab, sub) in enumerate(items)]


ST_H, WH_H, CP_H, CO_H, PE_H, EX_H, QU_H = 800, 1210, 1200, 1040, 1260, 870, 800
FOOT = "Data: Transport Canada, National Collision Database 2019-2020 (OGL - Canada). Fatal and injury collisions only."


def header(title, sub):
    return [textbox("hdr", 0, 0, 1280, 104, [
        [run("PORTFOLIO PROJECT  ·  REAL DATA: TRANSPORT CANADA NATIONAL COLLISION DATABASE, 2019 AND 2020", 8, "#F2C078", True)],
        [run(title, 22, "#FFFFFF", True)], [run(sub, 10, "#E4ECF3")]], 0, p=(18, 24, 8, 24))]


def band():
    return [("panel", 20, 120, 250, 64), ("tint", 290, 120, 830, 64)]


def fbox(n, x, y, head, big, txt, z):
    """One of the three finding boxes used on every page: heading, key number, one or two sentences."""
    return textbox("f%d" % n, x, y, 400, 150, [[run(head, 12, NAVY, True)], [run(big, 22, "#C77700", True)], [run(txt, 10.5, INK2)]], z, p=(10, 16, 6, 16))


def findings(y, items):
    return [fbox(i + 1, 20 + 420 * i, y, h, b, t, 820 + i) for i, (h, b, t) in enumerate(items)]


def footnote(y, text, z=800):
    return textbox("note", 20, y, 1240, 50, [[run("Footnote: ", 9, INK, True), run(text, 9, INK2)]], z, p=(8, 16, 4, 18))


def facts4(y, items, z0=300):
    X4 = [20, 335, 650, 965]
    return [card("k%d" % i, X4[i], y, 295, 110, m, lab, z0 + i, sub=sub, p=(10, 18, 6, 18)) for i, (m, lab, sub) in enumerate(items)]


def frow4(y): return [("card", x, y, 295, 110) for x in (20, 335, 650, 965)]


def topbar(headline_measure, yr_slicer=True):
    out = [reset_button(1140, 132, 120, 40, 150), card("headline", 290, 120, 830, 64, headline_measure, None, 200, font=(10, NAVY), p=(10, 18, 8, 18))]
    if yr_slicer:
        out.insert(0, slicer("yr", 20, 120, 250, 64, "Date", "Year Label", "Year (none = both)", 100, sync="Year"))
    return out


bg("canvas_start.png", ST_H, [("tint", 20, 120, 1100, 64)] + frow4(200) + [("panel", 20, 335, 610, 170), ("panel", 650, 335, 610, 170), ("panel", 20, 525, 610, 150), ("panel", 650, 525, 610, 150), ("warn", 20, 695, 1240, 50)])
bg("canvas_when.png", WH_H, band() + frow(200) + [("panel", 20, 330, 780, 600), ("panel", 820, 330, 440, 600), ("panel", 20, 950, 400, 150), ("panel", 440, 950, 400, 150), ("panel", 860, 950, 400, 150), ("warn", 20, 1120, 1240, 50)])
bg("canvas_compare.png", CP_H, [("tint", 20, 120, 1100, 64)] + frow(200) + [("panel", 20, 330, 610, 340), ("panel", 650, 330, 610, 340), ("panel", 20, 690, 610, 230), ("card", 40, 750, 275, 150), ("card", 335, 750, 275, 150), ("panel", 650, 690, 610, 230), ("panel", 20, 940, 400, 150), ("panel", 440, 940, 400, 150), ("panel", 860, 940, 400, 150), ("warn", 20, 1110, 1240, 50)])
bg("canvas_conditions.png", CO_H, band() + frow(200) + [("panel", 20, 330, 1240, 82), ("panel", 20, 422, 610, 338), ("panel", 650, 420, 610, 340), ("panel", 20, 780, 400, 150), ("panel", 440, 780, 400, 150), ("panel", 860, 780, 400, 150), ("warn", 20, 950, 1240, 50)])
bg("canvas_people.png", PE_H, band() + frow(200) + [("panel", 20, 330, 610, 310), ("panel", 650, 330, 610, 310), ("panel", 20, 660, 610, 310), ("panel", 650, 660, 610, 310), ("panel", 20, 990, 400, 150), ("panel", 440, 990, 400, 150), ("panel", 860, 990, 400, 150), ("warn", 20, 1160, 1240, 50)])
bg("canvas_explore.png", EX_H, [("tint", 20, 120, 1100, 64), ("panel", 20, 200, 1240, 550), ("warn", 20, 770, 1240, 50)])
bg("canvas_quality.png", QU_H, [("panel", 20, 130, 610, 350), ("panel", 20, 495, 610, 250), ("panel", 650, 130, 610, 350), ("panel", 650, 495, 610, 250)])

pages = {}

# ---- Start
st = header("When and where do Canadian roads turn deadly?", "Start here: four headline numbers, what the data shows, and what I would do about it.")
st += [textbox("q", 20, 120, 1100, 64, [[run("The question:  ", 10, INK, True),
            run("When, where and under what conditions do fatal collisions concentrate, and who is most at risk, so an insurer's analytics team knows what to monitor and what to say about safe driving?", 10, INK2)]], 100, p=(12, 18, 8, 18))]
st += [reset_button(1140, 132, 120, 40, 150)]
st += facts4(200, [("Collisions", "Collisions, 2019 and 2020", "=Collisions Sub"), ("Fatal Share", "Share that are fatal", "=Fatal Sub"),
                   ("Riskiest Hour Share", "Riskiest hour for a fatal outcome", "=Riskiest Hour Text"), ("Fatal Change", "Fatal collisions, 2020 against 2019", "=Pandemic Text")])
st += [block("finds", 20, 335, 610, 170, "What the data shows", [
           "Collisions fell 24.38% in 2020, but fatal collisions only 1.29%, so the fatal share rose from 1.53% to 2.00%.",
           "At night (10 pm to 6 am) 3.41% of collisions are fatal against 1.52% by day. The riskiest hour is 4 am, at 4.89%.",
           "Head-on collisions are 10.96% fatal and cause 17.80% of fatal collisions from 2.82% of all. Occupants with no safety device used die 16.09 times as often (6.98% against 0.43%)."], 300),
       block("recs", 650, 335, 610, 170, "What I would do", [
           "Monitor the fatal share, not only the count: in 2020 collisions fell but fatal ones did not.",
           "Put night driving, head-on and single-vehicle collisions, and roads with no traffic control on the risk watch list: they carry far more fatal outcomes than their share of collisions.",
           "Use the safety-device gap in safe-driving messaging. These are proposals from police-reported data, not claims or pricing advice."], 310),
       block("how", 20, 525, 610, 150, "How to use this report", [
           "Use the page tabs. When shows the hour and weekday pattern, Compare sets 2020 against 2019, and Conditions is a what-if scenario: choose how much of the gap between risky and safer roads to close.",
           "Explore is a decomposition tree: click the + to split fatal collisions by any factor.",
           "Fatal share means the share of reported collisions that caused at least one death."], 320),
       block("about", 650, 525, 610, 150, "About the data and model", [
           "Source: Transport Canada, National Collision Database, 2019 and 2020. Police-reported fatal and injury collisions, one row per person in each vehicle.",
           "A star schema: two fact tables (185,772 collisions and 463,630 people) and 15 dimensions. Every dimension has an 'unknown' member, so no record disappears from a chart.",
           "Collision counts here are not insurance claims."], 400),
       footnote(695, "this is police-reported fatal and injury collisions only: no property-damage-only collisions and no claims, so it cannot support loss ratios or pricing. 2020 is a pandemic year, so it is not a typical comparison.", 500)]
st += footer(ST_H)
pages["start"] = dict(name="Start here", H=ST_H, img="canvas_start.png", visuals=st)

# ---- When
wn = header("Fatal collisions peak between midnight and 5 am", "The fatal share of collisions by hour and weekday, with 2019 against 2020 by month.")
wn += topbar("When Headline")
wn += facts(200, [("Fatal share at night (10 pm to 6 am)", "Night Fatal Share", "Night Sub", False), ("Fatal share by day (6 am to 10 pm)", "Day Fatal Share", "Day Sub", False),
                  ("Night against day", "Night Times Day", "Night Times Sub", False)])
wn += [chart("heat", 20, 330, 780, 555, "pivotTable", {"Rows": [C("Dim_Hour", "Hour Label", "Hour")], "Columns": [C("Dim_Weekday", "Weekday")], "Values": [M("Heat Share", "Fatal share")]}, 300,
             "Fatal share by hour and weekday", "Darker means a higher fatal share. Cells with under 100 collisions are blank.",
             "Matrix heat map of the fatal share by hour and weekday",
             objects={"values": [{"properties": {"backColor": field_color("Heat Fill"), "fontColor": field_color("Heat Font"), "fontSize": num(10)},
                                  "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": "_Measures.Heat Share"}}],
                      "grid": [{"properties": {"rowPadding": num(1)}}], "columnHeaders": [{"properties": {"fontSize": num(10)}}], "rowHeaders": [{"properties": {"fontSize": num(10)}}],
                      "columnWidth": [{"properties": {"value": num(98)}, "selector": {"metadata": "_Measures.Heat Share"}}],
                      "subTotals": [{"properties": {"rowSubtotals": boolean(False), "columnSubtotals": boolean(False)}}]}),
       textbox("heatkey", 30, 890, 760, 38, [[run("Times the overall average:   ", 9, INK2), run("■ ", 12, "#FFF4DC"), run("under 0.75    ", 9, INK2), run("■ ", 12, "#FBD9A0"), run("0.75 to 1.5    ", 9, INK2),
                                              run("■ ", 12, "#F4B860"), run("1.5 to 2.5    ", 9, INK2), run("■ ", 12, "#E08A1E"), run("2.5 to 4    ", 9, INK2), run("■ ", 12, "#B85C00"), run("over 4", 9, INK2)]], 350, p=(6, 8, 4, 8)),
       chart("hourbar", 820, 330, 440, 600, "barChart", {"Category": [C("Dim_Hour", "Hour Label", "Hour")], "Y": [M("Heat Share", "Fatal share")]}, 400,
             "Fatal share by hour", "Amber bars are the night hours, 10 pm to 6 am.", "Bar chart of the fatal share by hour of day",
             objects={"dataPoint": [{"properties": {"fill": field_color("Hour Bar Color")}, "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
                      "labels": [{"properties": {"show": boolean(True), "fontSize": num(9), "labelDisplayUnits": num(1)}}], "categoryAxis": [{"properties": {"fontSize": num(9), "innerPadding": num(20)}}],
                      "valueAxis": [{"properties": {"show": boolean(False)}}]}),
       ] + findings(950, [("01 · Night against day", "2.24×", "Night collisions (10 pm to 6 am) are 3.41% fatal against 1.52% by day. The dark cells run from midnight to 5 am on every weekday."),
                         ("02 · The riskiest hour", "4.89%", "At 4 am nearly 1 in 20 collisions is fatal, against the 1.74% average. The night bars are amber in the chart on the right."),
                         ("03 · Read with care", "1,400 vs 16,000", "There are about 1,400 collisions at 4 am against 16,000 at 4 pm, so single night cells move more. Treat this as a pattern to monitor.")]) + [
       footnote(1120, "fatal share = fatal collisions divided by fatal and injury collisions. Collisions with no recorded hour (0.96%) are left out of this page. Cells under 100 collisions are blank.", 600)]
wn += footer(WH_H)
pages["when"] = dict(name="When", H=WH_H, img="canvas_when.png", visuals=wn)

# ---- Compare (time intelligence and a calculation group)
cp = header("2020 collision decline was driven almost entirely by injury collisions", "2020 against 2019: the overall change, the monthly pattern, fatal against injury, and where the decline came from.")
cp += [reset_button(1140, 132, 120, 40, 150), card("headline", 20, 120, 1100, 64, "Pandemic Headline", None, 200, font=(10, NAVY), p=(10, 18, 8, 18))]
cp += facts(200, [("Collisions, 2020 against 2019", "Collisions Change", "Coll Change Sub", False), ("Fatal collisions, 2020 against 2019", "Fatal Change", "Fatal Change Sub", False),
                  ("Fatal share in 2020", "Fatal Share 2020", "Fatal Share 2020 Sub", False)])
cp += [chart("months", 20, 330, 610, 340, "clusteredColumnChart", {"Category": [C("Date", "Month", "Month")], "Y": [M("Collisions Dated", "Collisions")], "Series": [C("Date", "Year Label", "Year")]}, 300,
             "Collisions by month, 2019 against 2020", "Each month has two bars. The gap in spring is the drop.", "Clustered column chart of collisions by month for 2019 and 2020",
             objects={"legend": [{"properties": {"show": boolean(True), "position": s("Bottom")}}], "labels": [{"properties": {"show": boolean(False)}}],
                      "dataPoint": [{"properties": {"fill": solid("#9FB3C8")}, "selector": {"metadata": "_Measures.Collisions Dated"}}]}),
       chart("index", 650, 330, 610, 340, "lineChart", {"Category": [C("Date", "Month", "Month")], "Y": [M("Injury Index", "Injury collisions"), M("Fatal Index", "Fatal collisions"), M("Level 100", "2019 level")]}, 400,
             "Monthly collision counts relative to 2019", "100 = the same month of 2019. Below 100 means fewer recorded collisions in 2020.",
             "Line chart of 2020 injury and fatal collisions as a percentage of 2019",
             objects={"dataPoint": [{"properties": {"fill": solid(NAVY)}, "selector": {"metadata": "_Measures.Injury Index"}}, {"properties": {"fill": solid("#C77700")}, "selector": {"metadata": "_Measures.Fatal Index"}}, {"properties": {"fill": solid("#8A97A5")}, "selector": {"metadata": "_Measures.Level 100"}}],
                      "legend": [{"properties": {"show": boolean(True), "position": s("Bottom")}}],
                      "valueAxis": [{"properties": {"start": num(0), "end": num(120)}}]},
             extra={"filterConfig": {"filters": [{"name": "f2020a", "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Date"}}, "Property": "Year"}}, "type": "Categorical",
                      "filter": {"Version": 2, "From": [{"Name": "d", "Entity": "Date", "Type": 0}],
                                 "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": "Year"}}], "Values": [[{"Literal": {"Value": "2020L"}}]]}}}]}}]}}),
       textbox("dhead", 30, 698, 590, 46, [[run("Where the decline came from", 12, INK, True)], [run("Change in collisions, 2019 to 2020. Injury and fatal add up to the total decrease.", 9, INK2)]], 505, p=(2, 4, 2, 4)),
       card("dinj", 40, 750, 275, 150, "Injury Diff", "Injury collisions", 506, sub="=Injury Decline Sub", font=(20, NAVY), p=(10, 14, 6, 14)),
       card("dfat", 335, 750, 275, 150, "Fatal Diff", "Fatal collisions", 507, sub="=Fatal Decline Sub", font=(20, NAVY), p=(10, 14, 6, 14)),
       chart("matrix", 650, 690, 610, 230, "pivotTable", {"Rows": [C("Dim_Severity", "Severity", "Severity")], "Values": [M("Collisions 2019", "2019"), M("Collisions 2020", "2020"), M("Collisions Diff", "Change"), M("Collisions Change", "% change")]}, 510,
             "Fatal and injury collisions: 2019 against 2020", "Full-year counts, the same totals as the cards above.",
             "Table of fatal and injury collisions in 2019 and 2020",
             objects={"subTotals": [{"properties": {"rowSubtotals": boolean(True), "columnSubtotals": boolean(False)}}], "grid": [{"properties": {"rowPadding": num(6)}}], "columnHeaders": [{"properties": {"fontSize": num(11)}}], "rowHeaders": [{"properties": {"fontSize": num(11)}}], "values": [{"properties": {"fontSize": num(11)}}]}),
       ] + findings(940, [("01 · Overall decline", "-24.38%", "Recorded collisions fell 24.38% in 2020. April had the largest drop: 52.10% below April 2019."),
                         ("02 · Driver of the decline", "99.92%", "Injury collisions account for 99.92% of the decrease. Fatal collisions fell only 1.29%."),
                         ("03 · Interpretation", "1.53% to 2.00%", "The fatal share rose because fatal collisions held while others fell. That is a change in the mix of recorded collisions, not proof that driving became riskier.")]) + [
       footnote(1110, "2020 is a pandemic year, so it is not a typical comparison. Cards and the table use all collisions in each year. Only the monthly charts leave out two collisions with no recorded month. Monthly fatal counts are small (about 70 to 200), so single months move more.", 600)]
cp += footer(CP_H)
pages["compare"] = dict(name="Compare", H=CP_H, img="canvas_compare.png", visuals=cp)

# ---- Conditions (what-if scenario)
cd = header("What if risky roads were made as safe as safe ones?", "A what-if scenario: choose how much of the gap to close and see how many fatal collisions that could avoid.")
cd += topbar("Scenario Headline")
cd += facts(200, [("Biggest single lever: fatal collisions avoided", "Top Lever Avoided", "Top Lever Sub", False), ("Share of all fatal collisions", "Top Lever Share", "Top Share Sub", False),
                  ("Share of the gap closed", "Uptake Value", "Uptake Sub", False)])
sl = slicer("uptake", 30, 334, 340, 74, "Uptake", "Uptake", "Share of the gap closed (none = 25%)", 400)
sl["visual"]["objects"]["header"][0]["properties"]["fontSize"] = num(10)
sl["visual"]["objects"]["items"] = [{"properties": {"fontSize": num(11)}}]
sl["visual"]["objects"]["selection"] = [{"properties": {"singleSelect": boolean(True), "selectAllCheckboxEnabled": boolean(False)}}]
cd += [sl,
       textbox("assume", 390, 338, 860, 66, [[run("How it works:  ", 10, INK, True), run("for each lever, the fatal share on the risky roads is moved toward the share on the safer roads, by the percentage you choose. "
            "Avoided = fatal collisions on the risky roads x (1 - safer share / risky share) x share chosen. It is illustrative: it assumes the gap is caused by the road, which the data cannot prove.", 9.5, INK2)]], 410, p=(4, 8, 4, 8)),
       chart("levers", 20, 430, 610, 330, "clusteredBarChart", {"Category": [C("Scenario", "Intervention", "Lever")], "Y": [M("Scn Avoided", "Fatal collisions avoided")]}, 500,
             "Fatal collisions avoided, by lever", "Each bar is one lever on its own. Levers overlap, so do not add them.", "Bar chart of fatal collisions avoided by each lever",
             sort=(mea("Scn Avoided"), "Descending"), labels=True,
             objects={"dataPoint": [{"properties": {"fill": solid("#C77700")}, "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
                      "categoryAxis": [{"properties": {"fontSize": num(10)}}], "valueAxis": [{"properties": {"show": boolean(False)}}], "labels": [{"properties": {"show": boolean(True), "fontSize": num(11), "labelDisplayUnits": num(1)}}]}),
       chart("detail", 650, 430, 610, 330, "pivotTable", {"Rows": [C("Scenario", "Intervention", "Lever")],
             "Values": [M("Scn Fatal Now", "Fatal now"), M("Scn Rate Now", "Fatal share now"), M("Scn Rate Safer", "Safer share"), M("Scn Avoided", "Avoided")]}, 510,
             "The numbers behind each lever", "Safer share is the fatal share on signalled roads, straight roads and midday.", "Table of the numbers behind each lever",
             objects={"grid": [{"properties": {"rowPadding": num(16)}}], "columnHeaders": [{"properties": {"fontSize": num(11)}}], "rowHeaders": [{"properties": {"fontSize": num(11)}}], "values": [{"properties": {"fontSize": num(11)}}],
                      "subTotals": [{"properties": {"rowSubtotals": boolean(False), "columnSubtotals": boolean(False)}}]}),
       ] + findings(780, [("01 · The biggest lever", "1,744", "If uncontrolled roads had the fatal share of signalled ones, about 1,744 fewer fatal collisions (54.09% of all) would have happened. That is the largest gap by far."),
                         ("02 · Smaller levers", "459 and 402", "Treating curved roads like straight ones would avoid about 459 (14.25%), and making night as safe as midday about 402 (12.46%). These are at 100% of the gap closed."),
                         ("03 · How to read this", "What-if", "This is a scenario, not a forecast. It uses recorded collisions with no traffic volumes, assumes the gap is caused by the road, and the levers overlap.")]) + [
       footnote(950, "fatal share = fatal collisions divided by fatal and injury collisions. Scenario results change with the Year slicer. The 25% default applies when no share is chosen.", 800)]
cd += footer(CO_H)
pages["conditions"] = dict(name="Conditions", H=CO_H, img="canvas_conditions.png", visuals=cd)

# ---- People
pe = header("Fatality rates vary sharply by road user, safety-device use and age", "Among people in reported fatal and injury collisions, motorcyclists, pedestrians and occupants with no safety device used show the highest fatality rates.")
pe += topbar("People Headline")
pe += facts(200, [("Fatality rate: no safety device used", "Unrestrained Rate", "Unrestrained Sub", False), ("Fatality rate: safety device used", "Restrained Rate", "Restrained Sub", False),
                  ("How much higher", "Unrestrained Multiple", "Multiple Sub", False)])


def nf(n, ent, prop):
    return {"filterConfig": {"filters": [{"name": n, "field": {"Column": {"Expression": {"SourceRef": {"Entity": ent}}, "Property": prop}}, "type": "Categorical",
            "filter": {"Version": 2, "From": [{"Name": "d", "Entity": ent, "Type": 0}],
                       "Where": [{"Condition": {"Not": {"Expression": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": prop}}], "Values": [[{"Literal": {"Value": "'Unknown or not reported'"}}]]}}}}}]}}]}}


def amber(color_measure):
    return {"properties": {"fill": field_color(color_measure)}, "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}


pe += [chart("user", 20, 330, 610, 310, "scatterChart", {"Category": [C("Dim_RoadUser", "Road User", "Road user")], "X": [M("People Involved", "People involved")], "Y": [M("Person Fatality Rate", "Fatality rate")], "Size": [M("Person Deaths", "Deaths")]}, 300,
             "Motorcyclists and pedestrians show the highest fatality rates", "Right = more people, up = higher rate, bigger bubble = more deaths.", "Bubble chart of road users by number of people and fatality rate",
             objects={"categoryLabels": [{"properties": {"show": boolean(True), "fontSize": num(10)}}], "bubbles": [{"properties": {"bubbleSize": num(15)}}], "dataPoint": [fill(NAVY)],
                      "categoryAxis": [{"properties": {"start": num(0), "end": num(360000)}}], "valueAxis": [{"properties": {"start": num(0), "end": num(0.05)}}]},
             extra=nf("fu", "Dim_RoadUser", "Road User")),
       chart("age", 650, 330, 610, 310, "columnChart", {"Category": [C("Dim_AgeBand", "Age Band", "Age band")], "Y": [M("Times Avg", "Times the average")]}, 400,
             "The fatality rate rises in older age groups", "Times the average rate (1.00×). Amber is 1.50× or more. Unknown ages left out.", "Column chart of the fatality rate by age band relative to the average",
             labels=True, objects={"dataPoint": [amber("Times Avg Color")], "valueAxis": [{"properties": {"show": boolean(False)}}]}, extra=nf("fa", "Dim_AgeBand", "Age Band")),
       chart("safe", 20, 660, 610, 310, "clusteredBarChart", {"Category": [C("Dim_Safety", "Safety Device", "Safety device")], "Y": [M("Occ Times Avg", "Times the rate with a device")]}, 500,
             "Occupants with no safety device used have a far higher fatality rate", "Occupants against those who used a device (1.00×). Unknown left out.", "Bar chart of occupant fatality rate by safety device relative to device use",
             sort=(mea("Occ Times Avg"), "Descending"), labels=True, objects={"dataPoint": [amber("Occ Times Color")], "categoryAxis": [{"properties": {"fontSize": num(9)}}], "valueAxis": [{"properties": {"show": boolean(False)}}]}, extra=nf("fs", "Dim_Safety", "Safety Device")),
       chart("veh", 650, 660, 610, 310, "clusteredBarChart", {"Category": [C("Dim_Vehicle", "Vehicle Group", "Vehicle group")], "Y": [M("Times Avg", "Times the average")]}, 600,
             "Two-wheelers have a higher fatality rate than cars", "Times the average rate. 'Other' is small (about 2,700 people): see footnote.", "Bar chart of the fatality rate by vehicle group relative to the average",
             sort=(mea("Times Avg"), "Descending"), labels=True, objects={"dataPoint": [amber("Times Avg Color")], "valueAxis": [{"properties": {"show": boolean(False)}}]}, extra=nf("fv", "Dim_Vehicle", "Vehicle Group")),
       ] + findings(990, [("01 · Road users", "4.91× and 3.77×", "Motorcyclists show 4.91 times the average fatality rate and pedestrians 3.77 times. Drivers, the largest group, are at 0.76 times."),
                         ("02 · Safety devices", "16.09×", "Occupants with no safety device used die 16.09 times as often (6.98% against 0.43%). The gap holds in every age band, but it is not adjusted for everything."),
                         ("03 · Age", "2.11×", "People 65 and over show 2.11 times the average fatality rate. These are unadjusted comparisons, not the effect of age alone.")]) + [
       footnote(1160, "fatality rate = deaths divided by people in reported fatal or injury collisions, not risk per trip or km. Findings use both years. 6.98%: 7,939 occupants, 554 deaths, 95% interval 6.44% to 7.56%; 0.43%: 315,866 occupants, 1,370 deaths. 'Other' vehicles: farm, construction, emergency, off-road, snowmobile, streetcar. 'Not used' differs from 'not equipped'.", 800)]
pe += footer(PE_H)
pages["people"] = dict(name="People", H=PE_H, img="canvas_people.png", visuals=pe)

# ---- Explore (AI visual)
ex = header("What drives a fatal outcome? Explore it yourself", "A decomposition tree: split the fatal collisions by any factor, in any order.")
ex += [reset_button(1140, 132, 120, 40, 150),
       textbox("q", 20, 120, 1100, 64, [[run("How to use it:  ", 10, INK, True),
            run("click the + under a bar and choose a factor. 'High value' picks the factor that most concentrates fatal collisions, so you can see what the data finds worth splitting on.", 10, INK2)]], 100, p=(12, 18, 8, 18)),
       chart("tree", 20, 200, 1240, 550, "decompositionTreeVisual",
             {"Analyze": [M("Fatal Collisions", "Fatal collisions")],
              "ExplainBy": [C("Dim_Hour", "Day Part", "Time of day"), C("Dim_CollisionType", "Collision Group", "Collision group"), C("Dim_TrafficControl", "Traffic Control", "Traffic control"),
                            C("Dim_RoadSurface", "Surface Group", "Road surface"), C("Dim_RoadAlignment", "Alignment Group", "Road alignment"), C("Dim_Weather", "Weather Group", "Weather"),
                            C("Dim_RoadLayout", "Layout Group", "Road layout"), C("Dim_Weekday", "Week Part", "Weekday or weekend")]}, 300,
             "Fatal collisions, split by the factors you choose", "Starts with all 3,225 fatal collisions.", "Decomposition tree of fatal collisions"),
       footnote(770, "the tree finds where fatal collisions concentrate by count, which favours common situations. Compare with the fatal share on the Conditions page, which shows how likely each situation is to be fatal.", 600)]
ex += footer(EX_H)
pages["explore"] = dict(name="Explore", H=EX_H, img="canvas_explore.png", visuals=ex)

# ---- Data quality
dq = header("Before any analysis: what each number in the file means", "How I found the collision ID, how the model is built, and what is missing.")
dq += [chart("unk", 20, 130, 610, 350, "clusteredBarChart", {"Category": [C("DQ_Field", "Field")], "Y": [M("Unknown Share (Field)", "Unknown or not reported")]}, 300,
             "Share of records with an unknown value", "Unknown means the police form left it blank or the jurisdiction did not provide it.", "Bar chart of the unknown share by field",
             sort=(mea("Unknown Share (Field)"), "Descending"), labels=True, objects={"dataPoint": [fill(NAVY)]}),
       block("idblock", 20, 495, 610, 250, "How I found the collision ID", [
           "The dictionary lists no collision ID, so my first version derived one from 'vehicle 1, person 1'. It found 185,359 collisions, 413 fewer than the real 185,772, so it had merged collisions that are separate.",
           "The file does hold a key, C_CASE, that the dictionary does not mention. It gives 185,772 collisions; severity, hour, weather and road surface never change inside a case, and the vehicle count matches 99.56%.",
           "I used C_CASE. Every fatal collision has a death and no injury collision does (3,508 deaths in 3,225 fatal collisions)."], 400),
       block("model", 650, 130, 610, 350, "How the model is built", [
           "A star schema: fact_collision and fact_person hold keys and counts only; 15 dimensions hold every label, group and sort order.",
           "Every dimension has an 'unknown' member (key 0), so records with a missing value stay in the totals and show as 'Unknown or not reported', never as (Blank).",
           "Dimensions have hierarchies (for example collision group to collision type) and are loaded through Power Query, which sets types and renames columns.",
           "One chart shows the unknown share of any field through a disconnected table and a SWITCH measure. A what-if parameter drives the Conditions scenario, and a Time Comparison calculation group (prior year, change, % change) is in the model.",
           "471,046 source rows (one per person in each vehicle) include 7,416 dummy or unmatched records, such as a dummy person for a parked car. The model keeps 463,630 real people. Two collisions have no recorded month, so they appear only when no year is chosen."], 410),
       block("terms", 650, 495, 610, 250, "Terms in plain language", [
           "Fatal share: the share of reported collisions that caused at least one death.",
           "Head-on: two vehicles hit while travelling in opposite directions.",
           "Fatality rate: deaths among the people in these collisions, not a risk per person on the road.",
           "Unknown or not reported: left blank on the police form, or not supplied by that jurisdiction.",
           "Only police-reported fatal and injury collisions are included, from 2019 and 2020 (the 2021 English file was blank in the catalogue)."], 420)]
dq += footer(QU_H)
pages["quality"] = dict(name="Data quality", H=QU_H, img="canvas_quality.png", visuals=dq)

# ---------------------------------------------------------------- theme
def sol(c): return {"solid": {"color": c}}


theme = {"name": "Collision Risk Portfolio", "dataColors": [NAVY, TEAL, AMBER, GREY, "#6B4C7A", "#B23A48", "#4F6D7A", LIGHT],
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
                                                 "pageOrder": ["start", "when", "compare", "conditions", "people", "explore", "quality"], "activePageName": "start"})
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
    "options": {"suppressActiveSection": True, "suppressDisplay": True}, "explorationState": {"version": "1.3", "activeSection": "when", "sections": sections}})
wjson(os.path.join(DEF, "bookmarks", "bookmarks.json"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json", "items": [{"name": "reset_filters"}]})
print("built", {k: len(v["visuals"]) for k, v in pages.items()}, "measures:", len(MEASURES))
