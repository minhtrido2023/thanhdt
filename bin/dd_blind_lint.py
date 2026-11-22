#!/usr/bin/env python3
"""dd_blind_lint — kiểm brief / fact-pack giao cho agent đọc ngành / định giá MÙ không rò giá/mã.

  python3 bin/dd_blind_lint.py <file>... [--ticker MÃ]... [--mode sector|valuation|skeptic] [--json]

rc=0 sạch · rc=1 có vi phạm · rc=2 lỗi dùng/không đọc được file.
Chỉ CẢNH BÁO + rc (chưa nối dispatch.sh). Miễn từng dòng: `<!-- blind-ok: lý do -->`.
Hằng tắt: MIKE_BLIND_LINT=off ⇒ rc=0 + cảnh báo.
Danh sách 36 mã lấy từ kb/dd_price_zones.json (chỉ ĐỌC).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZONES = os.path.join(ROOT, "kb", "dd_price_zones.json")
KINDS = ["PRICE_TOKEN", "MULTIPLE", "MARKET_CAP", "TICKER", "PATH_LEAK", "FORWARD_RETURN", "VERDICT_LEAK"]
EXEMPT = re.compile(r"<!--\s*blind-ok\s*:", re.I)

_CTX = re.compile(r"cổ phiếu|vùng|tâm|target|mục tiêu|price|đóng cửa|thị giá", re.I)
_NUM_K = re.compile(r"(?<![\w.,])\d{2,3}(?:[.,]\d+)?(?:\s*[–\-]\s*\d{2,3}(?:[.,]\d+)?)?\s*k\b(?!\w)(?!\s*(?:/|thùng|tấn|dwt|m[²³23]|kg|bbl|TEU|người|USD|MW|kWh|tỷ|triệu|lượt|căn|xe))", re.I)
_STK = r"(?:cổ phiếu|\bcp\b|thị giá|giá đóng cửa|đóng cửa|vùng|tâm|target|mục tiêu|nội tại|tham chiếu|thị trường|\bprice\b)"
_PRICE = [
    # "71.000đ" chỉ tính khi dòng có ngữ cảnh giá CỔ PHIẾU (giá hàng hoá "50.000 đ/tấn" không phải rò giá)
    re.compile(r"(?<![\d.,])\d{2,3}[.,]\d{3}\s*(?:đ|đồng|VND)(?!\w)(?!\s*/)", re.I),
    re.compile(r"\b(?:giá\s*(?:cổ\s*phiếu|đóng\s*cửa|thị\s*trường|thị\s*giá|mục\s*tiêu|tham\s*chiếu|hiện\s*tại)|vùng|(?<!trung\s)(?<!ly\s)tâm|target|mục\s*tiêu)\b[^\n.;|]{0,25}?(?<![\d.,])\d{2,3}[.,]\d{3}(?![\d.,]*\d)", re.I),
]
_PRICE_NEEDS_STK = {0}  # chỉ số regex cần _STK trên cùng dòng
_STK_RE = re.compile(_STK, re.I)
_NEG = re.compile(r"không|chưa|\bmù\b|blind|\bnot\b|\bnever\b|cấm|tránh|\bno\b|loại bỏ|ẩn", re.I)
_MULT = [
    re.compile(r"(?<![A-Za-z/])(?:P/?E|P/?B|EV/EBITDA|EV/EBIT)(?![A-Za-z])\s*(?:[:=≈~]|của|TTM|fwd|forward|trailing)?\s*(?!(?:19|20)\d\d)\d", re.I),
    re.compile(r"(?<![A-Za-z/])(?:P/E|P/B|EV/EBITDA)[^\n|]{0,15}?\d+(?:[.,]\d+)?\s*x\b", re.I),
]
_MCAP = [
    re.compile(r"(?<!vay\s)(?:vốn\s*ho[áa]|market\s*cap)[^\n;]{0,30}?\d", re.I),
    re.compile(r"\d[^\n]{0,15}tỷ(?:\s*đồng)?\s*vốn\s*ho[áa]", re.I),
]
_FWD = [
    re.compile(r"forward[\s_-]*return|lợi\s*suất\s*kỳ\s*vọng|profit_(?:2W|1M|2M|3M)", re.I),
    re.compile(r"kỳ\s*vọng\s*[+\-−]\d+(?:[.,]\d+)?\s*%", re.I),
]
_VERD = [
    re.compile(r"(?:cổ\s*phiếu|định\s*giá|\bmã\b|vùng|valuation|thị\s*giá)(?:\s+\S+){0,3}?\s+(?:đang\s+|khá\s+|quá\s+|còn\s+|rất\s+)?(?<!\w)(?:rẻ|đắt)(?!\w)", re.I),
    re.compile(r"\b(?:QUALIFY|CONFIRMED|REFUTED)\b"),
    re.compile(r"khuyến\s*nghị\s*(?:mua|bán)", re.I),
    re.compile(r"trung\s*(?:dung|tính)\s*[—-]|(?:DƯỚI|TRÊN)\s*vùng|vùng\s*mua|vùng\s*giá", re.I),
]
_PATH = [
    re.compile(r"\bdd_blind_[A-Za-z0-9]+"),
    re.compile(r"(?<![A-Za-z0-9])dd_[A-Z]{3,4}_\d{8}"),
    re.compile(r"(?<![A-Za-z0-9])[A-Z]{3,4}_DD_"),
]
_TBL_PE = re.compile(r"^(?:P/?E|P/?B|PE|PB)\b", re.I)


LEDGER_STOP = {"CSV"}  # trùng từ thường (đuôi file .csv) — gây báo giả, không phải mã cần chặn


def ledger_tickers():
    with open(ZONES, encoding="utf-8") as f:
        return sorted({e["ticker"] for e in json.load(f)["entries"] if e.get("ticker")} - LEDGER_STOP)


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def lint_text(text, tickers=None, ledger=None, mode="sector"):
    """Trả (violations[(line,kind,excerpt)], exempt_count)."""
    out, exempt = [], 0
    lines = text.splitlines()
    tk_res = [re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(t), re.I) for t in (tickers or [])]
    led_res = [(t, re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % t)) for t in (ledger or [])]
    pe_cols = None  # chỉ số cột P/E|P/B của bảng đang đọc
    for i, ln in enumerate(lines, 1):
        is_tbl = ln.lstrip().startswith("|")
        row_hits = []
        if is_tbl:
            cells = _cells(ln)
            if re.fullmatch(r"[\s:\-|]*", ln):
                pass
            elif pe_cols is None:
                cols = [j for j, c in enumerate(cells) if _TBL_PE.match(c)]
                pe_cols = cols if cols else []
                pe_cols = pe_cols or None
                if pe_cols is None:
                    pe_cols = []  # bảng không có cột P/E — đánh dấu đã đọc header
            else:
                for j in pe_cols:
                    if j < len(cells) and re.search(r"\d", cells[j]):
                        row_hits.append(("MULTIPLE", "cột %s=%s" % ("P/E|P/B", cells[j])))
        else:
            pe_cols = None
        hits = list(row_hits)
        for pi, rx in enumerate(_PRICE):
            m = rx.search(ln)
            if m and (pi not in _PRICE_NEEDS_STK or _STK_RE.search(ln)):
                hits.append(("PRICE_TOKEN", m.group(0)))
        for m in _NUM_K.finditer(ln):
            if _CTX.search(ln):
                hits.append(("PRICE_TOKEN", m.group(0)))
                break
        for rx in _MULT:
            m = rx.search(ln)
            if m:
                hits.append(("MULTIPLE", m.group(0)))
                break
        for rx in _MCAP:
            m = rx.search(ln)
            if m:
                hits.append(("MARKET_CAP", m.group(0)))
                break
        for rx in tk_res:
            m = rx.search(ln)
            if m:
                hits.append(("TICKER", m.group(0)))
        for t, rx in led_res:
            m = rx.search(ln)
            if m:
                hits.append(("TICKER", m.group(0)))
        for rx in _PATH:
            m = rx.search(ln)
            if m:
                hits.append(("PATH_LEAK", m.group(0)))
                break
        for t in (tickers or []):
            m = re.search(r"(?<![A-Za-z0-9])dd_%s(?![A-Za-z0-9])|(?<![A-Za-z0-9])%s_DD_" % (re.escape(t), re.escape(t)), ln, re.I)
            if m:
                hits.append(("PATH_LEAK", m.group(0)))
        for rx in _FWD:
            m = rx.search(ln)
            if m and not _NEG.search(ln[max(0, m.start() - 60):m.start()]):
                hits.append(("FORWARD_RETURN", m.group(0)))
                break
        if mode in ("sector", "valuation"):
            for rx in _VERD:
                m = rx.search(ln)
                if m and not _NEG.search(ln[max(0, m.start() - 40):m.start()]):
                    hits.append(("VERDICT_LEAK", m.group(0)))
                    break
        if not hits:
            continue
        if EXEMPT.search(ln):
            exempt += len(hits)
            continue
        seen = set()
        for k, ex in hits:
            if (k, ex) in seen:
                continue
            seen.add((k, ex))
            out.append((i, k, ex))
    return out, exempt


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--ticker", action="append", default=[])
    ap.add_argument("--mode", choices=["sector", "valuation", "skeptic"], default="sector")
    ap.add_argument("--json", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit:
        return 2
    if os.environ.get("MIKE_BLIND_LINT", "").lower() == "off":
        print("CẢNH BÁO: MIKE_BLIND_LINT=off — blind lint BỊ TẮT, không kiểm %d file" % len(a.files), file=sys.stderr)
        return 0
    ledger = None
    if not a.ticker and a.mode == "sector":
        try:
            ledger = ledger_tickers()
        except (OSError, ValueError, KeyError) as e:
            print("LỖI: không đọc được %s: %s" % (ZONES, e), file=sys.stderr)
            return 2
    res, tot_ex, bad = [], 0, False
    for fp in a.files:
        try:
            with open(fp, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError) as e:
            print("LỖI: không đọc được %s: %s" % (fp, e), file=sys.stderr)
            return 2
        v, ex = lint_text(text, a.ticker, ledger, a.mode)
        tot_ex += ex
        bad = bad or bool(v)
        for ln, k, e in v:
            res.append({"file": fp, "line": ln, "kind": k, "excerpt": e})
    if a.json:
        print(json.dumps({"violations": res, "exempt": tot_ex}, ensure_ascii=False, indent=1))
    else:
        for r in res:
            print("%s:%d: %s: %s" % (r["file"], r["line"], r["kind"], r["excerpt"]))
        print("tổng: %d vi phạm · miễn: %d" % (len(res), tot_ex))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
