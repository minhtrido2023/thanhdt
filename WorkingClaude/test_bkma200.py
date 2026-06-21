import subprocess, tempfile, os, io
BASH_EXE = r"C:\Program Files\Git\usr\bin\bash.exe"
PROJECT = "lithe-record-440915-m9"

sql = """SELECT t.ticker, t.time
FROM `tav2_bq.ticker` AS t
WHERE (t.time >= '2020-01-01' AND t.time <= '2026-04-03') AND  ((t.Volume_3M_P50*t.Price/ NULLIF(t.Inflation_7, 0)>1000000000.0) AND (t.Risk_Rating <= 6) AND ((t.ID_LO_3Y-t.ID_HI_3Y)>265.0) AND (t.MA50/ NULLIF(t.MA200, 0)>0.92) AND (t.MA10/ NULLIF(t.MA200, 0)<1.24) AND (t.ROE5Y >0.05) AND (t.PE <20.0) AND (t.PE >4.0) AND (t.NP_P0 > 1.28*t.NP_P1) AND (t.NP_P1 > 0) AND (t.HI_3M_T1/ NULLIF(t.LO_3M_T1, 0)<2.0) AND (t.ROE_Min3Y >0.02))
ORDER BY t.ticker, t.time"""

with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
    f.write(sql)
    sfwin = f.name
with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
    ofwin = f.name
sfbash = sfwin.replace("\\", "/").replace("C:", "/c")
ofbash = ofwin.replace("\\", "/").replace("C:", "/c")

print(f"SQL file: {sfbash}")
print(f"Out file: {ofbash}")

cmd = (
    f"source ~/.bashrc 2>/dev/null; "
    f"bq query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=2000000 "
    f"\"$(cat '{sfbash}')\" > '{ofbash}' 2>&1; "
    f"echo $?"
)

print("Starting subprocess...")
r = subprocess.run([BASH_EXE, "-c", cmd], capture_output=True, text=True, timeout=120)
print(f"RC={r.returncode} stdout={repr(r.stdout[:50])}")
with open(ofwin, encoding="utf-8", errors="replace") as f:
    out = f.read()
print(f"Output lines: {len(out.splitlines())}")
print("First 3 lines:", out.splitlines()[:3])
os.unlink(sfwin)
os.unlink(ofwin)
print("DONE")
