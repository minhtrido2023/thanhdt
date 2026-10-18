#!/usr/bin/env python3
"""gate_source_check.py — báo NGUỒN CỔNG get_gated_state() của CHÍNH lượt publish 19:00.

VÌ SAO (retro 2026-10-11 Pattern I, user duyệt 2026-10-12 11:01 ICT): cổng rơi về DT4_only ở mọi
lần gọi mà không dòng nào nói ra; check 13 của ops_health_check.sh chỉ kêu 08:20 sáng hôm sau,
tức SAU khi plan T+1 đã được duyệt. File này chạy ngay sau [pipeline-1] publish_gated_state của
bin/bq_freshness_check.sh — bản publish mà DollarBill đọc để lập plan — nên cảnh báo tới trước
lúc duyệt.

CHỈ CẢNH BÁO, KHÔNG CHẶN: DT4_only là fail-closed đúng thiết kế; duyệt plan hay không là quyết
định của user. Luôn thoát 0. source == DT5G_macro ⇒ KHÔNG in, KHÔNG ghi, KHÔNG gửi gì.

Nguyên nhân trong tin chỉ là BẰNG CHỨNG của lượt này (§29), không suy diễn: dòng
`[get_gated_state] …` cổng tự in trong output lượt publish (--publish-log) + status/ts của
data/macro_health.json. Không có dòng cổng ⇒ nói "không tìm thấy".

Khi source khác DT5G_macro (DT4_only, DT4_STALE, giá trị lạ, thiếu trường, file hỏng):
  1. một tin Discord topic trading_daily (bin/notify_thread.sh),
  2. một bus event `error` topic dt5g-gate-source-degraded-<ngày publish>,
  3. data/gate_source_alert.json — bằng chứng để send_plan_report.sh in một dòng vào báo cáo plan
     (plan_report_line() bên dưới; dòng đó đọc NGUỒN từ chính golive_state_today.json, file này
     chỉ cấp phần bằng chứng và bị bỏ qua nếu không thuộc đúng bản publish đang hiển thị).
Khoá chống lặp theo TỪNG CẶP (ngày publish theo mtime file state, nguồn): chạy lại chuỗi cùng ngày
không gửi lại kênh đã gửi cho cặp đó, kể cả khi giữa chừng có lượt ra nguồn khác. Kênh gửi HỎNG thì
chưa đánh dấu (§5) — nhưng KHÔNG có lượt tự chạy lại cùng ngày: lưới còn lại là kênh kia, dòng ⚠️
trong báo cáo plan 21:00 và check 13 của ops_health_check.sh sáng hôm sau. Không ghi được file dấu
(data/ chỉ-đọc, đĩa đầy) ⇒ VẪN gửi, chỉ mất chống lặp + mất bằng chứng cho báo cáo plan.

Lượt publish KHÔNG ghi file state (mtime < --since-epoch, hoặc file không tồn tại) ⇒ bỏ qua:
_assert_fresh_artifact của bq_freshness_check.sh đã chặn + báo ca đó, không báo trùng.

    python3 mike/bin/gate_source_check.py --workdir WC --publish-log F --since-epoch N --alert
"""
import argparse
import datetime as dt
import json
import os
import subprocess
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
GOOD_SOURCE = "DT5G_macro"
# Hai nguồn cổng CHỦ ĐỘNG trả khi bỏ macro cap (macro_state_live.get_gated_state: use_macro=False).
NO_CAP_SOURCES = ("DT4_only", "DT4_STALE")
MISSING_SOURCE = "<thiếu trường source>"
UNREADABLE = "<không đọc được file state>"
CHANNEL = "trading_daily"
GATE_PREFIX = "[get_gated_state]"
STATE_REL = os.path.join("deploy_golive_dt5g_v4", "golive_state_today.json")
HEALTH_REL = os.path.join("data", "macro_health.json")
MARKER_REL = os.path.join("data", "gate_source_alert.json")
# Trần mỗi lần gọi kênh báo. Biến môi trường chỉ để selfcheck rút ngắn, production không đặt.
SEND_TIMEOUT_S = float(os.environ.get("GATE_SOURCE_SEND_TIMEOUT_S") or 60)
# Lưới còn lại khi một kênh gửi hỏng (không có lượt tự chạy lại cùng ngày).
NETS = {"discord": "bus event error", "bus": "tin Discord Trading Daily"}
_DEGRADED_SEEN = ""     # nguồn suy giảm đã THẤY ở lượt này — để câu WARN cuối file nói đúng thực tế


def _err(exc):
    return f"{type(exc).__name__}: {str(exc)[:160]}"


def read_state(workdir):
    """(doc|None, lỗi thật|"") của golive_state_today.json."""
    try:
        with open(os.path.join(workdir, STATE_REL), encoding="utf-8") as f:
            doc = json.load(f)
        if not isinstance(doc, dict):
            return None, f"JSON không phải object ({type(doc).__name__})"
        return doc, ""
    except Exception as exc:                                        # noqa: BLE001
        return None, _err(exc)


def source_of(doc):
    """Nguồn đã chuẩn hoá: chuỗi nguyên văn, hoặc MISSING_SOURCE khi thiếu trường / null."""
    src = doc.get("source")
    return MISSING_SOURCE if src is None else str(src)


def gate_line(publish_log):
    """Dòng `[get_gated_state] …` CUỐI trong output lượt publish này; không có ⇒ nói thẳng."""
    if not publish_log or publish_log == os.devnull:
        return "", "output lượt publish không được giữ lại"
    try:
        with open(publish_log, encoding="utf-8", errors="replace") as f:
            hits = [ln.strip() for ln in f if ln.strip().startswith(GATE_PREFIX)]
    except OSError as exc:
        return "", f"không đọc được output lượt publish ({_err(exc)})"
    if not hits:
        return "", "không tìm thấy dòng [get_gated_state] trong output lượt publish này"
    return hits[-1][:300], ""


def health_evidence(workdir):
    """status + ts của macro_health.json, nguyên văn — không diễn giải."""
    try:
        with open(os.path.join(workdir, HEALTH_REL), encoding="utf-8") as f:
            h = json.load(f)
        return (f"status={h.get('status')}, ts={h.get('ts')}, "
                f"recommended_state_source={h.get('recommended_state_source')}")
    except Exception as exc:                                        # noqa: BLE001
        return f"KHÔNG đọc được ({_err(exc)})"


def _evidence_text(line, line_why, health):
    return (f"dòng cổng tự in: {'«' + line + '»' if line else line_why} · "
            f"data/macro_health.json: {health}")


def _cap_clause(src):
    if src in NO_CAP_SOURCES:
        return "state này KHÔNG áp macro cap (cổng fail-closed về DT4)"
    return "KHÔNG xác nhận được state này có áp macro cap hay không"


def load_marker(workdir):
    try:
        with open(os.path.join(workdir, MARKER_REL), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save_marker(workdir, marker):
    """Ghi dấu (atomic). Trả lỗi thật ("" = ghi được) — ghi hỏng KHÔNG được nuốt Discord/bus."""
    path = os.path.join(workdir, MARKER_REL)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(marker, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return ""
    except OSError as exc:
        return _err(exc)


def _run(cmd):
    """(ok, lỗi thật) — kênh báo hỏng không được làm chết bước kiểm."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=SEND_TIMEOUT_S)
    except Exception as exc:                                        # noqa: BLE001
        return False, _err(exc)
    return r.returncode == 0, f"rc={r.returncode} {(r.stderr or r.stdout).strip()[:200]}"


def plan_report_line(workdir):
    """Một dòng cho báo cáo plan (send_plan_report.sh); "" khi nguồn là DT5G_macro.

    File state thiếu/hỏng ⇒ "": ca đó đã có dòng "CHƯA đối chiếu được state plan" của gate state
    ngay cạnh, không in hai dòng cho một nguyên nhân."""
    doc, _ = read_state(workdir)
    if doc is None:
        return ""
    src = source_of(doc)
    if src == GOOD_SOURCE:
        return ""
    m = load_marker(workdir)
    if m.get("source") == src and m.get("published_at") == doc.get("published_at"):
        ev = "Bằng chứng lượt publish: " + _evidence_text(
            m.get("gate_line") or "", m.get("gate_line_why") or "", m.get("health") or "?")
    else:
        ev = ("Không có bằng chứng nguyên nhân của đúng lượt publish này (bước kiểm 19:00 không "
              "ghi lại) — xem mike/logs/bq_freshness.log")
    return (f"⚠️ **Cổng DT5G SUY GIẢM**: bản publish {doc.get('published_at')} (as_of "
            f"{doc.get('as_of')}) ra nguồn {src}, không phải {GOOD_SOURCE} ⇒ {_cap_clause(src)}. "
            f"Plan KHÔNG bị chặn — anh cân nhắc khi duyệt. {ev}.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--publish-log")
    ap.add_argument("--since-epoch", type=int, default=0)
    ap.add_argument("--alert", action="store_true", help="gửi Discord + bus (mặc định chỉ in)")
    a = ap.parse_args()

    state_path = os.path.join(a.workdir, STATE_REL)
    try:
        mtime = int(os.stat(state_path).st_mtime)   # giây nguyên, y như `stat -c %Y` của _assert_fresh_artifact
    except OSError:
        mtime = None
    if mtime is None or mtime < a.since_epoch:
        print(f"SKIP gate-source: lượt publish này không ghi {STATE_REL} "
              f"(mtime={'MISSING' if mtime is None else mtime} < {a.since_epoch}) — "
              f"_assert_fresh_artifact xử ca này, không báo trùng")
        return 0

    doc, read_err = read_state(a.workdir)
    src = UNREADABLE if doc is None else source_of(doc)
    if src == GOOD_SOURCE:
        return 0

    global _DEGRADED_SEEN
    _DEGRADED_SEEN = src
    doc = doc or {}
    pub = dt.datetime.fromtimestamp(mtime, ICT)
    publish_date = pub.date().isoformat()
    line, line_why = gate_line(a.publish_log)
    health = health_evidence(a.workdir)
    evidence = _evidence_text(line, line_why, health)
    if read_err:
        what = f"KHÔNG đọc được {STATE_REL} vừa ghi ({read_err}) ⇒ {_cap_clause(src)}"
    else:
        what = (f"ra nguồn {src} (không phải {GOOD_SOURCE}): as_of={doc.get('as_of')}, "
                f"state={doc.get('state')} (DT4 base={doc.get('base_state_dt4')}, DT5G macro="
                f"{doc.get('macro_state_dt5g')}), bq_publish_ok={doc.get('bq_publish_ok')} ⇒ "
                f"{_cap_clause(src)}")
    msg = (f"🟡 CỔNG DT5G SUY GIẢM ({publish_date} {pub:%H:%M} ICT): lượt publish của chuỗi EOD vừa xong "
           f"{what}. Plan T+1 sẽ lập trên state này. CHỈ CẢNH BÁO — pipeline và plan KHÔNG bị "
           f"chặn; duyệt plan hay không là quyết định của anh. Bằng chứng của chính lượt này — "
           f"{evidence}.")
    print(f"WARN gate-source: {msg}")

    # Khoá chống lặp theo TỪNG CẶP (ngày publish, nguồn): `sent` = {"<ngày>|<nguồn>": {kênh: True}}.
    # Chỉ giữ các cặp của CHÍNH ngày publish này (ngày khác = sự kiện mới, file không phình).
    key = f"{publish_date}|{src}"
    prev_sent = load_marker(a.workdir).get("sent")
    sent_all = {k: dict(v) for k, v in (prev_sent if isinstance(prev_sent, dict) else {}).items()
                if k.startswith(publish_date + "|") and isinstance(v, dict)}
    sent = sent_all.setdefault(key, {})
    marker = {"publish_date": publish_date, "source": src,
              "published_at": doc.get("published_at"), "as_of": doc.get("as_of"),
              "gate_line": line, "gate_line_why": line_why, "health": health, "sent": sent_all}

    def _mark():
        why = save_marker(a.workdir, marker)
        if why:
            print(f"  [WARN] gate-source: KHÔNG ghi được {MARKER_REL} — Lỗi thật: {why}. Nguồn "
                  f"suy giảm ĐÃ được phát hiện và vẫn báo qua Discord/bus; mất: chống lặp khi "
                  f"chạy lại + phần bằng chứng trong dòng ⚠️ của báo cáo plan 21:00.")

    _mark()                              # bằng chứng cho báo cáo plan — ghi kể cả khi không --alert
    if not a.alert:
        return 0

    sends = (
        ("discord", [os.path.join(MIKE_BIN, "notify_thread.sh"), msg, CHANNEL]),
        ("bus", [os.path.join(MIKE_BIN, "append_event.sh"), "Taylor", "error",
                 f"dt5g-gate-source-degraded-{publish_date}",
                 json.dumps({"publish_date": publish_date, "source": src, "blocking": False,
                             "state_file": {k: doc.get(k) for k in (
                                 "published_at", "as_of", "state", "base_state_dt4",
                                 "macro_state_dt5g", "bq_publish_ok")},
                             "state_file_error": read_err or None,
                             "gate_line": line or line_why, "macro_health": health},
                            ensure_ascii=False, default=str)]),
    )
    for kind, cmd in sends:
        if sent.get(kind):
            print(f"  [gate-source] {kind}: đã báo nguồn {src} cho lượt publish ngày "
                  f"{publish_date} — không gửi lại (§5)")
            continue
        ok, why = _run(cmd)
        if ok:
            sent[kind] = True
            _mark()                          # đánh dấu NGAY sau mỗi kênh, không gom cuối
        else:
            print(f"  [WARN] gate-source: gửi {kind} THẤT BẠI — Lỗi thật: {why}. Chưa đánh dấu; "
                  f"KHÔNG có lượt tự chạy lại cùng ngày — lưới còn lại: {NETS[kind]} (nếu gửi "
                  f"được), dòng ⚠️ trong báo cáo plan 21:00, check 13 ops_health_check sáng hôm sau.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:                                        # noqa: BLE001
        if _DEGRADED_SEEN:
            print(f"  [WARN] gate_source_check.py lỗi ({_err(exc)}) SAU KHI đã kiểm và THẤY nguồn "
                  f"cổng suy giảm ({_DEGRADED_SEEN}) — có thể CHƯA báo đủ Discord/bus, không chặn "
                  f"pipeline; xem dòng 'WARN gate-source' ngay trên và {STATE_REL}")
        else:
            print(f"  [WARN] gate_source_check.py lỗi ({_err(exc)}) — KHÔNG kiểm được nguồn cổng "
                  f"lượt publish này, không chặn pipeline; kiểm tay trường source trong {STATE_REL}")
        raise SystemExit(0)
