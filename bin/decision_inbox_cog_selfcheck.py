#!/usr/bin/env python3
"""Selfcheck decision_inbox_cog.py với discord.Message GIẢ (duck-typed) — không token, không mạng, không bus thật.

Cần discord.py + claude_discord ⇒ chạy bằng python của bridge: /workspace/claude-code-discord-bridge/.venv/bin/python
(tự re-exec nếu python hiện tại thiếu discord).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BRIDGE_PY = "/workspace/claude-code-discord-bridge/.venv/bin/python"
try:
    import discord  # noqa: F401
except ImportError:
    if os.path.exists(BRIDGE_PY) and os.environ.get("_DI_COG_REEXEC") != "1":
        os.environ["_DI_COG_REEXEC"] = "1"
        os.execv(BRIDGE_PY, [BRIDGE_PY, *sys.argv])
    sys.exit("decision_inbox_cog_selfcheck: thiếu discord.py và không có python của bridge — KHÔNG kết luận được")

import asyncio  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import tempfile  # noqa: E402
from types import SimpleNamespace as NS  # noqa: E402

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "bin"))
sys.path.insert(0, str(REPO / "ccdb_cogs"))
sys.path.insert(0, "/workspace/claude-code-discord-bridge")
import decision_inbox_cog as cog_mod  # noqa: E402
from decision_inbox_selfcheck import Env  # noqa: E402

N = [0, 0]
BOT_ID, USER_ID = 999, 111


def check(name, cond, detail=""):
    N[0] += 1
    if not cond:
        N[1] += 1
        print(f"FAIL {name}: {detail}", file=sys.stderr)


class Msg:
    def __init__(self, mid, content, author=USER_ID, bot=False, chan=5, ref=None):
        self.id = mid
        self.content = content
        self.author = NS(id=author, bot=bot)
        self.channel = NS(id=chan, parent_id=None)
        self.guild = NS(id=77)
        self.reference = NS(message_id=ref) if ref else None
        self.created_at = dt.datetime(2026, 11, 13, 8, 0, tzinfo=dt.timezone.utc)
        self.replies: list[str] = []
        self.reactions: list[str] = []

    async def reply(self, text, **kw):
        self.replies.append(text)

    async def add_reaction(self, e):
        self.reactions.append(e)


def mk(e: Env, ids=(str(USER_ID),), mode="live", script=None, timeout=None):
    bot = NS(user=NS(id=BOT_ID))
    c = cog_mod.DecisionInboxCog(bot, e.root, set(ids), mode, script=script or REPO / "bin" / "decision_inbox.py", timeout=timeout,
                                  inbox_path=REPO / "bin" / "decision_inbox.py")
    return c


def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def raw_files(e):
    d = e.root / "state" / "decision_inbox" / "raw"
    return sorted(d.glob("*.jsonl")) if d.exists() else []


with tempfile.TemporaryDirectory() as td:
    e = Env(td)
    q1 = e.q("Mike", "docs-one", ["A: x", "B: y"])
    q2 = e.q("Taylor", "docs-two", ["A: x", "B: y"])

    c = mk(e, ids=())
    m = Msg(1, "A #" + q1["tag"])
    run(c.on_message(m))
    check("1 user ids rỗng ⇒ vô hiệu: không raw log, không reply", raw_files(e) == [] and m.replies == [])
    c = mk(e)
    for name, msg in (("2 author ngoài allow-list", Msg(2, "A #" + q1["tag"], author=5)),
                      ("3 tin không khớp ngữ pháp", Msg(3, "A nhưng sửa ngưỡng")),
                      ("4 bot khác (không phải bot này)", Msg(4, "[#q123456]", author=555, bot=True)),
                      ("5 tin bot này KHÔNG có thẻ", Msg(5, "xin chào", author=BOT_ID, bot=True))):
        run(c.on_message(msg))
        check(f"{name} ⇒ lọc rẻ, không spawn", raw_files(e) == [] and msg.replies == [] and msg.reactions == [])
    ptr = e.root / "state" / "decision_inbox" / "last_bot" / "5.json"
    check("5b tin bot KHÔNG thẻ vẫn ghi con trỏ last-bot của channel (vòng 2, mục 3)",
          ptr.exists() and json.loads(ptr.read_text(encoding="utf-8"))["message_id"] == "5", str(ptr))
    check("5c tin bot của BOT KHÁC không ghi con trỏ", json.loads(ptr.read_text(encoding="utf-8"))["message_id"] != "4")
    check("5d timeout mặc định của cog > ngân sách nội bộ của script",
          c.timeout > c.inbox.SCRIPT_BUDGET_S and c.timeout == c.inbox.SCRIPT_BUDGET_S + 60.0, f"{c.timeout} vs {c.inbox.SCRIPT_BUDGET_S}")

    # tin bot có thẻ ⇒ ghi raw + surfaced
    run(c.on_message(Msg(10, f"❓ [#{q1['tag']}]", author=BOT_ID, bot=True)))
    run(c.on_message(Msg(11, f"❓ [#{q2['tag']}]", author=BOT_ID, bot=True)))
    surfaced = e.state_rows("surfaced.jsonl")
    check("6 tin bot có thẻ ⇒ surfaced.jsonl có 2 map", sorted(r["ref"] for r in surfaced) == ["Mike/docs-one", "Taylor/docs-two"], str(surfaced))
    rf = raw_files(e)
    lines = [json.loads(x) for x in rf[0].read_text(encoding="utf-8").splitlines()] if rf else []
    check("7 raw log: đủ trường, tên file = ngày ICT", len(rf) == 1 and len(rf[0].stem) == 8 and lines[0]["kind"] == "bot_message"
          and lines[0]["channel_id"] == "5" and lines[0]["message_id"] == "10", str(lines))
    check("7b không để lại file ev_ tạm", list((e.root / "state" / "decision_inbox" / "raw").glob("ev_*")) == [])

    # reply-to ⇒ đóng + reaction + reply (live)
    m = Msg(20, "Duyệt A", ref="10")
    run(c.on_message(m))
    check("8 live: reply-to ⇒ đóng, ✅ + 'Đã ghi'", m.reactions == ["✅"] and len(m.replies) == 1 and "Mike/docs-one = A" in m.replies[0]
          and len(e.answers("docs-one")) == 1, f"{m.replies} {m.reactions}")
    check("8b raw log ghi cả tin user", any(json.loads(x)["kind"] == "user_message" for x in rf[0].read_text(encoding="utf-8").splitlines()))

    # nhập nhằng ⇒ hỏi lại qua reply
    e2 = Env(tempfile.mkdtemp())
    a1 = e2.q("Mike", "docs-a", ["A: x", "B: y"])
    a2 = e2.q("Taylor", "docs-b", ["A: x", "B: y"])
    c2 = mk(e2)
    run(c2.on_message(Msg(1, f"[#{a1['tag']}]", author=BOT_ID, bot=True)))
    run(c2.on_message(Msg(2, f"[#{a2['tag']}]", author=BOT_ID, bot=True)))
    m = Msg(3, "A")
    run(c2.on_message(m))
    check("9 nhập nhằng ⇒ reply hỏi lại có cả 2 thẻ, không đóng", len(m.replies) == 1 and a1["tag"] in m.replies[0]
          and a2["tag"] in m.replies[0] and e2.answers() == [], str(m.replies))

    # shadow: không reply, không đóng, có status
    e3 = Env(tempfile.mkdtemp())
    s1 = e3.q("Mike", "docs-s", ["A: x", "B: y"])
    c3 = mk(e3, mode="shadow")
    m = Msg(1, "A #" + s1["tag"])
    run(c3.on_message(m))
    check("10 shadow ⇒ không reply/react, không đóng, có status shadow", m.replies == [] and m.reactions == []
          and e3.answers() == [] and len(e3.statuses("decision-inbox-shadow")) == 1)

    # script treo / crash / rác ⇒ không raise, không reply
    for name, body, tmo in (("11 script treo ⇒ kill + không raise", "import time; time.sleep(30)", 1.0),
                            ("12 script crash rc≠0", "import sys; sys.exit(3)", 5.0),
                            ("13 script in rác (không JSON)", "print('rác')", 5.0)):
        sp = Path(td) / "fake_script.py"
        sp.write_text(body, encoding="utf-8")
        e4 = Env(tempfile.mkdtemp())
        c4 = mk(e4, script=sp, timeout=tmo)
        m = Msg(1, "A #q000000")
        run(c4.on_message(m))
        check(name, m.replies == [] and c4.errors == 1, f"errors={c4.errors}")
        kind = {"11": "script_timeout", "12": "script_rc", "13": "script_bad_json"}[name.split()[0]]
        check(f"{name.split()[0]}b lỗi để lại dấu: state errors.jsonl kind={kind}",
              any(r.get("kind") == kind for r in e4.state_rows("errors.jsonl")), str(e4.state_rows("errors.jsonl")))
        check(f"{name.split()[0]}c … và lên bus status decision-inbox-error",
              any(r["payload"].get("kind") == kind for r in e4.statuses("decision-inbox-error")), str(e4.statuses("decision-inbox-error")))

    # timeout ⇒ giết CẢ NHÓM tiến trình (con của script không được mồ côi)
    sp = Path(td) / "spawn_child.py"
    pidf = Path(td) / "child.pid"
    sp.write_text("import subprocess,sys,time\nc=subprocess.Popen(['sleep','60'])\n"
                  f"open({str(pidf)!r},'w').write(str(c.pid))\ntime.sleep(60)\n", encoding="utf-8")
    e4 = Env(tempfile.mkdtemp())
    c4 = mk(e4, script=sp, timeout=2.0)
    run(c4.on_message(Msg(1, "A #q000000")))
    import time as _t
    _t.sleep(0.3)
    child = int(pidf.read_text()) if pidf.exists() else 0
    try:
        os.kill(child, 0)
        alive = True
    except ProcessLookupError:
        alive = False
    except PermissionError:
        alive = True
    check("11d timeout ⇒ tiến trình CON của script cũng bị giết (killpg)", child > 0 and not alive, f"child={child} alive={alive}")

    # message hỏng (thiếu thuộc tính) ⇒ nuốt lỗi
    bad = NS(id=1, content="A", author=None)
    run(c.on_message(bad))
    check("14 message hỏng ⇒ nuốt lỗi, errors tăng", c.errors == 1, str(c.errors))

    # reaction lỗi không chặn reply
    e5 = Env(tempfile.mkdtemp())
    r1 = e5.q("Mike", "docs-r", ["A: x", "B: y"])
    c5 = mk(e5)
    m = Msg(1, "A #" + r1["tag"])

    async def boom(_):
        raise RuntimeError("no perm")
    m.add_reaction = boom
    run(c5.on_message(m))
    check("15 add_reaction lỗi ⇒ vẫn reply", len(m.replies) == 1 and len(e5.answers()) == 1, str(m.replies))

    # nạp qua cog_loader THẬT của bridge
    from claude_discord.cog_loader import load_custom_cogs  # noqa: E402
    added = []

    class FakeBot:
        user = NS(id=BOT_ID)

        async def add_cog(self, cg):
            added.append(cg)
    os.environ.update(DECISION_INBOX_ROOT=str(REPO), DECISION_INBOX_USER_IDS="", DECISION_INBOX_MODE="bogus")
    n = run(load_custom_cogs(REPO / "ccdb_cogs", FakeBot(), None, None))
    check("16 cog_loader thật nạp được; mode lạ ⇒ shadow; ids rỗng ⇒ vô hiệu", n == 1 and len(added) == 1
          and added[0].mode == "shadow" and added[0].user_ids == set(), f"n={n} added={added}")
    extra = [f.name for f in (REPO / "ccdb_cogs").iterdir() if f.suffix == ".py" and not f.name.startswith("_")]
    check("17 thư mục ccdb_cogs chỉ chứa cog (mọi .py không '_' đều bị bridge exec)", extra == ["decision_inbox_cog.py"], str(extra))
    before = list(sys.path)
    cog_mod.DecisionInboxCog(NS(user=NS(id=1)), e.root, set(), "shadow", inbox_path=REPO / "bin" / "decision_inbox.py")
    check("18 cog không sửa sys.path của bridge", sys.path == before)
    os.environ.pop("DECISION_INBOX_ROOT"), os.environ.pop("DECISION_INBOX_USER_IDS"), os.environ.pop("DECISION_INBOX_MODE")

if N[1]:
    print(f"decision_inbox_cog_selfcheck: {N[0] - N[1]}/{N[0]} PASS, {N[1]} FAIL", file=sys.stderr)
    sys.exit(1)
print(f"decision_inbox_cog_selfcheck: {N[0]}/{N[0]} PASS")
