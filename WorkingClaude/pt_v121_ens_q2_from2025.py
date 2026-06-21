# -*- coding: utf-8 -*-
"""Wrapper: run pt_v121_ens_q2.py logic with START_DATE='2025-01-01' and unique outputs.

Does NOT overwrite production papertrade CSVs (data/pt_v121_ens_q2_*.csv).
Outputs go to data/pt_v121_ens_q2_from2025_*.csv instead.
"""
import os, sys, io, runpy
import pt_dates

# 1) Override start date BEFORE the inner script reads it
pt_dates.START_DATE = "2025-06-09"

# 2) Patch sys.argv-free path: re-exec inner script in its own namespace, with output
#    paths rewritten so production CSVs are not clobbered.
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
INNER = os.path.join(WORKDIR, "pt_v121_ens_q2.py")
with open(INNER, "r", encoding="utf-8") as f:
    code = f.read()

# Rewrite output file basenames
code = code.replace("pt_v121_ens_q2_logs.csv",          "pt_v121_ens_q2_from20250609_logs.csv")
code = code.replace("pt_v121_ens_q2_transactions.csv",  "pt_v121_ens_q2_from20250609_transactions.csv")
code = code.replace("pt_v121_ens_q2_open_positions.csv","pt_v121_ens_q2_from20250609_open_positions.csv")
code = code.replace("pt_v121_ens_q2_report.md",         "pt_v121_ens_q2_from20250609_report.md")
# Also rename the internal sim names so logs/prints carry the from2025 suffix
code = code.replace('name="pt_v121_ens_q2_BAL"',  'name="pt_v121_ens_q2_from20250609_BAL"')
code = code.replace('name="pt_v121_ens_q2_VN30"', 'name="pt_v121_ens_q2_from20250609_VN30"')

# Execute in a fresh module namespace
ns = {"__name__": "__main__", "__file__": INNER}
exec(compile(code, INNER, "exec"), ns)
