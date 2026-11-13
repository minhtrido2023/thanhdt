#!/usr/bin/env python3
"""decision_inbox_r2_selfcheck.py — ca ĐỐI KHÁNG vòng 2 (arch-review NEEDS_CHANGES 13/11), mục 1-6.

Mỗi khối tái hiện ĐÚNG lỗi reviewer đã tái hiện: FAIL trước khi sửa, PASS sau khi sửa.
Mục 7 (daily_retro.sh) ở bin/daily_retro_measured_by_selfcheck.sh; phần cog của mục 3/6 ở
bin/decision_inbox_cog_selfcheck.py.

Chạy: `env -u TZ python3 bin/decision_inbox_r2_selfcheck.py` và `TZ=America/New_York ...`
(MIKE_BOT_TEST_MODE=1 đặt sẵn; dùng --root tmpdir ⇒ KHÔNG đụng bus/kb thật).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
_dn = os.open(os.devnull, os.O_RDONLY)   # `remember.sh --set` đọc stdin: không bao giờ được treo selfcheck
os.dup2(_dn, 0)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decision_actions as da  # noqa: E402
import decision_inbox as di  # noqa: E402
from decision_inbox_selfcheck import Env, check as _chk, RESULTS  # noqa: E402

ROOT = HERE.parent


def check(name, cond, detail=""):
    _chk(name, cond, detail)


# ───────────── 1. chữ cái trả lời phải là ASCII A-H trong text gốc ─────────────
def item1():
    for text in ("Duyệt ạ", "ok ạ", "Chốt à", "chốt ạ!", "à", "pa ạ", "é", "ê", "đ", "ok đ", "ạ", "Duyệt đ"):
        check(f"1 parse_answer({text!r}) là None", di.parse_answer(text) is None, str(di.parse_answer(text)))
    for text, want in {"Duyệt A": ("A", None), "ok b": ("B", None), "A": ("A", None), "Chốt c.": ("C", None),
                       "Duyệt A #q1f2e3d": ("A", "q1f2e3d"), "PHƯƠNG ÁN d!": ("D", None),
                       "đồng ý H": ("H", None)}.items():
        check(f"1+ parse_answer({text!r})", di.parse_answer(text) == want, str(di.parse_answer(text)))


# ───────────── 2. reference_message_id ⇒ dừng, không rơi xuống T2/T3 ─────────────
def item2():
    # 2a: reply vào tin 999 không liên quan, trong thread có 1 câu normal đã surface
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-r2a", ["A: x", "B: y"])
        e.bot("b1", "c1", q["tag"])
        r = e.user("m1", "c1", "Duyệt A", ref="999")
        check("2a reply vào tin 999 không liên quan ⇒ KHÔNG đóng", e.answers() == [] and r["outcome"] != "closed", str(r))
        check("2a outcome no_binding", r["outcome"] == "no_binding", str(r))
        r = e.user("m2", "c1", "Duyệt A #" + q["tag"], ref="999")
        check("2a' reply tin lạ + thẻ tường minh ⇒ vẫn dừng (không rơi T2)", e.answers() == [] and r["outcome"] != "closed", str(r))
        r = e.user("m3", "c1", "Duyệt A")
        check("2a'' đối chứng: không reference ⇒ T3 vẫn đóng", r["outcome"] == "closed", str(r))

    # 2b: Q1 đã đóng + Q2 surface cùng thread; reply 'B' vào tin Q1 ⇒ không đóng Q2, on_answer không chạy
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        spec = {"B": [{"action": "append_event", "agent": "Mike", "type": "finding", "topic": "r2b-sideeffect",
                       "payload": {"x": 1}}]}
        q1 = e.q("Mike", "docs-r2b-one", ["A: x", "B: y"])
        q2 = e.q("Taylor", "docs-r2b-two", ["A: x", "B: y"], on_answer=spec)
        e.bot("b1", "c1", q1["tag"])
        r0 = e.user("m0", "c1", "A", ref="b1")
        check("2b setup: Q1 đóng qua reply-to", r0["outcome"] == "closed", str(r0))
        e.bot("b2", "c1", q2["tag"])
        r = e.user("m1", "c1", "B", ref="b1")
        check("2b reply 'B' vào tin Q1 (đã đóng) ⇒ KHÔNG đóng Q2", e.answers("docs-r2b-two") == [] and r["outcome"] != "closed", str(r))
        check("2b on_answer của Q2 KHÔNG chạy (không event r2b-sideeffect, không sổ actions)",
              e.statuses("r2b-sideeffect") == [] and not e.finding_topics("r2b-sideeffect")
              and e.state_rows("actions.jsonl") == [], str(r))
        r = e.user("m2", "c1", "B", ref="b1")
        check("2b lặp lại vẫn không đóng", e.answers("docs-r2b-two") == [], str(r))

    # 2c: T1 xung đột thẻ ⇒ nhập nhằng; khớp thẻ ⇒ đóng
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q1 = e.q("Mike", "docs-r2c-one", ["A: x", "B: y"])
        q2 = e.q("Taylor", "docs-r2c-two", ["A: x", "B: y"])
        e.bot("b1", "c1", q1["tag"])
        e.bot("b2", "c1", q2["tag"])
        r = e.user("m1", "c1", "A #" + q2["tag"], ref="b1")
        check("2c reply tin Q1 nhưng thẻ #Q2 ⇒ nhập nhằng, KHÔNG đóng gì",
              e.answers() == [] and r["outcome"] in ("ambiguous_asked", "ambiguous_suppressed"), str(r))
        r = e.user("m2", "c1", "A #" + q1["tag"], ref="b1")
        check("2c đối chứng: reply tin Q1 + thẻ #Q1 ⇒ đóng Q1", r["outcome"] == "closed" and r["ref"] == q1["ref"], str(r))


# ───────────── 3. T3 chỉ khi tin bot GẦN NHẤT là tin có thẻ + TTL 6h ─────────────
def item3():
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-r3a", ["A: x", "B: y"])
        e.bot("b1", "c1", q["tag"])
        e.note_untagged_bot("b2", "c1")          # cog ghi con trỏ cho cả tin bot KHÔNG thẻ
        r = e.user("m1", "c1", "A")
        check("3a 'A' sau một tin bot khác (không thẻ) ⇒ KHÔNG đóng", e.answers() == [] and r["outcome"] == "no_binding", str(r))
        r = e.user("m2", "c1", "A #" + q["tag"])
        check("3a' đối chứng: có thẻ tường minh ⇒ vẫn đóng", r["outcome"] == "closed", str(r))
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-r3b", ["A: x", "B: y"])
        e.bot("b1", "c1", q["tag"], now=e.now - dt.timedelta(days=30))
        r = e.user("m1", "c1", "A")
        check("3b câu surface 30 ngày trước ⇒ 'A' KHÔNG đóng", e.answers() == [] and r["outcome"] == "no_binding", str(r))
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-r3c", ["A: x", "B: y"])
        e.bot("b1", "c1", q["tag"])
        r = e.user("m1", "c1", "A", now=e.now + dt.timedelta(hours=7))
        check("3c sau 7h (> TTL 6h) ⇒ không đóng", e.answers() == [] and r["outcome"] == "no_binding", str(r))
        r = e.user("m2", "c1", "A", now=e.now + dt.timedelta(hours=5))
        check("3c' trong 5h + tin bot gần nhất là tin có thẻ ⇒ đóng qua thread", r["outcome"] == "closed"
              and r["matched_by"] == "thread", str(r))
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-r3d", ["A: x", "B: y"])
        e.bot("b1", "c1", q["tag"], pointer=False)      # cog không ghi con trỏ ⇒ fail-closed
        r = e.user("m1", "c1", "A")
        check("3d thiếu con trỏ last-bot ⇒ fail-closed, không đóng", e.answers() == [] and r["outcome"] == "no_binding", str(r))
    with tempfile.TemporaryDirectory() as td:   # con trỏ của channel KHÁC không cứu được
        e = Env(td)
        q = e.q("Mike", "docs-r3e", ["A: x", "B: y"])
        e.bot("b1", "c1", q["tag"])
        e.note_untagged_bot("b9", "c2")
        r = e.user("m1", "c1", "A")
        check("3e bot nhắn ở channel khác không làm mất ràng buộc channel này", r["outcome"] == "closed", str(r))


# ───────────── 4. phân loại money ─────────────
def item4():
    must_money = [("capit_margin_lever_reenable", {}), ("excluded_tickers_pnj", {}), ("stop-loss-tv1", {}),
                  ("x", {"options": ["A: Sell HPG", "B: giữ"]}),
                  ("x", {"summary": "Rút tiền thật … SpaceX 500tr"}),
                  ("x", {"summary": "bật đòn bẩy"}), ("x", {"summary": "mở leverage 1.5"}),
                  ("x", {"summary": "đổi broker"}), ("x", {"summary": "DNSE hạn mức"}),
                  ("x", {"summary": "approve plan"}), ("x", {"summary": "nạp tiền"}), ("x", {"summary": "Buy VNM"}),
                  ("stop_loss_rule", {}), ("capit-domain", {})]
    for topic, pl in must_money:
        got = di.classify_risk("Mike", topic, pl)
        check(f"4 money: {topic!r} {pl}", got == "money", got)
    for ag in ("DollarBill", "Mafee"):
        check(f"4 {ag} + payload risk=normal KHÔNG hạ được", di.classify_risk(ag, "docs", {"risk": "normal"}) == "money")
    check("4 đối chứng: docs-cleanup vẫn normal", di.classify_risk("Mike", "docs-cleanup", {"options": ["A", "B"]}) == "normal")
    check("4 đối chứng: agent thường + risk=normal tường minh vẫn là normal",
          di.classify_risk("Taylor", "docs-x", {"risk": "normal", "summary": "sửa lỗi chính tả"}) == "normal")


# ───────────── 5. chặn tiêm cờ vào remember.sh ─────────────
def item5():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "bin").mkdir()
        for f in ("remember.sh", "archive_memory.py"):
            shutil.copy(ROOT / "bin" / f, root / "bin" / f)
        (root / "kb" / "memory").mkdir(parents=True)
        (root / "kb" / "discord_channels.json").write_text(json.dumps({"channels": {"ops": "1"}}), encoding="utf-8")
        mem = root / "kb" / "memory" / "Mike.md"
        orig = "# Working memory — Mike\n\n- [2026-11-13T00:00:00Z] việc quan trọng phải còn nguyên\n"
        mem.write_text(orig, encoding="utf-8")
        for i, note in enumerate(("--clear", "--set x", " --clear", "-x")):
            qid = f"qid-r2-5-{i}"   # mỗi note 1 câu riêng: khoá idempotent không được che kết quả
            res = da.run_actions(root, qid, "A", [{"action": "remember", "agent": "Mike", "note": note}])
            check(f"5 remember note={note!r} ⇒ rejected", res[0]["status"] == "rejected", str(res))
            check(f"5 Mike.md KHÔNG đổi sau note={note!r}", mem.read_text(encoding="utf-8") == orig)
            # chạy lại với option khác để khoá idempotent không che
            da.run_actions(root, qid, "B", [{"action": "remember", "agent": "Mike", "note": note}])
        res = da.run_actions(root, "qid-r2-5ok", "A", [{"action": "remember", "agent": "Mike", "note": "ghi chú bình thường"}])
        check("5 đối chứng: note thường vẫn ghi được", res[0]["status"] == "done"
              and "ghi chú bình thường" in mem.read_text(encoding="utf-8") and "việc quan trọng" in mem.read_text(encoding="utf-8"), str(res))
        for msg in ("--help", " -x", "-"):
            errs = da.validate_action({"action": "notify_thread", "channel": "ops", "message": msg}, root)
            check(f"5 notify_thread message={msg!r} bị từ chối", bool(errs), str(errs))
        check("5 đối chứng: notify_thread message thường hợp lệ",
              da.validate_action({"action": "notify_thread", "channel": "ops", "message": "xong rồi"}, root) == [])


# ───────────── 6. intent vào sổ TRƯỚC khi đóng ─────────────
def item6():
    spec = {"A": [{"action": "append_event", "agent": "Mike", "type": "finding", "topic": "r2-6-effect",
                   "payload": {"x": 1}}]}
    # 6a: kill giữa chừng (BaseException) sau khi đóng, trước khi on_answer chạy
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-r2-6a", ["A: x", "B: y"], on_answer=spec)
        e.bot("b1", "c1", q["tag"])
        real = di._run_on_answer

        def killed(*a, **k):
            raise KeyboardInterrupt("simulated kill -9 giữa chừng")
        di._run_on_answer = killed
        try:
            try:
                e.user("m1", "c1", "A", ref="b1")
                died = False
            except KeyboardInterrupt:
                died = True
        finally:
            di._run_on_answer = real
        check("6a setup: tiến trình bị giết sau khi đóng", died and len(e.answers("docs-r2-6a")) == 1)
        intents = e.state_rows("intents.jsonl")
        check("6a intent đã nằm trong sổ TRƯỚC khi đóng (còn nguyên sau khi bị giết)",
              any(r.get("state") == "intent" and r.get("question_event_id") == q["eid"] and r.get("option") == "A"
                  and r.get("has_on_answer") for r in intents) and not any(r.get("state") == "done" for r in intents), str(intents))
        check("6a on_answer chưa chạy (đúng như mô phỏng)", e.finding_topics("r2-6-effect") == [])
        e.note_untagged_bot("b2", "c1")
        e.run({"kind": "bot_message", "message_id": "b2", "channel_id": "c1", "content": "tin sau, không thẻ"})
        errs = e.state_rows("errors.jsonl")
        bus = e.statuses("decision-inbox-error")
        check("6a lần xử lý kế tiếp BÁO intent mồ côi (state errors.jsonl)",
              any(r.get("kind") == "intent_orphan" and r.get("question_event_id") == q["eid"] for r in errs), str(errs))
        check("6a … và lên bus (status decision-inbox-error)",
              any(r["payload"].get("kind") == "intent_orphan" for r in bus), str(bus))
        e.run({"kind": "bot_message", "message_id": "b3", "channel_id": "c1", "content": "tin sau nữa, không thẻ"})
        check("6a chỉ báo MỘT lần (không spam mỗi sự kiện)",
              len([r for r in e.state_rows("errors.jsonl") if r.get("kind") == "intent_orphan"]) == 1)
    # 6b: đường thường ⇒ intent có `done`, không báo mồ côi
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-r2-6b", ["A: x", "B: y"], on_answer=spec)
        e.bot("b1", "c1", q["tag"])
        r = e.user("m1", "c1", "A", ref="b1")
        check("6b đường thường: closed + action done", r["outcome"] == "closed"
              and r.get("actions", [{}])[0].get("status") == "done", str(r))
        rows = e.state_rows("intents.jsonl")
        check("6b sổ intent có cả `intent` lẫn `done`", [x.get("state") for x in rows] == ["intent", "done"], str(rows))
        e.run({"kind": "bot_message", "message_id": "b2", "channel_id": "c1", "content": "x"})
        check("6b không báo mồ côi khi đã done", e.state_rows("errors.jsonl") == [])
    # 6c: ngân sách thời gian: timeout cog > tổng timeout nội bộ
    check("6c SCRIPT_BUDGET_S = tổng timeout nội bộ xấu nhất, và cog mặc định > ngân sách",
          hasattr(di, "SCRIPT_BUDGET_S") and di.ACTIONS_BUDGET_S == da.MAX_ACTIONS * da.ACTION_TIMEOUT
          and di.SCRIPT_BUDGET_S == di.LOAD_PENDING_TIMEOUT + di.CLOSE_TIMEOUT + di.POST_TIMEOUT
          + da.MAX_ACTIONS * da.ACTION_TIMEOUT, "")


def main() -> int:
    item1(); item2(); item3(); item4(); item5(); item6()
    bad = [r for r in RESULTS if not r[1]]
    n = len(RESULTS)
    if bad:
        print(f"decision_inbox_r2_selfcheck: {n - len(bad)}/{n} PASS, {len(bad)} FAIL", file=sys.stderr)
        return 1
    print(f"decision_inbox_r2_selfcheck: {n}/{n} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
