# Upload local vnindex_5state_v2g_full_history.csv as a temp BQ table for sim comparison.
import os, subprocess, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ = r"bq"

df = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_v2g_full_history.csv"))
df["time"] = pd.to_datetime(df["time"]).dt.strftime("%Y-%m-%d")
out = df[["time","state_v2g","state_raw"]].rename(columns={"state_v2g":"state"})
out["state"] = out["state"].astype("Int64")
out["state_raw"] = out["state_raw"].astype("Int64")
load_csv = os.path.join(WORKDIR, "_v2g_only_for_bq.csv")
out.to_csv(load_csv, index=False)
print(f"Uploading {len(out)} rows to tav2_bq.vnindex_5state_v2g_only ...")
cmd = (f'"{BQ}" load --replace --source_format=CSV --skip_leading_rows=1 '
       f'--project_id=lithe-record-440915-m9 '
       f'tav2_bq.vnindex_5state_v2g_only "{load_csv}" '
       f'time:DATE,state:INT64,state_raw:INT64')
r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
if r.returncode == 0:
    print("✓ uploaded")
else:
    print("✗ FAILED:", r.stderr[:500])
os.unlink(load_csv)
