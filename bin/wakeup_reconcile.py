#!/usr/bin/env python3
"""wakeup_reconcile.py — tầng LEVEL-TRIGGERED cho hệ wake-up (cron */5).

Bất biến được cưỡng chế ở đây:

    Mọi job TERMINAL do Mike tự dispatch (`from=Mike`), có `discord_thread_id`, CHƯA có
    `replied_at`, và `ended_at` đã quá GRACE_SECONDS ⇒ thread đó PHẢI có ≥1 one-shot
    wakeup còn PENDING trong tasks.db của ccdb, HOẶC session của thread đang `running`.

MỘT NGOẠI LỆ, thêm 2026-08-20: job thuộc một đợt fan-out (`batch_id`, dispatch.sh
--batch-id) mà batch CÒN ĐANG BAY thì im lặng là ĐÚNG THIẾT KẾ — anh em terminal cuối cùng
của đợt sẽ bắn MỘT lượt wake gộp cho cả batch (bin/batch_wake.sh). Cứu sớm ở đây chính là
dựng lại phiên Mike thứ hai mà batch sinh ra để chặn. Batch hết bay mà vẫn chưa ai
`claim-reply` ⇒ quay lại đường cứu bình thường — reconciler là lưới CUỐI của cơ chế batch.

Vi phạm ⇒ gọi lại `bin/wake_thread.sh` với prompt template chuẩn (MIKE.md §8.4, claim-reply
làm dòng đầu). Một lượt wake THỪA là vô hại (claim-reply là test-and-set nguyên tử, lượt thừa
tốn đúng 1 lượt exit-1) — nhưng lượt thừa LẶP VÔ HẠN thì không.

⚠️ CÓ TRẦN CỨNG, đây là phần quan trọng nhất của file (arch-reviewer BLOCKER 2026-08-20):
bản đầu giả định "wake thành công ⇒ tasks.db có row pending ⇒ chu kỳ sau tự im". **Giả định
đó SAI.** ccdb `SchedulerCog._claim_one_shot` XOÁ row one-shot **TRƯỚC KHI** Claude chạy
(guard F1/F3, chống replay khi daemon restart) — row chỉ sống ~≤30s. Nên nếu phiên được đánh
thức không claim-reply (nó chết giữa chừng, hết usage-limit, hoặc đơn giản là không làm),
chu kỳ 5' kế tiếp lại thấy "thiếu bảo hiểm" và bắn tiếp — trần duy nhất sẽ là look-back 48h
= 576 lượt wake, mỗi lượt dựng một phiên Claude mới (tiền thật). Ca này KHÔNG giả định: đo
trên job board 08-17→08-20, 4/5 job `--bg` chưa `replied_at` ĐỀU đã có dòng SUCCESS trong
logs/wake_thread.log — tức đã được đánh thức mà vẫn không ai claim.

Ba cái trần, tất cả đều bền qua restart (ghi vào state file, atomic tmp+rename):
  - MAX_FIRES_PER_JOB — cứu tối đa N lượt cho MỘT job, hết thì DỪNG HẲN và báo người
    (fail-safe pause §5: "không tự sửa được thì gọi người", không im lặng thử mãi).
  - REFIRE_COOLDOWN — 2 lượt cứu cùng job phải cách nhau ≥ N giây (không phải 5').
  - MAX_WAKES_PER_CYCLE — chặn fan-out: ccdb restart / Mike hết usage-limit có thể làm
    hàng loạt thread cùng "thiếu bảo hiểm" một lúc.
Đếm được ghi TRƯỚC khi gọi wake (không phải sau): chết giữa chừng thì mất một lượt cứu,
còn hơn mất trần rồi bắn vô hạn.

VÌ SAO CẦN (kb/incidents/2026-08/2026-08-20-wake-push-utf8-surrogate-deletes-ladder.md):
mọi tín hiệu wake của fleet đều EDGE-triggered (push lúc job xong, ladder ScheduleWakeup,
CronCreate one-shot). Mất cạnh — push chết vì encoding/ccdb restart, Mike quên đặt ladder,
ccdb xoá row one-shot rồi INSERT fail — là thread ngủ VÔ HẠN, không cơ chế nào phát hiện
(08-20: user tự thấy sau 12 phút). Ba tháng qua fleet phản ứng bằng cách THÊM cạnh, mỗi
cạnh mới lại đẻ race mới. Script này KHÔNG thêm cạnh: nó so "trạng thái mong muốn vs thực
tế" mỗi 5 phút, nên MỌI lỗi edge — kể cả lỗi chưa biết — suy biến thành "trễ ≤ 5 phút"
thay vì "im lặng vô hạn". Cùng pattern với `resume_pending.py` / `jobs.sh reap`.
Đề xuất kiến trúc đã duyệt: agents/Mike/research/wakeup_architecture_redesign_20260820.md

KIÊM NHIỆM VỤ THỨ HAI — đọc `logs/wake_thread_errors.log`. File đó tồn tại từ 2026-08-15
nhưng CHƯA CÓ CHECKER NÀO đọc (kiểm chứng bằng grep toàn bin/ ngày 08-20), nên 3 lần push
chết vì surrogate im lặng suốt 5 ngày. Script này là consumer DUY NHẤT: đếm dòng MỚI kể từ
lần chạy trước (offset lưu trong state file, ghi atomic tmp+rename) rồi báo Trading Daily.

FAIL-SAFE (user mandate 2026-08-03 "ưu tiên quan sát tự nhiên hơn tự động phục hồi"):
đọc tasks.db không được, hoặc `/api/sessions` không trả lời ⇒ KHÔNG bắn wake nào cả, ghi
log và exit khác 0. Thà trễ một chu kỳ còn hơn bắn mù vào thread đang có người làm việc
(mỗi wake sai = mở một lượt Claude tốn phí, và push ngoài còn XOÁ ladder đang chờ của
thread trước khi tạo task mới).

LOOK-BACK CÓ TRẦN — chỉ xét job có `ended_at` trong LOOKBACK_SECONDS (48h) VÀ sau
MIN_EFFECTIVE_TS. Hai mốc phục vụ 2 việc khác nhau:
  - 48h: đừng quét cả lịch sử job board mỗi 5 phút (rẻ + job cũ hơn thế đã hết ý nghĩa).
  - MIN_EFFECTIVE_TS = mốc DEPLOY: job terminal CŨ chưa bao giờ có `replied_at` (đã xử lý
    tay, hoặc từ thời chưa có claim-reply) là bình thường và RẤT NHIỀU. Không có mốc này,
    lần chạy đầu tiên sẽ bắn hàng loạt wake vào các thread cũ đã yên.

Chống chạy đè chính nó: flock non-blocking, đang có bản chạy thì exit im lặng (0).

Exit code: 0 = đã đối chiếu xong (kể cả khi không bắn gì) hoặc bị khoá.
           2 = không đọc được tasks.db.   3 = không đọc được /api/sessions.
Cả 2 mã khác 0 đều nghĩa "chu kỳ này KHÔNG đối chiếu được", không phải "có vi phạm".

CHÍNH NÓ CŨNG PHẢI CÓ NGƯỜI GIÁM SÁT (arch-reviewer BLOCKER-1, vòng 3): hai nhánh abort ở
trên từng chỉ `print("ABORT …")` ra cron log — mà `bin/cron_health_check.py` chỉ kêu khi log
STALE theo mtime (không xảy ra: script vẫn chạy mỗi 5' và vẫn append) hoặc khi dòng khớp
`ERROR_PATTERNS` (đo thật: chuỗi cũ NO-MATCH). Tức tầng lưới cuối này có thể mù nhiều ngày
liền trong khi mọi dashboard báo OK — đúng lỗi "file log không ai đọc" mà nó sinh ra để vá.
Nay có HAI đường báo, cố ý không chọn một: dòng `CRITICAL ABORT <ts ICT> …` ra stdout (đường
này sống cả khi ccdb chết) VÀ `notify()` vào trading_daily sau ABORT_ALERT_AFTER chu kỳ mù
liên tiếp (nhanh hơn, nhưng đi qua chính ccdb nên im khi ccdb là thứ đang hỏng).
"""
import datetime
import fcntl
import glob
import importlib.util
import json
import os
import subprocess
import sqlite3
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _env(name, default):
    """Cho phép selfcheck trỏ mọi đường dẫn/URL sang fixture (giống
    DISCORD_CHANNELS_REGISTRY của discord_channel.sh). Production không set biến nào."""
    return os.environ.get(name) or default


JOBS_DIR = _env("WAKEUP_RECONCILE_JOBS_DIR", os.path.join(ROOT, "bus", "jobs"))
TASKS_DB = _env("WAKEUP_RECONCILE_TASKS_DB", "/workspace/ccdb-mike/data/tasks.db")
SESSIONS_API = _env("WAKEUP_RECONCILE_SESSIONS_API", "http://127.0.0.1:8199/api/sessions")
WAKE_SH = _env("WAKEUP_RECONCILE_WAKE_SH", os.path.join(ROOT, "bin", "wake_thread.sh"))
NOTIFY_SH = _env("WAKEUP_RECONCILE_NOTIFY_SH", os.path.join(ROOT, "bin", "notify_thread.sh"))
ERR_LOG = _env("WAKEUP_RECONCILE_ERR_LOG", os.path.join(ROOT, "logs", "wake_thread_errors.log"))
LOG = _env("WAKEUP_RECONCILE_LOG", os.path.join(ROOT, "logs", "wakeup_reconcile.log"))
STATE_FILE = _env("WAKEUP_RECONCILE_STATE", os.path.join(ROOT, "state", "wakeup_reconcile_state.json"))
LOCK_FILE = _env("WAKEUP_RECONCILE_LOCK", os.path.join(ROOT, "state", "locks", "wakeup_reconcile.lock"))
BATCHES_DIR = _env("WAKEUP_RECONCILE_BATCHES_DIR", os.path.join(ROOT, "bus", "batches"))

# batch_in_flight: một job thuộc đợt fan-out (dispatch.sh --batch-id) CỐ Ý im lặng khi xong
# sớm — anh em cuối cùng của đợt mới bắn MỘT lượt wake gộp (bin/batch_wake.sh, RCA lỗi #1
# 2026-08-20). Không biết luật đó thì reconciler thấy "job terminal, chưa replied, thread
# không có wakeup pending" là ĐÚNG VI PHẠM theo bất biến cũ, và cứu nó sau 3 phút — dựng lại
# đúng cái phiên Mike thứ hai mà batch sinh ra để chặn. Import trực tiếp (không subprocess):
# gọi cho từng candidate mỗi 5 phút, một tiến trình python mỗi lần là phí vô ích.
# Nạp theo ĐƯỜNG DẪN, không `sys.path.insert(0, bin/)`: chèn bin/ lên đầu sys.path nghĩa là
# bất kỳ file bin/<tên>.py nào trùng tên module stdlib (token.py, types.py…) sẽ che stdlib cho
# CẢ tiến trình này — hôm nay chưa file nào trùng (đo 118 file), nhưng đó là bẫy đặt sẵn cho
# người viết script sau (arch-reviewer N7).
_mj_spec = importlib.util.spec_from_file_location(
    "mike_json_for_reconcile", os.path.join(ROOT, "bin", "mike_json.py"))
mike_json = importlib.util.module_from_spec(_mj_spec)
_mj_spec.loader.exec_module(mike_json)


def _batch_in_flight(batch_id, job_id):
    """Lỗi lạ ở đây KHÔNG được giết cả chu kỳ của LƯỚI CUỐI: không đọc được ⇒ False =
    "không đang bay" ⇒ cứu như trước khi có batch (thà wake thừa còn hơn ngủ vô hạn)."""
    try:
        return mike_json.batch_in_flight(BATCHES_DIR, batch_id, JOBS_DIR, job_id)
    except Exception as exc:
        log("BATCH-CHECK-FAILED batch=%s job=%s: %s — coi như KHÔNG đang bay" % (batch_id, job_id, exc))
        return False

# Tên topic trong kb/discord_channels.json — KHÔNG bao giờ ID trần (bin/discord_id_gate.sh
# chặn commit nếu snowflake xuất hiện ngoài registry; 4 lần rò rỉ chéo topic đều từ ID trần).
ALERT_CHANNEL = _env("WAKEUP_RECONCILE_ALERT_CHANNEL", "trading_daily")

TERMINAL = ("done", "failed", "timeout")   # KHÔNG gồm running/retrying/pending_resume
GRACE_SECONDS = 180        # job xong <3' thì push/ladder bình thường vẫn đang trên đường
LOOKBACK_SECONDS = 48 * 3600
# RESCUE_MAX_AGE ≠ LOOKBACK_SECONDS (tách ra 2026-08-20, arch-reviewer killer objection vòng
# audit trước-commit). Dùng CHUNG một hằng số cho "cửa sổ quét chi phí" và "job còn đáng đánh
# thức" là sai: dry-run trên job board thật cho ra job DollarBill_20260818_120602 kết thúc
# 155.121s (43 GIỜ) trước vẫn bị BẮN vào thread kênh `plan_approval` (kb/discord_channels.json — kênh duyệt plan) — sau bất
# kỳ khoảng mù nào (ccdb restart, 4 lần riêng 08-17), reconciler dựng hàng loạt phiên Claude để
# post KẾT QUẢ CŨ vào kênh tiền thật, trái hẳn nhãn công bố "trễ ≤5 phút". Job cũ hơn mức này
# CHỈ được báo (1 lần, xem too_old trong main()), KHÔNG bao giờ tự đánh thức.
RESCUE_MAX_AGE = 4 * 3600
MAX_FIRES_PER_JOB = 3      # hết trần ⇒ dừng hẳn job đó + báo người ĐÚNG 1 LẦN
REFIRE_COOLDOWN = 900      # ≥15' giữa 2 lượt cứu cùng job (3 chu kỳ cron)
MAX_WAKES_PER_CYCLE = 3    # chặn fan-out khi nhiều thread cùng mất tín hiệu
MAX_STALE_NOTIFIES_PER_CYCLE = 3   # cùng trần với MAX_WAKES_PER_CYCLE — chặn fan-out
# khi read_state() trả {} (state hỏng/mất) làm bùng toàn bộ tồn đọng too_old 48h cùng lúc
# ⚠️ TODO rà lại 2026-08-22 (arch-reviewer vòng 4, Tier-3 — không phải BLOCKER, chỉ nhiễu chứ
# không im lặng/không dựng phiên/không chạm tiền): khi `mike/state/` không ghi được, MỖI
# nhánh ghi state đang tự báo "tự dừng" RIÊNG (too_old + fire/escalate) — đo được 2 tin/chu
# kỳ, đều đặn KHÔNG dedupe (CA f8 chỉ assert `>= 1`, không bó trần). Ngoại suy cron */5 =
# ~576 tin/ngày vào trading_daily nếu đĩa đầy/lệch quyền kéo dài. Hướng sửa nếu tới hạn vẫn
# thấy đáng làm: in `CRITICAL` ra STDOUT khi write_state() hỏng (hiện chỉ vào
# logs/wakeup_reconcile.log — không checker nào đọc) rồi hạ tần suất notify Discord xuống 1
# lần/N chu kỳ, tương tự ABORT_ALERT_AFTER.
# Bao nhiêu chu kỳ abort LIÊN TIẾP thì gọi người. 3 chu kỳ */5 = 15' mù hoàn toàn — đủ dài để
# không kêu vì một lần ccdb restart, đủ ngắn để không lặp lại đúng lỗi 5 ngày im lặng của 08-20.
ABORT_ALERT_AFTER = 3
# Mốc hiệu lực = lúc deploy script này (2026-08-20 11:25 ICT / 04:25 UTC). Xem docstring.
MIN_EFFECTIVE_TS = int(_env("WAKEUP_RECONCILE_MIN_TS", "1787199900"))


def _ict():
    """Dấu thời gian ICT có offset tường minh, KHÔNG trông cậy TZ của tiến trình cron (§16)."""
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")


def log(msg):
    """Dấu thời gian ICT có offset tường minh — CÙNG ĐỊNH DẠNG `date -Iseconds` mà
    wake_thread.sh dùng cho logs/wake_thread.log và wake_thread_errors.log.

    Không phải chuyện thẩm mỹ: `daily_retro.sh` đếm cả 3 file bằng CÙNG một tiền tố
    `^$TODAY` (ngày ICT). Nếu file này ghi UTC như bản đầu thì cửa sổ ngày lệch 7 tiếng
    và số "reconciler đã cứu" sẽ ghép nhầm ngày. Neo múi giờ tường minh (§16), không
    trông cậy TZ của tiến trình cron.
    """
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        ts = _ict()
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (ts, msg))
    except Exception:
        pass


# --- state (offset của error log) ------------------------------------------------------
def read_state():
    """State rỗng là hợp lệ (lần chạy đầu). State HỎNG thì không — nó reset cả trần lẫn
    offset error-log một cách im lặng, nên phải để lại vết."""
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            s = json.load(f)
    except Exception as e:
        log("STATE-CORRUPT %s: %s — trần và offset errlog bị reset về 0" % (STATE_FILE, e))
        return {}
    if not isinstance(s, dict):
        log("STATE-CORRUPT %s: không phải object JSON — trần bị reset" % STATE_FILE)
        return {}
    return s


def write_state(state):
    """Atomic tmp+rename. Trả True khi CHẮC CHẮN đã ghi xuống đĩa.

    Giá trị trả về là load-bearing, không phải trang trí: toàn bộ trần chống-bắn-vô-hạn
    nằm trong file này, nên "ghi hỏng" = "trần bốc hơi". Bản trước nuốt exception rồi fire
    tiếp ⇒ chỉ cần `state/` không ghi được (ENOSPC, lệch quyền) là quay lại đúng lỗi
    BLOCKER: bắn mỗi 5' vô tận, `capped=0` mãi mãi, exit 0, không ai được báo (arch-reviewer
    đo thật 6/6 chu kỳ, vòng 2 — 2026-08-20). §5: không chắc hành động đã xảy ra chưa thì
    DỪNG và gọi người, đừng làm tiếp.

    Atomic cũng vẫn cần: cron 5' có thể bị kill giữa chừng, một state file cụt sẽ khiến lần
    sau đọc lại TỪ ĐẦU file lỗi và báo động toàn bộ lịch sử như thể vừa mới xảy ra.
    """
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)
        os.replace(tmp, STATE_FILE)
        return True
    except Exception as e:
        log("STATE-WRITE-FAILED %s: %s" % (STATE_FILE, e))
        return False


# --- nhiệm vụ 2: giám sát wake_thread_errors.log ---------------------------------------
def check_error_log(state):
    """Đếm dòng MỚI trong wake_thread_errors.log kể từ lần chạy trước, báo Trading Daily.

    Nhận diện file bị xoay vòng/cắt bằng (inode, size): size nhỏ hơn offset đã lưu hoặc
    inode đổi ⇒ đọc lại từ 0 thay vì seek quá đuôi file (sẽ im lặng bỏ sót mọi dòng mới).
    """
    try:
        st = os.stat(ERR_LOG)
    except OSError:
        return 0  # chưa có lỗi nào bao giờ — trạng thái BÌNH THƯỜNG, không phải sự cố
    off = int(state.get("errlog_offset", 0))
    ino = str(state.get("errlog_inode", ""))
    if ino != str(st.st_ino) or st.st_size < off:
        off = 0
    new = []
    try:
        with open(ERR_LOG, encoding="utf-8", errors="replace") as f:
            f.seek(off)
            new = [ln.rstrip("\n") for ln in f if ln.strip()]
            off = f.tell()
    except Exception as e:
        log("ERRLOG-READ-FAILED %s: %s" % (ERR_LOG, e))
        return 0
    if not new:
        state["errlog_offset"] = off
        state["errlog_inode"] = str(st.st_ino)
        return 0
    log("ERRLOG %d dòng mới" % len(new))
    msg = ("⚠️ **wake push lỗi** — %d dòng mới trong `logs/wake_thread_errors.log` "
           "(push wake-on-completion thất bại; thread liên quan có thể mất tín hiệu — "
           "reconciler sẽ tự cứu ở chu kỳ này nếu thật sự không còn wakeup nào chờ).\n"
           "```\n%s\n```" % (len(new), "\n".join(new[-5:])[:1200]))
    # Offset CHỈ tiến khi tin nhắn đã ra được. Gửi hỏng mà vẫn tiến offset = mất vĩnh viễn
    # đúng những dòng lỗi quan trọng nhất: notify_thread.sh chết chủ yếu khi ccdb sập, mà
    # ccdb sập cũng chính là lúc push wake lỗi. Giữ offset ⇒ chu kỳ sau báo lại (báo trùng
    # một lần thì thấy được; báo thiếu thì không).
    if not notify(msg):
        # GIỮ CẢ offset LẪN inode. Ghi inode riêng (bản trước làm vậy) là một cái bẫy: log
        # xoay vòng đúng lúc notify hỏng ⇒ chu kỳ sau thấy inode "đã khớp" nên seek thẳng
        # tới offset cũ TRONG FILE MỚI và nhảy qua mọi dòng đầu (arch-reviewer đo: báo 20/30
        # dòng, mất 10 dòng lỗi vĩnh viễn). Giữ nguyên cả hai ⇒ ca xấu nhất là BÁO TRÙNG,
        # đúng hướng an toàn đã tự nêu ở trên.
        log("NOTIFY-FAILED — GIỮ offset+inode, sẽ báo lại chu kỳ sau")
        return len(new)
    state["errlog_offset"] = off
    state["errlog_inode"] = str(st.st_ino)
    return len(new)


def notify(msg):
    """Gửi 1 tin vào topic ALERT_CHANNEL. True = chắc chắn đã gửi được."""
    try:
        r = subprocess.run([NOTIFY_SH, msg, ALERT_CHANNEL], timeout=30,
                           capture_output=True, text=True)
    except Exception as e:
        log("NOTIFY-EXC: %s" % e)
        return False
    if r.returncode != 0:
        log("NOTIFY-RC=%d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[:200]))
        return False
    return True


# --- nhiệm vụ 1: đối chiếu bất biến ----------------------------------------------------
def read_pending_threads():
    """Thread nào đang còn ≥1 one-shot wakeup CHỜ CHẠY trong tasks.db của ccdb.

    Read-only URI (mode=ro) — đây là DB của service khác đang chạy, tuyệt đối không ghi.
    Trả None nếu không đọc được (gọi bên ngoài phải fail-safe, đừng coi là "rỗng").
    """
    try:
        con = sqlite3.connect("file:%s?mode=ro" % TASKS_DB, uri=True, timeout=5)
        try:
            rows = con.execute(
                "SELECT thread_id FROM scheduled_tasks "
                "WHERE one_shot = 1 AND enabled = 1 AND executed_at IS NULL "
                "AND thread_id IS NOT NULL"
            ).fetchall()
        finally:
            con.close()
    except Exception as e:
        log("TASKS-DB-UNREADABLE %s: %s" % (TASKS_DB, e))
        return None
    return {str(r[0]) for r in rows}


def read_running_threads():
    """Thread nào đang có session state=running (đang xử lý — đánh thức là vô nghĩa/hại).

    Trả None nếu API không trả lời được: ccdb chết thì KHÔNG được suy ra "mọi session đều
    idle" rồi bắn wake cho tất cả (wake cũng sẽ chết theo, chỉ tổ đầy log lỗi).
    """
    # `?state=running&limit=100`: mặc định của API là limit=20 và HIỆN ĐANG CHẠM CAP đó
    # (đo 2026-08-20: trả đúng 20 session). Xin tường minh thay vì trông cậy vào chi tiết
    # nội bộ của repo khác về việc session live có luôn được merge vào không.
    sep = "&" if "?" in SESSIONS_API else "?"
    url = SESSIONS_API + sep + "state=running&limit=100"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, OSError, ValueError) as e:
        log("SESSIONS-API-UNREACHABLE %s: %s" % (url, e))
        return None
    out = set()
    for s in (data.get("sessions") or []):
        if str(s.get("state") or "").lower() == "running" and s.get("thread_id"):
            out.add(str(s["thread_id"]))
    return out


def scan_unreplied(now):
    """Job terminal from=Mike, có thread, chưa replied, quá hạn ân xá, trong cửa sổ hiệu lực.

    Sắp xếp theo ended_at TĂNG DẦN: job chờ lâu nhất được cứu trước (xem fire loop —
    mỗi thread chỉ bắn 1 lần/chu kỳ). Trả về (candidates, n_unreadable) — số record JSON
    không parse được PHẢI lộ ra ngoài (arch-reviewer F4): một script sinh ra để diệt lỗ im
    lặng mà tự nuốt lỗi đọc record thì đúng cùng loại bug nó đang vá.
    """
    out = []
    n_unreadable = 0
    for fp in glob.glob(os.path.join(JOBS_DIR, "*.json")):
        try:
            with open(fp, encoding="utf-8") as f:
                j = json.load(f)
        except Exception as exc:
            n_unreadable += 1
            log("JOB-UNREADABLE %s: %s" % (fp, exc))
            continue
        if str(j.get("status") or "") not in TERMINAL:
            continue
        if str(j.get("from") or "") != "Mike":
            continue
        # CHỈ job chạy NỀN (--bg). Job dispatch ĐỒNG BỘ cũng có from=Mike + thread ghim,
        # nhưng theo thiết kế nó KHÔNG BAO GIỜ được push wake (2 call site wake_thread.sh
        # đều nằm trong _bg_wrapper) và KHÔNG BAO GIỜ có replied_at — caller bash đã đọc
        # kết quả tại chỗ rồi. Không lọc thì mọi lượt `wags_autofix.sh` (dispatch sync,
        # from mặc định = Mike) sẽ đánh thức topic Architecture 3' sau khi chạy, dựng phiên
        # Claude ở thread không có ai chờ — đúng thứ header wake_thread.sh gọi là "wasted
        # spend". Đo thật trên job board: 192/773 record là sync, ca Wags_20260820_012007
        # khớp y hệt. Dấu hiệu phân biệt: chỉ _bg_wrapper ghi field `pid` (dispatch.sh).
        # ⚠️ TODO rà lại 2026-08-22 (arch-reviewer F2, trước-commit 08-20): `pid` KHÔNG phân
        # biệt "Mike live dispatch" với "cron tự dispatch" (vd DollarBill_*_1206xx plan-cron,
        # Winston_*_0120xx ops-autofix) — cả 2 lớp đều có pid + không bao giờ replied_at, nên
        # đều bị coi là "đang chờ cứu".
        # SỐ ĐO SẴN (re-audit 08-20, đừng đo lại từ đầu — chỉ cần đo LẠI để xem xu hướng có
        # đổi không): job board 4 ngày 08-16→08-20, **14/14 job** `from=Mike` có `pid` chưa
        # `replied_at` ĐỀU là cron-origin — Wags_20260816_090511 (wags_autofix), Taylor_
        # 20260817_010002 (corp_action_daily 00:30), DollarBill_20260817_120450/20260818_
        # 120602/120604/20260819_120605 (bq_freshness_check → plan-cron 19:0x, đích thread
        # kênh `plan_approval` = kênh duyệt plan), Winston_20260817_195843/20260820_012008
        # (ops_autofix 08:20). 0 ca "Mike live dispatch mất wakeup" trong mẫu này.
        # GIẢM NHẸ đã kiểm: KHÔNG phải toàn bộ là false positive — `DollarBill_20260819_120605`
        # là true-positive thật (push chết thật, `wake_thread_errors.log` ghi HTTP 409 lúc
        # 19:16:20 cùng ngày), và push `_bg_wrapper` gốc đã từng bắn đúng vào thread đó cho
        # các job còn lại (task_id 1764/1765/1815 trong wake_thread.log) — nên reconciler
        # không mở thêm 1 class kênh mới, chỉ LẶP LẠI 3× một wake vốn dĩ đã tồn tại.
        # Nếu tới hạn mà lớp cron-origin VẪN bị cứu HẰNG NGÀY (không phải sự cố push thật như
        # ca DollarBill 08-19) ⇒ LOẠI job dispatch-từ-cron khỏi phạm vi reconciler bằng field
        # phân biệt mới (dispatch.sh stamp thêm — vd DISPATCH_ORIGIN=cron/live), KHÔNG nới
        # trần MAX_FIRES_PER_JOB để che triệu chứng.
        if not str(j.get("pid") or "").strip():
            continue
        if str(j.get("replied_at") or "").strip():
            continue
        tid = str(j.get("discord_thread_id") or "").strip()
        if not tid.isdigit():
            continue
        try:
            ended = int(float(j.get("ended_at")))
        except (TypeError, ValueError):
            continue
        if ended < MIN_EFFECTIVE_TS or ended < now - LOOKBACK_SECONDS:
            continue
        if now - ended <= GRACE_SECONDS:
            continue
        bid = str(j.get("batch_id") or "").strip()
        jid_here = str(j.get("job_id") or os.path.basename(fp)[:-5])
        if bid and _batch_in_flight(bid, jid_here):
            # Im lặng CÓ CHỦ Ý, không phải tín hiệu mất: anh em cùng batch còn đang chạy và
            # sẽ bắn một lượt wake gộp cho cả đợt. Batch hết bay (đã có người claim, hoặc mọi
            # member còn lại đã chết/quá deadline) mà vẫn chưa ai claim-reply ⇒ chu kỳ sau
            # rơi lại vào đường cứu bình thường — đó chính là lưới cuối của cơ chế batch.
            log("BATCH-IN-FLIGHT bỏ qua %s (batch=%s) — chờ anh em cùng đợt" % (jid_here, bid))
            continue
        out.append({"job_id": str(j.get("job_id") or os.path.basename(fp)[:-5]),
                    "to": str(j.get("to") or "?"),
                    "status": str(j.get("status")),
                    "thread_id": tid, "ended_at": ended})
    return sorted(out, key=lambda x: x["ended_at"]), n_unreadable


def wake_prompt(job):
    """Template chuẩn MIKE.md §8.4 — claim-reply là DÒNG ĐẦU TIÊN, kèm đúng job_id.

    Cố ý KHÔNG nhúng preview nội dung log (bài học 08-20: chuỗi cắt theo byte đẻ surrogate
    làm chết cả lượt push). Lượt wake nào cũng phải đọc job record thật trước khi post
    (luật §8.3), nên preview không mang thêm thông tin gì mà chỉ thêm một tầng encoding.
    """
    return (
        "Đầu tiên: %s/bin/jobs.sh claim-reply %s → exit 1 → ScheduleWakeup(noop:true,stop:true), "
        "DỪNG. exit 0 → [logic poll + post bình thường]. exit 2 → báo job record thiếu, đừng im "
        "lặng. exit 3 → job chưa xong, post progress bình thường, KHÔNG claim. "
        "[WAKEUP-RECONCILER] Job `%s` (%s) đã terminal (status=%s) nhưng CHƯA ai post kết quả và "
        "thread này không còn wakeup nào đang chờ — tín hiệu wake gốc đã mất. Đọc kết quả bằng "
        "`%s/bin/jobs.sh status %s` + logfile ghi trong job record, rồi post kết quả cho user."
    ) % (ROOT, job["job_id"], job["job_id"], job["to"], job["status"], ROOT, job["job_id"])


def fire_wake(job, attempt):
    """`attempt` vào thẳng TÊN task ccdb — không phải trang trí (arch-reviewer #3, vòng 3).

    `wake_thread.sh` đặt tên task là `dispatch-wake-<suffix>`, mà cột `name` của
    `scheduled_tasks` là `TEXT NOT NULL UNIQUE`. Suffix cố định `<job>-reconcile` nghĩa là:
    chỉ cần còn tồn đọng một row cùng tên (đã `mark_executed` nhưng chưa bị xoá, hoặc
    `enabled=0` — CẢ HAI đều lọt khỏi truy vấn pending ở `read_pending_threads`), thì lượt
    cứu #2/#3 nhận 409 và TIÊU TRẦN mà không đánh thức được ai. Đo live 2026-08-20: 0 row
    leftback nên rủi ro hiện tại thấp — nhưng cái giá của việc vá là 1 số trong chuỗi.
    """
    try:
        r = subprocess.run(
            [WAKE_SH, job["thread_id"], wake_prompt(job),
             "%s-reconcile%d" % (job["job_id"], attempt)],
            capture_output=True, text=True, timeout=30)
    except Exception as e:
        log("WAKE-FAILED job=%s thread=%s: %s" % (job["job_id"], job["thread_id"], e))
        return False
    if r.returncode != 0:
        log("WAKE-FAILED job=%s thread=%s rc=%d: %s"
            % (job["job_id"], job["thread_id"], r.returncode,
               (r.stderr.strip() or r.stdout.strip())[:300]))
        return False
    log("RESCUED job=%s to=%s status=%s thread=%s (chờ %ds không ai trả lời)"
        % (job["job_id"], job["to"], job["status"], job["thread_id"],
           int(time.time()) - job["ended_at"]))
    return True


def note_abort(state, kind, n_err):
    """Đếm chu kỳ abort LIÊN TIẾP; ≥ABORT_ALERT_AFTER thì gọi người ĐÚNG 1 LẦN.

    VÌ SAO CẦN (arch-reviewer BLOCKER-1, vòng 3 — 2026-08-20): hai nhánh fail-safe của
    script này chỉ `print("ABORT …")` ra `logs/wakeup_reconcile_cron.log`. Consumer duy
    nhất của file đó là `bin/cron_health_check.py`, và nó chỉ kêu khi (a) log STALE theo
    MTIME — KHÔNG kích hoạt, vì script vẫn chạy mỗi 5' và vẫn append đều; hoặc (b) dòng
    khớp `ERROR_PATTERNS`. Chạy chính regex đó lên chuỗi cũ: **no-match**. Nghĩa là
    `TASKS_DB` đổi quyền/đổi deploy path, hay ccdb sập lâu, thì tầng lưới CUỐI này mù vô
    thời hạn trong khi mọi dashboard báo OK — đúng y lỗi "một file log không ai đọc" đã
    gây ra sự cố 08-20 mà chính nó sinh ra để chấm dứt.

    Hai đường báo, cố ý KHÔNG chọn một:
      - `CRITICAL ABORT` ra stdout ⇒ `cron_health_check_daily.sh` (08:25 T2-T6) bắt được
        (`CRITICAL` nằm sẵn trong ERROR_PATTERNS). Đường này sống cả khi ccdb chết.
      - `notify()` vào trading_daily ⇒ nhanh (15'), nhưng nó ĐI QUA ccdb nên khi ccdb chính
        là thứ đang hỏng thì nó im theo. Vì vậy mới cần đường trên.
    Kèm dấu thời gian ICT vào dòng in ra: `cron_health_check.scan_errors` lấy datestamp gần
    nhất để bỏ qua hit cũ hơn 10 ngày — không có dấu thời gian thì một dòng abort cũ sẽ được
    báo lại mãi mãi.
    """
    n = int(state.get("consecutive_aborts", 0)) + 1
    state["consecutive_aborts"] = n
    if n >= ABORT_ALERT_AFTER and not state.get("abort_alerted"):
        # `abort_alerted` CHỈ bật khi tin đã gửi được — notify hỏng thì chu kỳ sau báo lại
        # (cùng nguyên tắc với offset error-log: báo trùng thấy được, báo thiếu thì không).
        if notify("🛑 **wakeup-reconciler MÙ %d chu kỳ liên tiếp** (~%d phút) — %s. Trong "
                  "khoảng này KHÔNG có tầng nào bắt được thread ngủ vì mất tín hiệu wake. "
                  "Kiểm tra `%s` và `%s`; log chi tiết: `logs/wakeup_reconcile.log`."
                  % (n, n * 5, kind, TASKS_DB, SESSIONS_API)):
            state["abort_alerted"] = True
    # Giá trị trả về của write_state là LOAD-BEARING ở đây y như trong vòng fire (arch-reviewer
    # N3, vòng 4): bộ đếm mù sống trong state file, ghi hỏng ⇒ `consecutive_aborts` đóng băng ở
    # 1 mãi mãi ⇒ ngưỡng ABORT_ALERT_AFTER không bao giờ tới ⇒ đường notify chết câm, và dòng
    # CRITICAL còn báo SAI độ dài sự cố (§28: báo giá trị đo được, đừng để nhãn nói thay). Đo
    # thật: state dir chmod 500 + tasks.db hỏng 5 chu kỳ ⇒ luôn in "liên tiếp=1", notify=0 lần.
    # Không im lặng được thì phải nói ra trên đường CRITICAL — đường duy nhất còn sống ca này.
    _persisted = write_state(state)
    print("CRITICAL ABORT %s %s — không bắn wake nào (chu kỳ mù liên tiếp=%d%s, errlog_new=%d)"
          % (_ict(), kind, n,
             "" if _persisted else " — ⚠️ KHÔNG ghi được state, bộ đếm KHÔNG tích luỹ được "
             "nên con số này là 1 giả và cảnh báo Discord sẽ không bao giờ bắn",
             n_err))
    return n


def clear_abort(state):
    """Đối chiếu lại được ⇒ reset bộ đếm + cho phép báo lần sau. Không reset thì một lần
    ccdb sập sẽ khoá vĩnh viễn khả năng cảnh báo cho lần sập kế tiếp."""
    if state.get("consecutive_aborts") or state.get("abort_alerted"):
        state["consecutive_aborts"] = 0
        state["abort_alerted"] = False
        if not write_state(state):
            # Nhẹ hơn write_state hỏng ở too_old/escalate (không tự spam notify — chu kỳ
            # NÀY đã đối chiếu lại được, chỉ có bộ nhớ "đã báo lần trước" không xoá được),
            # nhưng vẫn phải LỘ RA: không thì `abort_alerted=True` kẹt trên đĩa ⇒ lần ccdb
            # sập KẾ TIẾP không bao giờ được cảnh báo, mà không dấu vết nào giải thích vì
            # sao (arch-reviewer vòng 3, mục nhẹ đi kèm killer chính).
            log("STATE-UNWRITABLE (clear_abort) — reset KHÔNG persist được, "
                "abort_alerted có thể vẫn kẹt True cho lần sập kế tiếp")


def prune_fired(state, now):
    """Bỏ bản ghi 'đã cứu' cũ hơn look-back — state file không được phình vô hạn."""
    hist = state.get("fired")
    if not isinstance(hist, dict):
        hist = {}
    state["fired"] = {k: v for k, v in hist.items()
                      if isinstance(v, dict) and int(v.get("last", 0)) > now - LOOKBACK_SECONDS}
    return state["fired"]


def main():
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    lock = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        # In RA STDOUT kể cả khi không làm gì: cron ghi stdout vào logs/wakeup_reconcile_cron.log
        # và bin/cron_health_check.py đo sức khoẻ job `*/5` bằng MTIME của chính file đó. Một
        # job im lặng tuyệt đối trông y hệt một job đã chết (nó đã báo STALE giả cho
        # resume_pending.py đúng vì lý do này).
        print("SKIP đang có bản chạy khác giữ lock")
        return 0

    state = read_state()
    # Giám sát log lỗi chạy TRƯỚC phần đối chiếu: nó độc lập với ccdb, và đúng lúc ccdb
    # hỏng (tasks.db/API không đọc được) mới là lúc file lỗi đó có nội dung cần báo nhất.
    n_err = check_error_log(state)
    write_state(state)

    pending = read_pending_threads()
    if pending is None:
        note_abort(state, "tasks.db không đọc được", n_err)
        return 2
    running = read_running_threads()
    if running is None:
        note_abort(state, "/api/sessions không trả lời", n_err)
        return 3
    clear_abort(state)

    now = int(time.time())
    hist = prune_fired(state, now)
    cand, n_unreadable = scan_unreplied(now)
    # Tách job "còn đáng đánh thức" khỏi "quá cũ" NGAY tại đây — xem RESCUE_MAX_AGE ở đầu
    # file. Job quá cũ CHỈ được báo (đúng 1 lần, dedupe qua `hist[jid]["stale_notified"]`,
    # cùng cơ chế `escalated` bên dưới), KHÔNG BAO GIỜ tự đánh thức.
    too_old = [j for j in cand if now - j["ended_at"] > RESCUE_MAX_AGE]
    cand = [j for j in cand if now - j["ended_at"] <= RESCUE_MAX_AGE]
    n_stale_notified = 0
    for job in too_old:
        jid = job["job_id"]
        rec = hist.get(jid) or {}
        # `escalated` (bỏ cuộc, xem vòng fire dưới) VÀ `stale_notified` cùng dedupe vào một
        # rec — một job đã "bỏ cuộc" rồi vượt 4h không cần nhận thêm tin "quá cũ" khác giọng
        # cho cùng một sự việc (arch-reviewer N2, re-audit trước-commit 08-20).
        if rec.get("stale_notified") or rec.get("escalated"):
            continue
        if n_stale_notified >= MAX_STALE_NOTIFIES_PER_CYCLE:
            log("STALE-CYCLE-CAP đạt %d tin/chu kỳ, hoãn %d job quá cũ còn lại sang chu kỳ sau"
                % (MAX_STALE_NOTIFIES_PER_CYCLE, len(too_old) - too_old.index(job)))
            break
        # Ghi TRƯỚC khi gọi notify — CÙNG thứ tự với vòng fire (§5 gốc): nếu không ghi được
        # thì KHÔNG ĐƯỢC báo, dù chỉ 1 lần. Đảo ngược thứ tự (notify trước, ghi sau) là đúng
        # lỗ arch-reviewer đo được (chmod 500 state dir ⇒ notify "quá cũ" bắn lại MỖI chu kỳ
        # vì dedupe không bao giờ persist được ⇒ 4/4 chu kỳ ra 8 tin, ngoại suy 288/ngày/job).
        # Đánh đổi chấp nhận được, ĐÃ có tiền lệ ở `n` của vòng fire: một notify() rớt mạng
        # hiếm khi xảy ra thì mất, còn hơn spam vô hạn khi cả state lẫn notify đều hỏng.
        rec["stale_notified"] = True
        rec["last"] = now
        hist[jid] = rec
        if not write_state(state):
            log("STATE-UNWRITABLE (too_old) — DỪNG báo job quá cũ (không có dedupe thì "
                "không được báo lặp)")
            notify("🛑 **wakeup-reconciler tự dừng (nhánh quá cũ)** — không ghi được "
                   "`%s` nên KHÔNG còn trần chống báo-lặp; dừng báo job quá cũ tới khi "
                   "ghi được. Kiểm tra dung lượng/quyền của `mike/state/`."
                   % STATE_FILE)
            break
        age_h = (now - job["ended_at"]) / 3600.0
        if notify("⏸️ **wakeup-reconciler: job quá cũ, KHÔNG tự đánh thức** — `%s` (%s, "
                  "status=%s) terminal cách đây %.1f giờ (> trần %.0fh) mà chưa ai "
                  "`claim-reply`. KHÔNG bắn wake (tránh post kết quả cũ vào thread `%s`) — "
                  "cần xử tay: `bin/jobs.sh status %s`."
                  % (jid, job["to"], job["status"], age_h, RESCUE_MAX_AGE / 3600.0,
                     job["thread_id"], jid)):
            n_stale_notified += 1
    fired_threads, n_fired, n_capped = set(), 0, 0
    for job in cand:
        tid, jid = job["thread_id"], job["job_id"]
        if tid in pending or tid in running or tid in fired_threads:
            # `fired_threads`: tối đa 1 wake/thread/chu kỳ. ccdb XOÁ one-shot pending của
            # thread ngay trước khi tạo task mới, nên bắn 2 phát liền cho cùng thread là
            # phát sau huỷ phát trước — job còn lại tự được cứu ở chu kỳ 5' kế tiếp.
            continue
        rec = hist.get(jid) or {}
        if int(rec.get("n", 0)) >= MAX_FIRES_PER_JOB:
            n_capped += 1
            if not rec.get("escalated"):
                # Cứu N lần không ăn thua = có gì đó reconciler KHÔNG sửa được (phiên chết
                # hẳn, thread bị archive, Mike hết quota). Gọi người ĐÚNG 1 LẦN rồi thôi.
                #
                # Ghi TRƯỚC khi notify — CÙNG thứ tự với too_old (arch-reviewer killer vòng
                # 3, re-audit trước-commit 08-20): bản đầu notify-trước-ghi-sau khiến, khi
                # state không ghi được, `rec["n"]` đã persist=3 từ TRƯỚC (lúc state còn sống)
                # nên điều kiện `n >= MAX_FIRES_PER_JOB` ở trên đúng MỖI chu kỳ bất kể chu kỳ
                # này ghi được hay không — đo được 5/5 chu kỳ gửi lại đúng tin "bỏ cuộc", còn
                # tin CHẨN ĐOÁN ĐÚNG "tự dừng" thì không bao giờ bắn vì nhánh này luôn
                # `continue` trước khi chạm logic kiểm write_state của vòng fire chính.
                # Đánh đổi CHẤP NHẬN ĐƯỢC (đã có tiền lệ ở `n`/too_old): một tin "bỏ cuộc"
                # hiếm khi rớt vì Discord tạch đúng lúc persist thành công thì mất, còn hơn
                # spam vô hạn khi state hỏng — dedupe qua state, không dedupe được thì phải
                # dừng hẳn, không đoán.
                _n, _ok = int(rec.get("n", 0)), int(rec.get("ok", 0))
                rec["escalated"] = True
                # Job đã "bỏ cuộc" ở đây (~30-45' sau khi terminal, luôn TRƯỚC RESCUE_MAX_AGE
                # =4h vì 3 lượt cứu cần tối thiểu 2×REFIRE_COOLDOWN=30') không cần thêm 1 tin
                # "quá cũ" khác giọng cho đúng cùng sự việc khi nó vượt 4h sau đó (N2).
                rec["stale_notified"] = True
                hist[jid] = rec
                if not write_state(state):
                    log("STATE-UNWRITABLE (escalate) — DỪNG báo 'bỏ cuộc' (không có dedupe "
                        "thì không được báo lặp)")
                    notify("🛑 **wakeup-reconciler tự dừng (nhánh bỏ cuộc)** — không ghi được "
                           "`%s` nên KHÔNG còn trần chống báo-lặp; dừng báo job bỏ cuộc tới "
                           "khi ghi được. Kiểm tra dung lượng/quyền của `mike/state/`."
                           % STATE_FILE)
                    break
                # Phân biệt "đã THỬ" với "push THẬT ra được": `n` đếm cả lượt wake_thread.sh
                # rc≠0 (cố ý — lượt hỏng vẫn tiêu trần). Nếu ccdb sập 45' thì cả 3 lượt đều
                # chết, mà tin lại nói "đã được đánh thức 3 lần" ⇒ người trực đi tìm sai
                # hướng, đúng kiểu nhãn "409 Task name already exists" đã lừa 3 lần trong
                # chính sự cố này (§28: báo GIÁ TRỊ đo được, đừng suy từ nhãn).
                _push = ("push ra được %d/%d lượt" % (_ok, _n) if _ok
                         else "**KHÔNG lượt push nào ra được** (%d/%d hỏng — nghi ccdb/API "
                              "chứ không phải phiên Mike; xem logs/wake_thread_errors.log)"
                              % (_n, _n))
                notify("🛑 **wakeup-reconciler bỏ cuộc** — job `%s` (%s, status=%s): đã "
                       "THỬ đánh thức %d lần (%s) mà vẫn KHÔNG ai `claim-reply`. Thread "
                       "`%s` có thể đã chết/archive, hoặc kết quả cần post tay. "
                       "Reconciler DỪNG cứu job này; xem `bin/jobs.sh status %s`."
                       % (jid, job["to"], job["status"], _n, _push, tid, jid))
            continue
        if rec and now - int(rec.get("last", 0)) < REFIRE_COOLDOWN:
            continue
        if n_fired >= MAX_WAKES_PER_CYCLE:
            log("CYCLE-CAP đạt %d wake/chu kỳ, hoãn %d job còn lại sang chu kỳ sau"
                % (MAX_WAKES_PER_CYCLE, len(cand) - cand.index(job)))
            break
        # Ghi TRƯỚC khi gọi (§5): chết giữa chừng thì mất một lượt cứu — chấp nhận được;
        # mất TRẦN rồi bắn vô hạn thì không. Và nếu KHÔNG ghi được thì KHÔNG ĐƯỢC BẮN: trần
        # sống trong file này, ghi hỏng = không còn trần, mà "không còn trần" chính là lỗi
        # BLOCKER ta vừa đi vá. Dừng cả vòng + gọi người đúng 1 lần.
        rec = {"n": int(rec.get("n", 0)) + 1, "ok": int(rec.get("ok", 0)),
               "last": now, "escalated": False}
        hist[jid] = rec
        if not write_state(state):
            log("STATE-UNWRITABLE — DỪNG bắn wake (không có trần thì không được bắn)")
            notify("🛑 **wakeup-reconciler tự dừng** — không ghi được `%s` nên KHÔNG còn "
                   "trần chống bắn-lặp; reconciler ngừng đánh thức cho tới khi ghi được. "
                   "Kiểm tra dung lượng/quyền của `mike/state/`. Job đang chờ cứu: `%s`."
                   % (STATE_FILE, jid))
            break
        if fire_wake(job, rec["n"]):
            rec["ok"] = int(rec.get("ok", 0)) + 1
            write_state(state)
            fired_threads.add(tid)
            n_fired += 1
    write_state(state)
    # Dấu thời gian ICT trên CẢ dòng OK: `daily_retro.sh` đếm số chu kỳ ĐÃ CHẠY trong ngày
    # từ chính dòng này (arch-reviewer N2, vòng 4). Không có nó thì "reconciler chạy sạch cả
    # ngày" và "cron bị gỡ, không chạy lần nào" cho ra CÙNG một báo cáo `rescued=0` — đúng
    # anti-pattern "im lặng = khoẻ" mà cả bản redesign này sinh ra để diệt.
    print("OK %s candidates=%d fired=%d capped=%d stale=%d unreadable=%d errlog_new=%d"
          % (_ict(), len(cand), n_fired, n_capped, n_stale_notified, n_unreadable, n_err))
    if n_unreadable:
        # `log()` (logs/wakeup_reconcile.log) không có checker nào đọc — cron_health_check.py
        # chỉ quét logs/wakeup_reconcile_cron.log (= stdout của chính tiến trình này). In
        # CRITICAL ra STDOUT thì regex thật của nó (ERROR_PATTERNS: r"CRITICAL", substring)
        # bắt được cùng ngày, thay vì tín hiệu chỉ tồn tại trong 1 file không ai quét
        # (arch-reviewer N4, re-audit trước-commit 08-20 — đo trực tiếp bằng ERROR_RE thật).
        print("CRITICAL %s %d job record không đọc được (JOB-UNREADABLE) — xem "
              "logs/wakeup_reconcile.log để biết file nào." % (_ict(), n_unreadable))
    return 0


if __name__ == "__main__":
    sys.exit(main())
