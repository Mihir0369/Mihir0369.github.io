"""Run every named query in sql/analysis.sql against 311.db, print the results, save each as CSV in results/."""
import pathlib
import re
import sqlite3

import pandas as pd

text = pathlib.Path("sql/analysis.sql").read_text(encoding="utf-8")
blocks = re.split(r"^-- (q\d+_\w+)[^\n]*\n", text, flags=re.M)[1:]
out = pathlib.Path("results")
out.mkdir(exist_ok=True)

with sqlite3.connect("311.db") as con:
    for name, sql in zip(blocks[0::2], blocks[1::2]):
        df = pd.read_sql_query(sql.strip().rstrip(";"), con)
        df.to_csv(out / f"{name}.csv", index=False)
        print(f"\n=== {name} ===")
        print(df.to_string(index=False))
