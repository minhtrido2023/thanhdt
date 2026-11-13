#!/usr/bin/env python3
"""decision_inbox_selfcheck.py — selfcheck cho bin/decision_inbox.py (DESIGN §7, ≥25 ca).

Dùng --root tmpdir (bus giả + append_event.sh stub) ⇒ KHÔNG đụng bus thật.
Chạy: `env -u TZ python3 bin/decision_inbox_selfcheck.py` và `TZ=America/New_York ...`.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decision_inbox as di  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS: list[tuple[str, bool, str]] = []

STUB = """#!/usr/bin/env python3
import datetime,json,pathlib,sys,uuid
agent,etype,topic,payload=sys.argv[1:5]
p=pathlib.Path(__file__).resolve().parents[1]/'bus'/'inbox'/f'{agent}.jsonl'
p.parent.mkdir(parents=True,exist_ok=True)
r={'event_id':str(uuid.uuid4()),'ts':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'agent_id':agent,'event_type':etype,'topic':topic,'payload':json.loads(payload)}
with p.open('a',encoding='utf-8') as f:f.write(json.dumps(r,ensure_ascii=False)+'\\n')
"""


def check(name: str, cond, detail: str = "") -> None:
    RESULTS.append((name, bool(cond), detail))
    if not cond:
        print(f"FAIL {name}: {detail}", file=sys.stderr)


class Env:
    def __init__(self, td: str):
        self.root = Path(td)
        (self.root / "bin").mkdir(parents=True)
        w = self.root / "bin" / "append_event.sh"
        w.write_text(STUB, encoding="utf-8")
        w.chmod(0o755)
        self.n = 0
        self.now = dt.datetime(2026, 11, 13, 8, 0, tzinfo=dt.timezone.utc)

    def q(self, agent, topic, options, risk=None, eid=None, **extra):
        """Ghi 1 câu hỏi; trả dict {tag, ref, eid}."""
        self.n += 1
        eid = eid or f"{0x1a2b3c + self.n * 0x10101:08x}-0000-4000-8000-000000000000"
        payload = {"options": options, **extra}
        if risk:
            payload["risk"] = risk
        rec = {"event_id": eid, "ts": f"2026-11-13T0{self.n % 9}:00:{self.n:02d}Z", "agent_id": agent,
               "event_type": "question", "topic": topic, "payload": payload}
        p = self.root / "bus" / "inbox" / f"{agent}.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return {"tag": "q" + eid[:6], "ref": f"{agent}/{topic}", "eid": eid}

    def note_untagged_bot(self, mid, chan, now=None):
        """Giống cog: ghi con trỏ 'tin bot gần nhất của channel' cho MỌI tin bot (kể cả không thẻ)."""
        note = getattr(di, "note_bot_message", None)
        if note:
            note(self.root, chan, mid, (now or self.now).isoformat())

    def bot(self, mid, chan, *tags, now=None, pointer=True):
        content = "Câu hỏi: " + " ".join(f"[#{t}]" for t in tags)
        if pointer:
            self.note_untagged_bot(mid, chan, now)   # cog ghi con trỏ TRƯỚC khi gọi script
        return self.run({"kind": "bot_message", "message_id": mid, "channel_id": chan,
                         "content": content}, now=now)

    def user(self, mid, chan, text, ref=None, author="u1", **kw):
        ev = {"kind": "user_message", "message_id": mid, "channel_id": chan, "author_id": author,
              "content": text, "reference_message_id": ref, "created_at": "2026-11-13T08:00:00Z"}
        return self.run(ev, **kw)

    def run(self, ev, mode="live", ids=("u1",), now=None):
        return di.process_event(di.Ctx(self.root, mode, set(ids), now or self.now), ev)

    def answers(self, topic=None):
        out = []
        for p in (self.root / "bus" / "inbox").glob("*.jsonl"):
            for line in p.read_text(encoding="utf-8").splitlines():
                r = json.loads(line)
                if r["event_type"] == "answer" and (topic is None or r["topic"] == topic):
                    out.append(r)
        return out

    def statuses(self, topic):
        out = []
        for p in (self.root / "bus" / "inbox").glob("*.jsonl"):
            for line in p.read_text(encoding="utf-8").splitlines():
                r = json.loads(line)
                if r["event_type"] in ("status", "error") and r["topic"] == topic:
                    out.append(r)
        return out

    def finding_topics(self, topic):
        out = []
        for p in (self.root / "bus" / "inbox").glob("*.jsonl"):
            for line in p.read_text(encoding="utf-8").splitlines():
                r = json.loads(line)
                if r["event_type"] == "finding" and r["topic"] == topic:
                    out.append(r)
        return out

    def state_rows(self, name):
        return di.State(self.root).read(name)


def grammar_cases():
    ok = {"A": ("A", None), "Duyệt A": ("A", None), "chọn B": ("B", None), "PA a": ("A", None),
          "Duyệt A #q1f2e3d": ("A", "q1f2e3d"), "option c": ("C", None), "a.": ("A", None),
          "Phương án D!": ("D", None), "  ok   b ": ("B", None), "ĐỒNG Ý A": ("A", None)}
    for text, want in ok.items():
        check(f"grammar+ {text!r}", di.parse_answer(text) == want, str(di.parse_answer(text)))
    bad = ["A nhưng sửa ngưỡng", "ok", "đồng ý", "chọn cái đầu", "A" * 41, "Duyệt A #qZZZZZZ",
           "chọn I", "", "duyệt", "A, B"]
    for text in bad:
        check(f"grammar- {text!r}", di.parse_answer(text) is None, str(di.parse_answer(text)))


def label_cases():
    lab, inf = di.parse_options(["A: giữ cảnh báo", "B: tự BOT_STOP"])
    check("labels explicit A:/B:", list(lab) == ["A", "B"] and not inf)
    lab, inf = di.parse_options(["A merge ngoài giờ", "B mốc cứng", "C bỏ nhánh"])
    check("labels explicit 'A merge' (không dấu hai chấm)", not inf and len(lab) == 3)
    lab, inf = di.parse_options(["giữ cảnh báo", "tự BOT_STOP"])
    check("labels inferred khi không tiền tố", inf and list(lab) == ["A", "B"])
    lab, inf = di.parse_options(["B: x", "A: y"])
    check("labels sai thứ tự ⇒ inferred", inf)
    lab, inf = di.parse_options(["A new plan", "C other"])
    check("labels nhảy cóc ⇒ inferred", inf)
    check("risk DollarBill ⇒ money", di.classify_risk("DollarBill", "x", {}) == "money")
    check("risk keyword NAV ⇒ money", di.classify_risk("Mike", "nav-loss-brake", {}) == "money")
    check("risk keyword tiếng Việt 'bán' ⇒ money",
          di.classify_risk("Mike", "x", {"options": ["A: bán hết"]}) == "money")
    check("risk 'bot-stop' (gạch nối) ⇒ money", di.classify_risk("Mike", "bot-stop-policy", {}) == "money")
    check("risk 'trading_rules' ⇒ money", di.classify_risk("Mike", "x", {"summary": "sửa trading_rules.json"}) == "money")
    check("risk mặc định normal", di.classify_risk("Mike", "docs-cleanup", {"options": ["A", "B"]}) == "normal")
    check("risk explicit normal thắng heuristic (agent thường; DollarBill/Mafee thì KHÔNG — vòng 2)",
          di.classify_risk("Taylor", "plan", {"risk": "normal"}) == "normal"
          and di.classify_risk("DollarBill", "plan", {"risk": "normal"}) == "money")


def main() -> int:
    grammar_cases()
    label_cases()

    # 1. reply-to tin có thẻ, câu money ⇒ đóng, provenance đầy đủ
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "nav-loss-brake-review", ["A: giữ cảnh báo", "B: tự BOT_STOP"])
        e.bot("b1", "c1", q["tag"])
        check("surfaced ghi map", [r["ref"] for r in e.state_rows("surfaced.jsonl")] == [q["ref"]])
        r = e.user("m1", "c1", "Duyệt A", ref="b1")
        check("1 reply-to money ⇒ closed", r["outcome"] == "closed" and r["matched_by"] == "reply_to", str(r))
        ans = e.answers("nav-loss-brake-review")
        p = ans[0]["payload"] if ans else {}
        check("1 decided_by=user + resolves", p.get("decided_by") == "user"
              and p.get("resolves") == [q["ref"]], str(p))
        check("1 provenance via/matched_by/author/risk",
              p.get("provenance", {}).get("via") == "decision_inbox"
              and p["provenance"]["matched_by"] == "reply_to"
              and p["provenance"]["discord_author_id"] == "u1" and p["provenance"]["risk"] == "money", str(p))
        check("1 decision.option_text", p.get("decision", {}).get("option_text") == "A: giữ cảnh báo", str(p))
        check("1 reply+react", r.get("react") == "✅" and "Đã ghi" in r.get("reply", ""))
        # tin lặp ⇒ duplicate, không đóng đôi
        r2 = e.run({"kind": "user_message", "message_id": "m1", "channel_id": "c1",
                    "author_id": "u1", "content": "Duyệt A", "reference_message_id": "b1"})
        check("1b message_id lặp ⇒ duplicate", r2["outcome"] == "duplicate" and len(e.answers()) == 1)
        # tin mới sau khi đã đóng ⇒ không còn ứng viên
        r3 = e.user("m2", "c1", "A #" + q["tag"])
        check("1c câu đã đóng, tag cũ ⇒ no_binding", r3["outcome"] == "no_binding", str(r3))

    # 2. 'A' trần, 2 câu mở được surface ⇒ hỏi 1 lần
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q1 = e.q("Mike", "docs-one", ["A: x", "B: y"])
        q2 = e.q("Taylor", "docs-two", ["A: x", "B: y"])
        e.bot("b1", "c1", q1["tag"])
        e.bot("b2", "c1", q2["tag"])
        r = e.user("m1", "c1", "A")
        check("2 hai câu mở ⇒ ambiguous_asked", r["outcome"] == "ambiguous_asked"
              and q1["tag"] in r["reply"] and q2["tag"] in r["reply"], str(r))
        r = e.user("m2", "c1", "A")
        check("2 lần hai cùng tập ⇒ KHÔNG hỏi thêm", r["outcome"] == "ambiguous_suppressed", str(r))
        # T3 có TTL 6h (vòng 2) ⇒ kiểm TTL hỏi-lại 24h qua đường reply-to tin 2 thẻ (T1 không có TTL)
        e.bot("b0", "c1", q1["tag"], q2["tag"])
        r = e.user("m2a", "c1", "A", ref="b0")
        check("2 reply-to tin 2 thẻ, cùng tập đã hỏi ⇒ suppressed", r["outcome"] == "ambiguous_suppressed", str(r))
        r = e.user("m3", "c1", "A", ref="b0", now=e.now + dt.timedelta(hours=25))
        check("2 sau TTL 24h ⇒ hỏi lại", r["outcome"] == "ambiguous_asked", str(r))
        check("2 không đóng gì", e.answers() == [])
        check("2 status ambiguous lên bus", len(e.statuses("decision-inbox-ambiguous")) >= 1)
        # reply-to tin có 2 thẻ ⇒ nhập nhằng; có thẻ #q ⇒ đóng đúng câu
        e.bot("b3", "c1", q1["tag"], q2["tag"])
        r = e.user("m4", "c1", "B", ref="b3", now=e.now + dt.timedelta(hours=50))
        check("2b reply-to tin 2 thẻ ⇒ nhập nhằng", r["outcome"] == "ambiguous_asked", str(r))
        r = e.user("m5", "c1", "B #" + q2["tag"])
        check("2c thẻ tường minh ⇒ đóng câu 2", r["outcome"] == "closed" and r["ref"] == q2["ref"]
              and r["matched_by"] == "tag", str(r))
        check("2c câu 1 vẫn mở", len(e.answers("docs-one")) == 0)
        r = e.user("m6", "c1", "A")
        check("2d còn 1 câu normal trong thread ⇒ đóng qua thread", r["outcome"] == "closed"
              and r["matched_by"] == "thread" and r["ref"] == q1["ref"], str(r))

    # 3. 'A' trần, không có câu surface ⇒ im lặng, không hỏi
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        e.q("Mike", "docs-one", ["A: x", "B: y"])
        r = e.user("m1", "c1", "A")
        check("3 không surface ⇒ no_binding", r["outcome"] == "no_binding", str(r))
        check("3 không ghi asked", e.state_rows("asked.jsonl") == [])

    # 4. thread 1 câu normal ⇒ đóng; money ⇒ hỏi lại
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        qn = e.q("Mike", "docs-cleanup", ["A: x", "B: y"])
        e.bot("b1", "c1", qn["tag"])
        r = e.user("m1", "c1", "A")
        check("4 thread 1 câu normal ⇒ closed(thread)", r["outcome"] == "closed" and r["matched_by"] == "thread", str(r))
        qm = e.q("Mike", "park-sizing-change", ["A: x", "B: y"])
        e.bot("b2", "c2", qm["tag"])
        r = e.user("m2", "c2", "A")
        check("4b cùng tình huống câu money ⇒ ambiguous_asked",
              r["outcome"] == "ambiguous_asked" and r["reason"] == "money_requires_reply_or_tag", str(r))
        check("4b money chưa đóng", e.answers("park-sizing-change") == [])
        r = e.user("m3", "c2", "A", ref="b2")
        check("4c money + reply-to ⇒ đóng", r["outcome"] == "closed" and r["matched_by"] == "reply_to", str(r))

    # 5. chữ cái ngoài nhãn
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-two-opt", ["A: x", "B: y"])
        r = e.user("m1", "c1", "C #" + q["tag"])
        check("5 'C' cho câu A/B ⇒ hỏi lại", r["outcome"] == "ambiguous_asked"
              and r["reason"] == "letter_not_in_labels", str(r))
        check("5 không đóng", e.answers() == [])

    # 6/7. ngữ pháp & author
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-three", ["A: x", "B: y"])
        r = e.user("m1", "c1", "A nhưng sửa ngưỡng #" + q["tag"])
        check("6 không khớp ngữ pháp", r["outcome"] == "ignored_grammar", str(r))
        r = e.user("m2", "c1", "A #" + q["tag"], author="stranger")
        check("7 author ngoài allow-list ⇒ bỏ qua", r["outcome"] == "ignored_author", str(r))
        r = e.user("m3", "c1", "A #" + q["tag"], ids=())
        check("7b DECISION_INBOX_USER_IDS rỗng ⇒ fail-closed", r["outcome"] == "ignored_author", str(r))
        check("7c không đóng gì", e.answers() == [])
        r = e.user("m4", "c1", "A #q000000")
        check("13 thẻ trỏ câu không tồn tại ⇒ no_binding", r["outcome"] == "no_binding", str(r))
        # 8. câu đã đóng giữa lúc khớp và lúc gọi ⇒ ALREADY_CLOSED_OR_UNKNOWN
        real = di.load_pending
        stale = real(e.root)
        subprocess.run([sys.executable, str(ROOT / "bin" / "close_bus_question.py"), q["ref"],
                        "--resolution", "x", "--evidence", "y", "--root", str(e.root)],
                       capture_output=True, text=True)
        di.load_pending = lambda root: stale
        try:
            r = e.user("m5", "c1", "A #" + q["tag"])
        finally:
            di.load_pending = real
        check("8 đóng trước giữa chừng ⇒ already_closed", r["outcome"] == "already_closed", str(r))

    # 9. bẫy substring ⇒ helper rc=5 ⇒ không đóng, báo
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        e.q("Mike", "gate-no-owner", ["A: x", "B: y"])
        qr = e.q("Mike", "gate-no-owner-recurring", ["A: x", "B: y"])
        r = e.user("m1", "c1", "A #" + qr["tag"])
        check("9 substring collateral ⇒ blocked rc=5", r["outcome"] == "blocked" and r["rc"] == 5, str(r))
        check("9 không ghi answer", e.answers() == [])
        check("9 status blocked lên bus", len(e.statuses("decision-inbox-blocked")) == 1)

    # 10. options không tiền tố + money ⇒ không đóng
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        qm = e.q("Mike", "bot-stop-policy", ["giữ cảnh báo", "tự dừng bot"])
        r = e.user("m1", "c1", "A #" + qm["tag"])
        check("10 money + nhãn suy ⇒ hỏi lại", r["outcome"] == "ambiguous_asked"
              and r["reason"] == "money_labels_inferred", str(r))
        check("10 chưa đóng", e.answers() == [])
        qn = e.q("Mike", "docs-style", ["giữ nguyên", "đổi"])
        r = e.user("m2", "c1", "B #" + qn["tag"])
        check("10b normal + nhãn suy ⇒ vẫn đóng", r["outcome"] == "closed", str(r))
        check("10b provenance labels_inferred=true",
              e.answers("docs-style")[0]["payload"]["decision"]["labels_inferred"] is True)

    # va chạm thẻ 6 hex giữa 2 câu mở ⇒ hỏi lại, không đoán
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        qa = e.q("Mike", "docs-col-a", ["A: x", "B: y"], eid="abcdef01-0000-4000-8000-000000000000")
        qb = e.q("Mike", "docs-col-b", ["A: x", "B: y"], eid="abcdef02-0000-4000-8000-000000000000")
        r = e.user("m1", "c1", "A #" + qa["tag"])
        check("K1 va chạm thẻ ⇒ ambiguous_asked, không đóng",
              qa["tag"] == qb["tag"] and r["outcome"] == "ambiguous_asked" and e.answers() == [], str(r))

    # shadow: không đóng, không trả lời; status ghi "sẽ đóng"
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-shadow", ["A: x", "B: y"])
        r = e.user("m1", "c1", "A #" + q["tag"], mode="shadow")
        check("S1 shadow ⇒ would_close, không đóng", r["outcome"] == "shadow_would_close"
              and e.answers() == [] and "reply" not in r, str(r))
        check("S2 shadow ghi status", len(e.statuses("decision-inbox-shadow")) == 1)
        q2 = e.q("Mike", "docs-shadow2", ["A: x", "B: y"])
        e.bot("b1", "c1", q.get("tag"), q2["tag"])
        r = e.user("m2", "c1", "A", mode="shadow")
        check("S3 shadow nhập nhằng ⇒ would_ask, KHÔNG ghi asked, không reply",
              r["outcome"] == "shadow_would_ask" and e.state_rows("asked.jsonl") == []
              and "reply" not in r, str(r))
        check("S4 mode lạ ⇒ rơi về shadow", di.Ctx(e.root, "wat", {"u1"}).mode == "shadow")

    # bot message: không thẻ / thẻ lạ
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        check("B1 bot không thẻ ⇒ ignored", e.bot("b1", "c1")["outcome"] == "ignored_bot_no_tag")
        check("B2 bot thẻ lạ ⇒ unknown_tag", e.bot("b2", "c1", "q123456")["outcome"] == "surfaced_unknown_tag")
        check("B3 kind lạ ⇒ ignored_kind", e.run({"kind": "x", "message_id": "z"})["outcome"] == "ignored_kind")

    # độ bền: dòng processed hỏng; exception ⇒ error + không đánh dấu processed (retry được)
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-robust", ["A: x", "B: y"])
        (e.root / "state" / "decision_inbox").mkdir(parents=True, exist_ok=True)
        (e.root / "state" / "decision_inbox" / "processed.jsonl").write_text('{"message_id": "m0"\n', encoding="utf-8")
        real = di.load_pending
        di.load_pending = lambda root: (_ for _ in ()).throw(RuntimeError("boom"))
        try:
            r = e.user("m1", "c1", "A #" + q["tag"])
        finally:
            di.load_pending = real
        check("R1 exception ⇒ outcome=error (không raise)", r["outcome"] == "error" and "boom" in r["error"], str(r))
        check("R2 error không đánh dấu processed ⇒ retry được",
              all(x.get("message_id") != "m1" for x in e.state_rows("processed.jsonl")))
        r = e.user("m1", "c1", "A #" + q["tag"])
        check("R3 retry sau lỗi ⇒ closed; dòng hỏng bị bỏ qua", r["outcome"] == "closed", str(r))

    # CLI end-to-end (cùng đường cog sẽ gọi) — fail-closed khi thiếu user ids
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        q = e.q("Mike", "docs-cli", ["A: x", "B: y"])
        evf = Path(td) / "ev.jsonl"
        evf.write_text(json.dumps({"kind": "user_message", "message_id": "m1", "channel_id": "c1",
                                   "author_id": "u1", "content": "A #" + q["tag"],
                                   "created_at": "2026-11-13T08:00:00Z"}) + "\n", encoding="utf-8")
        base = [sys.executable, str(ROOT / "bin" / "decision_inbox.py"), "--event-file", str(evf),
                "--root", str(e.root)]
        env = {k: v for k, v in os.environ.items() if not k.startswith("DECISION_INBOX")}
        run = subprocess.run(base + ["--mode", "live"], capture_output=True, text=True, env=env)
        check("C1 CLI không user ids ⇒ ignored_author", json.loads(run.stdout)["outcome"] == "ignored_author", run.stdout + run.stderr)
        run = subprocess.run(base + ["--user-ids", "u1"], capture_output=True, text=True, env=env)
        check("C2 CLI mặc định shadow ⇒ would_close", json.loads(run.stdout)["outcome"] == "shadow_would_close", run.stdout + run.stderr)
        evf.write_text(evf.read_text().replace('"m1"', '"m2"'), encoding="utf-8")
        run = subprocess.run(base + ["--user-ids", "u1", "--mode", "live"], capture_output=True, text=True, env=env)
        check("C3 CLI live ⇒ closed", json.loads(run.stdout)["outcome"] == "closed", run.stdout + run.stderr)

    bad = [r for r in RESULTS if not r[1]]
    n = len(RESULTS)
    if bad:
        print(f"decision_inbox_selfcheck: {n - len(bad)}/{n} PASS, {len(bad)} FAIL", file=sys.stderr)
        return 1
    print(f"decision_inbox_selfcheck: {n}/{n} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
