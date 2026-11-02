# Fabric notebook (PySpark). Reads Files/raw/contracts.csv in the attached lakehouse.
# Column names follow the published schema; the script reports any that are missing.
from pyspark.sql import functions as F

RAW_PATH = "Files/raw/contracts.csv"

raw = (spark.read.option("header", True).option("multiLine", True).option("escape", '"')
       .csv(RAW_PATH))
print("columns:", raw.columns)

expected = ["reference_number", "vendor_name", "contract_date", "contract_value", "original_value",
            "amendment_value", "commodity_type", "solicitation_procedure", "number_of_bids",
            "trade_agreement", "country_of_vendor", "instrument_type", "reporting_period"]
missing = [c for c in expected if c not in raw.columns]
print("missing expected columns:", missing)

# Department column: prefer owner_org_title if the file has it, otherwise buyer_name.
dept_col = "owner_org_title" if "owner_org_title" in raw.columns else "buyer_name"
print("department column:", dept_col)

# ---------- Bronze ----------
bronze = raw.withColumn("_ingested_at", F.current_timestamp())
bronze.write.mode("overwrite").format("delta").saveAsTable("bronze_contracts")


# ---------- Silver: typed, trimmed, deduplicated ----------
def money(col):
    return F.regexp_replace(F.col(col).cast("string"), r"[^0-9.\-]", "").cast("double")


silver = (spark.read.table("bronze_contracts")
    .withColumn("contract_date", F.to_date("contract_date"))
    .withColumn("contract_value", money("contract_value"))
    .withColumn("original_value", money("original_value"))
    .withColumn("amendment_value", money("amendment_value"))
    .withColumn("vendor_name", F.upper(F.trim(F.col("vendor_name"))))
    .withColumn("department", F.trim(F.col(dept_col)))
    .withColumn("number_of_bids", F.col("number_of_bids").cast("int"))
    .dropDuplicates(["reference_number", "contract_date", "vendor_name", "contract_value"]))
silver.write.mode("overwrite").format("delta").saveAsTable("silver_contracts")

# ---------- Gold: star schema ----------
s = spark.read.table("silver_contracts")

fact = (s.withColumn("is_competitive",
                     F.when(F.lower(F.col("solicitation_procedure")).contains("open"), 1)
                      .when(F.col("solicitation_procedure").isNull(), None)
                      .otherwise(0))
        .select("reference_number", "contract_date", "vendor_name", "department", "commodity_type",
                "instrument_type", "contract_value", "original_value", "amendment_value",
                "number_of_bids", "is_competitive", "solicitation_procedure", "trade_agreement",
                "country_of_vendor", "reporting_period"))
fact.write.mode("overwrite").format("delta").saveAsTable("gold_fact_contracts")

(s.select("vendor_name", "country_of_vendor").dropDuplicates(["vendor_name"])
  .write.mode("overwrite").format("delta").saveAsTable("gold_dim_vendor"))
(s.select("department").dropDuplicates()
  .write.mode("overwrite").format("delta").saveAsTable("gold_dim_department"))

bounds = s.agg(F.min("contract_date").alias("lo"), F.max("contract_date").alias("hi")).first()
dim_date = (spark.sql(f"SELECT explode(sequence(to_date('{bounds.lo}'), to_date('{bounds.hi}'), interval 1 day)) AS date")
    .withColumn("year", F.year("date")).withColumn("quarter", F.quarter("date"))
    .withColumn("month", F.month("date")).withColumn("month_name", F.date_format("date", "MMM")))
dim_date.write.mode("overwrite").format("delta").saveAsTable("gold_dim_date")

# ---------- Reconciliation ----------
raw_n = raw.count()
silver_n = s.count()
gold_n = spark.read.table("gold_fact_contracts").count()
print(f"raw rows: {raw_n}, silver rows: {silver_n}, gold rows: {gold_n}")
print(f"rows removed as duplicates: {raw_n - silver_n}")
print("null contract_date:", s.filter(F.col("contract_date").isNull()).count())
print("null contract_value:", s.filter(F.col("contract_value").isNull()).count())
print("total contract value (silver):", s.agg(F.sum("contract_value")).first()[0])
