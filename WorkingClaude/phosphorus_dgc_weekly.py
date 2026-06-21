#!/usr/bin/env python3
"""
phosphorus_dgc_weekly.py — WEEKLY yellow-phosphorus (P4) trend → DGC nhận định
==============================================================================
Why: DGC's real earnings driver is YELLOW PHOSPHORUS (P4), but the 8L cyclical
lens has no clean P4 feed and proxies it with DAP (see cyclical_multi.py:10
"real product = yellow phosphorus P4 (no clean history); DAP = partial proxy").
This script fills that gap on a WEEKLY cadence (not daily — per user request):

  1. Scrape China P4 spot from SunSirs prodetail-708 (solves the HW_CHECK cookie
     wall: fetch stub -> read token -> re-request -> full page).
  2. Forward-accumulate every captured daily print into data/phosphorus_weekly.csv
     (deduped by date), exactly like fetch_bdi_daily.py builds the BDI series.
  3. Pull DGC's latest quarter + valuation from BigQuery (graceful if bq absent).
  4. Render a dated nhận định into data/dgc_phosphorus_watch.md, folding the P4
     trend into DGC's earnings/valuation read (operating-leverage logic).

Run weekly:  python phosphorus_dgc_weekly.py
Outputs:     data/phosphorus_weekly.csv   (price series, appendable)
             data/dgc_phosphorus_watch.md (the living DGC assessment)
"""
import os, re, ssl, sys, subprocess, tempfile
from io import StringIO
import urllib.request
import pandas as pd
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

WORKDIR = os.environ.get("WORKDIR_8L", os.path.dirname(os.path.abspath(__file__)))
DATA    = os.path.join(WORKDIR, "data")
CSV     = os.path.join(DATA, "phosphorus_weekly.csv")
NOTE    = os.path.join(DATA, "dgc_phosphorus_watch.md")
URL     = "https://www.sunsirs.com/uk/prodetail-708.html"
PROJECT = "lithe-record-440915-m9"
BQ      = r"bq"

# --- P4 price-cycle zones (RMB/ton), anchored to the 2021-2026 history ----------
#  trough 2023-25 ~22-26k (DGC GPM compressed, e.g. 2026Q1 GPM 28.9%)
#  mid-cycle ~30-36k | 2022 supercycle 40-50k | 2021 dual-control spike >50k
TROUGH_HI, RECOVERY_HI, MID_HI = 27000, 32000, 38000
PIVOT = 30000  # structural "is the recovery holding?" line
# This-cycle trough = SunSirs beginning-of-March benchmark (news-31680), == chart y-axis min.
# Fallback headline anchor; once the seeded+live CSV spans the trough, the CSV min supersedes it.
CYCLE_TROUGH, CYCLE_TROUGH_WHEN = 24172.67, "đầu 3/2026"


def fetch_p4():
    """Return [{date, price_rmb}] from SunSirs, solving the HW_CHECK cookie wall."""
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
    stub = urllib.request.urlopen(urllib.request.Request(URL, headers=hdr), timeout=30, context=ctx).read().decode("utf-8", "ignore")
    m = re.search(r'var _0x2 = "([0-9a-f]+)"', stub)
    if not m:
        raise RuntimeError("HW_CHECK token not found (page format changed?)")
    h2 = dict(hdr); h2["Cookie"] = "HW_CHECK=" + m.group(1)
    html = urllib.request.urlopen(urllib.request.Request(URL, headers=h2), timeout=30, context=ctx).read().decode("utf-8", "ignore")
    rows = re.findall(r'(\d{4,6}\.\d{2})\s*</td>\s*<td[^>]*>\s*(\d{4}-\d{2}-\d{2})', html)
    if not rows:
        raise RuntimeError("price table not parsed (page format changed?)")
    out = [{"date": d, "price_rmb": float(p)} for p, d in rows]
    # dedupe by date keeping first
    seen = {}; [seen.setdefault(r["date"], r) for r in out]
    return sorted(seen.values(), key=lambda r: r["date"])


def update_csv(rows):
    new = pd.DataFrame(rows); new["src"] = "sunsirs"
    new["fetched"] = new["date"]
    if os.path.exists(CSV):
        old = pd.read_csv(CSV)
        comb = pd.concat([old, new], ignore_index=True).drop_duplicates(subset=["date"], keep="last")
    else:
        comb = new
    comb = comb.sort_values("date").reset_index(drop=True)
    os.makedirs(DATA, exist_ok=True)
    comb.to_csv(CSV, index=False)
    return comb


def trend_metrics(df):
    d = df.copy(); d["date"] = pd.to_datetime(d["date"])
    d = d.sort_values("date").set_index("date")
    s = d["price_rmb"]
    latest = float(s.iloc[-1]); latest_dt = s.index[-1]
    def change_near(target_days, tol):
        # % change vs the data point NEAREST to (latest - target_days), within +/-tol days.
        # Robust to a sparse/seeded series with gaps (won't mislabel a 3-week-old point as "1w").
        target = latest_dt - pd.Timedelta(days=target_days)
        dd = pd.Series((s.index - target).days)
        i = int(dd.abs().idxmin()); ref_dt = s.index[i]
        if ref_dt == latest_dt or abs(int(dd.iloc[i])) > tol:
            return None, None
        return (latest / float(s.iloc[i]) - 1) * 100, ref_dt
    wow, wow_ref = change_near(7, 6)
    mom, mom_ref = change_near(30, 14)
    # "off the cycle low": once the series actually spans the trough, use the real CSV min +
    # its date; else fall back to the known CYCLE_TROUGH anchor.
    csv_lo = float(s.min())
    if len(s) >= 10 and csv_lo <= CYCLE_TROUGH * 1.05:
        trough, trough_when = csv_lo, str(s.idxmin().date())
    else:
        trough, trough_when = CYCLE_TROUGH, CYCLE_TROUGH_WHEN
    off_trough = (latest / trough - 1) * 100
    # weekly = last print of each calendar week, labelled by its actual last trading date
    tmp = s.reset_index(); tmp.columns = ["date", "p"]
    tmp["wk"] = tmp["date"].dt.to_period("W")
    wk = tmp.groupby("wk", as_index=False).last()[["date", "p"]].tail(8)
    if latest >= MID_HI:       zone = ("MID-CAO", "vùng giữa-cao chu kỳ — biên gộp mở rộng mạnh; tiệm cận kịch bản lợi nhuận đột biến 2022")
    elif latest >= RECOVERY_HI: zone = ("MID THUẬN LỢI", "vùng giữa chu kỳ thuận lợi — biên gộp cải thiện rõ, tích cực cho EPS các quý tới")
    elif latest >= TROUGH_HI:   zone = ("HỒI PHỤC", "đang hồi từ đáy — biên bắt đầu cải thiện nhưng chưa mạnh")
    else:                       zone = ("ĐÁY", "vùng đáy chu kỳ — biên DGC bị nén (như Q1/2026)")
    return dict(latest=latest, latest_dt=latest_dt, wow=wow, wow_ref=wow_ref, mom=mom, mom_ref=mom_ref,
                trough=trough, trough_when=trough_when, off_trough=off_trough,
                weekly=wk, zone=zone, above_pivot=latest >= PIVOT)


def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=50'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:300])
    return pd.read_csv(StringIO(r.stdout.strip()))


def dgc_snapshot():
    """Latest DGC quarter + valuation from BQ. Returns dict or None (graceful)."""
    try:
        fin = bq_query("""
        SELECT f.quarter,
          ROUND(f.NP_P0/1e9,0) NP_bil, ROUND((f.NP_P0/NULLIF(f.NP_P4,0)-1)*100,1) NP_yoy,
          ROUND((f.Revenue_P0/NULLIF(f.Revenue_P4,0)-1)*100,1) Rev_yoy,
          ROUND(f.GPM_P0*100,1) GPM, ROUND(f.ROE_Trailing*100,1) ROE, f.FSCORE
        FROM tav2_bq.ticker_financial AS f
        WHERE f.ticker='DGC' ORDER BY f.time DESC LIMIT 1""")
        px = bq_query("""
        SELECT ROUND(t.Close,0) Close, ROUND(t.MA200,0) MA200,
          ROUND((t.Close/NULLIF(t.MA200,0)-1)*100,1) vs_ma200,
          ROUND(t.D_RSI*100,0) RSI, ROUND(t.PE,1) PE, ROUND(t.PB,2) PB, t.time
        FROM tav2_bq.ticker AS t WHERE t.ticker='DGC' ORDER BY t.time DESC LIMIT 1""")
        return {**fin.iloc[0].to_dict(), **px.iloc[0].to_dict()}
    except Exception as e:
        print(f"  [warn] BQ snapshot skipped: {e}")
        return None


def render_note(m, dgc, today_str):
    z_tag, z_desc = m["zone"]
    arrow = "▲" if (m["wow"] or 0) > 0.3 else ("▼" if (m["wow"] or 0) < -0.3 else "→")
    L = []
    L.append(f"# DGC × Phốt pho vàng (P4) — nhận định tuần\n")
    L.append(f"_Cập nhật: {today_str} · nguồn giá: SunSirs prodetail-708 (spot Trung Quốc, benchmark xuất khẩu P4 của DGC)_\n")
    L.append("## 1. Xu hướng giá P4")
    L.append(f"- **Mới nhất:** {m['latest']:,.0f} RMB/tấn ({m['latest_dt'].date()}) {arrow}")
    wow = (f"{m['wow']:+.1f}% (vs {m['wow_ref'].date()})" if m['wow'] is not None else "_đang tích lũy chuỗi_")
    mom = (f"{m['mom']:+.1f}% (vs {m['mom_ref'].date()})" if m['mom'] is not None else "_đang tích lũy chuỗi_")
    L.append(f"- **~1 tuần:** {wow}  ·  **~1 tháng:** {mom}")
    L.append(f"- **So với đáy chu kỳ** (~{m['trough']:,.0f}, {m['trough_when']}): **{m['off_trough']:+.1f}%**")
    L.append(f"- **Vùng chu kỳ:** `{z_tag}` — {z_desc}")
    pivot_txt = ("✅ trên mốc ~30k → phục hồi đang **giữ vững** (cấu trúc tích cực)"
                 if m["above_pivot"] else
                 "⚠️ dưới mốc ~30k → phục hồi **chưa được xác nhận**")
    L.append(f"- **Kiểm tra cấu trúc:** {pivot_txt}")
    L.append("")
    L.append("| Tuần (giá đóng) | P4 (RMB/tấn) |")
    L.append("|---|---|")
    weekly_dates = {str(r["date"].date()) for _, r in m["weekly"].iterrows()}
    if m["trough_when"] not in weekly_dates:   # only show anchor if trough not already in the table
        L.append(f"| {m['trough_when']} _(đáy chu kỳ)_ | {m['trough']:,.0f} |")
    for _, r in m["weekly"].iterrows():
        tag = " _(đáy chu kỳ)_" if str(r["date"].date()) == m["trough_when"] else ""
        L.append(f"| {r['date'].date()}{tag} | {r['p']:,.0f} |")
    L.append("")
    L.append("## 2. Nhận định cho DGC")
    if dgc:
        L.append(f"- **Định giá hiện tại:** giá {dgc['Close']:,.0f} · vs MA200 **{dgc['vs_ma200']:+.1f}%** · "
                 f"PB {dgc['PB']} · PE {dgc['PE']} · RSI {dgc['RSI']:.0f}")
        L.append(f"- **Quý gần nhất ({dgc['quarter']}):** LN {dgc['NP_bil']:,.0f} tỷ ({dgc['NP_yoy']:+.1f}% YoY) · "
                 f"DT {dgc['Rev_yoy']:+.1f}% YoY · GPM {dgc['GPM']}% · ROE_ttm {dgc['ROE']}% · FSCORE {dgc['FSCORE']:.0f}")
    L.append("- **Cơ chế:** DGC là nhà sản xuất P4 chi phí thấp nhất (apatite + thủy điện Lào Cai) → "
             "mỗi đồng giá P4 tăng chảy gần thẳng vào lợi nhuận gộp (đòn bẩy vận hành lớn). Truyền dẫn trễ ~1 quý.")
    # the verdict line keys off the zone + structure
    if m["latest"] >= RECOVERY_HI and m["above_pivot"]:
        verdict = ("**HƯỞNG LỢI** — giá đầu ra đang ở vùng thuận lợi và giữ vững. Nếu duy trì, biên gộp/EPS "
                   "của DGC sẽ cải thiện rõ ở các quý tới (đợt hồi này CHƯA phản ánh hết vào số báo cáo gần nhất).")
    elif m["latest"] >= TROUGH_HI:
        verdict = ("**ĐANG CẢI THIỆN** — giá đã rời đáy nhưng cần giữ trên ~30k để xác nhận. Theo dõi thêm "
                   "trước khi kết luận biên DGC phục hồi bền.")
    else:
        verdict = ("**CHƯA** — giá P4 còn ở đáy, biên DGC tiếp tục bị nén. Chờ tín hiệu đảo chiều của giá đầu ra.")
    L.append(f"- **Kết luận tuần:** {verdict}")
    L.append("- **Lưu ý (8L):** route DGC = CYCLICAL; lăng kính cyclical của 8L proxy bằng DAP (`WAIT`) — "
             "feed P4 này là tín hiệu trực tiếp & sớm hơn proxy. Cảnh giác đợt tăng do thiếu điện mùa khô "
             "(nhất thời, dễ revert) vs cầu/kỷ luật cung (cấu trúc, bền). Mùa mưa mà giá vẫn tăng = đáng chú ý.")
    L.append("")
    txt = "\n".join(L)
    with open(NOTE, "w", encoding="utf-8") as f:
        f.write(txt)
    return txt


def main():
    # WORKDIR has no clock dependency we control; derive 'today' from the latest data date
    rows = fetch_p4()
    df = update_csv(rows)
    m = trend_metrics(df)
    today_str = str(m["latest_dt"].date())
    dgc = dgc_snapshot()
    txt = render_note(m, dgc, today_str)
    print(f"P4 {m['latest']:,.0f} RMB/tấn ({m['latest_dt'].date()})  WoW {m['wow'] if m['wow'] is None else round(m['wow'],1)}%  "
          f"zone={m['zone'][0]}  pivot={'above' if m['above_pivot'] else 'below'}")
    print(f"-> {CSV} now {len(df)} daily prints ({df['date'].iloc[0]} .. {df['date'].iloc[-1]})")
    print(f"-> {NOTE} written")
    print("\n" + txt)


if __name__ == "__main__":
    main()
