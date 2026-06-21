#!/usr/bin/env python3
"""rebuild_commodity_wb.py — regenerate the cyclical commodity monthly CSVs from the AUTHORITATIVE
World Bank "Pink Sheet" (CMO Historical Monthly), replacing the prior hand-entered/estimate values.

Provenance fix (2026-06-12): production flagged data/*_monthly.csv as unreliable. caustic_soda was
SYNTHETIC (piecewise-linear, no WB source — WB does not track caustic soda) and is LEFT UNTOUCHED but
flagged. The other 5 (iron_ore, urea, dap, rubber, sugar) ARE World Bank series -> rebuilt here from the
Pink Sheet so they are authoritative & current (through 2026-05).

Source file: CMO-Historical-Data-Monthly.xlsx, sheet "Monthly Prices".
Run: python rebuild_commodity_wb.py "<path-to-xlsx>"
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd
W = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
XLSX = sys.argv[1] if len(sys.argv) > 1 else r"/home/trido/thanhdt/WorkingClaude/data/CMO-Historical-Data-Monthly.xlsx"
START = "2006-04"   # keep the existing file window

# 8L commodity file  ->  (World Bank Pink Sheet column, decimals)
MAP = {
    "iron_ore": ("Iron ore, cfr spot", 2),   # $/dmtu
    "urea":     ("Urea ",              2),    # $/mt  (note trailing space in WB header)
    "dap":      ("DAP",                2),    # $/mt
    "rubber":   ("Rubber, RSS3",       3),    # $/kg  (8L basis = RSS3, verified vs history)
    "sugar":    ("Sugar, world",       3),    # $/kg
    "brent":    ("Crude oil, Brent",   2),    # $/bbl
}

def main():
    df = pd.read_excel(XLSX, sheet_name="Monthly Prices", skiprows=4, header=0)
    mcol = df.columns[0]
    data = df.iloc[1:].copy()                       # row0 = units
    data["ym"] = data[mcol].astype(str).str.replace("M", "-", regex=False)  # 2006M04 -> 2006-04
    print(f"WB Pink Sheet loaded: {data['ym'].dropna().iloc[0]} -> {data['ym'].dropna().iloc[-1]}\n")
    for name, (col, dp) in MAP.items():
        if col not in df.columns:
            print(f"  [!] {name}: column '{col}' not found — SKIP"); continue
        s = data[["ym", col]].copy()
        s[col] = pd.to_numeric(s[col], errors="coerce")
        s = s.dropna()
        s = s[s["ym"] >= START]
        out = s.rename(columns={"ym": "month", col: "price"})
        out["price"] = out["price"].round(dp)
        path = os.path.join(W, "data", f"{name}_monthly.csv")
        out.to_csv(path, index=False)
        print(f"  [OK] {name:<9} ← WB '{col}'  | {len(out)} mo, {out['month'].iloc[0]}->{out['month'].iloc[-1]}, "
              f"last3={out['price'].tail(3).tolist()}")
    print("\nNOTE: caustic_soda_monthly.csv NOT rebuilt — World Bank has no caustic soda series. "
          "Left as flagged SYNTHETIC ESTIMATE (see data/caustic_soda_monthly.SOURCE.txt).")

if __name__ == "__main__":
    main()
