#!/usr/bin/env python3
"""treasury_buyback_window_monitor.py — monitor WARN-ONLY: mua cổ phiếu quỹ đã hoàn tất mà chưa
thấy dòng giảm niêm yết (AIS step-down) theo sau trong `tav2_bq.corporate_action`.

VÌ SAO TỒN TẠI (job `Taylor_20260917_160652`, user duyệt 2026-09-17 23:05 ICT)
------------------------------------------------------------------------------
Pháp lý (Wendy/legal-vn, có trích nguồn): Điều 112.5 Luật DN 2020 + Điều 36.1(a) Luật CK 2019
(hiệu lực 2021-01-01) — mua lại cổ phiếu quỹ THÔNG THƯỜNG phải đăng ký giảm vốn điều lệ trong 10
ngày kể từ ngày thanh toán xong. Ngoại lệ: cổ phiếu mua lại từ ESOP (Luật 56/2024/QH15 + NĐ
245/2025) được giữ làm quỹ, không giảm vốn.

Kiến trúc đã chốt: KHÔNG overlay trừ OShares, KHÔNG sửa `oshares_live.py`. Gap post-2021 phải TỰ
ĐÓNG qua AIS "Giảm niêm yết" mới — `oshares_live.py` đã đọc đúng AIS đó. Monitor
này chỉ canh trường hợp gap KHÔNG tự đóng. Cùng lớp với `corp_action_feed_canary.py`: chỉ ĐỌC BQ,
in log, post topic `architecture` khi có WARN; không ghi state, không chặn cổng publish nào.

LOGIC
-----
1. Sự kiện = `treasury_news.action_type = 'buy_done'`, `public_date` trong
   [`SCOPE_START`=2021-01-01, hôm nay], gộp theo (ticker, public_date) — nhiều dòng tin cùng ngày
   là nhiều nguồn cho MỘT sự kiện (bẫy (4) registry). Case pre-2021 (VRE/SRF MANUAL_FILL) nằm
   ngoài phạm vi bằng chính bộ lọc ngày này.
2. "Step-down" (giảm niêm yết) = dòng AIS `executed` có `shares_delta < 0`; `shares_delta` NULL ⇒
   tiêu đề chứa "giảm niêm yết". KHÔNG so `shares_total_after` với AIS liền trước (thiết kế ban
   đầu) — đo 2026-09-17 cho thấy chuỗi đó không đơn điệu theo ngày: ELC 2025-04-17 +4,16tr →
   87.453.925 rồi 2025-04-28 +1tr → 83.290.077 (giảm tổng dù Δ dương ⇒ "đóng" giả 4 sự kiện ELC);
   CMG/PSD cùng dạng; ngược lại VHM AIS −246.955.484 bị BỎ SÓT vì dòng trước ghi tổng 4.354.367
   (sai đơn vị). Dấu Δ khớp 30/30 dòng "Giảm niêm yết", 0 xung đột.
3. Sự kiện ĐÓNG khi có step-down với ngày trong [`public_date`, `public_date`+`MATCH_MAX_DAYS`].
   Chưa đóng: tuổi ≤ `CLOSE_WINDOW_DAYS` ⇒ trong cửa sổ, không báo; tuổi trong
   (`CLOSE_WINDOW_DAYS`, `MATCH_MAX_DAYS`] ⇒ WARN (post); tuổi > `MATCH_MAX_DAYS` ⇒ STALE — bằng
   chứng đã cố định, chỉ in log + đếm ở header post (không lặp danh sách cũ mỗi ngày; danh sách
   một lần nằm trong report job `Taylor_20260917_160652`).
4. WARN nêu: ticker, ngày buy_done, số ngày đã trôi, ngưỡng, AIS gần nhất TRƯỚC và SAU ngày đó
   (nếu có), và dấu hiệu nguồn gốc khác thông thường tìm được trong tiêu đề/tóm tắt tin. KHÔNG
   kết luận "vi phạm" — chỉ sự kiện + số liệu (§29).

NGƯỠNG `CLOSE_WINDOW_DAYS` = 45 ngày lịch (đề xuất trong dispatch: 10 ngày luật định + đệm).
⚠️ ĐO 2026-09-17: trong 29 sự kiện có step-down ≤365 ngày, độ trễ buy_done→AIS giảm =
22,28,35,38,39,43 | 56,67,72,72,76,79,81,87,87,90,97,97 | 133,154,161,162,169,187,196,244,255,277,
320 — chỉ 6/29 ≤45, 16/29 ≤90, 23/29 ≤180. Tức ở 45 ngày phần lớn WARN là "đang chờ sở cập nhật",
không phải gap treo; chọn giá trị là quyết định của Mike/user. Chỉnh hằng số này, không rải số.

HẠN CHẾ ĐÃ BIẾT (nói thẳng, không che)
--------------------------------------
(H1) ESOP KHÔNG phân biệt được bằng DỮ LIỆU CÓ CẤU TRÚC: `treasury_news` không có cột nguồn gốc
     (`category` NULL và `matched_keyword`='BUYBACK' ở 100% buy_done post-2021; đo 2026-09-17),
     `corporate_action` không có dòng buy_done. Monitor KHÔNG tự loại trừ sự kiện nào — chỉ GẮN
     CỜ `ORIGIN_HINT_RE` (từ khoá tiêu đề: ESOP / người lao động / CBNV / nghỉ việc / thu hồi / ưu
     đãi / lẻ...) vào dòng WARN để người đọc tự đánh giá. Heuristic văn bản, không phải field.
(H2) Một step-down đóng MỌI buy_done trong `MATCH_MAX_DAYS` trước nó (không ghép 1-1 theo số
     lượng vì phần lớn dòng buy_done thiếu `shares_delta`). Hai đợt mua gần nhau mà chỉ một đợt
     giảm vốn ⇒ đợt kia bị coi là đóng (false negative có thể). Độ trễ đóng in log (`closed_late`).
(H4) Ngày AIS là ngày hiệu lực NIÊM YẾT ở sở, không phải ngày đăng ký giảm vốn ở Sở KH&ĐT mà luật
     đếm 10 ngày ⇒ AIS muộn KHÔNG chứng minh chậm đăng ký. Monitor chỉ đo "feed đã phản ánh chưa".
(H3) Tin "Đính chính"/"Công văn UBCKNN nhận được báo cáo" cũng mang action_type buy_done ⇒ một đợt
     mua có thể thành 2 dòng WARN ngày gần nhau. Không gộp tự động (không có khoá sự kiện chung).

Mã thoát: 0 = không WARN (1 dòng log) · 1 = có WARN (đã post) · 2 = monitor lỗi (đã post, trích
lỗi thật) · 3 = post Discord thất bại (`NOTIFY_FAILED`).

Dùng:  python3 mike/bin/treasury_buyback_window_monitor.py [--dry-run] [--asof YYYY-MM-DD]
Selfcheck: `treasury_buyback_window_monitor_selfcheck.py` (hermetic, không BQ).
Registry: `mike/kb/data_registry/price-volume/treasury_news_buyback.md`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from wc_paths import find_wc_root  # noqa: E402

WC_ROOT = find_wc_root(__file__)
if WC_ROOT not in sys.path:
    sys.path.insert(0, WC_ROOT)

# Cùng lý do corp_action_feed_canary: đọc BQ SỐNG, không cache T-1 của wc_env.sh.
os.environ.pop("BQ_LOCAL_CACHE", None)

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
TREASURY_TABLE = "lithe-record-440915-m9.tav2_bq.treasury_news"
CA_TABLE = "lithe-record-440915-m9.tav2_bq.corporate_action"
NOTIFY_TOPIC = "architecture"

SCOPE_START = dt.date(2021, 1, 1)   # hiệu lực Luật DN 2020 + Luật CK 2019
CLOSE_WINDOW_DAYS = 45              # 10 ngày luật định + đệm độ trễ niêm yết/vendor
MATCH_MAX_DAYS = 365                # step-down xa hơn coi là không thuộc đợt mua này (đo: lag
                                    # ≤365 ngày dày tới 320, sau đó nhảy 395/402/913/1713)
ORIGIN_HINT_RE = re.compile(
    r"esop|người lao động|cbnv|cbcnv|cán bộ|nhân viên|nghỉ việc|thu hồi|ưu đãi|cổ phiếu lẻ"
    r"|phát sinh từ",
    re.IGNORECASE)


# ── SQL ───────────────────────────────────────────────────────────────────────────────────
def sql_events(today):
    return (f"/* treasury_window:events */\nSELECT ticker, CAST(public_date AS STRING) AS d, id, "
            f"title, short_content FROM `{TREASURY_TABLE}` WHERE action_type = 'buy_done' "
            f"AND public_date BETWEEN DATE '{SCOPE_START.isoformat()}' "
            f"AND DATE '{today.isoformat()}'")


def sql_ais(today):
    return (f"/* treasury_window:ais */\nSELECT ticker, id, "
            f"CAST(COALESCE(effective_date, public_date) AS STRING) AS d, "
            f"shares_delta, shares_total_after, event_title_vi AS title FROM `{CA_TABLE}` "
            f"WHERE event_code = 'AIS' AND event_status = 'executed' "
            f"AND COALESCE(effective_date, public_date) <= DATE '{today.isoformat()}' "
            f"AND ticker IN (SELECT DISTINCT ticker FROM `{TREASURY_TABLE}` "
            f"WHERE action_type = 'buy_done' "
            f"AND public_date >= DATE '{SCOPE_START.isoformat()}')")


# ── logic thuần ───────────────────────────────────────────────────────────────────────────
def _int(v):
    return None if v in (None, "") else int(v)


def group_events(rows):
    """{(ticker, date): {"n": số dòng tin, "hint": từ khoá nguồn gốc khác hoặc None, "title"}}."""
    out = {}
    for r in rows:
        key = (r["ticker"], dt.date.fromisoformat(r["d"]))
        if key[1] < SCOPE_START:  # phòng thủ ngoài WHERE của SQL: pre-2021 ngoài phạm vi
            continue
        ev = out.setdefault(key, {"n": 0, "hint": None, "title": r.get("title") or ""})
        ev["n"] += 1
        m = ORIGIN_HINT_RE.search(f"{r.get('title') or ''} {r.get('short_content') or ''}")
        if m and ev["hint"] is None:
            ev["hint"] = m.group(0)
            ev["title"] = r.get("title") or ""
    return out


def ais_series(rows):
    """{ticker: [ais...]} theo ngày, mỗi phần tử gắn `step_down` (Δ<0 / tiêu đề giảm niêm yết)."""
    by = {}
    for r in rows:
        by.setdefault(r["ticker"], []).append({
            "id": r.get("id"), "d": dt.date.fromisoformat(r["d"]), "title": r.get("title") or "",
            "delta": _int(r.get("shares_delta")), "total": _int(r.get("shares_total_after"))})
    for seq in by.values():
        seq.sort(key=lambda a: (a["d"], a["id"] or ""))
        for a in seq:
            a["step_down"] = (a["delta"] < 0 if a["delta"] is not None
                              else "giảm niêm yết" in a["title"].lower())
    return by


def evaluate(today, event_rows, ais_rows):
    events = group_events(event_rows)
    series = ais_series(ais_rows)
    res = {"scope_events": len(events), "scope_tickers": len({t for t, _ in events}),
           "open_in_window": [], "closed": [], "warn": [], "stale": []}
    for (t, d), ev in sorted(events.items()):
        seq = series.get(t, [])
        close = next((a for a in seq if a["step_down"]
                      and 0 <= (a["d"] - d).days <= MATCH_MAX_DAYS), None)
        elapsed = (today - d).days
        item = {"ticker": t, "date": d, "elapsed": elapsed, "n_news": ev["n"], "hint": ev["hint"],
                "title": ev["title"],
                "ais_before": next((a for a in reversed(seq) if a["d"] < d), None),
                "ais_after": next((a for a in seq if a["d"] >= d), None), "close": close}
        if close is not None:
            item["lag"] = (close["d"] - d).days
            res["closed"].append(item)
        elif elapsed > MATCH_MAX_DAYS:
            res["stale"].append(item)
        elif elapsed > CLOSE_WINDOW_DAYS:
            res["warn"].append(item)
        else:
            res["open_in_window"].append(item)
    return res


def _fmt_ais(a):
    if a is None:
        return "không có"
    tot = "?" if a["total"] is None else f"{a['total']:,}"  # tổng vendor, chỉ để đọc
    dl = "?" if a["delta"] is None else f"{a['delta']:+,}"
    return f"{a['d']} Δ{dl} → {tot}{' (step-down)' if a['step_down'] else ''}"


def render_warn(item):
    s = (f"• {item['ticker']} buy_done {item['date']} — {item['elapsed']} ngày > ngưỡng "
         f"{CLOSE_WINDOW_DAYS}; AIS trước: {_fmt_ais(item['ais_before'])}; "
         f"AIS sau: {_fmt_ais(item['ais_after'])}")
    if item["n_news"] > 1:
        s += f"; {item['n_news']} dòng tin"
    if item["hint"]:
        s += f"; ⚑ tiêu đề có '{item['hint']}' (có thể ESOP/ngoại lệ — chưa loại trừ)"
    return s


def render(today, res):
    w = res["warn"]
    head = (f"🏦 treasury_buyback_window_monitor {today}: {len(w)} sự kiện buy_done quá "
            f"{CLOSE_WINDOW_DAYS} ngày chưa thấy AIS giảm niêm yết — phạm vi "
            f"{res['scope_events']} sự kiện/{res['scope_tickers']} mã từ {SCOPE_START} "
            f"(đã đóng {len(res['closed'])}, trong cửa sổ {len(res['open_in_window'])}, STALE >"
            f"{MATCH_MAX_DAYS}d chỉ ghi log {len(res['stale'])}). "
            f"WARN-ONLY, không chặn gì. Nguồn gốc ESOP KHÔNG phân biệt được bằng field — "
            f"⚑ chỉ là từ khoá tiêu đề.")
    return "\n".join([head] + [render_warn(i) for i in w])


def summary_line(today, res):
    late = [i for i in res["closed"] if i["lag"] > CLOSE_WINDOW_DAYS]
    return (f"treasury_buyback_window_monitor {today}: scope={res['scope_events']} sự kiện/"
            f"{res['scope_tickers']} mã, closed={len(res['closed'])} (closed_late>"
            f"{CLOSE_WINDOW_DAYS}d={len(late)}: "
            + ", ".join(f"{i['ticker']}@{i['date']}+{i['lag']}d" for i in late)
            + f"), open_in_window={len(res['open_in_window'])}, warn={len(res['warn'])}, "
            f"stale>{MATCH_MAX_DAYS}d={len(res['stale'])}"
            + "".join("\n  STALE " + render_warn(i)[2:] for i in res["stale"]))


# ── chạy ─────────────────────────────────────────────────────────────────────────────────
def default_runner(sql):
    from corp_action_lib import bq
    return bq(sql, timeout=180)


def default_notifier(msg):
    """(ok, detail). Topic theo TÊN qua registry `kb/discord_channels.json`."""
    try:
        p = subprocess.run([os.path.join(HERE, "notify_thread.sh"), msg, NOTIFY_TOPIC],
                           capture_output=True, text=True, timeout=90)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    return p.returncode == 0, f"rc={p.returncode} stderr={p.stderr.strip()[-300:]}"


def main(argv=None, runner=default_runner, notifier=default_notifier, today=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="in message, không post Discord")
    ap.add_argument("--asof", help="YYYY-MM-DD thay cho hôm nay ICT (chạy lại/kiểm thử)")
    a = ap.parse_args(argv)
    today = today or (dt.date.fromisoformat(a.asof) if a.asof
                      else dt.datetime.now(ICT).date())
    try:
        res = evaluate(today, runner(sql_events(today)), runner(sql_ais(today)))
    except Exception as e:  # monitor tự hỏng ⇒ báo kèm lỗi thật, không đoán nguyên nhân
        msg = (f"🛠️ treasury_buyback_window_monitor {today}: MONITOR KHÔNG CHẠY ĐƯỢC — "
               f"{type(e).__name__}: {str(e).strip()[-600:]}")
        rc = 2
    else:
        print(f"{dt.datetime.now(ICT):%Y-%m-%d %H:%M} " + summary_line(today, res))
        if not res["warn"]:
            return 0
        msg, rc = render(today, res), 1
    print(msg)
    if a.dry_run:
        print("(dry-run: không post Discord)")
        return rc
    ok, detail = notifier(msg)
    if not ok:
        print(f"NOTIFY_FAILED topic={NOTIFY_TOPIC} {detail}")
        return 3
    return rc


if __name__ == "__main__":
    sys.exit(main())
