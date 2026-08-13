#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""corp_action_daily.py — cập nhật HÀNG NGÀY cổ tức tiền mặt + Oshares từ `tav2_bq.corporate_action`.

VÌ SAO TỒN TẠI — VÀ VÌ SAO KHÔNG CÓ LLM NÀO TRONG VÒNG LẶP
----------------------------------------------------------
User nêu đúng mối lo: một con số tài chính do LLM tính lại mỗi ngày là một con số KHÔNG tái lập
được. Thoả thuận: LLM viết code MỘT LẦN, cron chạy lại ĐÚNG file này mỗi ngày. Không có bước
gọi mô hình nào ở runtime — mọi phép tính đều là hàm Python thuần đã qua quant-skeptic:

  * `oshares_live.oshares_at()`  — số CP lưu hành point-in-time (CONFIRMED vòng 2, 2026-08-13)
  * `oshares_live._roll()`       — cùng một hàm lăn sự kiện, dùng lại cho bất biến §4 dưới đây
  * `dividend_adjusted_return.bq_corp_action()` — dedup DIV/ISS tại (mã, ex-date)
  * `corp_action_lib.{events, feed_freshness, is_price_adjusting}` — reader + taxonomy

File này KHÔNG chứa một công thức tài chính mới nào. Nó là **lịch trình + cổng chặn + đối soát**:
nó quyết định NGÀY NÀO chạm mã nào, và từ chối công bố khi bằng chứng không đủ.

LỊCH — sự kiện tự chọn ngày của nó, ta không chọn hộ
-----------------------------------------------------
Mỗi mã được cập nhật vào ĐÚNG ngày sự kiện của chính nó, không phải theo một lịch quét đều:

  * sự kiện CÓ điều chỉnh giá (DIV tiền mặt, cổ tức CP, thưởng, quyền mua) → `exright_date`
  * sự kiện KHÔNG điều chỉnh giá (ESOP, riêng lẻ, chuyển đổi TP, đấu giá, sáp nhập) → những
    dòng ISS này VẪN có `exright_date` trong bảng (đó là ngày chốt của đợt phát hành, dù giá
    không nhảy — đo thật HAH 2026-07-28, tỉ số 1,000000 → 1,000000), nên chúng cũng vào trigger
    theo `exright_date`; còn ngày CP mới thực sự vào lưu hành là `AIS.effective_date`, trễ tới
    ~7 tuần (Bẫy 1 của registry) và được bắt như một trigger RIÊNG.

Nói cách khác: một sự kiện chạm hệ thống này HAI lần — lúc ex-right (ước lượng, `ISS_ESTIMATE`)
và lúc AIS hiệu lực (số chính thức, `AIS_EXACT`). Cả hai lần đều được ghi lại, nên khoảng giữa
hai lần đó — đúng cái khoảng mà `ticker_financial.OShares` sai — là khoảng có số.

SÁU LỚP, KHÔNG LỚP NÀO ĐƯỢC BỎ
-------------------------------
1. **Cron Python thuần** — output là snapshot CÓ NGÀY TRONG TÊN
   (`data/corp_action_daily/corp_action_daily_<asof>.json`), ghi atomic. Không bao giờ ghi đè một
   tên canonical (§8 coding_guidelines): chạy lại cùng ngày cho cùng file, không đụng ngày khác.
2. **Đối soát chéo mỗi ngày** giữa `oshares_live` (corp-action) và `ticker_financial.OShares`
   (bq_admin) — xem §ĐỐI SOÁT dưới. Lệch quá ngưỡng ⇒ CẢNH BÁO kèm CẢ HAI số. Script này
   **không bao giờ tự chọn số nào đúng**.
3. **Selfcheck là CỔNG CHẶN chạy TRƯỚC publish** — chạy lại toàn bộ bộ hồi quy hiện có của
   `corp_action_lib` + `oshares_live` như tiến trình con. Fail bất kỳ ca nào ⇒ KHÔNG publish,
   ghi `*_FAILED.json`, báo lỗi. Không đoán.
4. **Bất biến số học** — so với snapshot tốt gần nhất: Oshares chỉ được đổi ĐÚNG BẰNG phần các
   sự kiện giữa hai ngày giải thích được. Ngưỡng KHÔNG phải "%/ngày" cố định (một đợt thưởng
   1:1 là +100% hoàn toàn hợp lệ, còn một cú +3% không sự kiện thì sai) — ngưỡng là **sai số so
   với kỳ vọng đã lăn sự kiện**, xem §NGƯỠNG.
5. **Freshness gate trên chính `corporate_action`** (Bẫy 2 của registry) — bảng không refresh ⇒
   không coi là dữ liệu mới, cảnh báo phân tầng theo chuỗi ngày im lặng (chống alert-fatigue).
6. **Cảnh báo PROACTIVE** cho mã ĐANG GIỮ THẬT có sự kiện trong ≤10 ngày tới — post TRƯỚC khi
   sự kiện xảy ra, vào kênh tra qua `kb/discord_channels.json` (không hardcode ID).

ĐỐI SOÁT — vì sao không so thẳng hai số hôm nay
-----------------------------------------------
So `oshares_live(asof)` với `ticker_financial.OShares` mới nhất là so hai thứ ở HAI THỜI ĐIỂM
khác nhau: dòng quý có thể cũ 3 tháng và lệch là ĐÚNG (đó chính là lý do module này tồn tại).
Phép so có nghĩa là so tại CÙNG một ngày — ngày của chính dòng quý:

    oshares_at(ticker, q.time)  ↔  q.OShares

Hai nguồn cùng khẳng định về cùng một thời điểm; lệch quá ngưỡng ⇒ hoặc dòng quý đã bị RESTATE
(đúng cơ chế đã đo: 2.667 dòng/576 mã mang số của một AIS hiệu lực SAU đó), hoặc mô hình lăn sự
kiện sai. Không phân biệt được từ phía này ⇒ **báo cả hai số, cả hai ngày, không chọn**.

Lớp thứ hai của đối soát là `rejected_anchors` do chính `oshares_live` sinh ra: cổng giải thích
bên trong nó đã âm thầm loại một dòng quý mâu thuẫn. Im lặng là cái ta không muốn — mỗi lần loại
đều được nâng lên thành một dòng cảnh báo đếm được theo ngày.

NGƯỠNG — hai con số, và vì sao đúng chúng
------------------------------------------
* **0,1% (`oshares_live.EXPLAIN_TOL`, import chứ không chép lại)** = "bằng nhau về mặt vật chất"
  cho MỌI phép so số CP trong file này. Neo bằng số đo, không phải cảm giác: sai số hợp lệ lớn
  nhất từng đo là làm tròn CP lẻ của FPT **0,0013%**; ca RESTATE thật của HAH là **10,1%**.
  0,1% nằm giữa, cách mỗi đầu hai bậc độ lớn. Dùng CHUNG một hằng số với cổng giải thích bên
  trong `oshares_live` là có chủ đích: hai ngưỡng khác nhau cho cùng khái niệm "bằng nhau" là
  cách sinh ra hai kết luận trái nhau trên cùng dữ liệu.
* **`SYSTEMIC_MIN = 3` mã VÀ `SYSTEMIC_FRAC = 0,05`** = ranh giới "một sự cố" ↔ "feed hỏng".
  Một mã vi phạm là chuyện thường (vendor đính chính một sự kiện) ⇒ giấu số của RIÊNG mã đó,
  phần còn lại vẫn publish. Nhiều mã vi phạm CÙNG NGÀY thì cái sai gần như chắc chắn nằm ở
  nguồn, không ở mã ⇒ không publish gì cả. Sàn tuyệt đối 3 mã để một track-set nhỏ (5 mã) không
  bị 1 vi phạm đơn lẻ đẩy thành "feed hỏng" chỉ vì 1/5 = 20% > 5%.

BA LỚP DỮ LIỆU, BA VINTAGE KHÁC NHAU — công bố hết, đừng để người đọc tự đoán
-----------------------------------------------------------------------------
* `corporate_action`  — vendor nạp ~22:2x ICT hôm trước (đo thật 2026-08-12 15:22→15:48 UTC).
* vị thế thật         — `data/execution_logs/active_nav_<label>.json`, cron 20:15 ICT hôm trước.
* `ticker_financial`  — theo quý, trễ tới ~3 tháng theo thiết kế.
Mỗi vintage đi kèm số trong output; cron chạy 07:30 ICT nên cả ba đều là "tối qua hoặc cũ hơn",
KHÔNG có thành phần nào cần dữ liệu trong phiên (§6: same-day thì phải hỏi DNSE, không phải BQ —
file này cố tình không hỏi câu nào cần same-day).

CÁI FILE NÀY KHÔNG LÀM
----------------------
* Không tính tỉ suất lợi nhuận. Cổ tức ở đây là **GỘP, nguồn vendor, CHƯA đối soát tiền broker**
  — §21 vẫn buộc mọi tỉ suất per-position đi qua `dividend_adjusted_return.py` (tiền thật của
  broker là nguồn số chính thức). Số ở đây dùng để BÁO TRƯỚC và để đối soát, không để báo cáo.
* Không đặt lệnh, không sửa plan, không đổi sizing. Chỉ đọc + ghi snapshot + báo người.
* Không tắt `update_shares_live.py` (quyết định user 2026-08-13: giữ đường reactive song song).

Usage:
    python3 mike/bin/corp_action_daily.py [--asof YYYY-MM-DD] [--dry-run] [--no-alert]
                                          [--selfcheck] [--lookahead-days 10]
Exit: 0 publish OK · 2 selfcheck gate fail · 3 feed chết · 4 bất biến vi phạm diện rộng · 5 lỗi khác
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

WC_ROOT = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
MIKE = os.path.join(WC_ROOT, "mike")
for _p in (WC_ROOT, os.path.join(MIKE, "bin")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# §11: đây là script PUBLISH — mọi truy vấn phải đi thẳng BQ, không qua cache T-1 mà
# `wc_env.sh` bơm vào env của cron. Pop tại chỗ, KHÔNG sửa `wc_env.sh` (script khác cần nó).
os.environ.pop("BQ_LOCAL_CACHE", None)

from corp_action_lib import events as ca_events, feed_freshness, is_price_adjusting  # noqa: E402
from oshares_live import EXPLAIN_TOL, _dedup_iss, _fetch, _roll, oshares_at  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
OUT_DIR = os.path.join(WC_ROOT, "data", "corp_action_daily")
ACTIVE_NAV_GLOB = os.path.join(WC_ROOT, "data", "execution_logs", "active_nav_*.json")
STATE_PATH = os.path.join(MIKE, "state", "corp_action_daily_state.json")
CHANNEL = "trading_daily"        # TÊN trong kb/discord_channels.json — KHÔNG hardcode ID

# xem §NGƯỠNG trong docstring. EXPLAIN_TOL được IMPORT, không chép lại.
SYSTEMIC_MIN = 3
SYSTEMIC_FRAC = 0.05

# feed coi là CHẾT khi lần nạp gần nhất cũ hơn ngần này (ngày lịch). 5 = nghỉ lễ 4 ngày + 1 ngày
# trượt; quá đó thì "refresh hàng ngày" không còn là mô tả đúng của bảng.
FEED_DEAD_DAYS = 5
# vị thế cũ hơn ngần này thì danh sách mã đang giữ có thể đã sai ⇒ cảnh báo (vẫn dùng, có nhãn).
POS_STALE_DAYS = 5
LOOKAHEAD_DAYS = 10


# ───────────────────────────────────────────────────────────── tiện ích ngày/ghi file

def today_ict() -> str:
    return dt.datetime.now(ICT).date().isoformat()


def prev_trading_day(d: dt.date) -> dt.date:
    """Ngày giao dịch LIỀN TRƯỚC (bỏ T7/CN + lễ). Dùng lại lịch lễ của `trading_bot.vn_market`
    thay vì tự khai một bản thứ hai — hai lịch lễ lệch nhau là một lớp bug không ai đọc ra."""
    from trading_bot.vn_market import is_holiday
    d = d - dt.timedelta(days=1)
    while d.weekday() >= 5 or is_holiday(d):
        d -= dt.timedelta(days=1)
    return d


def _atomic_write_json(path, obj):
    """tmp + os.replace (§5) — bị kill giữa chừng không để lại file dở cho lần chạy sau tin."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, path)


def _read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def snapshot_path(asof, failed=False):
    suffix = "_FAILED" if failed else ""
    return os.path.join(OUT_DIR, f"corp_action_daily_{asof}{suffix}.json")


def prior_snapshot(asof):
    """Snapshot ĐÃ PUBLISH gần nhất trước `asof` (bỏ qua `*_FAILED.json` — một lần chạy hỏng
    không được làm mốc so sánh cho lần sau, đó là cách một lỗi tự hợp thức hoá)."""
    best = None
    for p in sorted(glob.glob(os.path.join(OUT_DIR, "corp_action_daily_*.json"))):
        if p.endswith("_FAILED.json"):
            continue
        d = os.path.basename(p)[len("corp_action_daily_"):-len(".json")]
        if len(d) == 10 and d < asof and (best is None or d > best[0]):
            best = (d, p)
    if not best:
        return None, None
    return best[0], _read_json(best[1])


# ───────────────────────────────────────────────────────────── báo người

def notify(msg, channel=CHANNEL, telegram=False, enabled=True):
    """Discord (+ Telegram khi HIGH). Không bao giờ ném lỗi ra ngoài: kênh báo hỏng thì kết quả
    tính toán vẫn phải được ghi ra đĩa — mất cảnh báo còn hơn mất cả snapshot."""
    if not enabled:
        print(f"[notify:OFF] {msg[:200]}")
        return
    for cmd in ([os.path.join(MIKE, "bin", "notify_thread.sh"), msg, channel],
                *([[os.path.join(MIKE, "bin", "notify.sh"), msg]] if telegram else [])):
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except Exception as exc:                                    # noqa: BLE001
            print(f"[WARN] gửi cảnh báo thất bại ({cmd[0]}): {exc}")


def bus(kind, topic, payload, trace=None):
    cmd = [os.path.join(MIKE, "bin", "append_event.sh"), "Taylor", kind, topic,
           json.dumps(payload, ensure_ascii=False, default=str)]
    if trace:
        cmd.append(trace)
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except Exception as exc:                                        # noqa: BLE001
        print(f"[WARN] ghi bus thất bại: {exc}")


# ───────────────────────────────────────────────────────────── LỚP 3 · cổng selfcheck

def gate_selfcheck(runner=None):
    """Chạy LẠI bộ hồi quy của 2 module nền TRƯỚC khi publish. Trả (ok, chi tiết).

    Vì sao chạy như tiến trình con chứ không import hàm `_selfcheck`: bộ hồi quy đó truy vấn BQ
    thật. Chạy nó ở đây biến "BQ trả lời đúng như hôm nghiệm thu" thành ĐIỀU KIỆN để publish —
    một thay đổi lược đồ/dữ liệu phía vendor sẽ làm cổng đỏ, thay vì âm thầm chảy vào snapshot.
    `runner` chỉ để selfcheck của chính file này bơm kết quả giả vào; production để None.
    """
    targets = [("corp_action_lib", os.path.join(WC_ROOT, "corp_action_lib.py")),
               ("oshares_live", os.path.join(WC_ROOT, "oshares_live.py"))]
    run = runner or (lambda path: subprocess.run(
        [sys.executable, path, "--selfcheck"], capture_output=True, text=True,
        timeout=900, cwd=WC_ROOT))
    out, ok = [], True
    for name, path in targets:
        try:
            r = run(path)
            rc, tail = r.returncode, (r.stdout or "")[-400:]
        except Exception as exc:                                    # noqa: BLE001
            rc, tail = 99, f"lỗi chạy: {exc}"
        out.append({"module": name, "rc": rc, "tail": tail.strip().splitlines()[-1:] or [""]})
        ok = ok and rc == 0
    return ok, out


# ───────────────────────────────────────────────────────────── LỚP 5 · cổng freshness

def gate_freshness(asof, fresh=None):
    """(status, chi tiết) với status ∈ {FRESH, STALE, DEAD}.

    FRESH = lần nạp gần nhất rơi vào HOẶC SAU ngày giao dịch liền trước. Đây là mốc đúng chứ
    không phải "hôm nay": vendor nạp lúc ~22:2x ICT (đo thật 2026-08-12 15:22→15:48 UTC) nên vào
    07:30 ICT hôm sau, dữ liệu tươi nhất có thể có LUÔN mang ngày HÔM QUA. Lấy mốc "hôm nay" sẽ
    báo động giả mỗi sáng; lấy theo ngày GIAO DỊCH trước (không phải ngày lịch trước) thì sáng
    thứ Hai không đỏ vì cuối tuần.
    """
    f = fresh if fresh is not None else feed_freshness()
    raw = (f.get("max_ingested") or "")[:19]
    d_asof = dt.date.fromisoformat(asof)
    try:
        ing_utc = dt.datetime.fromisoformat(raw).replace(tzinfo=dt.timezone.utc)
        ing_ict = ing_utc.astimezone(ICT)
        ing_date = ing_ict.date()
    except Exception:                                               # noqa: BLE001
        return "DEAD", {**f, "reason": f"không đọc được max_ingested={f.get('max_ingested')!r}"}

    age_days = (d_asof - ing_date).days
    detail = {"max_ingested_utc": f.get("max_ingested"),
              "max_ingested_ict": ing_ict.isoformat(timespec="seconds"),
              "max_public_date": f.get("max_public"), "rows": f.get("n"),
              "age_days": age_days, "prev_trading_day": prev_trading_day(d_asof).isoformat()}
    if age_days > FEED_DEAD_DAYS:
        return "DEAD", {**detail, "reason": f"lần nạp gần nhất cũ {age_days} ngày "
                                            f"(> {FEED_DEAD_DAYS}) — bảng không còn refresh"}
    if ing_date >= prev_trading_day(d_asof):
        return "FRESH", detail
    return "STALE", {**detail,
                     "reason": f"chưa có lần nạp nào kể từ phiên {detail['prev_trading_day']}"}


def stale_streak(asof, status, signature, state_path=None):
    """Số ngày liên tiếp feed không nhúc nhích, để phân tầng cảnh báo (chống alert-fatigue).

    Một ngày im lặng là bình thường (không có sự kiện mới nào để nạp — bảng chỉ ~4 dòng/ngày
    trung bình). Năm ngày im lặng là feed chết. Cùng tinh thần phân tầng của
    `dt5g_writer_watch.py`: báo mỗi ngày = không ai đọc nữa đúng hôm cần đọc.
    """
    # phân giải TRONG THÂN HÀM, không làm giá trị mặc định: default được chốt lúc `def` chạy nên
    # gán `cad.STATE_PATH = <tmp>` trong một probe sẽ KHÔNG có tác dụng và probe lặng lẽ ghi đè
    # state production (đã xảy ra thật khi chạy probe ACB 2026-08-13).
    state_path = state_path or STATE_PATH
    st = _read_json(state_path, {}) or {}
    prev_sig, prev_streak = st.get("feed_signature"), int(st.get("stale_streak") or 0)
    streak = 0 if status == "FRESH" else (prev_streak + 1 if signature == prev_sig else 1)
    st.update({"feed_signature": signature, "stale_streak": streak, "last_run": asof})
    _atomic_write_json(state_path, st)
    return streak


# ───────────────────────────────────────────────────────────── track set + vị thế

def read_positions(nav_glob=ACTIVE_NAV_GLOB, asof=None):
    """{label: {"asof":…, "positions": {tk: qty}, "stale_days": n}} từ artifact 20:15 ICT.

    Đọc ARTIFACT chứ không gọi DNSE live có chủ đích: (a) cron 07:30 ICT không cần số trong
    phiên — câu hỏi ở đây là "mã nào ta đang giữ", không phải "giá bao nhiêu"; (b) không kéo
    credential broker vào một job giám sát; (c) mỗi file `active_nav_<label>.json` đã là output
    của `compute_active_nav_all.sh`, tức là danh sách account sống được suy từ chính cái iterator
    chuẩn tắc, không phải một danh sách chép tay lần thứ hai ở đây.

    Vị thế bị loại khỏi rebalancing (`excluded`, vd DGC của ZaloPay) VẪN được giữ trong danh
    sách: ta không giao dịch nó, nhưng ta vẫn SỞ HỮU nó, nên một đợt chốt quyền vẫn phải báo.
    """
    asof = asof or today_ict()
    out = {}
    for path in sorted(glob.glob(nav_glob)):
        d = _read_json(path)
        if not d:
            print(f"[WARN] không đọc được {path}")
            continue
        label = d.get("account") or os.path.basename(path)
        computed = d.get("computed_at") or ""
        try:
            stale = (dt.date.fromisoformat(asof) - dt.date.fromisoformat(computed)).days
        except Exception:                                           # noqa: BLE001
            stale = None
        pos = {p["ticker"]: int(p.get("qty") or 0) for p in (d.get("positions") or [])
               if p.get("ticker") and int(p.get("qty") or 0) > 0}
        out[label] = {"asof": computed, "stale_days": stale, "positions": pos,
                      "excluded_tickers": d.get("excluded_tickers") or [],
                      "source": os.path.relpath(path, WC_ROOT)}
    return out


def triggered_today(asof, rows=None):
    """Mã có sự kiện RƠI ĐÚNG hôm nay — hai loại trigger, cố ý tách nhau.

    `ex`  : `exright_date == asof` trên DIV/ISS đã `executed` → ngày quyền tách khỏi giá (DIV,
            cổ tức CP, thưởng, quyền mua) hoặc ngày chốt đợt phát hành không điều chỉnh giá
            (ESOP/riêng lẻ/chuyển đổi TP). Đây là lúc Oshares ước lượng nhảy.
    `ais` : `effective_date == asof` trên AIS → ngày CP mới CHÍNH THỨC vào lưu hành, trễ tới ~7
            tuần sau ex-right (Bẫy 1). Đây là lúc ước lượng được thay bằng số của sở.
    """
    rows = rows if rows is not None else _all_events_on(asof)
    ex = {r["ticker"] for r in rows
          if r["event_code"] in ("DIV", "ISS") and r.get("exright_date") == asof}
    ais = {r["ticker"] for r in rows
           if r["event_code"] == "AIS" and r.get("effective_date") == asof}
    return ex, ais, rows


def _all_events_on(asof):
    from corp_action_lib import bq, TABLE
    return bq(f"""
        SELECT ticker, event_code, CAST(exright_date AS STRING) exright_date,
               CAST(effective_date AS STRING) effective_date, event_status,
               value_per_share, exercise_ratio, issue_method_name_vi,
               shares_delta, shares_total_after, SUBSTR(event_title_vi, 1, 90) event_title_vi
        FROM `{TABLE}`
        WHERE event_status = "executed"
          AND (exright_date = DATE "{asof}" OR effective_date = DATE "{asof}")
        ORDER BY ticker, event_code
    """)


# ───────────────────────────────────────────────────────────── LỚP 4 · bất biến số học

def is_systemic(n_viol, n_cmp):
    """Vi phạm lẻ tẻ (giấu số của riêng mã) hay feed hỏng diện rộng (không publish gì)?

    Tách thành hàm riêng vì đây là RANH GIỚI CHÍNH SÁCH, phải kiểm được bằng số học thuần thay vì
    chỉ đọc lại biểu thức trong thân `run()`. Xem §NGƯỠNG.
    """
    return n_viol > 0 and n_viol >= max(SYSTEMIC_MIN, int(SYSTEMIC_FRAC * n_cmp) + 1)


def _as_roll_event(e):
    """Đổi tên khoá của một sự kiện ĐÃ ÁP (`oshares_live._event_dict`) về đúng tên `_roll()` đọc.

    KHÔNG phải chuyện thẩm mỹ: `_event_dict` xuất `exercise_ratio` ra dưới tên `ratio`, còn
    `_roll`/`_dedup_iss` đọc `exercise_ratio`/`issue_method_name_vi`. Đưa thẳng dict đã áp vào
    `_roll` thì MỌI sự kiện trở thành "không có tỉ lệ" ⇒ blocker ⇒ `check_invariants` lặng lẽ bỏ
    qua mọi mã và không bao giờ báo vi phạm. Đúng loại hỏng tệ nhất: cổng vẫn chạy, vẫn xanh, và
    không kiểm cái gì. Ca `INV3` trong selfcheck tồn tại để bắt đúng lỗi này.
    """
    return {"exright_date": e.get("exright_date"),
            "exercise_ratio": e.get("ratio"),
            "shares_delta": e.get("shares_delta"),
            "issue_method_name_vi": e.get("method_vi")}


def check_invariants(asof, cur, prev_asof, prev_snap):
    """[vi phạm] — Oshares hôm nay phải bằng Oshares hôm trước ĐÃ LĂN QUA sự kiện ở giữa.

    Vì sao KHÔNG dùng ngưỡng "%/ngày": một đợt thưởng 1:1 hợp lệ là +100%, còn +3% mà không sự
    kiện nào giải thích thì sai — một ngưỡng phần trăm cố định bắt nhầm cái đầu và bỏ lọt cái
    sau. Ngưỡng đúng là sai số so với KỲ VỌNG, và kỳ vọng dựng bằng CHÍNH `_roll()` mà
    `oshares_live` dùng để tính số hôm nay (dùng lại, không viết lại).

    Ba loại vi phạm:
      * `UNEXPLAINED_JUMP` / `UNEXPLAINED_DROP` — lệch kỳ vọng > 0,1%. DROP tách riêng vì giảm số
        CP chỉ có hai nguyên nhân lành tính: (a) ước lượng nhường chỗ cho số đo của AIS (luôn <
        0,1%, đã nằm trong dung sai), (b) mua lại CP quỹ — bảng này KHÔNG có mã sự kiện cho việc
        đó, nên mọi cú giảm còn lại phải được người xem, không được tự nuốt.
      * `RETRO_CHANGE` — tính lại NGÀY HÔM TRƯỚC bằng feed hôm nay ra số khác cái đã công bố hôm
        trước. Lịch sử vừa bị viết lại; số cũ đã đi vào báo cáo nào đó rồi.

    Giới hạn đã biết (nêu ra để người review không phải tự phát hiện): khi anchor NHẢY từ dòng
    quý/ước lượng sang một AIS hiệu lực ĐÚNG hôm nay, `events_applied` hôm nay rỗng (sự kiện đã
    nằm trong số của AIS) nên kỳ vọng = số hôm qua. Chênh do ước lượng nhường chỗ cho số đo luôn
    < 0,1% (đo thật FPT: −22.519/1,7 tỷ = 0,0013%) nên nằm trong dung sai; chênh LỚN hơn thế thì
    đúng là chuyện đáng xem, không phải nhiễu.
    """
    out = []
    if not prev_snap:
        return out
    prev_tk = prev_snap.get("tickers") or {}
    for tk, row in sorted(cur.items()):
        p = prev_tk.get(tk)
        if not p or p.get("value") is None or row.get("value") is None:
            continue
        pv, cv = float(p["value"]), float(row["value"])
        applied = [_as_roll_event(e) for e in row.get("events_applied") or []
                   if prev_asof < (e.get("exright_date") or "") <= asof]
        expected, _a, blockers = _roll(pv, _dedup_iss(applied))
        if blockers:                       # không dựng được kỳ vọng ⇒ không kết luận được
            continue
        err = abs(cv - expected) / expected if expected else 0.0
        if err > EXPLAIN_TOL:
            out.append({"ticker": tk,
                        "kind": "UNEXPLAINED_DROP" if cv < expected else "UNEXPLAINED_JUMP",
                        "prev_asof": prev_asof, "prev_value": pv, "value": cv,
                        "expected": expected, "err_pct": err * 100,
                        "events_between": [e.get("exright_date") for e in applied],
                        "note": "lệch so với kỳ vọng đã lăn qua sự kiện giữa hai ngày"})
    return out


def withhold_suspect(cur, viol):
    """Vi phạm LẺ TẺ ⇒ giấu số của RIÊNG mã đó (fail-closed cấp mã), phần còn lại vẫn publish.

    MỘT mã có thể dính NHIỀU vi phạm cùng lúc — đo thật trên probe ACB: `UNEXPLAINED_JUMP` kèm
    `RETRO_CHANGE`. Vì vậy `value_withheld` chỉ được ghi MỘT lần và danh sách vi phạm được GOM:
    gán đè ở vòng thứ hai sẽ chép `None` (giá trị vừa bị giấu ở vòng một) đè lên chính con số cần
    giữ lại làm bằng chứng — mất bằng chứng mà output vẫn trông bình thường. Ca `W2` bắt việc đó.
    """
    for v in viol:
        row = cur.get(v["ticker"])
        if row is None:
            continue
        if row.get("method") != "INVARIANT_SUSPECT":
            row["value_withheld"] = row.get("value")
            row["value"] = None
            row["method"] = "INVARIANT_SUSPECT"
            row["invariant_violations"] = []
        row["invariant_violations"].append(v)
    return cur


def check_retro(asof, prev_asof, prev_snap, cache, tickers):
    """`RETRO_CHANGE` — feed hôm nay kể một câu chuyện khác về ngày hôm trước."""
    out = []
    if not prev_snap or not tickers:
        return out
    back = oshares_at(sorted(tickers), prev_asof, _cache=cache)
    prev_tk = prev_snap.get("tickers") or {}
    for tk, r in sorted(back.items()):
        p = prev_tk.get(tk)
        if not p or p.get("value") is None or r.get("value") is None:
            continue
        pv, rv = float(p["value"]), float(r["value"])
        if abs(rv - pv) / pv > EXPLAIN_TOL:
            out.append({"ticker": tk, "kind": "RETRO_CHANGE", "prev_asof": prev_asof,
                        "published_then": pv, "recomputed_now": rv,
                        "err_pct": abs(rv - pv) / pv * 100,
                        "note": "tính lại quá khứ bằng feed hôm nay ra số khác đã công bố"})
    return out


# ───────────────────────────────────────────────────────────── LỚP 2 · đối soát chéo

def crosscheck(asof, tickers, cache):
    """[lệch] giữa `oshares_live` (corp-action) và `ticker_financial.OShares` (bq_admin).

    So TẠI NGÀY CỦA DÒNG QUÝ, không tại `asof` — xem §ĐỐI SOÁT trong docstring. Hai nguồn nói về
    cùng một thời điểm thì mới so được; so số hôm nay với dòng quý 3 tháng trước là so hai câu
    trả lời cho hai câu hỏi khác nhau, và sẽ lệch mỗi ngày một cách vô nghĩa.

    KHÔNG chọn bên nào đúng. Trả cả hai số + ngày + lý do (nếu cổng giải thích của `oshares_live`
    đã nêu ra), để người đọc quyết.
    """
    quarters, _corp = cache
    out = []
    for tk in sorted(tickers):
        qs = [q for q in quarters if q["ticker"] == tk and q["time"] <= asof]
        if not qs:
            continue
        q = max(qs, key=lambda r: r["time"])
        qv, qd = float(q["OShares"]), q["time"]
        mine = oshares_at([tk], qd, _cache=cache)[tk]
        if mine.get("value") is None:
            out.append({"ticker": tk, "at": qd, "ticker_financial": qv, "oshares_live": None,
                        "kind": "NO_MODEL_VALUE", "method": mine.get("method"),
                        "note": "mô hình từ chối trả số tại ngày dòng quý (fail-closed) ⇒ "
                                "không đối soát được, KHÔNG suy ra dòng quý đúng hay sai"})
            continue
        mv = float(mine["value"])
        # MẪU SỐ nằm ngay trong TÊN TRƯỜNG có chủ đích: chuỗi `reason` do `oshares_live` sinh ra
        # chia cho KỲ VỌNG, còn ở đây chia cho số `ticker_financial`. Cùng một sự kiện ra hai con
        # số (EVF: 7,40% vs 8,00%) — một tên trường trung tính là cách người đọc trích nhầm.
        err = abs(mv - qv) / qv if qv else 0.0
        if err > EXPLAIN_TOL:
            reasons = [r.get("reason") for r in (mine.get("rejected_anchors") or [])]
            out.append({"ticker": tk, "at": qd, "ticker_financial": qv, "oshares_live": mv,
                        "err_pct_vs_ticker_financial": err * 100, "kind": "DIVERGENT",
                        "model_method": mine.get("method"), "model_anchor": mine.get("anchor_date"),
                        "model_anchor_source": mine.get("anchor_source"),
                        "explain_gate_reasons": reasons,
                        "note": "hai nguồn nói khác nhau về CÙNG một ngày — script KHÔNG chọn"})
    return out


# ───────────────────────────────────────────────────────────── LỚP 6 · cảnh báo proactive

def upcoming_events(asof, tickers, days=LOOKAHEAD_DAYS, rows=None):
    """Sự kiện của mã ĐANG GIỮ rơi trong [asof, asof+days] — gồm cả `announced`.

    `executed_only=False` là CỐ Ý và là điểm khác biệt duy nhất so với mọi consumer khác của
    bảng này: một sự kiện tương lai gần như luôn ở trạng thái `announced` (đo 2026-08-13: 35 DIV
    + 7 ISS có `exright_date` tương lai, TẤT CẢ đều `announced`; 0 dòng `executed`). Lọc
    `executed` cho câu hỏi "sắp tới có gì" sẽ trả về rỗng MỖI NGÀY và trông y hệt "không có sự
    kiện nào" — đúng kiểu im lặng nguy hiểm nhất. Đổi lại, `announced` có thể bị huỷ hoặc đổi
    ngày, nên `event_status` đi kèm từng dòng và cảnh báo nói rõ đây là dự kiến.
    `not_executed` (đã huỷ) vẫn bị loại.
    """
    if not tickers:
        return []
    end = (dt.date.fromisoformat(asof) + dt.timedelta(days=days)).isoformat()
    if rows is None:
        rows = ca_events(sorted(tickers), codes=("DIV", "ISS", "AIS"), executed_only=False)
    out = []
    for r in rows:
        if r.get("event_status") == "not_executed" or r["ticker"] not in tickers:
            continue
        ex, eff = r.get("exright_date"), r.get("effective_date")
        when, why = (None, None)
        if ex and asof <= ex <= end:
            when, why = ex, "exright_date"
        elif r["event_code"] == "AIS" and eff and asof <= eff <= end:
            when, why = eff, "effective_date"
        if not when:
            continue
        out.append({"ticker": r["ticker"], "date": when, "date_field": why,
                    "event_code": r["event_code"], "event_status": r.get("event_status"),
                    "days_ahead": (dt.date.fromisoformat(when) - dt.date.fromisoformat(asof)).days,
                    "price_adjusting": is_price_adjusting(r),
                    "value_per_share": r.get("value_per_share"),
                    "exercise_ratio": r.get("exercise_ratio"),
                    "issue_method_vi": r.get("issue_method_name_vi"),
                    "title": (r.get("event_title_vi") or "")[:90]})
    return sorted(out, key=lambda e: (e["date"], e["ticker"]))


def _fmt_event(e, holders):
    who = ", ".join(f"{lb}:{q:,}cp" for lb, q in holders.get(e["ticker"], []))
    bits = [f"**{e['ticker']}** {e['date']} (còn {e['days_ahead']}n, {e['date_field']})",
            f"{e['event_code']}"]
    if e.get("value_per_share"):
        bits.append(f"{float(e['value_per_share']):,.0f}đ/cp")
    if e.get("exercise_ratio"):
        bits.append(f"tỉ lệ {float(e['exercise_ratio']):.4f}")
    if e.get("issue_method_vi"):
        bits.append(e["issue_method_vi"])
    bits.append("điều chỉnh giá" if e["price_adjusting"] else "KHÔNG điều chỉnh giá")
    if e.get("event_status") != "executed":
        bits.append(f"[{e.get('event_status')} — dự kiến, có thể đổi/huỷ]")
    return "• " + " · ".join(bits) + (f"\n    đang giữ: {who}" if who else "")


# ───────────────────────────────────────────────────────────── điều phối

def run(asof=None, dry_run=False, alert=True, lookahead=LOOKAHEAD_DAYS, trace=None):
    asof = asof or today_ict()
    started = dt.datetime.now(ICT).isoformat(timespec="seconds")
    print(f"== corp_action_daily asof={asof} (bắt đầu {started}) ==")

    # ── LỚP 3 · cổng selfcheck TRƯỚC mọi thứ khác
    ok, sc = gate_selfcheck()
    print(f"[gate-1 selfcheck] {'PASS' if ok else 'FAIL'} — {sc}")
    if not ok:
        snap = {"asof": asof, "status": "FAILED", "usable": False,
                "failed_gate": "selfcheck", "selfcheck": sc, "generated_at": started}
        if not dry_run:
            _atomic_write_json(snapshot_path(asof, failed=True), snap)
        notify(f"🛑 corp_action_daily {asof}: **KHÔNG PUBLISH** — bộ hồi quy nền FAIL "
               f"({[s['module'] for s in sc if s['rc'] != 0]}). Số Oshares/cổ tức hôm nay "
               f"KHÔNG được dùng. Chi tiết: {snapshot_path(asof, True)}",
               telegram=True, enabled=alert)
        bus("error", f"corp-action-daily {asof} selfcheck gate FAIL",
            {"gate": "selfcheck", "detail": sc}, trace)
        return 2, snap

    # ── LỚP 5 · freshness của chính bảng nguồn
    status, fresh = gate_freshness(asof)
    streak = stale_streak(asof, status, fresh.get("max_ingested_utc"))
    print(f"[gate-2 freshness] {status} — {fresh} (chuỗi im lặng {streak})")
    if status == "DEAD":
        snap = {"asof": asof, "status": "FAILED", "usable": False, "failed_gate": "feed_dead",
                "feed": fresh, "selfcheck": sc, "generated_at": started}
        if not dry_run:
            _atomic_write_json(snapshot_path(asof, failed=True), snap)
        notify(f"🛑 corp_action_daily {asof}: **KHÔNG PUBLISH** — `corporate_action` không còn "
               f"refresh ({fresh.get('reason')}). Nạp gần nhất "
               f"{fresh.get('max_ingested_ict')}.", telegram=True, enabled=alert)
        bus("error", f"corp-action-daily {asof} feed DEAD", {"gate": "freshness", "feed": fresh},
            trace)
        return 3, snap

    # ── track set: mã đang giữ THẬT ∪ mã có sự kiện rơi đúng hôm nay
    pos = read_positions(asof=asof)
    held = sorted({tk for a in pos.values() for tk in a["positions"]})
    ex_today, ais_today, ev_rows = triggered_today(asof)
    track = sorted(set(held) | ex_today | ais_today)
    print(f"[track] {len(track)} mã = {len(held)} đang giữ ∪ {len(ex_today)} ex-right hôm nay "
          f"∪ {len(ais_today)} AIS hiệu lực hôm nay")
    stale_pos = {lb: a["stale_days"] for lb, a in pos.items()
                 if a["stale_days"] is None or a["stale_days"] > POS_STALE_DAYS}

    # ── Oshares point-in-time cho toàn track set (một lần fetch, dùng lại cho mọi phép so)
    cache = _fetch(track, asof) if track else ([], [])
    cur = oshares_at(track, asof, _cache=cache) if track else {}

    # ── LỚP 4 · bất biến, so với snapshot ĐÃ PUBLISH gần nhất
    prev_asof, prev_snap = prior_snapshot(asof)
    viol = check_invariants(asof, cur, prev_asof, prev_snap) if prev_snap else []
    viol += check_retro(asof, prev_asof, prev_snap, cache, set(cur)) if prev_snap else []
    n_cmp = len(set(cur) & set((prev_snap or {}).get("tickers") or {}))
    # đếm theo MÃ, không theo số dòng vi phạm: một mã có thể sinh 2 vi phạm (JUMP + RETRO) nên
    # đếm dòng sẽ gọi 2 mã hỏng là "diện rộng" ở ngưỡng 3. Câu hỏi là "bao nhiêu MÃ sai".
    systemic = is_systemic(len({v["ticker"] for v in viol}), n_cmp)
    print(f"[gate-3 bất biến] {len(viol)} vi phạm / {n_cmp} mã so được "
          f"(mốc {prev_asof or 'chưa có'}) systemic={systemic}")

    if systemic:
        snap = {"asof": asof, "status": "FAILED", "usable": False,
                "failed_gate": "invariants_systemic", "violations": viol,
                "n_compared": n_cmp, "feed": fresh, "selfcheck": sc, "generated_at": started}
        if not dry_run:
            _atomic_write_json(snapshot_path(asof, failed=True), snap)
        notify(f"🛑 corp_action_daily {asof}: **KHÔNG PUBLISH** — {len(viol)}/{n_cmp} mã vi phạm "
               f"bất biến số CP cùng lúc ⇒ nghi feed hỏng diện rộng, không phải sự kiện đơn lẻ. "
               f"Mã: {sorted({v['ticker'] for v in viol})[:12]}", telegram=True, enabled=alert)
        bus("error", f"corp-action-daily {asof} bất biến vi phạm diện rộng",
            {"gate": "invariants", "n_violations": len(viol), "n_compared": n_cmp,
             "violations": viol[:20]}, trace)
        return 4, snap

    # vi phạm lẻ tẻ ⇒ GIẤU SỐ của riêng mã đó (fail-closed cấp mã), phần còn lại vẫn publish
    withhold_suspect(cur, viol)

    # ── LỚP 2 · đối soát chéo hai nguồn
    diverge = crosscheck(asof, track, cache) if track else []
    print(f"[gate-4 đối soát] {len(diverge)} mã lệch giữa corp-action và ticker_financial")

    # ── cổ tức tiền mặt rơi đúng hôm nay (GỘP, nguồn vendor — CHƯA đối soát tiền broker)
    div_today = {}
    from dividend_adjusted_return import bq_corp_action
    for tk in sorted(ex_today):
        ca = bq_corp_action(tk, asof)
        if not ca or not ca.get("cash"):
            continue
        holders = {lb: a["positions"][tk] for lb, a in pos.items() if tk in a["positions"]}
        div_today[tk] = {
            "cash_per_share_gross_vnd": ca["cash"], "stock_ratio": ca.get("stock"),
            "titles": ca.get("titles"), "holders_qty": holders,
            "accrual_gross_vnd": {lb: q * ca["cash"] for lb, q in holders.items()},
            "basis": "GỘP, nguồn vendor corporate_action — CHƯA đối soát tiền broker. §21 buộc "
                     "mọi tỉ suất báo cáo đi qua dividend_adjusted_return.py, KHÔNG dùng số này."}

    # ── LỚP 6 · sự kiện sắp tới của mã ĐANG GIỮ
    upcoming = upcoming_events(asof, set(held), lookahead)
    holders_map = {}
    for e in upcoming:
        holders_map.setdefault(e["ticker"], [])
    for lb, a in pos.items():
        for tk in holders_map:
            if tk in a["positions"]:
                holders_map[tk].append((lb, a["positions"][tk]))

    snap = {
        "asof": asof, "status": "OK", "usable": True,
        "feed_fresh_today": status == "FRESH", "feed_status": status, "feed": fresh,
        "feed_stale_streak": streak,
        "generated_at": started, "generator": "mike/bin/corp_action_daily.py",
        "selfcheck": sc,
        "vintages": {"corporate_action": fresh.get("max_ingested_ict"),
                     "positions": {lb: a["asof"] for lb, a in pos.items()},
                     "ticker_financial": "quý, trễ tới ~3 tháng theo thiết kế"},
        "triggers": {"exright_today": sorted(ex_today), "ais_effective_today": sorted(ais_today)},
        "events_today": ev_rows,
        "tickers": cur,
        "cash_dividend_today": div_today,
        "crosscheck_divergent": diverge,
        "invariant_violations": viol, "n_compared": n_cmp, "prev_snapshot_asof": prev_asof,
        "upcoming_events_held": upcoming, "lookahead_days": lookahead,
        "positions_stale": stale_pos,
        "n_track": len(track), "n_held": len(held),
    }
    if not dry_run:
        _atomic_write_json(snapshot_path(asof), snap)
        print(f"[publish] {snapshot_path(asof)}")

    # ── báo người: chỉ khi CÓ CHUYỆN. Im lặng hoàn toàn thì không phân biệt được với chết,
    # nên tình trạng "sạch" vẫn đi bus (quiet), chỉ không ping Discord.
    lines = []
    if upcoming:
        lines.append(f"📅 **Sự kiện quyền ≤{lookahead} ngày tới trên mã ĐANG GIỮ** ({asof}):")
        lines += [_fmt_event(e, holders_map) for e in upcoming[:15]]
        if len(upcoming) > 15:
            lines.append(f"… và {len(upcoming) - 15} sự kiện nữa — xem "
                         f"{os.path.relpath(snapshot_path(asof), WC_ROOT)}")
    if div_today:
        lines.append(f"💰 **Chốt quyền cổ tức tiền mặt HÔM NAY**: " + "; ".join(
            f"{tk} {v['cash_per_share_gross_vnd']:,.0f}đ/cp"
            f"{' (giữ ' + ', '.join(f'{lb} {q:,}cp' for lb, q in v['holders_qty'].items()) + ')' if v['holders_qty'] else ''}"
            for tk, v in sorted(div_today.items())))
    if ais_today:
        lines.append(f"🧾 **AIS hiệu lực hôm nay** (số CP chính thức đổi): {sorted(ais_today)}")
    if diverge:
        lines.append(f"⚠️ **Lệch nguồn Oshares** ({len(diverge)} mã, script KHÔNG tự chọn số): " +
                     "; ".join(f"{d['ticker']}@{d['at']} corp-action "
                               f"{(d['oshares_live'] or 0):,.0f} vs bq_admin "
                               f"{d['ticker_financial']:,.0f}"
                               f" ({d.get('err_pct_vs_ticker_financial', 0):.2f}%)"
                               for d in diverge[:8]))
    if viol:
        lines.append(f"🚨 **Bất biến số CP vi phạm** ({len(viol)} mã — số đã bị GIẤU, không "
                     f"publish giá trị): " + "; ".join(
                         f"{v['ticker']} {v['kind']} {v.get('err_pct', 0):.2f}%"
                         for v in viol[:8]))
    if status == "STALE" and streak >= 2:
        lines.append(f"🕒 `corporate_action` không nạp thêm gì {streak} ngày liên tiếp "
                     f"(gần nhất {fresh.get('max_ingested_ict')}) — sự kiện MỚI công bố hôm nay "
                     f"có thể chưa có trong bảng.")
    if stale_pos:
        lines.append(f"📄 Vị thế đọc từ artifact CŨ: {stale_pos} (ngày) — danh sách mã đang giữ "
                     f"có thể thiếu mã mới mua.")

    if lines and alert:
        notify("\n".join(lines), telegram=(bool(viol) or streak >= 5))
    elif not lines:
        print("[quiet] không có sự kiện/lệch/vi phạm nào — không ping Discord")

    bus("finding" if not viol else "error",
        f"corp-action-daily {asof} {'OK' if not viol else 'CÓ VI PHẠM BẤT BIẾN'}",
        {"asof": asof, "feed_status": status, "n_track": len(track), "n_held": len(held),
         "exright_today": sorted(ex_today), "ais_today": sorted(ais_today),
         "cash_dividend_today": sorted(div_today), "n_upcoming_held": len(upcoming),
         "n_crosscheck_divergent": len(diverge), "n_invariant_violations": len(viol),
         "snapshot": os.path.relpath(snapshot_path(asof), WC_ROOT)}, trace)
    return 0, snap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", help="YYYY-MM-DD (mặc định hôm nay ICT)")
    ap.add_argument("--dry-run", action="store_true", help="không ghi snapshot")
    ap.add_argument("--no-alert", action="store_true", help="không gửi Discord/Telegram")
    ap.add_argument("--lookahead-days", type=int, default=LOOKAHEAD_DAYS)
    ap.add_argument("--trace", help="trace_id để gộp event của cùng một job")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        from corp_action_daily_selfcheck import main as sc_main
        return sc_main()
    try:
        rc, _snap = run(asof=a.asof, dry_run=a.dry_run, alert=not a.no_alert,
                        lookahead=a.lookahead_days, trace=a.trace)
    except Exception as exc:                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        notify(f"🛑 corp_action_daily lỗi KHÔNG BẮT ĐƯỢC: {type(exc).__name__}: {exc}",
               telegram=True, enabled=not a.no_alert)
        bus("error", "corp-action-daily crash", {"error": f"{type(exc).__name__}: {exc}"}, a.trace)
        return 5
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
