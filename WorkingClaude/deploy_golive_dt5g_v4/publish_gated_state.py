# -*- coding: utf-8 -*-
"""
publish_gated_state.py  —  LAYER 1 (DT5G state engine) publisher.

Computes today's FAIL-SAFE gated market-state series (DT5G macro overlay, auto-reverting
to DT4-only when macro_healthcheck flags the feeds) via macro_state_live.get_gated_state,
then publishes it so the production recommender (LAYER 2) can consume it:
  - BQ table  tav2_bq.vnindex_5state_dt5g_live   (state,state_raw) — read by golive_recommend's SIGNAL_V11
  - local CSV vnindex_5state_dt5g_live.csv        (mirror / audit)
  - golive_state_today.json                       (today's state + source + provenance)

PRECONDITIONS (run earlier in golive_daily.bat): pull_us_market -> rebuild_state_from_ticker
-> macro_healthcheck (writes data/macro_health.json that the gate reads).

Run: python deploy_golive_dt5g_v4/publish_gated_state.py
"""
import os, sys, io, json, subprocess
from datetime import datetime
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from macro_state_live import get_gated_state

PROJECT = "lithe-record-440915-m9"
BQ_TABLE = f"{PROJECT}:tav2_bq.vnindex_5state_dt5g_live"
WARMUP_START = "2014-01-01"     # SIGNAL_V11 state-join needs history; gate warms DT4 from 2014
END = datetime.now().strftime("%Y-%m-%d")
LOCAL_CSV = os.path.join(WORKDIR, "data/vnindex_5state_dt5g_live.csv")
STATE_JSON = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_state_today.json")

print("=" * 88); print(f"  PUBLISH GATED STATE (DT5G, fail-safe)  -> {END}"); print("=" * 88)

g = get_gated_state(WARMUP_START, END)          # [time, state, base_state, macro_state, source]
out = pd.DataFrame({"time": pd.to_datetime(g["time"]).dt.strftime("%Y-%m-%d"),
                    "state": g["state"].astype(int),
                    "state_raw": g["base_state"].astype(int)})   # state_raw = DT4 base (audit)
out.to_csv(LOCAL_CSV, index=False)
print(f"  wrote {LOCAL_CSV} ({len(out)} rows, {out['time'].iloc[0]} -> {out['time'].iloc[-1]})")

# publish to BQ (replace) so SIGNAL_V11 reads the gated series.
# Reuse the SAME bq.cmd path + shell=True invocation as simulate_holistic_nav.bq
# (Windows: `bq` is a .cmd wrapper not on the python subprocess PATH).
from simulate_holistic_nav import BQ_BIN
try:
    cmd = (f'"{BQ_BIN}" load --replace --source_format=CSV --skip_leading_rows=1 '
           f'--location=asia-southeast1 --schema=time:DATE,state:INT64,state_raw:INT64 '
           f'{BQ_TABLE} "{LOCAL_CSV}"')
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding="utf-8",
                       errors="replace", timeout=300)
    if r.returncode == 0:
        print(f"  published -> BQ {BQ_TABLE}")
    else:
        print(f"  WARNING: BQ load failed (rc={r.returncode}): {(r.stderr or r.stdout).strip()[:300]}")
except Exception as e:
    print(f"  WARNING: BQ load exception: {e}")

last = g.iloc[-1]
prov = {"published_at": datetime.now().isoformat(timespec="seconds"),
        "as_of": str(pd.to_datetime(last["time"]).date()),
        "state": int(last["state"]),
        "base_state_dt4": int(last["base_state"]),
        "macro_state_dt5g": int(last["macro_state"]),
        "source": str(last["source"]),
        "bq_table": BQ_TABLE.split(":")[1]}
os.makedirs(os.path.dirname(STATE_JSON), exist_ok=True)
json.dump(prov, open(STATE_JSON, "w", encoding="utf-8"), indent=2)
print(f"  today: as_of={prov['as_of']} state={prov['state']} source={prov['source']} "
      f"(DT4={prov['base_state_dt4']}, DT5G={prov['macro_state_dt5g']})")
print(f"  wrote {STATE_JSON}")
print("DONE.")
