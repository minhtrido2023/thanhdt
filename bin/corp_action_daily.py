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

BẢY LỚP, KHÔNG LỚP NÀO ĐƯỢC BỎ
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
7. **Phát hiện phiên BỊ LỠ + backfill** — vì trigger ở lớp trên chỉ hỏi BQ cho ĐÚNG ngày hôm
   nay, một lượt cron không chạy được (crash, timeout, máy tắt) làm sự kiện của ngày đó biến
   mất VĨNH VIỄN khỏi hệ: vòng xác nhận không cứu được (nó chỉ theo cái ĐÃ ghi), và không có
   đường nào quay lại. Lớp này so `prev_asof` với `asof` theo LỊCH GIAO DỊCH, chạy lại đúng
   truy vấn ngày-sự-kiện cho từng phiên đã lỡ, rồi thả kết quả vào chính vòng xác nhận trên.
   Ngày backfill hỏng/vượt trần đi vào `backfill_deferred_days` của snapshot và được lượt sau
   lấy lại — hàng đợi tự rút, không có cái cap im lặng nào. Xem `missed_trading_days`.

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

    `ex`  : `exright_date == asof` trên DIV/ISS → ngày quyền tách khỏi giá (DIV, cổ tức CP,
            thưởng, quyền mua) hoặc ngày chốt đợt phát hành không điều chỉnh giá (ESOP/riêng
            lẻ/chuyển đổi TP). Đây là lúc Oshares ước lượng nhảy.
    `ais` : `effective_date == asof` trên AIS → ngày CP mới CHÍNH THỨC vào lưu hành, trễ tới ~7
            tuần sau ex-right (Bẫy 1). Đây là lúc ước lượng được thay bằng số của sở.
    """
    rows = rows if rows is not None else _all_events_on(asof)
    ex = {r["ticker"] for r in rows
          if r["event_code"] in ("DIV", "ISS") and r.get("exright_date") == asof}
    ais = {r["ticker"] for r in rows
           if r["event_code"] == "AIS" and r.get("effective_date") == asof}
    return ex, ais, rows


def _events_on_sql(asof, table=None, include_cancelled=False):
    """SQL cho MỌI sự kiện rơi đúng `asof`. Tách khỏi hàm chạy để **kiểm được hình dạng truy vấn**.

    ⚠️ BUG THẬT, quant-skeptic REFUTED vòng 1 (2026-08-13): bản đầu lọc `event_status =
    "executed"` ở đây, và **trigger ngày-sự-kiện KHÔNG BAO GIỜ nổ**. Vendor chỉ đổi
    `announced → executed` trong lần reload toàn bảng rơi vào ~22:2x ICT CỦA CHÍNH NGÀY SỰ KIỆN —
    tức ~15 tiếng SAU khi cron 07:30 đã đọc xong lô của tối hôm trước. Đo thật trên đúng lô
    2026-08-12 22:48 mà cron 08-13 nhìn thấy:

        exright 2026-08-11 → AAM/BFC/BSR/MBB×2/SBD/VGR đều `executed`
        exright 2026-08-13 → DHN 1.500đ, HGM 5.000đ, SAC 1.000đ, BCF ISS 0,11 — **tất cả
                             `announced`**

    ⇒ lọc `executed` cho `asof = hôm nay` trả 0 dòng MỖI NGÀY, và không có lượt chạy nào quay lại
    ngày đã lỡ. Đúng cái bẫy "im lặng trả rỗng" mà `upcoming_events` đã phòng — cách đó 30 dòng.

    Nay lọc `!= "not_executed"` (chỉ loại sự kiện đã HUỶ) và **mang `event_status` theo từng
    dòng** để người đọc phân biệt "đã xảy ra" với "công bố, chưa xác nhận". Lượt chạy hôm sau
    xác nhận lại bằng `confirm_prior_triggers()`.

    Selfcheck bơm `rows=` vào `triggered_today` sẽ đi VÒNG QUA mệnh đề WHERE này (đúng nhận xét
    của quant-skeptic), nên ca `Q1`-`Q3` kiểm THẲNG chuỗi SQL, còn ca `--live` kiểm truy vấn thật.
    """
    from corp_action_lib import TABLE
    # bảng dựng tay (subquery `(SELECT …)`) KHÔNG được bọc backtick, tên bảng thì có. Nhờ vậy ca
    # `--live` chấm được chính mệnh đề WHERE này bằng máy SQL thật trên dữ liệu tự dựng, thay vì
    # chỉ so chuỗi — mà không phải viết một biến thể SQL thứ hai chỉ để test (biến thể thứ hai
    # là thứ trôi khỏi bản production rồi test cái không còn tồn tại).
    src = table or TABLE
    src = src if src.lstrip().startswith("(") else f"`{src}`"
    return f"""
        SELECT id, ticker, event_code, CAST(exright_date AS STRING) exright_date,
               CAST(effective_date AS STRING) effective_date, event_status,
               value_per_share, exercise_ratio, issue_method_name_vi,
               shares_delta, shares_total_after, SUBSTR(event_title_vi, 1, 90) event_title_vi
        FROM {src}
        WHERE {'TRUE' if include_cancelled else 'event_status != "not_executed"'}
          AND (exright_date = DATE "{asof}" OR effective_date = DATE "{asof}")
        ORDER BY ticker, event_code
    """


def _all_events_on(asof):
    from corp_action_lib import bq
    return bq(_events_on_sql(asof))


# ─────────────────────────────────────────── LỚP 7 · phiên BỊ LỠ (phát hiện + backfill)

# Trần số phiên được backfill trong MỘT lượt chạy. Không phải "đủ dùng" — là chặn một lượt chạy
# duy nhất bắn ra hàng trăm truy vấn khi cron chết dài ngày (hoặc khi ai đó chạy `--asof` của một
# ngày xa trong quá khứ). Chọn 10 = 2 tuần giao dịch: dài hơn mọi kỳ nghỉ lễ VN (Tết ~9 ngày
# lịch ≈ 5-6 phiên) nên một kỳ nghỉ KHÔNG BAO GIỜ chạm trần, mà cron chết quá 2 tuần thì đó là
# sự cố cần người, không phải cái để một lượt chạy lặng lẽ đuổi kịp.
# Ngày vượt trần KHÔNG bị vứt: nó vào `deferred_days`, được ghi ra snapshot và lượt sau lấy lại
# (10 phiên/lượt) — nên hàng đợi tự rút, không có cái cap im lặng nào.
BACKFILL_MAX_DAYS = 10


def missed_trading_days(prev_asof, asof, deferred=()):
    """Các phiên GIAO DỊCH cron đã LỠ = ngày giao dịch nằm HẲN giữa `prev_asof` và `asof`.

    Đếm theo LỊCH GIAO DỊCH (`prev_trading_day`, tức lịch lễ của `trading_bot.vn_market`), không
    theo số ngày lịch: sáng thứ Hai luôn cách snapshot thứ Sáu 3 ngày lịch nhưng KHÔNG lỡ phiên
    nào; ngược lại một phiên bị lỡ ngay trước kỳ nghỉ chỉ cách 1 ngày lịch mà vẫn là lỡ thật.

    `prev_asof=None` (chưa từng có snapshot nào) ⇒ RỖNG, cố ý: lần chạy đầu tiên không có mốc để
    nói ngày nào là "đã lỡ", và backfill toàn bộ lịch sử lúc cài cron là việc khác hẳn — nếu cần
    thì chạy tay `--asof` từng ngày, không để một lượt cron tự quyết.

    `deferred` = ngày lượt trước ĐỊNH backfill mà chưa xong (lỗi truy vấn, hoặc vượt trần). Gộp
    vào đây là toàn bộ cơ chế "không mất ngày nào": chúng được ghi ra snapshot nên còn sống qua
    lượt chạy, và vì `prev_asof` sau đó đã nhảy lên ngày mới, không có đường nào khác tìm lại.
    """
    out = set()
    if prev_asof:
        d_prev = dt.date.fromisoformat(prev_asof)
        d = prev_trading_day(dt.date.fromisoformat(asof))
        while d > d_prev:
            out.add(d.isoformat())
            d = prev_trading_day(d)
    out |= {d for d in (deferred or []) if d and d < asof}
    return sorted(out)


def backfill_missed(days, fetch=None, max_days=BACKFILL_MAX_DAYS):
    """Chạy LẠI truy vấn sự kiện-trong-ngày cho từng phiên bị lỡ, như thể cron đã chạy đúng ngày đó.

    Dùng ĐÚNG `_events_on_sql` của đường chính (qua `_all_events_on`) chứ không viết một truy vấn
    thứ hai: một biến thể SQL riêng cho backfill là thứ sẽ trôi khỏi bản production rồi ta test
    cái không còn tồn tại — đúng lý do `_events_on_sql` được tách ra ở vòng trước.

    `include_cancelled=False` (mặc định của `_all_events_on`) là CÓ CHỦ ĐÍCH: sự kiện đã HUỶ
    trong khoảng bị lỡ thì không có gì để ghi — ta chưa từng công bố nó nên không có snapshot nào
    sai để đính chính. Đây là chỗ backfill TỐT HƠN một lượt chạy đúng ngày (lượt đúng ngày sẽ ghi
    bản `announced` rồi hôm sau phải rút lại); khác biệt duy nhất, và nó nghiêng về phía an toàn.

    ⚠️ GIỚI HẠN CÓ CHỦ ĐÍCH — backfill KHÔNG dựng lại `cash_dividend_today` cho ngày đã lỡ.
    Khối đó mang `holders_qty`/`accrual_gross_vnd` theo vị thế, mà `read_positions` chỉ đọc được
    artifact MỚI NHẤT: dựng accrual của một ngày quá khứ bằng vị thế HÔM NAY là gán tiền cho một
    danh mục không phải danh mục lúc chốt quyền — sai lặng lẽ, và tệ hơn là không có. Cái được
    ghi lại là SỰ KIỆN (đủ để `dividend_adjusted_return.py` — nguồn chuẩn tắc §21 — tính đúng
    sau), cộng một dòng cảnh báo liệt kê mã ĐANG GIỮ có dính sự kiện trong khoảng bị lỡ.

    Trả về một khối tự mô tả — `days_backfilled` (đã xong), `deferred_days` (chưa, sẽ thử lại),
    `errors` (vì sao). Lỗi truy vấn KHÔNG làm hỏng lượt chạy: ngày đó rơi vào `deferred_days` và
    lượt sau lấy lại. Ném lỗi ra ngoài ở đây = mất luôn cả snapshot hôm nay vì một ngày quá khứ.
    """
    fetch = fetch or _all_events_on
    days = sorted(set(days))
    over = days[:-max_days] if max_days and len(days) > max_days else []
    events, done, errors, deferred = [], [], [], list(over)
    for d in days[len(over):]:                    # phiên GẦN NHẤT trước — sát vị thế đang giữ nhất
        try:
            rows = fetch(d)
        except Exception as exc:                                    # noqa: BLE001
            errors.append({"date": d, "error": f"{type(exc).__name__}: {exc}"})
            deferred.append(d)
            continue
        for r in rows or []:
            events.append({**r, "event_date": d, "backfilled": True})
        done.append(d)
    return {"days_missed": days, "days_backfilled": done, "events": events,
            "n_events": len(events), "deferred_days": sorted(set(deferred)), "errors": errors,
            "ok": not deferred}


def _num_tag(x):
    """Số → chuỗi ổn định qua vòng JSON. `3000`, `3000.0`, `"3000"`, `Decimal("3000")` phải cho
    CÙNG một khoá, nếu không thì sự kiện tự-không-khớp-chính-mình sau khi đọc lại snapshot."""
    if x is None or x == "":
        return ""
    try:
        return f"{float(x):.6f}"
    except (TypeError, ValueError):
        return str(x)


def _event_key(r):
    """Khoá NỘI DUNG của MỘT sự kiện — dùng khi không có `id`, hoặc `id` không khớp được.

    ⚠️ Bản trước chỉ có 4 trường đầu và quant-skeptic vòng 2 (2026-08-13) đã chọc thủng bằng ca
    CÓ THẬT ghi ngay trong docstring của `bq_corp_action`: MBB 2026-08-11 có HAI sự kiện cùng
    ticker + cùng `event_code` (ISS) + cùng `exright_date` (quyền mua 10% và cổ tức CP 15%, khác
    nhau ở `issue_method_name_vi`/`exercise_ratio`). Hai sự kiện gộp về một khoá ⇒ một dòng ghi
    đè dòng kia ⇒ nếu một cái bị HUỶ và một cái được xác nhận, kết quả CONFIRMED hay CANCELLED
    phụ thuộc THỨ TỰ DÒNG BigQuery trả về, tức là một khoản đã huỷ có thể được báo là đã xác
    nhận. Thêm ratio/method/title/value làm khoá phân biệt hai đợt đó tách hẳn nhau.
    """
    return (r.get("ticker") or "", r.get("event_code") or "",
            r.get("exright_date") or "", r.get("effective_date") or "",
            _num_tag(r.get("value_per_share")), _num_tag(r.get("exercise_ratio")),
            r.get("issue_method_name_vi") or "", r.get("event_title_vi") or "")


def _kind_of(status):
    if status == "__MISSING__":
        return "VANISHED"
    if status == "not_executed":
        return "CANCELLED"
    if status == "executed":
        return "CONFIRMED"
    return "STILL_ANNOUNCED"


# thứ tự "TỆ NHẤT TRƯỚC". Dùng khi phải gán nhiều trạng thái vào nhiều sự kiện cùng khoá nội dung:
# gán tệ trước ⇒ một vụ HUỶ luôn được báo ra, bất kể BigQuery trả dòng theo thứ tự nào.
_KIND_RANK = {"CANCELLED": 0, "VANISHED": 1, "STILL_ANNOUNCED": 2, "CONFIRMED": 3}


def _match_events(recorded, now_rows):
    """Ghép TỪNG sự kiện đã ghi với dòng hiện tại → [(bản ghi, trạng thái nay)].

    Hai lượt, cố ý theo thứ tự này:
      1. **`id` của vendor** (`corporate_action.id`, đã kiểm: 36.149/36.149 duy nhất, 0 NULL) —
         khoá thật, chính xác từng dòng.
      2. **khoá nội dung** cho phần còn lại. KHÔNG bỏ được lượt này: cả bảng chỉ có MỘT ngày
         `ingested_at` nên KHÔNG kiểm chứng được `id` có bền qua lần vendor nạp lại hay không.
         Nếu vendor sinh `id` mới mỗi lần reload thì lượt 1 trượt sạch, và không có lượt 2 thì
         mọi sự kiện sẽ bị báo `VANISHED` hàng loạt ngay lần reload đầu tiên — một cảnh báo giả
         diện rộng còn tệ hơn cái nó định phòng.

    Trong lượt 2, nếu vẫn còn nhiều sự kiện chung một khoá nội dung (hai đợt y hệt nhau tới từng
    ký tự), trạng thái được gán TỆ NHẤT TRƯỚC ⇒ kết quả không phụ thuộc thứ tự dòng BQ trả về.
    """
    used = [False] * len(now_rows)
    by_id = {}
    for i, r in enumerate(now_rows):
        if r.get("id"):
            by_id.setdefault(str(r["id"]), i)
    out, left = [], []
    for rec in recorded:
        rid = str(rec.get("id") or "")
        i = by_id.get(rid, -1) if rid else -1
        if i >= 0 and not used[i]:
            used[i] = True
            out.append((rec, now_rows[i].get("event_status")))
        else:
            left.append(rec)
    pool = {}
    for i, r in enumerate(now_rows):
        if not used[i]:
            pool.setdefault(_event_key(r), []).append(r.get("event_status"))
    for sts in pool.values():
        sts.sort(key=lambda s: _KIND_RANK[_kind_of(s)])
    for rec in sorted(left, key=lambda r: str(_event_key(r))):
        sts = pool.get(_event_key(rec)) or []
        out.append((rec, sts.pop(0) if sts else "__MISSING__"))
    return out


# Sự kiện còn `announced` được kiểm lại tối đa ngần này LƯỢT CHẠY rồi mới escalate. Chọn 5 vì:
# (a) đo thật trên 90 ngày ex-right, mọi ngày cách hôm nay ≥2 phiên đều 100% `executed` ⇒ còn
# `announced` sang tới lượt thứ 5 là bất thường rõ ràng, không phải nhịp bình thường của vendor;
# (b) bằng đúng `FEED_DEAD_DAYS` — một feed đứng im nhưng chưa CHẾT đã có cảnh báo riêng của nó,
# đặt N nhỏ hơn sẽ sinh cảnh báo thứ hai nói cùng một chuyện; đặt lớn hơn thì có ngày feed đã bị
# tuyên CHẾT mà hàng treo vẫn im lặng. (c) Đây là ngưỡng CẢNH BÁO, không phải ngưỡng tiền — sai
# một phiên chỉ đổi thời điểm một dòng Discord.
PENDING_MAX_CHECKS = 5

# các trường phải mang theo để lượt sau dựng lại được khoá + kể lại được lịch sử món treo
PENDING_FIELDS = ("id", "ticker", "event_code", "exright_date", "effective_date",
                  "value_per_share", "exercise_ratio", "issue_method_name_vi",
                  "event_title_vi", "status_then", "event_date", "first_seen_asof", "n_checks",
                  "backfilled")


def pending_items(prev_asof, prev_snap, backfilled=None, asof=None):
    """Danh sách sự kiện CẦN kiểm ở lượt này = MỚI ghi hôm trước ∪ CÒN TREO từ các lượt trước
    ∪ VỪA BACKFILL từ các phiên bị lỡ.

    ⚠️ Bản trước dựng `recorded` CHỈ từ `events_today` của snapshot liền trước, nên một sự kiện
    trả `STILL_ANNOUNCED` ở D+1 KHÔNG BAO GIỜ được kiểm lại ở D+2 — vòng xác nhận chỉ bắn một
    phát rồi thôi (quant-skeptic vòng 2). Mà lượt chạy sống DUY NHẤT của vòng này cho 4/4
    `STILL_ANNOUNCED`, tức đúng cái nhánh bị rơi lại là nhánh xảy ra thật.

    Sự kiện backfill đi vào ĐÚNG danh sách này, không có nhánh riêng: nhờ vậy nó thừa hưởng
    nguyên bộ máy đã qua quant-skeptic (ghép theo `id` → khoá nội dung, phân loại CONFIRMED /
    CANCELLED / STILL_ANNOUNCED, đồng hồ `n_checks`, `carry_forward`) mà không thêm một cách
    phân loại thứ hai — hai cách phân loại cho cùng một khái niệm là cách sinh ra hai kết luận
    trái nhau trên cùng dữ liệu.

    Khoá chống trùng `(ngày sự kiện, id, khoá nội dung)` là thứ làm backfill IDEMPOTENT (§5):
    chạy lại cron cùng ngày, hoặc một ngày `deferred` được thử lại trong khi món của chính ngày
    đó đang nằm trong hàng treo, đều cho MỘT dòng. Và vì hàng treo được nạp TRƯỚC, dòng thắng là
    dòng giữ `n_checks`/`first_seen_asof` THẬT — không phải dòng backfill vừa dựng với n_checks=0.
    """
    items, seen = [], set()

    def _add(src, event_date, first_seen, n_checks, backfill=False):
        it = {k: src.get(k) for k in PENDING_FIELDS}
        it["status_then"] = src.get("status_then") or src.get("event_status")
        it["event_date"], it["first_seen_asof"], it["n_checks"] = event_date, first_seen, n_checks
        it["backfilled"] = bool(src.get("backfilled") or backfill)
        k = (event_date, str(src.get("id") or ""), _event_key(src))
        if k in seen:
            return
        seen.add(k)
        items.append(it)

    # hàng treo TRƯỚC hàng mới: món treo giữ được `first_seen_asof`/`n_checks` thật của nó, không
    # bị một dòng cùng khoá của ngày hôm trước reset đồng hồ về 0.
    for p in (prev_snap or {}).get("pending_confirmations") or []:
        _add(p, p.get("event_date") or prev_asof, p.get("first_seen_asof") or prev_asof,
             int(p.get("n_checks") or 0))
    if prev_asof:
        for r in (prev_snap or {}).get("events_today") or []:
            _add(r, prev_asof, prev_asof, 0)
    for r in backfilled or []:
        # `first_seen_asof` = HÔM NAY, không phải ngày sự kiện: đồng hồ `PENDING_MAX_CHECKS` đếm
        # số LƯỢT CHẠY đã kiểm, mà món này mới được nhìn lần đầu hôm nay. Lấy ngày sự kiện làm
        # mốc sẽ khiến một món backfill của 6 phiên trước hết hạn ngay lượt đầu và không bao giờ
        # được theo tới lúc ngã ngũ.
        _add(r, r.get("event_date") or asof or prev_asof, asof or prev_asof, 0, backfill=True)
    return items


def confirm_prior_triggers(prev_asof, prev_snap, rows=None, rows_by_date=None,
                           max_checks=PENDING_MAX_CHECKS, backfilled=None, asof=None):
    """Sự kiện đã ghi trước đó GIỜ ra sao — vòng xác nhận cho các dòng lúc đó còn `announced`.

    Vì trigger ngày-sự-kiện buộc phải chạy trên `announced` (xem `_events_on_sql`), snapshot của
    ngày D có thể ghi một khoản cổ tức mà sau đó bị HUỶ. Không có vòng này thì snapshot D sai
    vĩnh viễn và không ai biết. Mỗi lượt chạy đọc lại NGÀY SỰ KIỆN của từng món đang chờ, với
    MỌI trạng thái, và trả:

      * `CANCELLED`  — đã ghi, nay `not_executed`. Sai số thật, phải báo người.
      * `CONFIRMED`  — `announced` → `executed`. Bình thường, chỉ ghi vào snapshot.
      * `STILL_ANNOUNCED` — vendor chưa đổi trạng thái. Chưa sai, nhưng chưa chắc ⇒ MANG SANG
        lượt sau (`carry_forward`), kiểm lại tới khi ngã ngũ.
      * `UNRESOLVED_TIMEOUT` — vẫn `announced` sau `max_checks` lượt. Thôi mang tiếp, báo người.
      * `VANISHED`   — dòng biến mất khỏi bảng. Bất thường, báo người.

    `backfilled=` là các sự kiện vừa moi lại từ những phiên cron bị LỠ (xem `backfill_missed`).
    Chúng được hỏi lại NGAY trong lượt này bằng chính truy vấn xác nhận (`include_cancelled=True`,
    tức một truy vấn thứ hai cho cùng ngày). Dư một truy vấn nhỏ — chỉ ở đúng cái nhánh hiếm là
    "cron vừa lỡ phiên" — và đổi lại: đường đi của sự kiện backfill giống hệt từng bước đường đi
    của sự kiện ghi đúng ngày, nên không có nhánh nào chỉ backfill mới chạy qua và không ai test.

    `rows=` (một ngày, chính là `prev_asof`) và `rows_by_date=` (nhiều ngày) là điểm bơm cho bộ
    hồi quy hermetic — không có chúng thì hàm tự truy vấn BQ.
    """
    items = pending_items(prev_asof, prev_snap, backfilled=backfilled, asof=asof)
    if not items:
        return []
    by_date = {}
    for it in items:
        by_date.setdefault(it["event_date"], []).append(it)
    out = []
    for d in sorted(by_date):
        if rows_by_date is not None:
            # `.get(d, [])` chứ KHÔNG rơi về BQ khi thiếu ngày: điểm bơm phải KÍN, không thì một
            # ca hermetic thiếu một ngày sẽ lặng lẽ đi hỏi bảng thật và bộ này hết hermetic.
            now_rows = rows_by_date.get(d, [])
        elif rows is not None and d == prev_asof:
            now_rows = rows
        else:
            from corp_action_lib import bq
            # include_cancelled=True: chính CÁI ĐÃ HUỶ mới là thứ vòng này đi tìm.
            now_rows = bq(_events_on_sql(d, include_cancelled=True))
        recorded = sorted(by_date[d], key=lambda r: str(_event_key(r)))
        for rec, is_ in _match_events(recorded, now_rows):
            kind = _kind_of(is_)
            n = int(rec.get("n_checks") or 0) + 1
            if kind == "STILL_ANNOUNCED" and n >= max_checks:
                kind = "UNRESOLVED_TIMEOUT"
            c = {k: rec.get(k) for k in PENDING_FIELDS}
            c.update({"status_now": is_, "kind": kind, "n_checks": n,
                      # giữ tên cũ `prev_asof` = ngày sự kiện của CHÍNH món này (không còn luôn
                      # bằng snapshot liền trước, vì hàng treo có thể cũ hơn thế).
                      "prev_asof": rec.get("event_date")})
            out.append(c)
    return out


def carry_forward(confirmations):
    """Món MANG SANG lượt sau — chỉ những cái còn `announced` mà chưa hết hạn kiểm.

    `UNRESOLVED_TIMEOUT` cố ý KHÔNG nằm ở đây: đã báo người một lần rồi thì thôi mang tiếp, nếu
    không danh sách chờ chỉ dài ra mãi và cảnh báo lặp lại mỗi ngày cho tới khi hết ai đọc.
    """
    return [{k: c.get(k) for k in PENDING_FIELDS}
            for c in confirmations if c["kind"] == "STILL_ANNOUNCED"]


def dividend_event_status(ev_rows, asof):
    """Nhãn trạng thái cho SỐ CỔ TỨC GỘP của từng mã — gộp có chủ đích, và gộp về phía THẬN TRỌNG.

    `bq_corp_action` trả TỔNG tiền của mọi sự kiện `DIV` cùng ngày của một mã, nên nhãn đi kèm
    buộc phải ở cấp MÃ. Bản trước dựng `{ticker: status}` bằng một comprehension ⇒ dòng CUỐI
    thắng, mà thứ tự dòng BQ trả về không xác định ⇒ nhãn *(dự kiến)* có thể biến mất chỉ vì đổi
    thứ tự dòng (cùng một lỗi gộp khoá như `confirm_prior_triggers`, quant-skeptic vòng 2).

    Nay gộp theo TỪNG SỰ KIỆN rồi mới hạ về mã bằng luật **`executed` CHỈ KHI mọi sự kiện đều
    `executed`** — kết quả không phụ thuộc thứ tự, và sai thì sai về phía dán thêm nhãn "dự
    kiến", không phải phía bỏ nhãn đi.
    """
    per_event = {}
    for r in ev_rows:
        if r.get("event_code") == "DIV" and r.get("exright_date") == asof:
            per_event[(str(r.get("id") or ""), _event_key(r))] = r.get("event_status")
    out = {}
    for (_rid, key), st in per_event.items():
        tk = key[0]
        cur = out.get(tk)
        if cur is None or _KIND_RANK[_kind_of(st)] < _KIND_RANK[_kind_of(cur)]:
            out[tk] = st
    return out


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


def _fmt_divergence(diverge, limit=8):
    """Dòng Discord cho kết quả `crosscheck()`. Trả `None` khi không có gì để báo.

    `crosscheck()` trả HAI loại bản ghi khác hẳn nhau về NGHĨA, và tới 2026-08-13 dòng này in
    chung một khuôn:
      * `DIVERGENT`      — hai nguồn CÙNG trả số, và hai số đó khác nhau. Có `oshares_live` (số)
                           và `err_pct_vs_ticker_financial`.
      * `NO_MODEL_VALUE` — mô hình TỪ CHỐI trả số (fail-closed). `oshares_live` là `None` và
                           KHÔNG có trường sai số, vì không có sai số nào để tính.

    Khuôn chung viết `(d['oshares_live'] or 0)` với `err_pct` mặc định `0`, nên ca thứ hai in ra
    **"TCB@2026-07-21 corp-action 0 vs bq_admin 7.086.240.414 (0,00%)"** — đọc y hệt "khớp hoàn
    hảo" trong khi sự thật là "KHÔNG xác minh được". `or 0` ở đây KHÔNG phải một mặc định lành
    tính: nó biến một lời TỪ CHỐI TRẢ LỜI thành một con số, và con số đó tình cờ làm sai số bằng
    đúng 0 — hướng sai lệch tệ nhất có thể, vì nó trấn an người đọc thay vì cảnh báo họ.

    Lỗi có sẵn từ khi viết `crosscheck()`, nhưng ngày 2026-08-13 mới lần đầu kích hoạt trên mã
    ĐANG GIỮ THẬT (TCB, cả SpaceX lẫn ZaloPay) — cổng chứng nhận neo AIS vòng 4 đẩy TCB từ
    `DIVERGENT` sang `NO_MODEL_VALUE`. quant-skeptic vòng 4 tìm ra; xem `research/
    oshares_gate_move_20260813/`.

    Hai loại được ĐẾM RIÊNG ở đầu dòng, không gộp thành một con số: "3 mã lệch" và "2 mã lệch +
    1 mã không đối soát được" là hai tình trạng khác nhau của hệ thống.
    """
    if not diverge:
        return None

    def refused(d):
        """MỘT vị ngữ dùng cho CẢ đầu dòng lẫn thân dòng — cố ý.

        Bản đầu của hàm này đếm theo `kind` nhưng render theo `oshares_live is None`; một bản ghi
        thiếu `kind` liền được đếm là "1 mã LỆCH" trong khi thân dòng nói "TỪ CHỐI trả số". Hai
        vị ngữ cho cùng một câu hỏi là cách một dòng cảnh báo tự mâu thuẫn với chính nó.
        """
        return d.get("kind") == "NO_MODEL_VALUE" or d.get("oshares_live") is None

    n_none = sum(1 for d in diverge if refused(d))
    n_div = len(diverge) - n_none
    head = []
    if n_div:
        head.append(f"{n_div} mã LỆCH")
    if n_none:
        head.append(f"{n_none} mã KHÔNG đối soát được")

    def one(d):
        if refused(d):
            return (f"{d['ticker']}@{d['at']} mô hình TỪ CHỐI trả số "
                    f"({d.get('method') or 'không rõ nhãn'}) — KHÔNG đối soát được với bq_admin "
                    f"{d['ticker_financial']:,.0f}")
        return (f"{d['ticker']}@{d['at']} corp-action {d['oshares_live']:,.0f} vs bq_admin "
                f"{d['ticker_financial']:,.0f} "
                f"({d['err_pct_vs_ticker_financial']:.2f}%)")

    more = f" … và {len(diverge) - limit} mã nữa" if len(diverge) > limit else ""
    return (f"⚠️ **Đối soát nguồn Oshares** ({' + '.join(head)}, script KHÔNG tự chọn số): "
            + "; ".join(one(d) for d in diverge[:limit]) + more)


def none_value_watch(cur, prev_snap):
    """Lưới giám sát DIỄN BIẾN của fail-closed: hôm nay có bao nhiêu mã bị TỪ CHỐI trả số?

    Fail-closed cấp mã (`value is None`) an toàn theo thiết kế, nhưng nếu không ai theo dõi con
    số đó thì một feed hỏng dần chỉ biểu hiện thành "im lặng ngày càng nhiều" — không cổng nào
    đỏ, không ai biết. quant-skeptic vòng 4 gọi đúng tên: "im lặng vĩnh viễn không giám sát".

    Báo khi số mã bị từ chối TĂNG so với snapshot đã publish gần nhất. KHÔNG báo khi giảm hay
    giữ nguyên (giảm là feed lành lại; giữ nguyên là hiện trạng đã biết). Cũng liệt kê mã MỚI
    rơi vào diện từ chối kể cả khi tổng không tăng — một mã lành lại che một mã hỏng đi thì tổng
    đứng yên, mà đó vẫn là chuyện phải biết.
    """
    now = {tk: r.get("method") for tk, r in (cur or {}).items() if r.get("value") is None}
    prev_tk = (prev_snap or {}).get("tickers") or {}
    before = {tk for tk, r in prev_tk.items() if r.get("value") is None}
    return {"n_none": len(now), "n_none_prev": len(before) if prev_snap else None,
            "n_total": len(cur or {}),
            "delta": (len(now) - len(before)) if prev_snap else None,
            "newly_none": {tk: m for tk, m in sorted(now.items()) if tk not in before},
            "recovered": sorted(before - set(now)),
            "by_method": {m: sorted(t for t, mm in now.items() if mm == m)
                          for m in sorted({m for m in now.values()})},
            # `has_baseline=False` ⇒ CHƯA ĐÁNH GIÁ ĐƯỢC, không phải "không tăng". Cùng kỷ luật
            # với `invariant_evaluated`: không có mốc thì không có kết luận.
            "has_baseline": bool(prev_snap),
            "alert": bool(prev_snap) and (len(now) > len(before) or bool(set(now) - before))}


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
    # hai nhánh trả về HAI tên khoá khác nhau: nhánh thường có `max_ingested_utc`, nhánh DEAD
    # do parse lỗi trả nguyên `f` nên chỉ có `max_ingested`. Lấy một tên thôi ⇒ chữ ký lặng lẽ
    # thành None đúng lúc feed hỏng, và `stale_streak` đếm lại từ 1 mỗi ngày vì None == None
    # khớp chữ ký cũ sai cách. (quant-skeptic vòng 1, mục `_secondary`.)
    streak = stale_streak(asof, status,
                          fresh.get("max_ingested_utc") or fresh.get("max_ingested"))
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
    # `0 vi phạm` KHI `n_cmp == 0` là RỖNG, không phải PASS (quant-skeptic vòng 1: đúng cái nhãn
    # đó đã bị trích như một kết quả trong ngày đầu chưa có mốc nào). Nói thẳng ra cả 2 chỗ.
    inv_evaluated = n_cmp > 0
    print(f"[gate-3 bất biến] {'' if inv_evaluated else 'CHƯA ĐÁNH GIÁ ĐƯỢC (chưa có mốc) — '}"
          f"{len(viol)} vi phạm / {n_cmp} mã so được "
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
    n_nomodel = sum(1 for d in diverge if d.get("kind") == "NO_MODEL_VALUE")
    print(f"[gate-4 đối soát] {len(diverge) - n_nomodel} mã LỆCH + {n_nomodel} mã KHÔNG đối soát "
          f"được (mô hình từ chối trả số) giữa corp-action và ticker_financial")

    # ── LỚP 4b · diễn biến của fail-closed (xem `none_value_watch`)
    none_watch = none_value_watch(cur, prev_snap)
    print(f"[gate-4b im lặng] {none_watch['n_none']}/{none_watch['n_total']} mã bị TỪ CHỐI trả số"
          + (f" (mốc {prev_asof}: {none_watch['n_none_prev']}, Δ{none_watch['delta']:+d})"
             if none_watch["has_baseline"] else " — CHƯA ĐÁNH GIÁ ĐƯỢC diễn biến (chưa có mốc)")
          + (f" MỚI: {sorted(none_watch['newly_none'])}" if none_watch["newly_none"] else ""))

    # ── cổ tức tiền mặt rơi đúng hôm nay (GỘP, nguồn vendor — CHƯA đối soát tiền broker)
    # `include_announced=True` là BẮT BUỘC ở đây, không phải nới lỏng: vào 07:30 ngày ex-right,
    # dòng của chính ngày đó LUÔN còn `announced` (xem `_events_on_sql`). Trạng thái thật đi kèm
    # từng mã, và lượt chạy hôm sau xác nhận lại qua `confirm_prior_triggers()`.
    div_today = {}
    from dividend_adjusted_return import bq_corp_action
    ev_status = dividend_event_status(ev_rows, asof)
    for tk in sorted(ex_today):
        ca = bq_corp_action(tk, asof, include_announced=True)
        if not ca or not ca.get("cash"):
            continue
        holders = {lb: a["positions"][tk] for lb, a in pos.items() if tk in a["positions"]}
        div_today[tk] = {
            "cash_per_share_gross_vnd": ca["cash"], "stock_ratio": ca.get("stock"),
            "titles": ca.get("titles"), "holders_qty": holders,
            "event_status": ev_status.get(tk),
            "accrual_gross_vnd": {lb: q * ca["cash"] for lb, q in holders.items()},
            "basis": "GỘP, nguồn vendor corporate_action — CHƯA đối soát tiền broker. §21 buộc "
                     "mọi tỉ suất báo cáo đi qua dividend_adjusted_return.py, KHÔNG dùng số này."
                     + (" ⚠️ event_status=announced: DỰ KIẾN, chưa xác nhận — lượt chạy hôm sau "
                        "sẽ xác nhận lại." if ev_status.get(tk) != "executed" else "")}

    # ── LỚP 7 · phiên BỊ LỠ: phát hiện + backfill
    # Đặt SAU các cổng chặn có chủ đích: nếu selfcheck/feed/bất biến đỏ thì lượt này ghi
    # `*_FAILED.json`, mà `prior_snapshot` bỏ qua bản _FAILED ⇒ `prev_asof` KHÔNG nhích, nên ngày
    # hôm nay tự động trở thành "phiên bị lỡ" của lượt sau. Không cần cờ riêng cho ca đó.
    bf = backfill_missed(missed_trading_days(
        prev_asof, asof, (prev_snap or {}).get("backfill_deferred_days") or []))
    if bf["days_missed"]:
        print(f"[gate-5 phiên lỡ] {len(bf['days_missed'])} phiên lỡ {bf['days_missed']} — "
              f"backfill {len(bf['days_backfilled'])} ngày / {bf['n_events']} sự kiện; "
              f"hoãn lại {bf['deferred_days']}; lỗi {bf['errors']}")
    else:
        print("[gate-5 phiên lỡ] 0 — lượt chạy gần nhất là đúng phiên giao dịch liền trước")

    # ── vòng XÁC NHẬN: sự kiện đã ghi hôm trước giờ ra sao (huỷ? đã xác nhận? vẫn dự kiến?)
    confirmations = confirm_prior_triggers(prev_asof, prev_snap,
                                           backfilled=bf["events"], asof=asof)
    cancelled = [c for c in confirmations if c["kind"] in ("CANCELLED", "VANISHED")]
    timed_out = [c for c in confirmations if c["kind"] == "UNRESOLVED_TIMEOUT"]
    pending_next = carry_forward(confirmations)
    print(f"[xác nhận] {len(confirmations)} sự kiện đang theo dõi "
          f"(ngày sự kiện {sorted({c['event_date'] for c in confirmations}) or '—'}): "
          f"{len([c for c in confirmations if c['kind'] == 'CONFIRMED'])} CONFIRMED, "
          f"{len(pending_next)} còn dự kiến → mang sang lượt sau, "
          f"{len(timed_out)} quá {PENDING_MAX_CHECKS} lượt chưa ngã ngũ, "
          f"{len(cancelled)} HUỶ/BIẾN MẤT")

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
        # diễn biến fail-closed — publish RA snapshot để lượt sau có mốc so, và để người đọc lại
        # file này thấy được xu hướng mà không phải tự dựng lại từ `tickers`.
        "none_value_watch": none_watch,
        "invariant_violations": viol, "n_compared": n_cmp, "prev_snapshot_asof": prev_asof,
        # `0 vi phạm` với `n_compared == 0` KHÔNG phải PASS — không có gì để so. Ghi cờ ra
        # snapshot để người đọc (và mọi script đọc lại file này) không trích nhầm nó là kết quả.
        "invariant_evaluated": inv_evaluated,
        "prior_trigger_confirmations": confirmations,
        # phiên cron BỊ LỠ + kết quả backfill. `backfill_deferred_days` là hàng đợi sống: lượt
        # sau đọc lại đúng field này nên một ngày lỡ mà truy vấn hỏng KHÔNG mất — dù `prev_asof`
        # lúc đó đã nhảy qua nó.
        "missed_runs": {"prev_snapshot_asof": prev_asof, "days_missed": bf["days_missed"],
                        "days_backfilled": bf["days_backfilled"],
                        "n_events_backfilled": bf["n_events"],
                        "deferred_days": bf["deferred_days"], "errors": bf["errors"],
                        "backfill_ok": bf["ok"], "max_days_per_run": BACKFILL_MAX_DAYS},
        "backfill_deferred_days": bf["deferred_days"],
        "backfilled_events": bf["events"],
        # hàng CÒN TREO mang sang lượt sau — thứ biến vòng xác nhận từ một-phát-rồi-thôi thành
        # theo tới khi ngã ngũ. Lượt sau đọc lại đúng field này (`pending_items`).
        "pending_confirmations": pending_next,
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
    if bf["days_missed"]:
        # CẢNH BÁO RIÊNG, không gộp vào cảnh báo freshness (🕒): hai chuyện khác hẳn nhau — kia
        # là "bảng nguồn không có gì mới", đây là "CHÍNH TA đã không chạy". Gộp lại thì một sự cố
        # hạ tầng của mình đọc ra như một ngày yên ả của vendor.
        hit = sorted({r["ticker"] for r in bf["events"]} & set(held))
        lines.append(
            f"⏭️ **CRON BỊ LỠ {len(bf['days_missed'])} PHIÊN** (snapshot gần nhất {prev_asof} → "
            f"nay {asof}): {', '.join(bf['days_missed'])}. Đã backfill "
            f"{len(bf['days_backfilled'])}/{len(bf['days_missed'])} ngày, {bf['n_events']} sự "
            f"kiện" + (f"; mã ĐANG GIỮ dính: {hit}" if hit else "; không mã nào đang giữ dính")
            + (f". 🛑 backfill LỖI {[e['date'] for e in bf['errors']]}: "
               f"{bf['errors'][0]['error'][:120]}" if bf["errors"] else "")
            + (f". ⏸️ HOÃN sang lượt sau (trần {BACKFILL_MAX_DAYS} phiên/lượt): "
               f"{bf['deferred_days']}" if bf["deferred_days"] else "")
            + ". Kiểm vì sao cron không chạy trước khi tin số của khoảng này.")
    if upcoming:
        lines.append(f"📅 **Sự kiện quyền ≤{lookahead} ngày tới trên mã ĐANG GIỮ** ({asof}):")
        lines += [_fmt_event(e, holders_map) for e in upcoming[:15]]
        if len(upcoming) > 15:
            lines.append(f"… và {len(upcoming) - 15} sự kiện nữa — xem "
                         f"{os.path.relpath(snapshot_path(asof), WC_ROOT)}")
    if div_today:
        lines.append(f"💰 **Chốt quyền cổ tức tiền mặt HÔM NAY**: " + "; ".join(
            f"{tk} {v['cash_per_share_gross_vnd']:,.0f}đ/cp"
            # nhãn đi kèm TỪNG mã, không phải một dòng chú thích chung ở cuối: vào 07:30 sáng
            # ngày ex-right thì gần như mã nào cũng còn `announced`, và người đọc cần biết con
            # số nào là DỰ KIẾN ngay tại chỗ nó xuất hiện.
            f"{'' if v.get('event_status') == 'executed' else ' *(dự kiến)*'}"
            f"{' (giữ ' + ', '.join(f'{lb} {q:,}cp' for lb, q in v['holders_qty'].items()) + ')' if v['holders_qty'] else ''}"
            for tk, v in sorted(div_today.items())))
    if ais_today:
        lines.append(f"🧾 **AIS hiệu lực hôm nay** (số CP chính thức đổi): {sorted(ais_today)}")
    if diverge:
        lines.append(_fmt_divergence(diverge))
    if none_watch["alert"]:
        lines.append(
            f"🔇 **Số mã bị TỪ CHỐI trả số CP tăng**: {none_watch['n_none_prev']} → "
            f"{none_watch['n_none']}/{none_watch['n_total']} mã (so mốc {prev_asof})"
            + (f"; MỚI: " + ", ".join(f"{tk} ({m})"
                                      for tk, m in none_watch["newly_none"].items())
               if none_watch["newly_none"] else "")
            + (f"; lành lại: {none_watch['recovered']}" if none_watch["recovered"] else "")
            + ". Fail-closed nên KHÔNG có số sai nào được công bố — nhưng số mã không xác minh "
              "được đang nhiều lên, kiểm feed trước khi tin phần còn lại.")
    if viol:
        lines.append(f"🚨 **Bất biến số CP vi phạm** ({len(viol)} mã — số đã bị GIẤU, không "
                     f"publish giá trị): " + "; ".join(
                         f"{v['ticker']} {v['kind']} {v.get('err_pct', 0):.2f}%"
                         for v in viol[:8]))
    if cancelled:
        # Đây là cái giá PHẢI trả cho việc ghi trên `announced`: một khoản đã ghi hôm trước có
        # thể bị huỷ. Không báo = snapshot hôm qua sai vĩnh viễn và không ai biết.
        lines.append(f"🔁 **Sự kiện đã ghi nay ĐÃ HUỶ/BIẾN MẤT** "
                     f"({len(cancelled)} — snapshot ngày đó SAI, đọc lại trước khi dùng): " +
                     "; ".join(f"{c['ticker']} {c['event_code']} @{c['event_date']} "
                               f"{c['status_then']}→{c['status_now']}" for c in cancelled[:8]))
    if timed_out:
        # KHÔNG gộp vào `cancelled`: chưa có bằng chứng sai, chỉ là vendor im quá lâu. Nhưng cũng
        # KHÔNG được im — đây là lúc thôi mang tiếp, nên không báo bây giờ thì không bao giờ báo.
        lines.append(f"⏳ **Còn `announced` sau {PENDING_MAX_CHECKS} lượt kiểm — thôi theo dõi, "
                     f"cần người xem** ({len(timed_out)}): " +
                     "; ".join(f"{c['ticker']} {c['event_code']} @{c['event_date']} "
                               f"(từ {c['first_seen_asof']})" for c in timed_out[:8]))
    if status == "STALE" and streak >= 2:
        lines.append(f"🕒 `corporate_action` không nạp thêm gì {streak} ngày liên tiếp "
                     f"(gần nhất {fresh.get('max_ingested_ict')}) — sự kiện MỚI công bố hôm nay "
                     f"có thể chưa có trong bảng.")
    if stale_pos:
        lines.append(f"📄 Vị thế đọc từ artifact CŨ: {stale_pos} (ngày) — danh sách mã đang giữ "
                     f"có thể thiếu mã mới mua.")

    if lines and alert:
        # phiên bị lỡ ⇒ Telegram: đây là sự cố HẠ TẦNG của chính mình (cron chết/timeout), loại
        # việc mà nếu chỉ nằm trong Discord thì có thể trôi qua đúng những ngày không ai đọc.
        notify("\n".join(lines),
               telegram=(bool(viol) or bool(cancelled) or bool(bf["days_missed"]) or streak >= 5))
    elif not lines:
        print("[quiet] không có sự kiện/lệch/vi phạm nào — không ping Discord")
    if lines and not alert:
        # `--no-alert` phải cho xem ĐƯỢC cái sẽ gửi. Không in ra thì cách duy nhất để kiểm chuỗi
        # thật là để nó ping người thật — và đúng lỗi hiển thị TCB 2026-08-13 đã sống qua nhiều
        # vòng review vì không ai đọc chuỗi cuối cùng, chỉ đọc dict.
        print("[dry] tin nhắn SẼ gửi:\n" + "\n".join(lines))

    bus("finding" if not viol else "error",
        f"corp-action-daily {asof} {'OK' if not viol else 'CÓ VI PHẠM BẤT BIẾN'}",
        {"asof": asof, "feed_status": status, "n_track": len(track), "n_held": len(held),
         "exright_today": sorted(ex_today), "ais_today": sorted(ais_today),
         "cash_dividend_today": sorted(div_today), "n_upcoming_held": len(upcoming),
         # tách HAI loại: "hai nguồn nói khác nhau" và "mô hình từ chối trả số" là hai tình trạng
         # khác hẳn nhau; gộp thành một con số là đúng cái nhầm lẫn dòng Discord từng mắc.
         "n_crosscheck_divergent": len(diverge) - n_nomodel,
         "n_crosscheck_no_model_value": n_nomodel,
         "n_none_value": none_watch["n_none"], "none_value_alert": none_watch["alert"],
         "n_invariant_violations": len(viol),
         # `n_invariant_violations: 0` một mình là mơ hồ — kèm luôn cờ "có so được gì không"
         # để người đọc bus không phải mở snapshot mới biết con số 0 đó có nghĩa hay không.
         "invariant_evaluated": inv_evaluated, "n_compared": n_cmp,
         "n_prior_cancelled": len(cancelled), "n_pending_confirmations": len(pending_next),
         "n_unresolved_timeout": len(timed_out),
         "missed_sessions": bf["days_missed"], "n_backfilled_events": bf["n_events"],
         "backfill_ok": bf["ok"], "backfill_deferred_days": bf["deferred_days"],
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
