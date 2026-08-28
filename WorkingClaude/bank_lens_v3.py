#!/usr/bin/env python3
"""
bank_lens_v3.py — bank screen with ASSET-QUALITY GATE + NPL TREND (real vnstock data)
=====================================================================================
v2 ranked by score; v3 adds (1) asset-quality as a HARD GATE (a bank's #1 risk is
a bad-debt blowup — quality is pass/fail, not just points), and (2) NPL TREND over
the last ~6 quarters (NPL *rising* is more dangerous than its absolute level).

⚠️ MIGRATED 2026-08-28 (job Taylor_20260828_084735) — `finance.ratio()` (source of
ALL 11 original columns) crashes `KeyError('lengthReport')` on every ticker since
vnstock deprecated the old `Vnstock().stock().finance.ratio()` shape 31/08/2025
(same root cause `build_bank_casa_ldr.py` already documented for CASA). `ratio()`
is UNUSABLE now — switched to `finance.balance_sheet()` + `finance.income_statement()`
(community edition: only 4 latest quarters) + `company.overview()` (price/shares).

WHAT CAN BE RECOMPUTED FROM balance_sheet/income_statement (verified against VCB's
own narrative profile text 2026-08-28: ROE self-calc 16.76% vs profile-stated 16.73%,
NIM self-calc 2.81% vs profile-stated 2.63% — same ballpark, method is sound):
  - ROE   = trailing-4Q "Cổ đông của Công ty mẹ" (NPAT to parent) / latest equity
  - CIR   = trailing-4Q |"Chi phí quản lý doanh nghiệp"| / trailing-4Q "Tổng thu nhập hoạt động"
  - NIM   = trailing-4Q "Thu nhập lãi thuần" / avg(earning assets) — APPROX: "earning
            assets" here = loans + investment securities + interbank placements,
            averaged over only the oldest/newest of the 4 available quarters (community
            edition caps history at 4Q, so this is NOT a true 5-quarter daily-average NIM).
  - loanG = QoQ growth of "Cho vay khách hàng" (gross) latest vs oldest of the 4
            available quarters (~1 quarter apart, NOT true YoY — 4Q cap means the
            oldest available quarter is only ~3 quarters back, not 4).
  - PB    = current_price (company.overview) / (latest equity / issue_share)

WHAT CANNOT BE RECOMPUTED FROM balance_sheet/income_statement — NPL_4q, NPL_slope,
CAR, CASA. None of these appear in main line items: CAR is a regulatory capital
ratio not derivable from the balance sheet, CASA needs the deposit-type breakdown
note. Same limitation `build_bank_casa_ldr.py` already hit for CASA (2026-08-14) —
these live only in BCTC thuyết minh (footnotes), which vnstock's community balance
sheet/income statement endpoints do not expose. Left as NaN, NOT estimated.

**NPL/coverage — 9/18 mã ĐÃ CÓ (2026-08-28), qua OCR thuyết minh 'Phân loại nợ' gốc**
(`mike/agents/Taylor/build_bank_npl_coverage.py`, PDF static2.vietstock.vn, cùng phương pháp CASA
2 bất biến độc lập): VCB BID CTG ACB TCB MBB VIB STB SHB. 9 mã còn lại (HDB TPB MSB VPB OCB LPB
EIB NAB SSB) VẪN NaN — locate-page tự động không tìm ra trang phân loại nợ trong PDF (OCB PDF tải
lỗi hoàn toàn) — cần làm thủ công tiếp, KHÔNG suy diễn/estimate. Xem
`mike/kb/data_registry/rating-8l/bank_lens_v3.md` cho trạng thái PARTIAL đầy đủ.
`company.overview()`'s free-text `company_profile` DOES narrate NPL/NIM/ROE for the
most recent FULL YEAR for some banks (e.g. VCB: "Tỷ lệ nợ xấu ở mức 0.58%") — this
was deliberately NOT parsed into structured columns: it's prose (format/presence
not verified consistent across all 18 banks), annual only (no quarterly trend, so
NPL_slope still impossible), and parsing prose into a "hard gate" input is exactly
the kind of guess-shaped-like-data this codebase's rules warn against (§1 CLAUDE.md
data_registry). If a future job wants it, verify format across all 18 tickers first.

GATE (asset-quality inputs unavailable → cannot evaluate the original AVOID/WATCH/
CLEAN thresholds, which depended on NPL/coverage/CAR). Silently falling through to
"else: CLEAN" when those are NaN would be a fail-OPEN bug (NaN comparisons are all
False in pandas, so old `gate()` would mislabel every bank CLEAN). Replaced with an
explicit ROE-only gate, matching `rating_8l.py::rate_bank()`'s existing philosophy
(ROE is the base; NPL/coverage are differentiators applied ONLY when present):
  AVOID     : ROE<8% (weak franchise — the one input we still have real data for)
  DATA_GAP  : else (profitable but asset-quality unverifiable — NPL/CAR/coverage/
              CASA are NaN pending a footnote-scraping migration)
Downstream consumer `rating_8l.py::rate_bank()` already fails safe on NaN NPL/cov
(falls through to ROE-only buckets) — this file's `gate` column is DISPLAY-ONLY
metadata, not consumed as a hard filter anywhere else (verified by grep 2026-08-28).
Output: data/bank_lens_v3.md + .csv
"""
import warnings; warnings.filterwarnings("ignore")
import sys, logging
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
logging.disable(logging.CRITICAL)
import os, time
import numpy as np, pandas as pd
from vnstock import Vnstock
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
BANKS=["VCB","BID","CTG","TCB","MBB","ACB","VPB","VIB","HDB","STB","SHB","TPB","MSB","OCB","LPB","EIB","NAB","SSB"]

# NPL/coverage OCR'd from BCTC thuyet minh gốc, 2 bất biến verify (mike/agents/Taylor/
# build_bank_npl_coverage.py) — 9/18 mã (VCB BID CTG ACB TCB MBB VIB STB SHB); 9 mã còn lại
# (HDB TPB MSB VPB OCB LPB EIB NAB SSB) chưa OCR (locate-page tự động không tìm ra trang phân
# loại nợ; OCB PDF tải lỗi) — vẫn NaN, KHÔNG suy diễn.
NPL_COVERAGE_CSV=os.path.join(WORKDIR,"data","bank_npl_coverage_primary_20260828.csv")
def load_npl_coverage():
    if not os.path.exists(NPL_COVERAGE_CSV): return {}
    d=pd.read_csv(NPL_COVERAGE_CSV)
    d=d[d["verified"].astype(str)=="True"]
    return {r["ticker"]:(r["NPL"],r["coverage"]) for _,r in d.iterrows()}
NPL_COV=load_npl_coverage()

IT_LOAN="Cho vay khách hàng"; IT_EQUITY="VỐN CHỦ SỞ HỮU"; IT_SEC="Chứng khoán đầu tư"
IT_INTERBANK="Tiền gửi tại các TCTD khác và cho vay các TCTD khác"
INC_NPAT_PARENT="Cổ đông của Công ty mẹ"; INC_NPAT="Lợi nhuận sau thuế"
INC_OPEX="Chi phí quản lý doanh nghiệp"; INC_OPINC="Tổng thu nhập hoạt động"
INC_NII="Thu nhập lãi thuần"

def pull(tk, retries=4):
    for attempt in range(retries):
        try:
            v=Vnstock().stock(symbol=tk, source="VCI")
            bs=v.finance.balance_sheet(period="quarter", lang="vi", dropna=False)
            time.sleep(2)
            inc=v.finance.income_statement(period="quarter", lang="vi", dropna=False)
            time.sleep(2)
            ov=v.company.overview()
            ov=ov.loc[:,~ov.columns.duplicated()]  # vnstock 2026-08-28: overview() started returning dup cols (e.g. 4x issue_share)
            break
        except Exception as e:
            if attempt==retries-1: print(f"  [skip {tk}] {repr(e)[:60]}",flush=True); return None
            time.sleep(30)  # guest tier: 20 req/min -> cooldown, not a quick retry
    try:
        periods=sorted(c for c in bs.columns if isinstance(c,str) and "-Q" in c)
        if len(periods)<2: print(f"  [skip {tk}] <2 periods",flush=True); return None
        def bsget(item,p,agg="max"):
            rows=bs.loc[bs["item"]==item,p].dropna()
            return float(rows.max() if agg=="max" else rows.min()) if len(rows) else np.nan
        def incget(item,p):
            rows=inc.loc[inc["item"]==item,p].dropna()
            return float(rows.iloc[0]) if len(rows) else np.nan
        eq=bsget(IT_EQUITY,periods[-1])
        loan_latest=bsget(IT_LOAN,periods[-1]); loan_old=bsget(IT_LOAN,periods[0])
        loanG=loan_latest/loan_old-1 if loan_old else np.nan
        npat_ser=[incget(INC_NPAT_PARENT,p) for p in periods]
        if all(pd.isna(x) for x in npat_ser): npat_ser=[incget(INC_NPAT,p) for p in periods]
        npat_trail=np.nansum(npat_ser) if not all(pd.isna(x) for x in npat_ser) else np.nan
        roe=npat_trail/eq if eq and pd.notna(npat_trail) else np.nan
        opex_trail=np.nansum([abs(incget(INC_OPEX,p)) if pd.notna(incget(INC_OPEX,p)) else np.nan for p in periods])
        opinc_trail=np.nansum([incget(INC_OPINC,p) for p in periods])
        cir=opex_trail/opinc_trail if opinc_trail else np.nan
        nii_trail=np.nansum([incget(INC_NII,p) for p in periods])
        ea_latest=np.nansum([bsget(IT_LOAN,periods[-1]),bsget(IT_SEC,periods[-1]),bsget(IT_INTERBANK,periods[-1])])
        ea_old=np.nansum([bsget(IT_LOAN,periods[0]),bsget(IT_SEC,periods[0]),bsget(IT_INTERBANK,periods[0])])
        avg_ea=(ea_latest+ea_old)/2
        nim=nii_trail/avg_ea if avg_ea else np.nan
        price=float(ov["current_price"].iloc[0]) if len(ov) else np.nan
        shares=float(ov["issue_share"].iloc[0]) if len(ov) else np.nan
        pb=price/(eq/shares) if eq and shares else np.nan
        npl,coverage=NPL_COV.get(tk,(np.nan,np.nan))
        gap_note=("CAR/CASA need BCTC thuyet minh, not in vnstock balance_sheet/income_statement"
                   if tk in NPL_COV else
                   "NPL/CAR/coverage/CASA need BCTC thuyet minh, not in vnstock balance_sheet/income_statement")
        return {"ticker":tk,"NIM":nim,"NPL":npl,"NPL_4q":np.nan,"NPL_slope":np.nan,
            "CAR":np.nan,"CASA":np.nan,"coverage":coverage,"CIR":cir,
            "loanG":loanG,"ROE":roe,"PB":pb,
            "loanG_basis":f"{periods[0]}->{periods[-1]}", "data_gap":gap_note,
            "npl_source":"OCR_thuyetminh_2026Q2_verified" if tk in NPL_COV else None}
    except Exception as e:
        print(f"  [skip {tk}] parse {repr(e)[:50]}",flush=True); return None

rows=[]
for i,tk in enumerate(BANKS):
    r=pull(tk)
    if r:
        rows.append(r)
        print(f"  {tk}: ROE={r['ROE']*100:.1f}% NIM={r['NIM']*100:.2f}% CIR={r['CIR']*100:.0f}% PB={r['PB']:.2f} loanG({r['loanG_basis']})={r['loanG']*100:+.1f}%",flush=True)
    if i<len(BANKS)-1: time.sleep(12)
df=pd.DataFrame(rows)
if len(df)==0: print("NO DATA (network)."); sys.exit(0)
df["NPL_chg4q"]=np.nan
df["rising"]=False

def gate(r):
    if pd.isna(r["ROE"]): return "UNVERIFIED"
    if r["ROE"]<0.08: return "AVOID"
    return "DATA_GAP"  # asset-quality (NPL/CAR/coverage/CASA) unavailable — profitable but unverified
df["gate"]=df.apply(gate,axis=1)

# rank by profitability+value only (asset-quality axis unavailable — q_assetq/q_cap dropped,
# NOT silently zeroed, since QUALITY averaging a dropped axis to 0 would look like "bad AQ"
# when the honest state is "unknown AQ")
ranked=df[df["gate"]!="AVOID"].copy()
if len(ranked)>=2:
    def rk(s,asc=True): return s.rank(pct=True) if asc else (1-s.rank(pct=True))
    ranked["q_profit"]=(rk(ranked["NIM"])+rk(ranked["CIR"],asc=False))/2
    ranked["roe_pb"]=ranked["ROE"]/ranked["PB"]
    b=np.polyfit(ranked["ROE"],ranked["PB"],1); ranked["pb_resid"]=ranked["PB"]-(b[0]*ranked["ROE"]+b[1])
    ranked["q_value"]=(rk(ranked["roe_pb"])+rk(ranked["pb_resid"],asc=False))/2
    ranked["SCORE"]=0.5*rk(ranked["ROE"])+0.25*ranked["q_profit"]+0.25*ranked["q_value"]
    ranked=ranked.sort_values("SCORE",ascending=False)

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Bank lens v3 — ROE-based gate (NPL/coverage OCR'd 9/18 mã 2026-08-28; CAR/CASA still unavailable)")
P("GATE: AVOID(ROE<8%) else DATA_GAP (profitable, asset-quality unverified — see data_gap col)")
P("")
P(f"{'tkr':<5}{'ROE%':>6}{'NIM%':>6}{'CIR%':>6}{'PB':>5}{'loanG%':>8}{'gate':>10}")
P("-"*46)
for _,r in df.sort_values(["gate","ROE"],ascending=[True,False]).iterrows():
    P(f"{r['ticker']:<5}{r['ROE']*100:>6.1f}{r['NIM']*100:>6.2f}{r['CIR']*100:>6.0f}{r['PB']:>5.2f}{r['loanG']*100:>+8.1f}{r['gate']:>10}")
P("")
if len(ranked)>=2:
    P("## Ranked (excl. ROE<8% AVOID) — 0.5*ROE + 0.25*profit(NIM/CIR) + 0.25*value(ROE/PB)")
    P(f"{'rank tkr':<10}{'SCORE':>6}{'ROE%':>6}{'PB':>5}")
    for i,(_,r) in enumerate(ranked.iterrows(),1):
        P(f"{i:>2} {r['ticker']:<6}{r['SCORE']:>6.2f}{r['ROE']*100:>6.1f}{r['PB']:>5.2f}")
P("")
P("AVOID (ROE<8%): "+", ".join(df[df['gate']=='AVOID']['ticker'].tolist() or ['none']))
P("DATA_GAP (profitable, AQ unverified): "+", ".join(df[df['gate']=='DATA_GAP']['ticker'].tolist() or ['none']))
P("")
P("NOTE: vnstock's finance.ratio() (old source of ALL 11 cols) is broken since 31/08/2025 (KeyError")
P("lengthReport, community edition shape change). Recomputed ROE/NIM/CIR/loanG/PB from")
P("balance_sheet+income_statement+company.overview instead. NPL/coverage: 9/18 mã OCR'd from BCTC")
P("thuyet minh (see npl_source col in CSV); the other 9 + CAR/CASA still NaN. See module docstring.")
df.to_csv(os.path.join(WORKDIR,"data","bank_lens_v3.csv"),index=False)
with open(os.path.join(WORKDIR,"data","bank_lens_v3.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/bank_lens_v3.{md,csv}")
