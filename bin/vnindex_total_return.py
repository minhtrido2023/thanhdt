#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VN-Index CÓ CỔ TỨC tự dựng — thư viện + CLI (quỹ mở bước 4, SPEC phần A).

HOSE KHÔNG công bố bản tổng thu nhập (TRI) của VN-Index (factsheet HOSE-Index 03/2025: chỉ VN30/
VN100/VNMidcap/VNSmallcap/VNAllshare có TRI). Chuỗi này = chỉ số GIÁ CHÍNH THỨC + điểm % cổ tức tự
ước. Nghiên cứu + kiểm chứng chéo: `agents/Taylor/research/fund_step4_20261014/README.md`; nguyên mẫu
hành vi tham chiếu `tr_build.py` cùng thư mục (bản này phải ra đúng số của nó trên cùng dữ liệu).

CÔNG THỨC (một chỗ: `div_yield_daily` + `chain`)
  Rổ ngày t  = mã đang niêm yết HOSE ngày t (bảng sàn theo vintage `hose_membership_*.json`), có giá
               phiên t-1 (phiên t-1 của mã PHẢI là phiên liền trước của chỉ số) và số CP lưu hành.
  Trọng số   = vốn hoá ĐẦY ĐỦ phiên t-1 = Price_{t-1} × OShares_{t-1} (VN-Index không free-float).
  y_t        = Σ OShares_{i,t-1} × DIV_{i,t} / Σ vốn hoá_{i,t-1};  DIV = tổng cổ tức tiền mặt GỘP có
               ngày GDKHQ = t (`corporate_action`, DIV, executed).
  TR_t       = TR_{t-1} × (VNINDEX_t / VNINDEX_{t-1} + k × y_t);  k = 1 (`tr_gross`) hoặc
               1 − DIV_TAX_RATE (`tr_net`, sau thuế TNCN 5% trên cổ tức).
  Phần GIÁ lấy nguyên chỉ số chính thức ⇒ sai số rổ/trọng số chỉ đi vào số hạng cổ tức.

CHUỖI `data/benchmark/vnindex_tr_daily.csv` (một dòng/phiên): dòng mới `provisional`, thành `sealed`
khi đã có SEAL_AFTER phiên sau nó (dòng DIV có thể vào `corporate_action` muộn hơn ngày GDKHQ).
`--update` dựng lại mọi dòng `provisional` + VERIFY_SEALED dòng `sealed` cuối để kiểm: dòng `sealed`
dựng lại mà `y_gross` đổi > SEALED_Y_TOL (0,1 điểm cơ bản) hoặc `vnindex` đổi ⇒ rc=2, KHÔNG ghi gì.
`--update` không bao giờ viết lại phần `sealed`, và KHÔNG seal dòng mà cổng G1/G4 của chính nó đang nổ
chưa có ack (dòng đó và mọi dòng sau ở lại `provisional`, chờ BQ lấp hoặc người ack).
Đường DUY NHẤT sửa dòng `sealed` = `--restate-sealed DATE... --reason --confirmed-by`: dựng lại các dòng
đó từ BQ hiện tại, nối lại TR mọi dòng sau, ghi sổ CHỈ-THÊM `vnindex_tr_restatements.jsonl` (md5
trước/sau, dòng cũ/mới, lý do, người xác nhận) TRƯỚC khi thay file.

CỔNG FAIL-CLOSED cho một kỳ (`check_period`, G1–G8 của SPEC §A4). Consumer KHÔNG được rơi im lặng về
chỉ số giá: cổng hỏng ⇒ ô có cổ tức ghi `chưa có số (<lý do>)`, lý do trích đúng giá trị đã đọc (§29).

Dùng:
  python3 mike/bin/vnindex_total_return.py --update                 # cron, sau corporate_action ~22:48
  python3 mike/bin/vnindex_total_return.py --check --period 2026-07-06 2026-10-13
  python3 mike/bin/vnindex_total_return.py --period 2026-07-06 2026-10-13   # JSON, rc=1 khi cổng hỏng
  python3 mike/bin/vnindex_total_return.py --selfcheck              # = vnindex_total_return_selfcheck.py
  python3 mike/bin/vnindex_total_return.py --restate-sealed 2026-10-12 --reason "..." --confirmed-by "..." [--dry-run]
"""
import argparse
import csv
import datetime as dt
import fcntl
import io
import json
import math
import os
import re
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wc_paths import find_wc_root  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
WC_ROOT = find_wc_root(__file__)
BENCH_DIR = os.path.join(WC_ROOT, "data", "benchmark")
SERIES_PATH = os.path.join(BENCH_DIR, "vnindex_tr_daily.csv")
MEMBERSHIP_LATEST = os.path.join(BENCH_DIR, "hose_membership_latest.json")
ACKS_PATH = os.path.join(BENCH_DIR, "vnindex_tr_acks.json")
RESTATE_LOG = os.path.join(BENCH_DIR, "vnindex_tr_restatements.jsonl")   # sổ đính chính, chỉ-thêm

# Thuế TNCN trên cổ tức tiền mặt: 5% (TT 111/2013/TT-BTC Điều 10; Luật Thuế TNCN 109/2025 giữ nguyên).
DIV_TAX_RATE = 0.05
FIRST_DATE = "2013-12-31"          # dòng mốc của chuỗi (TR = chỉ số giá ngày này); y bắt đầu 2014-01-02
SEAL_AFTER = 5                     # số phiên sau đó một dòng mới thành `sealed`
VERIFY_SEALED = 5                  # số dòng `sealed` cuối được dựng lại để kiểm mỗi lần --update
SEALED_Y_TOL = 1e-5                # 0,1 điểm cơ bản (y là phân số)
SEALED_IDX_TOL = 1e-9              # chỉ số giá của dòng sealed coi như không được đổi
DY_CORRUPT = 0.5                   # cổ tức > 50% giá phiên trước: dữ liệu hỏng, loại khỏi y (nguyên mẫu)

# Ngưỡng cổng (SPEC §A4)
G2_TOL = 1e-4                      # BQ vs DNSE > 0,01%
# G4 số mã: SPEC đề xuất "> 5 mã" nhưng ĐO THẬT (chuỗi 2014→2026-10-13): từ 2026-06-25 BQ `ticker`
# không còn dòng cho mã HOSE không khớp lệnh trong phiên ⇒ phiên liền trước của mã ≠ phiên chỉ số ⇒ mã
# rơi khỏi rổ ngày hôm sau; số mã dao động 340–370, |Δ| > 5 ở 16/76 phiên 2026-06-25→10-13 (mọi kỳ báo
# cáo đều nổ). Mã rơi ra là mã thanh khoản thấp (vốn hoá nhỏ — điều kiện vốn hoá 3% không nổ phiên nào
# trong cùng cửa sổ). Ngưỡng dùng: |Δ| > 5% số mã phiên trước (đo: chỉ 2026-06-25, −24/395, nổ).
G4_MAX_N_CHANGE_FRAC = 0.05
G4_MC_TOL = 0.03
G4_ACK_PREFIX = "@G4_N"            # khoá ack nhánh số mã: (date, "@G4_N:<n_prev>><n>") — ràng GIÁ TRỊ đã xem
G4_MC_ACK_PREFIX = "@G4_MC"        # khoá ack nhánh vốn hoá: (date, "@G4_MC:<mc_prev>><mc>") — VND làm tròn nguyên


def g4_ack_key(date, n_prev: int, n: int) -> tuple:
    """Khoá ack G4-số-mã. Gắn cả (n_prev, n): dòng `provisional` bị dựng lại mỗi lần --update, nên ack
    chỉ có hiệu lực khi số mã quan sát được Y HỆT số người đã xem (đổi hướng/độ lớn ⇒ G4 nổ lại)."""
    return (date if isinstance(date, str) else date.isoformat(), f"{G4_ACK_PREFIX}:{n_prev}>{n}")


def g4_mc_ack_key(date, mc_prev, mc) -> tuple:
    """Khoá ack G4-vốn-hoá. Như g4_ack_key, ràng cả hai giá trị vốn hoá rổ (VND, làm tròn về số nguyên):
    dựng lại ra vốn hoá khác số người đã xem ⇒ ack không còn hiệu lực, G4 nổ lại."""
    return (date if isinstance(date, str) else date.isoformat(),
            f"{G4_MC_ACK_PREFIX}:{int(round(mc_prev))}>{int(round(mc))}")


G5_WINDOW = 60
G5_TOL = 0.005                     # 0,5 điểm %
G6_DY = 0.30
G7_MAX_AGE_DAYS = 35
G8_MAX_SHARE = 0.005
# G1 (vòng 2, B3): tập phiên = CHÍNH các dòng của chuỗi (mỗi dòng là phiên BQ VNINDEX, `--update` từ chối
# khi DNSE có phiên BQ thiếu) — KHÔNG dùng bảng lễ nhập tay `trading_bot.vn_market` (chưa có Tết; 2025
# thiếu 8 phiên ⇒ G1 báo oan, chặn mọi weekly/monthly từ Tết 2027). Hai lớp chống "dòng bị mất":
G1_MAX_GAP_DAYS = 14               # khoảng trống giữa 2 dòng liền nhau; đo 2014→2026-10-13: dài nhất 11 ngày (Tết 2015)
G1_CHAIN_TOL = 1e-9                # TR_t/TR_{t-1} phải = VNINDEX_t/VNINDEX_{t-1} + k·y_t (đo: lệch ≤ 9e-15)
SESSION_CLOSE_ICT = dt.time(15, 0)  # sau giờ này DNSE/BQ đã có nến của ngày (ATC HOSE xong 14:45)

COLUMNS = ["date", "vnindex", "vnindex_src2", "y_gross", "n_members", "mc_members_vnd",
           "div_cash_vnd", "tr_gross", "tr_net", "k2_synth_pr", "status", "membership_vintage",
           "ca_max_ingested_at", "built_at_ict",
           # ngoài danh sách cột của SPEC — cần cho G6/G8 lúc kiểm một kỳ (không đọc lại BQ):
           "max_dy", "max_dy_ticker", "osh_missing_max_pct", "osh_missing_ticker"]
KINDS = ("price", "tr_gross", "tr_net")
NO_NUMBER = "chưa có số"


class SealedChanged(Exception):
    """Dựng lại dòng `sealed` ra số khác ⇒ rc=2, file không đổi."""


class BuildRefused(Exception):
    """Đầu vào không đủ để dựng (thiếu phiên, thiếu bảng sàn...) ⇒ rc=3, file không đổi."""


class RestateRefused(Exception):
    """Đính chính không đủ điều kiện (thiếu lý do/người xác nhận, ngày không phải dòng sealed, dòng
    sau đính chính vẫn nổ G1/G4...) ⇒ rc=4, file + sổ không đổi."""


class PeriodError(ValueError):
    """Kỳ hỏi không hợp lệ (mốc không phải phiên trong chuỗi...)."""


def _d(s) -> dt.date:
    return s if isinstance(s, dt.date) else dt.date.fromisoformat(str(s)[:10])


def now_ict() -> dt.datetime:
    return dt.datetime.now(ICT)


# ─────────────────────────────────────────────────────────── bảng sàn

def load_membership(path: str = MEMBERSHIP_LATEST) -> dict:
    """spells[ticker] = [(start, end)] — khoảng [start, end) mã nằm trên HOSE (date)."""
    return {tk: [(_d(a), _d(b)) for a, b, *_ in sp]
            for tk, sp in _read_membership(path)["spells"].items()}


def _read_membership(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        m = json.load(f)
    if not m.get("vintage") or not isinstance(m.get("spells"), dict):
        raise BuildRefused(f"bảng sàn {path} thiếu 'vintage'/'spells' (khoá có: {sorted(m)})")
    return m


def membership_vintage(path: str = MEMBERSHIP_LATEST) -> str:
    return _read_membership(path)["vintage"]


# ─────────────────────────────────────────────────────────── cổ tức + y

def dividends(ca_df):
    """(ticker, time, div) — cổ tức tiền mặt GỘP theo (mã, ngày GDKHQ).
    Chỉ `event_code='DIV'`, `event_status='executed'`, `value_per_share > 0`; bỏ trùng HOÀN TOÀN trên
    (mã, ex-date, số tiền, năm, đợt); CỘNG các đợt khác nhau cùng ngày (DGC 14/09/2026: 3.000 + 5.000)."""
    import pandas as pd
    d = ca_df[(ca_df.event_code == "DIV") & ca_df.exright_date.notna()]
    d = d[(d.event_status == "executed") & (d.value_per_share > 0)].copy()
    d["exright_date"] = pd.to_datetime(d["exright_date"])
    d = d.drop_duplicates(["ticker", "exright_date", "value_per_share", "dividend_year",
                           "dividend_stage_vi"])
    g = d.groupby(["ticker", "exright_date"], as_index=False).value_per_share.sum()
    g.columns = ["ticker", "time", "div"]
    return g


def div_yield_daily(panel, spells: dict, divs, idx, after=None):
    """Bảng theo phiên của chỉ số (index = Timestamp), cột: y, n, mc, div_cash, k2_synth_pr, max_dy,
    max_dy_ticker, osh_missing_max_pct, osh_missing_ticker.

    `panel`: DataFrame[time, ticker, Price, Close, OShares] KHÔNG gồm VNINDEX; `idx`: Series giá
    VNINDEX theo time (định nghĩa tập phiên). `after`: chỉ trả các phiên > after."""
    import numpy as np
    import pandas as pd
    s = panel.copy()
    s["time"] = pd.to_datetime(s["time"])
    s = s.sort_values(["ticker", "time"]).reset_index(drop=True)
    g = s.groupby("ticker")
    s["P1"] = g.Price.shift(1)
    s["C1"] = g.Close.shift(1)
    s["S1"] = g.OShares.shift(1)
    s["t1"] = g.time.shift(1)
    s["S1_ff"] = g.OShares.transform(lambda x: x.ffill()).groupby(s.ticker).shift(1)
    if after is not None:
        s = s[s.time > pd.Timestamp(after)].copy()
    s["hose"] = False
    for code, rows in s.groupby("ticker").groups.items():
        sp = spells.get(code)
        if not sp:
            continue
        tt = s.loc[rows, "time"].values
        m = np.zeros(len(tt), bool)
        for a, b in sp:
            m |= (tt >= np.datetime64(a)) & (tt < np.datetime64(b))
        s.loc[rows, "hose"] = m
    dv = divs.copy()
    dv["time"] = pd.to_datetime(dv["time"])
    s = s.merge(dv, on=["ticker", "time"], how="left")
    s["div"] = s["div"].fillna(0.0)
    idx = idx.sort_index()
    idx.index = pd.to_datetime(idx.index)
    prev_idx = pd.Series(idx.index[:-1], index=idx.index[1:])
    s["t1_ok"] = s.t1.values == s.time.map(prev_idx).values
    base = s.hose & s.t1_ok & s.P1.gt(0) & s.Price.gt(0)
    u = s[base & s.S1.gt(0)].copy()
    u["mc1"] = u.P1 * u.S1
    u["divcash"] = u.S1 * u["div"]
    u["dy_i"] = u["div"] / u.P1
    u.loc[u.dy_i > DY_CORRUPT, "divcash"] = 0.0
    u["tr_i"] = u.Close / u.C1 - 1
    day = u.groupby("time").agg(mc=("mc1", "sum"), div_cash=("divcash", "sum"), n=("ticker", "size"))
    day["y"] = day.div_cash / day.mc
    day["tr_synth"] = (u.tr_i * u.mc1).groupby(u.time).sum() / day.mc
    day["k2_synth_pr"] = day.tr_synth - day.y
    top = u.sort_values("dy_i").groupby("time").tail(1).set_index("time")
    day["max_dy"] = top.dy_i.reindex(day.index).fillna(0.0)
    day["max_dy_ticker"] = top.ticker.reindex(day.index).where(day.max_dy > 0, "")
    # G8: thành viên có giá nhưng KHÔNG có OShares phiên t-1 — ước vốn hoá bằng OShares gần nhất
    miss = s[base & ~s.S1.gt(0) & s.S1_ff.gt(0)].copy()
    miss["mc_est"] = miss.P1 * miss.S1_ff
    if len(miss):
        mt = miss.sort_values("mc_est").groupby("time").tail(1).set_index("time")
        share = mt.mc_est / (day.mc.reindex(mt.index) + mt.mc_est)
        day["osh_missing_max_pct"] = share.reindex(day.index).fillna(0.0)
        day["osh_missing_ticker"] = mt.ticker.reindex(day.index).fillna("")
    else:
        day["osh_missing_max_pct"] = 0.0
        day["osh_missing_ticker"] = ""
    day = day[day.index.isin(idx.index)]
    return day.drop(columns=["tr_synth"])


def chain(prev_tr: float, idx_ratio: float, y: float, k: float) -> float:
    return prev_tr * (idx_ratio + k * y)


# ─────────────────────────────────────────────────────────── chuỗi trên đĩa

def _fmt(x, nd=15):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ""
    return format(float(x), f".{nd}g")


def _row_line(r: dict) -> str:
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow([r.get(c, "") for c in COLUMNS])
    return buf.getvalue()


def _parse_row(r: dict) -> dict:
    out = dict(r)
    for c in ("vnindex", "vnindex_src2", "y_gross", "mc_members_vnd", "div_cash_vnd", "tr_gross",
              "tr_net", "k2_synth_pr", "max_dy", "osh_missing_max_pct"):
        out[c] = float(r[c]) if r.get(c) not in (None, "") else None
    out["n_members"] = int(r["n_members"]) if r.get("n_members") not in (None, "") else None
    out["date"] = _d(r["date"])
    return out


def read_series(path: str = SERIES_PATH) -> list:
    """Danh sách dòng (đã parse), theo ngày tăng dần. Không có file ⇒ FileNotFoundError."""
    with open(path, encoding="utf-8", newline="") as f:
        return _parse_lines(f.read().splitlines(keepends=True), path)


def _parse_lines(lines: list, path: str) -> list:
    rd = csv.DictReader(lines)
    if rd.fieldnames != COLUMNS:
        raise ValueError(f"{path}: cột {rd.fieldnames} khác hợp đồng {COLUMNS}")
    rows = [_parse_row(r) for r in rd]
    for a, b in zip(rows, rows[1:]):
        if not a["date"] < b["date"]:
            raise ValueError(f"{path}: ngày không tăng dần ({a['date']} → {b['date']})")
    return rows


def build_rows(day, anchor: dict, src2: dict, vintage: str, ca_max_ingested_at: str,
               built_at: str) -> list:
    """Dòng chuỗi cho mọi phiên của `day` (sau anchor), chain từ `anchor` (dòng đã có hoặc mốc)."""
    rows, prev = [], anchor
    for ts, r in day.sort_index().iterrows():
        d = ts.date()
        ratio = r.vnindex / prev["vnindex"]
        rows.append({
            "date": d.isoformat(), "vnindex": _fmt(r.vnindex),
            "vnindex_src2": _fmt(src2.get(d)), "y_gross": _fmt(r.y),
            "n_members": str(int(r.n)), "mc_members_vnd": _fmt(r.mc, 15),
            "div_cash_vnd": _fmt(r.div_cash, 15),
            "tr_gross": _fmt(chain(prev["tr_gross"], ratio, r.y, 1.0), 15),
            "tr_net": _fmt(chain(prev["tr_net"], ratio, r.y, 1.0 - DIV_TAX_RATE), 15),
            "k2_synth_pr": _fmt(r.k2_synth_pr), "status": "provisional",
            "membership_vintage": vintage, "ca_max_ingested_at": ca_max_ingested_at,
            "built_at_ict": built_at, "max_dy": _fmt(r.max_dy, 8),
            "max_dy_ticker": r.max_dy_ticker or "", "osh_missing_max_pct": _fmt(r.osh_missing_max_pct, 8),
            "osh_missing_ticker": r.osh_missing_ticker or ""})
        prev = {"vnindex": float(rows[-1]["vnindex"]), "tr_gross": float(rows[-1]["tr_gross"]),
                "tr_net": float(rows[-1]["tr_net"])}
    return rows


def anchor_row(date: str, vnindex: float, src2, vintage, ca_ing, built_at) -> dict:
    """Dòng MỐC của chuỗi: TR = chỉ số giá ngày đó, y không áp dụng."""
    return {"date": date, "vnindex": _fmt(vnindex), "vnindex_src2": _fmt(src2), "y_gross": "",
            "n_members": "", "mc_members_vnd": "", "div_cash_vnd": "", "tr_gross": _fmt(vnindex, 15),
            "tr_net": _fmt(vnindex, 15), "k2_synth_pr": "", "status": "provisional",
            "membership_vintage": vintage, "ca_max_ingested_at": ca_ing, "built_at_ict": built_at,
            "max_dy": "", "max_dy_ticker": "", "osh_missing_max_pct": "", "osh_missing_ticker": ""}


def _raw_lines(path: str):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", newline="") as f:
        return f.read().splitlines(keepends=True)


def merge_rebuilt(path: str, rebuilt: list, acks: set = frozenset()) -> bytes:
    """Nội dung file mới: phần `sealed` cũ giữ NGUYÊN BYTE, dòng dựng lại thay phần còn lại.
    Dòng `sealed` có trong `rebuilt` được SO (không ghi đè): lệch ⇒ SealedChanged."""
    return _merge_lines(_raw_lines(path), rebuilt, acks, path)[0]


def _merge_lines(lines, rebuilt: list, acks: set, label: str = "chuỗi") -> tuple:
    """(bytes file mới, danh sách dòng bị cổng G1/G4 giữ lại provisional) — xem merge_rebuilt."""
    old = _parse_lines(lines, label) if lines else []
    head = "".join(lines[:1]) if lines else _row_line(dict(zip(COLUMNS, COLUMNS)))
    by_date = {r["date"]: r for r in rebuilt}
    keep, diffs = [], []
    for i, r in enumerate(old):
        if r["status"] != "sealed":
            break
        nr = by_date.pop(r["date"].isoformat(), None)
        if nr is not None:
            dy = abs((float(nr["y_gross"]) if nr["y_gross"] else 0.0) - (r["y_gross"] or 0.0))
            di = abs(float(nr["vnindex"]) / r["vnindex"] - 1)
            if dy > SEALED_Y_TOL or di > SEALED_IDX_TOL:
                diffs.append(f"{r['date']}: y_gross {r['y_gross']!r} → {nr['y_gross']!r} "
                             f"(|Δ|={dy:.3g} > {SEALED_Y_TOL:g}), vnindex {r['vnindex']!r} → "
                             f"{nr['vnindex']!r}")
        keep.append(lines[1 + i])
    if diffs:
        raise SealedChanged("dựng lại dòng sealed ra số khác — KHÔNG ghi; dùng đường đính chính "
                            "(bước 3): " + "; ".join(diffs))
    last_sealed = old[len(keep) - 1]["date"] if keep else None
    tail = [r for d, r in sorted(by_date.items()) if last_sealed is None or _d(d) > last_sealed]
    # Nối lại phần đuôi từ dòng sealed GIỮ BYTE: `rebuilt` được chain từ giá trị DỰNG LẠI của cửa sổ
    # kiểm, lệch dòng đã ghi trong phạm vi SEALED_Y_TOL ⇒ không nối lại thì G1 nổ ở ranh giới.
    prev = old[len(keep) - 1] if keep else None
    # đánh dấu sealed: dòng có >= SEAL_AFTER phiên sau nó trong file mới VÀ cổng G1/G4 của chính nó
    # không nổ (hoặc đã ack). Dòng đầu tiên bị chặn giữ nó + mọi dòng sau ở provisional (sealed = tiền tố).
    hist = old[max(len(keep) - 2, 0):len(keep)]          # 2 dòng trước (đã parse) cho G4 nhánh vốn hoá
    n, blocked = len(tail), []
    for j, r in enumerate(tail):
        if prev is not None:
            ratio = float(r["vnindex"]) / prev["vnindex"]
            y = float(r["y_gross"]) if r["y_gross"] else 0.0
            r["tr_gross"] = _fmt(chain(prev["tr_gross"], ratio, y, 1.0), 15)
            r["tr_net"] = _fmt(chain(prev["tr_net"], ratio, y, 1.0 - DIV_TAX_RATE), 15)
        prev = {"vnindex": float(r["vnindex"]), "tr_gross": float(r["tr_gross"]),
                "tr_net": float(r["tr_net"])}
        pr = _parse_row(r)
        seal = n - 1 - j >= SEAL_AFTER and not blocked
        if seal and hist:
            errs = seal_blockers(hist[-2] if len(hist) > 1 else None, hist[-1], pr, acks)
            if errs:
                blocked.append({"date": r["date"], "errors": errs})
                seal = False
        r["status"] = "sealed" if seal else "provisional"
        hist = (hist + [pr])[-2:]
    return (head + "".join(keep) + "".join(_row_line(r) for r in tail)).encode("utf-8"), blocked


def _write_atomic(path: str, data: bytes):
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _load_acks_or_refuse(acks_path: str) -> set:
    try:
        return load_acks(acks_path)
    except (OSError, ValueError) as exc:              # sổ ack hỏng ⇒ không seal theo giả định
        raise BuildRefused(f"không đọc được sổ ack {acks_path}: {type(exc).__name__} ({exc})") from None


def append_series(path: str, rebuilt: list, write: bool = True, acks_path: str = None) -> dict:
    """Ghi chuỗi: khoá `flock` + file tạm + `os.replace`; phần sealed cũ không đổi byte."""
    acks = _load_acks_or_refuse(ACKS_PATH if acks_path is None else acks_path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path + ".lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        lines = _raw_lines(path)
        old = "".join(lines or []).encode("utf-8")
        new, blocked = _merge_lines(lines, rebuilt, acks, path)
        n_sealed_old = sum(1 for r in (_parse_lines(lines, path) if lines else []) if r["status"] == "sealed")
        if write and new != old:
            _write_atomic(path, new)
    res = {"changed": new != old, "bytes": len(new), "sealed_before": n_sealed_old}
    if blocked:
        res["seal_blocked"] = blocked
    return res


# ─────────────────────────────────────────────────────────── kỳ + cổng

def _checked_through_stamp(stamp: str):
    """Ngày cuối mà một lần dựng ở thời điểm `stamp` (ISO có múi giờ) đã đối chiếu BQ ∪ DNSE: trước
    15:00 ICT ⇒ hôm trước (nến ngày chưa chốt). Không đọc được / thiếu múi giờ ⇒ None (fail-closed)."""
    try:
        t = dt.datetime.fromisoformat(stamp or "")
    except ValueError:
        return None
    if t.tzinfo is None:
        return None
    t = t.astimezone(ICT)
    return t.date() if t.time() >= SESSION_CLOSE_ICT else t.date() - dt.timedelta(days=1)


def checked_through(series: list):
    """Chuỗi đã được đối chiếu BQ ∪ DNSE tới ngày nào: `built_at_ict` của dòng CUỐI — dòng cuối luôn
    `provisional` nên MỖI lần `--update` thành công đều ghi lại nó (lần bị từ chối không ghi gì ⇒ mốc
    cũ, fail-closed). Ngày thường không có dòng trong (dòng cuối, mốc này] = không phải phiên."""
    return _checked_through_stamp(series[-1]["built_at_ict"]) if series else None


def _index_of(series: list, d: dt.date):
    for i, r in enumerate(series):
        if r["date"] == d:
            return i
    return None


def period_return(series: list, start_date, end_date, kind: str) -> float:
    """Tỉ suất kỳ (start, end]: `start` là NGÀY MỐC (giá chốt ngày đó), cùng quy ước `nav_unit_ledger`.
    Cả hai ngày PHẢI là phiên có trong chuỗi — mốc rơi vào ngày nghỉ ⇒ PeriodError (không tự lùi)."""
    if kind not in KINDS:
        raise PeriodError(f"kind {kind!r} không thuộc {KINDS}")
    a, b = _d(start_date), _d(end_date)
    ia, ib = _index_of(series, a), _index_of(series, b)
    if ia is None or ib is None:
        miss = [str(x) for x, i in ((a, ia), (b, ib)) if i is None]
        raise PeriodError(f"ngày {', '.join(miss)} không phải phiên có trong chuỗi "
                          f"({series[0]['date']} → {series[-1]['date']}) — không tự lùi mốc")
    if ib < ia:
        raise PeriodError(f"kỳ ngược: {a} > {b}")
    col = "vnindex" if kind == "price" else kind
    return series[ib][col] / series[ia][col] - 1


def _ack_section(a: dict, sect: str, path: str) -> list:
    """Mục ack phải là LIST các object. dict/chuỗi/… ⇒ ValueError rõ ràng (trước đây AttributeError khó đọc)."""
    v = a.get(sect, [])
    if not isinstance(v, list):
        raise ValueError(f"{path}: mục {sect} phải là list các object, không phải {type(v).__name__}")
    for e in v:
        if not isinstance(e, dict):
            raise ValueError(f"{path}: mục {sect} có phần tử không phải object ({type(e).__name__}): {e!r}")
    return v


def _ack_str(e: dict, k: str, path: str, sect: str):
    v = e.get(k)
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{path}: mục {sect} thiếu/rỗng {k} (cần chuỗi không rỗng): {e}")
    return v


def _ack_date(e: dict, path: str, sect: str) -> str:
    d = _ack_str(e, "date", path, sect)
    try:
        if dt.date.fromisoformat(d).isoformat() != d:
            raise ValueError
    except ValueError:
        raise ValueError(f"{path}: mục {sect} date phải dạng YYYY-MM-DD: {e}") from None
    return d


def load_acks(path: str = ACKS_PATH) -> set:
    """Tập khoá đã được NGƯỜI xác nhận: (date, ticker) cho G6; (date, '@G4_N:<n_prev>><n>') cho G4-số-mã;
    (date, '@G4_MC:<mc_prev>><mc>') cho G4-vốn-hoá.
    Thiếu file = không có xác nhận nào. Mục hỏng ⇒ ValueError (không lặng lẽ bỏ qua)."""
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        a = json.load(f)
    if not isinstance(a, dict):
        raise ValueError(f"{path}: gốc phải là object có các mục G6/G4/G4_MC, không phải {type(a).__name__}")
    out = set()
    for e in _ack_section(a, "G6", path):
        if not (e.get("confirmed_by") and e.get("date") and e.get("ticker")):
            raise ValueError(f"{path}: mục G6 thiếu confirmed_by/date/ticker: {e}")
        if not re.fullmatch(r"[A-Z0-9]{2,}", str(e["ticker"])):        # chặn giả khoá G4 qua mục G6
            raise ValueError(f"{path}: mục G6 ticker không hợp lệ: {e}")
        out.add((e["date"], e["ticker"]))
    # G4 (chỉ nhánh SỐ MÃ): ngày rổ đổi do BQ `ticker` thiếu dòng, đã có người xác nhận CHÍNH số mã đã xem.
    # Nhánh vốn hoá (mục G4_MC) cũng ràng GIÁ TRỊ: mc_prev, mc là vốn hoá rổ (VND) hai dòng liền nhau, lấy
    # đúng số trong thông báo lỗi G4. Tiền điều kiện ghi ack: mã thiếu không có GDKHQ cổ tức
    # tiền ở ngày D và D+1 (xem kb/data_registry/price-volume/vnindex_total_return.md).
    for e in _ack_section(a, "G4", path):
        d = _ack_date(e, path, "G4")
        _ack_str(e, "confirmed_by", path, "G4")
        _ack_str(e, "reason", path, "G4")
        for k in ("n_prev", "n"):
            if type(e.get(k)) is not int or e[k] <= 0:
                raise ValueError(f"{path}: mục G4 thiếu/sai {k} (số nguyên dương: số mã rổ đã xem): {e}")
        out.add(g4_ack_key(d, e["n_prev"], e["n"]))
    for e in _ack_section(a, "G4_MC", path):
        d = _ack_date(e, path, "G4_MC")
        _ack_str(e, "confirmed_by", path, "G4_MC")
        _ack_str(e, "reason", path, "G4_MC")
        for k in ("mc_prev", "mc"):
            v = e.get(k)
            if type(v) not in (int, float) or not math.isfinite(v) or v <= 0:
                raise ValueError(f"{path}: mục G4_MC thiếu/sai {k} (số dương: vốn hoá rổ VND đã xem): {e}")
        out.add(g4_mc_ack_key(d, e["mc_prev"], e["mc"]))
    return out


def _g1_link_errs(p: dict, r: dict) -> list:
    """G1 giữa hai dòng liền nhau (đã parse): khoảng trống quá dài, hoặc TR không nối được từ dòng trước."""
    errs = []
    if (r["date"] - p["date"]).days > G1_MAX_GAP_DAYS:
        errs.append(f"G1: {p['date']} → {r['date']} không có dòng nào ({(r['date'] - p['date']).days} "
                    f"ngày lịch > {G1_MAX_GAP_DAYS}) — chuỗi mất dòng?")
    y = r["y_gross"] or 0.0
    for col, k in (("tr_gross", 1.0), ("tr_net", 1.0 - DIV_TAX_RATE)):
        dev = r[col] / p[col] - (r["vnindex"] / p["vnindex"] + k * y)
        if abs(dev) > G1_CHAIN_TOL:
            errs.append(f"G1: {r['date']} {col} không nối từ dòng liền trước {p['date']} (lệch "
                        f"{dev:+.2e}) — có dòng bị xoá/sửa giữa hai dòng này")
            break
    return errs


def _g4_errs(pp, p: dict, r: dict, acks: set) -> list:
    """G4 của dòng r (đã parse): số mã đổi > G4_MAX_N_CHANGE_FRAC chưa ack; vốn hoá rổ lệch chỉ số
    > G4_MC_TOL chưa ack (khoá ràng cả hai giá trị vốn hoá). `pp` = dòng trước p (None ⇒ bỏ nhánh
    vốn hoá)."""
    errs = []
    if p["n_members"] is None or r["n_members"] is None:
        return errs
    dn = r["n_members"] - p["n_members"]
    if abs(dn) > G4_MAX_N_CHANGE_FRAC * p["n_members"] and \
            g4_ack_key(r["date"], p["n_members"], r["n_members"]) not in acks:
        errs.append(f"G4: {r['date']} số mã rổ {p['n_members']} → {r['n_members']} "
                    f"({dn:+d}, > {100 * G4_MAX_N_CHANGE_FRAC:g}% của {p['n_members']}) — "
                    f"chờ lấp dữ liệu BQ hoặc người xác nhận (n_prev={p['n_members']}, n={r['n_members']}) "
                    f"ở vnindex_tr_acks.json mục G4")
    if pp is not None and p["mc_members_vnd"]:
        exp = pp_ratio = p["vnindex"] / pp["vnindex"]
        dev = r["mc_members_vnd"] / p["mc_members_vnd"] / exp - 1
        if abs(dev) > G4_MC_TOL and \
                g4_mc_ack_key(r["date"], p["mc_members_vnd"], r["mc_members_vnd"]) not in acks:
            errs.append(f"G4: {r['date']} vốn hoá rổ đổi {100 * (r['mc_members_vnd'] / p['mc_members_vnd'] - 1):+.2f}% "
                        f"vs chỉ số {100 * (pp_ratio - 1):+.2f}% (lệch {100 * dev:+.2f}%, "
                        f"> {100 * G4_MC_TOL:g}%) — chờ lấp dữ liệu BQ hoặc người xác nhận "
                        f"(mc_prev={int(round(p['mc_members_vnd']))}, mc={int(round(r['mc_members_vnd']))}) "
                        f"ở vnindex_tr_acks.json mục G4_MC")
    return errs


def seal_blockers(pp, p: dict, r: dict, acks: set) -> list:
    """Lỗi cổng G1/G4 của CHÍNH dòng r — khác rỗng ⇒ r không được seal (C, vòng 2 ngày 21/10)."""
    return _g1_link_errs(p, r) + _g4_errs(pp, p, r, acks)


def check_period(series: list, start_date, end_date, acks: set = None, today: dt.date = None) -> list:
    """Danh sách lỗi cổng (rỗng = qua) cho kỳ (start, end]. Mỗi lỗi: 'Gx: <giá trị đã đọc>'."""
    a, b = _d(start_date), _d(end_date)
    acks = set() if acks is None else acks
    errs = []
    if not series:
        return ["G1: chuỗi rỗng"]
    last = series[-1]["date"]
    # G1 — phiên cuối của kỳ: chuỗi phải đã được đối chiếu BQ ∪ DNSE tới hết kỳ (tập phiên = dòng chuỗi)
    ct = checked_through(series)
    if b > last and (ct is None or b > ct):
        errs.append(f"G1: chuỗi dừng ở {last}; lần --update thành công cuối (built_at_ict "
                    f"{series[-1]['built_at_ict']!r}) mới đối chiếu BQ ∪ DNSE tới {ct} — chưa biết có "
                    f"phiên nào trong ({max(last, ct) if ct else last}, {b}] (kỳ tới {b})")
    ia = _index_of(series, a)
    if ia is None:
        errs.append(f"G1: mốc {a} không phải phiên có trong chuỗi")
        return errs
    ib = max(i for i, r in enumerate(series) if r["date"] <= b)
    rows = series[ia:ib + 1]
    # G1 — dòng bị mất giữa kỳ: khoảng trống quá dài, hoặc chuỗi TR không nối được từ dòng liền trước
    for p, r in zip(rows, rows[1:]):
        errs += _g1_link_errs(p, r)
    for i, r in enumerate(rows):
        # G2 — cả dòng mốc (mức chỉ số của nó đi vào tỉ suất)
        s2 = r["vnindex_src2"]
        if s2 is None:
            errs.append(f"G2: {r['date']} thiếu chỉ số nguồn 2 (DNSE); BQ {r['vnindex']}")
        elif abs(r["vnindex"] / s2 - 1) > G2_TOL:
            errs.append(f"G2: {r['date']} BQ {r['vnindex']} vs DNSE {s2} lệch "
                        f"{100 * (r['vnindex'] / s2 - 1):+.3f}% (> {100 * G2_TOL:g}%)")
        if i == 0:
            continue
        # G3 — feed corporate_action phải đã nạp sau phiên của dòng lúc dựng
        ing = (r["ca_max_ingested_at"] or "")[:10]
        if not ing or _d(ing) < r["date"]:
            errs.append(f"G3: {r['date']} dựng khi corporate_action nạp gần nhất {r['ca_max_ingested_at']!r} "
                        f"(trước phiên) — chưa chắc đủ dòng cổ tức")
        # G4 — rổ đổi đột ngột
        errs += _g4_errs(series[ia + i - 2] if ia + i - 2 >= 0 else None, series[ia + i - 1], r, acks)
        # G5 — chỉ số giá tổng hợp từ rổ, luỹ kế 60 phiên, so chỉ số chính thức
        j = ia + i
        if j - G5_WINDOW >= 0:
            w = series[j - G5_WINDOW + 1:j + 1]
            if all(x["k2_synth_pr"] is not None for x in w):
                synth = math.prod(1 + x["k2_synth_pr"] for x in w) - 1
                off = series[j]["vnindex"] / series[j - G5_WINDOW]["vnindex"] - 1
                if abs(synth - off) > G5_TOL:
                    errs.append(f"G5: {r['date']} 60 phiên rổ {100 * synth:+.2f}% vs VN-Index "
                                f"{100 * off:+.2f}% (lệch {100 * (synth - off):+.2f} điểm %, > "
                                f"{100 * G5_TOL:g})")
        # G6 — cổ tức bất thường chưa có người xác nhận
        if r["max_dy"] is not None and r["max_dy"] > G6_DY and \
                (r["date"].isoformat(), r["max_dy_ticker"]) not in acks:
            errs.append(f"G6: {r['date']} {r['max_dy_ticker']} cổ tức = {100 * r['max_dy']:.1f}% giá "
                        f"phiên trước (> {100 * G6_DY:g}%) — chờ người xác nhận ở vnindex_tr_acks.json")
        # G7 — bảng sàn cũ (so với ngày của dòng)
        v = r["membership_vintage"]
        if not v or (r["date"] - _d(v)).days > G7_MAX_AGE_DAYS:
            errs.append(f"G7: {r['date']} dựng với bảng sàn vintage {v!r} "
                        f"(> {G7_MAX_AGE_DAYS} ngày)")
        # G8 — OShares thiếu ở mã lớn
        if r["osh_missing_max_pct"] is not None and r["osh_missing_max_pct"] > G8_MAX_SHARE:
            errs.append(f"G8: {r['date']} {r['osh_missing_ticker']} thiếu OShares, ước "
                        f"{100 * r['osh_missing_max_pct']:.2f}% vốn hoá rổ (> {100 * G8_MAX_SHARE:g}%)")
    return errs


def _acked_g4_days(series: list, start_date, end_date, acks: set) -> list:
    """Các ngày trong kỳ mà G4 đã nổ nhưng được người ack: [{date, n_prev, n}] (nhánh số mã) hoặc
    [{date, mc_prev, mc}] (nhánh vốn hoá) — để chú thích báo cáo."""
    a, b = _d(start_date), _d(end_date)
    out = []
    for i, (p, r) in enumerate(zip(series, series[1:])):
        if not (a < r["date"] <= b) or p["n_members"] is None or r["n_members"] is None:
            continue
        if abs(r["n_members"] - p["n_members"]) > G4_MAX_N_CHANGE_FRAC * p["n_members"] and \
                g4_ack_key(r["date"], p["n_members"], r["n_members"]) in acks:
            out.append({"date": r["date"].isoformat(), "n_prev": p["n_members"], "n": r["n_members"]})
        if i >= 1 and p["mc_members_vnd"] and r["mc_members_vnd"] and \
                abs(r["mc_members_vnd"] / p["mc_members_vnd"] / (p["vnindex"] / series[i - 1]["vnindex"]) - 1) > G4_MC_TOL \
                and g4_mc_ack_key(r["date"], p["mc_members_vnd"], r["mc_members_vnd"]) in acks:
            out.append({"date": r["date"].isoformat(), "mc_prev": int(round(p["mc_members_vnd"])),
                        "mc": int(round(r["mc_members_vnd"]))})
    return out


def benchmark_period(start_date, end_date, series_path: str = SERIES_PATH, acks_path: str = ACKS_PATH,
                     series: list = None) -> dict:
    """Khối benchmark cho consumer (nav_period_returns). Không bao giờ ném lỗi: thiếu số ⇒
    `status='unavailable'` + `reason` (giá trị đã đọc), các ô % = None — KHÔNG thay bằng chỉ số giá.
    Ô chỉ số GIÁ vẫn có số khi chỉ cổng phần cổ tức hỏng (G3–G8); G1/G2 làm hỏng cả ô giá."""
    out = {"vnindex_price_pct": None, "vnindex_tr_gross_pct": None, "vnindex_tr_net_pct": None,
           "status": "unavailable", "reason": None}
    try:
        if series is None:
            series = read_series(series_path)
        acks = load_acks(acks_path)            # đọc MỘT lần: cổng và danh sách ngày ack cùng một tập
        errs = check_period(series, start_date, end_date, acks)
    except Exception as exc:                                        # noqa: BLE001
        out["reason"] = f"{type(exc).__name__} ({exc})"
        return out
    price_errs = [e for e in errs if e.startswith(("G1", "G2"))]
    try:
        if not price_errs:
            out["vnindex_price_pct"] = round(100 * period_return(series, start_date, end_date, "price"), 3)
        if not errs:
            for k in ("tr_gross", "tr_net"):
                out[f"vnindex_{k}_pct"] = round(100 * period_return(series, start_date, end_date, k), 3)
    except PeriodError as exc:
        errs = errs + [f"G1: {exc}"]
    if errs:
        out["reason"] = "; ".join(errs[:6]) + (f" (+{len(errs) - 6} lỗi nữa)" if len(errs) > 6 else "")
        out["n_gate_errors"] = len(errs)
    else:
        out["status"] = "ok"
        prov = [r for r in series if _d(start_date) < r["date"] <= _d(end_date)
                and r["status"] == "provisional"]
        if prov:
            out["provisional_sessions"] = len(prov)
        acked = _acked_g4_days(series, start_date, end_date, acks)
        if acked:                    # dữ liệu cho consumer; CHƯA có consumer nào in ra báo cáo (18/10)
            out["acked_g4_days"] = acked
    return out


# ─────────────────────────────────────────────────────────── cho báo cáo (nav_period_returns)

CONFIG_PATH = os.path.join(BENCH_DIR, "benchmark_config.json")
# Q2 (user 2026-10-14): cột "VN-Index có cổ tức" hiển thị số SAU thuế 5% (số thực nhận) — `tr_net`.
# Đổi sang `tr_gross` bằng file cấu hình, không sửa code: {"report_tr_kind": "tr_gross"}.
DEFAULT_REPORT_TR_KIND = "tr_net"
TR_FOOTNOTE = {
    "tr_net": ("VN-Index có cổ tức: đội tự tính từ cổ tức tiền mặt của cổ phiếu HOSE, tái đầu tư tại "
               "ngày GDKHQ, sau thuế TNCN 5% trên cổ tức; HOSE không công bố bản có cổ tức của VN-Index."),
    "tr_gross": ("VN-Index có cổ tức: đội tự tính từ cổ tức tiền mặt của cổ phiếu HOSE, tái đầu tư tại "
                 "ngày GDKHQ, trước thuế; HOSE không công bố bản có cổ tức của VN-Index."),
}


def report_tr_kind(path: str = CONFIG_PATH) -> str:
    """Loại chỉ số có cổ tức hiển thị trong báo cáo. Thiếu file ⇒ mặc định user chốt (`tr_net`);
    giá trị lạ ⇒ ValueError (không đoán)."""
    if not os.path.exists(path):
        return DEFAULT_REPORT_TR_KIND
    with open(path, encoding="utf-8") as f:
        k = json.load(f).get("report_tr_kind", DEFAULT_REPORT_TR_KIND)
    if k not in TR_FOOTNOTE:
        raise ValueError(f"{path}: report_tr_kind={k!r} không thuộc {sorted(TR_FOOTNOTE)}")
    return k


def index_session_for(series: list, d) -> tuple:
    """(phiên của chỉ số ứng với dòng sổ ngày d, ghi chú). d là phiên có trong chuỗi ⇒ chính nó. d KHÔNG
    phải phiên (không có dòng, nằm trong vùng chuỗi đã đối chiếu BQ ∪ DNSE) ⇒ phiên gần nhất trước đó —
    NAV của dòng sổ ngày nghỉ được định giá bằng giá đóng cửa phiên đó, nên đây là mức chỉ số CÙNG thời
    điểm, không phải tự lùi mốc. d sau vùng đã đối chiếu / trước đầu chuỗi ⇒ (None, lý do G1)."""
    d = _d(d)
    dates = [r["date"] for r in series]
    if d in dates:
        return d, None
    if not dates or d < dates[0]:
        return None, f"G1: {d} trước đầu chuỗi ({dates[0] if dates else 'chuỗi rỗng'})"
    if d > dates[-1]:
        ct = checked_through(series)
        if ct is None or d > ct:
            return None, (f"G1: {d} sau phiên cuối của chuỗi {dates[-1]}; lần --update thành công cuối "
                          f"(built_at_ict {series[-1]['built_at_ict']!r}) mới đối chiếu BQ ∪ DNSE tới {ct} "
                          f"— chưa biết {d} có phải phiên không")
    prev = max(x for x in dates if x < d)
    return prev, f"{d} không giao dịch ⇒ mức chỉ số đóng cửa {prev} (giá dùng cho NAV dòng đó)"


def report_benchmark(anchor_date, end_date, series_path: str = SERIES_PATH, acks_path: str = ACKS_PATH,
                     config_path: str = CONFIG_PATH, series: list = None) -> dict:
    """Khối `benchmark` của một kỳ báo cáo. `anchor_date` = ngày của DÒNG SỔ ĐƠN VỊ làm mốc kỳ (không do
    người soạn chọn). Không bao giờ ném lỗi; thiếu số ⇒ ô None + `reason`."""
    out = {"anchor_date": str(anchor_date)[:10], "end_date": str(end_date)[:10],
           "index_anchor_date": None, "index_end_date": None}
    try:
        kind = report_tr_kind(config_path)
        if series is None:
            series = read_series(series_path)
    except Exception as exc:                                        # noqa: BLE001
        out.update({"vnindex_price_pct": None, "vnindex_tr_gross_pct": None, "vnindex_tr_net_pct": None,
                    "tr_kind": None, "vnindex_tr_pct": None, "status": "unavailable",
                    "reason": f"{type(exc).__name__} ({exc})"})
        return out
    a, na = index_session_for(series, anchor_date)
    b, nb = index_session_for(series, end_date)
    notes = [n for n in (na, nb) if n and not n.startswith("G1")]
    if a is None or b is None:
        res = {"vnindex_price_pct": None, "vnindex_tr_gross_pct": None, "vnindex_tr_net_pct": None,
               "status": "unavailable", "reason": "; ".join(n for n in (na, nb) if n and n.startswith("G1"))}
    else:
        res = benchmark_period(a, b, series=series, acks_path=acks_path)
        out.update({"index_anchor_date": a.isoformat(), "index_end_date": b.isoformat()})
    out.update(res)
    out["tr_kind"] = kind
    out["vnindex_tr_pct"] = res.get(f"vnindex_{kind}_pct")
    out["footnote"] = TR_FOOTNOTE[kind]
    if notes:
        out["notes"] = notes
    return out


# ─────────────────────────────────────────────────────────── nguồn dữ liệu (--update)

def fetch_dnse_vnindex(start: dt.date, end: dt.date, timeout: int = 30) -> dict:
    """{date: close} VNINDEX từ DNSE chart-api (nguồn 2). Ngày = ngày ICT của nhãn thời gian."""
    import urllib.request
    t0 = int(dt.datetime.combine(start, dt.time(0), ICT).timestamp())
    t1 = int(dt.datetime.combine(end + dt.timedelta(days=1), dt.time(0), ICT).timestamp())
    url = ("https://services.entrade.com.vn/chart-api/v2/ohlcs/index?symbol=VNINDEX&resolution=1D"
           f"&from={t0}&to={t1}")
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        j = json.loads(resp.read().decode("utf-8"))
    return {dt.datetime.fromtimestamp(t, ICT).date(): float(c) for t, c in zip(j["t"], j["c"])}


def fetch_bq(since: dt.date) -> dict:
    """panel (time, ticker, Price, Close, OShares) từ `since`, VNINDEX, DIV rows, MAX(ingested_at)."""
    import pandas as pd
    if WC_ROOT not in sys.path:
        sys.path.insert(0, WC_ROOT)
    from corp_action_lib import TABLE, bq
    proj = TABLE.split(".")[0]
    p = pd.DataFrame(bq(f"SELECT CAST(t.time AS STRING) time, t.ticker, t.Price, t.Close, t.OShares "
                        f"FROM `{proj}.tav2_bq.ticker` AS t WHERE t.time >= '{since.isoformat()}'"))
    ca = pd.DataFrame(bq(f"SELECT c.ticker, c.event_code, CAST(c.exright_date AS STRING) exright_date, "
                         f"c.value_per_share, c.dividend_year, c.dividend_stage_vi, c.event_status "
                         f"FROM `{TABLE}` AS c WHERE c.event_code = 'DIV' "
                         f"AND c.exright_date >= '{since.isoformat()}'"))
    ing = bq(f"SELECT CAST(MAX(c.ingested_at) AS STRING) m FROM `{TABLE}` AS c")[0]["m"]
    return {"panel": p, "ca": ca, "ca_max_ingested_utc": ing}


def _coerce_inputs(panel, ca):
    import pandas as pd
    panel = panel.copy()
    for c in ("Price", "Close", "OShares"):
        panel[c] = pd.to_numeric(panel[c], errors="coerce")
    panel["time"] = pd.to_datetime(panel["time"])
    ca = ca.copy()
    if len(ca):
        ca["value_per_share"] = pd.to_numeric(ca["value_per_share"], errors="coerce")
        ca["exright_date"] = pd.to_datetime(ca["exright_date"])
    else:
        ca = pd.DataFrame(columns=["ticker", "event_code", "exright_date", "value_per_share",
                                   "dividend_year", "dividend_stage_vi", "event_status"])
    return panel, ca


def _utc_to_ict(s: str) -> str:
    if not s:
        return ""
    t = dt.datetime.fromisoformat(s.replace(" UTC", "").replace("Z", "")[:26])
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t.astimezone(ICT).isoformat(timespec="seconds")


def update(series_path: str = SERIES_PATH, membership_path: str = MEMBERSHIP_LATEST, inputs=None,
           src2=None, write: bool = True, rebuild_from: str = None, built_at: str = None,
           first_date: str = FIRST_DATE, acks_path: str = None) -> dict:
    """Dựng các phiên còn thiếu + dựng lại phiên `provisional` + VERIFY_SEALED dòng sealed cuối.
    `inputs`/`src2` tiêm được (selfcheck, dựng lại offline); mặc định đọc BQ + DNSE."""
    old = read_series(series_path) if os.path.exists(series_path) else []
    sealed_idx = [i for i, r in enumerate(old) if r["status"] == "sealed"]
    # Mốc chain = một dòng SEALED (giữ nguyên byte); chưa có dòng sealed nào ⇒ dựng lại từ đầu chuỗi.
    if rebuild_from:
        k = max((i for i in sealed_idx if old[i]["date"] < _d(rebuild_from)), default=None)
    elif sealed_idx:
        k = sealed_idx[max(len(sealed_idx) - 1 - VERIFY_SEALED, 0)]
    else:
        k = None
    since, rebuilt, ca_ing = _rebuild(old, k, membership_path, inputs, src2, built_at, first_date)
    res = append_series(series_path, rebuilt, write=write, acks_path=acks_path)
    res.update({"anchor": since.isoformat(), "rebuilt": len(rebuilt),
                "last": rebuilt[-1]["date"] if rebuilt else None, "ca_max_ingested_ict": ca_ing})
    return res


def _rebuild(old: list, k, membership_path: str, inputs, src2, built_at, first_date) -> tuple:
    """(ngày mốc, dòng dựng lại mọi phiên sau mốc old[k] — chain từ dòng mốc —, ca_max_ingested ICT).
    k=None ⇒ dựng từ đầu chuỗi. Không ghi gì."""
    import pandas as pd
    built_at = built_at or now_ict().isoformat(timespec="seconds")
    mem = _read_membership(membership_path)
    spells = load_membership(membership_path)
    anchor = old[k] if k is not None else None
    since = anchor["date"] if anchor else (old[0]["date"] if old else _d(first_date))
    if inputs is None:
        inputs = fetch_bq(since)
    panel, ca = _coerce_inputs(inputs["panel"], inputs["ca"])
    ca_ing = _utc_to_ict(inputs.get("ca_max_ingested_utc") or "")
    idx = panel[panel.ticker == "VNINDEX"].set_index("time").Price.sort_index()
    idx = idx[idx.index >= pd.Timestamp(since)]
    if idx.empty or idx.index[0].date() != since:
        raise BuildRefused(f"BQ không có dòng VNINDEX ngày mốc {since} (dòng đầu: "
                           f"{idx.index[0].date() if len(idx) else None})")
    sess = [t.date() for t in idx.index]
    # `built_at` của dòng cuối = mốc "đã đối chiếu BQ ∪ DNSE tới" mà G1 tin (checked_through) ⇒ DNSE phải
    # được hỏi tới đúng mốc đó; DNSE có phiên BQ chưa có (BQ chưa sync) ⇒ từ chối, không ghi.
    ct = _checked_through_stamp(built_at)
    if ct is None:
        raise BuildRefused(f"built_at {built_at!r} không phải thời điểm ISO có múi giờ")
    if src2 is None:
        src2 = fetch_dnse_vnindex(since, max(sess[-1], ct))
    elif src2:
        # dựng offline (src2 tiêm vào): chỉ vouch được tới phiên cuối của dữ liệu DNSE đưa vào
        cap = dt.datetime.combine(max(src2), dt.time(23, 59, 59), ICT)
        if dt.datetime.fromisoformat(built_at) > cap:
            built_at = cap.isoformat(timespec="seconds")
            ct = _checked_through_stamp(built_at)
    missing = sorted(d for d in src2 if since < d <= max(sess[-1], ct) and d not in set(sess))
    if missing:
        raise BuildRefused(f"DNSE có {len(missing)} phiên mà BQ VNINDEX không có: "
                           f"{[d.isoformat() for d in missing[:5]]} (BQ tới {sess[-1]}, đối chiếu tới {ct}) "
                           f"— không dựng chuỗi có lỗ")
    day = div_yield_daily(panel[panel.ticker != "VNINDEX"], spells, dividends(ca), idx, after=since)
    day = day.join(idx.rename("vnindex"))
    # phiên chỉ số không có thành viên nào ⇒ không suy được y: từ chối thay vì bỏ qua im lặng
    lost = [t.date() for t in idx.index[1:] if t not in day.index]
    if lost:
        raise BuildRefused(f"{len(lost)} phiên VNINDEX không có mã nào trong rổ: {lost[:5]}")
    if anchor is None:
        a = anchor_row(since.isoformat(), float(idx.iloc[0]), src2.get(since), mem["vintage"],
                       ca_ing, built_at)
        prev = {"vnindex": float(a["vnindex"]), "tr_gross": float(a["tr_gross"]),
                "tr_net": float(a["tr_net"])}
        rebuilt = [a] + build_rows(day, prev, src2, mem["vintage"], ca_ing, built_at)
    else:
        rebuilt = build_rows(day, anchor, src2, mem["vintage"], ca_ing, built_at)
        if abs(float(idx.iloc[0]) / anchor["vnindex"] - 1) > SEALED_IDX_TOL:
            raise SealedChanged(f"chỉ số dòng mốc {since} đổi: {anchor['vnindex']} → {float(idx.iloc[0])}")
    lost_old = sorted({r["date"] for r in old if r["date"] > since} - {_d(r["date"]) for r in rebuilt})
    if lost_old:
        raise BuildRefused(f"lần dựng này không phủ {len(lost_old)} phiên đã có trong chuỗi: "
                           f"{[d.isoformat() for d in lost_old[:5]]} (BQ mất dòng?) — không ghi")
    return since, rebuilt, ca_ing


def _without_built_at(line: str) -> list:
    v = next(csv.reader([line]))
    v[COLUMNS.index("built_at_ict")] = ""
    return v


def _md5(b: bytes) -> str:
    import hashlib
    return hashlib.md5(b).hexdigest()


def _last_log_entry(log_path: str):
    """Dòng sổ đính chính cuối (dict) hoặc None (không có/không đọc được — chỉ mất chú thích retry_of)."""
    try:
        with open(log_path, encoding="utf-8") as f:
            last = [x for x in f.read().splitlines() if x.strip()][-1:]
        return json.loads(last[0]) if last else None
    except (OSError, ValueError):
        return None


UNDO_KEYS = ("md5_before", "md5_after", "rows_before", "rechained_sealed_before", "last_sealed_before",
             "tail_before")


def undo_restatement(entry: dict, new_bytes: bytes) -> bytes:
    """Nội dung file TRƯỚC một đính chính, dựng từ chính dòng sổ + file ngay sau đính chính (md5_after) —
    hoàn tác byte-exact không cần bản sao lưu ngoài. Chỉ đúng khi file chưa bị `--update` ghi tiếp.
    Dòng sổ cũ thiếu byte cũ (vd dòng 12:34 21/10: không có rechained_sealed_before/tail_before) ⇒ ValueError."""
    if entry.get("kind") == "undo":
        raise ValueError("dòng sổ này là một undo, không phải đính chính — không hoàn tác được")
    miss = [k for k in UNDO_KEYS if k not in entry]
    if miss:
        raise ValueError(f"dòng sổ {entry.get('ts_ict')} thiếu {miss} (ghi trước khi sổ giữ byte cũ) — "
                         f"không undo được bằng hàm; khôi phục từ bản sao lưu")
    if _md5(new_bytes) != entry["md5_after"]:
        raise ValueError(f"file hiện tại md5 {_md5(new_bytes)} ≠ md5_after {entry['md5_after']} của dòng sổ")
    lines = new_bytes.decode("utf-8").splitlines(keepends=True)
    rows = _parse_lines(lines, "undo")
    first = min(entry["rows_before"])
    k = [r["date"].isoformat() for r in rows].index(first)
    old_by_date = {**entry["rechained_sealed_before"], **entry["rows_before"]}
    end = [r["date"].isoformat() for r in rows].index(entry["last_sealed_before"])
    mid = [old_by_date.get(rows[i]["date"].isoformat(), lines[1 + i]) for i in range(k, end + 1)]
    out = "".join(lines[:1 + k] + mid + entry["tail_before"]).encode("utf-8")
    if _md5(out) != entry["md5_before"]:
        raise ValueError(f"dựng lại md5 {_md5(out)} ≠ md5_before {entry['md5_before']}")
    return out


def _append_log(log_path: str, entry: dict):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _need_reason_who(reason, confirmed_by, flag: str):
    if not isinstance(reason, str) or not reason.strip():
        raise RestateRefused(f"thiếu --reason (lý do {flag}, trích số thật) — không làm")
    if not isinstance(confirmed_by, str) or not confirmed_by.strip():
        raise RestateRefused("thiếu --confirmed-by (người xác nhận + thời điểm) — không làm")


def undo_last_restatement(reason: str, confirmed_by: str, series_path: str = SERIES_PATH,
                          write: bool = True, log_path: str = None) -> dict:
    """Hoàn tác đính chính CUỐI trong sổ. Fail-closed (RestateRefused, không ghi gì) khi: thiếu lý do/người
    xác nhận; sổ trống/không đọc được; dòng sổ cuối thuộc chuỗi khác hoặc đã là undo; md5 file hiện tại ≠
    md5_after của dòng cuối (đã có --update/đính chính khác chạm vào); dòng sổ thiếu byte cũ. Ghi dòng
    {"kind":"undo"} vào sổ TRƯỚC, rồi mới thay file (flock + tmp + os.replace)."""
    _need_reason_who(reason, confirmed_by, "hoàn tác")
    log_path = RESTATE_LOG if log_path is None else log_path
    abs_series = os.path.abspath(series_path)
    with open(series_path + ".lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            with open(log_path, encoding="utf-8") as f:
                rows = [x for x in f.read().splitlines() if x.strip()]
            last = json.loads(rows[-1])
        except (OSError, IndexError, ValueError) as exc:
            raise RestateRefused(f"không đọc được dòng sổ cuối {log_path}: {type(exc).__name__} ({exc})") from None
        if last.get("series") != abs_series:
            raise RestateRefused(f"dòng sổ cuối thuộc chuỗi {last.get('series')}, không phải {abs_series}")
        if last.get("kind") == "undo":
            raise RestateRefused(f"dòng sổ cuối ({last.get('ts_ict')}) đã là một undo — không hoàn tác chồng")
        with open(series_path, "rb") as f:
            cur = f.read()
        if _md5(cur) != last.get("md5_after"):
            raise RestateRefused(f"file hiện tại md5 {_md5(cur)} ≠ md5_after {last.get('md5_after')} của dòng "
                                 f"sổ cuối — chuỗi đã đổi sau đính chính (--update?), không undo được")
        try:
            out = undo_restatement(last, cur)
        except ValueError as exc:
            raise RestateRefused(str(exc)) from None
        entry = {"kind": "undo", "ts_ict": now_ict().isoformat(timespec="seconds"), "series": abs_series,
                 "md5_before": _md5(cur), "md5_after": _md5(out), "undoes": last["md5_after"],
                 "undoes_ts_ict": last.get("ts_ict"), "confirmed_by": confirmed_by.strip(),
                 "reason": reason.strip()}
        if write:
            _append_log(log_path, entry)
            _write_atomic(series_path, out)
    return {"written": bool(write), **{k: entry[k] for k in ("kind", "md5_before", "md5_after", "undoes")}}


def restate_sealed(dates, reason: str, confirmed_by: str, series_path: str = SERIES_PATH,
                   membership_path: str = MEMBERSHIP_LATEST, inputs=None, src2=None, write: bool = True,
                   built_at: str = None, acks_path: str = None, log_path: str = None) -> dict:
    """ĐƯỜNG DUY NHẤT sửa dòng `sealed`. Dựng lại các dòng `dates` từ dữ liệu hiện tại (BQ + DNSE, hoặc
    tiêm), nối lại TR mọi dòng sau (sealed lẫn provisional), ghi sổ chỉ-thêm `log_path` RỒI mới thay file
    (atomic, dưới flock). Từ chối (RestateRefused, không ghi gì) khi: thiếu lý do/người xác nhận; ngày
    không phải dòng sealed / là dòng mốc; dòng sealed KHÁC trong vùng dựng lại lệch > ngưỡng (phải nêu tên
    nó); dòng đính chính vẫn nổ G1/G4 chưa ack; không có gì thay đổi."""
    _need_reason_who(reason, confirmed_by, "đính chính")
    want = sorted({_d(x) for x in dates})
    if not want:
        raise RestateRefused("không có ngày nào để đính chính")
    acks_path = ACKS_PATH if acks_path is None else acks_path
    log_path = RESTATE_LOG if log_path is None else log_path
    try:
        acks = load_acks(acks_path)
    except (OSError, ValueError) as exc:
        raise RestateRefused(f"không đọc được sổ ack {acks_path}: {type(exc).__name__} ({exc})") from None
    with open(series_path + ".lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        lines = _raw_lines(series_path)
        if not lines:
            raise RestateRefused(f"{series_path} không có/rỗng")
        old = _parse_lines(lines, series_path)
        pos = {r["date"]: i for i, r in enumerate(old)}
        bad = [f"{d} ({'không có dòng' if d not in pos else old[pos[d]]['status']})" for d in want
               if d not in pos or old[pos[d]]["status"] != "sealed"]
        if bad:
            raise RestateRefused(f"chỉ đính chính được dòng sealed: {bad}")
        k = pos[want[0]]
        if k == 0:
            raise RestateRefused(f"{want[0]} là dòng mốc của chuỗi — không đính chính")
        since, rebuilt, ca_ing = _rebuild(old, k - 1, membership_path, inputs, src2, built_at, None)
        by_date = {r["date"]: dict(r) for r in rebuilt}
        last_sealed = max(i for i, r in enumerate(old) if r["status"] == "sealed")
        # vùng sealed [k, last_sealed]: dòng được nêu ⇒ thay bằng dòng dựng lại; dòng khác ⇒ giữ trường,
        # chỉ nối lại tr (hệ quả toán học). Mọi dòng được nối lại từ dòng mốc old[k-1] giữ byte.
        prev, new_sealed, rechained, rows_before, rows_after = old[k - 1], [], [], {}, {}
        rechained_before = {}
        for i in range(k, last_sealed + 1):
            d = old[i]["date"].isoformat()
            raw = dict(zip(COLUMNS, next(csv.reader([lines[1 + i]]))))
            if old[i]["date"] in want:
                r = by_date.get(d)
                if r is None:
                    raise RestateRefused(f"dữ liệu hiện tại không có phiên {d} — không dựng lại được")
                r["status"] = "sealed"
            else:
                r = raw
            y = float(r["y_gross"]) if r["y_gross"] else 0.0
            ratio = float(r["vnindex"]) / float(prev["vnindex"])
            r["tr_gross"] = _fmt(chain(float(prev["tr_gross"]), ratio, y, 1.0), 15)
            r["tr_net"] = _fmt(chain(float(prev["tr_net"]), ratio, y, 1.0 - DIV_TAX_RATE), 15)
            line = _row_line(r)
            if old[i]["date"] in want:
                rows_before[d], rows_after[d] = lines[1 + i], line
            elif line != lines[1 + i]:
                rechained.append(d)
                rechained_before[d] = lines[1 + i]
            new_sealed.append(line)
            prev = r
        staged = lines[:1 + k] + new_sealed + lines[2 + last_sealed:]
        try:
            # so dòng sealed khác trong vùng dựng lại (lệch ⇒ SealedChanged), nối lại + seal-guard đuôi
            new, blocked = _merge_lines(staged, rebuilt, acks, series_path)
        except SealedChanged as exc:
            raise RestateRefused(f"dòng sealed KHÔNG được nêu cũng lệch — nêu tên chúng nếu muốn đính "
                                 f"chính: {exc}") from None
        nrows = _parse_lines(new.decode("utf-8").splitlines(keepends=True), series_path)
        npos = {r["date"]: i for i, r in enumerate(nrows)}
        # bất biến C: mọi dòng sealed từ ngày đính chính đầu tiên trở đi phải sạch G1/G4 (hoặc đã ack)
        still = {}
        for i in range(npos[want[0]], len(nrows)):
            if nrows[i]["status"] != "sealed":
                break
            e = seal_blockers(nrows[i - 2] if i >= 2 else None, nrows[i - 1], nrows[i], acks)
            if e:
                still[nrows[i]["date"].isoformat()] = e
        if still:
            raise RestateRefused(f"sau đính chính dòng vẫn nổ cổng (ack trước, hoặc chờ BQ lấp): {still}")
        old_b = "".join(lines).encode("utf-8")
        # "không đổi" xét trên CÁC DÒNG ĐƯỢC NÊU, bỏ qua built_at_ict (mỗi lần dựng một dấu thời gian mới;
        # đuôi provisional luôn được dựng lại). Dòng chỉ bị nối lại (nhiễu float trong G1_CHAIN_TOL) KHÔNG
        # tính là đổi — nếu không, chạy lại cùng lệnh hoặc đính chính "không có gì" vẫn ghi sổ một đính chính rỗng
        if all(_without_built_at(rows_after[d]) == _without_built_at(rows_before[d]) for d in rows_after):
            raise RestateRefused("dựng lại ra đúng số cũ ở các dòng được nêu — không có gì để đính chính, không ghi sổ")
        entry = {"ts_ict": now_ict().isoformat(timespec="seconds"), "series": os.path.abspath(series_path),
                 "dates": [d.isoformat() for d in want], "reason": reason.strip(),
                 "confirmed_by": confirmed_by.strip(), "md5_before": _md5(old_b), "md5_after": _md5(new),
                 "anchor": since.isoformat(), "rows_before": rows_before, "rows_after": rows_after,
                 "rechained_sealed": rechained, "rechained_sealed_before": rechained_before,
                 "last_sealed_before": old[last_sealed]["date"].isoformat(),
                 "tail_before": lines[2 + last_sealed:], "ca_max_ingested_ict": ca_ing,
                 "membership_vintage": membership_vintage(membership_path)}
        if blocked:
            entry["seal_blocked"] = blocked
        prior = _last_log_entry(log_path)
        if prior and prior.get("kind") != "undo" and prior.get("series") == entry["series"] \
                and prior.get("md5_before") == entry["md5_before"] \
                and prior.get("md5_after") != entry["md5_before"] \
                and all(prior.get(k_) == entry[k_] for k_ in ("dates", "reason", "confirmed_by")):
            # lần trước ghi sổ rồi chết trước khi thay file (file vẫn md5_before của nó) VÀ cùng ngày + lý do +
            # người xác nhận ⇒ đây là CHẠY LẠI. Chỉ khớp md5 chưa đủ: sau khi khôi phục file, một đính chính
            # độc lập (ngày/lý do khác) cũng có md5_before trùng — không được gắn nhầm retry_of
            entry["retry_of"] = {"ts_ict": prior.get("ts_ict"), "md5_after": prior.get("md5_after")}
        if write:
            # sổ TRƯỚC, file SAU: chết giữa chừng ⇒ có dòng sổ mà md5_after không khớp file (phát hiện
            # được); ngược lại sẽ là file đã sửa mà không có sổ = đường im lặng.
            _append_log(log_path, entry)
            _write_atomic(series_path, new)
    return {"written": bool(write), **{k_: entry[k_] for k_ in ("dates", "md5_before", "md5_after",
            "anchor", "rows_before", "rows_after", "rechained_sealed")}}


# ─────────────────────────────────────────────────────────── CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--rebuild-from", help="YYYY-MM-DD: dựng lại (kiểm) từ phiên này (dòng sealed chỉ được SO)")
    ap.add_argument("--from-cache", help="thư mục có panel.parquet + ca.parquet (dựng offline, không BQ)")
    ap.add_argument("--src2-csv", help="CSV date,close của DNSE (dựng offline, không mạng)")
    ap.add_argument("--dry-run", action="store_true", help="--update nhưng không ghi file")
    ap.add_argument("--check", action="store_true", help="chạy cổng cho --period; rc≠0 nếu hỏng")
    ap.add_argument("--period", nargs=2, metavar=("MOC", "DEN"))
    ap.add_argument("--series", default=SERIES_PATH)
    ap.add_argument("--membership", default=MEMBERSHIP_LATEST)
    ap.add_argument("--acks", default=ACKS_PATH)
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--restate-sealed", nargs="+", metavar="DATE",
                    help="ĐÍNH CHÍNH dòng sealed: dựng lại từ dữ liệu hiện tại + nối lại đuôi + ghi sổ")
    ap.add_argument("--undo-last-restatement", action="store_true",
                    help="HOÀN TÁC đính chính cuối trong sổ (chỉ khi file còn đúng md5_after của nó); ghi dòng undo")
    ap.add_argument("--reason", help="lý do (bắt buộc với --restate-sealed / --undo-last-restatement; trích số thật)")
    ap.add_argument("--confirmed-by", help="người xác nhận + thời điểm (bắt buộc với --restate-sealed / --undo-last-restatement)")
    ap.add_argument("--restate-log", default=RESTATE_LOG, help="sổ đính chính chỉ-thêm (JSONL)")
    a = ap.parse_args(argv)
    if a.selfcheck:
        import vnindex_total_return_selfcheck as sc
        return sc.main()
    if a.undo_last_restatement:
        if a.update or a.restate_sealed:
            ap.error("--undo-last-restatement là việc riêng — chạy từng lệnh")
        try:
            res = undo_last_restatement(a.reason, a.confirmed_by, a.series, write=not a.dry_run,
                                        log_path=a.restate_log)
        except RestateRefused as exc:
            print(f"LỖI vnindex_total_return --undo-last-restatement: {exc}", file=sys.stderr)
            return 4
        print(json.dumps(res, ensure_ascii=False))
        return 0
    if a.update or a.restate_sealed:
        inputs = src2 = None
        if a.from_cache:
            import pandas as pd
            try:
                import db_dtypes  # noqa: F401 — cột DATE của BQ trong parquet
            except ImportError:
                pass
            def _load(name):
                pq = os.path.join(a.from_cache, f"{name}.parquet")
                return pd.read_parquet(pq) if os.path.exists(pq) else \
                    pd.read_csv(os.path.join(a.from_cache, f"{name}.csv"))
            inputs = {"panel": _load("panel"), "ca": _load("ca"), "ca_max_ingested_utc": None}
            ca = inputs["ca"]
            if "ingested_at" in ca.columns and len(ca):
                inputs["ca_max_ingested_utc"] = str(ca.ingested_at.max())
        if a.src2_csv:
            with open(a.src2_csv) as f:
                src2 = {_d(r["date"]): float(r["close"]) for r in csv.DictReader(f)}
        try:
            if a.restate_sealed:
                if a.update:
                    ap.error("--restate-sealed và --update là hai việc riêng — chạy từng lệnh")
                res = restate_sealed(a.restate_sealed, a.reason, a.confirmed_by, a.series, a.membership,
                                     inputs=inputs, src2=src2, write=not a.dry_run, acks_path=a.acks,
                                     log_path=a.restate_log)
            else:
                res = update(a.series, a.membership, inputs=inputs, src2=src2, write=not a.dry_run,
                             rebuild_from=a.rebuild_from, acks_path=a.acks)
        except RestateRefused as exc:
            print(f"LỖI vnindex_total_return --restate-sealed: {exc}", file=sys.stderr)
            return 4
        except SealedChanged as exc:
            print(f"LỖI vnindex_total_return --update: {exc}", file=sys.stderr)
            return 2
        except BuildRefused as exc:
            print(f"LỖI vnindex_total_return --update: {exc}", file=sys.stderr)
            return 3
        print(json.dumps(res, ensure_ascii=False))
        return 0
    if a.period:
        try:
            series = read_series(a.series)
        except (OSError, ValueError) as exc:
            print(f"LỖI vnindex_total_return: {type(exc).__name__} ({exc})", file=sys.stderr)
            return 1
        res = benchmark_period(a.period[0], a.period[1], series=series, acks_path=a.acks)
        res.update({"anchor_date": a.period[0], "end_date": a.period[1]})
        print(json.dumps(res, ensure_ascii=False, indent=1))
        if res["status"] != "ok":
            print(f"CỔNG HỎNG ({a.period[0]} → {a.period[1]}): {res['reason']}", file=sys.stderr)
            return 1
        return 0
    if a.check:
        ap.error("--check cần --period MOC DEN")
    ap.error("cần --update | --restate-sealed DATE... | --period MOC DEN [--check] | --selfcheck")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
