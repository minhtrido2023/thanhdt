"""decision_inbox_cog.py — Cog MỎNG cho bridge ccdb-mike: tin Discord của user ("Duyệt A") → bin/decision_inbox.py.

Nạp qua `CUSTOM_COGS_DIR` (claude_discord.cog_loader) — KHÔNG sửa lõi bridge. Listener `on_message` chạy SONG SONG
với ClaudeChat.on_message (discord.py gọi mọi listener): không nuốt tin, Mike vẫn nhận tin như cũ.

Cog chỉ THU + CHUYỂN. Mọi logic khớp/đóng/hành động nằm trong script xác định `bin/decision_inbox.py` (test được
ngoài bridge). Lỗi trong handler bị nuốt + log (không raise ⇒ không ảnh hưởng listener khác).

Cấu hình (env của ccdb-mike, ĐỌC LÚC LOAD):
  DECISION_INBOX_USER_IDS   danh sách user id Discord được phép, phân tách bằng dấu phẩy. RỖNG ⇒ cog VÔ HIỆU (fail-closed).
  DECISION_INBOX_MODE       `shadow` (mặc định: chỉ ghi status "sẽ đóng X", không đóng, không trả lời) | `live`.
  DECISION_INBOX_ROOT       gốc dữ liệu/bus (mặc định: thư mục `mike/` chứa file này).
Thiết kế: agents/Taylor/research/decision_inbox_design_20261113/DESIGN.md §1(a), §2.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import importlib.util
import json
import logging
import os
import signal
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from discord.ext import commands

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
DEFAULT_ROOT = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)


def _load_inbox(script: Path):
    """Nạp bin/decision_inbox.py dưới tên riêng, KHÔNG đụng sys.path của bridge (mike/bin có nhiều file
    trùng tên module phổ biến — chèn vào sys.path có thể che thư viện của bridge). Dùng chung regex ngữ
    pháp với script ⇒ 1 nguồn duy nhất."""
    spec = importlib.util.spec_from_file_location("_mike_decision_inbox", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class DecisionInboxCog(commands.Cog):
    def __init__(self, bot, root: Path, user_ids: set[str], mode: str,
                 script: Path | None = None, timeout: float | None = None, inbox_path: Path | None = None):
        self.bot = bot
        self.root = Path(root)
        self.user_ids = user_ids
        self.mode = mode if mode in ("shadow", "live") else "shadow"
        self.script = Path(script) if script else self.root / "bin" / "decision_inbox.py"
        self.inbox = _load_inbox(Path(inbox_path) if inbox_path else self.root / "bin" / "decision_inbox.py")
        # Timeout cog PHẢI > tổng timeout nội bộ xấu nhất của script (inbox.SCRIPT_BUDGET_S); nếu cog kill sớm hơn
        # thì script đang giữa `đóng` ↔ `on_answer` bị giết (vòng 2, mục 6).
        self.timeout = float(timeout) if timeout is not None else float(self.inbox.SCRIPT_BUDGET_S) + 60.0
        self._lock = asyncio.Lock()
        self.errors = 0

    # ── listener ──
    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        try:
            await self._handle(message)
        except Exception:  # noqa: BLE001 — không bao giờ làm hỏng listener khác của bridge
            self.errors += 1
            logger.exception("decision_inbox: lỗi xử lý message (đã nuốt)")

    def _event(self, message) -> dict | None:
        """Sự kiện thô nếu đáng xử lý, ngược lại None (lọc rẻ — không spawn process cho mọi tin)."""
        content = message.content or ""
        me = getattr(self.bot, "user", None)
        if me is not None and message.author.id == me.id:
            self._note_bot(message)   # con trỏ 'tin bot gần nhất của channel' — kể cả tin KHÔNG thẻ (mục 3)
            if not self.inbox.TAG_RE.search(content):
                return None
            kind = "bot_message"
        elif message.author.bot:
            return None
        else:
            if str(message.author.id) not in self.user_ids or not self.inbox.parse_answer(content):
                return None
            kind = "user_message"
        ref = getattr(message, "reference", None)
        ch = message.channel
        return {
            "kind": kind, "message_id": str(message.id), "channel_id": str(ch.id),
            "parent_id": str(getattr(ch, "parent_id", None) or ""),
            "author_id": str(message.author.id),
            "reference_message_id": str(ref.message_id) if ref and ref.message_id else None,
            "content": content, "created_at": message.created_at.isoformat(),
            "guild_id": str(getattr(getattr(message, "guild", None), "id", "") or ""),
        }

    def _note_bot(self, message) -> None:
        try:
            self.inbox.note_bot_message(self.root, str(message.channel.id), str(message.id),
                                        message.created_at.isoformat())
        except Exception:  # noqa: BLE001 — thiếu con trỏ ⇒ script fail-closed ở T3, không hỏng listener
            logger.warning("decision_inbox: không ghi được con trỏ last-bot", exc_info=True)

    async def _handle(self, message) -> None:
        if not self.user_ids:
            return  # fail-CLOSED
        ev = self._event(message)
        if ev is None:
            return
        raw = self.root / "state" / "decision_inbox" / "raw"
        raw.mkdir(parents=True, exist_ok=True)
        line = json.dumps(ev, ensure_ascii=False) + "\n"
        day = dt.datetime.now(ICT).strftime("%Y%m%d")
        with (raw / f"{day}.jsonl").open("a", encoding="utf-8") as fh:   # nhật ký thô để đối soát (§6 bước 7)
            fh.write(line)
        evf = raw / f"ev_{ev['message_id']}.jsonl"
        evf.write_text(line, encoding="utf-8")
        try:
            async with self._lock:
                out = await self._run_script(evf)
        finally:
            evf.unlink(missing_ok=True)
        if out is None:
            return
        if out.get("react"):
            try:
                await message.add_reaction(out["react"])
            except Exception:  # noqa: BLE001
                logger.warning("decision_inbox: không thả được reaction", exc_info=True)
        if out.get("reply"):
            await message.reply(out["reply"], mention_author=False)

    async def _fail(self, kind: str, detail: dict) -> None:
        """Mọi lỗi chạy script phải để lại dấu: state errors.jsonl + bus status decision-inbox-error."""
        self.errors += 1
        logger.error("decision_inbox: %s %s", kind, detail)
        try:
            await asyncio.get_running_loop().run_in_executor(
                None, lambda: self.inbox.record_error(self.root, kind, detail))
        except Exception:  # noqa: BLE001
            logger.warning("decision_inbox: không ghi được record_error", exc_info=True)

    async def _run_script(self, evf: Path) -> dict | None:
        env = dict(os.environ, DECISION_INBOX_MODE=self.mode, DECISION_INBOX_USER_IDS=",".join(sorted(self.user_ids)))
        proc = await asyncio.create_subprocess_exec(
            sys.executable, str(self.script), "--event-file", str(evf), "--root", str(self.root),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env,
            start_new_session=True)   # cả nhóm tiến trình (close_bus_question, dispatch…) kill được 1 phát
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout)
        except asyncio.TimeoutError:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()
            await proc.wait()
            await self._fail("script_timeout", {"timeout_s": self.timeout, "event_file": evf.name})
            return None
        if proc.returncode != 0:
            await self._fail("script_rc", {"rc": proc.returncode, "event_file": evf.name,
                                           "stderr": stderr.decode("utf-8", "replace")[-300:]})
            return None
        for ln in reversed(stdout.decode("utf-8", "replace").splitlines()):
            try:
                return json.loads(ln)
            except ValueError:
                continue
        await self._fail("script_bad_json", {"event_file": evf.name, "stdout": stdout.decode("utf-8", "replace")[-300:]})
        return None


async def setup(bot, runner, components) -> None:
    root = Path(os.environ.get("DECISION_INBOX_ROOT") or DEFAULT_ROOT)
    ids = {x.strip() for x in os.environ.get("DECISION_INBOX_USER_IDS", "").split(",") if x.strip()}
    mode = os.environ.get("DECISION_INBOX_MODE", "shadow")
    if not ids:
        logger.warning("decision_inbox: DECISION_INBOX_USER_IDS rỗng ⇒ cog VÔ HIỆU (fail-closed)")
    await bot.add_cog(DecisionInboxCog(bot, root, ids, mode))
    logger.info("decision_inbox: loaded (mode=%s, users=%d, root=%s)", mode if mode in ("shadow", "live") else "shadow", len(ids), root)
