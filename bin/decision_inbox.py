#!/usr/bin/env python3
"""decision_inbox.py — bộ khớp XÁC ĐỊNH: tin Discord của user ("Duyệt A") ⇒ đóng câu hỏi bus.

Thiết kế: agents/Taylor/research/decision_inbox_design_20261113/DESIGN.md (§2-§4). Cog trong
bridge (mike/ccdb_cogs/decision_inbox_cog.py) chỉ thu sự kiện thô rồi gọi script này; MỌI logic
khớp/đóng nằm ở đây để test được ngoài bridge và để LLM không nằm trên đường quyết định.

Sự kiện vào (JSON, 1 object/dòng trong --event-file):
  {"kind":"user_message"|"bot_message","message_id","channel_id","parent_id","author_id",
   "reference_message_id","content","created_at","guild_id"(tuỳ chọn)}
Kết quả: mỗi sự kiện in 1 dòng JSON {"outcome": ..., "reply"?, "react"?, ...} lên stdout.

Chế độ (DECISION_INBOX_MODE): `shadow` (MẶC ĐỊNH) = chỉ ghi status "sẽ đóng X", KHÔNG đóng, KHÔNG
trả lời; `live` = đóng thật. Fail-CLOSED: DECISION_INBOX_USER_IDS rỗng ⇒ không làm gì.

Idempotent (coding_guidelines §5): `processed.jsonl` khoá theo message_id; process_event giữ flock
toàn cục nên 2 tin tới đồng thời không hỏi lại / đóng đôi.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import glob
import gzip
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATCHER_VERSION = "1"
ASK_TTL = dt.timedelta(hours=24)
MAX_LEN = 40

ANSWER_RE = re.compile(
    r"^(?:(?:duyet|chon|chot|ok|dong y)\s+)?(?:(?:phuong an|pa|option)\s+)?([a-h])"
    r"(?:\s+#(q[0-9a-f]{6}))?$")
TAG_RE = re.compile(r"\[#(q[0-9a-f]{6})\]")
LABEL_RE = re.compile(r"^([A-Ha-h])(?:\s*[:)\.]|\s+|$)")
MONEY_RE = re.compile(
    r"\b(?:plan|lenh|order|bot[-_ ]stop|margin|park|excluded|trading[-_ ]rules|live|ban|mua|nav|"
    r"sizing|egg|trung)\b")
MONEY_AGENTS = {"DollarBill", "Mafee"}
# Outcome KHÔNG có tác dụng phụ ⇒ không đánh dấu processed (đổi user-ids/mode xong gửi lại vẫn xử lý được).
NO_RECORD = {"error", "ignored_author", "ignored_grammar", "ignored_kind", "ignored_bot_no_tag",
             "no_binding", "surfaced_unknown_tag"}


# ───────────────────────── ngữ pháp ─────────────────────────
def norm(text: str) -> str:
    t = unicodedata.normalize("NFC", text or "").lower()
    t = t.replace("đ", "d")
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"[.!]+$", "", t).strip()


def parse_answer(text: str):
    """⇒ (LETTER, tag|None) nếu TOÀN BỘ tin khớp ngữ pháp, ngược lại None."""
    if not text or len(text) > MAX_LEN:
        return None
    m = ANSWER_RE.match(norm(text))
    if not m:
        return None
    return m.group(1).upper(), m.group(2)


# ───────────────────────── câu hỏi bus ─────────────────────────
def _iter_events(path: str):
    opener = gzip.open if path.endswith(".gz") else open
    try:
        with opener(path, "rt", encoding="utf-8") as fh:
            for line in fh:
                try:
                    yield json.loads(line)
                except ValueError:
                    continue
    except OSError:
        return


def _agent_of(path: str) -> str:
    name = os.path.basename(path).replace(".jsonl.gz", "").replace(".jsonl", "")
    return re.sub(r"_\d{4}-\d{2}$", "", name)


def parse_options(options) -> tuple[dict, bool]:
    """⇒ ({LABEL: text}, labels_inferred). Nhãn tường minh chỉ khi MỌI option i bắt đầu bằng
    chữ cái thứ i (A,B,C…); nếu không ⇒ suy theo thứ tự và đánh dấu inferred."""
    opts = [str(o) for o in (options or [])]
    explicit = bool(opts)
    for i, o in enumerate(opts):
        m = LABEL_RE.match(o.strip())
        if not m or m.group(1).upper() != chr(65 + i):
            explicit = False
            break
    return {chr(65 + i): o for i, o in enumerate(opts[:8])}, not explicit


def classify_risk(agent: str, topic: str, payload: dict) -> str:
    r = payload.get("risk")
    if r in ("money", "normal"):
        return r
    if agent in MONEY_AGENTS:
        return "money"
    blob = " ".join([topic or "", str(payload.get("summary", "")),
                     " ".join(str(o) for o in (payload.get("options") or []))])
    return "money" if MONEY_RE.search(norm(blob)) else "normal"


def load_pending(root: Path) -> list[dict]:
    env = dict(os.environ)
    env["BUS_AUDIT_ROOT"] = str(root)
    run = subprocess.run([sys.executable, str(ROOT / "bin" / "bus_question_audit.py"), "--json"],
                         env=env, capture_output=True, text=True, timeout=60)
    try:
        pending = json.loads(run.stdout).get("pending", [])
    except ValueError as exc:
        raise RuntimeError(f"không đọc được audit pending: {exc}; stderr={run.stderr[-200:]}")
    want = {(q["agent"], q["topic"], q["ts"]): q for q in pending}
    files = sorted(glob.glob(str(root / "bus" / "inbox" / "*.jsonl"))) + \
        sorted(glob.glob(str(root / "bus" / "inbox" / "archive" / "*.jsonl.gz")))
    found: dict = {}
    for p in files:
        agent = _agent_of(p)
        for rec in _iter_events(p):
            if rec.get("event_type") != "question":
                continue
            key = (agent, rec.get("topic"), rec.get("ts"))
            if key in want and key not in found:
                found[key] = rec
    out = []
    for key, q in want.items():
        rec = found.get(key)
        if not rec:
            continue
        payload = rec.get("payload")
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except ValueError:
                payload = {}
        if not isinstance(payload, dict):
            payload = {}
        eid = str(rec.get("event_id") or "")
        if not eid:
            continue  # câu hỏi cũ không có event_id ⇒ không có thẻ ổn định ⇒ không xử lý
        labels, inferred = parse_options(payload.get("options"))
        out.append({
            "ref": f"{q['agent']}/{q['topic']}", "agent": q["agent"], "topic": q["topic"],
            "event_id": eid, "tag": "q" + eid.replace("-", "")[:6].lower(),
            "labels": labels, "labels_inferred": inferred,
            "risk": classify_risk(q["agent"], q["topic"], payload), "payload": payload,
        })
    return out


# ───────────────────────── trạng thái ─────────────────────────
class State:
    def __init__(self, root: Path):
        self.dir = root / "state" / "decision_inbox"
        self.dir.mkdir(parents=True, exist_ok=True)

    def read(self, name: str) -> list[dict]:
        p = self.dir / name
        if not p.exists():
            return []
        rows = []
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue  # dòng hỏng (kill giữa chừng) ⇒ bỏ qua, không làm sập
        return rows

    def append(self, name: str, rec: dict) -> None:
        with (self.dir / name).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _parse_ts(s, default: dt.datetime) -> dt.datetime:
    try:
        d = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return default


def post_event(root: Path, etype: str, topic: str, payload: dict) -> None:
    """Ghi bus qua append_event.sh của chính --root. Không bao giờ làm hỏng luồng chính."""
    try:
        subprocess.run([str(root / "bin" / "append_event.sh"), "Mike", etype, topic,
                        json.dumps(payload, ensure_ascii=False)],
                       capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        pass


# ───────────────────────── lõi ─────────────────────────
class Ctx:
    def __init__(self, root: Path, mode: str, user_ids: set[str], now: dt.datetime | None = None):
        self.root = root
        self.mode = mode if mode in ("shadow", "live") else "shadow"
        self.user_ids = user_ids
        self.now = now or dt.datetime.now(dt.timezone.utc)
        self.state = State(root)


def _record_surfaced(ctx: Ctx, ev: dict) -> dict:
    tags = TAG_RE.findall(ev.get("content") or "")
    if not tags:
        return {"outcome": "ignored_bot_no_tag"}
    pending = load_pending(ctx.root)
    saved = []
    for tag in dict.fromkeys(tags):
        for q in (x for x in pending if x["tag"] == tag):
            ctx.state.append("surfaced.jsonl", {
                "message_id": str(ev.get("message_id")), "channel_id": str(ev.get("channel_id")),
                "tag": tag, "question_event_id": q["event_id"], "ref": q["ref"],
                "ts": ctx.now.isoformat()})
            saved.append(q["ref"])
    return {"outcome": "surfaced_recorded" if saved else "surfaced_unknown_tag", "refs": saved}


def _candidate_line(q: dict) -> str:
    return f"`#{q['tag']}` {q['ref']} ({'/'.join(q['labels'])})"


def _ask(ctx: Ctx, ev: dict, cands: list[dict], reason: str) -> dict:
    ids = sorted(q["event_id"] for q in cands)
    key = {"channel_id": str(ev.get("channel_id")), "ids": ids}
    for row in ctx.state.read("asked.jsonl"):
        if row.get("channel_id") == key["channel_id"] and row.get("ids") == ids:
            if ctx.now - _parse_ts(row.get("ts"), ctx.now) < ASK_TTL:
                return {"outcome": "ambiguous_suppressed", "reason": reason}
    post_event(ctx.root, "status", "decision-inbox-ambiguous",
               {"reason": reason, "mode": ctx.mode, "candidates": [q["ref"] for q in cands],
                "discord_message_id": str(ev.get("message_id")),
                "measured_by": "decision_inbox.py ambiguity"})
    if ctx.mode != "live":
        return {"outcome": "shadow_would_ask", "reason": reason,
                "candidates": [q["ref"] for q in cands]}
    ctx.state.append("asked.jsonl", {**key, "ts": ctx.now.isoformat()})
    body = " · ".join(_candidate_line(q) for q in cands) if cands else "(không có câu mở nào khớp)"
    reply = ("Mình chưa đóng được vì chưa rõ bạn trả lời câu nào: " + body +
             ". Reply thẳng vào tin câu hỏi, hoặc gõ `A #<thẻ>`.")
    return {"outcome": "ambiguous_asked", "reason": reason,
            "candidates": [q["ref"] for q in cands], "reply": reply}


def _bind(ctx: Ctx, ev: dict, letter: str, tag: str | None, pending: list[dict]):
    """⇒ (question|None, matched_by|None, ambiguous_candidates|None)."""
    by_id = {q["event_id"]: q for q in pending}
    by_tag: dict[str, list[dict]] = {}
    for q in pending:
        by_tag.setdefault(q["tag"], []).append(q)
    surfaced = ctx.state.read("surfaced.jsonl")
    chan = str(ev.get("channel_id"))

    ref_id = ev.get("reference_message_id")
    if ref_id:  # T1
        qs = {r["question_event_id"] for r in surfaced if r.get("message_id") == str(ref_id)}
        live = [by_id[i] for i in qs if i in by_id]
        if len(live) == 1:
            return live[0], "reply_to", None
        if len(live) > 1:
            return None, None, live
    if tag:  # T2
        hits = by_tag.get(tag, [])
        if len(hits) == 1:
            return hits[0], "tag", None
        if len(hits) > 1:  # va chạm 6 hex (hiếm) ⇒ hỏi lại thay vì đoán
            return None, None, hits
        return None, None, None  # thẻ trỏ câu không (còn) tồn tại ⇒ không làm gì
    # T3 — chỉ câu có options được surface trong CHÍNH thread này
    open_ids = []
    for r in surfaced:
        if r.get("channel_id") == chan and r.get("question_event_id") in by_id \
                and by_id[r["question_event_id"]]["labels"] \
                and r["question_event_id"] not in open_ids:
            open_ids.append(r["question_event_id"])
    if not open_ids:
        return None, None, None
    cands = [by_id[i] for i in open_ids]
    if len(cands) > 1:
        return None, None, cands
    return cands[0], "thread", None


def _close(ctx: Ctx, ev: dict, q: dict, letter: str, matched_by: str) -> dict:
    text = ev.get("content") or ""
    prov = {
        "decision": {"option": letter, "option_text": q["labels"][letter],
                     "labels_inferred": q["labels_inferred"]},
        "provenance": {
            "via": "decision_inbox", "matcher_version": MATCHER_VERSION,
            "matched_by": matched_by, "discord_message_id": str(ev.get("message_id")),
            "discord_channel_id": str(ev.get("channel_id")),
            "discord_author_id": str(ev.get("author_id")),
            "message_text": text[:200], "message_ts": str(ev.get("created_at") or ""),
            "question_event_id": q["event_id"], "risk": q["risk"]},
    }
    cmd = [sys.executable, str(ROOT / "bin" / "close_bus_question.py"), q["ref"],
           "--resolution", f"User chọn {letter}: {q['labels'][letter][:160]}",
           "--evidence", f"discord msg {ev.get('message_id')} (channel {ev.get('channel_id')})"
                         f" matched_by={matched_by}",
           "--source-topic", f"discord:{ev.get('channel_id')}", "--decided-by-user",
           "--actor", "Mike", "--provenance-json", json.dumps(prov, ensure_ascii=False),
           "--root", str(ctx.root)]
    run = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    out = (run.stdout or "") + (run.stderr or "")
    base = {"ref": q["ref"], "option": letter, "matched_by": matched_by, "risk": q["risk"]}
    if run.returncode == 0 and "CLOSED" in run.stdout and "ALREADY_CLOSED" not in run.stdout:
        return {**base, "outcome": "closed", "react": "✅",
                "reply": f"Đã ghi: {q['ref']} = {letter} (user)"}
    if run.returncode == 0 and "ALREADY_CLOSED_OR_UNKNOWN" in run.stdout:
        return {**base, "outcome": "already_closed"}
    post_event(ctx.root, "status", "decision-inbox-blocked",
               {**base, "rc": run.returncode, "detail": out[-300:],
                "measured_by": "close_bus_question.py rc"})
    return {**base, "outcome": "blocked", "rc": run.returncode, "detail": out[-300:]}


def _handle_user(ctx: Ctx, ev: dict) -> dict:
    if not ctx.user_ids or str(ev.get("author_id")) not in ctx.user_ids:
        return {"outcome": "ignored_author"}
    ans = parse_answer(ev.get("content") or "")
    if not ans:
        return {"outcome": "ignored_grammar"}
    letter, tag = ans
    pending = [q for q in load_pending(ctx.root) if q["labels"]]
    q, via, amb = _bind(ctx, ev, letter, tag, pending)
    if amb:
        return _ask(ctx, ev, amb, "ambiguous_binding")
    if not q:
        return {"outcome": "no_binding"}
    if letter not in q["labels"]:
        return _ask(ctx, ev, [q], "letter_not_in_labels")
    if q["risk"] == "money" and via == "thread":
        return _ask(ctx, ev, [q], "money_requires_reply_or_tag")
    if q["risk"] == "money" and q["labels_inferred"]:
        return _ask(ctx, ev, [q], "money_labels_inferred")
    if ctx.mode != "live":
        res = {"outcome": "shadow_would_close", "ref": q["ref"], "option": letter,
               "matched_by": via, "risk": q["risk"]}
        post_event(ctx.root, "status", "decision-inbox-shadow",
                   {**res, "discord_message_id": str(ev.get("message_id")),
                    "message_text": (ev.get("content") or "")[:200],
                    "measured_by": "decision_inbox.py shadow"})
        return res
    res = _close(ctx, ev, q, letter, via)
    if res.get("outcome") == "closed" and q["risk"] != "money":
        res["actions"] = _run_on_answer(ctx, q, letter)
    return res


def _run_on_answer(ctx: Ctx, q: dict, letter: str) -> list:
    """Hậu quả khai báo sẵn (DESIGN §4). Câu money KHÔNG bao giờ tới đây."""
    spec = (q["payload"].get("on_answer") or {}).get(letter)
    if not spec:
        return []
    try:
        sys.path.insert(0, str(ROOT / "bin"))
        import decision_actions  # noqa: WPS433 — nạp trễ: module whitelist tách riêng
    except ImportError:
        return [{"action": "*", "status": "decision_actions_missing"}]
    return decision_actions.run_actions(ctx.root, q["event_id"], letter, spec)


def process_event(ctx: Ctx, ev: dict) -> dict:
    mid = str(ev.get("message_id") or "")
    lock_path = ctx.state.dir / ".lock"
    with lock_path.open("a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        if mid and any(r.get("message_id") == mid and r.get("kind") == ev.get("kind")
                       for r in ctx.state.read("processed.jsonl")):
            return {"outcome": "duplicate"}
        try:
            if ev.get("kind") == "bot_message":
                res = _record_surfaced(ctx, ev)
            elif ev.get("kind") == "user_message":
                res = _handle_user(ctx, ev)
            else:
                res = {"outcome": "ignored_kind"}
        except Exception as exc:  # không bao giờ làm sập cog
            res = {"outcome": "error", "error": f"{type(exc).__name__}: {exc}"}
            post_event(ctx.root, "error", "decision-inbox-error",
                       {"error": res["error"], "discord_message_id": mid,
                        "measured_by": "decision_inbox.py exception"})
        if mid and res.get("outcome") not in NO_RECORD:
            ctx.state.append("processed.jsonl", {"message_id": mid, "kind": ev.get("kind"),
                                                 "outcome": res.get("outcome"),
                                                 "ts": ctx.now.isoformat()})
        return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--event-file", required=True, type=Path)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--mode", default=os.environ.get("DECISION_INBOX_MODE", "shadow"))
    ap.add_argument("--user-ids", default=os.environ.get("DECISION_INBOX_USER_IDS", ""))
    a = ap.parse_args()
    ids = {x.strip() for x in a.user_ids.split(",") if x.strip()}
    for line in a.event_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            print(json.dumps({"outcome": "bad_event_json"}))
            continue
        ctx = Ctx(a.root, a.mode, ids,
                  _parse_ts(ev.get("created_at"), dt.datetime.now(dt.timezone.utc)))
        print(json.dumps(process_event(ctx, ev), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
