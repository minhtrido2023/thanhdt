#!/usr/bin/env python3
"""exp_ prefix — R&D probe, NOT canonical. Cross-check bank_lens_v3.csv self-calc
NIM/CIR/ROE against vnstock KBS-source Finance.ratio() vendor-computed values.
Job Taylor_20260828_092753 (follow-up to Taylor_20260828_084735 / commit b23d7541)."""
import warnings; warnings.filterwarnings("ignore")
import sys, time
import logging; logging.disable(logging.CRITICAL)
import pandas as pd
from vnstock.api.financial import Finance

BANKS=["VCB","BID","CTG","TCB","MBB","ACB","VPB","VIB","HDB","STB","SHB","TPB","MSB","OCB","LPB","EIB","NAB","SSB"]
LATEST_COL="2026-Q2"

rows=[]
for i,tk in enumerate(BANKS):
    try:
        f=Finance(symbol=tk, source="KBS")
        r=f.ratio(period="quarter")
        if LATEST_COL not in r.columns:
            print(f"  [skip {tk}] no {LATEST_COL} col, cols={r.columns.tolist()}",flush=True); continue
        def get(item_id):
            row=r.loc[r["item_id"]==item_id, LATEST_COL]
            return float(row.iloc[0]) if len(row) else float("nan")
        rows.append({"ticker":tk,
            "roe_trailing_kbs":get("roe_trailling"),
            "nim_q_kbs":get("net_interest_margin_nim"),
            "cir_q_kbs":get("cost_income_ratio_cir"),
            "ldr_kbs":get("outstanding_loans_customer_deposits"),
            "eq_deposits_kbs":get("equity_deposits_from_customers"),
            "eq_assets_kbs":get("equity_total_assets"),
            "provision_loan_ratio_kbs":get("loan_loss_provision_ratio"),
        })
        print(f"  {tk}: ROE_trail={rows[-1]['roe_trailing_kbs']:.2f} NIM_q={rows[-1]['nim_q_kbs']:.2f} CIR_q={rows[-1]['cir_q_kbs']:.2f}",flush=True)
    except Exception as e:
        print(f"  [skip {tk}] {repr(e)[:80]}",flush=True)
    if i<len(BANKS)-1: time.sleep(12)

kbs=pd.DataFrame(rows)
self_df=pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/bank_lens_v3.csv")
m=self_df.merge(kbs,on="ticker",how="left")
m["roe_self_pct"]=m["ROE"]*100
m["nim_self_pct"]=m["NIM"]*100
m["cir_self_pct"]=m["CIR"]*100
m["roe_diff_pp"]=m["roe_self_pct"]-m["roe_trailing_kbs"]
m["nim_q_x4_kbs"]=m["nim_q_kbs"]*4
m["nim_diff_pp"]=m["nim_self_pct"]-m["nim_q_x4_kbs"]
m["cir_q_x4_kbs"]=m["cir_q_kbs"]  # CIR is already a ratio of trailing-ish income base per KBS docs; compare direct (quarterly) not x4
m["cir_diff_pp"]=m["cir_self_pct"]-m["cir_q_kbs"]
out=m[["ticker","roe_self_pct","roe_trailing_kbs","roe_diff_pp",
       "nim_self_pct","nim_q_kbs","nim_q_x4_kbs","nim_diff_pp",
       "cir_self_pct","cir_q_kbs","cir_diff_pp",
       "ldr_kbs","eq_deposits_kbs","eq_assets_kbs","provision_loan_ratio_kbs"]]
pd.set_option("display.width",220); pd.set_option("display.max_columns",30)
print(out.to_string(index=False))
out.to_csv("/home/trido/thanhdt/WorkingClaude/agents/Taylor/exp_bank_kbs_crosscheck.csv",index=False)
print("\nsaved exp_bank_kbs_crosscheck.csv")
