#!/usr/bin/env python3
"""CỔNG CHẶN CỨNG — mọi tỉ suất per-position công bố trong báo cáo phải đã cộng cổ tức.

Vì sao tồn tại (coding_guidelines §22 — "luật sống trong văn xuôi mà LLM cứ áp sai mỗi lần thì
chuyển thành code"): §21 nói "PHẢI đi qua `dividend_adjusted_return.py`" bằng VĂN XUÔI, và đã bị
áp sai **HAI LẦN** trên báo cáo gửi nhà đầu tư:

  * lần 1 (2026-08-02, job Taylor_20260802_060243) — quên cộng cổ tức của các sự kiện TRONG kỳ;
  * lần 2 (2026-08-10, job Taylor_20260810_030558) — người viết báo cáo tuần 03→07/08 kiểm tra
    `cum_dividend_excl`=0 (cổ tức PHÁT SINH trong đúng tuần đó) rồi kết luận "không cần điều
    chỉnh". SAI TÍN HIỆU: 6 sự kiện có ex-date TRƯỚC tuần báo cáo (MBB 09/07, BID 17/07, CTG+VCB
    23/07, NCT 27/07, SAB 28/07) vẫn nằm trong giá vốn của vị thế ĐANG GIỮ. Hậu quả: SpaceX công
    bố −3,28% thay vì −1,94%; SAB −5,53% thay vì +0,49% (đảo dấu); ZaloPay −0,75% thay vì +0,60%
    (đảo dấu).

Bài học đóng vào code: tín hiệu đúng KHÔNG phải "tuần này có cổ tức không" mà là "giá vốn đang
dùng có khớp giá vốn broker không". Cổng này KHÔNG đọc `verified_snapshot_*.json` (nguồn sinh ra
số sai) — nó dựng lại kỳ vọng từ HAI nguồn độc lập với nhau và với báo cáo:

    (1) `costPrice` trong `positions` của DNSE (`dnse_raw_*.jsonl`) — broker TỰ trừ cổ tức GỘP
        khỏi giá vốn, nên nó là nhân chứng độc lập cho CẢ hai lỗi: thiếu cổ tức, và sai cơ sở
        giá vốn vì lý do khác (ca LPB 2026-08-07: báo cáo 52.583,3 vs broker 51.466,7 — bình
        quân gia quyền của `verify_account_snapshot.py` không RESET khi vị thế về 0 rồi mua lại).
    (2) `dividend_adjusted_return.resolve_dividends()` — cổ tức GỘP đồng/cp giải ra từ tiền mặt
        broker thật, dùng để cộng lại phần thuế TNCN 5% (Bẫy 5).

Đẳng thức kỳ vọng (quy ước báo cáo: mẫu số = giá vốn THÔ, cổ tức RÒNG cộng vào TỬ SỐ — §21):

    lãi/lỗ RÒNG = qty×(giá − costPrice_broker) − thuế5%×qty×cổ_tức_GỘP
    giá vốn THÔ = costPrice_broker + cổ_tức_GỘP
    %           = lãi/lỗ RÒNG / (qty × giá vốn THÔ) × 100

Hưởng quyền tính RIÊNG từng tài khoản qua `_qty_at()` (ca thật: ZaloPay KHÔNG hưởng cổ tức MBB
09/07 vì chưa nắm giữ tại ngày chốt quyền, trong khi SpaceX hưởng trên 2.400cp).

PHẠM VI (nói thẳng, không cắt âm thầm): chỉ phủ bảng **vị thế ĐANG GIỮ cuối kỳ** — khớp theo cặp
(mã, KL) với sổ vị thế broker. Bảng lãi/lỗ ĐÃ THỰC HIỆN (KL đã bán, không còn trong `positions`)
KHÔNG được cổng này kiểm; cổng in rõ số dòng nó không phủ.

    python3 mike/bin/report_return_gate.py --report mike/reports/<file>.md
    python3 mike/bin/report_return_gate.py --selfcheck      # offline, không cần BQ/log
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dividend_adjusted_return as dar  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXEC_DIR = os.path.join(ROOT, "data", "execution_logs")
LOOKBACK_DAYS = 120          # đủ phủ mọi ex-date còn nằm trong giá vốn của vị thế đang giữ
DEFAULT_TOL_PP = 0.15        # điểm %; nới hơn sai số làm tròn giá vốn 2 chữ số, chặt hơn mọi cổ tức thật

# chân SỔ PAPER (thêm 2026-08-13). Nhận diện theo NỘI DUNG, không theo tên file: mục paper đi vào
# báo cáo "New deals" — tên file KHÔNG chứa nhãn tài khoản nào, nên chân broker ở trên tự bỏ qua.
#
# Cả 2 marker PHẢI neo vào heading mà newdeals_daily_report.py TỰ KIỂM SOÁT ("## AlphaLens Paper
# Portfolio" / "## DC Book Paper Portfolio" — parts[] trong build_message()), KHÔNG neo vào text
# nội bộ của converge_report.py/alphalens_report.py (thư viện khác, đổi độc lập không ai báo).
# quant-skeptic vòng 3 (Taylor_20260813_073404): marker cũ "DC Book (double-confirm)" chỉ tình cờ
# khớp một dòng "### 🔗 DC Book (double-confirm) — Paper Portfolio" bên TRONG converge_md — không
# khớp heading thật mà newdeals_daily_report.py tự in ra; đổi tên heading nội bộ đó (không ai
# review vì nó không đụng gate) sẽ âm thầm vô hiệu hoá gate.
PAPER_MARKERS = ("AlphaLens Paper Portfolio", "DC Book Paper Portfolio")


# ---------------------------------------------------------------- nguồn (1): broker
def broker_positions(account_no: str, asof: str) -> dict:
    """{mã: (qty, costPrice, marketPrice)} từ bản ghi `positions` CUỐI CÙNG của ngày `asof`.

    §12: lọc `account_no` TRƯỚC mọi phép tính — file dnse_raw dùng chung mọi tài khoản.
    """
    path = os.path.join(EXEC_DIR, f"dnse_raw_{asof}.jsonl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"thiếu {path} — không dựng được kỳ vọng, CHẶN (fail-closed)")
    last = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(rec.get("account_no")) != str(account_no) or rec.get("kind") != "positions":
                continue
            last = rec
    if last is None:
        raise ValueError(f"không có bản ghi positions nào của {account_no} ngày {asof} — CHẶN")
    out = {}
    for p in last["payload"].get("positions", []):
        if str(p.get("accountNo")) != str(account_no):
            continue
        qty = float(p.get("openQuantity") or 0)
        if qty <= 0:
            continue
        out[p["symbol"]] = (qty, float(p.get("costPrice") or 0), float(p.get("marketPrice") or 0))
    return out


# ---------------------------------------------------------------- nguồn (2): cổ tức
def entitled_gross(tickers, account_no: str, asof: str) -> dict:
    """{mã: cổ tức GỘP đồng/cp mà CHÍNH tài khoản này được hưởng, ex-date ≤ asof}."""
    start = (_dt.date.fromisoformat(asof) - _dt.timedelta(days=LOOKBACK_DAYS)).isoformat()
    adjs = dar.resolve_dividends(sorted(tickers), start, asof)
    qmap = dar.broker_qty(account_no)
    out = {}
    for a in adjs:
        if a.cash_per_share <= 0 or a.ex_date > asof:
            continue
        if dar._qty_at(qmap, a) <= 0:          # tài khoản này KHÔNG nắm giữ tại ngày chốt quyền
            continue
        out[a.ticker] = out.get(a.ticker, 0.0) + a.cash_per_share
    return out


def expected_pct(qty: float, cost_price: float, market: float, gross_ps: float,
                 tax: float = dar.PIT_DIVIDEND_RATE) -> tuple:
    """(%, lãi/lỗ ròng VND, giá vốn thô/cp) — xem đẳng thức ở docstring đầu file."""
    raw_cost = cost_price + gross_ps
    pl_net = qty * (market - cost_price) - tax * qty * gross_ps
    return pl_net / (qty * raw_cost) * 100.0, pl_net, raw_cost


# ---------------------------------------------------------------- báo cáo
ROW_RE = re.compile(r"^\|\s*(?:\*\*)?([A-Z]{3})(?:\*\*)?\s*\|(.+)\|\s*$")
SEP_RE = re.compile(r"^\|[\s:|-]+\|\s*$")
# Văn xuôi: CHỈ bắt "MÃ +12,3%" / "MÃ −4,5%" — bắt buộc có DẤU và đứng liền mã, nên
# "DGC 46,5% NAV" (tỷ trọng, không dấu) không bị nhận nhầm là tỉ suất.
PROSE_RE = re.compile(r"\b([A-Z]{3})\s*\*{0,2}\s*([+\-−]\d+(?:[.,]\d+)?)\s*%")
# Cột % nào là TỈ SUẤT lãi/lỗ (được kiểm) — cột nào là tỷ trọng (bỏ qua).
PCT_HEADER_OK = ("lãi", "lai/lo", "tỉ suất", "ti suat", "return", "p&l")
PCT_HEADER_NO = ("nav", "tỷ trọng", "ty trong", "phân bổ", "phan bo", "trần", "quota")


def _num(cell: str):
    cell = cell.strip().replace("**", "").replace("−", "-")
    cell = re.sub(r"[^0-9,.\-+]", "", cell)
    if not cell or cell in "+-":
        return None
    cell = cell.replace(".", "").replace(",", ".")   # định dạng VN: 1.234,5
    try:
        return float(cell)
    except ValueError:
        return None


def _pick_columns(header_cells: list) -> tuple:
    """(chỉ số cột KL, chỉ số cột % TỈ SUẤT) — None nếu bảng này không công bố tỉ suất.

    Chọn theo TIÊU ĐỀ, không theo vị trí: bảng Mục 5.3 có 2 cột `%` nhưng cả hai là **tỷ trọng
    NAV**, không phải tỉ suất — lấy "ô % cuối dòng" sẽ kiểm nhầm tỷ trọng vào tỉ suất.
    """
    qty_i = pct_i = None
    for i, h in enumerate(header_cells):
        low = h.strip().lower().replace("*", "")
        if qty_i is None and (low == "kl" or "khối lượng" in low or "khoi luong" in low):
            qty_i = i
        if "%" not in low:
            continue
        if any(bad in low for bad in PCT_HEADER_NO):
            continue
        if low == "%" or any(ok in low for ok in PCT_HEADER_OK):
            pct_i = i
    return qty_i, pct_i


def _strip_quote(line: str) -> str:
    """Bóc mọi dấu blockquote `>` đầu dòng (`> | … |` ⇒ `| … |`) rồi trả phần đã lstrip.

    Markdown cho phép lồng (`>> `); bóc lặp để một bảng trong blockquote vẫn được nhận là BẢNG,
    không phải văn xuôi."""
    s = line.lstrip()
    while s.startswith(">"):
        s = s[1:].lstrip()
    return s


def parse_report_rows(path: str) -> list:
    """[(ticker, qty, pct)] — chỉ lấy từ bảng có cột KL **và** cột % là tỉ suất lãi/lỗ."""
    with open(path, encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]
    rows, qty_i, pct_i = [], None, None
    for i, line in enumerate(lines):
        if line.startswith("|") and i + 1 < len(lines) and SEP_RE.match(lines[i + 1]):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            qty_i, pct_i = _pick_columns(cells)
            continue
        if not line.startswith("|"):
            qty_i = pct_i = None
            continue
        if qty_i is None or pct_i is None:
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if max(qty_i, pct_i) >= len(cells):
            continue
        qty, pct = _num(cells[qty_i]), _num(cells[pct_i])
        if qty is None or pct is None:
            continue
        rows.append((m.group(1), qty, pct))
    return rows


def parse_prose_pcts(path: str) -> list:
    """[(ticker, pct, lineno)] công bố trong VĂN XUÔI (vd "NCT −12,5% · TCB −6,1%").

    Bảng không phải chỗ duy nhất tỉ suất lọt ra ngoài: Mục 5.3 của báo cáo tuần 03→07/08 công bố
    tỉ suất từng mã của ZaloPay bằng một câu văn, không có cột nào.

    BỎ QUA dòng bảng — đã do `parse_report_rows()` xử lý theo tiêu đề cột; quét lại ở đây sẽ đọc
    nhầm ô "biến động NGÀY" (`— DGC +6,9%` trong bảng NAV) thành tỉ suất vị thế. Dấu trích dẫn
    `>` đứng trước PHẢI được bóc trước khi nhận diện: bảng tóm tắt của mục ĐÍNH CHÍNH nằm trong
    blockquote (`> | Mã bị đảo dấu | SAB −5,53% | … |`), nên bản đầu của cổng đọc nó thành văn
    xuôi và CHẶN OAN chính báo cáo đã sửa đúng (ca thật 2026-08-10 — xem `_selfcheck` ca 19-21).

    Trả kèm số dòng để `run_gate()` áp luật "cũ → đúng" theo TỪNG DÒNG.
    """
    out = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if _strip_quote(line).startswith("|"):
                continue
            for tk, num in PROSE_RE.findall(line):
                v = _num(num)
                if v is not None:
                    out.append((tk, v, i))
    return out


def excluded_tickers(label: str) -> set:
    """Mã ngoài phạm vi bot (vị thế legacy) — báo cáo KHÔNG công bố tỉ suất từ-ngày-mua cho chúng
    (không có giá vốn xác minh qua journal), nên mọi `MÃ ±x%` của chúng là biến động kỳ, không
    phải tỉ suất vị thế ⇒ cổng không kiểm. Đọc từ config, KHÔNG hardcode (§7)."""
    try:
        sys.path.insert(0, ROOT)
        from trading_bot import config as _cfg
        for p in _cfg.load_accounts(_cfg.load_config()):
            if p["label"] == label:
                return {t.upper() for t in (p.get("excluded_tickers") or [])}
    except Exception as exc:                       # thiếu secrets/config → không suy diễn
        print(f"⚠️  không đọc được excluded_tickers của {label} ({exc}) — coi như rỗng", file=sys.stderr)
    return set()


def accounts_asof_from_name(path: str) -> tuple:
    """(danh sách nhãn tài khoản, ngày chốt) suy từ TÊN FILE báo cáo."""
    name = os.path.basename(path)
    labels = [lb for lb in dar.ACCOUNTS if lb in name]
    dates = re.findall(r"(\d{4}-\d{2}-\d{2})", name)
    if dates:
        return labels, dates[-1]
    ym = re.search(r"(\d{4})-(\d{2})\.md$", name)
    if ym:                                        # báo cáo tháng → phiên cuối có log trong tháng
        pref = f"dnse_raw_{ym.group(1)}-{ym.group(2)}-"
        days = sorted(f for f in os.listdir(EXEC_DIR) if f.startswith(pref))
        if days:
            return labels, days[-1][len("dnse_raw_"):-len(".jsonl")]
    raise ValueError(f"không suy được ngày chốt từ tên file: {name}")


# ---------------------------------------------------------------- chân SỔ PAPER (T1)
def paper_t1_verdict(book: str, ticker: str, asof: str, adj, price_adjusting_events) -> list:
    """Phán quyết T1 cho MỘT vị thế paper — thuần logic, không I/O (để selfcheck chạy offline).

    `adj` = một `AdjustedEntry`; chỉ đọc `factor_terp`, `factor`, `status`, `degraded`, `note`.
    """
    fails = []
    moved = adj.factor_terp is not None and adj.factor_terp < 1.0 - 1e-6
    has_event = bool(price_adjusting_events)
    if has_event != moved:
        detail = ", ".join(f"{e['event_code']} {e['exright_date']}"
                           for e in price_adjusting_events) or "—"
        fails.append(
            f"{book}/{ticker}: Close/Price {'ĐÃ' if moved else 'KHÔNG'} điều chỉnh sau {asof} "
            f"nhưng corporate_action nói {'KHÔNG có' if moved else 'CÓ'} sự kiện ({detail}) "
            f"— một trong hai nguồn sai, không được công bố tỉ suất khi chưa biết là nguồn nào")
    if adj.degraded:
        fails.append(f"{book}/{ticker}: trạng thái {adj.status} — tỉ suất đang tính trên giá "
                     f"THÔ: {adj.note}")
    return fails


def paper_entry_gate(report_path: str, out=sys.stdout) -> tuple:
    """(applied, fails) — kiểm giá VÀO của sổ paper bằng nguồn ĐỘC LẬP với chuỗi giá.

    Vì sao cần một chân riêng: chân broker ở trên đối chiếu tỉ suất với `costPrice` — sổ paper
    không có tài khoản broker nào để đối chiếu. Giá vào của nó được quy về hệ điều chỉnh bằng
    `Close/Price` (`paper_entry_adjust.py`), và cách hỏng ÂM THẦM của cơ chế đó là factor = 1,0:
    cache giá cũ/lệch vintage cho ra ĐÚNG con số mà "mã này không có sự kiện gì" cũng cho ra.
    Không phân biệt được hai thứ đó = phục hồi nguyên vẹn bug 2026-08-13 (MBB báo −18,8% thay vì
    −2,9%) mà không ai thấy. Nên phép kiểm phải hỏi một nguồn KHÁC: `tav2_bq.corporate_action`.

        T1:  factor_terp < 1  ⟺  tồn tại DIV/ISS executed điều-chỉnh-giá trong (asof, hôm nay]

    T1 neo vào `factor_terp` (Close/Price thô) chứ KHÔNG phải factor được dùng để báo cáo: T1 hỏi
    "chuỗi giá có điều chỉnh không", đó là câu hỏi về chuỗi giá. Quy ước accrue-only (loại quyền
    mua) là lựa chọn của TA ở tầng trên; một sự kiện quyền-mua-đơn-thuần sẽ cho factor accrue-only
    = 1,0 một cách hoàn toàn đúng đắn, và neo T1 vào nó sẽ sinh báo động giả.

    Mọi trạng thái `degraded` (`RIGHTS_UNRESOLVED`, `VINTAGE_STALE`, `BAD_FACTOR`, `NO_DATA`) đều
    CHẶN: báo cáo đang in tỉ suất tính trên giá THÔ, tức là con số sai kiểu cũ.

    Fail-closed: không tra được `corporate_action` ⇒ CHẶN. Cổng này tồn tại đúng để bắt ca "không
    biết mà tưởng biết"; trả PASS khi không kiểm được là tự vô hiệu hoá mình.
    """
    try:
        with open(report_path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        return False, [f"không đọc được báo cáo: {e}"]
    if not any(m in text for m in PAPER_MARKERS):
        return False, []

    sys.path.insert(0, ROOT)
    try:
        from corp_action_lib import is_price_adjusting
        from paper_entry_adjust import adjust_entries, stale_years
        from paper_entry_corpaction_crosscheck import _bq, load_books
    except Exception as e:
        return True, [f"sổ paper: không nạp được công cụ đối chiếu ({e}) — CHẶN (fail-closed)"]

    books = load_books()
    if not books:
        return True, ["báo cáo có mục sổ paper nhưng không đọc được file paper nào — CHẶN"]

    fails = []
    # KHÔNG chặn theo "có file năm nào cũ không" — đo thật 2026-08-13: 13/14 file năm (2013-2025)
    # cũ hơn 2026.parquet ~14 ngày, đó là trạng thái BÌNH THƯỜNG của cache (sync đêm chỉ ghi lại
    # năm hiện tại). Chặn theo đó = báo động giả trên MỌI báo cáo, và một cổng kêu mỗi ngày là
    # một cổng bị bỏ qua. Việc chặn thuộc về `adjust_entries`, nó gắn VINTAGE_STALE cho ĐÚNG vị
    # thế nào có `asof` rơi vào một năm cũ — và VINTAGE_STALE là `degraded` nên bị chặn bên dưới.
    stale = stale_years()
    used_years = sorted({a[:4] for _, _, a, _ in books})
    if stale:
        print(f"\nℹ️  bq_cache/ticker: {len(stale)} file năm cũ hơn phần còn lại "
              f"({', '.join(sorted(stale))}); sổ paper đang dùng năm {', '.join(used_years)} "
              f"⇒ {'CÓ giao nhau, xem trạng thái VINTAGE_STALE bên dưới' if set(stale) & set(used_years) else 'không giao nhau, không ảnh hưởng'}",
              file=out)

    try:
        adj = adjust_entries([(t, a, p) for _, t, a, p in books])
        tk_sql = ",".join(f'"{t}"' for t in sorted({t for _, t, _, _ in books}))
        asof_min = min(a for _, _, a, _ in books)
        events = _bq(f"""
            SELECT ticker, event_code, CAST(exright_date AS STRING) exright_date,
                   value_per_share, exercise_ratio, issue_method_name_vi
            FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
            WHERE ticker IN ({tk_sql}) AND event_code IN ("DIV", "ISS")
              AND event_status = "executed"
              AND exright_date > DATE "{asof_min}" AND exright_date <= CURRENT_DATE()
        """)
    except Exception as e:
        return True, [f"sổ paper: không đối chiếu được với corporate_action ({str(e)[:150]}) "
                      f"— CHẶN (fail-closed)"]

    by_ticker = {}
    for e in events:
        by_ticker.setdefault(e["ticker"], []).append(e)

    print(f"\nCHÂN SỔ PAPER (T1 — đối chiếu corporate_action, độc lập với chuỗi giá): "
          f"{len(books)} vị thế", file=out)
    for book, ticker, asof, entry_price in books:
        a = adj[(ticker, asof)]
        evs = [e for e in by_ticker.get(ticker, [])
               if e["exright_date"] > asof and is_price_adjusting(e)]
        detail = ", ".join(f"{e['event_code']} {e['exright_date']}" for e in evs) or "—"
        bad = paper_t1_verdict(book, ticker, asof, a, evs)
        print(f"   {'CHẶN' if bad else 'OK  '} {book:9s} {ticker:4s} "
              f"asof={asof} terp={a.factor_terp if a.factor_terp is not None else float('nan'):.6f} "
              f"dùng={a.factor if a.factor is not None else float('nan'):.6f} "
              f"[{a.status}] | {detail}", file=out)
        fails.extend(bad)
    return True, fails


# ---------------------------------------------------------------- cổng
def run_gate(report_path: str, tol_pp: float = DEFAULT_TOL_PP, out=sys.stdout) -> int:
    # chân sổ paper chạy TRƯỚC và độc lập với chân broker: báo cáo "New deals" mang mục paper
    # nhưng không mang nhãn tài khoản nào, nên nhánh thoát sớm dưới đây sẽ bỏ qua nó.
    paper_applied, paper_fails = paper_entry_gate(report_path, out=out)

    labels, asof = accounts_asof_from_name(report_path)
    if not labels:
        if paper_applied:
            if paper_fails:
                print(f"\n❌ CHẶN — {len(paper_fails)} vấn đề ở sổ paper:", file=out)
                for f_ in paper_fails:
                    print(f"   • {f_}", file=out)
                return 1
            print("\n✅ PASS — chân sổ paper khớp corporate_action (chân broker không áp dụng: "
                  "tên file không mang nhãn tài khoản nào).", file=out)
            return 0
        print(f"⚠️  {os.path.basename(report_path)}: không nhận ra tài khoản nào trong tên file "
              f"→ cổng KHÔNG áp dụng (không chặn).", file=out)
        return 0
    rows = parse_report_rows(report_path)
    print(f"CỔNG TỈ SUẤT — {os.path.basename(report_path)} | chốt {asof} | "
          f"tài khoản {', '.join(labels)} | dung sai {tol_pp:.2f}pp", file=out)

    expected, ambiguous, agg, skipped = {}, set(), {}, set()
    for lb in labels:
        acct = dar.ACCOUNTS[lb]
        pos = broker_positions(acct, asof)
        excl = excluded_tickers(lb)
        skipped |= {f"{t} ({lb})" for t in pos if t in excl}
        pos = {t: v for t, v in pos.items() if t not in excl}
        gross = entitled_gross(pos.keys(), acct, asof)
        tot_pl = tot_cost = 0.0
        for tk, (qty, cp, mkt) in pos.items():
            pct, pl, raw = expected_pct(qty, cp, mkt, gross.get(tk, 0.0))
            tot_pl += pl
            tot_cost += qty * raw
            key = (tk, qty)
            if key in expected:                   # 2 tài khoản trùng cả mã lẫn KL → không phân biệt được
                ambiguous.add(key)
            expected[key] = (lb, pct, pl, raw, cp, gross.get(tk, 0.0))
        agg[lb] = (tot_pl, tot_cost, tot_pl / tot_cost * 100.0 if tot_cost else 0.0)

    fails, checked, unmatched = list(paper_fails), 0, 0
    print(f"\n{'ma':5}{'KL':>7}{'TK':>9}{'% cong bo':>11}{'% ky vong':>11}{'lech pp':>9}"
          f"{'co tuc GOP':>11}  ket qua", file=out)
    for tk, qty, pct in rows:
        key = (tk, qty)
        if key not in expected:
            unmatched += 1
            continue
        if key in ambiguous:
            fails.append(f"{tk} KL={qty:.0f}: trùng (mã,KL) ở nhiều tài khoản — không quy được về "
                         f"tài khoản nào, CHẶN (fail-closed)")
            continue
        lb, exp, _pl, _raw, _cp, g = expected[key]
        diff = pct - exp
        ok = abs(diff) <= tol_pp
        checked += 1
        if not ok:
            fails.append(f"{tk} ({lb}, KL={qty:.0f}): báo cáo {pct:+.2f}% vs kỳ vọng {exp:+.2f}% "
                         f"(lệch {diff:+.2f}pp; cổ tức GỘP {g:,.0f}đ/cp)")
        print(f"{tk:5}{qty:>7.0f}{lb:>9}{pct:>11.2f}{exp:>11.2f}{diff:>9.2f}{g:>11,.0f}"
              f"  {'OK' if ok else 'LỆCH'}", file=out)

    # ---- tỉ suất công bố trong VĂN XUÔI (không có KL ⇒ đối chiếu với MỌI tài khoản giữ mã đó)
    by_ticker = {}
    for (tk, _q), (lb, exp, *_r) in expected.items():
        by_ticker.setdefault(tk, []).append((lb, exp))
    # Luật "CŨ → ĐÚNG" (thêm 2026-08-10 sau khi cổng chặn oan chính báo cáo đã sửa): một mục đính
    # chính TỬ TẾ phải nêu lại số SAI bên cạnh số ĐÚNG ("SAB −5,53% → SAB +0,49%"), nên cấm số sai
    # xuất hiện là cấm luôn việc công bố minh bạch. Gom theo (DÒNG, MÃ): dòng nào có ÍT NHẤT một
    # tỉ suất khớp kỳ vọng thì các số còn lại của mã đó trên chính dòng ấy là số đối chiếu/lịch sử.
    # KHÔNG phải lỗ hổng: muốn lách phải in kèm số ĐÚNG ngay cạnh — tức là đã công bố đúng.
    prose_checked, by_line = 0, {}
    for tk, pct, ln in parse_prose_pcts(report_path):
        if tk in by_ticker:
            by_line.setdefault((ln, tk), []).append(pct)
    for (ln, tk), pcts in sorted(by_line.items()):
        cands = by_ticker[tk]
        prose_checked += len(pcts)
        if any(abs(p - e) <= tol_pp for p in pcts for _lb, e in cands):
            continue
        shown = " / ".join(f"{p:+.2f}%" for p in pcts)
        fails.append(f"{tk} (văn xuôi, dòng {ln}): báo cáo {shown} không khớp tài khoản nào — "
                     "kỳ vọng " + ", ".join(f"{lb} {e:+.2f}%" for lb, e in cands))

    # ---- TỔNG kỳ vọng của từng tài khoản: cổng KHÔNG tự dò dòng tổng trong văn bản (quá mong
    # manh), nhưng in ra để người soạn đối chiếu tay — không phủ thì phải nói ra, không im lặng.
    print("\nTỔNG kỳ vọng (vị thế đang giữ, đã cộng cổ tức RÒNG — đối chiếu tay với dòng tổng "
          "trong báo cáo):", file=out)
    for lb, (pl, cost, pct) in agg.items():
        print(f"   {lb:8} giá vốn thô {cost:>15,.0f}  lãi/lỗ tổng {pl:>15,.0f}  {pct:>7.2f}%", file=out)
    if skipped:
        print(f"   (bỏ qua vị thế excluded: {', '.join(sorted(skipped))} — không có giá vốn xác "
              f"minh, báo cáo không công bố tỉ suất từ-ngày-mua)", file=out)

    seen = {(a, b) for a, b, _ in rows}
    prose_tk = {t for t, _, _ in parse_prose_pcts(report_path)}
    nocover = [f"{tk} ({lb}, cổ tức {g:,.0f}đ/cp)" for (tk, q), (lb, _e, _pl, _raw, _cp, g)
               in expected.items() if g > 0 and (tk, q) not in seen and tk not in prose_tk]

    print(f"\nĐã kiểm {checked} dòng bảng + {prose_checked} tỉ suất trong văn xuôi; {unmatched} dòng "
          f"KHÔNG khớp sổ vị thế broker (bảng lãi/lỗ ĐÃ THỰC HIỆN / phân bổ — NGOÀI phạm vi cổng "
          f"này, xem docstring).", file=out)
    if nocover:
        print(f"ℹ️  {len(nocover)} vị thế CÓ cổ tức nhưng báo cáo không công bố tỉ suất riêng "
              f"(không chặn — không công bố thì không sai được): {', '.join(nocover)}", file=out)
    if fails:
        print(f"\n❌ CHẶN — {len(fails)} vấn đề:", file=out)
        for f_ in fails:
            print(f"   • {f_}", file=out)
        print("\n   Sửa: chạy `mike/bin/dividend_adjusted_return.py --resolve <rổ mã> --from … --to …`,"
              "\n   cộng cổ tức RÒNG vào TỬ SỐ (giữ giá vốn THÔ ở mẫu số) — coding_guidelines §21.", file=out)
        return 1
    print("\n✅ PASS — mọi tỉ suất vị thế đang giữ đã khớp kỳ vọng dựng từ sổ broker + cổ tức đã xác minh.",
          file=out)
    return 0


# ---------------------------------------------------------------- selfcheck (offline)
def _selfcheck() -> int:
    ok = True
    ran = []                 # counted, never typed — a hand-written "N ca" drifts silently

    pass_count = 0

    def check(name, got, want):
        nonlocal ok, pass_count
        ran.append(name)
        good = (abs(got - want) < 1e-6) if isinstance(want, float) else (got == want)
        if good:
            pass_count += 1
        else:
            ok = False
        print(f"  {'PASS' if good else 'FAIL'}  {name}: got={got!r} want={want!r}")

    # 1-4: ca THẬT SpaceX 07/08 (số broker), kỳ vọng đã tính tay trong báo cáo đính chính
    pct, pl, raw = expected_pct(1500, 24850.0, 24150.0, 1000.0)
    check("MBB đúng: lãi/lỗ ròng", round(pl), -1_125_000)
    check("MBB đúng: giá vốn thô", raw, 25850.0)
    check("MBB đúng: %", round(pct, 2), -2.90)
    pct0, _, _ = expected_pct(1500, 25850.0, 24150.0, 0.0)
    check("MBB SAI (quên cổ tức) khác đúng > dung sai", abs(pct0 - pct) > DEFAULT_TOL_PP, True)

    # 5-7: NCT — cổ tức lớn nhất, ca đảo hẳn mức lỗ
    pct, pl, raw = expected_pct(500, 86360.0, 82600.0, 8000.0)
    check("NCT: giá vốn thô", raw, 94360.0)
    check("NCT: lãi/lỗ ròng", round(pl), -2_080_000)
    check("NCT: %", round(pct, 2), -4.41)

    # 8-9: SAB — ca ĐẢO DẤU (báo lỗ oan thành lãi)
    pct, _, _ = expected_pct(1100, 44368.1818, 44750.0, 3000.0)
    check("SAB đúng: dương", pct > 0, True)
    pct0, _, _ = expected_pct(1100, 47368.1818, 44750.0, 0.0)
    check("SAB sai: âm (đảo dấu)", pct0 < 0, True)

    # 10: mã KHÔNG cổ tức — cổng không được đụng vào
    pct, pl, raw = expected_pct(3500, 17100.0, 18350.0, 0.0)
    check("PVT (không cổ tức): %", round(pct, 2), 7.31)

    # 11: thuế TNCN 5% thật sự bị trừ khỏi tử số (không phải cộng gộp)
    _, pl_g, _ = expected_pct(1000, 10000.0, 10000.0, 1000.0)
    check("thuế 5% trên cổ tức 1.000đ×1.000cp", round(pl_g), -50_000)

    # 12-18: parser bảng/văn xuôi định dạng VN — gồm CA THẬT gây dương tính giả (bảng % NAV)
    import tempfile
    md = ("| Mã | KL | Giá vốn thật | Giá | Giá trị TT (VND) | Lãi/lỗ | % | Nhóm |\n"
          "|---|---:|---:|---:|---:|---:|---:|---|\n"
          "| NCT | 500 | 94.360,00 | 82.600 | 41.300.000 | −5.880.000 | −12,46% | CAPIT |\n"
          "| SIP | 1.700 | 47.058,80 | 50.900 | 86.530.000 | +6.530.000 | **+8,16%** | CAPIT |\n"
          "| Tiền mặt | | | | 203.656.265 | | | |\n"
          "\n"
          "| Mã | KL | Giá | Giá trị TT (VND) | % NAV | % active NAV | Nhóm |\n"
          "|---|---:|---:|---:|---:|---:|---|\n"
          "| DGC | 10.000 | 44.200 | 442.000.000 | **46,5%** | — | Excluded |\n"
          "| CTG | 1.050 | 32.500 | 34.125.000 | 3,6% | 6,7% | Ngân hàng |\n"
          "\n"
          "Tốt nhất: **CSV +11,4%** · SIP +8,0%. Yếu nhất: **NCT −12,5%** · TCB −6,1%.\n"
          "DGC vẫn là rủi ro lớn nhất (46,5% NAV cuối kỳ).\n"
          "\n"
          "> | Chỉ tiêu | Số CŨ (sai) | Số ĐÚNG |\n"
          "> |---|---:|---:|\n"
          "> | Mã bị đảo dấu | SAB −5,53% | **SAB +0,49%** |\n")
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(md)
        p = fh.name
    rows = parse_report_rows(p)
    prose = parse_prose_pcts(p)
    os.unlink(p)
    check("parser: số dòng bảng (bảng %NAV bị loại)", len(rows), 2)
    check("parser: NCT (âm, dấu − unicode)", rows[0], ("NCT", 500.0, -12.46))
    check("parser: SIP (bold, nghìn phân cách)", rows[1], ("SIP", 1700.0, 8.16))
    check("parser: KHÔNG lấy cột % NAV làm tỉ suất", [r[0] for r in rows], ["NCT", "SIP"])
    check("văn xuôi: bắt đủ 4 tỉ suất có dấu", len(prose), 4)
    check("văn xuôi: CSV +11,4", prose[0][:2], ("CSV", 11.4))
    check("văn xuôi: BỎ QUA '46,5% NAV' (không dấu)", [t for t, _, _ in prose],
          ["CSV", "SIP", "NCT", "TCB"])

    # 19-21: DƯƠNG TÍNH GIẢ THẬT 2026-08-10 — bảng ĐÍNH CHÍNH nằm trong blockquote (`> | … |`).
    # Bản đầu của cổng đọc nó thành văn xuôi ⇒ chặn oan chính báo cáo ĐÃ SỬA ĐÚNG, vì mục đính
    # chính bắt buộc phải nhắc lại số SAI bên cạnh số ĐÚNG.
    check("blockquote `> |` là BẢNG, không phải văn xuôi",
          [t for t, _, _ in prose].count("SAB"), 0)
    check("_strip_quote bóc lồng nhau", _strip_quote(">> | a |"), "| a |")
    # luật "cũ → đúng" theo DÒNG: có số đúng cạnh bên ⇒ không chặn; chỉ có số sai ⇒ chặn
    line_ok = [-5.53, 0.49]
    line_bad = [-5.53]
    check("dòng có CẢ số cũ lẫn số đúng ⇒ KHÔNG chặn",
          any(abs(p - 0.49) <= DEFAULT_TOL_PP for p in line_ok), True)
    check("dòng CHỈ có số cũ ⇒ CHẶN",
          any(abs(p - 0.49) <= DEFAULT_TOL_PP for p in line_bad), False)

    # 15: suy tài khoản + ngày chốt từ tên file
    labels, asof = accounts_asof_from_name(
        "/x/SpaceX_ZaloPay_weekly_report_2026-08-03_to_2026-08-07.md")
    check("tên file → (tài khoản, ngày chốt)", (sorted(labels), asof),
          (["SpaceX", "ZaloPay"], "2026-08-07"))

    # 16: thiếu log broker ⇒ NÉM LỖI (fail-closed), tuyệt đối không im lặng bỏ qua
    try:
        broker_positions("0002023347", "1999-01-01")
        check("thiếu dnse_raw ⇒ fail-closed", "không ném lỗi", "FileNotFoundError")
    except FileNotFoundError:
        check("thiếu dnse_raw ⇒ fail-closed", True, True)

    # 17-24: chân SỔ PAPER (T1). Logic thuần, chạy offline — không chạm BQ, không chạm cache.
    class _A:                                   # thế thân AdjustedEntry, chỉ các trường T1 đọc
        def __init__(self, terp, factor, status, note=None):
            self.factor_terp, self.factor, self.status, self.note = terp, factor, status, note

        @property
        def degraded(self):
            return self.status in ("NO_DATA", "BAD_FACTOR", "RIGHTS_UNRESOLVED", "VINTAGE_STALE")

    DIV = [{"event_code": "DIV", "exright_date": "2026-07-09"}]
    v = lambda a, evs: paper_t1_verdict("alphalens", "MBB", "2026-06-30", a, evs)  # noqa: E731

    check("paper T1: có sự kiện + factor ĐÃ điều chỉnh ⇒ qua",
          v(_A(0.800794, 0.836, "ADJUSTED"), DIV), [])
    # ĐÂY là ca cổng sinh ra để bắt: cache cũ ⇒ factor 1,0 ⇒ status UNCHANGED, trông y hệt
    # "mã này không có sự kiện gì". Bug 2026-08-13 (MBB −18,8%) quay lại qua đúng cửa này.
    check("paper T1: CÓ sự kiện nhưng factor = 1,0 (cache cũ) ⇒ CHẶN",
          len(v(_A(1.0, 1.0, "UNCHANGED"), DIV)), 1)
    check("paper T1: KHÔNG sự kiện nhưng factor < 1 (chuỗi giá điều chỉnh vu vơ) ⇒ CHẶN",
          len(v(_A(0.95, 0.95, "ADJUSTED"), [])), 1)
    check("paper T1: không sự kiện + không điều chỉnh ⇒ qua (không báo động giả)",
          v(_A(1.0, 1.0, "UNCHANGED"), []), [])
    # quy ước accrue-only: quyền mua ĐƠN THUẦN cho factor dùng-để-báo-cáo = 1,0 một cách ĐÚNG
    # ĐẮN. T1 neo vào factor_terp nên không được coi đó là lỗi.
    check("paper T1: quyền mua đơn thuần (accrue-only = 1,0, terp < 1) ⇒ KHÔNG báo động giả",
          v(_A(0.90, 1.0, "UNCHANGED"), [{"event_code": "ISS", "exright_date": "2026-08-11"}]), [])
    for st in ("VINTAGE_STALE", "RIGHTS_UNRESOLVED", "BAD_FACTOR", "NO_DATA"):
        check(f"paper T1: trạng thái {st} ⇒ CHẶN (đang in tỉ suất trên giá THÔ)",
              len(v(_A(0.800794, None, st, "…"), DIV)) >= 1, True)

    # 25-26: nhận diện theo NỘI DUNG — báo cáo không có mục paper thì chân này không chạy
    import tempfile as _tf
    with _tf.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write("# báo cáo không có sổ paper\n\n| mã | % |\n|---|---|\n| FPT | +1,0% |\n")
        p_no = fh.name
    applied, f_ = paper_entry_gate(p_no, out=open(os.devnull, "w"))
    check("báo cáo KHÔNG có mục paper ⇒ chân paper không áp dụng, không chặn", (applied, f_),
          (False, []))
    os.unlink(p_no)

    # 27: coupling test THẬT với newdeals_daily_report.build_message() — thay ca cũ ("marker nhận
    # diện đúng 2 mục paper thật") vốn so PAPER_MARKERS với một bản copy cứng của CHÍNH NÓ (tautology,
    # không bao giờ fail được dù ai đổi tiêu đề thật). quant-skeptic vòng 3, Taylor_20260813_073404.
    # Stub 3 nguồn dữ liệu build_message() cần (sector_lens_monitor/alphalens_report/converge_report
    # — đều chạm BQ/cache thật) qua sys.modules; phần build header "## AlphaLens Paper Portfolio" /
    # "## DC Book Paper Portfolio" chạy CODE THẬT của newdeals_daily_report.py, không phải giả lập.
    import pandas as _pd
    import types as _types

    def _fake_compute_status():
        df = _pd.DataFrame([{"ticker": "FPT", "status": "BUY", "buy_mode": "ACCUMULATE"}])
        return {"df": df, "transitions": ["FPT BUY"], "prior": {}, "state": "BULL",
                "spread_yoy": 0.0, "feed_ok": True, "feed_asof": "2026-08-13"}

    _fake_slm = _types.ModuleType("sector_lens_monitor")
    _fake_slm.compute_status = _fake_compute_status
    _fake_slm.load_ratings = lambda: {"FPT": 1}
    _fake_slm.build_telegram_message = lambda *a, **k: "<b>sector stub</b>"
    _fake_alphalens = _types.ModuleType("alphalens_report")
    _fake_alphalens.generate_section = lambda as_of_date=None: "alphalens stub"
    _fake_converge = _types.ModuleType("converge_report")
    _fake_converge.generate_section = lambda as_of_date=None, live_set=None: "converge stub"

    _stub_names = ("sector_lens_monitor", "alphalens_report", "converge_report")
    _saved_mods = {n: sys.modules.get(n) for n in _stub_names}
    sys.modules["sector_lens_monitor"] = _fake_slm
    sys.modules["alphalens_report"] = _fake_alphalens
    sys.modules["converge_report"] = _fake_converge
    sys.path.insert(0, ROOT)
    sys.path.insert(0, os.path.join(ROOT, "mike", "bin"))
    try:
        import newdeals_daily_report as _ndr
        msg, changed = _ndr.build_message()
    finally:
        for n in _stub_names:
            if _saved_mods[n] is None:
                sys.modules.pop(n, None)
            else:
                sys.modules[n] = _saved_mods[n]

    check("coupling THẬT: build_message() nhánh có-thay-đổi → changed=True", changed, True)
    # all(), KHÔNG any(): production chỉ cần any() để KÍCH gate (đủ 1 marker khớp), nhưng
    # selfcheck phải bắt được CẢ HAI marker trôi độc lập — any() sẽ vẫn PASS nếu marker[0]
    # ("AlphaLens Paper Portfolio") còn đúng trong khi marker[1] đã trôi, y hệt lỗ hổng vừa vá
    # (reverse-proof đã chạy tay: any() không bắt được khi marker[1] bị đổi lại về giá trị cũ sai).
    check("coupling THẬT: CẢ HAI marker khớp heading thật (fail nếu bất kỳ heading nào trôi)",
          all(m in msg for m in PAPER_MARKERS), True)

    # 28: ngày KHÔNG có gì mới — đường chạy hàng ngày thật, trước bản vá này chưa có test nào phủ.
    # one-liner "vẫn giám sát bình thường" không được chứa marker paper nào (không kích T1/BQ oan),
    # và run_gate() trên đúng nội dung đó phải PASS (rc=0) vì nó không mang mục paper nào cả.
    quiet_msg = ("🆕 **NEW DEALS — 2026-08-13** — Không có deal mới / thay đổi thứ hạng đáng chú ý "
                 "trong AlphaLens, Golden/Strong Watchlist, DC Book hôm nay. Hệ thống vẫn giám "
                 "sát bình thường.")
    check("ngày không đổi gì: one-liner KHÔNG chứa marker paper nào",
          any(m in quiet_msg for m in PAPER_MARKERS), False)
    with tempfile.NamedTemporaryFile("w", suffix="_2026-08-13.md", delete=False,
                                      encoding="utf-8") as fh:
        fh.write(quiet_msg)
        p_quiet = fh.name
    rc_quiet = run_gate(p_quiet, out=open(os.devnull, "w"))
    os.unlink(p_quiet)
    check("ngày không đổi gì: run_gate() PASS (rc=0, không có tài khoản/mục paper nào để chặn)",
          rc_quiet, 0)

    # 29: nhánh CRASH của _check_return_gate() (import lỗi / run_gate() tự ném exception, ca
    # thật: gate chạm parquet cache đang ghi dở lúc overnight sync 06:00 ICT) — quant-skeptic
    # vòng 4, Taylor_20260813_075454. Trước bản vá này alert chỉ nằm bên trong
    # _check_return_gate() (nhánh `if rc != 0`), nên khi CHÍNH nó ném exception, main() bắt ở
    # `except Exception` và return 3 mà KHÔNG post gì — 1 ngày gate crash không phân biệt được
    # với 1 ngày yên ả. Stub sector_lens_monitor/alphalens_report/converge_report (build_message
    # cần) + report_return_gate.run_gate() ném lỗi + notify_thread.sh (subprocess.run) để bắt
    # đúng 1 lần gọi, đúng loại "crash" (không lẫn với "blocked").
    _fake_slm2 = _types.ModuleType("sector_lens_monitor")
    _fake_slm2.compute_status = _fake_compute_status
    _fake_slm2.load_ratings = lambda: {"FPT": 1}
    _fake_slm2.build_telegram_message = lambda *a, **k: "<b>sector stub</b>"
    _fake_alphalens2 = _types.ModuleType("alphalens_report")
    _fake_alphalens2.generate_section = lambda as_of_date=None: "alphalens stub"
    _fake_converge2 = _types.ModuleType("converge_report")
    _fake_converge2.generate_section = lambda as_of_date=None, live_set=None: "converge stub"

    class _CrashingGate:
        @staticmethod
        def run_gate(*a, **k):
            raise RuntimeError("parquet cache đang ghi dở (mô phỏng đúng overnight sync)")

    _saved_mods2 = {n: sys.modules.get(n) for n in _stub_names}
    _saved_rrg = sys.modules.get("report_return_gate")
    sys.modules["sector_lens_monitor"] = _fake_slm2
    sys.modules["alphalens_report"] = _fake_alphalens2
    sys.modules["converge_report"] = _fake_converge2
    sys.modules["report_return_gate"] = _CrashingGate
    notify_calls = []
    _saved_subprocess_run = _ndr.subprocess.run
    _ndr.subprocess.run = lambda cmd, **k: notify_calls.append(cmd)
    try:
        rc_crash = _ndr.main()
    finally:
        _ndr.subprocess.run = _saved_subprocess_run
        for n in _stub_names:
            if _saved_mods2[n] is None:
                sys.modules.pop(n, None)
            else:
                sys.modules[n] = _saved_mods2[n]
        if _saved_rrg is None:
            sys.modules.pop("report_return_gate", None)
        else:
            sys.modules["report_return_gate"] = _saved_rrg

    check("nhánh CRASH: main() trả về rc=3", rc_crash, 3)
    check("nhánh CRASH: đúng 1 alert được post", len(notify_calls), 1)
    crash_msg = notify_calls[0][1] if notify_calls else ""
    check("nhánh CRASH: nội dung alert đúng loại 'crash' (không lẫn 'blocked')",
          ("TỰ CRASH" in crash_msg) and ("BLOCKED by return gate" not in crash_msg), True)

    print(f"SELFCHECK: {'PASS' if ok else 'FAIL'} ({pass_count}/{len(ran)} ca)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", help="đường dẫn file .md báo cáo sắp gửi")
    ap.add_argument("--tolerance-pp", type=float, default=DEFAULT_TOL_PP)
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        return _selfcheck()
    if not a.report:
        ap.error("cần --report hoặc --selfcheck")
    return run_gate(a.report, a.tolerance_pp)


if __name__ == "__main__":
    sys.exit(main())
