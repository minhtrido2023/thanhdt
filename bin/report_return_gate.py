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

Đẳng thức kỳ vọng — CHUẨN TỈ SUẤT TỔNG (user chốt 2026-10-10: GIPS / tax-lot; §21). Mọi số
per-share ở CÙNG một hệ: cổ phiếu ĐANG GIỮ.

    cổ_tức_GỘP  = Σ sự kiện  tiền/cp_lúc_chốt_quyền ÷ F × φ
                  F = Π hệ số thưởng/cổ tức CP của mọi sự kiện có ex-date ≥ sự kiện đó
                  φ = phần KL đang giữ thật sự hưởng sự kiện đó (mua thêm SAU ex-date làm loãng)
    giá vốn THÔ = costPrice_broker + phần_broker_đã_trừ   (= cổ_tức_GỘP, trừ ca ghi ở dưới)
    lãi/lỗ RÒNG = qty×(giá − giá vốn THÔ) + (1 − thuế5%)×qty×cổ_tức_GỘP
    %           = lãi/lỗ RÒNG / (qty × giá vốn THÔ) × 100

  · Cổ tức TIỀN là THU NHẬP (tử số, sau thuế) — KHÔNG phải khoản giảm giá vốn. Broker thì trừ nó
    khỏi `costPrice`, nên phải CỘNG LẠI đúng phần broker đã trừ mới ra giá vốn thô.
  · Thưởng/cổ tức CP KHÔNG phải thu nhập: broker chia `costPrice` cho hệ số, TỔNG giá vốn giữ
    nguyên ⇒ không cộng lại gì, nhưng cổ tức tiền của các sự kiện TRƯỚC đó phải ÷ hệ số.
  · Broker trừ giá vốn tối ngày CUỐI CÒN QUYỀN, tức TRƯỚC ex-date một phiên. Báo cáo chốt đúng
    ngày đó: giá vốn đã bị trừ (phải cộng lại) nhưng giá còn nguyên quyền (CHƯA có thu nhập).

KHI NÀO CỔNG **KHÔNG CẤP KỲ VỌNG** (fail-closed — bản trước 2026-10-10 cấp bừa rồi PASS số sai):
`costPrice` của broker ĐÃ bị trừ cổ tức mà cổng không biết trừ bao nhiêu thì "costPrice + 0" là
một mẫu số quá nhỏ và tỉ suất bị THỔI LÊN (DRI 2026-10-09: +37,81% thay vì +34,58%). Nên một mã
bị gắn "không kỳ vọng" khi (i) nó có sự kiện tài khoản được hưởng mà chưa giải xong, hoặc (ii) sổ
giá vốn broker có một bước (`dar.classify_cost_steps`) không sự kiện đã giải nào khớp. Mã không
kỳ vọng mà báo cáo vẫn công bố tỉ suất ⇒ CHẶN.

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
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dividend_adjusted_return as dar  # noqa: E402
import wc_paths  # noqa: E402


ROOT = wc_paths.find_wc_root(__file__)
EXEC_DIR = os.path.join(ROOT, "data", "execution_logs")
LOOKBACK_DAYS = 120          # SÀN của cửa sổ tra sự kiện — xem `_lookback_start`
PRE_EX_DAYS = 10             # broker trừ giá vốn trước ex-date tối đa bấy nhiêu ngày lịch
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

# Content-completeness gate (thêm 2026-09-02, sau vụ báo cáo tháng 08 — template tạo 25/08 với
# 5/10 mục còn "[TBD" bị report_delivery_gate coi là hoàn tất và GIAO THẬT cho user 28/08, TRƯỚC
# CẢ KHI tháng đóng). report_return_gate PASS trong rỗng vì các mục TBD không có dòng bảng/văn
# xuôi nào để kiểm — cổng tỉ suất không phải cổng "báo cáo đã điền đủ". Marker khớp NGUYÊN VĂN
# quy ước đang dùng trong reports/*.md (`[TBD`, `[chưa điền`, `[placeholder`) — mở rộng danh sách
# này nếu thấy quy ước khác được dùng, đừng đoán.
INCOMPLETE_MARKERS = ("[TBD", "[chưa điền", "[chua dien", "[placeholder")


def find_incomplete_markers(report_path: str) -> list:
    """[(dòng, nội dung)] cho mọi chỗ báo cáo còn nội dung CHƯA ĐIỀN."""
    hits = []
    with open(report_path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if any(m in line for m in INCOMPLETE_MARKERS):
                hits.append((i, line.strip()))
    return hits


# ---------------------------------------------------------------- nguồn (1): broker
def broker_positions(account_no: str, asof: str, price_fn=None) -> dict:
    """{mã: (qty, costPrice bình quân gia quyền GỘP lô, giá đóng cửa BQ)} — khối lượng và giá
    vốn từ bản ghi `positions` CUỐI CÙNG của ngày `asof`; GIÁ từ BQ, không từ `marketPrice`.

    §12: lọc `account_no` TRƯỚC mọi phép tính — file dnse_raw dùng chung mọi tài khoản.

    Gộp NHIỀU LÔ cùng mã (khác `loanPackageId`, vd margin thường + gói CAPIT riêng) — phát hiện
    2026-09-02 khi dựng báo cáo tháng 08: bản trước GHI ĐÈ theo mã (dict[symbol] = lô cuối cùng
    trong mảng `positions`), lặng lẽ BỎ mất lô đứng trước — ca thật ZaloPay 08-31: BID
    107cp(loanPkg 1826)+320cp(1258) → gate chỉ thấy 320cp; MBB 400+252 → chỉ thấy 252cp; VCB
    200+100 → chỉ thấy 100cp. Không phải test giả định — 3/30 mã ZaloPay bị cắt ngay lần dùng
    thật đầu tiên.
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
    agg = {}   # symbol -> [tổng qty, tổng cost_value]
    for p in last["payload"].get("positions", []):
        if str(p.get("accountNo")) != str(account_no):
            continue
        qty = float(p.get("openQuantity") or 0)
        if qty <= 0:
            continue
        cp = float(p.get("costPrice") or 0)
        a = agg.setdefault(p["symbol"], [0.0, 0.0])
        a[0] += qty
        a[1] += qty * cp
    if not agg:
        return {}

    # GIÁ THỊ TRƯỜNG KHÔNG lấy từ `positions[].marketPrice` nữa (sửa 2026-09-09).
    # Hai lý do độc lập, cái nào cũng đủ:
    #   1. Bản cũ `agg.setdefault(sym, [0, 0, mp])` khiến giá của lô ĐẦU TIÊN trong mảng
    #      thắng im lặng, rồi giá đó được áp cho TỔNG khối lượng ở expected_pct(). Các lô
    #      cùng mã KHÔNG phải lúc nào cũng cùng giá: đo thật trên dnse_raw 08→09 có 5 bản
    #      đọc mà 2 lô cùng mã lệch nhau (ZaloPay 2026-08-14T19:10:23 BID 35.800 vs 38.850
    #      — lệch 8,5%), do replica đọc-sau-ghi của DNSE trả dòng cũ trong lúc batch
    #      reprice EOD đang chạy. Comment cũ ở đây khẳng định "giống nhau mọi lô cùng mã",
    #      điều đã bị chính dữ liệu bác bỏ.
    #   2. Kể cả khi mọi lô đồng giá, `marketPrice` VỐN không phải giá đóng cửa ATC —
    #      `verify_account_snapshot.dnse_close_prices()` đã ghi rõ "không dùng" từ ca
    #      2026-07-06. Cổng này công bố TỈ SUẤT cho nhà đầu tư nên phải dùng giá đóng cửa.
    # Giá từ BQ (KHÔNG phải `dnse_close_prices`): `asof` ở đây là ngày LỊCH SỬ, mà bản DNSE chỉ
    # trả giá phiên hiện tại. BQ vốn đã là phụ thuộc cứng của cổng này (`dar.resolve_dividends`
    # query `tav2_bq.corporate_action`) nên không thêm kiểu lỗi mới.
    # `price_fn` chỉ để selfcheck chạy offline — production luôn dùng mặc định `raw_close_prices`
    # (thay `verify_account_snapshot.bq_close_prices` từ 2026-10-10 — xem docstring hàm đó).
    if price_fn is None:
        price_fn = raw_close_prices
    prices = price_fn(sorted(agg), asof)

    out = {}
    for sym, (qty, cost_value) in agg.items():
        px = prices.get(sym)
        if not px:
            # Fail-closed: thiếu giá 1 mã ⇒ chặn cả lượt, KHÔNG đoán và KHÔNG lặng lẽ bỏ mã
            # (bỏ mã sẽ làm tỉ suất TỔNG công bố cho nhà đầu tư thiếu đúng mã đó).
            raise ValueError(f"thiếu giá đóng cửa {sym} ngày {asof} — CHẶN (fail-closed)")
        out[sym] = (qty, cost_value / qty, float(px))
    return out


def _today_ict() -> str:
    """Hôm nay theo giờ ICT (§16 — không đọc TZ của process)."""
    from zoneinfo import ZoneInfo
    return _dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()


def pick_raw_price(close: float, price: float, later_events: bool) -> tuple:
    """PURE — (giá THÔ của phiên, tên cột đã dùng).

    `tav2_bq.ticker.Close` được viết lại HỒI TỐ sau mỗi ex-date. Cổng này làm việc trên giá vốn
    THÔ, nên `Close` chỉ dùng được khi CHƯA có sự kiện nào sau phiên đó; đã có thì `Close` của
    phiên đó thấp hơn giá khớp thật đúng bằng phần điều chỉnh — lấy nó trừ giá vốn thô là phạt cổ
    tức HAI LẦN (lỗi số 2 trong docstring `dividend_adjusted_return.py`). Đo 2026-10-10: TV1
    phiên 06/10 `Price` 20.600 nhưng `Close` 19.110 (đã trừ cổ tức 1.500đ ex 07/10); bản cũ của
    cổng (`bq_close_prices` — cột `Close`) chạy lại cho một báo cáo chốt 06/10 sẽ ra tỉ suất
    thấp hơn thật ~7 điểm %. Chạy ĐÚNG NGÀY thì hai cột trùng nhau nên lỗi chỉ lộ khi cổng chạy
    lại sau (rescue/gửi lại báo cáo cũ — đúng việc `report_delivery_gate` làm).

    Không có sự kiện sau ⇒ giữ `Close` (giá khớp cuối; trên UPCOM `Price` là giá BÌNH QUÂN và có
    thể lệch 1 bước giá — DRI 08/10: `Price` 16.600, `Close` 16.700).
    """
    return (price, "Price") if later_events else (close, "Close")


def raw_close_prices(tickers, asof: str) -> dict:
    """{mã: giá THÔ phiên mới nhất ≤ asof}. Fail-closed: không tra được ⇒ ValueError (CHẶN)."""
    inlist = ",".join(f"'{t}'" for t in sorted(set(tickers)))
    try:
        rows = dar._bq(f"""
            SELECT t.ticker AS tk, t.Close AS close, t.Price AS price,
                   CAST(t.time AS STRING) AS d
            FROM `{dar.BQ_PROJECT}.tav2_bq.ticker` AS t
            WHERE t.ticker IN ({inlist})
              AND t.time BETWEEN DATE_SUB(DATE '{asof}', INTERVAL 30 DAY) AND DATE '{asof}'
              AND t.Price > 0 AND t.Close > 0
            QUALIFY ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) = 1
        """)
        today = _today_ict()
        # kể cả `announced`: vendor chỉ đổi sang `executed` ~22:2x của CHÍNH ex-date, trong
        # khi `Close` có thể đã được viết lại trước đó — nghi thì dùng `Price` (thô).
        later = (dar.bq_corp_events_window(tickers, asof, today, include_announced=True)
                 if asof < today else {})
    except Exception as e:                                          # noqa: BLE001
        raise ValueError(f"không lấy được giá thô {asof} từ BQ: {str(e)[:300]} — CHẶN") from e
    later_tk = {tk for (tk, _ex) in later}
    newest = max((str(r["d"])[:10] for r in rows), default=None)
    out, used_price, lagging = {}, [], {}
    for r in rows:
        px, col = pick_raw_price(float(r["close"]), float(r["price"]), r["tk"] in later_tk)
        out[r["tk"]] = px
        if col == "Price":
            used_price.append(f"{r['tk']} {px:,.0f} (Close {float(r['close']):,.0f})")
        if str(r["d"])[:10] != newest:
            lagging[r["tk"]] = str(r["d"])[:10]
    if used_price:
        print(f"ℹ️  giá {asof}: dùng cột `Price` (thô) thay `Close` cho mã có sự kiện ex-date SAU "
              f"{asof} — `Close` của phiên đó đã bị điều chỉnh hồi tố: {', '.join(sorted(used_price))}",
              file=sys.stderr)
    if lagging:
        print(f"⚠️ BQ: các mã có phiên giá cũ hơn {newest} (dùng giá phiên gần nhất của CHÍNH mã "
              f"đó — kiểm tra ngừng giao dịch/thiếu dòng): {lagging}", file=sys.stderr)
    return out


# ---------------------------------------------------------------- nguồn (2): cổ tức
def _lookback_start(asof: str) -> str:
    """Ngày bắt đầu tra sự kiện = sớm hơn trong (asof − LOOKBACK_DAYS, ngày đầu của sổ dnse_raw).

    Bản cũ chỉ lùi 120 ngày cố định với lý do "đủ phủ mọi ex-date còn nằm trong giá vốn" — SAI
    theo thời gian: cổ tức MBB 09/07 nằm trong giá vốn broker VĨNH VIỄN, nhưng từ 2026-11-06 nó
    rơi khỏi cửa sổ, cổng thôi cộng lại 1.000đ và kỳ vọng tự thổi lên (NCT 8.000đ: từ 24/11; SAB
    3.000đ: từ 25/11). Sổ broker là giới hạn bằng chứng thật, nên cửa sổ phải phủ hết nó.
    """
    floor = (_dt.date.fromisoformat(asof) - _dt.timedelta(days=LOOKBACK_DAYS)).isoformat()
    try:
        days = sorted(f[len("dnse_raw_"):-len(".jsonl")] for f in os.listdir(EXEC_DIR)
                      if f.startswith("dnse_raw_") and f.endswith(".jsonl"))
    except OSError:
        days = []
    return min(floor, days[0]) if days else floor


def _holding(series: list, asof: str) -> tuple:
    """(bản ghi của ĐỢT NẮM GIỮ HIỆN TẠI tới hết `asof`, các bước giá vốn của đợt đó).

    Đợt hiện tại bắt đầu sau lần cuối KL về 0: bán hết rồi mua lại là một vị thế MỚI — giá vốn
    reset, cổ tức của đợt cũ không thuộc về nó (cùng họ với ca LPB 2026-08-07).
    """
    cut = [r for r in series if r[0][:10] <= asof]
    last0 = max((i for i, r in enumerate(cut) if r[1] <= 0), default=-1)
    cur = cut[last0 + 1:]
    return cur, dar.classify_cost_steps(cur)


def _observe(cur: list, steps: list, claimed: set, a) -> dict:
    """Sổ giá vốn broker nói gì trong cửa sổ [ngày cuối còn quyền, ex-date] của sự kiện `a`.

    `kind`: "cash" | "stock" | "cash+stock" (thấy bước — kèm `cash`, `mult`, `ts`)
            "none"   — có bản ghi TRƯỚC ngày cuối còn quyền và TỪ ex-date trở đi, không lệnh khớp
                       che, và giá vốn KHÔNG đổi ⇒ broker xác nhận không đụng tới vị thế này
            "hidden" — không quan sát được (thiếu bản ghi bao hai đầu, hoặc có lệnh mua/bước lạ
                       rơi cùng cửa sổ che mất) ⇒ KHÔNG kết luận gì từ sổ
    Bước đã được một sự kiện khác nhận (`claimed`) thì không tính lại.
    """
    win = [(i, st) for i, st in enumerate(steps)
           if a.last_cum_date <= st["ts"][:10] <= a.ex_date and i not in claimed]
    corp = [(i, st) for i, st in win if st["kind"] in ("cash", "stock", "cash+stock")]
    if corp:
        claimed.update(i for i, _ in corp)
        cash = sum(st["cash"] for _, st in corp)
        mult = 1.0
        for _, st in corp:
            mult *= st["mult"]
        kind = "cash+stock" if cash > 0 and mult > 1.0 else ("cash" if cash > 0 else "stock")
        return {"kind": kind, "cash": cash, "mult": mult, "ts": corp[0][1]["ts"],
                "q0": corp[0][1]["q0"], "q1": corp[-1][1]["q1"]}
    covered = (any(r[0][:10] < a.last_cum_date for r in cur)
               and any(r[0][:10] >= a.ex_date for r in cur))
    if not covered or any(st["kind"] in ("buy", "other") for _, st in win):
        return {"kind": "hidden"}
    return {"kind": "none"}


def _dilution(steps: list, after_ts: str) -> float:
    """φ — phần KL ĐANG GIỮ là hậu duệ của cổ phiếu đã hưởng một sự kiện xảy ra ở `after_ts`.

    Giá vốn broker là BÌNH QUÂN GIA QUYỀN: bán thì cổ tức đã nhận ra đi theo tỉ lệ (φ không
    đổi), thưởng thì cả hai cùng nhân hệ số (φ không đổi), chỉ MUA THÊM mới pha loãng:
    φ ×= KL_trước / KL_sau. Cộng nguyên cổ tức/cp cho cả phần mua sau ex-date là trao thu nhập
    cho cổ phiếu chưa từng nhận nó.
    """
    phi = 1.0
    for st in steps:
        if st["ts"] > after_ts and st["kind"] == "buy" and st["q1"] > 0:
            phi *= st["q0"] / st["q1"]
    return phi


def _pre_ex_event(ticker: str, step: dict, asof: str):
    """Bước trừ giá vốn CHƯA có ex-date ≤ asof nào nhận: có phải cổ tức sẽ chốt quyền ngay sau
    `asof` không? Trả (ex-date, đồng/cp) khi vendor (kể cả `announced` — ngày ex chưa tới thì
    vendor chưa đổi sang `executed`) khai ĐÚNG số tiền broker vừa trừ; None nếu không. Hai nguồn
    độc lập phải khớp tới đồng mới nhận — không khớp là không biết, và không biết là CHẶN."""
    end = (_dt.date.fromisoformat(asof) + _dt.timedelta(days=PRE_EX_DAYS)).isoformat()
    vend = dar.bq_corp_events_window([ticker], asof, end, include_announced=True)
    for (_tk, ex), row in sorted(vend.items()):
        cash = float(row.get("cash") or 0.0)
        if cash > 0 and float(row.get("stock_free") or 0.0) <= 0 \
                and abs(cash - step["cash"]) <= 1.0:
            return ex, cash
    return None


def entitled_gross(tickers, account_no: str, asof: str) -> tuple:
    """({mã: cổ tức GỘP đồng/cp TRÊN KL ĐANG GIỮ, ex-date ≤ asof}, [lệch nguồn vendor], extra).

    Phần tử thứ hai là danh sách sự kiện mà (a) TIỀN BROKER THẬT và nguồn vendor
    `tav2_bq.corporate_action` cho hai số KHÁC nhau quá ngưỡng (`reason` = cash_mismatch /
    stock_leg_ignored / unknown), HOẶC (b) BQ lỗi hạ tầng nên KHÔNG tra được vendor cho sự kiện đó
    (`reason` = "lookup_failed", arch-review 2026-09-24 R1) — `dar` đã hạ cả hai loại về
    `UNVERIFIED` (cash_per_share = 0) nên nếu chỉ trả về `out` thì mã đó lặng lẽ mất phần cổ tức
    khỏi kỳ vọng mà KHÔNG ai biết. Trả kèm ra ngoài để cổng nói thành lời, không suy diễn từ sự
    vắng mặt (§28).

    Mỗi phần tử là 7-tuple `(ticker, ex_date, per_share, vendor_cash, reason, vendor_stock,
    had_broker_cash)`. `had_broker_cash` (arch-review vòng 5, R1-A/R1-B) phân biệt "per_share LÀ
    tiền broker thật" (nhánh mismatch LUÔN True — chỉ chạy trong `kind == CASH_CONFIRMED`; nhánh
    lookup_failed đọc `a.lookup_failed_had_broker_cash`) khỏi "per_share chỉ là ƯỚC LƯỢNG tỉ số,
    chưa từng là tiền broker" — quyết định CẢ câu chẩn đoán (§29) LẪN phạm vi CHẶN (§R1-B: chỉ
    chặn khi lookup_failed thật sự làm MẤT một số đã từng công bố).

    `extra` (thêm 2026-10-10) — những gì cổng cần để KHÔNG cấp một kỳ vọng sai:
      "blockers" {mã: [lý do]} — KHÔNG dựng được giá vốn thô của mã này (xem docstring đầu file);
      "addback"  {mã: đồng/cp} — phần broker ĐÃ trừ khỏi `costPrice`, CHỈ khi khác cổ tức thu
                 nhập (broker trừ trước ex-date; hoặc broker không trừ);
      "notes"    [str] — bằng chứng đã dùng (hệ số KL, pha loãng, sự kiện được sổ broker gỡ).
    Trọng tài cuối cùng của "giá vốn tài khoản này có bị đụng tới không" là SỔ GIÁ VỐN CỦA CHÍNH
    BROKER (`dar.broker_cost_series`) — per-mã, per-tài-khoản; tỉ số giá và bảng vendor đều
    không biết tài khoản nào hưởng gì.
    """
    start = _lookback_start(asof)
    adjs = dar.resolve_dividends(sorted(tickers), start, asof)
    qmap = dar.broker_qty(account_no)
    series = dar.broker_cost_series(account_no)
    out, mismatches = {}, []
    blockers, addback, notes = {}, {}, [f"resolve_dividends: {w}"
                                        for w in getattr(adjs, "warnings", ())]
    hold = {tk: _holding(series.get(tk, []), asof) for tk in tickers}
    claimed = {tk: set() for tk in tickers}
    deducted = {}                       # mã -> phần broker đã trừ (đồng/cp trên KL đang giữ)

    def block(tk, why):
        blockers.setdefault(tk, []).append(why)

    # Sự kiện ĐÃ GIẢI nhận bước giá vốn trước; sự kiện chưa giải chỉ thấy phần còn lại — một cú
    # nhảy tỉ số chưa rõ nằm sát một cổ tức thật không được "cướp" bước trừ của cổ tức đó.
    for a in sorted(adjs, key=lambda x: (not getattr(x, "resolved", False), x.ex_date)):
        if a.ex_date > asof:
            continue
        if getattr(a, "kind", "") == "RATIO_NOISE":
            continue                           # đã chứng minh KHÔNG phải sự kiện
        if dar._qty_at(qmap, a) <= 0:          # tài khoản này KHÔNG nắm giữ tại ngày chốt quyền
            continue
        tk = a.ticker
        cur, steps = hold.get(tk, ([], []))
        if cur and a.ex_date < cur[0][0][:10]:
            continue                           # thuộc một đợt nắm giữ ĐÃ ĐÓNG — không phải vị thế này
        obs = _observe(cur, steps, claimed.setdefault(tk, set()), a)
        if a.vendor_check == "mismatch":
            # Mã lý do đi kèm để tầng ngoài nói ĐÚNG nguyên nhân: "hai nguồn lệch SỐ" và "vendor
            # khai thuần cổ phiếu mà solver giải ra tiền" dẫn tới hai việc điều tra KHÁC nhau,
            # và ở ca thứ hai `vendor_cash = 0` nên nếu chỉ in hai con số thì người đọc hiểu là
            # "vendor không có dữ liệu" — trái hẳn sự thật (§29).
            # Fail-closed về "unknown" khi thiếu/rỗng — KHÔNG đoán "cash_mismatch" (arch-review D1b,
            # R2). `dar` LUÔN set field này ở cả hai nhánh dựng `mismatch` nên đường này không nên
            # tới trong sản xuất bình thường; nhưng nếu một `Adjustment` nào đó (caller cũ/hỏng)
            # không set, đoán mò tên lý do sẽ dẫn Winston điều tra sai hướng ngay dòng đầu — đúng
            # lớp lỗi §29 mà chính sách vendor-mismatch này sinh ra để chặn.
            # `had_broker_cash=True` cố định: nhánh này CHỈ chạy bên trong `if adj.kind ==
            # "CASH_CONFIRMED"` ở dividend_adjusted_return.py (xem docstring hàm này) — `per_share`
            # LUÔN là tiền broker thật ở đây, không phải ước lượng.
            mismatches.append((a.ticker, a.ex_date, a.per_share, a.vendor_cash,
                               getattr(a, "vendor_mismatch_reason", "") or "unknown",
                               a.vendor_stock, True))
            block(tk, f"sự kiện ex {a.ex_date}: tiền broker và vendor LỆCH nhau "
                      f"({a.per_share:,.0f} vs {a.vendor_cash:,.0f}đ/cp) — chưa biết broker đã trừ "
                      f"bao nhiêu khỏi giá vốn")
            continue
        if a.vendor_check == "lookup_failed":
            # BQ lỗi hạ tầng KHÔNG tra được vendor cho sự kiện NÀY (arch-review 2026-09-24, R1) —
            # KHÁC `unavailable` (vendor XÁC NHẬN 0 dòng). `dar` đã hạ `kind` về UNVERIFIED khi sự
            # kiện từng CASH_CONFIRMED nên `cash_per_share` = 0 ở đây; nếu chỉ rơi xuống nhánh
            # `continue` dưới như trước bản vá này thì cổ tức lặng lẽ biến mất khỏi kỳ vọng mà
            # KHÔNG ai nói ra — dùng lại đúng cơ chế "báo tầng ngoài" của nhánh mismatch, reason
            # cố định "lookup_failed" (không đọc `vendor_mismatch_reason` — trường đó chỉ có ý
            # nghĩa cho nhánh mismatch).
            # `had_broker_cash` = provenance THẬT của `dar` (R1-A) — KHÔNG cố định True/False ở
            # đây: sự kiện có thể chưa bao giờ là CASH_CONFIRMED (per_share chỉ là ước lượng tỉ
            # số), auto-gán True sẽ tái tạo đúng lớp lỗi mà field này sinh ra để chặn.
            mismatches.append((a.ticker, a.ex_date, a.per_share, 0.0, "lookup_failed", 0.0,
                               a.lookup_failed_had_broker_cash))
            # Sổ broker gỡ được ca "chỉ là ước lượng tỉ số" (56/62 sự kiện K1, phần lớn là nhiễu):
            # giá vốn KHÔNG đổi quanh ngày đó ⇒ với tài khoản này nó không phải sự kiện.
            if obs["kind"] != "none":
                block(tk, f"sự kiện ex {a.ex_date}: KHÔNG tra được vendor (BQ lỗi) — "
                          + _obs_text(obs))
            continue
        if not getattr(a, "resolved", a.cash_per_share > 0):
            if obs["kind"] == "none":
                notes.append(f"{tk} ex {a.ex_date} [{a.kind}] CHƯA giải nhưng sổ giá vốn broker "
                             f"KHÔNG đổi trong [{a.last_cum_date}, {a.ex_date}] ⇒ không đụng tới "
                             f"vị thế này, không tính")
                continue
            block(tk, f"sự kiện ex {a.ex_date} [{a.kind}] CHƯA giải ({(a.note or '—')[:140]}) — "
                      + _obs_text(obs))
            continue

        # ---- sự kiện ĐÃ GIẢI: đối chiếu với bước giá vốn broker (khi quan sát được)
        want_cash = a.cash_per_share
        want_mult = float(getattr(a, "share_multiplier", 1.0) or 1.0)
        if obs["kind"] in ("cash", "stock", "cash+stock"):
            bad_cash = abs(obs["cash"] - want_cash) > 1.0
            bad_mult = abs(obs["q1"] - obs["q0"] * want_mult) > 1.5
            if bad_cash or bad_mult:
                block(tk, f"sự kiện ex {a.ex_date} đã giải là {want_cash:,.0f}đ/cp ×{want_mult:.4f} "
                          f"nhưng " + _obs_text(obs))
                continue
        if want_cash <= 0:
            continue                           # thưởng/quyền thuần: không thu nhập, không cộng lại
        after = obs["ts"] if "ts" in obs else a.last_cum_date + "T99"
        phi = _dilution(steps, after)
        g = a.cash_per_share_now * phi
        out[tk] = out.get(tk, 0.0) + g
        if obs["kind"] == "none":
            notes.append(f"{tk} ex {a.ex_date}: cổ tức {want_cash:,.0f}đ/cp đã giải nhưng broker "
                         f"KHÔNG trừ giá vốn trong [{a.last_cum_date}, {a.ex_date}] ⇒ thu nhập có, "
                         f"cộng-lại-giá-vốn KHÔNG")
        else:
            deducted[tk] = deducted.get(tk, 0.0) + g
        if abs(a.frame_factor - 1.0) > 1e-9 or abs(phi - 1.0) > 1e-9:
            notes.append(f"{tk} ex {a.ex_date}: {want_cash:,.0f}đ/cp lúc chốt quyền ÷ hệ số KL "
                         f"{a.frame_factor:.4f} × phần hưởng {phi:.4f} = {g:,.2f}đ/cp trên KL "
                         f"đang giữ")

    # ---- bước giá vốn KHÔNG sự kiện (ex-date ≤ asof) nào nhận
    for tk in tickers:
        cur, steps = hold.get(tk, ([], []))
        for i, st in enumerate(steps):
            if i in claimed.get(tk, set()) or st["kind"] not in ("cash", "stock", "cash+stock"):
                continue
            pre = None
            if st["kind"] == "cash":
                try:
                    pre = _pre_ex_event(tk, st, asof)
                except Exception as e:                              # noqa: BLE001
                    block(tk, f"{_step_text(st)} — không sự kiện đã giải nào khớp, và KHÔNG tra "
                              f"được vendor để xem có phải cổ tức sắp chốt quyền ({str(e)[:120]})")
                    continue
            if pre is None:
                block(tk, f"{_step_text(st)} — KHÔNG có sự kiện đã giải nào khớp")
                continue
            g = st["cash"] * _dilution(steps, st["ts"])
            deducted[tk] = deducted.get(tk, 0.0) + g
            notes.append(f"{tk}: broker đã trừ {st['cash']:,.0f}đ/cp khỏi giá vốn lúc {st['ts']} "
                         f"cho cổ tức ex {pre[0]} (vendor khai {pre[1]:,.0f}đ/cp) — ex-date SAU "
                         f"{asof} ⇒ cộng lại giá vốn, CHƯA tính thu nhập (giá còn nguyên quyền)")

    for tk in set(out) | set(deducted):
        if abs(deducted.get(tk, 0.0) - out.get(tk, 0.0)) > 1e-6:
            addback[tk] = deducted.get(tk, 0.0)
    return out, mismatches, {"blockers": blockers, "addback": addback, "notes": notes}


def _step_text(st: dict) -> str:
    if st["kind"] == "cash":
        return (f"sổ broker lúc {st['ts']}: KL giữ nguyên {st['q0']:,.0f}, giá vốn/cp bị TRỪ "
                f"{st['cash']:,.2f}đ")
    if st["kind"] == "stock":
        return (f"sổ broker lúc {st['ts']}: KL {st['q0']:,.0f}→{st['q1']:,.0f} "
                f"(×{st['mult']:.4f}), tổng giá vốn giữ nguyên")
    return (f"sổ broker lúc {st['ts']}: KL {st['q0']:,.0f}→{st['q1']:,.0f} (×{st['mult']:.4f}) và "
            f"tổng giá vốn GIẢM {st['cash']:,.2f}đ trên mỗi cp cũ")


def _obs_text(obs: dict) -> str:
    if obs["kind"] == "hidden":
        return ("sổ giá vốn broker KHÔNG quan sát được quanh ngày đó (thiếu bản ghi bao hai đầu "
                "hoặc có lệnh khớp che) nên không loại trừ được việc giá vốn đã bị trừ")
    if obs["kind"] == "none":
        return "sổ giá vốn broker KHÔNG đổi quanh ngày đó"
    return _step_text({**obs, "kind": obs["kind"]})


def expected_pct(qty: float, cost_price: float, market: float, gross_ps: float,
                 tax: float = dar.PIT_DIVIDEND_RATE, addback_ps: float = None) -> tuple:
    """(%, lãi/lỗ ròng VND, giá vốn thô/cp) — xem đẳng thức ở docstring đầu file.

    `gross_ps` = cổ tức THU NHẬP (đồng/cp trên KL đang giữ); `addback_ps` = phần broker đã trừ
    khỏi `cost_price`. Bỏ trống ⇒ bằng nhau (ca thường). Khác nhau khi broker trừ giá vốn TRƯỚC
    ex-date: giá vốn phải cộng lại nhưng thu nhập chưa có.
    """
    if addback_ps is None:
        addback_ps = gross_ps
    raw_cost = cost_price + addback_ps
    pl_net = qty * (market - raw_cost) + (1.0 - tax) * qty * gross_ps
    return pl_net / (qty * raw_cost) * 100.0, pl_net, raw_cost


# ---------------------------------------------------------------- báo cáo
# Mã chứng khoán VN = 3 ký tự, ký tự 2-3 có thể là SỐ (TV1, PC1, VC3, L18). Bản cũ `[A-Z]{3}`
# làm dòng TV1 của CẢ HAI báo cáo tuần 05→09/10 không bao giờ được đọc: không kiểm, không đếm,
# rồi cổng in "TV1 CÓ cổ tức nhưng báo cáo không công bố tỉ suất riêng" — sai sự thật.
_TK = r"[A-Z][A-Z0-9]{2}"
ROW_RE = re.compile(r"^\|\s*(?:\*\*)?(" + _TK + r")(?:\*\*)?\s*\|(.+)\|\s*$")
SEP_RE = re.compile(r"^\|[\s:|-]+\|\s*$")
# Văn xuôi: CHỈ bắt "MÃ +12,3%" / "MÃ −4,5%" — bắt buộc có DẤU và đứng liền mã, nên
# "DGC 46,5% NAV" (tỷ trọng, không dấu) không bị nhận nhầm là tỉ suất.
PROSE_RE = re.compile(r"\b(" + _TK + r")\s*\*{0,2}\s*([+\-−]\d+(?:[.,]\d+)?)\s*%")
# Cột % nào là TỈ SUẤT lãi/lỗ (được kiểm) — cột nào là tỷ trọng (bỏ qua).
PCT_HEADER_OK = ("lãi", "lỗ", "lai/lo", "tỉ suất", "tỷ suất", "ti suat", "ty suat", "return", "p&l")
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
    """(chỉ số cột KL, chỉ số cột % TỈ SUẤT, [cột ứng viên nhận THEO Ô]) — cột % là None nếu
    tiêu đề không cột nào vừa mang `%` vừa mang tên tỉ suất.

    Chọn theo TIÊU ĐỀ, không theo vị trí: bảng Mục 5.3 có 2 cột `%` nhưng cả hai là **tỷ trọng
    NAV**, không phải tỉ suất — lấy "ô % cuối dòng" sẽ kiểm nhầm tỷ trọng vào tỉ suất.

    Tiêu đề KHÔNG mang dấu `%` nhưng mang tên tỉ suất (`Lãi/lỗ`, `Tỷ suất`) ⇒ là ỨNG VIÊN
    "theo ô" (phần tử thứ ba): mỗi dòng lấy ứng viên ĐẦU TIÊN mà chính Ô đó có `%`, vì cùng tên
    ấy cũng được dùng cho cột số tiền (`| Tỷ suất | Lãi (VND) |`). Đo thật: bảng vị thế của MỌI báo cáo tuần 31/08→02/10/2026 có
    tiêu đề `| Mã | KL | Giá vốn | Giá … | Giá trị thị trường | % NAV | Lãi/lỗ |` với ô
    `+32,11%` — bản cũ đòi `%` trong tiêu đề nên bỏ cả bảng và PASS trên 0 dòng.
    """
    qty_i = pct_i = None
    cands = []
    for i, h in enumerate(header_cells):
        low = h.strip().lower().replace("*", "")
        if qty_i is None and (low in ("kl", "qty") or "khối lượng" in low or "khoi luong" in low):
            qty_i = i
        if any(bad in low for bad in PCT_HEADER_NO):
            continue
        named = any(ok in low for ok in PCT_HEADER_OK)
        if "%" not in low:
            if named:
                cands.append(i)
            continue
        if low == "%" or named:
            pct_i = i
    return qty_i, pct_i, ([] if pct_i is not None else cands)


SIGNED_PCT_CELL_RE = re.compile(r"^\s*(?:\*\*)?[+\-−]\d+(?:[.,]\d+)?\s*%(?:\*\*)?\s*$")


def _strip_quote(line: str) -> str:
    """Bóc mọi dấu blockquote `>` đầu dòng (`> | … |` ⇒ `| … |`) rồi trả phần đã lstrip.

    Markdown cho phép lồng (`>> `); bóc lặp để một bảng trong blockquote vẫn được nhận là BẢNG,
    không phải văn xuôi."""
    s = line.lstrip()
    while s.startswith(">"):
        s = s[1:].lstrip()
    return s


def _scan_tables(path: str) -> tuple:
    """(dòng tỉ suất đã nhận, dòng CÓ tỉ suất mà cổng không nhận ra cột) của mọi bảng có cột KL."""
    with open(path, encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]
    rows, blind = [], []
    qty_i = pct_i = None
    cands, header = [], []
    for i, line in enumerate(lines):
        if line.startswith("|") and i + 1 < len(lines) and SEP_RE.match(lines[i + 1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            qty_i, pct_i, cands = _pick_columns(header)
            continue
        if not line.startswith("|"):
            qty_i = pct_i = None
            continue
        if qty_i is None:
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        col = pct_i
        if col is None:
            col = next((j for j in cands if j < len(cells) and "%" in cells[j]), None)
        if col is None:
            # bảng VỊ THẾ (có cột KL) mà không cột nào được nhận là tỉ suất — kể cả khi mọi cột
            # ứng viên "theo ô" hoá ra là cột SỐ TIỀN: một ô "+12,3%" có DẤU nằm ở cột không
            # thuộc nhóm tỷ trọng ⇒ có tỉ suất đang được công bố ngoài tầm cổng
            for j, c in enumerate(cells):
                h = header[j] if j < len(header) else ""
                if SIGNED_PCT_CELL_RE.match(c) and not any(
                        bad in h.lower() for bad in PCT_HEADER_NO):
                    blind.append((i + 1, m.group(1), h, c))
            continue
        if max(qty_i, col) >= len(cells):
            continue
        qty, pct = _num(cells[qty_i]), _num(cells[col])
        if qty is None or pct is None:
            continue
        rows.append((m.group(1), qty, pct))
    return rows, blind


def parse_report_rows(path: str) -> list:
    """[(ticker, qty, pct)] — chỉ lấy từ bảng có cột KL **và** cột % là tỉ suất lãi/lỗ."""
    return _scan_tables(path)[0]


def unrecognized_return_cells(path: str) -> list:
    """[(số dòng, mã, tiêu đề cột, ô)] — ô tỉ suất CÓ DẤU trong bảng vị thế (có cột KL) mà
    `_pick_columns` không nhận cột nào là tỉ suất. `run_gate` CHẶN: không kiểm được thì không
    được PASS (bảng bị bỏ im lặng = đúng cách cổng đã PASS trên 0 dòng)."""
    return _scan_tables(path)[1]


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
    """Mã ngoài phạm vi bot (vị thế legacy). Đọc từ config, KHÔNG hardcode (§7).

    Hệ quả ở `run_gate` (sửa 2026-10-10): mã excluded đứng NGOÀI tổng kỳ vọng của tài khoản và
    `MÃ ±x%` của nó trong VĂN XUÔI không được kiểm (thường là biến động kỳ). Nhưng một DÒNG BẢNG
    có cột KL và cột tỉ suất thì CÓ kiểm: bản cũ loại hẳn mã khỏi cổng rồi in "báo cáo không công
    bố tỉ suất từ-ngày-mua" — một câu cổng chưa hề đọc báo cáo để biết (§29). Ca thật ZaloPay
    tuần 05→09/10: bảng 3.5 công bố DGC −29,25% (thuần giá, thiếu 8.000đ cổ tức) và lọt."""
    try:
        sys.path.insert(0, ROOT)
        from trading_bot import config as _cfg
        for p in _cfg.load_accounts(_cfg.load_config()):
            if p["label"] == label:
                return {t.upper() for t in (p.get("excluded_tickers") or [])}
    except Exception as exc:                       # thiếu secrets/config → không suy diễn
        print(f"⚠️  không đọc được excluded_tickers của {label} ({exc}) — coi như rỗng", file=sys.stderr)
    return set()


def _all_account_labels() -> set:
    """Nhãn của MỌI account BROKER DNSE trong `trading_bot_accounts.json`, KỂ CẢ disabled.

    Dùng để phân biệt hai ca mà nhánh "không nhận ra tài khoản nào" của `main()` trước đây gộp
    làm một: (a) báo cáo thật sự không thuộc account nào (vd "New deals") ⇒ cho qua; (b) tên file
    nhắc một account CÓ THẬT mà `dar.ACCOUNTS` không thấy vì config lệch ⇒ phải chặn.

    CHỈ lấy profile broker DNSE — đúng population mà `dar.ACCOUNTS` rút từ. Lọc này KHÔNG phải
    cho gọn: sổ paper có nhãn `main`, `ab_dip`, `ab_cross`; `"main" in <tên file>` khớp bừa vào
    hàng loạt tên file vô can và biến cổng thành chặn oan. Đọc không được ⇒ trả rỗng (main() giữ
    hành vi cũ, không tự bịa ra chặn).
    """
    try:
        sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
        from trading_bot import config as _cfg
        # PHẢI dùng ĐÚNG biểu thức broker của `live_dnse_labels()` (config.py:371):
        # `(p.get("broker") or p["cfg"].get("broker") or "phs")`. Hai population này bắt buộc
        # trùng nhau — lệch một chút là account khai broker CHỈ ở `cfg` sẽ vắng ở đây và cổng ÂM
        # THẦM trở lại fail-open đúng cho account đó. Hôm nay hai bên cho cùng kết quả
        # {RocketX, SpaceX, ZaloPay} nên lệch là LATENT, không phải vô hại.
        return {p["label"] for p in _cfg.load_accounts(_cfg.load_config())
                if p.get("label")
                and str(p.get("broker") or p["cfg"].get("broker") or "phs").lower() == "dnse"}
    except Exception:                                          # noqa: BLE001
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
    # Content-completeness TRƯỚC MỌI THỨ: một báo cáo còn "[TBD" không có tỉ suất nào để kiểm
    # (đó chính là cách nó lọt PASS trong rỗng ở vụ tháng 08), nên phải chặn ở đây trước khi
    # chân broker/paper thậm chí bắt đầu chạy.
    incomplete = find_incomplete_markers(report_path)
    if incomplete:
        print(f"\n❌ CHẶN — {len(incomplete)} chỗ còn nội dung CHƯA ĐIỀN trong báo cáo:", file=out)
        for ln, snippet in incomplete:
            print(f"   • dòng {ln}: {snippet[:160]}", file=out)
        return 1

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
        # FAIL-CLOSED khi tên file CÓ nhắc một account mà `dar.ACCOUNTS` lại KHÔNG có
        # (arch-review 2026-09-27). `accounts_asof_from_name()` suy nhãn bằng `dar.ACCOUNTS`,
        # và từ 2026-09-27 `ACCOUNTS` đọc `trading_bot_accounts.json` thay vì hardcode ⇒ một
        # config lệch (`enabled=false`, `mode` đổi, thiếu `account_id`) làm nhãn BIẾN MẤT, nhánh
        # này trả 0 và cổng tỉ suất của báo cáo gửi nhà đầu tư TẮT ÂM THẦM. So với danh sách
        # TOÀN BỘ account (kể cả disabled) để phân biệt "báo cáo không thuộc account nào" (đúng,
        # cho qua) với "account có thật mà cổng không nhìn thấy" (phải chặn).
        _known = _all_account_labels()
        _named = sorted(lb for lb in _known if lb in os.path.basename(report_path))
        if _named:
            print(f"\n❌ CHẶN — tên file nhắc tài khoản {_named} nhưng "
                  f"`dividend_adjusted_return.ACCOUNTS` (đọc trading_bot_accounts.json) chỉ có "
                  f"{sorted(dar.ACCOUNTS)} ⇒ cổng tỉ suất KHÔNG kiểm được báo cáo này. Đây là "
                  f"lệch CONFIG, không phải báo cáo sai: kiểm `enabled`/`mode`/`account_id` của "
                  f"{_named}. KHÔNG cho qua im lặng (§6 mục 5 — email fail-closed theo cổng này).",
                  file=out)
            return 1
        print(f"⚠️  {os.path.basename(report_path)}: không nhận ra tài khoản nào trong tên file "
              f"→ cổng KHÔNG áp dụng (không chặn).", file=out)
        return 0
    rows = parse_report_rows(report_path)
    print(f"CỔNG TỈ SUẤT — {os.path.basename(report_path)} | chốt {asof} | "
          f"tài khoản {', '.join(labels)} | dung sai {tol_pp:.2f}pp", file=out)

    expected, ambiguous, agg = {}, set(), {}
    excluded_keys = {}       # (mã, KL) -> nhãn TK: vị thế excluded — kiểm dòng bảng, ngoài tổng
    unresolved = {}          # (mã, KL) -> (nhãn TK, [lý do]): KHÔNG cấp kỳ vọng (fail-closed)
    basis_notes = []
    vendor_mismatch = []     # (nhãn TK, mã, ex-date, đồng/cp broker, đồng/cp vendor)
    for lb in labels:
        acct = dar.ACCOUNTS[lb]
        pos = broker_positions(acct, asof)
        excl = excluded_tickers(lb)
        res = entitled_gross(pos.keys(), acct, asof)
        gross, mism = res[0], res[1]
        extra = res[2] if len(res) > 2 else {}
        blockers, addback = extra.get("blockers", {}), extra.get("addback", {})
        basis_notes.extend(f"{lb} · {n}" for n in extra.get("notes", []))
        vendor_mismatch.extend((lb,) + m for m in mism)
        tot_pl = tot_cost = 0.0
        left_out = []
        for tk, (qty, cp, mkt) in pos.items():
            key = (tk, qty)
            if tk in excl:
                excluded_keys[key] = lb
            if tk in blockers:
                # KHÔNG dựng được giá vốn thô ⇒ không có kỳ vọng nào để cấp. Cấp "costPrice + 0"
                # ở đây chính là lỗi DRI: mẫu số thiếu đúng phần broker đã trừ, tỉ suất bị thổi lên.
                unresolved[key] = (lb, blockers[tk])
                if tk not in excl:
                    left_out.append(tk)
                continue
            g = gross.get(tk, 0.0)
            pct, pl, raw = expected_pct(qty, cp, mkt, g, addback_ps=addback.get(tk))
            if tk not in excl:
                tot_pl += pl
                tot_cost += qty * raw
            if key in expected:                   # 2 tài khoản trùng cả mã lẫn KL → không phân biệt được
                ambiguous.add(key)
            expected[key] = (lb, pct, pl, raw, cp, g)
        agg[lb] = (tot_pl, tot_cost, tot_pl / tot_cost * 100.0 if tot_cost else 0.0, left_out)

    fails, checked, unmatched = list(paper_fails), 0, 0
    for ln, tk, hdr, cell in unrecognized_return_cells(report_path):
        fails.append(f"{tk} (bảng, dòng {ln}): ô '{cell}' ở cột '{hdr}' là một tỉ suất có dấu "
                     f"nhưng cổng KHÔNG nhận ra cột này là tỉ suất lãi/lỗ hay tỷ trọng ⇒ không "
                     f"kiểm được. Đặt tiêu đề cột là 'Lãi/lỗ (%)' nếu là tỉ suất từ-ngày-mua.")
    fails_no_div = []   # mã lệch mà cổ tức = 0 ⇒ nguyên nhân KHÔNG phải thiếu cổ tức
    fails_with_div = [] # mã lệch mà CÓ cổ tức ⇒ câu "cộng cổ tức ròng vào tử số" mới có nghĩa
    # §corp-action (job Taylor_20260924_064510, Việc 4) — mã CÒN GIỮ (có mặt trong `expected`
    # dưới KL khác) mà lệch KL không phải "lệnh đã thực hiện/ngoài phạm vi" như mọi unmatched
    # khác: có thể là vị thế ĐANG GIỮ bị lệch KL do corp-action credit sớm giữa lúc báo cáo
    # soạn và lúc cổng chạy. Tách riêng để KHÔNG khẳng định nguyên nhân khi chưa xác nhận (§29).
    unmatched_held_qty_mismatch = []
    expected_tickers = {t for t, _q in expected}
    unresolved_published = set()
    print(f"\n{'ma':5}{'KL':>7}{'TK':>9}{'% cong bo':>11}{'% ky vong':>11}{'lech pp':>9}"
          f"{'co tuc GOP':>11}{'gia von THO':>13}  ket qua", file=out)
    for tk, qty, pct in rows:
        key = (tk, qty)
        if key in unresolved:
            lb, why = unresolved[key]
            unresolved_published.add(key)
            fails.append(f"{tk} ({lb}, KL={qty:.0f}): báo cáo công bố {pct:+.2f}% nhưng cổng KHÔNG "
                         f"dựng được giá vốn thô để kiểm — " + " | ".join(why))
            print(f"{tk:5}{qty:>7.0f}{lb:>9}{pct:>11.2f}{'—':>11}{'—':>9}{'—':>11}{'—':>13}"
                  f"  KHÔNG KỲ VỌNG", file=out)
            continue
        if key not in expected:
            if tk in expected_tickers:
                held_qtys = sorted(q for (t2, q) in expected if t2 == tk)
                unmatched_held_qty_mismatch.append((tk, qty, pct, held_qtys))
                continue
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
            # Ghi lại mã nào lệch mà KHÔNG có cổ tức — quyết định câu gợi ý sửa ở cuối.
            if g <= 0:
                fails_no_div.append(tk)
            else:
                fails_with_div.append(tk)
        print(f"{tk:5}{qty:>7.0f}{lb:>9}{pct:>11.2f}{exp:>11.2f}{diff:>9.2f}{g:>11,.2f}"
              f"{_raw:>13,.2f}  {'OK' if ok else 'LỆCH'}"
              f"{'  (excluded — ngoài tổng)' if key in excluded_keys else ''}", file=out)

    # ---- tỉ suất công bố trong VĂN XUÔI (không có KL ⇒ đối chiếu với MỌI tài khoản giữ mã đó)
    # Mã excluded KHÔNG vào đây: `MÃ ±x%` của nó trong văn xuôi thường là biến động kỳ (xem
    # `excluded_tickers`). Dòng BẢNG của nó thì đã kiểm ở vòng lặp trên.
    by_ticker = {}
    for key, (lb, exp, *_r) in expected.items():
        if key not in excluded_keys:
            by_ticker.setdefault(key[0], []).append((lb, exp))
    # Luật "CŨ → ĐÚNG" (thêm 2026-08-10 sau khi cổng chặn oan chính báo cáo đã sửa): một mục đính
    # chính TỬ TẾ phải nêu lại số SAI bên cạnh số ĐÚNG ("SAB −5,53% → SAB +0,49%"), nên cấm số sai
    # xuất hiện là cấm luôn việc công bố minh bạch. Gom theo (DÒNG, MÃ): dòng nào có ÍT NHẤT một
    # tỉ suất khớp kỳ vọng thì các số còn lại của mã đó trên chính dòng ấy là số đối chiếu/lịch sử.
    # KHÔNG phải lỗ hổng: muốn lách phải in kèm số ĐÚNG ngay cạnh — tức là đã công bố đúng.
    prose_checked, by_line = 0, {}
    unresolved_tk = {k[0]: k for k in unresolved if k not in excluded_keys}
    for tk, pct, ln in parse_prose_pcts(report_path):
        if tk in by_ticker:
            by_line.setdefault((ln, tk), []).append(pct)
        elif tk in unresolved_tk and unresolved_tk[tk] not in unresolved_published:
            key = unresolved_tk[tk]
            unresolved_published.add(key)
            lb, why = unresolved[key]
            fails.append(f"{tk} ({lb}; văn xuôi, dòng {ln}): báo cáo công bố {pct:+.2f}% nhưng cổng "
                         f"KHÔNG dựng được giá vốn thô để kiểm — " + " | ".join(why))
    for (ln, tk), pcts in sorted(by_line.items()):
        cands = by_ticker[tk]
        prose_checked += len(pcts)
        if any(abs(p - e) <= tol_pp for p in pcts for _lb, e in cands):
            continue
        shown = " / ".join(f"{p:+.2f}%" for p in pcts)
        fails.append(f"{tk} (văn xuôi, dòng {ln}): báo cáo {shown} không khớp tài khoản nào — "
                     "kỳ vọng " + ", ".join(f"{lb} {e:+.2f}%" for lb, e in cands))
        if all(expected.get((tk, q), (None, None, None, None, None, 0))[5] <= 0
               for (t2, q) in expected if t2 == tk):
            fails_no_div.append(tk)
        else:
            fails_with_div.append(tk)

    # ---- TỔNG kỳ vọng của từng tài khoản: cổng KHÔNG tự dò dòng tổng trong văn bản (quá mong
    # manh), nhưng in ra để người soạn đối chiếu tay — không phủ thì phải nói ra, không im lặng.
    print("\nTỔNG kỳ vọng (vị thế đang giữ, đã cộng cổ tức RÒNG — đối chiếu tay với dòng tổng "
          "trong báo cáo):", file=out)
    for lb, (pl, cost, pct, left_out) in agg.items():
        print(f"   {lb:8} giá vốn thô {cost:>15,.0f}  lãi/lỗ tổng {pl:>15,.0f}  {pct:>7.2f}%"
              + (f"   ⚠️ THIẾU {', '.join(sorted(left_out))} (không dựng được kỳ vọng — tổng này "
                 f"KHÔNG so được với dòng tổng của báo cáo)" if left_out else ""), file=out)
    seen = {(a, b) for a, b, _ in rows}
    if excluded_keys:
        # Nói ĐÚNG điều cổng vừa làm với từng mã excluded, đọc từ `rows` — không khẳng định "báo
        # cáo không công bố" khi chưa nhìn (§29).
        pub = sorted(f"{tk} ({lb})" for (tk, q), lb in excluded_keys.items() if (tk, q) in seen)
        nopub = sorted(f"{tk} ({lb})" for (tk, q), lb in excluded_keys.items()
                       if (tk, q) not in seen)
        print("   (vị thế excluded — NGOÀI tổng ở trên; giá vốn = sổ broker + cổ tức đã giải, "
              "không có journal lệnh mua: "
              + "; ".join(x for x in (
                  f"ĐÃ KIỂM dòng bảng công bố tỉ suất của {', '.join(pub)}" if pub else "",
                  f"không thấy dòng bảng (mã, KL) nào của {', '.join(nopub)}" if nopub else "") if x)
              + ")", file=out)
    if basis_notes:
        print("\nCƠ SỞ GIÁ VỐN / CỔ TỨC — bằng chứng đã dùng:", file=out)
        for n in basis_notes:
            print(f"   · {n}", file=out)
    quiet = sorted((k, v) for k, v in unresolved.items() if k not in unresolved_published)
    if quiet:
        print(f"\nℹ️  {len(quiet)} vị thế KHÔNG có kỳ vọng nhưng báo cáo không công bố tỉ suất "
              f"riêng của nó (không chặn — vẫn phải xử trước khi công bố):", file=out)
        for (tk, q), (lb, why) in quiet:
            print(f"   • {tk} ({lb}, KL={q:.0f}): " + " | ".join(why), file=out)
    prose_tk = {t for t, _, _ in parse_prose_pcts(report_path)}
    nocover = [f"{tk} ({lb}, cổ tức {g:,.0f}đ/cp)" for (tk, q), (lb, _e, _pl, _raw, _cp, g)
               in expected.items() if g > 0 and (tk, q) not in seen and tk not in prose_tk]

    print(f"\nĐã kiểm {checked} dòng bảng + {prose_checked} tỉ suất trong văn xuôi; {unmatched} dòng "
          f"KHÔNG khớp sổ vị thế broker (bảng lãi/lỗ ĐÃ THỰC HIỆN / phân bổ — NGOÀI phạm vi cổng "
          f"này, xem docstring).", file=out)
    if unmatched_held_qty_mismatch:
        print(f"\n⚠️  {len(unmatched_held_qty_mismatch)} dòng CÒN GIỮ mã đó trên sổ broker nhưng KL "
              f"báo cáo KHÔNG khớp KL đang giữ — KHÔNG được tính vào '{unmatched} dòng ngoài phạm "
              f"vi' phía trên (đó là suy luận cho lệnh ĐÃ THỰC HIỆN, ca này vẫn ĐANG GIỮ). Nghi "
              f"corp-action credit sớm giữa lúc soạn báo cáo và lúc cổng chạy — CHƯA xác nhận, "
              f"kiểm tay trước khi kết luận nguyên nhân (§29):", file=out)
        for tk, qty, pct, held_qtys in unmatched_held_qty_mismatch:
            print(f"   • {tk}: báo cáo KL={qty:.0f} ({pct:+.2f}%), broker đang giữ KL="
                  f"{'/'.join(f'{q:.0f}' for q in held_qtys)}", file=out)
    if nocover:
        print(f"ℹ️  {len(nocover)} vị thế CÓ cổ tức nhưng báo cáo không công bố tỉ suất riêng "
              f"(không chặn — không công bố thì không sai được): {', '.join(nocover)}", file=out)
    # ---- LỆCH NGUỒN VENDOR: luôn NÓI RA (không im lặng), chặn khi mã đó đang được CÔNG BỐ.
    # Cảnh báo phải tới người đọc kể cả khi báo cáo PASS — nếu chỉ chặn thì một báo cáo không
    # công bố tỉ suất mã đó sẽ đi qua mà không ai biết nguồn vendor đang lệch.
    vendor_fails = []
    vendor_fail_reasons = set()   # mã lý do của các sự kiện THẬT SỰ bị chặn (R1-C: khác reasons_present)
    reasons_present = set()
    if vendor_mismatch:
        published = {tk for tk, _q, _p in rows} | prose_tk
        print("\n⚠️  LỆCH NGUỒN VENDOR — tiền broker thật ≠ `tav2_bq.corporate_action`:", file=out)
        for lb, tk, ex, broker_ps, vendor_ps, reason, vendor_stock, had_broker_cash in \
                sorted(vendor_mismatch):
            reasons_present.add(reason)
            if reason == "lookup_failed":
                # KHÁC HẲN 3 nhánh dưới: đây KHÔNG PHẢI hai nguồn bất đồng số, mà là "chưa tra
                # được nguồn thứ hai" (BQ lỗi hạ tầng). `vendor_ps=0.0` ở đây là SENTINEL "chưa
                # biết", không phải "vendor xác nhận 0đ" (đó là nhãn `unavailable` KHÁC) — in lẫn
                # vào cặp số VENDOR_MISMATCH_ALERT sẽ tái tạo đúng lớp lỗi §29 mà nhãn
                # `lookup_failed` sinh ra để chặn (arch-review 2026-09-24 vòng 4, R1). Vì vậy dòng
                # MÁY ĐỌC riêng `VENDOR_LOOKUP_FAILED` (7 trường) thay vì tái dùng
                # VENDOR_MISMATCH_ALERT/REASON.
                # `had_broker_cash` (R1-A): `broker_ps` chỉ LÀ tiền broker thật khi sự kiện TỪNG
                # là CASH_CONFIRMED trước khi lookup thất bại — nếu không, nó chỉ là ƯỚC LƯỢNG tỉ
                # số từ giá rơi (tầng 1) và nói "broker đã giải" là khẳng định KHÔNG có bằng chứng
                # (đúng lớp lỗi D1 mà chính sách vendor-mismatch sinh ra để đóng, chỉ đảo vai).
                if had_broker_cash:
                    money_txt = (f"broker đã giải {broker_ps:,.0f}đ/cp nhưng chưa đối soát chéo "
                                 f"được")
                else:
                    money_txt = (f"broker CHƯA giải được số nào (ước lượng từ giá rơi "
                                 f"{broker_ps:,.0f}đ/cp, KHÔNG phải tiền broker thật)")
                line = (f"{tk} ({lb}, ex {ex}): KHÔNG TRA ĐƯỢC nguồn vendor "
                        f"`tav2_bq.corporate_action` (lỗi hạ tầng BQ, KHÔNG phải vendor xác nhận "
                        f"0 sự kiện) — {money_txt}, thử lại khi BQ khoẻ")
                print(f"   • {line}", file=out)
                # R1-B: chỉ CHẶN khi lookup_failed THẬT SỰ làm mất một số đã từng công bố
                # (had_broker_cash=True). Khi False, `cash_per_share` đã là 0 TRƯỚC lookup thất
                # bại (event chưa bao giờ CASH_CONFIRMED) nên không con số công bố nào bị mất —
                # đo K1 2026-09-24: 56/62 sự kiện 6 tháng rơi vào nhóm này (gồm 3 ca nhiễu giá rơi
                # ~100-300đ: SCL/DRI/TV1), chặn TRỌN báo cáo vì chúng là quá tay so với bằng chứng.
                if had_broker_cash and tk in published:
                    vendor_fails.append(line)
                    vendor_fail_reasons.add(reason)
                # Trường cuối là "đang công bố" THÔ (giống hệt cách nhánh ALERT dưới in nó) —
                # KHÔNG gán sẵn quyết định CHẶN vào đây: shell tự tính blocked = hadcash AND
                # published, cùng công thức với Python ở trên, để câu "báo cáo vẫn gửi (không
                # công bố tỉ suất mã này)" chỉ in đúng lúc mã đó THẬT SỰ không được công bố —
                # gán sẵn sẽ làm câu đó SAI cho ca "có công bố nhưng had_broker_cash=False".
                print(f"VENDOR_LOOKUP_FAILED|{lb}|{tk}|{ex}|{broker_ps:.0f}|"
                      f"{1 if had_broker_cash else 0}|{1 if tk in published else 0}", file=out)
                continue
            # Câu chẩn đoán rẽ theo MÃ LÝ DO mà `dar` đã tính, không phát một câu cố định (§29).
            # BA nhánh, không phải hai — mã lý do thiếu/lạ (fail-closed "unknown", xem `mismatches`
            # ở entitled_gross) KHÔNG được rơi vào nhánh `else` cũ và bị gán nhầm thành câu
            # "cash_mismatch": im lặng đoán mò đúng lúc bằng chứng nói "không biết vì sao".
            if reason == "stock_leg_ignored":
                line = (f"{tk} ({lb}, ex {ex}): vendor khai THUẦN CỔ PHIẾU (ISS tỉ lệ "
                        f"{vendor_stock:.4f}, không có chân tiền) nhưng solver giải ra "
                        f"{broker_ps:,.0f}đ/cp TIỀN MẶT mà chưa biết chân cổ phiếu "
                        f"(share_multiplier=1,0) — nghi giá rơi chia tách bị đọc thành cổ tức")
            elif reason == "cash_mismatch":
                lech = (abs(vendor_ps - broker_ps) / broker_ps * 100.0 if broker_ps > 0
                        else float("inf"))
                line = (f"{tk} ({lb}, ex {ex}): broker giải {broker_ps:,.0f}đ/cp vs vendor "
                        f"{vendor_ps:,.0f}đ/cp — lệch {lech:.1f}%")
            else:
                line = (f"{tk} ({lb}, ex {ex}): LỆCH NGUỒN cổ tức nhưng KHÔNG xác định được mã lý "
                        f"do (broker {broker_ps:,.0f}đ/cp vs vendor {vendor_ps:,.0f}đ/cp) — kiểm "
                        f"thủ công, KHÔNG suy đoán nguyên nhân (§29)")
            print(f"   • {line}", file=out)
            if tk in published:
                vendor_fails.append(line)
                vendor_fail_reasons.add(reason)
            # Dòng MÁY ĐỌC cạnh dòng người đọc: stdout của cổng này chảy vào stdout của
            # `report_delivery_gate.py` (subprocess kế thừa fd) rồi vào LOG của cron — nên nếu
            # không có gì để shell caller bám vào thì cảnh báo chết trong log, KHÔNG tới user.
            # `bin/vendor_mismatch_alert.sh` parse đúng dòng này (giá trị đã chuẩn hoá, KHÔNG
            # grep câu văn xuôi — §28) và bắn Discord/bus. Cố ý in cho CẢ ca không công bố
            # (rc=0): đó chính là ca mà cổng KHÔNG chặn nên không kênh nào khác kêu.
            print(f"VENDOR_MISMATCH_ALERT|{lb}|{tk}|{ex}|{broker_ps:.0f}|{vendor_ps:.0f}|"
                  f"{1 if tk in published else 0}", file=out)
            # MÃ LÝ DO đi ở dòng TAG RIÊNG, KHÔNG thêm trường thứ 8 vào dòng trên. Lý do rất cụ
            # thể: `bin/vendor_mismatch_alert.sh` đọc dòng `ALERT` bằng
            # `while IFS='|' read -r _tag acct tk ex broker vendor published` — `read` gộp MỌI
            # trường dư vào biến CUỐI, nên một trường thứ 8 sẽ biến `published` thành
            # `"1|stock_leg_ignored"`, `[ "$published" = "1" ]` FAIL, và cảnh báo nói "báo cáo vẫn
            # gửi" đúng lúc báo cáo đang bị CHẶN. Tag riêng ⇒ reader cũ bỏ qua (grep của nó neo
            # `^VENDOR_MISMATCH_ALERT\|`), reader mới đọc thêm được. Hợp đồng cũ giữ NGUYÊN BYTE.
            print(f"VENDOR_MISMATCH_REASON|{lb}|{tk}|{ex}|{reason}|{vendor_stock:.4f}", file=out)
        print("   → sự kiện đã bị HẠ VỀ UNVERIFIED: cổ tức của nó KHÔNG vào kỳ vọng và KHÔNG được "
              "công bố (§21).", file=out)
        # "VIỆC CẦN LÀM" rẽ theo mã lý do THỰC SỰ có mặt — một báo cáo có thể gộp cả hai (hoặc cả
        # ba) loại cùng lúc, và "đối soát để hai nguồn khớp lại" chỉ đúng cho cash_mismatch; áp nó
        # cho stock_leg_ignored/unknown là chỉ sai hướng người xử lý (§29, cùng lớp lỗi với R1).
        if "cash_mismatch" in reasons_present:
            print("   → VIỆC CẦN LÀM (bất đồng số cổ tức): Winston (data-ops) đối soát "
                  "`tav2_bq.corporate_action` với sổ broker cho đúng (mã, ex-date) trên; chỉ khi "
                  "hai nguồn khớp lại thì tỉ suất mã đó mới được công bố.", file=out)
        if "stock_leg_ignored" in reasons_present:
            print("   → VIỆC CẦN LÀM (nghi giá rơi chia tách bị đọc thành cổ tức): Winston xác "
                  "nhận lại sự kiện CỔ PHIẾU (ISS) với vendor — vì sao chân cổ phiếu chưa được "
                  "credit vào vị thế; KHÔNG PHẢI đối soát số tiền (vendor không khai chân tiền nào "
                  "cho sự kiện này).", file=out)
        if "lookup_failed" in reasons_present:
            print("   → VIỆC CẦN LÀM (hạ tầng tra vendor thất bại, KHÔNG PHẢI bất đồng số liệu): "
                  "chạy lại `report_return_gate.py` cho báo cáo này SAU KHI BQ khoẻ; KHÔNG cần "
                  "Winston đối soát số hay xác nhận sự kiện trừ khi lỗi lặp lại nhiều lượt liên "
                  "tiếp.", file=out)
        if reasons_present - {"cash_mismatch", "stock_leg_ignored", "lookup_failed"}:
            print("   → VIỆC CẦN LÀM (mã lý do không xác định): kiểm thủ công (mã lý do bị "
                  "thiếu/rỗng ở nguồn) — KHÔNG suy đoán nguyên nhân.", file=out)
    if vendor_fails:
        print(f"\n❌ CHẶN — {len(vendor_fails)} mã đang CÔNG BỐ tỉ suất nhưng có sự kiện cổ tức "
              f"lệch nguồn (UNVERIFIED):", file=out)
        for v in vendor_fails:
            print(f"   • {v}", file=out)
        # R1-C: câu "hai nguồn độc lập đang bất đồng" chỉ ĐÚNG khi lý do chặn thật là
        # cash_mismatch/stock_leg_ignored/unknown (hai nguồn CÙNG có số để so). Ca THUẦN
        # lookup_failed KHÔNG có nguồn thứ hai nào để "bất đồng" — chỉ CHƯA TRA ĐƯỢC. In câu này
        # vô điều kiện (như bản trước arch-review vòng 5) tự mâu thuẫn với chính dòng lookup_failed
        # ngay phía trên nó (§29).
        if vendor_fail_reasons - {"lookup_failed"}:
            print("   Nguyên nhân KHÔNG phải sai cơ sở giá cũng KHÔNG phải quên cộng cổ tức: hai "
                  "nguồn độc lập đang bất đồng về SỐ cổ tức.", file=out)
            print("   Gỡ chặn = Winston xác minh xong nguồn vendor, KHÔNG phải nới dung sai cổng.",
                  file=out)
        if "lookup_failed" in vendor_fail_reasons:
            print("   (các mã lookup_failed ở trên: KHÔNG PHẢI hai nguồn bất đồng — BQ lỗi hạ "
                  "tầng chưa tra được nguồn thứ hai. Gỡ chặn = chạy lại khi BQ khoẻ, KHÔNG cần "
                  "Winston đối soát số.)", file=out)
    if fails:
        print(f"\n❌ CHẶN — {len(fails)} vấn đề:", file=out)
        for f_ in fails:
            print(f"   • {f_}", file=out)
        if unresolved_published:
            print("\n   Với mã 'KHÔNG dựng được giá vốn thô': KHÔNG sửa bằng cách lấy costPrice "
                  "broker làm giá vốn — broker đã trừ cổ tức khỏi nó, mẫu số sẽ thiếu và tỉ suất "
                  "bị thổi lên. Gỡ chặn = giải xong sự kiện nêu trong lý do (`dividend_adjusted_"
                  "return.py --resolve <mã> --from … --to …`), hoặc bỏ tỉ suất của mã đó khỏi báo "
                  "cáo và nói rõ vì sao.", file=out)
        # Gợi ý sửa phải theo ĐÚNG nguyên nhân của chính những mã đang lệch, không phát một
        # câu cố định. Mã lệch mà cổ tức = 0đ/cp thì KHÔNG THỂ là "thiếu cộng cổ tức" — ca
        # thật SCL 2026-08 (+17,00% vs +17,85%, cổ tức 0đ): nguyên nhân là CƠ SỞ GIÁ, báo cáo
        # dựng trên `marketPrice` thay vì giá đóng cửa. Câu gợi ý cũ chỉ vào cổ tức sẽ đẩy
        # người sửa đi sai hướng ngay dòng đầu (§29).
        # Loại mã ĐANG có sự kiện lệch nguồn/lookup_failed khỏi câu "sai cơ sở giá" — cổ tức của
        # NÓ = 0 vì bị hạ UNVERIFIED (vendor bất đồng hoặc chưa tra được), KHÔNG PHẢI vì thật sự
        # không có cổ tức; nguyên nhân đúng đã in ở khối LỆCH NGUỒN VENDOR trên, in thêm câu "sai
        # cơ sở giá" ở đây cho ĐÚNG mã đó là chẩn đoán SAI chồng lên chẩn đoán ĐÚNG (§29, arch-review
        # 2026-09-24 vòng 4 R1(b)).
        vendor_mismatch_tks = {tk for _lb, tk, *_r in vendor_mismatch}
        fails_no_div_shown = sorted(set(fails_no_div) - vendor_mismatch_tks)
        if fails_no_div_shown:
            print(f"\n   Trong đó {', '.join(fails_no_div_shown)} KHÔNG có cổ tức ⇒ lệch "
                  f"KHÔNG phải do thiếu cộng cổ tức. Gần như chắc chắn sai CƠ SỞ GIÁ: dùng "
                  f"`mtm_price` trong `data/execution_logs/verified_snapshot_<acct>_<asof>.json` "
                  f"(giá đóng cửa đã xác minh), KHÔNG dùng `positions[].marketPrice` — field đó "
                  f"không phải giá ATC.", file=out)
        # Chỉ in khi THẬT SỰ có mã lệch mang cổ tức (đọc từ `g` của chính dòng lệch). Bản cũ
        # suy từ "token đầu của câu lỗi không nằm trong fails_no_div" nên in câu này cho cả lỗi
        # sổ paper lẫn mã không dựng được kỳ vọng — chỉ sai hướng người sửa (§29).
        if fails_with_div:
            print(f"\n   Với mã CÓ cổ tức ({', '.join(sorted(set(fails_with_div)))}): chạy "
                  "`mike/bin/dividend_adjusted_return.py --resolve <rổ mã> --from … --to …`,"
                  "\n   cộng cổ tức RÒNG vào TỬ SỐ (giữ giá vốn THÔ ở mẫu số); giá vốn và cổ "
                  "tức/cp đều quy về KL ĐANG GIỮ (cột 'gia von THO' và 'co tuc GOP' ở bảng trên) "
                  "— coding_guidelines §21.", file=out)
        return 1
    if vendor_fails:
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

    # 16b: NHIỀU LÔ cùng mã (khác loanPackageId) ⇒ GỘP qty + bình quân gia quyền cost, không
    # ghi đè mất lô đứng trước (bug thật 2026-09-02, ZaloPay 08-31: BID/MBB/VCB mỗi mã 2 lô).
    _fake_asof = "9999-01-01"
    _fake_path = os.path.join(EXEC_DIR, f"dnse_raw_{_fake_asof}.jsonl")
    with open(_fake_path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "account_no": "0009999999", "kind": "positions",
            "payload": {"positions": [
                {"accountNo": "0009999999", "symbol": "XYZ", "marketType": "STOCK",
                 "openQuantity": 100, "costPrice": 10000.0, "marketPrice": 12000.0,
                 "loanPackageId": 1},
                {"accountNo": "0009999999", "symbol": "XYZ", "marketType": "STOCK",
                 "openQuantity": 300, "costPrice": 11000.0, "marketPrice": 12000.0,
                 "loanPackageId": 2},
            ]},
        }, ensure_ascii=False) + "\n")
    try:
        pos = broker_positions("0009999999", _fake_asof,
                               price_fn=lambda tks, d: {"XYZ": 12000.0})
        qty, cost, mp = pos["XYZ"]
        # tổng qty = 100+300=400; cost bình quân = (100*10000+300*11000)/400 = 10750
        check("multi-lot: gộp tổng qty (100+300, không mất lô đầu)", qty, 400.0)
        check("multi-lot: cost bình quân gia quyền đúng", round(cost, 4), 10750.0)
        check("multi-lot: giá lấy từ nguồn giá đóng cửa, không từ lô", mp, 12000.0)
    finally:
        os.unlink(_fake_path)

    # 16c: LÔ LỆCH GIÁ THẬT — fixture lấy nguyên từ ZaloPay 2026-08-14T19:10:23 (BID 107cp
    # @35.800 gói 1826 / 300cp @38.850 gói 1258, lệch 8,5% trong CÙNG một bản đọc; nguyên nhân
    # là replica đọc-sau-ghi của DNSE trong lúc batch reprice EOD chạy).
    # Bản CŨ `agg.setdefault(sym, [0,0,mp])` lấy giá lô ĐẦU (35.800) rồi áp cho TỔNG 407cp.
    # Bản mới KHÔNG đọc marketPrice nữa ⇒ lô lệch giá không còn ảnh hưởng kết quả. Đây là ca
    # mà fixture cũ (2 lô CÙNG giá 12.000) không bao giờ chạm tới được.
    _fake_asof2 = "9999-01-02"
    _fake_path2 = os.path.join(EXEC_DIR, f"dnse_raw_{_fake_asof2}.jsonl")
    with open(_fake_path2, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "account_no": "0009999999", "kind": "positions",
            "payload": {"positions": [
                {"accountNo": "0009999999", "symbol": "BID", "marketType": "STOCK",
                 "openQuantity": 107, "costPrice": 30000.0, "marketPrice": 35800.0,
                 "loanPackageId": 1826},
                {"accountNo": "0009999999", "symbol": "BID", "marketType": "STOCK",
                 "openQuantity": 300, "costPrice": 30000.0, "marketPrice": 38850.0,
                 "loanPackageId": 1258},
            ]},
        }, ensure_ascii=False) + "\n")
    try:
        pos2 = broker_positions("0009999999", _fake_asof2,
                                price_fn=lambda tks, d: {"BID": 35800.0})
        q2, c2, mp2 = pos2["BID"]
        check("lô lệch giá: vẫn gộp đủ khối lượng (107+300)", q2, 407.0)
        check("lô lệch giá: KHÔNG lấy giá từ lô nào cả — dùng giá đóng cửa", mp2, 35800.0)
        # Chứng minh ngược: nếu nguồn giá trả số khác, kết quả PHẢI đi theo nguồn giá,
        # không bị lô 35.800/38.850 kéo về.
        pos3 = broker_positions("0009999999", _fake_asof2,
                                price_fn=lambda tks, d: {"BID": 36500.0})
        check("lô lệch giá: đổi nguồn giá thì kết quả đổi theo (không dính giá lô)",
              pos3["BID"][2], 36500.0)
        # Thiếu giá 1 mã ⇒ CHẶN, không đoán và không lặng lẽ bỏ mã.
        try:
            broker_positions("0009999999", _fake_asof2, price_fn=lambda tks, d: {})
            check("lô lệch giá: thiếu giá ⇒ phải CHẶN", "không raise", "raise ValueError")
        except ValueError:
            check("lô lệch giá: thiếu giá ⇒ CHẶN (fail-closed)", True, True)
    finally:
        os.unlink(_fake_path2)

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

    # 30-32: content-completeness gate (thêm 2026-09-02, vụ báo cáo tháng 08 giao template dở).
    # Ca 1: có marker TBD ⇒ CHẶN, kể cả khi tên file không mang nhãn tài khoản nào (accounts_
    # asof_from_name() sẽ ném ValueError cho "SpaceX_ZaloPay_monthly_report_2026-08.md" là bình
    # thường — completeness phải chặn TRƯỚC bước đó nên không phụ thuộc suy luận tên file).
    with tempfile.NamedTemporaryFile("w", suffix="_monthly_report_2026-08.md", delete=False,
                                      encoding="utf-8") as fh:
        fh.write("## 1. TÓM TẮT ĐIỀU HÀNH\n\n| NAV | *[TBD]* |\n\n## 5. Vĩ mô\nĐã điền đầy đủ.\n")
        p_tbd = fh.name
    rc_tbd = run_gate(p_tbd, out=open(os.devnull, "w"))
    check("content-gate: còn marker TBD ⇒ run_gate() CHẶN (rc=1)", rc_tbd, 1)
    hits = find_incomplete_markers(p_tbd)
    check("content-gate: báo đúng dòng chứa marker", [h[0] for h in hits], [3])
    os.unlink(p_tbd)

    # Ca 2: đầy đủ, không marker nào ⇒ im lặng hoàn toàn ở bước completeness (không tự tạo báo
    # động giả) — dùng file không mang nhãn tài khoản để không phụ thuộc dnse_raw/BQ thật.
    with tempfile.NamedTemporaryFile("w", suffix="_report_2026-08-13.md", delete=False,
                                      encoding="utf-8") as fh:
        fh.write("## 1. Đã điền đầy đủ\n\nKhông còn chỗ nào bỏ trống.\n")
        p_full = fh.name
    check("content-gate: đầy đủ ⇒ find_incomplete_markers() rỗng",
          find_incomplete_markers(p_full), [])
    rc_full = run_gate(p_full, out=open(os.devnull, "w"))
    check("content-gate: đầy đủ + không tài khoản nào trong tên ⇒ run_gate() PASS (rc=0)",
          rc_full, 0)
    os.unlink(p_full)

    # Ca 3: chạy 2 lần liên tiếp trên CÙNG file đầy đủ ⇒ vẫn PASS cả 2 lần, không đổi hành vi
    # theo số lần chạy (gate không có state riêng, nên "không spam" tương đương "idempotent").
    with tempfile.NamedTemporaryFile("w", suffix="_report_2026-08-14.md", delete=False,
                                      encoding="utf-8") as fh:
        fh.write("## Đầy đủ, chạy 2 lần\n")
        p_twice = fh.name
    rc1 = run_gate(p_twice, out=open(os.devnull, "w"))
    rc2 = run_gate(p_twice, out=open(os.devnull, "w"))
    check("content-gate: chạy 2 lần liên tiếp ⇒ kết quả giống nhau (rc, rc)", (rc1, rc2), (0, 0))
    os.unlink(p_twice)

    # ---- LỆCH NGUỒN VENDOR (chính sách user chốt 2026-09-24) — offline, không chạm BQ/broker.
    # Ca gốc: broker giải 1.000đ/cp, vendor `corporate_action` khai 1.500đ/cp (lệch 50%).
    # `dar` đã hạ sự kiện về UNVERIFIED ⇒ cổ tức biến mất khỏi kỳ vọng; nếu cổng KHÔNG nói ra thì
    # đó đúng là "báo cáo bị chặn/lệch trong IM LẶNG" mà chính sách cấm.
    def _run_vendor_case(report_body: str, mism):
        g = globals()
        keep = {k: g[k] for k in ("broker_positions", "entitled_gross", "excluded_tickers",
                                  "parse_prose_pcts")}
        g["broker_positions"] = lambda acct, asof, **kw: {"ZZZ": (100.0, 27_800.0, 24_464.0)}
        g["entitled_gross"] = lambda tks, acct, asof: ({}, list(mism))
        g["excluded_tickers"] = lambda lb: set()
        with tempfile.NamedTemporaryFile("w", suffix="_SpaceX_report_2026-09-24.md",
                                          delete=False, encoding="utf-8") as fh:
            fh.write(report_body)
            path = fh.name
        buf = io.StringIO()
        try:
            rc = run_gate(path, out=buf)
        finally:
            g.update(keep)
            os.unlink(path)
        return rc, buf.getvalue()

    _MISM = [("ZZZ", "2026-09-24", 1_000.0, 1_500.0, "cash_mismatch", 0.0, True)]
    # Vị thế ZZZ: 100cp, giá vốn broker 27.800, giá 24.464 ⇒ -12,00% (đúng con số arch-review dựng)
    rc_pub, txt_pub = _run_vendor_case(
        "## Vị thế\n\n| Mã | KL | % lãi/lỗ |\n|---|---|---|\n| ZZZ | 100 | -12,00% |\n", _MISM)
    check("vendor mismatch + mã ĐANG công bố ⇒ CHẶN (rc=1)", rc_pub, 1)
    check("cảnh báo nêu cả hai số nguồn", ("1,000" in txt_pub and "1,500" in txt_pub), True)
    check("cảnh báo lệch 50,0%", "50.0%" in txt_pub, True)
    check("cảnh báo chỉ đích danh Winston (data-ops), không phải câu chung chung (§29)",
          "Winston" in txt_pub, True)
    # Dòng MÁY ĐỌC là HỢP ĐỒNG với `bin/vendor_mismatch_alert.sh` (V3): thiếu nó thì cảnh báo
    # chỉ còn là văn xuôi trong log cron, không kênh nào bắn tới user được.
    check("có dòng máy đọc VENDOR_MISMATCH_ALERT, cờ published=1",
          "VENDOR_MISMATCH_ALERT|SpaceX|ZZZ|2026-09-24|1000|1500|1" in txt_pub, True)
    assert rc_pub == 1 and "Winston" in txt_pub, (
        "MUTATION-GUARD gate_vendor_mismatch_block: mã có sự kiện lệch nguồn vẫn được CÔNG BỐ tỉ "
        f"suất mà cổng cho qua (rc={rc_pub}) hoặc không nêu Winston.")

    # arch-review vòng 8 (job Taylor_20260927_103400): `gate_vendor_mismatch_block` ở trên chỉ ghim
    # rc=1 + có chữ "Winston" — mà "Winston" xuất hiện ở NHIỀU khối (kể cả câu "Gỡ chặn = Winston
    # xác minh xong nguồn vendor" của khối CHẶN). Nên mutation `if "cash_mismatch" in
    # reasons_present: -> if False:` (dòng 786) vẫn PASS 99/99 (đo thật): dòng VIỆC CẦN LÀM nói
    # ĐÚNG việc phải làm biến mất mà không ca nào FAIL. Anchor RIÊNG của nhánh này: tiền tố
    # "VIỆC CẦN LÀM (bất đồng số cổ tức)".
    check("khối VIỆC CẦN LÀM có dòng RIÊNG cho cash_mismatch (anchor riêng, không dùng chung chữ "
          "'Winston' với khối CHẶN)",
          "VIỆC CẦN LÀM (bất đồng số cổ tức)" in txt_pub, True)
    assert "VIỆC CẦN LÀM (bất đồng số cổ tức)" in txt_pub, (
        "MUTATION-GUARD gate_reasons_present_cash_mismatch_todo: nhánh "
        "`if \"cash_mismatch\" in reasons_present:` (khối VIỆC CẦN LÀM) đã bị tắt/hỏng — báo cáo "
        "vẫn CHẶN nhưng người xử lý không còn được bảo phải làm gì (Winston đối soát "
        "`tav2_bq.corporate_action` với sổ broker). Chữ 'Winston' ở khối CHẶN KHÔNG phải bằng "
        f"chứng cho nhánh này. Đang là: {txt_pub!r}")

    # Không công bố tỉ suất mã đó ⇒ KHÔNG chặn (không công bố thì không sai được), NHƯNG cảnh báo
    # vẫn phải in ra — đây chính là "raise warning mà KHÔNG chặn báo cáo im lặng".
    rc_quiet2, txt_quiet2 = _run_vendor_case("## Không công bố tỉ suất mã nào\n", _MISM)
    check("vendor mismatch + mã KHÔNG công bố ⇒ không chặn (rc=0)", rc_quiet2, 0)
    check("… nhưng cảnh báo VẪN in ra (không im lặng)", "LỆCH NGUỒN VENDOR" in txt_quiet2, True)
    check("… và dòng máy đọc vẫn có, cờ published=0 (ca rc=0 — nếu thiếu, cảnh báo chết trong log)",
          "VENDOR_MISMATCH_ALERT|SpaceX|ZZZ|2026-09-24|1000|1500|0" in txt_quiet2, True)
    assert "LỆCH NGUỒN VENDOR" in txt_quiet2, (
        "MUTATION-GUARD gate_vendor_warning_always: cổng PASS mà không hề nhắc tới lệch nguồn ⇒ "
        "user không bao giờ biết để gọi Winston.")

    # Chống hồi quy: không có lệch nguồn ⇒ không có dòng cảnh báo nào, hành vi cũ nguyên vẹn.
    rc_ok2, txt_ok2 = _run_vendor_case("## Không công bố tỉ suất mã nào\n", [])
    check("không lệch nguồn ⇒ rc=0 và KHÔNG có cảnh báo vendor", (rc_ok2, "LỆCH NGUỒN VENDOR" in txt_ok2),
          (0, False))
    check("không lệch nguồn ⇒ KHÔNG có dòng máy đọc (không báo động giả tới user)",
          "VENDOR_MISMATCH_ALERT" in txt_ok2, False)

    # ---- LÝ DO THỨ HAI `stock_leg_ignored` (arch-review vòng 2, D1). Ở ca này `vendor_cash = 0`,
    # nên câu cũ ("broker 1.000 vs vendor 0 — lệch 100%") mời người đọc hiểu "vendor KHÔNG CÓ dữ
    # liệu", trái hẳn sự thật: vendor có dữ liệu RÕ RÀNG và đang nói sự kiện này không có tiền.
    _MISM_STOCK = [("ZZZ", "2026-09-24", 1_000.0, 0.0, "stock_leg_ignored", 0.2604104, True)]
    rc_st, txt_st = _run_vendor_case(
        "## Vị thế\n\n| Mã | KL | % lãi/lỗ |\n|---|---|---|\n| ZZZ | 100 | -12,00% |\n", _MISM_STOCK)
    check("stock_leg_ignored + mã ĐANG công bố ⇒ vẫn CHẶN (rc=1)", rc_st, 1)
    check("câu chẩn đoán nói ĐÚNG nguyên nhân (thuần cổ phiếu + tỉ lệ ISS), KHÔNG nói 'vendor 0đ'",
          ("THUẦN CỔ PHIẾU" in txt_st and "0.2604" in txt_st), True)
    check("… và KHÔNG phát câu 'lệch 100.0%' gây hiểu sai", "lệch 100.0%" in txt_st, False)
    # Hợp đồng CŨ giữ nguyên byte (7 trường) — thêm trường thứ 8 sẽ làm `read -r` của shell gộp
    # nó vào `published` và đảo ngược cờ CHẶN. Mã lý do đi ở dòng TAG RIÊNG.
    check("dòng ALERT giữ ĐÚNG 7 trường như hợp đồng cũ (không thêm trường thứ 8)",
          "VENDOR_MISMATCH_ALERT|SpaceX|ZZZ|2026-09-24|1000|0|1\n" in txt_st, True)
    check("có dòng TAG RIÊNG mang mã lý do + tỉ lệ ISS",
          "VENDOR_MISMATCH_REASON|SpaceX|ZZZ|2026-09-24|stock_leg_ignored|0.2604" in txt_st, True)
    assert "THUẦN CỔ PHIẾU" in txt_st and "VENDOR_MISMATCH_REASON" in txt_st, (
        "MUTATION-GUARD gate_vendor_reason_routing: hai mã lý do khác nhau mà cổng phát CÙNG một "
        "câu ⇒ ca D1 bị đọc thành 'vendor thiếu dữ liệu' và Winston điều tra sai hướng ngay dòng "
        f"đầu (§29). Đang là: {txt_st!r}")

    # arch-review vòng 8 (job Taylor_20260927_103400): `gate_vendor_reason_routing` ở trên bám vào
    # dòng chẩn đoán PER-EVENT ("THUẦN CỔ PHIẾU") — nó KHÔNG phủ nhánh VIỆC CẦN LÀM riêng
    # `if "stock_leg_ignored" in reasons_present:` (dòng 790). Mutation dòng đó thành `if False:`
    # vẫn PASS 99/99 (đo thật) ⇒ Winston mất dòng chỉ dẫn "xác nhận lại sự kiện CỔ PHIẾU (ISS)"
    # mà không assertion nào kêu. Anchor RIÊNG: cụm "KHÔNG PHẢI đối soát số tiền" chỉ có ở đây
    # (dòng chẩn đoán per-event không nhắc tới việc đối soát số tiền).
    check("khối VIỆC CẦN LÀM có dòng RIÊNG cho stock_leg_ignored (giao Winston xác nhận chân CỔ "
          "PHIẾU, KHÔNG PHẢI đối soát số tiền)",
          "KHÔNG PHẢI đối soát số tiền" in txt_st, True)
    assert "KHÔNG PHẢI đối soát số tiền" in txt_st, (
        "MUTATION-GUARD gate_reasons_present_stock_leg_todo: nhánh "
        "`if \"stock_leg_ignored\" in reasons_present:` (khối VIỆC CẦN LÀM) đã bị tắt/hỏng — "
        "Winston mất dòng 'xác nhận lại sự kiện CỔ PHIẾU (ISS) … KHÔNG PHẢI đối soát số tiền' và "
        "sẽ đi đối soát TIỀN cho một sự kiện vendor khai thuần cổ phiếu (§29). Câu chẩn đoán "
        f"per-event 'THUẦN CỔ PHIẾU' KHÔNG phải bằng chứng cho nhánh này. Đang là: {txt_st!r}")

    # ---- LÝ DO THỨ BA: mã lý do KHÔNG xác định (arch-review D1b, R2) — fail-closed, KHÔNG đoán.
    # Mô phỏng đúng ca reviewer bắn: `Adjustment` set `vendor_check="mismatch"` mà không set
    # `vendor_mismatch_reason` (caller cũ/hỏng) ⇒ `entitled_gross` phải trả "unknown", KHÔNG được
    # đoán "cash_mismatch" rồi phát câu "lệch X%" như thể đã biết nguyên nhân.
    _MISM_UNKNOWN = [("ZZZ", "2026-09-24", 1_000.0, 700.0, "unknown", 0.0, True)]
    rc_unk, txt_unk = _run_vendor_case(
        "## Vị thế\n\n| Mã | KL | % lãi/lỗ |\n|---|---|---|\n| ZZZ | 100 | -12,00% |\n",
        _MISM_UNKNOWN)
    check("mã lý do unknown + mã ĐANG công bố ⇒ vẫn CHẶN (rc=1)", rc_unk, 1)
    check("câu chẩn đoán nói THẲNG không xác định được mã lý do",
          "KHÔNG xác định được mã lý do" in txt_unk, True)
    check("… và KHÔNG lặng lẽ đoán thành câu 'lệch X%' của cash_mismatch",
          "lệch 30.0%" in txt_unk, False)
    check("… VIỆC CẦN LÀM nói đúng 'kiểm thủ công', không phải 'đối soát cho khớp lại'",
          "kiểm thủ công" in txt_unk, True)
    assert "KHÔNG xác định được mã lý do" in txt_unk and "kiểm thủ công" in txt_unk, (
        "MUTATION-GUARD gate_vendor_reason_unknown_no_guess: mã lý do rỗng/lạ mà cổng vẫn phát một "
        "trong hai câu chẩn đoán cố định (cash_mismatch hoặc stock_leg_ignored) ⇒ đoán mò nguyên "
        f"nhân đúng lúc bằng chứng nói 'không biết' (§29). Đang là: {txt_unk!r}")

    # arch-review vòng 8 (job Taylor_20260927_103400): guard `gate_vendor_reason_unknown_no_guess`
    # ở trên dùng anchor "kiểm thủ công", chuỗi CÓ MẶT ở CẢ HAI chỗ — dòng chẩn đoán per-event
    # (nhánh `else` của `reason`) VÀ khối VIỆC CẦN LÀM (`if reasons_present - {...}`). Nên mutation
    # `if reasons_present - {...}: -> if False:` (dòng 800) vẫn PASS 99/99 (đo thật). Anchor RIÊNG
    # của khối VIỆC CẦN LÀM: tiền tố "VIỆC CẦN LÀM (mã lý do không xác định)" chỉ có ở đó.
    check("khối VIỆC CẦN LÀM có dòng RIÊNG cho mã lý do không xác định (anchor riêng, không dùng "
          "chung 'kiểm thủ công' với dòng chẩn đoán per-event)",
          "VIỆC CẦN LÀM (mã lý do không xác định)" in txt_unk, True)
    assert "VIỆC CẦN LÀM (mã lý do không xác định)" in txt_unk, (
        "MUTATION-GUARD gate_reasons_present_unknown_todo: nhánh "
        "`if reasons_present - {\"cash_mismatch\", \"stock_leg_ignored\", \"lookup_failed\"}:` "
        "(khối VIỆC CẦN LÀM) đã bị tắt/hỏng — người xử lý mất dòng chỉ dẫn 'kiểm thủ công (mã lý "
        "do bị thiếu/rỗng ở nguồn)'. Chuỗi 'kiểm thủ công' ở dòng chẩn đoán per-event KHÔNG phải "
        f"bằng chứng cho nhánh này. Đang là: {txt_unk!r}")

    # ---- LOOKUP_FAILED (arch-review 2026-09-24 vòng 4, R1): BQ lỗi hạ tầng, KHÔNG tra được vendor
    # — KHÁC HẲN "hai nguồn bất đồng số" (mismatch). Trước bản vá này sự kiện loại này KHÔNG vào
    # `mismatches` nên biến mất khỏi kỳ vọng mà KHÔNG ai nói ra, và nếu mã đó lệch % công bố thì
    # cổng còn tự đoán nhầm nguyên nhân thành "sai cơ sở giá" (§29).
    # had_broker_cash=True (arch-review vòng 5, R1-A/R1-B): sự kiện TỪNG là CASH_CONFIRMED trước
    # khi lookup thất bại ⇒ per_share LÀ tiền broker thật, mã ĐANG công bố ⇒ CHẶN vẫn đúng.
    _LOOKUP = [("ZZZ", "2026-09-24", 1_000.0, 0.0, "lookup_failed", 0.0, True)]
    rc_lkf, txt_lkf = _run_vendor_case(
        "## Vị thế\n\n| Mã | KL | % lãi/lỗ |\n|---|---|---|\n| ZZZ | 100 | -12,00% |\n",
        _LOOKUP)
    check("lookup_failed + mã ĐANG công bố ⇒ CHẶN (rc=1)", rc_lkf, 1)
    check("câu người-đọc nói ĐÚNG 'lỗi hạ tầng BQ', không phải 'hai nguồn bất đồng'",
          "lỗi hạ tầng BQ" in txt_lkf, True)
    check("R1-A: had_broker_cash=True ⇒ câu khẳng định ĐÚNG 'broker đã giải' (per_share là tiền thật)",
          "broker đã giải 1,000đ/cp" in txt_lkf, True)
    check("có dòng máy đọc VENDOR_LOOKUP_FAILED, had_broker_cash=1, published=1",
          "VENDOR_LOOKUP_FAILED|SpaceX|ZZZ|2026-09-24|1000|1|1\n" in txt_lkf, True)
    check("KHÔNG in dòng VENDOR_MISMATCH_ALERT cho ca lookup_failed (tránh trộn sentinel 0đ vào "
          "cặp số cũ)", "VENDOR_MISMATCH_ALERT" in txt_lkf, False)
    check("VIỆC CẦN LÀM nói 'chạy lại' (rerun khi BQ khoẻ), không giao Winston đối soát số",
          "chạy lại" in txt_lkf, True)
    # arch-review dispatch 2026-09-24 (audit vòng 7, C1): check "chạy lại" ở trên là VACUOUS cho
    # nhánh `if "lookup_failed" in reasons_present:` (khối VIỆC CẦN LÀM) — chuỗi "chạy lại" CŨNG
    # xuất hiện ở khối `if "lookup_failed" in vendor_fail_reasons:` phía dưới (T1(b) đã ghim
    # riêng), nên ca `_LOOKUP` này (bị CHẶN, cả hai khối cùng chạy) khiến mutation
    # `if "lookup_failed" in reasons_present: -> if False:` vẫn PASS 93/93 (đo thật: sed dòng
    # 732 thành `if False:` rồi chạy --selfcheck, không FAIL ca nào). Cần anchor RIÊNG của khối
    # VIỆC CẦN LÀM: "hạ tầng tra vendor thất bại, KHÔNG PHẢI bất đồng số liệu" chỉ có ở đây,
    # khối kia dùng chữ khác ("KHÔNG PHẢI hai nguồn bất đồng").
    check("khối VIỆC CẦN LÀM (reasons_present) có câu riêng 'hạ tầng tra vendor thất bại, KHÔNG "
          "PHẢI bất đồng số liệu'", "hạ tầng tra vendor thất bại, KHÔNG PHẢI bất đồng số liệu"
          in txt_lkf, True)
    assert "hạ tầng tra vendor thất bại, KHÔNG PHẢI bất đồng số liệu" in txt_lkf, (
        "MUTATION-GUARD gate_lookup_failed_reasons_present_note: nhánh "
        "`if \"lookup_failed\" in reasons_present:` (khối VIỆC CẦN LÀM) đã bị tắt/hỏng — câu "
        "'chạy lại' sống sót chỉ nhờ khối `vendor_fail_reasons` khác phía dưới, KHÔNG phải bằng "
        f"chứng cho nhánh này. Đang là: {txt_lkf!r}")
    assert rc_lkf == 1 and "VENDOR_LOOKUP_FAILED" in txt_lkf and "VENDOR_MISMATCH_ALERT" not in txt_lkf, (
        "MUTATION-GUARD gate_lookup_failed_own_tag: ca BQ lỗi hạ tầng phải dùng TAG RIÊNG "
        "VENDOR_LOOKUP_FAILED, KHÔNG tái dùng VENDOR_MISMATCH_ALERT (sentinel 0đ sẽ bị đọc nhầm "
        f"thành 'vendor xác nhận 0đ'). Đang là: {txt_lkf!r}")
    # R1-C, T1(a) (arch-review vòng 6): ca THUẦN lookup_failed (không có cash_mismatch/
    # stock_leg_ignored/unknown nào khác) KHÔNG được in câu "hai nguồn độc lập đang bất đồng" —
    # câu đó chỉ đúng khi có NGUỒN THỨ HAI để so, mà lookup_failed nghĩa là CHƯA TRA ĐƯỢC nguồn
    # đó. Trước bản vá này, mutation `if vendor_fail_reasons - {"lookup_failed"}: -> if True:`
    # vẫn PASS 90/90 vì không có assertion nào bám vào SỰ VẮNG MẶT của câu này.
    check("KHÔNG in câu 'hai nguồn độc lập đang bất đồng' cho ca THUẦN lookup_failed",
          "hai nguồn độc lập đang bất đồng" in txt_lkf, False)
    check("KHÔNG in câu 'Gỡ chặn = Winston xác minh xong nguồn vendor' (sai người — BQ lỗi hạ "
          "tầng, không phải Winston đối soát)",
          "Gỡ chặn = Winston xác minh xong nguồn vendor" in txt_lkf, False)
    assert "hai nguồn độc lập đang bất đồng" not in txt_lkf, (
        "MUTATION-GUARD gate_lookup_failed_no_mismatch_sentence: ca THUẦN lookup_failed mà cổng "
        "vẫn in câu 'hai nguồn độc lập đang bất đồng' ⇒ tự mâu thuẫn với dòng lookup_failed ngay "
        f"phía trên nó, sai nguyên nhân (§29). Đang là: {txt_lkf!r}")
    # T1(b): câu riêng "(các mã lookup_failed ở trên: KHÔNG PHẢI hai nguồn bất đồng…)" PHẢI có
    # mặt cho ca này (bị CHẶN, vendor_fail_reasons={"lookup_failed"}) — dùng anchor RIÊNG của
    # nhánh này, KHÔNG dùng "chạy lại" (câu đó CŨNG xuất hiện ở khối VIỆC CẦN LÀM phía trên,
    # theo `reasons_present` — một mutation tắt nhánh `if "lookup_failed" in vendor_fail_reasons:`
    # vẫn để "chạy lại" sống sót nhờ khối kia, nên check cũ ở dòng trên KHÔNG bắt được mutation này).
    check("có câu riêng '…chưa tra được nguồn thứ hai' cho ca THUẦN lookup_failed BỊ CHẶN",
          "chưa tra được nguồn thứ hai" in txt_lkf, True)
    assert "chưa tra được nguồn thứ hai" in txt_lkf, (
        "MUTATION-GUARD gate_lookup_failed_reason_note: ca THUẦN lookup_failed bị CHẶN mà thiếu "
        "câu ghi chú riêng '…chưa tra được nguồn thứ hai' — nhánh "
        "`if \"lookup_failed\" in vendor_fail_reasons:` đã bị tắt/hỏng (câu 'chạy lại' ở khối "
        f"VIỆC CẦN LÀM phía trên KHÔNG phải bằng chứng cho nhánh này). Đang là: {txt_lkf!r}")

    rc_lkf_q, txt_lkf_q = _run_vendor_case("## Không công bố tỉ suất mã nào\n", _LOOKUP)
    check("lookup_failed + mã KHÔNG công bố ⇒ không chặn (rc=0)", rc_lkf_q, 0)
    check("… nhưng vẫn cảnh báo (không im lặng)", "KHÔNG TRA ĐƯỢC nguồn vendor" in txt_lkf_q, True)
    check("… và dòng máy đọc vẫn có, had_broker_cash=1, published=0",
          "VENDOR_LOOKUP_FAILED|SpaceX|ZZZ|2026-09-24|1000|1|0\n" in txt_lkf_q, True)

    # ---- R1-A/R1-B (arch-review vòng 5): had_broker_cash=False — ca THẬT MBS 2026-04-02 dựng lại
    # từ exp_vendor_mismatch/k1_v2_rerun.log (STOCK_CONFIRMED/unresolved, broker=4.828,8đ/cp chỉ là
    # ƯỚC LƯỢNG từ giá rơi chia tách, CHƯA từng là CASH_CONFIRMED — 0 chân tiền, phát hành CP 1:0,5).
    # Trước bản vá R1-A/R1-B, ca này bị in "broker đã giải 4.829đ/cp" (SAI — chưa từng là tiền
    # broker) và CHẶN oan dù không mất số công bố nào (K1: 56/62 sự kiện 6 tháng thuộc nhóm này).
    _LOOKUP_NOCASH = [("ZZZ", "2026-09-24", 4_829.0, 0.0, "lookup_failed", 0.0, False)]
    rc_lkf_nc, txt_lkf_nc = _run_vendor_case(
        "## Vị thế\n\n| Mã | KL | % lãi/lỗ |\n|---|---|---|\n| ZZZ | 100 | -12,00% |\n",
        _LOOKUP_NOCASH)
    check("R1-B: had_broker_cash=False + mã ĐANG công bố ⇒ KHÔNG CHẶN (rc=0, chưa mất số công bố)",
          rc_lkf_nc, 0)
    check("R1-A: had_broker_cash=False ⇒ câu ĐÚNG 'broker CHƯA giải được số nào (ước lượng...)'",
          "broker CHƯA giải được số nào (ước lượng từ giá rơi 4,829đ/cp" in txt_lkf_nc, True)
    check("R1-A: KHÔNG khẳng định sai 'broker đã giải' khi had_broker_cash=False",
          "broker đã giải" in txt_lkf_nc, False)
    check("dòng máy đọc VENDOR_LOOKUP_FAILED có had_broker_cash=0, published=1",
          "VENDOR_LOOKUP_FAILED|SpaceX|ZZZ|2026-09-24|4829|0|1\n" in txt_lkf_nc, True)
    assert rc_lkf_nc == 0, (
        "MUTATION-GUARD gate_lookup_failed_hadcash_gate: had_broker_cash=False (per_share chỉ là "
        "ƯỚC LƯỢNG từ giá rơi, KHÔNG mất số công bố nào) nhưng cổng vẫn CHẶN — quá tay so với bằng "
        f"chứng (R1-B, arch-review vòng 5). rc={rc_lkf_nc}, đang là: {txt_lkf_nc!r}")
    assert "broker đã giải" not in txt_lkf_nc, (
        "MUTATION-GUARD gate_lookup_failed_hadcash_money_text: had_broker_cash=False mà câu vẫn "
        "khẳng định 'broker đã giải' — per_share ở đây CHƯA TỪNG là tiền broker thật, chỉ là ước "
        f"lượng tỉ số từ giá rơi (R1-A, arch-review vòng 5). Đang là: {txt_lkf_nc!r}")

    # R1(b): mã có sự kiện lookup_failed mà % công bố ≠ % kỳ vọng (vì thiếu cổ tức bị hạ) KHÔNG
    # được lẫn vào câu "sai CƠ SỞ GIÁ" — nguyên nhân ĐÚNG (chưa tra được vendor) đã nói ở khối
    # LỆCH NGUỒN VENDOR trên rồi.
    rc_lkf_wrong, txt_lkf_wrong = _run_vendor_case(
        "## Vị thế\n\n| Mã | KL | % lãi/lỗ |\n|---|---|---|\n| ZZZ | 100 | -8,00% |\n",
        _LOOKUP)
    check("% công bố lệch kỳ vọng ⇒ vẫn CHẶN (rc=1, qua nhánh fails chính)", rc_lkf_wrong, 1)
    check("KHÔNG phát câu 'sai CƠ SỞ GIÁ' cho ZZZ (nguyên nhân thật đã nói ở trên, §29)",
          "Gần như chắc chắn sai CƠ SỞ GIÁ" in txt_lkf_wrong, False)
    assert "Gần như chắc chắn sai CƠ SỞ GIÁ" not in txt_lkf_wrong, (
        "MUTATION-GUARD gate_lookup_failed_not_price_basis: mã có sự kiện lookup_failed mà % công "
        "bố lệch kỳ vọng lại bị cổng gán nhầm nguyên nhân 'sai cơ sở giá' — chẩn đoán SAI chồng "
        f"lên chẩn đoán ĐÚNG (§29). Đang là: {txt_lkf_wrong!r}")

    # ---- CHÍNH `entitled_gross` (arch-review vòng 2, V1). 6 ca ngay trên MONKEYPATCH chính
    # `entitled_gross` nên chúng chỉ kiểm nửa DƯỚI (cổng xử lý danh sách mismatch được BƠM TAY);
    # nửa TRÊN — đoạn đọc `adjs` thật để SINH ra danh sách đó — không có một assertion nào: xoá
    # hẳn khối `if a.vendor_check == "mismatch"` vẫn cho 137 PASS / 0 FAIL. Ở đây patch TẦNG
    # DƯỚI (`dar.resolve_dividends` / `dar.broker_qty` / `dar._qty_at`) để thân hàm thật chạy
    # đủ, TUYỆT ĐỐI không patch `entitled_gross`.
    _ASOF = "2026-09-24"

    def _adj(tk, ex, ps, kind, vcheck, vcash, reason=None, had_cash=None):
        a = dar.Adjustment(ticker=tk, ex_date=ex, last_cum_date=ex, last_cum_price=10_000.0,
                           per_share=ps)
        a.kind, a.vendor_check, a.vendor_cash = kind, vcheck, vcash
        if reason is not None:
            a.vendor_mismatch_reason = reason
        if had_cash is not None:
            a.lookup_failed_had_broker_cash = had_cash
        return a

    _EG_ADJS = [
        # (1) lệch nguồn, ĐÃ bị `dar` hạ về UNVERIFIED — phải nổi lên ở danh sách mismatch
        _adj("AAA", "2026-09-10", 1_000.0, "UNVERIFIED", "mismatch", 1_500.0,
             reason="cash_mismatch"),
        # (2) hai nguồn khớp — vẫn phải vào kỳ vọng như cũ
        _adj("BBB", "2026-09-11", 800.0, "CASH_CONFIRMED", "match", 800.0),
        # (3) ex-date SAU asof — ngoài kỳ, bỏ
        _adj("CCC", "2026-09-30", 700.0, "CASH_CONFIRMED", "match", 700.0),
        # (4) tài khoản không nắm giữ tại ngày chốt quyền — bỏ
        _adj("DDD", "2026-09-12", 600.0, "CASH_CONFIRMED", "match", 600.0),
        # (5) PHÒNG THỦ NHIỀU TẦNG: giả định `dar` hồi quy, để nguyên CASH_CONFIRMED cho một sự
        # kiện lệch nguồn ⇒ `cash_per_share` > 0. Cổng vẫn PHẢI loại nó khỏi kỳ vọng, không
        # được dựa vào tầng dưới đã hạ cấp hộ.
        _adj("EEE", "2026-09-13", 500.0, "CASH_CONFIRMED", "mismatch", 900.0,
             reason="cash_mismatch"),
        # (6) R2 (arch-review D1b): `vendor_check="mismatch"` mà KHÔNG set `vendor_mismatch_reason`
        # (caller cũ/hỏng, y hệt ca reviewer bắn) — `entitled_gross` phải fail-closed về "unknown",
        # KHÔNG được đoán "cash_mismatch" chỉ vì đó là default cũ.
        _adj("FFF", "2026-09-14", 400.0, "CASH_CONFIRMED", "mismatch", 700.0),
        # (7) arch-review 2026-09-24 vòng 4, R1: BQ lỗi hạ tầng (KHÔNG tra được vendor) — `dar` đã
        # hạ về UNVERIFIED trước khi `entitled_gross` thấy Adjustment này (y hệt luồng thật ở
        # `bq_corp_action`'s except-block). Phải nổi lên mismatches với reason="lookup_failed",
        # KHÔNG được lặng lẽ `continue` như trước bản vá này. had_cash=False (mặc định dataclass,
        # ghi rõ ở đây): per_share CHƯA từng là CASH_CONFIRMED (đúng luồng ước lượng từ giá rơi).
        _adj("GGG", "2026-09-15", 300.0, "UNVERIFIED", "lookup_failed", 0.0, had_cash=False),
        # (8) arch-review vòng 5, R1-A: cùng nhãn lookup_failed nhưng had_cash=True — mô phỏng sự
        # kiện TỪNG là CASH_CONFIRMED trước khi `bq_corp_action` lỗi hạ (đúng luồng
        # `resolve_dividends` gán `adj.lookup_failed_had_broker_cash = (adj.kind ==
        # "CASH_CONFIRMED")` TRƯỚC khi hạ `kind` về UNVERIFIED). `entitled_gross` phải đọc field
        # này từ Adjustment thật, không phải suy đoán/gán cứng.
        _adj("HHH", "2026-09-16", 200.0, "UNVERIFIED", "lookup_failed", 0.0, had_cash=True),
    ]

    # `broker_cost_series` (cửa I/O thêm 2026-10-10) cũng phải stub — không thì thân hàm thật
    # đọc sổ dnse_raw THẬT của SpaceX và ca này thôi offline. Rỗng = "sổ không quan sát được".
    _saved_dar = {k: getattr(dar, k) for k in ("resolve_dividends", "broker_qty", "_qty_at",
                                               "broker_cost_series")}
    try:
        dar.resolve_dividends = lambda tks, start, end: list(_EG_ADJS)
        dar.broker_qty = lambda acct: {"stub": True}
        dar._qty_at = lambda qmap, a, frame=None: (0.0 if a.ticker == "DDD" else 100.0)
        dar.broker_cost_series = lambda acct: {}
        eg_out, eg_mism, eg_extra = entitled_gross(
            ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH"], "0002023347", _ASOF)
    finally:
        for k, v in _saved_dar.items():
            setattr(dar, k, v)

    check("entitled_gross: sự kiện lệch nguồn vào ĐÚNG phần tử thứ 2 (mã, ex, broker, vendor, "
          "had_broker_cash — arch-review vòng 5, R1-A)",
          sorted(eg_mism), [("AAA", "2026-09-10", 1_000.0, 1_500.0, "cash_mismatch", 0.0, True),
                            ("EEE", "2026-09-13", 500.0, 900.0, "cash_mismatch", 0.0, True),
                            ("FFF", "2026-09-14", 400.0, 700.0, "unknown", 0.0, True),
                            ("GGG", "2026-09-15", 300.0, 0.0, "lookup_failed", 0.0, False),
                            ("HHH", "2026-09-16", 200.0, 0.0, "lookup_failed", 0.0, True)])
    check("entitled_gross: mã lệch nguồn KHÔNG vào kỳ vọng công bố",
          ("AAA" in eg_out, "EEE" in eg_out, "FFF" in eg_out, "GGG" in eg_out, "HHH" in eg_out),
          (False, False, False, False, False))
    check("entitled_gross: sự kiện hai nguồn KHỚP vẫn vào kỳ vọng", eg_out, {"BBB": 800.0})
    assert [m[0] for m in sorted(eg_mism)] == ["AAA", "EEE", "FFF", "GGG", "HHH"], (
        "MUTATION-GUARD entitled_gross_detect_mismatch: thân hàm thật KHÔNG sinh ra danh sách "
        "lệch nguồn ⇒ cổng dưới không bao giờ có gì để chặn/cảnh báo (xoá khối "
        "`if a.vendor_check == \"mismatch\"` mà mọi test vẫn xanh).")
    _eg_mism_by_tk_early = {m[0]: m for m in eg_mism}
    assert _eg_mism_by_tk_early["GGG"][4] == "lookup_failed", (
        "MUTATION-GUARD entitled_gross_lookup_failed_detect: `Adjustment.vendor_check == "
        "'lookup_failed'` (BQ lỗi hạ tầng) KHÔNG nổi lên `mismatches` ⇒ cổ tức của mã đó lặng lẽ "
        "biến mất khỏi kỳ vọng mà không ai nói ra (arch-review 2026-09-24 vòng 4, R1). Đang là: "
        f"{_eg_mism_by_tk_early.get('GGG')!r}")
    assert "GGG" not in eg_out, (
        "MUTATION-GUARD entitled_gross_lookup_failed_excluded: sự kiện lookup_failed vẫn cộng cổ "
        "tức vào kỳ vọng (bỏ `continue` sau khi ghi nhận).")
    # R1-A: had_broker_cash phải LÀ provenance THẬT đọc từ `Adjustment.lookup_failed_had_broker_cash`
    # — KHÔNG được gán cứng True/False cho MỌI sự kiện lookup_failed (GGG=False, HHH=True, khác
    # nhau đúng vì Adjustment khác nhau; gán cứng một giá trị sẽ làm MỘT trong hai assertion sau
    # rơi vào nhánh sai mà không lộ ra nếu chỉ test một chiều).
    assert _eg_mism_by_tk_early["GGG"][6] is False, (
        "MUTATION-GUARD entitled_gross_hadcash_provenance_false: GGG có "
        "`lookup_failed_had_broker_cash=False` (per_share CHƯA từng là tiền broker thật) nhưng "
        f"`entitled_gross` trả had_broker_cash khác False. Đang là: {_eg_mism_by_tk_early['GGG']!r}")
    assert _eg_mism_by_tk_early["HHH"][6] is True, (
        "MUTATION-GUARD entitled_gross_hadcash_provenance_true: HHH có "
        "`lookup_failed_had_broker_cash=True` (per_share LÀ tiền broker thật, sự kiện TỪNG "
        "CASH_CONFIRMED) nhưng `entitled_gross` trả had_broker_cash khác True — nếu code gán cứng "
        f"False cho mọi lookup_failed, đây là assertion duy nhất bắt được. Đang là: "
        f"{_eg_mism_by_tk_early['HHH']!r}")
    _eg_mism_by_tk = {m[0]: m for m in eg_mism}
    assert _eg_mism_by_tk["FFF"][4] == "unknown", (
        "MUTATION-GUARD gate_vendor_reason_failclosed: Adjustment KHÔNG tự set "
        "`vendor_mismatch_reason` (caller cũ/hỏng) mà `entitled_gross` vẫn ĐOÁN thành "
        "'cash_mismatch' ⇒ Winston bị dẫn sai hướng đúng lúc mã lý do THẬT SỰ không xác định "
        f"được (§29). Đang là: {_eg_mism_by_tk['FFF'][4]!r}")
    assert "EEE" not in eg_out, (
        "MUTATION-GUARD entitled_gross_mismatch_excluded: sự kiện lệch nguồn vẫn cộng cổ tức vào "
        "kỳ vọng (bỏ `continue` sau khi ghi nhận mismatch).")

    # ---- Việc 4 (job Taylor_20260924_064510) — dòng CÒN GIỮ mã (broker vẫn có vị thế) nhưng KL
    # báo cáo KHÔNG khớp KL broker phải rơi vào nhánh cảnh báo RIÊNG, KHÔNG bị đếm/chẩn đoán
    # chung với "lệnh đã thực hiện/phân bổ — ngoài phạm vi" (đó là suy luận SAI khi mã vẫn đang
    # được giữ — §29). Mã THẬT SỰ ngoài phạm vi (broker không hề giữ) phải giữ NGUYÊN hành vi cũ.
    def _run_unmatched_case(report_body: str, positions: dict):
        g = globals()
        keep = {k: g[k] for k in ("broker_positions", "entitled_gross", "excluded_tickers")}
        g["broker_positions"] = lambda acct, asof, **kw: dict(positions)
        g["entitled_gross"] = lambda tks, acct, asof: ({}, [])
        g["excluded_tickers"] = lambda lb: set()
        with tempfile.NamedTemporaryFile("w", suffix="_SpaceX_report_2026-09-24.md",
                                          delete=False, encoding="utf-8") as fh:
            fh.write(report_body)
            path = fh.name
        buf = io.StringIO()
        try:
            rc = run_gate(path, out=buf)
        finally:
            g.update(keep)
            os.unlink(path)
        return rc, buf.getvalue()

    # QQQ: broker ĐANG GIỮ 100cp; báo cáo ghi KL=150 (lệch, nghi corp-action). RRR: broker
    # KHÔNG hề giữ mã này — đúng nghĩa "lệnh đã thực hiện/ngoài phạm vi" cũ.
    rc_um, txt_um = _run_unmatched_case(
        "## Vị thế\n\n| Mã | KL | % lãi/lỗ |\n|---|---|---|\n"
        "| QQQ | 150 | +2,00% |\n| RRR | 999 | +3,00% |\n",
        {"QQQ": (100.0, 20000.0, 22000.0)})
    check("Việc4: PASS (rc=0) — không mã nào bị CHẶN vì lệch KL", rc_um, 0)
    check("Việc4: QQQ (còn giữ, lệch KL) rơi vào khối cảnh báo RIÊNG",
          "CÒN GIỮ mã đó" in txt_um and "QQQ" in txt_um, True)
    check("Việc4: khối cảnh báo nêu đúng KL báo cáo (150) và KL broker đang giữ (100)",
          "KL=150" in txt_um and "KL=100" in txt_um, True)
    check("Việc4: đếm 'ngoài phạm vi' KHÔNG gộp mã còn giữ (đúng 1 dòng: chỉ RRR)",
          "Đã kiểm 0 dòng bảng + 0 tỉ suất trong văn xuôi; 1 dòng" in txt_um, True)
    check("Việc4: RRR (thật sự ngoài phạm vi) KHÔNG xuất hiện trong khối cảnh báo lệch KL",
          "RRR" not in txt_um.split("CÒN GIỮ mã đó")[1].split("vị thế CÓ cổ tức")[0]
          if "CÒN GIỮ mã đó" in txt_um else True, True)

    # MUTATION-GUARD: nếu ai revert về hành vi cũ (`unmatched += 1; continue` cho MỌI mã không
    # khớp key, không phân biệt còn giữ hay không) — QQQ sẽ bị gộp vào đếm "ngoài phạm vi" (đếm
    # sẽ là 2, không phải 1) và khối cảnh báo riêng biến mất hoàn toàn.
    assert "CÒN GIỮ mã đó" in txt_um, (
        "MUTATION-GUARD unmatched_held_qty_mismatch_missing: mã CÒN GIỮ trên broker nhưng lệch "
        "KL không còn được tách khỏi 'ngoài phạm vi' — hành vi CŨ (unmatched += 1 vô điều kiện) "
        f"đã quay lại. Output thật: {txt_um!r}")
    assert "Đã kiểm 0 dòng bảng + 0 tỉ suất trong văn xuôi; 2 dòng" not in txt_um, (
        "MUTATION-GUARD unmatched_count_wrongly_includes_held: đếm 'ngoài phạm vi' đang gộp cả "
        "QQQ (còn giữ) lẫn RRR (ngoài phạm vi thật) thành 2 — đúng lỗi §29 dispatch mô tả.")

    _selfcheck_total_return(check)

    print(f"SELFCHECK: {'PASS' if ok else 'FAIL'} ({pass_count}/{len(ran)} ca)")
    return 0 if ok else 1


def _selfcheck_total_return(check) -> None:
    """Chuẩn tỉ suất tổng 2026-10-10 — 4 ca thật + các lỗi cùng lớp. OFFLINE: mọi cửa I/O của
    `dar` và `broker_positions` thay bằng số THẬT chép từ dnse_raw / corporate_action; thân
    `entitled_gross` và `run_gate` chạy THẬT (không patch hai hàm đó). Mutation tương ứng nằm ở
    `bin/total_return_mutants.py`."""
    import tempfile
    g = globals()

    def ev(tk, cum, ex, cash, kind="CASH_CONFIRMED", vcheck="match", mult=1.0, frame=1.0, **kw):
        a = dar.Adjustment(ticker=tk, ex_date=ex, last_cum_date=cum, last_cum_price=10_000.0,
                           per_share=cash)
        a.kind, a.vendor_check, a.share_multiplier, a.frame_factor = kind, vcheck, mult, frame
        for k, v in kw.items():
            setattr(a, k, v)
        return a

    def run(body, positions, adjs, series, excl=(), window=None, asof="2026-10-09",
            label="ZaloPay", direct=False):
        """Chạy cổng THẬT trên fixture. `window` = dict (vendor cửa sổ) hoặc Exception để ném."""
        keep_g = {k: g[k] for k in ("broker_positions", "excluded_tickers")}
        names = ("resolve_dividends", "broker_qty", "_qty_at", "broker_cost_series",
                 "bq_corp_events_window")
        keep_d = {k: getattr(dar, k) for k in names}

        def _win(*a, **k):
            if isinstance(window, Exception):
                raise window
            return dict(window or {})
        g["broker_positions"] = lambda acct, d, **kw: dict(positions)
        g["excluded_tickers"] = lambda lb: set(excl)
        dar.resolve_dividends = lambda tks, start, end: [a for a in adjs if a.ticker in tks]
        dar.broker_qty = lambda acct: {}
        dar._qty_at = lambda qmap, a, frame=None: 100.0
        dar.broker_cost_series = lambda acct: {k: list(v) for k, v in series.items()}
        dar.bq_corp_events_window = _win
        try:
            if direct:
                return entitled_gross(list(positions), "x", asof)
            with tempfile.NamedTemporaryFile("w", suffix=f"_{label}_report_{asof}.md",
                                             delete=False, encoding="utf-8") as fh:
                fh.write(body)
                path = fh.name
            buf = io.StringIO()
            try:
                return run_gate(path, out=buf), buf.getvalue()
            finally:
                os.unlink(path)
        finally:
            g.update(keep_g)
            for k, v in keep_d.items():
                setattr(dar, k, v)

    def table(*rows):
        return ("## 3.5 Danh mục\n\n| Mã | KL | Giá vốn | Lãi/lỗ (%) |\n|---|---:|---:|---:|\n"
                + "".join(f"| {tk} | {kl} | x | {pct} |\n" for tk, kl, pct in rows))

    # ---- sổ giá vốn broker THẬT (dnse_raw) quanh từng sự kiện
    DRI_HI, DRI_LO = 1900 * 13263.1579, 1900 * 12263.1579
    S_DRI = {"DRI": [("2026-09-04T19:07:00", 1900.0, DRI_HI), ("2026-09-18T19:07:00", 1900.0, DRI_HI),
                     ("2026-09-21T04:51:37", 1900.0, DRI_HI), ("2026-09-21T19:07:40", 1900.0, DRI_LO),
                     ("2026-09-22T19:07:32", 1900.0, DRI_LO), ("2026-10-09T23:30:07", 1900.0, DRI_LO)]}
    P_DRI = {"DRI": (1900.0, 12263.1579, 16900.0)}
    dri_ok = ev("DRI", "2026-09-21", "2026-09-22", 1000.0)
    dri_unv = ev("DRI", "2026-09-21", "2026-09-22", 910.0, kind="UNVERIFIED", vcheck="unavailable",
                 note="hệ VÔ ĐỊNH")

    print("  -- CA 2: cổ tức CHƯA giải mà broker đã trừ giá vốn ⇒ KHÔNG cấp kỳ vọng")
    rc, txt = run(table(("DRI", "1.900", "+37,81%")), P_DRI, [dri_unv], S_DRI)
    check("CA2: báo cáo công bố +37,81% (costPrice đã trừ cổ tức + cổ tức 0) ⇒ CHẶN", rc, 1)
    check("CA2: cổng KHÔNG in một '% kỳ vọng' nào cho DRI", "KHÔNG KỲ VỌNG" in txt, True)
    check("CA2: KHÔNG còn PASS", "✅ PASS" in txt, False)
    check("CA2: lý do trích bằng chứng sổ broker (trừ đúng 1.000đ lúc 21/09 19:07)",
          "bị TRỪ 1,000.00đ" in txt and "2026-09-21T19:07:40" in txt, True)
    check("CA2: gợi ý KHÔNG bảo 'lấy costPrice làm giá vốn'",
          "KHÔNG sửa bằng cách lấy costPrice" in txt, True)
    rc, txt = run(table(("DRI", "1.900", "+34,58%")), P_DRI, [dri_unv], S_DRI)
    check("CA2: kể cả số ĐÚNG cũng không được cấp PASS khi cổng chưa kiểm được", rc, 1)
    rc, txt = run("## Ghi chú\n\nKhông có bảng vị thế.\n", P_DRI, [dri_unv], S_DRI)
    check("CA2: không công bố tỉ suất DRI ⇒ không chặn", rc, 0)
    check("CA2: … nhưng vẫn NÓI RA mã đang thiếu kỳ vọng",
          "KHÔNG có kỳ vọng nhưng báo cáo không công bố" in txt, True)
    rc, txt = run("## Nhận định\n\nDRI +37,81% từ ngày mua.\n", P_DRI, [dri_unv], S_DRI)
    check("CA2: công bố qua VĂN XUÔI cũng bị chặn", rc, 1)
    rc, txt = run(table(("DRI", "1.900", "+34,58%")), P_DRI, [dri_ok], S_DRI)
    check("CA2: sự kiện ĐÃ giải ⇒ kỳ vọng +34,58% và PASS", (rc, "34.58" in txt), (0, True))
    check("CA2: giá vốn THÔ in ra = 13.263,16", "13,263.16" in txt, True)
    rc, txt = run(table(("DRI", "1.900", "+37,81%")), P_DRI, [dri_ok], S_DRI)
    check("CA2: sự kiện đã giải, báo cáo vẫn ghi +37,81% ⇒ LỆCH", rc, 1)

    print("  -- sổ broker làm TRỌNG TÀI: bước trừ không ai nhận / cú nhảy không đụng giá vốn")
    rc, txt = run(table(("DRI", "1.900", "+37,81%")), P_DRI, [], S_DRI)
    check("không sự kiện nào được phát hiện nhưng sổ broker có bước trừ 1.000đ ⇒ CHẶN",
          (rc, "KHÔNG có sự kiện đã giải nào khớp" in txt), (1, True))
    noise = ev("DRI", "2026-09-07", "2026-09-08", 90.0, kind="UNVERIFIED", vcheck="lookup_failed")
    out, mism, extra = run("", P_DRI, [noise, dri_ok], S_DRI, direct=True)
    check("cú nhảy chưa giải (BQ lỗi) mà giá vốn broker KHÔNG đổi quanh ngày đó ⇒ không chặn",
          extra["blockers"], {})
    check("… cổ tức thật vẫn vào kỳ vọng", out, {"DRI": 1000.0})
    near = ev("DRI", "2026-09-18", "2026-09-21", 90.0, kind="UNVERIFIED", vcheck="unavailable")
    out, mism, extra = run("", P_DRI, [near, dri_ok], S_DRI, direct=True)
    check("cú nhảy chưa giải SÁT sự kiện thật không 'cướp' bước trừ của sự kiện đã giải",
          (extra["blockers"], out), ({}, {"DRI": 1000.0}))
    nz = ev("DRI", "2026-09-18", "2026-09-21", 0.0, kind="RATIO_NOISE", vcheck="unavailable")
    out, mism, extra = run("", P_DRI, [nz, dri_ok], S_DRI, direct=True)
    check("cú nhảy ĐÃ chứng minh là nhiễu (ex 21/09, sát sự kiện thật) không được đụng tới sổ",
          (extra["blockers"], out), ({}, {"DRI": 1000.0}))
    out, mism, extra = run("", P_DRI, [dri_unv], {}, direct=True)
    check("sự kiện chưa giải + sổ broker KHÔNG quan sát được ⇒ chặn (không loại trừ được)",
          list(extra["blockers"]), ["DRI"])
    wrong = ev("DRI", "2026-09-21", "2026-09-22", 800.0)
    out, mism, extra = run("", P_DRI, [wrong], S_DRI, direct=True)
    check("sự kiện 'đã giải' 800đ nhưng broker trừ 1.000đ ⇒ chặn, không cộng số sai",
          (list(extra["blockers"]), out), (["DRI"], {}))

    print("  -- broker trừ giá vốn TRƯỚC ex-date (tối ngày cuối còn quyền)")
    S_PRE = {"DRI": S_DRI["DRI"][:4]}
    P_PRE = {"DRI": (1900.0, 12263.1579, 14800.0)}
    W = {("DRI", "2026-09-22"): {"cash": 1000.0, "stock": None, "stock_free": 0.0}}
    rc, txt = run(table(("DRI", "1.900", "+11,59%")), P_PRE, [], S_PRE, window=W, asof="2026-09-21")
    check("chốt 21/09 (ex 22/09): cộng lại 1.000đ giá vốn, CHƯA tính thu nhập ⇒ +11,59% PASS", rc, 0)
    check("… và nói rõ đã làm gì", "CHƯA tính thu nhập" in txt, True)
    rc, txt = run(table(("DRI", "1.900", "+20,69%")), P_PRE, [], S_PRE, window=W, asof="2026-09-21")
    check("… +20,69% (lấy costPrice đã trừ làm giá vốn) ⇒ CHẶN", rc, 1)
    rc, txt = run(table(("DRI", "1.900", "+11,59%")), P_PRE, [], S_PRE, asof="2026-09-21",
                  window={("DRI", "2026-09-22"): {"cash": 900.0, "stock": None, "stock_free": 0.0}})
    check("vendor khai 900đ ≠ broker trừ 1.000đ ⇒ không nhận, CHẶN", rc, 1)
    rc, txt = run(table(("DRI", "1.900", "+11,59%")), P_PRE, [], S_PRE, asof="2026-09-21",
                  window=RuntimeError("bq query failed"))
    check("không tra được vendor ⇒ CHẶN (fail-closed), nêu lỗi thật",
          (rc, "bq query failed" in txt), (1, True))
    pct, _pl, raw = expected_pct(1900, 12263.1579, 14800.0, 0.0, addback_ps=1000.0)
    check("expected_pct: addback 1.000, thu nhập 0 ⇒ giá vốn thô 13.263,16", round(raw, 2), 13263.16)
    check("expected_pct: mặc định addback = cổ tức (hành vi cũ không đổi)",
          expected_pct(500, 86360.0, 82600.0, 8000.0),
          expected_pct(500, 86360.0, 82600.0, 8000.0, addback_ps=8000.0))

    print("  -- CA 3: mã excluded CÓ dòng bảng công bố tỉ suất thì PHẢI được kiểm")
    P_DGC = {"DGC": (10000.0, 39775.0, 33800.0), "PVT": (2071.0, 17248.31, 25200.0)}
    S_DGC = {"DGC": [("2026-09-10T19:07:23", 10000.0, 477_750_000.0),
                     ("2026-09-11T19:07:51", 10000.0, 397_750_000.0),
                     ("2026-09-14T20:15:01", 10000.0, 397_750_000.0),
                     ("2026-10-09T23:30:07", 10000.0, 397_750_000.0)]}
    dgc = ev("DGC", "2026-09-11", "2026-09-14", 8000.0)
    rc, txt = run(table(("DGC", "10.000", "−29,25%"), ("PVT", "2.071", "+46,10%")),
                  P_DGC, [dgc], S_DGC, excl={"DGC"})
    check("CA3: DGC −29,25% (thuần giá, thiếu 8.000đ cổ tức) ⇒ CHẶN", rc, 1)
    check("CA3: … kỳ vọng in ra là −13,34%", "-13.34" in txt, True)
    rc, txt = run(table(("DGC", "10.000", "−13,34%"), ("PVT", "2.071", "+46,10%")),
                  P_DGC, [dgc], S_DGC, excl={"DGC"})
    check("CA3: DGC −13,34% ⇒ PASS", rc, 0)
    check("CA3: cổng nói ĐÚNG việc nó vừa làm (đã kiểm), không còn câu 'báo cáo không công bố'",
          ("ĐÃ KIỂM dòng bảng công bố tỉ suất của DGC" in txt,
           "báo cáo không công bố tỉ suất từ-ngày-mua" in txt), (True, False))
    check("CA3: DGC đứng NGOÀI tổng tài khoản", f"{2071 * 17248.31:,.0f}" in txt, True)
    check("CA3: dòng DGC được đếm là ĐÃ KIỂM (không rơi vào 'ngoài phạm vi')",
          "Đã kiểm 2 dòng bảng + 0 tỉ suất trong văn xuôi; 0 dòng" in txt, True)
    rc, txt = run(table(("PVT", "2.071", "+46,10%")) + "\nDGC −4,79% trong tuần.\n",
                  P_DGC, [dgc], S_DGC, excl={"DGC"})
    check("CA3: văn xuôi về mã excluded (biến động kỳ) KHÔNG bị kiểm như tỉ suất vị thế", rc, 0)
    check("CA3: không có dòng bảng DGC ⇒ nói 'không thấy dòng bảng', không nói 'đã kiểm'",
          ("không thấy dòng bảng (mã, KL) nào của DGC" in txt, "ĐÃ KIỂM" in txt), (True, False))

    print("  -- CA 4: TPB — tiền 500đ + thưởng 15% cùng ex-date; mọi số về KL đang giữ")
    P_TPB = {"TPB": (30.0, 14173.913, 11450.0)}
    S_TPB = {"TPB": [("2026-09-30T19:30:06", 200.0, 200 * 16800.0),
                     ("2026-10-01T19:03:01", 230.0, 230 * 14173.913),
                     ("2026-10-02T09:52:33", 30.0, 30 * 14173.913),
                     ("2026-10-09T23:30:08", 30.0, 30 * 14173.913)]}
    tpb = ev("TPB", "2026-10-01", "2026-10-02", 500.0, mult=1.15, frame=1.15)
    out, mism, extra = run("", P_TPB, [tpb], S_TPB, direct=True)
    check("CA4: cổ tức/cp trên KL đang giữ = 500/1,15 = 434,78 (KHÔNG phải 500)",
          round(out["TPB"], 4), 434.7826)
    pct, _pl, raw = expected_pct(30, 14173.913, 11450.0, out["TPB"])
    check("CA4: giá vốn thô/cp = 16.800/1,15 = 14.608,70 (KHÔNG phải 14.674)", round(raw, 2), 14608.7)
    check("CA4: tỉ suất kỳ vọng = −18,79%", round(pct, 2), -18.79)
    check("CA4: bước 'tiền + thưởng' của broker khớp sự kiện ⇒ không chặn", extra["blockers"], {})
    rc, txt = run(table(("TPB", "30", "−18,79%")), P_TPB, [tpb], S_TPB, label="SpaceX")
    check("CA4: báo cáo −18,79% ⇒ PASS", rc, 0)
    rc, txt = run(table(("TPB", "30", "−18,50%")), P_TPB, [tpb], S_TPB, label="SpaceX")
    check("CA4: −18,50% ⇒ LỆCH", rc, 1)
    tpb_bad = ev("TPB", "2026-10-01", "2026-10-02", 500.0, mult=1.20, frame=1.20)
    out, mism, extra = run("", P_TPB, [tpb_bad], S_TPB, direct=True)
    check("CA4: sự kiện khai hệ số ×1,20 nhưng broker credit ×1,15 ⇒ chặn",
          list(extra["blockers"]), ["TPB"])

    print("  -- cùng lớp: mua thêm SAU ex-date pha loãng cổ tức/cp; vị thế đóng rồi mở lại")
    c0, c1 = 2400 * 25850.0, 2400 * 24850.0
    S_MBB = {"MBB": [("2026-07-08T15:00:15", 2400.0, c0), ("2026-07-09T15:00:19", 2400.0, c1),
                     ("2026-07-20T15:00:00", 3000.0, c1 + 600 * 24000.0),
                     ("2026-07-30T15:00:00", 1500.0, (c1 + 600 * 24000.0) / 2)]}
    mbb = ev("MBB", "2026-07-08", "2026-07-09", 1000.0)
    cp_now = (c1 + 600 * 24000.0) / 3000.0
    out, mism, extra = run("", {"MBB": (1500.0, cp_now, 22000.0)}, [mbb], S_MBB, direct=True)
    check("600cp mua SAU ex-date không hưởng ⇒ cổ tức/cp = 1.000 × 2.400/3.000 = 800",
          round(out["MBB"], 6), 800.0)
    # đối chứng độc lập: giá vốn thô bình quân gia quyền tính THẲNG từ các lệnh mua
    raw_true = (2400 * 25850.0 + 600 * 24000.0) / 3000.0
    check("… và giá vốn thô dựng lại = bình quân gia quyền của CHÍNH các lệnh mua",
          round(expected_pct(1500, cp_now, 22000.0, out["MBB"])[2], 6), round(raw_true, 6))
    S_RE = {"MBB": [("2026-07-08T15:00:15", 2400.0, c0), ("2026-07-09T15:00:19", 2400.0, c1),
                    ("2026-07-15T15:00:00", 0.0, 0.0), ("2026-08-03T15:00:00", 500.0, 500 * 23000.0),
                    ("2026-08-04T15:00:00", 500.0, 500 * 23000.0)]}
    out, mism, extra = run("", {"MBB": (500.0, 23000.0, 22000.0)}, [mbb], S_RE, direct=True)
    check("bán hết rồi mua lại ⇒ cổ tức của đợt nắm giữ CŨ không cộng vào vị thế mới",
          (out, extra["blockers"]), ({}, {}))

    print("  -- mã có chữ số (TV1) phải được đọc")
    P_TV1 = {"TV1": (2300.0, 18647.8261, 19300.0)}
    S_TV1 = {"TV1": [("2026-10-05T04:55:53", 2300.0, 2300 * 20147.8261),
                     ("2026-10-06T20:15:02", 2300.0, 2300 * 18647.8261),
                     ("2026-10-09T23:30:08", 2300.0, 2300 * 18647.8261)]}
    tv1 = ev("TV1", "2026-10-06", "2026-10-07", 1500.0)
    rc, txt = run(table(("TV1", "2.300", "+2,86%")), P_TV1, [tv1], S_TV1, label="SpaceX")
    check("TV1: dòng bảng được ĐỌC và kiểm (bản cũ regex [A-Z]{3} bỏ qua)",
          (rc, "Đã kiểm 1 dòng bảng" in txt), (0, True))
    check("TV1: không còn câu sai 'CÓ cổ tức nhưng báo cáo không công bố tỉ suất riêng'",
          "báo cáo không công bố tỉ suất riêng" in txt, False)
    rc, txt = run(table(("TV1", "2.300", "+10,47%")), P_TV1, [tv1], S_TV1, label="SpaceX")
    check("TV1: số sai +10,47% ⇒ CHẶN (bản cũ: lọt vì dòng không được đọc)", rc, 1)
    check("văn xuôi 'TV1 +2,86%' cũng được nhận là tỉ suất",
          PROSE_RE.findall("lãi TV1 +2,86% từ ngày mua"), [("TV1", "+2,86")])
    check("'MA20 +1%' KHÔNG bị nhận nhầm là mã", PROSE_RE.findall("MA20 +1,0%"), [])

    print("  -- bảng vị thế phải được ĐỌC dù tiêu đề cột viết kiểu nào; không đọc được thì CHẶN")

    def scan(header, *rows):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
            fh.write(f"| {' | '.join(header)} |\n|{'---|' * len(header)}\n"
                     + "".join(f"| {' | '.join(r)} |\n" for r in rows))
        try:
            return _scan_tables(fh.name)
        finally:
            os.unlink(fh.name)
    # tiêu đề THẬT của báo cáo tuần 28/09→02/10 (đã gửi): cột tỉ suất tên `Lãi/lỗ`, không có `%`
    H_SENT = ["Mã", "KL", "Giá vốn", "Giá 02/10", "Giá trị thị trường", "% NAV", "Lãi/lỗ"]
    check("tiêu đề `Lãi/lỗ` KHÔNG có `%`, ô `+32,11%` ⇒ dòng được đọc (bản cũ: 0 dòng, PASS rỗng)",
          scan(H_SENT, ["DRI", "3.700", "12.262", "16.200", "59.940.000", "6,14", "+32,11%"]),
          ([("DRI", 3700.0, 32.11)], []))
    check("cùng tiêu đề `Lãi/lỗ` nhưng ô là SỐ TIỀN ⇒ không đọc thành tỉ suất, không chặn",
          scan(["Mã", "KL", "Lãi/lỗ"], ["DRI", "3.700", "+14.570.000"]), ([], []))
    check("tiêu đề `Tỷ suất` (chữ ỷ) đứng TRƯỚC cột tiền cùng nhóm tên (`Lỗ (VND)`) — báo cáo "
          "tháng 08 ⇒ đọc đúng cột có `%`",
          scan(["Mã", "Khối lượng", "Tỷ suất", "Lỗ (VND)"], ["TPB", "500", "−12,80%", "−1.075.000đ"]),
          ([("TPB", 500.0, -12.8)], []))
    check("tiêu đề `% lỗ` ⇒ dòng được đọc",
          scan(["Mã", "qty", "% lỗ", "VND"], ["TPB", "500", "−12,80%", "−1.075.000đ"]),
          ([("TPB", 500.0, -12.8)], []))
    check("cột KL tên `qty` (báo cáo tháng 08 gộp) ⇒ dòng được đọc",
          scan(["Mã", "qty", "% lãi", "VND"], ["PVT", "3.500", "+18,13%", "+10.850.000đ"]),
          ([("PVT", 3500.0, 18.13)], []))
    # tiêu đề THẬT của báo cáo tuần 27→31/07: tỉ suất nằm ở cột `% tổng`, cột `Lãi/lỗ do giá` là tiền
    H_0727 = ["Mã", "KL", "Giá vốn thật", "Lãi/lỗ do giá", "% tổng", "Nhóm"]
    check("ô tỉ suất có dấu ở cột cổng KHÔNG nhận ra (`% tổng`) ⇒ báo là điểm mù, không bỏ im lặng",
          scan(H_0727, ["SIP", "1.700", "47.059", "**+1.770.000**", "+2,2%", "CAPIT"]),
          ([], [(3, "SIP", "% tổng", "+2,2%")]))
    check("ô có dấu ở cột TỶ TRỌNG (`% NAV`) hay ô không dấu ⇒ KHÔNG phải điểm mù",
          scan(["Mã", "KL", "% NAV", "Δ % NAV", "% tổng"], ["SIP", "1.700", "8,42", "+0,50%", "2,2%"]),
          ([], []))
    rc, txt = run("## 3.5 Danh mục\n\n| Mã | KL | Giá vốn | % tổng |\n|---|---:|---:|---:|\n"
                  "| TV1 | 2.300 | x | +2,86% |\n", P_TV1, [tv1], S_TV1, label="SpaceX")
    check("… và cổng CHẶN (rc=1) báo cáo có ô tỉ suất nằm ngoài tầm kiểm, nêu đúng cột",
          (rc, "cột '% tổng'" in txt), (1, True))

    print("  -- cửa sổ tra sự kiện phủ HẾT sổ broker; giá thô khi Close đã bị điều chỉnh hồi tố")
    tmp = tempfile.mkdtemp(prefix="rrg_lb_")
    keep_dir = g["EXEC_DIR"]
    try:
        open(os.path.join(tmp, "dnse_raw_2026-07-06.jsonl"), "w").close()
        g["EXEC_DIR"] = tmp
        check("chốt 01/12: cửa sổ lùi tới ngày đầu sổ broker (06/07), KHÔNG chỉ 120 ngày (03/08)",
              _lookback_start("2026-12-01"), "2026-07-06")
        check("chốt 01/08: sàn 120 ngày vẫn giữ khi nó sớm hơn", _lookback_start("2026-08-01"),
              "2026-04-03")
    finally:
        g["EXEC_DIR"] = keep_dir
        os.unlink(os.path.join(tmp, "dnse_raw_2026-07-06.jsonl"))
        os.rmdir(tmp)
    check("TV1 phiên 06/10 CÓ sự kiện sau (ex 07/10) ⇒ dùng `Price` thô 20.600, không phải Close 19.110",
          pick_raw_price(19110.0, 20600.0, True), (20600.0, "Price"))
    check("không có sự kiện sau ⇒ giữ `Close` (DRI 08/10: giá khớp cuối 16.700)",
          pick_raw_price(16700.0, 16600.0, False), (16700.0, "Close"))


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
