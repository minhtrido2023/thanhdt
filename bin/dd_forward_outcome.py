#!/usr/bin/env python3
"""dd_forward_outcome.py — CHẨN ĐOÁN: giá/tâm (r) tại lúc ghi sổ DD → lợi suất sau 63/126/252 phiên.

CHỈ ĐỌC: sổ `kb/dd_price_zones.json` + BQ `tav2_bq.ticker` (lịch sử, KHÔNG same-day — §6) +
`data/benchmark/vnindex_tr_daily.csv`. Chỉ ghi `outcomes.csv` + `summary.md`. Không đổi luật, không wire.

QUY ƯỚC (khai trong summary.md):
  * Mỗi (ticker, dd_date) lấy entry CUỐI = (rev cao nhất; hoà → recorded_at muộn nhất). rev=None ⇒ 1.
  * r = price_ref / center tại thời điểm ghi sổ (entry cuối). center rỗng ⇒ loại khỏi nhóm r.
  * PIT/T+1: phiên VÀO = phiên giao dịch ĐẦU TIÊN SAU max(ngày recorded_at theo ICT, price_date, dd_date).
    Giá vào = Close phiên đó. (Ghi sổ lúc nào cũng vào phiên SAU ngày ghi — bảo thủ, kể cả ghi trong phiên.)
  * Lợi suất h phiên = Close[i+h]/Close[i]-1, i = phiên vào, lịch phiên = ngày có dòng VNINDEX trong BQ.
    Chỉ tính khi i+h đã có dòng; còn lại 'chua_du'. Thiếu dòng giá mã tại i hoặc i+h ⇒ 'thieu_gia'.
  * `Close` BQ = hồi tố cổ tức+tách (vintage hôm nay) ⇒ Close/Close ≈ TOTAL-RETURN gần đúng. Đây là
    tầng PHÁT HIỆN/chẩn đoán, KHÔNG phải số báo cáo §21; sự kiện chưa đối soát sổ broker.
  * VNINDEX cùng kỳ: giá (BQ) và TR gộp (`tr_gross`, rổ HOSE, 5 phiên cuối provisional).
    excess = lợi suất mã − TR VNINDEX (cùng hệ tổng-lợi-suất với Close hồi tố).
"""
import argparse, csv, datetime as dt, json, math, os, statistics, subprocess, io
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
HERE = os.path.dirname(os.path.abspath(__file__))
MIKE = os.path.dirname(HERE)
WC = os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude")
DEF_LEDGER = os.path.join(MIKE, "kb", "dd_price_zones.json")
DEF_OUT = os.path.join(MIKE, "agents", "Taylor", "research", "dd_label_20261124", "forward")
VNI_TR = os.path.join(WC, "data", "benchmark", "vnindex_tr_daily.csv")
HORIZONS = (63, 126, 252)
OFFICIAL_EVAL = "2027-03-31"
N_INDEP_MIN = 30   # ≥30 ngày-DD độc lập CÓ KẾT QUẢ mới được kết luận


# ---------------------------------------------------------------- sổ
def load_entries(path):
    return json.load(open(path))["entries"]


def pick_last(entries):
    """entry cuối cho mỗi (ticker, dd_date)."""
    best = {}
    for e in entries:
        k = (e["ticker"], e["dd_date"])
        key = (e.get("rev") or 1, e.get("recorded_at") or "")
        if k not in best or key > best[k][0]:
            best[k] = (key, e)
    return [v[1] for v in sorted(best.values(), key=lambda x: (x[1]["dd_date"], x[1]["ticker"]))]


def zone_label(e):
    lo, hi, p = e.get("zone_low"), e.get("zone_high"), e.get("price_ref")
    if p is None or lo is None or hi is None:
        return "KHONG_RO"
    return "DUOI" if p < lo else ("TREN" if p > hi else "TRONG")


def r_bin(r):
    if r is None:
        return "KHONG_CO_TAM"
    return "r<=0.85 (luat4)" if r <= 0.85 else ("0.85<r<=1.0" if r <= 1.0 else "r>1.0")


def anchor_date(e):
    """ngày neo PIT = max(ngày recorded_at ICT, price_date, dd_date); trả (date, cờ)."""
    ds = [e["dd_date"]]
    flag = ""
    ra = e.get("recorded_at")
    if ra:
        ds.append(dt.datetime.fromisoformat(ra).astimezone(ICT).date().isoformat())
    else:
        flag = "recorded_at_missing"
    if e.get("price_date"):
        ds.append(e["price_date"])
    return max(ds), flag


# ---------------------------------------------------------------- giá
def bq_prices(tickers, d0, bq_runner=None):
    sql = ("SELECT t.ticker AS ticker, FORMAT_DATE('%F', t.time) AS d, t.Close AS close, t.Price AS price "
           "FROM tav2_bq.ticker AS t WHERE t.time >= DATE '{0}' AND t.ticker IN ({1})"
           ).format(d0, ",".join("'%s'" % x for x in sorted(set(tickers))))
    cmd = ("source %s/wc_env.sh >/dev/null 2>&1; bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 "
           "--format=csv --max_rows=1000000 \"$SQL\"" % WC)
    r = subprocess.run(["bash", "-c", cmd], env=dict(os.environ, SQL=sql), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("bq lỗi: %s" % r.stderr[-500:])
    out = {}
    for row in csv.DictReader(io.StringIO(r.stdout)):
        out.setdefault(row["ticker"], {})[row["d"]] = (float(row["close"]) if row["close"] else None,
                                                       float(row["price"]) if row["price"] else None)
    return out


def load_vni_tr(path=VNI_TR):
    d = {}
    for row in csv.DictReader(open(path)):
        d[row["date"]] = float(row["tr_gross"])
    return d


# ---------------------------------------------------------------- lõi tính
def compute(picked, series, vni_tr, horizons):
    """series[ticker][date]=(close,price); series['VNINDEX'] = lịch. Trả list dict."""
    cal = sorted(series["VNINDEX"])
    rows = []
    for e in picked:
        a, flag = anchor_date(e)
        # phiên vào = phiên đầu tiên SAU ngày neo (chặt)
        nxt = [i for i, d in enumerate(cal) if d > a]
        r = (e["price_ref"] / e["center"]) if (e.get("center") and e.get("price_ref")) else None
        row = dict(ticker=e["ticker"], dd_date=e["dd_date"], rev=e.get("rev") or 1,
                   recorded_at=e.get("recorded_at") or "", price_date=e.get("price_date") or "",
                   center=e.get("center"), price_ref=e.get("price_ref"),
                   r=(round(r, 4) if r is not None else ""), r_bin=r_bin(r), zone=zone_label(e),
                   skeptic_final=e.get("skeptic_final"), flag=flag, anchor=a)
        if not nxt:
            row.update(entry_session="", entry_close="")
            for h in horizons:
                row.update({"st_%d" % h: "chua_co_phien_vao"})
            rows.append(row)
            continue
        i = nxt[0]
        ent = cal[i]
        c0 = series.get(e["ticker"], {}).get(ent, (None, None))[0]
        row.update(entry_session=ent, entry_close=c0 if c0 is not None else "")
        for h in horizons:
            j = i + h
            if j >= len(cal):
                row["st_%d" % h] = "chua_du"
                continue
            ex = cal[j]
            c1 = series.get(e["ticker"], {}).get(ex, (None, None))[0]
            if c0 is None or c1 is None:
                row["st_%d" % h] = "thieu_gia"
                continue
            ret = c1 / c0 - 1
            vp = series["VNINDEX"][ex][0] / series["VNINDEX"][ent][0] - 1
            tr0, tr1 = vni_tr.get(ent), vni_tr.get(ex)
            vt = (tr1 / tr0 - 1) if (tr0 and tr1) else None
            row["st_%d" % h] = "ok"
            row["exit_%d" % h] = ex
            row["ret_%d" % h] = round(ret, 5)
            row["vni_px_%d" % h] = round(vp, 5)
            row["vni_tr_%d" % h] = round(vt, 5) if vt is not None else ""
            row["excess_%d" % h] = round(ret - vt, 5) if vt is not None else ""
        rows.append(row)
    return rows


def lookahead_check(picked, series):
    """(5) price_ref có phải giá thật tại price_date không (so Price thô BQ) + chênh recorded_at/price_date."""
    n_px = n_match = n_nobq = n_after_dd = n_rec_before_px = 0
    for e in picked:
        if e.get("price_date") and e["price_date"] > e["dd_date"]:
            n_after_dd += 1
        ra = e.get("recorded_at")
        if ra and e.get("price_date") and dt.datetime.fromisoformat(ra).astimezone(ICT).date().isoformat() < e["price_date"]:
            n_rec_before_px += 1
        if not e.get("price_ref") or not e.get("price_date"):
            continue
        n_px += 1
        pr = series.get(e["ticker"], {}).get(e["price_date"], (None, None))[1]
        if pr is None:
            n_nobq += 1
        elif abs(pr / e["price_ref"] - 1) <= 0.005:
            n_match += 1
    return dict(n_with_px=n_px, n_match_raw_price=n_match, n_no_bq_row=n_nobq,
                n_price_date_after_dd_date=n_after_dd, n_recorded_before_price_date=n_rec_before_px)


# ---------------------------------------------------------------- thống kê
def _mean(x): return sum(x) / len(x) if x else None
def _med(x): return statistics.median(x) if x else None
def f(x, p=1): return "—" if x is None else ("%+.*f%%" % (p, 100 * x))


def group_stats(rows, h, keyf):
    g = {}
    for r in rows:
        g.setdefault(keyf(r), []).append(r)
    out = []
    for k in sorted(g):
        rr = g[k]
        ok = [x for x in rr if x["st_%d" % h] == "ok"]
        ex = [x["excess_%d" % h] for x in ok if x.get("excess_%d" % h) not in ("", None)]
        out.append(dict(group=k, n_so=len(rr), n_ma=len({x["ticker"] for x in rr}),
                        n_dd_date=len({x["dd_date"] for x in rr}),
                        n_ok=len(ok), n_ma_ok=len({x["ticker"] for x in ok}),
                        n_dd_date_ok=len({x["dd_date"] for x in ok}),
                        mean_ret=_mean([x["ret_%d" % h] for x in ok]), med_ret=_med([x["ret_%d" % h] for x in ok]),
                        mean_ex=_mean(ex), med_ex=_med(ex),
                        hit=(sum(1 for v in ex if v > 0) / len(ex) if ex else None)))
    return out


def sigma_hist(tickers, series_long, vni_tr, h):
    """σ lợi suất vượt VNINDEX-TR h phiên của chính các mã DD trong lịch sử (KHÔNG phải outcome sổ DD)."""
    cal = sorted(series_long["VNINDEX"])
    xs = []
    for t in tickers:
        s = series_long.get(t, {})
        for i in range(0, len(cal) - h, 5):
            a, b = cal[i], cal[i + h]
            if a in s and b in s and s[a][0] and s[b][0] and vni_tr.get(a) and vni_tr.get(b):
                xs.append(s[b][0] / s[a][0] - 1 - (vni_tr[b] / vni_tr[a] - 1))
    return (statistics.pstdev(xs), len(xs)) if len(xs) > 30 else (None, len(xs))


def approx_calendar_after(last_day, n):
    """lịch phiên TƯƠNG LAI xấp xỉ: T2–T6, bỏ 4–12/02/2027 (Tết ước lượng) — CHỈ cho 'mốc đủ' (ước lượng)."""
    d = dt.date.fromisoformat(last_day)
    out = []
    while len(out) < n:
        d += dt.timedelta(days=1)
        if d.weekday() < 5 and not (dt.date(2027, 2, 4) <= d <= dt.date(2027, 2, 12)) and d != dt.date(2027, 1, 1):
            out.append(d.isoformat())
    return out


def maturity(rows, cal, h):
    """ngày (ước lượng) mỗi entry đủ h phiên."""
    last = cal[-1]
    fut = approx_calendar_after(last, h + 5)
    full = cal + fut
    res = {}
    for r in rows:
        es = r.get("entry_session") or next((d for d in full if d > r["anchor"]), None)
        if not es:
            continue
        i = full.index(es) if es in full else None
        if i is not None and i + h < len(full):
            res[(r["ticker"], r["dd_date"])] = full[i + h]
    return res


# ---------------------------------------------------------------- báo cáo
def build_summary(rows, picked, lk, series, vni_tr, horizons, ledger_path, n_raw, series_long, today):
    L = []
    cal = sorted(series["VNINDEX"])
    L.append("# DD forward outcome — chẩn đoán giá/tâm → lợi suất sau 63/126/252 phiên")
    L.append("")
    L.append("_Sinh bởi `bin/dd_forward_outcome.py` ngày %s · lịch BQ tới %s · CHẨN ĐOÁN, không đổi luật, không wire._" % (today, cal[-1]))
    L.append("**Mốc đánh giá chính thức: %s.**" % OFFICIAL_EVAL)
    L.append("")
    L.append("## Quy ước (đọc trước khi dùng số)")
    L.append("- Sổ `%s`: %d entry thô → **%d** (mã, dd_date) sau khi lấy entry CUỐI (rev cao nhất; hoà → recorded_at muộn nhất)." %
             (os.path.relpath(ledger_path, MIKE) if ledger_path.startswith(MIKE) else ledger_path, n_raw, len(picked)))
    L.append("- r = price_ref / center tại lúc ghi sổ. Thiếu tâm ⇒ nhóm `KHONG_CO_TAM`.")
    L.append("- PIT/T+1: phiên vào = phiên giao dịch đầu tiên SAU max(ngày recorded_at ICT, price_date, dd_date); giá vào = Close phiên đó.")
    L.append("- Lợi suất h phiên giao dịch (lịch = ngày có dòng VNINDEX trong BQ). `Close` BQ hồi tố cổ tức+tách ⇒ **total-return gần đúng** (tầng phát hiện, chưa đối soát broker — không phải số §21).")
    L.append("- excess = lợi suất mã − VNINDEX **TR gộp** (`vnindex_tr_daily.csv`, 5 phiên cuối provisional). VNINDEX giá cũng có trong CSV.")
    L.append("- Nhãn vùng DƯỚI/TRONG/TRÊN suy cơ học từ zone_low/zone_high vs price_ref (không parse chữ).")
    L.append("")
    L.append("## Độ phủ kết quả (trung thực)")
    L.append("| h | có kết quả / tổng entry | chưa đủ kỳ | chưa có phiên vào (neo ≥ phiên cuối BQ) | thiếu giá | ngày-DD độc lập có kết quả |")
    L.append("|---|---|---|---|---|---|")
    for h in horizons:
        ok = [r for r in rows if r["st_%d" % h] == "ok"]
        L.append("| %d | %d / %d | %d | %d | %d | %d / %d |" % (
            h, len(ok), len(rows), sum(1 for r in rows if r["st_%d" % h] == "chua_du"),
            sum(1 for r in rows if r["st_%d" % h] == "chua_co_phien_vao"),
            sum(1 for r in rows if r["st_%d" % h] == "thieu_gia"),
            len({r["dd_date"] for r in ok}), len({r["dd_date"] for r in rows})))
    L.append("")
    L.append("Phân bố ngày DD: %d ngày-DD khác nhau, %d mã, khoảng %s → %s; số THÁNG lịch độc lập: %d." % (
        len({r["dd_date"] for r in rows}), len({r["ticker"] for r in rows}),
        min(r["dd_date"] for r in rows), max(r["dd_date"] for r in rows), len({r["dd_date"][:7] for r in rows})))
    L.append("")
    # nhóm r + vùng (n sổ luôn hiện; thống kê chỉ khi có kết quả)
    for title, keyf in (("Nhóm theo r (luật 4: r ≤ 0,85)", lambda r: r["r_bin"]), ("Nhóm theo nhãn vùng", lambda r: r["zone"])):
        L.append("## %s" % title)
        L.append("| h | nhóm | n sổ | n mã | n ngày-DD | n có KQ | mã có KQ | ngày-DD có KQ | TB ret | TB excess | trung vị excess | tỉ lệ thắng VNI-TR |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for h in horizons:
            for s in group_stats(rows, h, keyf):
                L.append("| %d | %s | %d | %d | %d | %d | %d | %d | %s | %s | %s | %s |" % (
                    h, s["group"], s["n_so"], s["n_ma"], s["n_dd_date"], s["n_ok"], s["n_ma_ok"], s["n_dd_date_ok"],
                    f(s["mean_ret"]), f(s["mean_ex"]), f(s["med_ex"]),
                    "—" if s["hit"] is None else "%.0f%%" % (100 * s["hit"])))
        L.append("")
    # kết luận
    nd = {h: len({r["dd_date"] for r in rows if r["st_%d" % h] == "ok"}) for h in horizons}
    L.append("## Kết luận")
    concl = [h for h in horizons if nd[h] >= N_INDEP_MIN]
    if not concl:
        L.append("**KHÔNG KẾT LUẬN.** Ngày-DD độc lập có kết quả: %s (cần ≥ %d, hoặc dùng khối tháng). Số trong bảng trên (nếu có) chỉ là mô tả, không phải bằng chứng." %
                 (", ".join("h%d=%d" % (h, nd[h]) for h in horizons), N_INDEP_MIN))
    else:
        L.append("Đủ ngưỡng N độc lập cho h=%s — xem bảng; vẫn cần quant-skeptic trước khi dùng." % concl)
    L.append("")
    # MDE
    L.append("## MDE và mốc dữ liệu đủ (ƯỚC LƯỢNG)")
    tick = sorted({r["ticker"] for r in rows})
    vt = load_vni_tr() if vni_tr is None else vni_tr
    for h in horizons:
        sg, ns = sigma_hist(tick, series_long, vt, h)
        if sg is None:
            L.append("- h=%d: σ không đủ dữ liệu lịch sử (ns=%d)." % (h, ns))
            continue
        mats = maturity(rows, cal, h)
        n_dd_mat = sorted({(r["dd_date"], mats[(r["ticker"], r["dd_date"])]) for r in rows if (r["ticker"], r["dd_date"]) in mats})
        dd_dates = sorted({r["dd_date"] for r in rows})
        # ngày mà TẤT CẢ ngày-DD hiện có đã đủ kỳ
        last_ready = max((m for _, m in n_dd_mat), default="?")
        mde = lambda n1, n2: 2.8 * sg * math.sqrt(1.0 / n1 + 1.0 / n2)
        n_all = len(dd_dates)
        L.append("- h=%d: σ(excess, ĐO từ lịch sử %d mã DD, bước 5 phiên chồng lấn, %d mẫu — KHÔNG phải outcome sổ DD) = %.1f%%. "
                 "MDE 80%% power α=0,05 hai phía, so 2 nhóm chia đôi %d ngày-DD hiện có (**ước lượng**, coi mỗi ngày-DD là 1 đơn vị độc lập — lạc quan vì cùng mùa BCTC): ≈ %.1f điểm %%. "
                 "Ngày-DD hiện có đủ kỳ h=%d **tới ~%s** (ước lượng, lịch xấp xỉ T2–T6 trừ Tết 4–12/02/2027). "
                 "Cần ≥%d ngày-DD độc lập: hiện chỉ %d ngày-DD ⇒ cần thêm ≥%d ngày-DD MỚI (DD mới) cộng thời gian chờ h phiên."
                 % (h, len(tick), ns, 100 * sg, n_all, 100 * mde(n_all // 2, n_all - n_all // 2) if n_all >= 4 else float("nan"),
                    h, last_ready, N_INDEP_MIN, n_all, max(0, N_INDEP_MIN - n_all)))
    parts = []
    for h in horizons:
        m = maturity(rows, cal, h)
        parts.append("h=%d: %d/%d entry đủ kỳ trước mốc" % (h, sum(1 for v in m.values() if v <= OFFICIAL_EVAL), len(rows)))
    L.append("- Tại mốc %s (**ước lượng**, lịch phiên tương lai xấp xỉ): %s." % (OFFICIAL_EVAL, "; ".join(parts)))
    L.append("")
    L.append("## Kiểm look-ahead (mục 5)")
    L.append("- price_ref có dòng BQ `Price` thô tại price_date: %d/%d entry; khớp ≤0,5%%: **%d** (khớp = price_ref là giá thật phiên đó, không phải số điền sau)." %
             (lk["n_with_px"] - lk["n_no_bq_row"], lk["n_with_px"], lk["n_match_raw_price"]))
    L.append("- Không có dòng BQ tại price_date (mã/ngày thiếu): %d." % lk["n_no_bq_row"])
    L.append("- Entry cuối có price_date SAU dd_date: %d/%d (đã cập nhật giá khi hiệu đính — chấp nhận được vì phiên vào được neo theo max(recorded_at, price_date, dd_date))." %
             (lk["n_price_date_after_dd_date"], len(picked)))
    L.append("- recorded_at (ngày ICT) TRƯỚC price_date: **%d** (>0 = giá điền trước ngày giá — lỗi PIT)." % lk["n_recorded_before_price_date"])
    L.append("- ⚠️ r dùng center ENTRY CUỐI: center có thể đã hiệu chỉnh sau phản biện/sau khi giá đã di chuyển (recorded_at trễ dd_date tới vài ngày; vd entry rev>1 ghi sau BCTC). Phiên vào neo theo recorded_at nên KHÔNG nhìn trước giá sau recorded_at, nhưng center cuối có thể phản ánh thông tin hiệu đính sau dd_date. %d entry thiếu center, %d entry thiếu recorded_at (dùng dd_date làm neo, cờ `recorded_at_missing`)." % (
        sum(1 for e in picked if not e.get("center")), sum(1 for e in picked if not e.get("recorded_at"))))
    L.append("- ⚠️ Close hồi tố vintage hôm nay: lợi suất mỗi kỳ không bị double-count (một lần Close/Close), nhưng sự kiện cổ tức/tách chưa đối soát broker (§21).")
    L.append("")
    L.append("## Tái lập")
    L.append("`python3 mike/bin/dd_forward_outcome.py` (đọc ledger live + BQ read-only). Selfcheck: `python3 mike/bin/dd_forward_outcome_selfcheck.py`.")
    return "\n".join(L) + "\n"


def write_csv(rows, horizons, path):
    cols = ["ticker", "dd_date", "rev", "recorded_at", "price_date", "anchor", "flag", "center", "price_ref", "r", "r_bin",
            "zone", "skeptic_final", "entry_session", "entry_close"]
    for h in horizons:
        cols += ["st_%d" % h, "exit_%d" % h, "ret_%d" % h, "vni_px_%d" % h, "vni_tr_%d" % h, "excess_%d" % h]
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=DEF_LEDGER)
    ap.add_argument("--out-dir", default=DEF_OUT)
    ap.add_argument("--horizons", default=",".join(map(str, HORIZONS)))
    ap.add_argument("--post-bus", action="store_true", help="ghi 1 dòng finding lên bus CHỈ khi đủ N độc lập")
    a = ap.parse_args()
    horizons = tuple(int(x) for x in a.horizons.split(","))
    entries = load_entries(a.ledger)
    picked = pick_last(entries)
    d0 = min(e["dd_date"] for e in picked)
    d0 = (dt.date.fromisoformat(d0) - dt.timedelta(days=20)).isoformat()
    tick = sorted({e["ticker"] for e in picked}) + ["VNINDEX"]
    series = bq_prices(tick, d0)
    series_long = bq_prices(tick, "2023-06-01")   # cho σ lịch sử (MDE)
    vni_tr = load_vni_tr()
    rows = compute(picked, series, vni_tr, horizons)
    lk = lookahead_check(picked, series)
    os.makedirs(a.out_dir, exist_ok=True)
    write_csv(rows, horizons, os.path.join(a.out_dir, "outcomes.csv"))
    today = dt.datetime.now(ICT).date().isoformat()
    s = build_summary(rows, picked, lk, series, vni_tr, horizons, a.ledger, len(entries), series_long, today)
    tmp = os.path.join(a.out_dir, "summary.md.tmp")
    open(tmp, "w").write(s)
    os.replace(tmp, os.path.join(a.out_dir, "summary.md"))
    nd = {h: len({r["dd_date"] for r in rows if r["st_%d" % h] == "ok"}) for h in horizons}
    print("entries thô=%d cuối=%d | độc lập có KQ: %s | out=%s" % (len(entries), len(picked), nd, a.out_dir))
    if a.post_bus and any(v >= N_INDEP_MIN for v in nd.values()):
        subprocess.run([os.path.join(MIKE, "bin", "append_event.sh"), "Taylor", "finding", "dd-forward-outcome-monthly",
                        json.dumps({"n_dd_date_ok": nd, "measured_by": "dd_forward_outcome.py → %s/summary.md" % a.out_dir})])


if __name__ == "__main__":
    main()
