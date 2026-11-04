#!/usr/bin/env python3
"""macro_snapshot_asof.py — khối bối cảnh vĩ mô as-of cho Bobby (đọc MÙ) và khối "điều thị trường
chưa tính" của báo cáo DD. Đọc CHỈ tav2_bq.macro_indicator (read-only, KHÔNG tạo object BQ).
DISPLAY-ONLY: không gate/sizing, không chạm macro_state_live.py/DT5G. Snapshot KHÔNG chứa forward return.

PIT: bảng không có ngày công bố ⇒ asof >= observation_date mới nhất của cả bộ series ⇒ "live", dùng dòng
mới nhất, không lag. Ngược lại ("lịch sử") mỗi dòng chỉ hiện nếu observation_date + LAG[series] <= asof.
Series không có trong LAG ⇒ BỎ khỏi snapshot (fail-closed, không đoán). Lỗi BQ / thiếu dữ liệu ⇒ nói thẳng,
không điền số cũ (§29). Hôm nay neo ICT (§16).

Nguồn lag (WebSearch 2026-11-05; lag = số ngày lịch sau observation_date, CỐ Ý lớn hơn lịch thật):
  GSO/NSO: báo cáo KT-XH hằng tháng công bố ~ngày 6 tháng sau (CPI, IIP, bán lẻ, XNK, FDI, khách QT; quý:
    GDP) — https://thesaigontimes.vn/cpi-ca-nuoc-tang-369-sau-11-thang/ , https://www.nso.gov.vn
    (trang cũ nso.gov.vn ghi lịch cuối tháng giai đoạn trước ⇒ sớm hơn, lag 10/15 vẫn bảo thủ).
  S&P Global VN PMI: ngày làm việc đầu tháng sau — https://www.pmi.spglobal.com/Public/Release/ReleaseDates
  ISM: ngày làm việc đầu tháng sau — https://ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/
  NBS PMI TQ: ~ngày cuối tháng tham chiếu — https://www.finlogix.com/calendar/cn/nbs-manufacturing-pmi
  VAMA: ~ngày 9-13 tháng sau — https://www.wardsauto.com/table-vietnam-april-auto-sales-jump-34-pct-yy-industry
  vn_fx_reserves, vn_wages: KHÔNG tìm được lịch ⇒ lag lớn (90 / 60).
Caveat: giá trị lịch sử là bản hiệu chỉnh HIỆN HÀNH (bảng không có vintage, backfill 2026-10-30), không phải số công bố
  lúc đó; lag chỉ chặn việc "thấy sớm hơn ngày công bố", không khôi phục số liệu gốc.
Δ tắt (NO_DELTA): vn_gdp_construction (luỹ kế YTD tới Q4/2023, theo quý từ Q1/2024), vn_fdi Δ3T (luỹ kế YTD reset tháng 1).
Env chỉ dùng test: MACRO_SNAP_TODAY (YYYY-MM-DD).
Exit: 0 ok · 2 lỗi dữ liệu/BQ (không in số).
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

PROJECT = "lithe-record-440915-m9"

# key: (nhóm, nhãn, lag_ngày, kiểu Δ: 'pp' = hiệu tuyệt đối | 'pct' = % thay đổi, max_age_ngày để coi là tươi, ghi chú)
D = 4  # tươi tối đa series hằng ngày (cuối tuần/lễ)
M = 75  # tháng: obs cuối tháng + lag + công bố trễ
Q = 140
SPEC = {
    # chính sách / thanh khoản
    "vn_policy_rate":      ("Chính sách/thanh khoản", "Lãi suất tái cấp vốn SBV (%)", 7, "pp", 400, ""),
    "vn_interbank_3m":     ("Chính sách/thanh khoản", "Liên ngân hàng 3M (%)", 3, "pp", D + 3, "lag 3 (quan sát thực trễ 2 ngày)"),
    # lạm phát
    "vn_cpi_yoy":          ("Lạm phát", "CPI YoY (%)", 10, "pp", M, ""),
    "vn_core_cpi_yoy":     ("Lạm phát", "CPI lõi YoY (%)", 10, "pp", M, ""),
    "vn_cpi_mom":          ("Lạm phát", "CPI MoM (%)", 10, "pp", M, ""),
    # hoạt động
    "vn_mfg_pmi":          ("Hoạt động", "PMI SX VN (điểm)", 7, "pp", M, ""),
    "vn_ind_production_yoy": ("Hoạt động", "Sản xuất CN YoY (%)", 10, "pp", M, ""),
    "vn_retail_sales_yoy": ("Hoạt động", "Bán lẻ YoY (%)", 10, "pp", M, ""),
    "vn_exports":          ("Hoạt động", "Xuất khẩu (tỷ USD/tháng)", 10, "pct", M, ""),
    "vn_imports":          ("Hoạt động", "Nhập khẩu (tỷ USD/tháng)", 10, "pct", M, ""),
    "vn_trade_balance":    ("Hoạt động", "Cán cân thương mại (tỷ USD)", 10, "pp", M, ""),
    "vn_fdi":              ("Hoạt động", "FDI luỹ kế từ đầu năm (tỷ USD)", 10, "pct", M, "luỹ kế YTD, reset mỗi tháng 1 ⇒ chỉ Δ12T (cùng kỳ năm trước), không Δ3T"),
    "vn_gdp_growth_yoy":   ("Hoạt động", "GDP YoY (%)", 15, "pp", Q, ""),
    "vn_gdp_construction": ("Hoạt động", "GDP xây dựng (nghìn tỷ VND)", 15, "pct", Q, "định nghĩa gãy: luỹ kế YTD tới Q4/2023, theo quý từ Q1/2024 ⇒ không in Δ"),
    "vn_car_registrations": ("Hoạt động", "Ô tô đăng ký/bán (xe)", 25, "pct", M, ""),
    "vn_tourist_arrivals": ("Hoạt động", "Khách quốc tế (nghìn)", 10, "pct", M, ""),
    "vn_wages":            ("Hoạt động", "Lương (nghìn VND/tháng)", 60, "pct", Q, "lag không có nguồn lịch"),
    # ngoại sinh / FX
    "vn_usdvnd":           ("Ngoại sinh/FX", "USD/VND", 1, "pct", D, ""),
    "vn_bond_10y":         ("Ngoại sinh/FX", "TPCP 10Y VN (%) — CHỈ TIN Δ", 1, "pp", D, "mức UNVERIFIED lệch VBMA +0,13…0,21pp"),
    "us_bond_2y":          ("Ngoại sinh/FX", "US 2Y (%)", 1, "pp", D, ""),
    "us_bond_10y":         ("Ngoại sinh/FX", "US 10Y (%)", 1, "pp", D, ""),
    "us_dxy":              ("Ngoại sinh/FX", "DXY", 1, "pct", D, ""),
    "cn_usdcny":           ("Ngoại sinh/FX", "USD/CNY", 1, "pct", D, ""),
    "cn_nbs_mfg_pmi":      ("Ngoại sinh/FX", "PMI NBS TQ (điểm)", 3, "pp", M, ""),
    "us_ism_mfg_pmi":      ("Ngoại sinh/FX", "ISM SX Mỹ (điểm)", 7, "pp", M, ""),
    "vn_fx_reserves":      ("Ngoại sinh/FX", "Dự trữ ngoại hối (triệu USD)", 90, "pct", 160, "lag không có nguồn lịch"),
}
LAG = {k: v[2] for k, v in SPEC.items()}
# Δ bị tắt do định nghĩa series gãy/luỹ kế (quét dữ liệu thật 2026-11-05): key -> các Δ không in
NO_DELTA = {"vn_gdp_construction": ("d3", "d12"), "vn_fdi": ("d3",)}
# series CÓ trong bảng nhưng CỐ Ý không đưa vào snapshot (giá thị trường: Bobby đọc mù sẽ nhận ra giai đoạn)
EXCLUDED_ON_PURPOSE = ("us_sp500", "jp_usdjpy")
SPREAD_KEY = "spread_interbank3m_minus_policy"

SECTOR_MAP = [
    ("Bán lẻ (PNJ, MWG…)", "vn_retail_sales_yoy, vn_cpi_yoy, vn_core_cpi_yoy"),
    ("Xây dựng / thép / xi măng", "vn_gdp_construction, vn_ind_production_yoy, vn_fdi"),
    ("BĐS khu công nghiệp", "vn_fdi, vn_ind_production_yoy, vn_mfg_pmi"),
    ("Xuất khẩu / logistics / cảng", "vn_exports, vn_imports, vn_trade_balance, vn_mfg_pmi, cn_nbs_mfg_pmi, cn_usdcny"),
    ("Ngân hàng", "vn_policy_rate, vn_interbank_3m, spread, vn_bond_10y (Δ), vn_usdvnd"),
    ("Tiêu dùng / ô tô / du lịch", "vn_car_registrations, vn_tourist_arrivals, vn_wages, vn_retail_sales_yoy"),
]


def today_ict():
    t = os.environ.get("MACRO_SNAP_TODAY")
    return dt.date.fromisoformat(t) if t else dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()


def months_back(d, n):
    y, m = divmod(d.year * 12 + d.month - 1 - n, 12)
    m += 1
    import calendar
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def fetch(asof, keys=None):
    """→ {series: [(obs_date, value, unit)]} ASC, đã khử trùng (fetched_at mới nhất). Raise RuntimeError khi lỗi."""
    keys = keys or list(SPEC)
    lo = asof - dt.timedelta(days=900)
    sql = ("SELECT t.series_key, CAST(t.observation_date AS STRING) AS d, t.value, t.unit "
           "FROM `%s.tav2_bq.macro_indicator` AS t WHERE t.series_key IN (%s) "
           "AND t.observation_date BETWEEN '%s' AND '%s' "
           "QUALIFY ROW_NUMBER() OVER (PARTITION BY t.series_key, t.observation_date ORDER BY t.fetched_at DESC)=1 "
           "ORDER BY 1,2" % (PROJECT, ",".join("'%s'" % k for k in keys), lo, asof))
    p = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--project_id=" + PROJECT, "--format=json",
                        "--quiet", "--max_rows=100000", sql], capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise RuntimeError("bq rc=%d: %s" % (p.returncode, (p.stderr.strip() or p.stdout.strip() or "<rỗng>")[:400]))
    try:
        js = json.loads(p.stdout or "[]")
    except ValueError as e:
        raise RuntimeError("output bq không phải JSON (%s): %r" % (e, p.stdout[:200]))
    out = {}
    for r in js:
        if r["value"] in (None, ""):
            continue
        out.setdefault(r["series_key"], []).append((dt.date.fromisoformat(r["d"]), float(r["value"]), r.get("unit") or ""))
    return out


def table_max():
    """observation_date lớn nhất của cả bộ series trong bảng (KHÔNG cắt theo asof) — quyết định chế độ live."""
    sql = ("SELECT CAST(MAX(t.observation_date) AS STRING) AS m FROM `%s.tav2_bq.macro_indicator` AS t "
           "WHERE t.series_key IN (%s)" % (PROJECT, ",".join("'%s'" % k for k in SPEC)))
    p = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--project_id=" + PROJECT, "--format=json", "--quiet", sql],
                       capture_output=True, text=True, timeout=90)
    if p.returncode != 0:
        raise RuntimeError("bq(table_max) rc=%d: %s" % (p.returncode, (p.stderr.strip() or p.stdout.strip())[:300]))
    m = json.loads(p.stdout or "[]")
    if not m or not m[0].get("m"):
        raise RuntimeError("không đọc được MAX(observation_date)")
    return dt.date.fromisoformat(m[0]["m"])


def all_series_keys():
    """mọi series_key phân biệt trong bảng (để khai báo series bị bỏ). Raise RuntimeError khi lỗi."""
    sql = "SELECT DISTINCT t.series_key AS k FROM `%s.tav2_bq.macro_indicator` AS t ORDER BY 1" % PROJECT
    p = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--project_id=" + PROJECT, "--format=json", "--quiet",
                        "--max_rows=1000", sql], capture_output=True, text=True, timeout=90)
    if p.returncode != 0:
        raise RuntimeError("bq(all_series_keys) rc=%d: %s" % (p.returncode, (p.stderr.strip() or p.stdout.strip())[:300]))
    return [r["k"] for r in json.loads(p.stdout or "[]")]


def visible(rows, cutoff, lag):
    """dòng mới nhất có obs + lag <= cutoff (lag=0 ⇒ chế độ live)."""
    best = None
    for d, v, u in rows:
        if d + dt.timedelta(days=lag) <= cutoff and (best is None or d > best[0]):
            best = (d, v, u)
    return best


def pick(rows, key, cutoff, live):
    return visible(rows, cutoff, 0 if live else LAG[key])


def delta(cur, old, kind):
    if old is None:
        return None
    if kind == "pct":
        return None if old[1] == 0 else (cur[1] / old[1] - 1) * 100
    return cur[1] - old[1]


def build(data, asof, tmax, all_keys=None):
    """→ dict snapshot. data = fetch(), tmax = table_max(). Thuần hàm (selfcheck dùng)."""
    live = asof >= tmax
    snap = {"asof": asof.isoformat(), "mode": "live" if live else "historical-lag", "series": {}, "missing": [],
            "omitted_no_lag": sorted(set(all_keys or ()) - set(SPEC))}
    c3, c12 = months_back(asof, 3), months_back(asof, 12)
    for k, (grp, label, lag, kind, maxage, note) in SPEC.items():
        rows = data.get(k, [])
        cur = pick(rows, k, asof, live)
        if cur is None:
            snap["missing"].append(k)
            continue
        o3, o12 = pick(rows, k, c3, live), pick(rows, k, c12, live)
        # cùng dòng quan sát (series quý/chậm) ⇒ Δ không có nghĩa, không in 0 giả
        o3 = None if (o3 and o3[0] == cur[0]) else o3
        o12 = None if (o12 and o12[0] == cur[0]) else o12
        nd = NO_DELTA.get(k, ())
        o3 = None if "d3" in nd else o3
        o12 = None if "d12" in nd else o12
        age = (asof - cur[0]).days
        snap["series"][k] = dict(group=grp, label=label, kind=kind, value=cur[1], obs=cur[0].isoformat(),
                                 d3=delta(cur, o3, kind), d12=delta(cur, o12, kind),
                                 obs3=o3[0].isoformat() if o3 else None, obs12=o12[0].isoformat() if o12 else None,
                                 age_days=age, stale=age > maxage, lag=0 if live else lag, note=note)
    # spread
    a, b = data.get("vn_interbank_3m", []), data.get("vn_policy_rate", [])
    def sp(cut):
        x, y = pick(a, "vn_interbank_3m", cut, live), pick(b, "vn_policy_rate", cut, live)
        return None if (x is None or y is None) else (x[1] - y[1], x[0], y[0])
    s0, s3, s12 = sp(asof), sp(c3), sp(c12)
    if s0:
        age = (asof - min(s0[1], s0[2])).days
        snap["series"][SPREAD_KEY] = dict(group="Chính sách/thanh khoản", label="Spread LNH 3M − lãi điều hành (pp)",
                                          kind="pp", value=s0[0], obs="%s/%s" % (s0[1], s0[2]),
                                          d3=None if not s3 else s0[0] - s3[0], d12=None if not s12 else s0[0] - s12[0],
                                          obs3=None, obs12=None, age_days=age, stale=age > 400, lag=0 if live else 7,
                                          note="giả thuyết thanh khoản, chưa kiểm (D2)")
    else:
        snap["missing"].append(SPREAD_KEY)
    if SPREAD_KEY in snap["series"]:
        ser, new = snap["series"], {}
        for k2, v in ser.items():
            if k2 != SPREAD_KEY:
                new[k2] = v
            if k2 == "vn_interbank_3m":
                new[SPREAD_KEY] = ser[SPREAD_KEY]
        snap["series"] = new
    return snap


def fmt(x, kind=None, signed=False):
    if x is None:
        return "n/a"
    s = ("%+.2f" if signed else "%.2f") % x
    return s + ("%" if kind == "pct" and signed else "")


def render_md(snap):
    L = ["## Bối cảnh vĩ mô as-of %s (%s)" % (snap["asof"], snap["mode"]),
         "_Nguồn: tav2_bq.macro_indicator (TradingEconomics, status UNVERIFIED). DISPLAY-ONLY, không chứa forward return. "
         "Δ: `pp` = hiệu tuyệt đối, `%` = % thay đổi. Chế độ historical-lag: dòng chỉ hiện nếu ngày quan sát + độ trễ công bố bảo thủ <= as-of._",
         "_⚠ Giá trị lịch sử là bản hiệu chỉnh HIỆN HÀNH (bảng không có vintage, backfill 2026-10-30), không phải số công bố lúc đó._",
         "_us_sp500, jp_usdjpy bị loại CÓ CHỦ ĐÍCH (giá thị trường — Bobby đọc mù sẽ nhận ra giai đoạn)._", ""]
    grp_prev = None
    for k, s in snap["series"].items():
        if s["group"] != grp_prev:
            L += ["", "### " + s["group"], "", "| Chỉ báo | Giá trị | Ngày QS | Δ3T | Δ12T | Tươi |", "|---|---|---|---|---|---|"]
            grp_prev = s["group"]
        flag = "STALE (%dd)" % s["age_days"] if s["stale"] else "ok (%dd)" % s["age_days"]
        unit = "pp" if s["kind"] == "pp" else "%"
        d3 = "n/a" if s["d3"] is None else fmt(s["d3"], s["kind"], True) + ("" if unit == "%" else "pp")
        d12 = "n/a" if s["d12"] is None else fmt(s["d12"], s["kind"], True) + ("" if unit == "%" else "pp")
        lab = s["label"] + (" ⚠ " + s["note"] if s["note"] else "")
        L.append("| %s | %s | %s | %s | %s | %s |" % (lab, fmt(s["value"]), s["obs"], d3, d12, flag))
    if snap["missing"]:
        L += ["", "**KHÔNG CÓ DỮ LIỆU tại as-of (không điền số cũ):** " + ", ".join(snap["missing"])]
    om = [k for k in snap["omitted_no_lag"] if k not in EXCLUDED_ON_PURPOSE]
    L += ["", "**Ngoài snapshot (không khai lag / không thuộc nhóm):** %d series khác trong bảng bị bỏ (%s)." % (len(om), ", ".join(om))
          if om else "", "",
          "### Ánh xạ ngành → chỉ báo (cho DD)", "", "| Ngành | Chỉ báo |", "|---|---|"]
    L += ["| %s | %s |" % x for x in SECTOR_MAP]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", required=True)
    ap.add_argument("--format", choices=["md", "json"], default="md")
    a = ap.parse_args()
    try:
        asof = dt.date.fromisoformat(a.asof)
        if asof > today_ict():
            raise ValueError("asof %s ở tương lai (hôm nay ICT %s)" % (asof, today_ict()))
        snap = build(fetch(asof), asof, table_max(), all_series_keys())
        if not snap["series"]:
            raise RuntimeError("không có series nào tại as-of")
    except Exception as e:
        print("LỖI macro_snapshot_asof (không in số, KHÔNG phải 'không có biến động'): %s: %s" % (type(e).__name__, e),
              file=sys.stderr)
        return 2
    print(render_md(snap) if a.format == "md" else json.dumps(snap, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
