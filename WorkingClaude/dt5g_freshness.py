# -*- coding: utf-8 -*-
"""dt5g_freshness.py — "publisher CỦA TA đã chạy xong hôm nay chưa?" cho các consumer ĐỌC.

VÌ SAO KHÔNG HỎI THẲNG BẢNG BQ: `tav2_bq.vnindex_5state_dt5g_live` có HAI writer —
publisher của ta (daily_refresh step [12] ~18:35 + bq_freshness_check ~19:01) và pipeline
kaffa_v2 của team dữ liệu (~17:12 ICT, implementation DT5G RIÊNG). Kaffa đẩy MAX(time) =
hôm nay từ 17:12, nên `SELECT ... ORDER BY time DESC LIMIT 1` PASS kể cả khi chain của ta
chết sạch — consumer tưởng đang đọc state hôm nay của engine ta, thực ra không phải.
Truy vết: mike/agents/Winston/dt5g_live_second_writer_20260729.md.

NGUỒN SỰ THẬT DUY NHẤT = `deploy_golive_dt5g_v4/golive_state_today.json` — file này CHỈ
`publish_gated_state.py` ghi được (writer ngoài không chạm tới), nên nó là bằng chứng
publisher của ta thật sự đã chạy. Cùng bộ điều kiện mà gate chặn cứng
`mike/bin/bq_freshness_check.sh` (§ publisher-evidence, ~dòng 225-272) đang dùng:
    as_of == phiên giao dịch gần nhất  AND  bq_publish_ok == true
    AND (nếu hôm nay LÀ phiên) mtime của file == hôm nay
Ngày KHÔNG giao dịch (lễ giữa tuần, cron vẫn chạy T2-T6): bỏ điều kiện mtime — nếu không
sẽ báo oan mọi ngày lễ.

⚠️ Bản bash trong bq_freshness_check.sh vẫn là gate CHẶN của pipeline 19:00 và CỐ Ý không
bị đụng tới trong job này (sửa gate chặn = rủi ro vận hành lớn hơn lợi ích). Module này chỉ
phục vụ các consumer CHỈ-CẢNH-BÁO chạy SAU đó (eod_trading_report 19:10, pt_8l_daily 19:20,
rating_8l). Hai bản đọc CÙNG artifact với CÙNG luật; đổi luật thì phải sửa cả hai — việc gộp
bash gate về gọi module này là follow-up nên làm, chưa làm hôm nay.

Dùng:
    from dt5g_freshness import dt5g_publisher_evidence
    ev = dt5g_publisher_evidence()          # {"is_stale":bool, "reason":str, ...}

    python3 dt5g_freshness.py --warn-line   # in 1 dòng cảnh báo nếu stale, im nếu tươi
    python3 dt5g_freshness.py --json
Luôn exit 0 — đây là cảnh báo, KHÔNG phải gate.
"""
import datetime
import json
import os
import sys

WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
STATE_JSON = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_state_today.json")
ICT = datetime.timezone(datetime.timedelta(hours=7))

WARN_LINE = ("⚠️ Trạng thái DT5G có thể là dữ liệu HÔM QUA (publisher chưa xác nhận xong "
             "lúc báo cáo này chạy) — xem lại trước khi dùng để quyết định.")


def _ict_today():
    """Hôm nay theo giờ VN — tính tường minh UTC+7, KHÔNG dựa vào TZ hệ thống (cron chạy UTC)."""
    return datetime.datetime.now(ICT).date()


def _last_trading_day(today):
    """Phiên giao dịch gần nhất <= today (T7/CN + lịch nghỉ VN)."""
    try:
        sys.path.insert(0, WORKDIR)
        from trading_bot.vn_market import is_holiday
    except Exception:
        is_holiday = lambda d: False   # noqa: E731 — thiếu module thì chỉ bỏ qua lễ, vẫn né T7/CN
    d = today
    trading_today = not (d.weekday() >= 5 or is_holiday(d))
    while d.weekday() >= 5 or is_holiday(d):
        d -= datetime.timedelta(days=1)
    return d, trading_today


def dt5g_publisher_evidence(today=None, state_json=None):
    """Publisher DT5G CỦA TA đã chạy xong cho phiên gần nhất chưa?

    Trả dict: is_stale (bool), reason (str, "" khi tươi), as_of, published_at,
    bq_publish_ok, mtime_date, last_trading_day, is_trading_today.
    KHÔNG bao giờ raise — consumer là báo cáo, một lỗi đọc file không được giết báo cáo.
    """
    path = state_json or STATE_JSON
    today = today or _ict_today()
    out = {"is_stale": True, "reason": "", "as_of": None, "published_at": None,
           "bq_publish_ok": None, "mtime_date": None,
           "last_trading_day": None, "is_trading_today": None}
    try:
        ltd, trading_today = _last_trading_day(today)
        out["last_trading_day"], out["is_trading_today"] = str(ltd), trading_today
        if not os.path.exists(path):
            out["reason"] = f"{os.path.basename(path)} KHÔNG TỒN TẠI — publisher của ta chưa từng chạy"
            return out
        d = json.load(open(path, encoding="utf-8"))
        out["as_of"] = d.get("as_of")
        out["published_at"] = d.get("published_at")
        out["bq_publish_ok"] = bool(d.get("bq_publish_ok"))
        mdate = datetime.datetime.fromtimestamp(os.path.getmtime(path), ICT).date()
        out["mtime_date"] = str(mdate)
        if str(out["as_of"]) != str(ltd):
            out["reason"] = f"as_of={out['as_of']} ≠ phiên gần nhất {ltd}"
        elif not out["bq_publish_ok"]:
            out["reason"] = "bq_publish_ok=false — publish lên BQ đã HỎNG"
        elif trading_today and mdate != today:
            out["reason"] = f"mtime={mdate} ≠ hôm nay {today} — publisher của ta KHÔNG chạy hôm nay"
        out["is_stale"] = bool(out["reason"])
    except Exception as ex:
        out["is_stale"], out["reason"] = True, f"không đọc được bằng chứng publisher ({ex})"
    return out


def dt5g_warn_line(today=None, state_json=None):
    """Dòng cảnh báo để chèn ĐẦU báo cáo, hoặc "" khi state tươi."""
    ev = dt5g_publisher_evidence(today, state_json)
    if not ev["is_stale"]:
        return ""
    return f"{WARN_LINE} (chi tiết: {ev['reason']})"


if __name__ == "__main__":
    args = sys.argv[1:]
    ev = dt5g_publisher_evidence()
    if "--json" in args:
        print(json.dumps(ev, ensure_ascii=False))
    else:                      # --warn-line (mặc định): im lặng khi tươi, 1 dòng khi cũ
        line = dt5g_warn_line()
        if line:
            print(line)
    sys.exit(0)
