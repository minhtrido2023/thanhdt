#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""selfcheck_baseline_diff.py <baseline.json> <result.json> <results.jsonl>

Tầng SO SÁNH + ESCALATE của bin/selfcheck_weekly_baseline_check.sh. Tách khỏi heredoc bash để
(a) test được bằng import, (b) không phải sửa logic escalation bên trong một chuỗi bash.

VÌ SAO CÓ FILE NÀY (job Wags_20260812_112724, sự cố 2026-08-10 → 12):
4 selfcheck (extreme_regime, hard_no_chase_ceiling, paper_main_window, t2_settlement) ĐỎ từ
2026-08-10 mà không ai biết suốt 2 ngày. Điều tra cho thấy **KHÔNG PHẢI không ai quét** —
`state/selfcheck_runs.json` đã ghi extreme_regime + hard_no_chase_ceiling FAIL đúng
2026-08-10T12:05:23Z. Ba lỗ hổng thật, đây là chỗ vá 2 cái đầu:

  L1. Kết quả chỉ nằm trong file JSON + prompt LLM hàng tuần ⇒ KHÔNG có escalation xác định
      (deterministic) tới người. Nay: bus `question` 1-lần-1-ca + ack + Discord topic.
  L2. `new_red` KHÔNG BAO GIỜ được ghi vào `known_red` ⇒ mỗi lần chạy lại báo y hệt. Ở nhịp
      tuần đó là 1 lần lặp/tuần (chịu được); nâng lên nhịp NGÀY mà không vá thì thành bão báo
      động giả — đúng lớp lỗi ~/.claude/skills/close-the-loop mô tả. Nay: escalate xong thì
      GHI NGAY vào known_red kèm `topic`+`escalated_utc` ⇒ đúng 1 lần/ca.
  L3. (vá ở script gọi) phạm vi chỉ có gốc WorkingClaude, thiếu `mike/bin/*_selfcheck.py`.

BẤT BIẾN QUAN TRỌNG — dùng ĐỊNH DANH, không dựng lại chuỗi topic:
`known_red[file]["topic"]` LƯU nguyên văn topic câu hỏi đã đăng; lúc ca đó xanh lại, answer
đóng vòng đọc topic TỪ ĐÓ chứ không ghép lại từ tên file. Đây là fix cấu trúc cho bug B của
close-the-loop (tra cứu bằng chuỗi tự dựng ⇒ "không tìm thấy" âm thầm hoá thành "vẫn treo").
Topic answer CHỨA nguyên topic câu hỏi ⇒ khớp `_resolved()` của ops_health_check.sh
(điều kiện: r == q hoặc q in r, và r_ts >= q_ts).

Entry known_red do NGƯỜI curate (không có `auto: true`, vd immutable_publish với lý do IAM)
được tôn trọng: không escalate, và khi xanh lại chỉ gỡ + in ra, KHÔNG đăng answer (không có
câu hỏi nào của ta để đóng).

Env cho test: SC_BUS_CMD / SC_DISCORD_CMD (đường dẫn script thay thế), SC_NO_SIDE_EFFECTS=1.
"""
import datetime as dt
import json
import os
import subprocess
import sys

MIKE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPIC_PREFIX = "selfcheck-red: "
ACK_PREFIX = "triaged-needs-human: "     # phải khớp ACK_PREFIX trong bin/ops_health_check.sh
DISCORD_CHANNEL = "architecture"         # tên trong kb/discord_channels.json, KHÔNG hardcode ID
AGENT = "Wags"


def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t=None):
    return (t or now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd, timeout=90):
    if os.environ.get("SC_NO_SIDE_EFFECTS") == "1":
        print("[no-side-effects] %s" % " ".join(cmd[:4]))
        return True
    try:
        subprocess.run(cmd, check=True, timeout=timeout,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        print("⚠️ lệnh thất bại (%s): %s" % (cmd[0], e))
        return False


def bus(etype, topic, payload):
    cmd = os.environ.get("SC_BUS_CMD") or os.path.join(MIKE_ROOT, "bin", "append_event.sh")
    return _run([cmd, AGENT, etype, topic, json.dumps(payload, ensure_ascii=False)])


def discord(msg):
    cmd = os.environ.get("SC_DISCORD_CMD") or os.path.join(MIKE_ROOT, "bin", "notify_thread.sh")
    return _run([cmd, msg, DISCORD_CHANNEL])


def save_baseline(path, baseline):
    """Ghi nguyên tử: kill giữa chừng không để lại baseline cụt (mất known_red = escalate lại
    TOÀN BỘ lần sau)."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(baseline, f, ensure_ascii=False, indent=2, sort_keys=False)
    os.replace(tmp, path)


def load_results(jsonl_path):
    results = {}
    with open(jsonl_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            results[rec["file"]] = rec["status"]
    return results


def diff_and_escalate(baseline_path, result_path, jsonl_path, min_files=60):
    results = load_results(jsonl_path)

    # ANTI-EMPTY-SCAN: quét ra quá ít file ⇒ KHÔNG kết luận gì. Một scanner hỏng trả về rỗng sẽ
    # (a) báo "0 đỏ" và (b) gỡ SẠCH known_red vì "mọi ca đều xanh" — vừa mù vừa xoá trí nhớ.
    # Bài học round-5 commit-collision (Wags 2026-08-12): sai thì phát hiện được, rỗng thì không.
    if len(results) < min_files:
        msg = ("❌ selfcheck baseline diff: chỉ có %d kết quả (<%d) — RUNNER HỎNG hoặc glob sai. "
               "KHÔNG kết luận gì về trạng thái selfcheck, KHÔNG đụng baseline." % (len(results), min_files))
        print(msg)
        discord(msg)
        return 2

    with open(baseline_path, encoding="utf-8") as f:
        baseline = json.load(f)
    known_red = baseline.setdefault("known_red", {})

    new_red = {k: v for k, v in results.items() if v != "PASS" and k not in known_red}
    now_green = [k for k in known_red if results.get(k) == "PASS"]
    still_red_known = [k for k, v in results.items() if v != "PASS" and k in known_red]

    # ── ca ĐỎ MỚI: escalate ĐÚNG 1 LẦN rồi ghi vào known_red NGAY (L2).
    #    Ghi sau MỖI ca chứ không gom cuối vòng: bị kill giữa chừng thì ca đã báo không báo lại,
    #    ca chưa báo vẫn báo lần sau — không nuốt im lặng (coding_guidelines §5).
    escalated = []
    for f, status in sorted(new_red.items()):
        topic = TOPIC_PREFIX + f
        ok = bus("question", topic, {
            "question": "Selfcheck `%s` ĐỎ (%s) — chủ sở hữu file cần xác định: assertion đã lỗi "
                        "thời (production đổi hành vi CÓ CHỦ ĐÍCH) hay production thật sự hỏng? "
                        "Wags chỉ dựng cơ chế phát hiện, KHÔNG tự sửa logic giao dịch." % (f, status),
            "file": f, "status": status,
            "reproduce": "bash mike/bin/selfcheck_weekly_baseline_check.sh  (env đúng: "
                         "$DNA_PYEXE + GOOGLE_APPLICATION_CREDENTIALS, xem kb/selfcheck_baseline.json"
                         ".required_env — chạy bằng system python3 sẽ ra FAIL GIẢ)",
            "urgency": "normal",
            "source": "bin/selfcheck_baseline_diff.py",
        })
        if not ok:
            continue   # đăng hỏng ⇒ KHÔNG ghi known_red ⇒ lần sau thử lại, không nuốt cảnh báo
        # Ack "chờ NGƯỜI": câu hỏi này thuộc chủ sở hữu file (Taylor/DollarBill/Winston) hoặc cần
        # user quyết — wags_autofix KHÔNG sửa được logic giao dịch. Không ack thì mỗi ngày
        # ops_health_check dispatch 2-4 job Wags cho việc đã báo (đúng ca thật 2026-08-03).
        bus("status", ACK_PREFIX + topic,
            {"reason": "selfcheck đỏ cần chủ sở hữu file hoặc user quyết; Wags chỉ phát hiện",
             "suppress_days": 14})
        known_red[f] = {"reason": "TỰ PHÁT HIỆN bởi selfcheck_baseline_diff.py — CHƯA AI TRIAGE. "
                                  "Đây KHÔNG phải 'đỏ đã chấp nhận': nó nằm đây chỉ để không báo "
                                  "động lặp mỗi ngày. Xử lý xong thì XOÁ entry này.",
                        "since": iso(), "status": status, "auto": True,
                        "topic": topic, "escalated_utc": iso(),
                        "fix_needed": "chủ sở hữu file xác định assertion lỗi thời vs production hỏng"}
        save_baseline(baseline_path, baseline)
        escalated.append(f)

    # ── ca ĐÃ XANH LẠI: gỡ khỏi known_red + tự đóng câu hỏi cũ kèm BẰNG CHỨNG (close-the-loop A)
    for f in now_green:
        entry = known_red[f]
        topic = entry.get("topic")
        if topic and entry.get("auto"):
            bus("answer", "%s — recovered %s" % (topic, now().strftime("%Y-%m-%d")),
                {"context": "selfcheck_baseline_diff tự đóng: ca đỏ này đã XANH trở lại",
                 "file": f, "artifact": "chạy lại lúc %s bằng đúng required_env ⇒ PASS" % iso(),
                 "red_since": entry.get("since"), "was_status": entry.get("status"),
                 "decided_by": "automation (bằng chứng chạy lại, không phải self-report)"})
        del known_red[f]
        save_baseline(baseline_path, baseline)

    out = {"ts": iso(), "total": len(results),
           "pass": sum(1 for v in results.values() if v == "PASS"),
           "new_red": new_red, "escalated": escalated,
           "now_green_removed_from_baseline": now_green,
           "still_red_known": still_red_known, "raw": results}
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # ── Discord: CHỈ khi có thay đổi (đỏ mới / xanh lại). Không có gì mới thì im lặng ở đây —
    #    người vẫn thấy tình trạng qua ops_health_check check #11 (đọc baseline + mtime kết quả),
    #    nên im lặng ở đây KHÔNG đồng nghĩa "không phân biệt được với cron chết".
    if escalated or now_green:
        parts = ["🔴 **Selfcheck baseline sweep** — %d file, %d PASS."
                 % (out["total"], out["pass"])]
        if escalated:
            parts.append("**%d ca ĐỎ MỚI** (mỗi ca 1 bus `question` + ack, escalate ĐÚNG 1 lần):"
                         % len(escalated))
            parts += ["• `%s` — %s" % (f, new_red[f]) for f in escalated]
        if still_red_known:
            parts.append("(%d ca đỏ ĐÃ BIẾT, không báo lại: %s)"
                         % (len(still_red_known), ", ".join("`%s`" % f for f in sorted(still_red_known))))
        if now_green:
            parts.append("✅ **%d ca XANH TRỞ LẠI** (đã gỡ khỏi baseline, câu hỏi cũ tự đóng kèm "
                         "bằng chứng): %s" % (len(now_green), ", ".join("`%s`" % f for f in now_green)))
        parts.append("Chi tiết: `%s`" % os.path.relpath(result_path, os.path.dirname(MIKE_ROOT)))
        discord("\n".join(parts))

    if escalated:
        print("NEW_RED: %d file(s) — đã escalate + ghi vào known_red: %s" % (len(escalated), escalated))
    failed_to_post = sorted(set(new_red) - set(escalated))
    if failed_to_post:
        print("⚠️ %d ca đỏ mới KHÔNG đăng được lên bus (sẽ thử lại lần sau): %s"
              % (len(failed_to_post), failed_to_post))
    if now_green:
        print("BASELINE_UPDATED: %d file(s) gỡ khỏi known_red (đã xanh): %s" % (len(now_green), now_green))
    if not new_red:
        print("OK: %d/%d PASS, %d known-red không đổi" % (out["pass"], out["total"], len(still_red_known)))
    return 1 if new_red else 0


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit("usage: selfcheck_baseline_diff.py <baseline.json> <result.json> <results.jsonl>")
    sys.exit(diff_and_escalate(sys.argv[1], sys.argv[2], sys.argv[3],
                               min_files=int(os.environ.get("SC_MIN_FILES") or 60)))
