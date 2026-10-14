#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bảng 3.2 "Hiệu suất lũy kế" (weekly/monthly) — RENDER từ đầu ra `nav_period_returns.py` và CỔNG đối
chiếu ô chỉ số trong báo cáo với chính đầu ra đó (quỹ bước 4, SPEC §A5/§B4). Một module giữ cả hai để
tên cột/nhãn dòng của người soạn và của cổng không thể trôi khỏi nhau.

    python3 mike/bin/period_table_32.py --account ZaloPay --report-date 2026-10-09 [--with-sleeve]

Cột: | Giai đoạn | <TK> | VN-Index (giá) | VN-Index có cổ tức | Chênh so giá | Chênh so có cổ tức |
Số lấy NGUYÊN từ CLI (không tự trừ lại). Cột có cổ tức = `vnindex_tr_pct` (cờ Q2, mặc định tr_net).
Ô không có số ⇒ `chưa có số (<lý do>)` — KHÔNG in chỉ số giá vào cột có cổ tức, KHÔNG bỏ cột.

Cổng (`check_report`): ô chỉ số/chênh lệch CLI ⩽ 0,005 điểm %; cột có cổ tức `chưa có số` ở chuỗi
chính ⇒ CHẶN (Q9, user 2026-10-14); ở dòng "Phần bot quản lý" (chuỗi b) ⇒ cho qua (số chính thức là a).
CLI rc≠0 ⇒ CHẶN. Selfcheck: `period_table_32_selfcheck.py`.
"""
import argparse
import datetime
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

COL_PRICE, COL_TR = "VN-Index (giá)", "VN-Index có cổ tức"
COL_XP, COL_XT = "Chênh so giá", "Chênh so có cổ tức"
NO_NUMBER = "chưa có số"
SLEEVE_LABEL = "Phần bot quản lý (không gồm DGC)"
CELL_TOL_PP = 0.005           # SPEC §A5: dung sai làm tròn hiển thị 2 chữ số
PERIODS = (("wtd", "Tuần này"), ("mtd", "Từ đầu tháng"), ("inception", "Từ khi bắt đầu hoạt động"))


# ─────────────────────────────────────────────────────────── render

def _ddmm(iso: str) -> str:
    return f"{iso[8:10]}/{iso[5:7]}"


def fmt_num(x: float, unit: str) -> str:
    """-1.157 → '−1,16%' (dấu trừ U+2212, thập phân phẩy, 2 chữ số); unit '%' hoặc 'pp'."""
    s = f"{x:+.2f}".replace(".", ",")
    s = s.replace("-", "−") if s.startswith("-") else s
    return s + unit if s not in ("+0,00", "−0,00") else "0,00" + unit


def _label(key: str, p: dict, report_date: str) -> str:
    rng = f"{_ddmm(p['from_date'])} → {_ddmm(p['to_date'])}"
    if key == "wtd":
        return f"Tuần này ({rng})"
    if key == "mtd":
        return f"Từ đầu tháng {int(report_date[5:7])} (MTD, {rng})"
    return f"Từ khi bắt đầu hoạt động ({rng})"


def _na(why) -> str:
    return f"{NO_NUMBER} ({str(why).replace('|', '/')})"      # '|' trong lý do sẽ vỡ bảng markdown


def _cells(p: dict) -> list:
    bm = p.get("benchmark") or {}
    na = _na(bm.get("reason") or "không có khối benchmark")
    price = bm.get("vnindex_price_pct")
    tr = bm.get("vnindex_tr_pct")
    return [fmt_num(p["return_pct"], "%"),
            fmt_num(price, "%") if price is not None else na,
            fmt_num(tr, "%") if tr is not None else na,
            fmt_num(bm["excess_vs_price_pp"], "pp") if bm.get("excess_vs_price_pp") is not None else na,
            fmt_num(bm["excess_vs_tr_pp"], "pp") if bm.get("excess_vs_tr_pp") is not None else na]


def render(main: dict, sleeve: dict = None) -> str:
    """Bảng markdown + chú thích. `sleeve` = đầu ra `--sleeve bot` (dict có `inception`) hoặc dict
    `{"status": "unavailable", "reason": ...}` hoặc None (không có dòng b)."""
    acc, rd = main["account"], main["report_date"]
    lines = [f"| Giai đoạn | {acc} | {COL_PRICE} | {COL_TR} | {COL_XP} | {COL_XT} |",
             "|---|---:|---:|---:|---:|---:|"]
    for key, _ in PERIODS:
        p = main.get(key)
        if p is not None:
            lines.append("| " + " | ".join([_label(key, p, rd)] + _cells(p)) + " |")
    if sleeve is not None:
        for key, _ in PERIODS:
            if sleeve.get("status") == "unavailable":
                cells = [_na(sleeve.get("reason"))] * 5
                lbl = f"{SLEEVE_LABEL} — {dict(PERIODS)[key]}"
            else:
                p = sleeve.get(key)
                if p is None:
                    continue
                cells = _cells(p)
                lbl = f"{SLEEVE_LABEL} — {_label(key, p, rd)}"
            lines.append("| " + " | ".join([lbl] + cells) + " |")
    foot = next((main[k]["benchmark"]["footnote"] for k in ("inception", "mtd", "wtd")
                 if main.get(k) and main[k].get("benchmark", {}).get("footnote")), None)
    notes = [foot] if foot else []
    if sleeve is not None and sleeve.get("status") != "unavailable" and sleeve.get("inception"):
        nav_a, nav_b = main["inception"]["nav1"], sleeve["inception"]["nav1"]
        tick = ", ".join(e["ticker"] for e in sleeve.get("outside_scope", [])) or "—"
        notes.append(f"Dòng \"{SLEEVE_LABEL}\": loại phần ngoài bot ({tick}) ≈ "
                     f"{fmt_num(100 * (1 - nav_b / nav_a), '%').lstrip('+')} NAV ngày {_ddmm(rd)}; "
                     f"số chính thức của tài khoản là các dòng phía trên.")
    return "\n".join(lines) + ("\n\n" + "\n".join(f"_{n}_" for n in notes) if notes else "") + "\n"


# ─────────────────────────────────────────────────────────── đọc bảng trong báo cáo

def parse_cell(cell: str):
    """'−1,16%' / '+1,91pp' → float; ô bắt đầu bằng 'chưa có số' → NO_NUMBER; còn lại → None."""
    c = cell.strip()
    if c.lower().startswith(NO_NUMBER):
        return NO_NUMBER
    m = re.fullmatch(r"\**([+\-−]?\d+(?:,\d+)?)\s*(%|pp)\**", c)
    if not m:
        return None
    v = float(m.group(1).replace("−", "-").replace(",", "."))
    return v if math.isfinite(v) else None


def find_table(text: str):
    """(header_cells, [row_cells...]) của bảng NGAY dưới tiêu đề chứa 'Hiệu suất lũy kế', hoặc None."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("#") and "Hiệu suất lũy kế" in ln:
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("|"):
                if lines[j].lstrip().startswith("#"):
                    return None
                j += 1
            rows = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            if len(rows) < 2:
                return None
            return rows[0], [r for r in rows[2:]]
    return None


def _period_of(label: str):
    sleeve = SLEEVE_LABEL.split(" (")[0] in label
    for key, kw in PERIODS:
        if kw in label:
            return sleeve, key
    return sleeve, None


# ─────────────────────────────────────────────────────────── cổng

class TableBlock(RuntimeError):
    pass


def run_cli(account: str, report_date: str, sleeve: bool = False, bin_dir: str = HERE) -> tuple:
    """(rc, json|None, stderr) của `<bin_dir>/nav_period_returns.py` (cổng giao báo cáo truyền bin của
    cây canonical, cùng chỗ `_check_period_returns` gọi)."""
    cmd = [sys.executable, os.path.join(bin_dir, "nav_period_returns.py"), "--account", account,
           "--report-date", report_date] + (["--sleeve", "bot"] if sleeve else [])
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        j = json.loads(p.stdout)
    except json.JSONDecodeError:
        j = None
    return p.returncode, j, p.stderr


def _series_installed() -> bool:
    import vnindex_total_return as vtr
    return os.path.exists(vtr.SERIES_PATH)


def check_report(name: str, text: str, account: str, report_date: str, cli=run_cli,
                 series_installed=_series_installed) -> list:
    """Trả list dòng PASS (để in); vi phạm ⇒ TableBlock (thông điệp trích đúng ô + số CLI — §29).
    Chỉ gọi cho weekly/monthly. Không có bảng 3.2 ⇒ [] (cổng period-return cũ lo phần đó)."""
    t = find_table(text)
    if t is None:
        return [f"benchmark-table SKIP ({name}): không có bảng 'Hiệu suất lũy kế'"]
    header, rows = t
    idx = {c: header.index(c) for c in (COL_PRICE, COL_TR, COL_XP, COL_XT) if c in header}
    if COL_TR not in idx:
        if series_installed():
            raise TableBlock(f"benchmark-table BLOCK ({name}): bảng 'Hiệu suất lũy kế' thiếu cột "
                             f"'{COL_TR}' (header {header}) — chuỗi VN-Index có cổ tức đã có, KHÔNG được "
                             f"bỏ cột; render bằng `period_table_32.py --account {account} --report-date "
                             f"{report_date}`")
        return [f"benchmark-table WARN ({name}): bảng định dạng cũ (không có cột '{COL_TR}'), chuỗi "
                f"VN-Index có cổ tức chưa cài — bỏ qua"]
    missing = [c for c in (COL_PRICE, COL_XP, COL_XT) if c not in idx]
    if missing:
        raise TableBlock(f"benchmark-table BLOCK ({name}): có cột '{COL_TR}' nhưng thiếu {missing} "
                         f"(header {header})")
    need_sleeve = any(_period_of(r[0])[0] for r in rows if r)
    out = {}
    rc, j, err = cli(account, report_date, False)
    if rc != 0 or not j:
        raise TableBlock(f"benchmark-table BLOCK ({name}): nav_period_returns.py --account {account} "
                         f"--report-date {report_date} rc={rc} — không có số chuẩn để đối chiếu. "
                         f"stderr: {(err or '').strip()[-400:] or '(rỗng)'}")
    out[False] = j
    if need_sleeve:
        rc, j, err = cli(account, report_date, True)
        if rc not in (0, 3) or not j:
            raise TableBlock(f"benchmark-table BLOCK ({name}): nav_period_returns.py --account {account} "
                             f"--report-date {report_date} --sleeve bot rc={rc}. stderr: "
                             f"{(err or '').strip()[-400:] or '(rỗng)'}")
        out[True] = j
    passes = []
    for r in rows:
        if not r or len(r) <= max(idx.values()):
            continue
        sleeve, key = _period_of(r[0])
        cells = {c: (r[i], parse_cell(r[i])) for c, i in idx.items()}
        if key is None:
            nums = [c for c, (_, v) in cells.items() if isinstance(v, float)]
            if nums:
                raise TableBlock(f"benchmark-table BLOCK ({name}): dòng {r[0]!r} có số ở cột {nums} nhưng "
                                 f"không thuộc kỳ nào CLI đưa ra (Tuần này / Từ đầu tháng / Từ khi bắt đầu "
                                 f"hoạt động) — không đối chiếu được")
            continue
        res = out[sleeve]
        tag = f"{'(b) ' if sleeve else ''}{key}"
        if res.get("status") == "unavailable":          # chuỗi b chưa có số
            bad = [f"{c}={raw!r}" for c, (raw, v) in cells.items() if v != NO_NUMBER]
            if bad:
                raise TableBlock(f"benchmark-table BLOCK ({name}): dòng {r[0]!r}: CLI --sleeve bot nói "
                                 f"chưa có số ({res.get('reason')}) nhưng bảng ghi {bad}")
            passes.append(f"{tag}: chưa có số (đúng CLI)")
            continue
        p = res.get(key)
        bm = (p or {}).get("benchmark")
        if not bm:
            raise TableBlock(f"benchmark-table BLOCK ({name}): CLI không có kỳ {key} / khối benchmark "
                             f"cho dòng {r[0]!r}")
        want = {COL_PRICE: bm.get("vnindex_price_pct"), COL_TR: bm.get("vnindex_tr_pct"),
                COL_XP: bm.get("excess_vs_price_pp"), COL_XT: bm.get("excess_vs_tr_pp")}
        for c, (raw, v) in cells.items():
            w = want[c]
            if w is None:
                if v != NO_NUMBER:
                    raise TableBlock(f"benchmark-table BLOCK ({name}): dòng {r[0]!r} cột '{c}' = {raw!r} "
                                     f"nhưng CLI không có số ({bm.get('reason')}) — phải ghi "
                                     f"'{NO_NUMBER} (lý do)', KHÔNG thay bằng số khác")
                if c in (COL_TR, COL_XT) and not sleeve:
                    raise TableBlock(f"benchmark-table BLOCK ({name}): cột '{c}' dòng {r[0]!r} chưa có số "
                                     f"({bm.get('reason')}) — Q9 (user 2026-10-14): weekly/monthly CHẶN gửi "
                                     f"khi cột có cổ tức thiếu số")
                continue
            if not isinstance(v, float):
                raise TableBlock(f"benchmark-table BLOCK ({name}): dòng {r[0]!r} cột '{c}' = {raw!r} không "
                                 f"đọc ra số; CLI = {w:+.3f}")
            if abs(v - w) > CELL_TOL_PP + 1e-9:
                raise TableBlock(f"benchmark-table BLOCK ({name}): dòng {r[0]!r} cột '{c}' = {raw!r}, CLI "
                                 f"= {w:+.3f} — lệch {abs(v - w):.3f} > {CELL_TOL_PP} điểm %")
        if not sleeve:
            foot = bm.get("footnote")
            if foot and foot not in text:
                raise TableBlock(f"benchmark-table BLOCK ({name}): thiếu chú thích cố định dưới bảng: "
                                 f"{foot!r} (cờ {bm.get('tr_kind')})")
        passes.append(f"{tag}: khớp CLI")
    if not passes:
        raise TableBlock(f"benchmark-table BLOCK ({name}): có cột '{COL_TR}' nhưng không dòng nào đối "
                         f"chiếu được")
    return [f"benchmark-table PASS ({name}): " + "; ".join(passes)]


# ─────────────────────────────────────────────────────────── CLI

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--account", required=True, choices=["SpaceX", "ZaloPay"])
    ap.add_argument("--report-date", required=True)
    ap.add_argument("--with-sleeve", action="store_true", help="thêm dòng 'Phần bot quản lý' (chuỗi b)")
    a = ap.parse_args()
    datetime.date.fromisoformat(a.report_date)
    rc, main_j, err = run_cli(a.account, a.report_date)
    if rc != 0 or not main_j:
        print(f"LỖI period_table_32: nav_period_returns rc={rc}: {err.strip()[-400:]}", file=sys.stderr)
        return 1
    sleeve = None
    if a.with_sleeve:
        rc, sleeve, err = run_cli(a.account, a.report_date, True)
        if rc not in (0, 3) or not sleeve:
            print(f"LỖI period_table_32: --sleeve bot rc={rc}: {err.strip()[-400:]}", file=sys.stderr)
            return 1
    sys.stdout.write(render(main_j, sleeve))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
