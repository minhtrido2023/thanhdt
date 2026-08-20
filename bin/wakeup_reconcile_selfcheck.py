#!/usr/bin/env python3
"""wakeup_reconcile_selfcheck.py — bộ hồi quy GIẢ LẬP HOÀN TOÀN cho bin/wakeup_reconcile.py.

KHÔNG chạm tasks.db thật, KHÔNG gọi /api/sessions thật, KHÔNG gọi wake_thread.sh thật:
mỗi ca dựng một sandbox riêng (job board fixture + sqlite fixture + HTTP server localhost
trả JSON fixture + stub bash ghi lại lời gọi) rồi chạy CHÍNH `wakeup_reconcile.py` như một
tiến trình con, với mọi đường dẫn/URL trỏ vào sandbox qua biến môi trường. Nhờ vậy nó test
đúng code production (kể cả flock, exit code, subprocess argv), không copy lại logic.

Ca gốc lấy từ sự cố thật: kb/incidents/2026-08/2026-08-20-wake-push-utf8-surrogate-deletes-ladder.md

Usage: python3 bin/wakeup_reconcile_selfcheck.py     (exit 0 = PASS)
       env -u TZ python3 bin/wakeup_reconcile_selfcheck.py            (§16)
       TZ=Pacific/Kiritimati python3 bin/wakeup_reconcile_selfcheck.py
"""
import http.server
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "bin", "wakeup_reconcile.py")

# Schema thật của ccdb (đọc từ /workspace/ccdb-mike/data/tasks.db ngày 2026-08-20). Chép
# vào đây có chủ đích: fixture phải hermetic, không được đọc DB sống của service khác.
TASKS_SCHEMA = """
CREATE TABLE scheduled_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    prompt TEXT NOT NULL,
    interval_seconds INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    working_dir TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    next_run_at REAL NOT NULL,
    last_run_at REAL,
    created_at REAL NOT NULL,
    anchor_hour INTEGER,
    anchor_minute INTEGER DEFAULT 0,
    thread_id INTEGER,
    one_shot INTEGER DEFAULT 0,
    executed_at REAL
)
"""

# Đọc TRẦN từ chính module production — chép số vào đây thì đổi hằng số là test tự mốc.
_spec = importlib.util.spec_from_file_location("wakeup_reconcile", SCRIPT)
_wr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_wr)
MAXFIRE, REFIRE, MAXCYCLE = (_wr.MAX_FIRES_PER_JOB, _wr.REFIRE_COOLDOWN,
                             _wr.MAX_WAKES_PER_CYCLE)

# Số hư cấu (KHÔNG phải Discord ID thật — bin/discord_id_gate.sh chặn cứng mọi snowflake
# trần bắt đầu bằng "1" dài 18-19 chữ số ngoài kb/discord_channels.json; đổi tiền tố "1"->"2"
# để test fixture khỏi bị hiểu nhầm là ID thật, dù đây chỉ là sandbox hermetic không đụng
# Discord thật — KHÔNG dùng "9": sqlite INTEGER là int64 có dấu, trần ~9.22e18, số 19 chữ số
# bắt đầu bằng 9 tràn số). Cùng chữ số với thread "Maintenance"/"Architecture" của sự cố
# 08-20 để dễ nhận diện khi đọc log test, không phải ID sống.
THREAD_A = "2539659365324169287"
THREAD_B = "2521475726329516122"

FAILS = []
CASES = [0]


def check(name, got, want):
    CASES[0] += 1
    if got == want:
        print("    ok   %-58s = %r" % (name, got))
    else:
        print("    FAIL %s: thực=%r ≠ mong đợi=%r" % (name, got, want))
        FAILS.append(name)


class _Sessions(http.server.BaseHTTPRequestHandler):
    payload = b'{"sessions": []}'
    fail = False

    def do_GET(self):
        if _Sessions.fail:
            self.send_error(500, "ccdb down")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(_Sessions.payload)))
        self.end_headers()
        self.wfile.write(_Sessions.payload)

    def log_message(self, *a):
        pass


class Sandbox:
    def __init__(self, sessions=(), tasks=(), corrupt_db=False, api_down=False,
                 wake_persist=False, notify_fail=False):
        self.wake_persist = wake_persist
        self.notify_fail = notify_fail
        self.dir = tempfile.mkdtemp(prefix="wakerec_")
        self.jobs = os.path.join(self.dir, "jobs")
        os.makedirs(self.jobs)
        self.batches = os.path.join(self.dir, "batches")
        os.makedirs(self.batches)
        self.calls = os.path.join(self.dir, "wake.calls")
        self.notify_calls = os.path.join(self.dir, "notify.calls")
        self.db = os.path.join(self.dir, "tasks.db")
        self.errlog = os.path.join(self.dir, "wake_thread_errors.log")
        self.state = os.path.join(self.dir, "state.json")
        self._make_db(tasks, corrupt_db)
        self._make_stubs()
        _Sessions.payload = json.dumps({"sessions": list(sessions)}).encode()
        _Sessions.fail = api_down

    def _make_db(self, tasks, corrupt):
        if corrupt:
            with open(self.db, "wb") as f:
                f.write(b"this is not a sqlite database at all\n" * 20)
            return
        con = sqlite3.connect(self.db)
        con.execute(TASKS_SCHEMA)
        for i, (name, tid, one_shot, executed) in enumerate(tasks):
            con.execute(
                "INSERT INTO scheduled_tasks (name, prompt, interval_seconds, channel_id, "
                "enabled, next_run_at, created_at, thread_id, one_shot, executed_at) "
                "VALUES (?,?,?,?,1,?,?,?,?,?)",
                (name, "p", 60, int(tid), time.time(), time.time(), int(tid), one_shot, executed))
        con.commit()
        con.close()

    def _make_stubs(self):
        # wake_thread.sh giả — ghi lại argv, và MÔ PHỎNG ĐÚNG vòng đời row của ccdb.
        #
        # ⚠️ Bản đầu của file này INSERT row pending rồi ĐỂ NGUYÊN MÃI MÃI, nên ca "chạy 2
        # lần liên tiếp" PASS một cách giả tạo và che mất bug bắn-lặp-vô-hạn (arch-reviewer
        # bắt được, 2026-08-20). Sự thật đọc từ code ccdb (`SchedulerCog._claim_one_shot`,
        # claude-code-discord-bridge): one-shot bị `mark_executed` rồi `delete` **TRƯỚC KHI**
        # Claude chạy (guard F1/F3 chống replay khi daemon restart) ⇒ row chỉ sống ~≤30s.
        # `wake_persist` mô phỏng 2 thế giới:
        #   True  = ccdb vừa tạo row, scheduler CHƯA kịp nhặt (cửa sổ ≤30s)
        #   False = MẶC ĐỊNH, đúng thực tế sau ~30s: row đã bị xoá, không còn "bảo hiểm" nào
        self.wake_sh = os.path.join(self.dir, "wake_thread.sh")
        _sql = ("con.execute('INSERT INTO scheduled_tasks (name,prompt,interval_seconds,"
                "channel_id,enabled,next_run_at,created_at,thread_id,one_shot,executed_at) "
                "VALUES (?,?,?,?,1,?,?,?,1,NULL)', ('dispatch-wake-'+sys.argv[2], 'p', 60, "
                "int(sys.argv[1]), time.time(), time.time(), int(sys.argv[1])))")
        if not self.wake_persist:
            _sql += ("\ncon.execute('DELETE FROM scheduled_tasks WHERE name = ?', "
                     "('dispatch-wake-'+sys.argv[2],))")
        wake_body = "\n".join([
            "#!/usr/bin/env bash",
            'printf "%s\\t%s\\t%s\\n" "$1" "$2" "${3:-}" >> ' + self.calls,
            "test -n \"${WAKE_STUB_FAIL:-}\" && exit 1",
            'python3 - "$1" "$3" <<PY',
            "import sqlite3, sys, time",
            "con = sqlite3.connect(" + repr(self.db) + ")",
            _sql,
            "con.commit()",
            "PY",
            "",
        ])
        with open(self.wake_sh, "w") as f:
            f.write(wake_body)
        os.chmod(self.wake_sh, 0o755)
        self.notify_sh = os.path.join(self.dir, "notify_thread.sh")
        # Tin nhắn notify là NHIỀU DÒNG (có khối ```), nên stub phải ép về 1 dòng/lời gọi
        # — nếu không, đếm dòng file này = đếm dòng tin nhắn chứ không phải số lời gọi.
        with open(self.notify_sh, "w") as f:
            f.write("#!/usr/bin/env bash\n"
                    'printf "%s\\t%s\\n" "$2" "$(printf "%s" "$1" | tr "\\n" " ")" >> '
                    + self.notify_calls + "\n"
                    + ("exit 1\n" if self.notify_fail else ""))
        os.chmod(self.notify_sh, 0o755)

    def job(self, job_id, **kw):
        # `pid` = dấu hiệu job chạy NỀN (chỉ _bg_wrapper của dispatch.sh ghi field này).
        # Job dispatch ĐỒNG BỘ không có field này và cố ý nằm ngoài phạm vi reconciler.
        rec = {"job_id": job_id, "from": "Mike", "to": "Taylor", "status": "done",
               "pid": "12345",
               "discord_thread_id": THREAD_A, "ended_at": str(int(time.time()) - 600)}
        rec.update(kw)
        rec = {k: v for k, v in rec.items() if v is not None}
        with open(os.path.join(self.jobs, job_id + ".json"), "w") as f:
            json.dump(rec, f)

    def batch(self, batch_id, members, expected=0, claimed=""):
        """Dựng thẳng bus/batches/<id>.json — đợt fan-out của dispatch.sh --batch-id."""
        with open(os.path.join(self.batches, batch_id + ".json"), "w") as f:
            json.dump({"batch_id": batch_id, "created_at": int(time.time()) - 60,
                       "expected": expected or len(members), "members": list(members),
                       "wake_claimed_by": claimed}, f)

    def run(self, min_ts=0):
        env = dict(os.environ)
        env.update({
            "WAKEUP_RECONCILE_JOBS_DIR": self.jobs,
            "WAKEUP_RECONCILE_TASKS_DB": self.db,
            "WAKEUP_RECONCILE_SESSIONS_API": API_URL,
            "WAKEUP_RECONCILE_WAKE_SH": self.wake_sh,
            "WAKEUP_RECONCILE_NOTIFY_SH": self.notify_sh,
            "WAKEUP_RECONCILE_ERR_LOG": self.errlog,
            "WAKEUP_RECONCILE_LOG": os.path.join(self.dir, "reconcile.log"),
            "WAKEUP_RECONCILE_STATE": self.state,
            "WAKEUP_RECONCILE_LOCK": os.path.join(self.dir, "lock"),
            "WAKEUP_RECONCILE_BATCHES_DIR": self.batches,
            "WAKEUP_RECONCILE_MIN_TS": str(min_ts),
        })
        r = subprocess.run([sys.executable, SCRIPT], env=env, capture_output=True,
                           text=True, timeout=60)
        return r.returncode

    def lock_state_dir(self):
        """chmod 500 thư mục chứa state file ⇒ os.replace() ném exception. Mô phỏng
        ENOSPC/lệch quyền trên mike/state/ — ca mà arch-reviewer đo được là làm trần
        bốc hơi im lặng."""
        self._state_dir = os.path.join(self.dir, "statedir")
        os.makedirs(self._state_dir, exist_ok=True)
        self.state = os.path.join(self._state_dir, "state.json")
        os.chmod(self._state_dir, 0o500)

    def unlock_state_dir(self):
        os.chmod(self._state_dir, 0o700)

    def break_db(self):
        """Ghi đè tasks.db bằng rác ⇒ sqlite mở được file nhưng đọc bảng thì ném. Mô phỏng
        ccdb đổi deploy path / lệch quyền / DB hỏng — ca mà reconciler phải abort."""
        with open(self.db, "wb") as f:
            f.write(b"this is not a sqlite database at all\n" * 20)

    def repair_db(self):
        """ccdb sống lại: dựng lại schema rỗng (không task pending nào)."""
        os.remove(self.db)
        self._make_db((), False)

    def notify_fail_on(self):
        with open(self.notify_sh, "a") as f:
            f.write("exit 1\n")

    def notify_fail_off(self):
        lines = [ln for ln in open(self.notify_sh).read().splitlines() if ln != "exit 1"]
        with open(self.notify_sh, "w") as f:
            f.write("\n".join(lines) + "\n")

    def age_state(self, seconds):
        """Tua ngược mốc `last` của mọi job đã cứu — giả lập đã qua cooldown, để test
        được trần MAX_FIRES_PER_JOB mà không phải sleep 15 phút thật."""
        with open(self.state, encoding="utf-8") as f:
            st = json.load(f)
        for rec in (st.get("fired") or {}).values():
            rec["last"] = int(rec.get("last", 0)) - seconds
        with open(self.state, "w", encoding="utf-8") as f:
            json.dump(st, f)

    def state_json(self):
        with open(self.state, encoding="utf-8") as f:
            return json.load(f)

    def wakes(self):
        if not os.path.exists(self.calls):
            return []
        with open(self.calls) as f:
            return [ln.rstrip("\n").split("\t") for ln in f if ln.strip()]

    def notifies(self):
        if not os.path.exists(self.notify_calls):
            return []
        with open(self.notify_calls) as f:
            return [ln.rstrip("\n").split("\t", 1) for ln in f if ln.strip()]

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def sess(tid, state="idle"):
    return {"thread_id": int(tid), "state": state}


def main():
    print("== CA a: surrogate-kill 08-20 — job done, ccdb đã XOÁ ladder rồi INSERT chết, "
          "session idle ⇒ phải cứu")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_015520")
    rc = sb.run()
    w = sb.wakes()
    check("exit code", rc, 0)
    check("số lần wake", len(w), 1)
    check("wake đúng thread", w[0][0] if w else "", THREAD_A)
    check("prompt mở đầu bằng claim-reply đúng job",
          bool(w) and w[0][1].split("[WAKEUP")[0].count(
              "jobs.sh claim-reply Taylor_20260820_015520") == 1, True)
    check("prompt KHÔNG nhúng preview log (Phase 2)",
          bool(w) and "tail -c" not in w[0][1] and "status=done" in w[0][1], True)
    # Hậu tố mang SỐ LẦN BẮN (arch-reviewer #3, 2026-08-20): cột `name` của scheduled_tasks
    # là UNIQUE, tên cố định ⇒ một row tồn đọng làm lượt cứu #2/#3 nhận 409 và tiêu trần mà
    # không đánh thức được ai. Tính phân biệt của chuỗi này được khoá riêng ở CA n.
    check("name_suffix có hậu tố -reconcile<lần bắn>", w[0][2] if w else "",
          "Taylor_20260820_015520-reconcile1")
    sb.close()

    print("== CA b: Mike QUÊN đặt ladder — không có one-shot nào của thread này, không có "
          "session nào ⇒ phải cứu")
    sb = Sandbox(sessions=[sess(THREAD_B, "running")],
                 tasks=[("wakeup-thread-" + THREAD_B, THREAD_B, 1, None)])
    sb.job("Winston_20260820_020453")
    rc = sb.run()
    check("exit code", rc, 0)
    check("số lần wake", len(sb.wakes()), 1)
    check("one-shot của thread KHÁC không được tính là bảo hiểm",
          sb.wakes()[0][0] if sb.wakes() else "", THREAD_A)
    sb.close()

    print("== CA c: session của thread ĐANG running ⇒ KHÔNG bắn")
    sb = Sandbox(sessions=[sess(THREAD_A, "running")], tasks=[])
    sb.job("Taylor_20260820_015520")
    check("exit code", sb.run(), 0)
    check("số lần wake", len(sb.wakes()), 0)
    sb.close()

    print("== CA c2: thread đã có one-shot pending (ladder còn sống) ⇒ KHÔNG bắn")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")],
                 tasks=[("wakeup-thread-" + THREAD_A, THREAD_A, 1, None)])
    sb.job("Taylor_20260820_015520")
    check("exit code", sb.run(), 0)
    check("số lần wake", len(sb.wakes()), 0)
    sb.close()

    print("== CA c3: one-shot của thread ĐÃ CHẠY (executed_at) ⇒ không còn là bảo hiểm, phải cứu")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")],
                 tasks=[("wakeup-thread-" + THREAD_A, THREAD_A, 1, time.time())])
    sb.job("Taylor_20260820_015520")
    check("exit code", sb.run(), 0)
    check("số lần wake", len(sb.wakes()), 1)
    sb.close()

    print("== CA d: job ĐÃ replied ⇒ KHÔNG bắn")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_015520", replied_at="2026-08-20T04:01:17Z")
    check("exit code", sb.run(), 0)
    check("số lần wake", len(sb.wakes()), 0)
    sb.close()

    print("== CA e: tasks.db HỎNG ⇒ KHÔNG bắn + exit khác 0 (fail-safe, không đoán 'rỗng')")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[], corrupt_db=True)
    sb.job("Taylor_20260820_015520")
    check("exit code = 2", sb.run(), 2)
    check("số lần wake", len(sb.wakes()), 0)
    sb.close()

    print("== CA e2: /api/sessions chết ⇒ KHÔNG bắn + exit 3")
    sb = Sandbox(sessions=[], tasks=[], api_down=True)
    sb.job("Taylor_20260820_015520")
    check("exit code = 3", sb.run(), 3)
    check("số lần wake", len(sb.wakes()), 0)
    sb.close()
    _Sessions.fail = False

    print("== CA f: chạy 2 lần liên tiếp ⇒ lần 2 KHÔNG bắn lại (cooldown giữ, DÙ ccdb đã "
          "xoá row one-shot trước khi Claude chạy)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_015520")
    sb.run()
    n1 = len(sb.wakes())
    sb.run()
    n2 = len(sb.wakes())
    check("lần 1 bắn 1", n1, 1)
    check("tổng sau lần 2 vẫn là 1", n2, 1)
    check("state ghi bền số lần đã cứu",
          sb.state_json().get("fired", {}).get("Taylor_20260820_015520", {}).get("n"), 1)
    sb.close()

    print("== CA f2: cửa sổ ≤30s — ccdb vừa tạo row, scheduler chưa nhặt ⇒ lần 2 vẫn KHÔNG bắn")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[], wake_persist=True)
    sb.job("Taylor_20260820_015520")
    sb.run()
    sb.age_state(REFIRE + 60)   # qua cooldown rồi, chỉ còn row pending là lý do dừng
    sb.run()
    check("tổng số wake", len(sb.wakes()), 1)
    sb.close()

    print("== CA f3: BLOCKER — phiên được đánh thức KHÔNG claim, nhiều chu kỳ liên tiếp ⇒ "
          "TỔNG wake ≤ MAX_FIRES_PER_JOB rồi DỪNG HẲN + đúng 1 lần escalate")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_015520")
    for _ in range(8):          # 8 chu kỳ, mỗi chu kỳ đã qua cooldown
        sb.run()
        sb.age_state(REFIRE + 60)
    check("tổng số wake = trần MAX_FIRES_PER_JOB", len(sb.wakes()), MAXFIRE)
    esc = [n for n in sb.notifies() if "bỏ cuộc" in n[1]]
    check("escalate ĐÚNG 1 lần (không spam mỗi 5')", len(esc), 1)
    check("escalate vào trading_daily", esc[0][0] if esc else "", "trading_daily")
    check("escalate nêu đúng job_id",
          "Taylor_20260820_015520" in esc[0][1] if esc else False, True)
    sb.close()

    print("== CA f4: escalate mà notify HỎNG (Discord/ccdb tạch, KHÔNG PHẢI state hỏng) ⇒ ghi "
          "TRƯỚC vẫn đánh dấu escalated=True (đổi 2026-08-20, arch-reviewer vòng 3: notify-"
          "trước-ghi-sau khiến 'n' đã persist=3 từ sớm làm điều kiện MAX_FIRES đúng MỖI chu "
          "kỳ bất kể chu kỳ đó ghi được hay không ⇒ spam 'bỏ cuộc' khi STATE hỏng — case đó "
          "giờ khoá ở CA u dưới. Cái giá đổi lại, đo ở đây: 1 lần Discord tạch thoáng qua "
          "(ccdb/API sống, chỉ notify_thread.sh lỗi) làm MẤT VĨNH VIỄN đúng 1 tin — chấp "
          "nhận được, cùng tiền lệ với `n`/too_old, ĐÃ ghi rõ trong comment tại chỗ)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[], notify_fail=True)
    sb.job("Taylor_20260820_015520")
    for _ in range(MAXFIRE + 3):
        sb.run()
        sb.age_state(REFIRE + 60)
    check("cờ escalated VẪN bật dù notify_thread.sh lỗi (state ghi được)",
          sb.state_json().get("fired", {}).get("Taylor_20260820_015520", {}).get("escalated"),
          True)
    check("CHỈ thử báo 'bỏ cuộc' ĐÚNG 1 lần (không lặp lại vô ích vì đã persist escalated)",
          len([n for n in sb.notifies() if "bỏ cuộc" in n[1] and "tự dừng" not in n[1]]), 1)
    sb.close()

    print("== CA u: n ĐÃ persist=MAXFIRE (từ lúc state còn sống), rồi STATE mới hỏng — đây ĐÚNG "
          "kịch bản arch-reviewer vòng 3 chỉ đích danh killer (khác CA f4: đó là Discord/notify "
          "tạch trong khi state vẫn ghi được). PHẢI dừng như too_old, 0 lần 'bỏ cuộc' lặp lại — "
          "trước vá này đo được 5/5 chu kỳ gửi lại đúng tin sai chẩn đoán")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_state_hong_escalate")
    for _ in range(MAXFIRE):  # n: 0->1->2->3, escalate CHƯA kích hoạt (check n>=3 ở đầu chu kỳ)
        sb.run()
        sb.age_state(REFIRE + 60)
    check("n đã persist đúng MAXFIRE trước khi state hỏng",
          sb.state_json().get("fired", {}).get("Taylor_state_hong_escalate", {}).get("n"), MAXFIRE)
    # `lock_state_dir()` chuyển sang MỘT ĐƯỜNG DẪN MỚI trống rỗng (mất luôn n=3 vừa persist) —
    # dùng đúng cho CA f8/q (hỏng NGAY TỪ ĐẦU) nhưng SAI cho ca này (cần giữ nguyên state đã
    # có rồi mới khoá). Tự chép nội dung state hiện tại sang thư mục chỉ-đọc mới.
    _locked_dir = os.path.join(sb.dir, "statedir_u")
    os.makedirs(_locked_dir, exist_ok=True)
    shutil.copy(sb.state, os.path.join(_locked_dir, "state.json"))
    sb.state = os.path.join(_locked_dir, "state.json")
    os.chmod(_locked_dir, 0o500)
    for _ in range(4):  # MỖI chu kỳ này mới thấy n>=MAXFIRE (đọc từ state đã persist trước đó)
        sb.run()
        sb.age_state(REFIRE + 60)
    os.chmod(_locked_dir, 0o700)
    # "tự dừng (nhánh bỏ cuộc)" CŨNG chứa substring "bỏ cuộc" — phải loại trừ tường minh,
    # đừng để việc đếm nhầm 2 loại tin khác nhau che mất đúng bug đang test.
    check("0 tin 'bỏ cuộc' khi escalate lần đầu rơi đúng lúc state hỏng (không phải 4)",
          len([n for n in sb.notifies() if "bỏ cuộc" in n[1] and "tự dừng" not in n[1]]), 0)
    check("có tin 'tự dừng (nhánh bỏ cuộc)' báo đúng lý do",
          any("tự dừng (nhánh bỏ cuộc)" in m for _, m in sb.notifies()), True)
    sb.close()

    print("== CA f5: wake_thread.sh THẤT BẠI ⇒ vẫn tính vào trần (không thử vô hạn)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_015520")
    os.environ["WAKE_STUB_FAIL"] = "1"
    try:
        for _ in range(6):
            sb.run()
            sb.age_state(REFIRE + 60)
    finally:
        os.environ.pop("WAKE_STUB_FAIL", None)
    check("số lần THỬ = trần, không hơn", len(sb.wakes()), MAXFIRE)
    sb.close()

    print("== CA f6: MAX_WAKES_PER_CYCLE — 6 thread cùng mất tín hiệu ⇒ 1 chu kỳ bắn tối đa 3")
    threads = [str(2539000000000000000 + i) for i in range(6)]  # số hư cấu, xem THREAD_A ở trên
    sb = Sandbox(sessions=[], tasks=[])
    for i, t in enumerate(threads):
        sb.job("job_%d" % i, discord_thread_id=t,
               ended_at=str(int(time.time()) - 600 - i))
    check("exit code", sb.run(), 0)
    check("số lần wake trong 1 chu kỳ", len(sb.wakes()), MAXCYCLE)
    sb.close()

    print("== CA f7: job dispatch ĐỒNG BỘ (không có field pid) ⇒ ngoài phạm vi, KHÔNG bắn")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Wags_20260820_012007", pid=None)
    check("exit code", sb.run(), 0)
    check("số lần wake", len(sb.wakes()), 0)
    sb.close()

    print("== CA f8: state file KHÔNG GHI ĐƯỢC ⇒ KHÔNG bắn (không có trần thì không bắn) "
          "+ báo người, và KHÔNG lặp lại mỗi chu kỳ")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_015520")
    sb.lock_state_dir()
    try:
        for _ in range(5):
            sb.run()
    finally:
        sb.unlock_state_dir()
    check("số lần wake khi không ghi được state", len(sb.wakes()), 0)
    check("có báo người là đã tự dừng",
          len([n for n in sb.notifies() if "tự dừng" in n[1]]) >= 1, True)
    sb.close()

    print("== CA f9: escalate phải phân biệt 'đã THỬ' với 'push THẬT ra được' "
          "(ccdb sập ⇒ 3 lượt đều chết)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_015520")
    os.environ["WAKE_STUB_FAIL"] = "1"
    try:
        for _ in range(MAXFIRE + 2):
            sb.run()
            sb.age_state(REFIRE + 60)
    finally:
        os.environ.pop("WAKE_STUB_FAIL", None)
    esc = [n for n in sb.notifies() if "bỏ cuộc" in n[1]]
    check("có escalate", len(esc) >= 1, True)
    check("tin nói RÕ không lượt push nào ra được",
          "KHÔNG lượt push nào ra được" in esc[0][1] if esc else False, True)
    check("KHÔNG khẳng định 'đã được đánh thức N lần'",
          "được đánh thức" not in esc[0][1] if esc else False, True)
    check("rec['ok'] = 0 khi mọi lượt push đều hỏng",
          sb.state_json().get("fired", {}).get("Taylor_20260820_015520", {}).get("ok"), 0)
    sb.close()

    print("== CA f10: log lỗi XOAY VÒNG đúng lúc notify hỏng ⇒ KHÔNG được nhảy qua dòng đầu "
          "của file mới (thà báo trùng còn hơn báo thiếu)")
    sb = Sandbox(sessions=[sess(THREAD_A, "running")], tasks=[])
    with open(sb.errlog, "w") as f:
        for i in range(20):
            f.write("2026-08-20T10:%02d:00+07:00 wake_thread: HTTP 409 | cu-%d\n" % (i, i))
    sb.run()                                   # notify OK ⇒ offset tiến tới cuối file cũ
    check("chu kỳ 1 báo 20 dòng cũ", len(sb.notifies()), 1)
    sb.notify_fail_on()                        # ccdb sập
    # XOAY VÒNG THẬT: đổi tên file cũ rồi tạo file MỚI ⇒ inode đổi. (Đường xoay vòng khác
    # của fleet — fleet_housekeeping.sh dùng `cp + truncate`, giữ nguyên inode — được phủ
    # ở CA f11 bên dưới.)
    os.rename(sb.errlog, sb.errlog + ".1")
    with open(sb.errlog, "w") as f:
        for i in range(30):
            f.write("2026-08-20T11:%02d:00+07:00 wake_thread: HTTP 409 | moi-%d\n" % (i, i))
    sb.run()
    sb.notify_fail_off()                       # ccdb sống lại
    sb.run()
    _n = sb.notifies()
    last = _n[-1][1] if _n else ""   # đừng để IndexError nuốt mất các ca phía sau
    check("chu kỳ cuối báo ĐỦ 30 dòng file mới, không nhảy qua 10 dòng đầu",
          "30 dòng mới" in last, True)
    # ⚠️ Assertion `notifies()[-1]` ở trên MỘT MÌNH là ca PASS-BẤT-KỂ (arch-reviewer #2,
    # vòng 3 — đo thật: mutation "tiến errlog_offset+inode DÙ notify() trả False" vẫn PASS
    # 58/58). Lý do: stub notify ghi dòng vào notify.calls RỒI MỚI `exit 1`, nên lượt gửi
    # HỎNG vẫn nằm trong notifies() và phần tử [-1] khớp ở cả hai phía. Số ĐẾM thì không:
    #   code đúng   = 3 lời gọi (20 dòng OK | 30 dòng FAIL | 30 dòng gửi LẠI OK)
    #   code mutate = 2 lời gọi (offset đã tiến ⇒ chu kỳ 3 không thấy dòng mới nào)
    # Đây chính là bất biến "thà báo trùng còn hơn báo thiếu" — phải khoá bằng số đếm.
    check("báo LẠI được sau khi ccdb sống lại (3 lời gọi, không nuốt mất 30 dòng)",
          len(sb.notifies()), 3)
    sb.close()

    print("== CA f11: xoay vòng kiểu `cp + truncate` (fleet_housekeeping.sh — GIỮ inode, "
          "size về 0) ⇒ đọc lại từ đầu, không seek quá đuôi")
    sb = Sandbox(sessions=[sess(THREAD_A, "running")], tasks=[])
    with open(sb.errlog, "w") as f:
        for i in range(20):
            f.write("2026-08-20T10:%02d:00+07:00 wake_thread: HTTP 409 | cu-%d\n" % (i, i))
    sb.run()
    with open(sb.errlog, "w"):                 # truncate tại chỗ, inode KHÔNG đổi
        pass
    with open(sb.errlog, "a") as f:
        for i in range(4):
            f.write("2026-08-20T12:%02d:00+07:00 wake_thread: HTTP 409 | sau-%d\n" % (i, i))
    sb.run()
    _n = sb.notifies()
    last = _n[-1][1] if _n else ""   # guard: mutation làm mất notify không được crash cả bộ
    check("báo đúng 4 dòng sau khi truncate (không im lặng bỏ qua)",
          "4 dòng mới" in last, True)
    sb.close()

    print("== CA g: 2 job chưa reply CÙNG 1 thread ⇒ chỉ 1 wake/chu kỳ (ccdb xoá task cũ "
          "khi tạo task mới)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_015520", ended_at=str(int(time.time()) - 900))
    sb.job("Winston_20260820_020453", ended_at=str(int(time.time()) - 600))
    check("exit code", sb.run(), 0)
    check("số lần wake", len(sb.wakes()), 1)
    check("cứu job chờ LÂU NHẤT trước",
          "Taylor_20260820_015520" in sb.wakes()[0][1] if sb.wakes() else False, True)
    sb.close()

    print("== CA h: các dạng job KHÔNG thuộc phạm vi ⇒ KHÔNG bắn")
    now = int(time.time())
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("j_running", status="running")
    sb.job("j_retrying", status="retrying")
    sb.job("j_not_mike", **{"from": "Taylor"})
    sb.job("j_no_thread", discord_thread_id=None)
    sb.job("j_in_grace", ended_at=str(now - 60))          # < GRACE 180s
    sb.job("j_no_ended", ended_at=None)
    sb.job("j_too_old", ended_at=str(now - 49 * 3600))    # ngoài look-back 48h
    check("exit code", sb.run(), 0)
    check("số lần wake", len(sb.wakes()), 0)
    sb.close()

    print("== CA i: mốc hiệu lực MIN_TS — job terminal CŨ (trước deploy) KHÔNG bị bắn hàng loạt")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("j_old_1", ended_at=str(now - 3600))
    sb.job("j_old_2", ended_at=str(now - 7200), discord_thread_id=THREAD_B)
    check("exit code", sb.run(min_ts=now - 600), 0)
    check("số lần wake", len(sb.wakes()), 0)
    sb.close()

    print("== CA j: giám sát wake_thread_errors.log — dòng mới ⇒ notify đúng 1 lần vào "
          "trading_daily; chạy lại KHÔNG báo lại")
    sb = Sandbox(sessions=[sess(THREAD_A, "running")], tasks=[])
    with open(sb.errlog, "w") as f:
        f.write("2026-08-20T10:44:54 wake_thread: HTTP 409 | thread_id=%s\n" % THREAD_A)
    sb.run()
    n = sb.notifies()
    check("notify 1 lần", len(n), 1)
    check("notify đúng topic (TÊN, không phải ID trần)", n[0][0] if n else "", "trading_daily")
    check("notify trích nội dung dòng lỗi", "HTTP 409" in n[0][1] if n else False, True)
    sb.run()
    check("chạy lại không báo lại dòng cũ", len(sb.notifies()), 1)
    with open(sb.errlog, "a") as f:
        f.write("2026-08-20T10:50:00 wake_thread: unreachable | thread_id=%s\n" % THREAD_A)
    sb.run()
    check("dòng lỗi MỚI thì báo tiếp", len(sb.notifies()), 2)
    sb.close()

    print("== CA k: KHÔNG có lỗi nào (file log không tồn tại) ⇒ im lặng, không notify")
    sb = Sandbox(sessions=[sess(THREAD_A, "running")], tasks=[])
    sb.run()
    check("notify 0 lần", len(sb.notifies()), 0)
    sb.close()

    print("== CA m: abort LIÊN TIẾP ⇒ gọi người đúng 1 lần (arch-reviewer BLOCKER-1: nhánh "
          "fail-safe không được im lặng vĩnh viễn), và reset khi ccdb sống lại")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_020000")
    sb.break_db()
    rc1 = sb.run()
    check("chu kỳ mù 1: exit 2", rc1, 2)
    check("chu kỳ mù 1: CHƯA gọi người (1 lần restart ccdb không đáng kêu)",
          len(sb.notifies()), 0)
    sb.run()
    check("chu kỳ mù 2: vẫn chưa gọi người", len(sb.notifies()), 0)
    sb.run()
    n = sb.notifies()
    check("chu kỳ mù 3 (=15' mù): gọi người ĐÚNG 1 lần", len(n), 1)
    check("gọi đúng topic theo TÊN", n[0][0] if n else "", "trading_daily")
    check("tin nói rõ đang mù mấy chu kỳ", "3 chu kỳ liên tiếp" in n[0][1] if n else False, True)
    sb.run()
    check("chu kỳ mù 4: KHÔNG spam lại", len(sb.notifies()), 1)
    check("KHÔNG bắn wake nào suốt các chu kỳ mù", len(sb.wakes()), 0)
    sb.repair_db()
    check("ccdb sống lại: exit 0", sb.run(), 0)
    check("bộ đếm mù được reset", sb.state_json().get("consecutive_aborts"), 0)
    check("cờ đã-báo được hạ (lần sập sau vẫn báo được)",
          sb.state_json().get("abort_alerted"), False)
    sb.close()

    print("== CA m5: ccdb sống lại NHƯNG state không ghi được ⇒ clear_abort() phải LỘ RA lý do, "
          "không được im lặng nuốt lỗi (arch-reviewer vòng 4, mục nhẹ đi kèm — mutation bỏ check "
          "giá trị trả về ở clear_abort SỐNG SÓT ở vòng đó, khoá lại ở đây)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_050000")
    sb.break_db()
    for _ in range(3):
        sb.run()
    check("abort_alerted đã bật trước khi state hỏng",
          sb.state_json().get("abort_alerted"), True)
    sb.repair_db()
    # Cùng kỹ thuật CA u: chép state ĐÃ CÓ sang thư mục mới rồi khoá — lock_state_dir() gốc
    # chuyển sang path trống, không mô phỏng đúng "ccdb sống lại NHƯNG đĩa state hỏng".
    _locked_dir = os.path.join(sb.dir, "statedir_m5")
    os.makedirs(_locked_dir, exist_ok=True)
    shutil.copy(sb.state, os.path.join(_locked_dir, "state.json"))
    sb.state = os.path.join(_locked_dir, "state.json")
    os.chmod(_locked_dir, 0o500)
    rc = sb.run()
    os.chmod(_locked_dir, 0o700)
    check("exit 0 (ccdb sống lại, chu kỳ vẫn coi là chạy được)", rc, 0)
    with open(os.path.join(sb.dir, "reconcile.log"), encoding="utf-8") as f:
        recon_log = f.read()
    check("có dòng STATE-UNWRITABLE (clear_abort) trong log",
          "STATE-UNWRITABLE (clear_abort)" in recon_log, True)
    check("abort_alerted VẪN kẹt True trên đĩa (reset không persist được — rủi ro đã khai)",
          sb.state_json().get("abort_alerted"), True)
    sb.close()

    print("== CA m3: notify HỎNG khi đang mù ⇒ KHÔNG đánh dấu đã báo, chu kỳ sau THỬ LẠI "
          "(ca này là ca THƯỜNG GẶP NHẤT: tasks.db/API chết thì notify_thread.sh cũng chết "
          "— cùng bridge 127.0.0.1:8199)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[], notify_fail=True)
    sb.job("Taylor_20260820_040000")
    sb.break_db()
    for _ in range(5):
        sb.run()
    # `abort_alerted` bật DÙ notify hỏng = cảnh báo mù bị nuốt VĨNH VIỄN. Đây đúng invariant
    # mà CA f4 đã khoá cho `escalated`; arch-reviewer vòng 4 đo được nó chưa được khoá cho
    # `abort_alerted` (mutation đưa gán ra ngoài khối `if notify(...)` vẫn PASS 76/76).
    # `is True` chứ không `== False`: chưa từng gửi được thì khoá còn VẮNG (None) — cả None
    # lẫn False đều là "chưa báo được", cái ta cấm là True.
    check("KHÔNG đánh dấu đã báo khi notify hỏng",
          sb.state_json().get("abort_alerted") is True, False)
    check("chu kỳ sau vẫn THỬ báo lại (không bỏ cuộc im lặng)",
          len(sb.notifies()) >= 2, True)
    check("vẫn KHÔNG bắn wake nào", len(sb.wakes()), 0)
    sb.notify_fail_off()                       # ccdb sống lại đủ để nhận tin
    sb.run()
    check("gửi được rồi thì mới đánh dấu", sb.state_json().get("abort_alerted"), True)
    _before = len(sb.notifies())
    sb.run()
    check("đã đánh dấu rồi thì KHÔNG spam nữa", len(sb.notifies()), _before)
    sb.close()

    print("== CA m2: dòng abort in ra stdout phải có tiền tố CRITICAL + dấu thời gian ⇒ "
          "bin/cron_health_check.py bắt được (đường báo sống cả khi ccdb chết)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[], corrupt_db=True)
    env = dict(os.environ)
    env.update({
        "WAKEUP_RECONCILE_JOBS_DIR": sb.jobs, "WAKEUP_RECONCILE_TASKS_DB": sb.db,
        "WAKEUP_RECONCILE_SESSIONS_API": API_URL, "WAKEUP_RECONCILE_WAKE_SH": sb.wake_sh,
        "WAKEUP_RECONCILE_NOTIFY_SH": sb.notify_sh, "WAKEUP_RECONCILE_ERR_LOG": sb.errlog,
        "WAKEUP_RECONCILE_LOG": os.path.join(sb.dir, "reconcile.log"),
        "WAKEUP_RECONCILE_STATE": sb.state,
        "WAKEUP_RECONCILE_LOCK": os.path.join(sb.dir, "lock"),
        "WAKEUP_RECONCILE_MIN_TS": "0",
    })
    out = subprocess.run([sys.executable, SCRIPT], env=env, capture_output=True,
                         text=True, timeout=60).stdout
    check("stdout có tiền tố CRITICAL (nằm sẵn trong ERROR_PATTERNS)",
          out.startswith("CRITICAL ABORT") or "\nCRITICAL ABORT" in out, True)
    # Dấu thời gian là load-bearing: `cron_health_check.scan_errors` lấy datestamp GẦN NHẤT
    # để bỏ hit cũ hơn 10 ngày. Dòng không có ngày ⇒ một abort cũ bị báo lại vĩnh viễn.
    check("stdout có dấu thời gian ICT để hit tự già đi",
          bool(re.search(r"20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\+07:00", out)), True)
    # Chạy CHÍNH regex của cron_health_check.py lên dòng vừa in — đừng tin "CRITICAL chắc
    # là khớp", đo nó (chuỗi CŨ `ABORT tasks.db...` đã được đo là NO-MATCH).
    sys.path.insert(0, os.path.dirname(SCRIPT))
    chc = importlib.import_module("cron_health_check")
    hit = [ln for ln in out.splitlines() if chc.ERROR_RE.search(ln)]
    check("regex THẬT của cron_health_check.py khớp dòng abort", len(hit) >= 1, True)
    sb.close()

    # Dòng OK (chu kỳ đối chiếu ĐƯỢC) cũng phải mang dấu thời gian ICT: `daily_retro.sh` đếm
    # `^OK $TODAY` để biết reconciler có THẬT SỰ chạy hay không. Không có nó thì "chạy sạch cả
    # ngày" và "cron bị gỡ" cho ra cùng một báo cáo rescued=0 (arch-reviewer N2, vòng 4).
    sb = Sandbox(sessions=[sess(THREAD_A, "running")], tasks=[])
    env["WAKEUP_RECONCILE_JOBS_DIR"] = sb.jobs
    env["WAKEUP_RECONCILE_TASKS_DB"] = sb.db
    env["WAKEUP_RECONCILE_WAKE_SH"] = sb.wake_sh
    env["WAKEUP_RECONCILE_NOTIFY_SH"] = sb.notify_sh
    env["WAKEUP_RECONCILE_ERR_LOG"] = sb.errlog
    env["WAKEUP_RECONCILE_LOG"] = os.path.join(sb.dir, "reconcile.log")
    env["WAKEUP_RECONCILE_STATE"] = sb.state
    env["WAKEUP_RECONCILE_LOCK"] = os.path.join(sb.dir, "lock")
    out_ok = subprocess.run([sys.executable, SCRIPT], env=env, capture_output=True,
                            text=True, timeout=60).stdout
    check("dòng OK mang dấu thời gian ICT (daily_retro đếm chu kỳ ĐÃ CHẠY từ nó)",
          bool(re.match(r"^OK 20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\+07:00 candidates=",
                        out_ok.strip())), True)
    sb.close()

    print("== CA m4: state KHÔNG ghi được khi đang mù ⇒ bộ đếm không tích luỹ được ⇒ đường "
          "notify chết câm; dòng CRITICAL PHẢI nói ra điều đó, không được im")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_050000")
    sb.break_db()
    sb.lock_state_dir()                        # chmod 500 ⇒ os.replace() ném
    outs = []
    for _ in range(5):
        env = dict(os.environ)
        env.update({
            "WAKEUP_RECONCILE_JOBS_DIR": sb.jobs, "WAKEUP_RECONCILE_TASKS_DB": sb.db,
            "WAKEUP_RECONCILE_SESSIONS_API": API_URL, "WAKEUP_RECONCILE_WAKE_SH": sb.wake_sh,
            "WAKEUP_RECONCILE_NOTIFY_SH": sb.notify_sh, "WAKEUP_RECONCILE_ERR_LOG": sb.errlog,
            "WAKEUP_RECONCILE_LOG": os.path.join(sb.dir, "reconcile.log"),
            "WAKEUP_RECONCILE_STATE": sb.state,
            "WAKEUP_RECONCILE_LOCK": os.path.join(sb.dir, "lock"),
            "WAKEUP_RECONCILE_MIN_TS": "0",
        })
        outs.append(subprocess.run([sys.executable, SCRIPT], env=env, capture_output=True,
                                   text=True, timeout=60).stdout)
    # Ca đo được (arch-reviewer N3, vòng 4): đếm đóng băng ở 1 qua CẢ 5 chu kỳ, ngưỡng
    # ABORT_ALERT_AFTER không bao giờ tới ⇒ 0 lời gọi notify. Đường CRITICAL là đường DUY
    # NHẤT còn sống, nên nó không được nói "liên tiếp=1" như thể sự cố vừa mới bắt đầu.
    check("đếm quả thật đóng băng (ca này là ca xấu, ta đang đo nó)",
          all("liên tiếp=1" in o for o in outs), True)
    check("KHÔNG có lời gọi notify nào (đúng: bộ đếm không tới ngưỡng được)",
          len(sb.notifies()), 0)
    check("dòng CRITICAL nói RÕ là không ghi được state",
          all("KHÔNG ghi được state" in o for o in outs), True)
    check("dòng CRITICAL nói RÕ cảnh báo Discord sẽ không bắn",
          "sẽ không bao giờ bắn" in outs[-1], True)
    sb.unlock_state_dir()
    sb.close()

    print("== CA n: mỗi lượt cứu dùng TÊN TASK ccdb KHÁC NHAU (name là UNIQUE — trùng tên ⇒ "
          "409 tiêu trần mà không đánh thức được ai)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_20260820_030000")
    sb.run()
    sb.age_state(REFIRE + 60)
    sb.run()
    sb.age_state(REFIRE + 60)
    sb.run()
    sfx = [w[2] for w in sb.wakes()]
    check("cứu đủ 3 lượt (đúng MAX_FIRES_PER_JOB)", len(sfx), 3)
    check("3 tên task PHÂN BIỆT được", len(set(sfx)), 3)
    check("tên vẫn truy ra được job gốc",
          all(x.startswith("Taylor_20260820_030000-reconcile") for x in sfx), True)
    sb.close()

    print("== CA o: job QUÁ CŨ (arch-reviewer killer objection trước-commit 08-20 — dry-run "
          "thật cho ra job 43 GIỜ tuổi vẫn bị bắn vào kênh plan). RESCUE_MAX_AGE phải chặn "
          "wake, chỉ báo 1 lần, không spam lại chu kỳ sau")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    old_ended = str(int(time.time()) - _wr.RESCUE_MAX_AGE - 3600)  # 1h qua trần
    sb.job("DollarBill_old_stale", ended_at=old_ended)
    rc1 = sb.run()
    check("exit 0 (chu kỳ vẫn chạy sạch dù có job quá cũ)", rc1, 0)
    check("KHÔNG bắn wake nào cho job quá cũ", len(sb.wakes()), 0)
    n1 = sb.notifies()
    check("đúng 1 notify 'quá cũ, KHÔNG tự đánh thức'",
          sum(1 for _, m in n1 if "quá cũ" in m and "KHÔNG" in m), 1)
    sb.run()
    n2 = sb.notifies()
    check("chu kỳ sau KHÔNG notify lại (đã dedupe qua stale_notified)", len(n2), len(n1))
    check("state ghi nhớ stale_notified cho đúng job",
          bool((sb.state_json().get("fired") or {})
               .get("DollarBill_old_stale", {}).get("stale_notified")), True)
    sb.close()

    print("== CA p: 1 job record JSON HỎNG nằm cạnh 1 job HỢP LỆ — reconciler không được chết "
          "hay bỏ sót job hợp lệ, và KHÔNG được nuốt lỗi im lặng (arch-reviewer F4)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_valid_ok")
    with open(os.path.join(sb.jobs, "Broken_record.json"), "w") as f:
        f.write("{ dây không phải JSON hợp lệ")
    rc = sb.run()
    check("exit 0 (record hỏng không làm chết cả chu kỳ)", rc, 0)
    check("job HỢP LỆ vẫn được cứu bình thường", len(sb.wakes()), 1)
    with open(os.path.join(sb.dir, "reconcile.log"), encoding="utf-8") as f:
        recon_log = f.read()
    check("có dòng JOB-UNREADABLE nêu tên file hỏng",
          "JOB-UNREADABLE" in recon_log and "Broken_record.json" in recon_log, True)
    sb.close()

    print("== CA q: state KHÔNG ghi được + 1 job quá cũ, 4 chu kỳ liên tiếp — nhánh too_old "
          "PHẢI tôn trọng write_state() y hệt vòng fire (arch-reviewer killer, re-audit 08-20: "
          "trước vá này đo được 4/4 chu kỳ đều gửi lại cùng tin, ngoại suy 288/ngày/job)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_stale_statehỏng", ended_at=str(int(time.time()) - _wr.RESCUE_MAX_AGE - 3600))
    sb.lock_state_dir()
    for _ in range(4):
        sb.run()
    # Ghi TRƯỚC-notify-SAU (khớp vòng fire, xem sửa F1-followup): state hỏng ⇒ KHÔNG BAO GIỜ
    # tới được lời gọi notify "quá cũ" — 0 lần, không phải 1 lần rồi thôi. "tự dừng" được
    # PHÉP lặp lại mỗi chu kỳ (cùng tiền lệ CA f8 của vòng fire, dòng ~439: đây là cảnh báo
    # vận hành hợp lệ tái diễn tới khi ai đó sửa quyền/dung lượng đĩa, khác bản chất với tin
    # "quá cũ" — thứ mà arch-reviewer chỉ đích danh KHÔNG được lặp).
    check("KHÔNG BAO GIỜ tới được notify 'quá cũ' khi state hỏng ngay từ đầu",
          sum(1 for _, m in sb.notifies() if "quá cũ" in m and "tự dừng" not in m), 0)
    check("có tin 'tự dừng (nhánh quá cũ)' báo lý do",
          any("tự dừng (nhánh quá cũ)" in m for _, m in sb.notifies()), True)
    sb.unlock_state_dir()
    sb.close()

    print("== CA r: 12 job quá cũ CÙNG một chu kỳ — MAX_STALE_NOTIFIES_PER_CYCLE phải chặn "
          "fan-out (arch-reviewer N3, re-audit 08-20: trước vá này đo được 12 tin/1 chu kỳ)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    old_ts = str(int(time.time()) - _wr.RESCUE_MAX_AGE - 3600)
    for i in range(12):
        sb.job("Taylor_manyold_%d" % i, ended_at=old_ts,
               discord_thread_id=str(int(THREAD_A) + i))
    sb.run()
    check("chặn đúng trần MAX_STALE_NOTIFIES_PER_CYCLE (không phải 12)",
          len(sb.notifies()), _wr.MAX_STALE_NOTIFIES_PER_CYCLE)
    sb.close()

    print("== CA s: job ĐÃ bỏ cuộc (escalated) rồi mới vượt 4h — KHÔNG được nhận thêm 1 tin "
          "'quá cũ' khác giọng cho CÙNG một sự việc (arch-reviewer N2, re-audit 08-20)")
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    # ended_at gần đây (an toàn, không đua với thời gian thật của subprocess) — 4 lượt run()
    # dùng age_state() để nhảy cooldown mà KHÔNG đụng ended_at, nên job không vô tình tự
    # trôi qua RESCUE_MAX_AGE giữa chừng do overhead spawn subprocess.
    sb.job("Taylor_escalate_then_old", ended_at=str(int(time.time()) - 300))
    for _ in range(3):
        sb.run()
        sb.age_state(REFIRE + 60)
    sb.run()  # lượt thứ 4: n đã = MAX_FIRES_PER_JOB -> escalate ở ĐÂY (khớp cách CA n đo)
    n_before = len(sb.notifies())
    check("đã bỏ cuộc đúng 1 lần sau khi hết trần cứu", n_before, 1)
    check("state đã đánh dấu CẢ escalated LẪN stale_notified tại thời điểm bỏ cuộc",
          all(sb.state_json().get("fired", {})
              .get("Taylor_escalate_then_old", {}).get(k) for k in ("escalated", "stale_notified")),
          True)
    # Ghi ĐÈ TRỰC TIẾP ended_at của job (không chờ thời gian thật trôi 4h) để mô phỏng nó
    # giờ đã quá cũ — state (escalated/stale_notified) giữ nguyên từ bước trên.
    sb.job("Taylor_escalate_then_old",
           ended_at=str(int(time.time()) - _wr.RESCUE_MAX_AGE - 3600))
    sb.run()
    check("KHÔNG nhận thêm tin 'quá cũ' sau khi đã bỏ cuộc (dedupe qua stale_notified chung)",
          len(sb.notifies()), n_before)
    sb.close()

    print("== CA t: record hỏng -> phải in CRITICAL RA STDOUT (không chỉ ghi vào log riêng) "
          "để bin/cron_health_check.py bắt được cùng ngày (arch-reviewer N4, re-audit 08-20)")
    import re as _re
    CRON_HEALTH_ERROR_RE = _re.compile(r"CRITICAL", _re.MULTILINE)
    sb = Sandbox(sessions=[sess(THREAD_A, "idle")], tasks=[])
    sb.job("Taylor_valid_for_t")
    with open(os.path.join(sb.jobs, "Broken_for_t.json"), "w") as f:
        f.write("{ vẫn không phải JSON hợp lệ")
    r = subprocess.run(
        [sys.executable, SCRIPT], env={**os.environ,
            "WAKEUP_RECONCILE_JOBS_DIR": sb.jobs, "WAKEUP_RECONCILE_TASKS_DB": sb.db,
            "WAKEUP_RECONCILE_SESSIONS_API": API_URL, "WAKEUP_RECONCILE_WAKE_SH": sb.wake_sh,
            "WAKEUP_RECONCILE_NOTIFY_SH": sb.notify_sh, "WAKEUP_RECONCILE_ERR_LOG": sb.errlog,
            "WAKEUP_RECONCILE_LOG": os.path.join(sb.dir, "reconcile.log"),
            "WAKEUP_RECONCILE_STATE": sb.state,
            "WAKEUP_RECONCILE_LOCK": os.path.join(sb.dir, "lock"),
            "WAKEUP_RECONCILE_BATCHES_DIR": sb.batches,
            "WAKEUP_RECONCILE_MIN_TS": "0"},
        capture_output=True, text=True, timeout=60)
    check("dòng CRITICAL khớp ĐÚNG regex thật của cron_health_check.py",
          bool(CRON_HEALTH_ERROR_RE.search(r.stdout)), True)
    check("dòng CRITICAL nêu số record không đọc được",
          "1 job record không đọc được" in r.stdout, True)
    sb.close()

    print("== CA u: job thuộc đợt fan-out (--batch-id) mà batch CÒN ĐANG BAY ⇒ KHÔNG cứu "
          "(im lặng là đúng thiết kế: anh em cuối đợt sẽ bắn 1 wake gộp). Hết bay ⇒ cứu lại.")
    sb = Sandbox()
    sb.job("Plan_A", batch_id="planT1_u", ended_at=str(int(time.time()) - 600))
    # Anh em cùng đợt CÒN CHẠY THẬT: pid của chính tiến trình test (chắc chắn sống) + deadline
    # còn hạn. Đây là ca đã tái diễn thật 08-18/08-20 — hai job DollarBill lệch nhau 31-83s.
    sb.job("Plan_B", status="running", pid=str(os.getpid()),
           deadline=str(int(time.time()) + 600), batch_id="planT1_u", ended_at=None)
    sb.batch("planT1_u", ["Plan_A", "Plan_B"], expected=2)
    sb.run()
    check("batch còn bay ⇒ KHÔNG cứu job xong sớm (0 wake)", len(sb.wakes()), 0)
    # Anh em xong ⇒ batch hết bay. Lượt wake gộp của dispatch.sh có thể đã chết (đó là lý do
    # reconciler tồn tại) ⇒ lưới cuối phải cứu lại, đúng 1 lượt cho cả thread.
    sb.job("Plan_B", status="done", pid=str(os.getpid()),
           deadline=str(int(time.time()) + 600), batch_id="planT1_u",
           ended_at=str(int(time.time()) - 600))
    sb.run()
    check("batch hết bay mà vẫn chưa ai claim-reply ⇒ lưới cuối cứu (1 wake)", len(sb.wakes()), 1)
    sb.close()

    print()
    if FAILS:
        print("wakeup_reconcile_selfcheck: FAIL (%d/%d) — %s"
              % (len(FAILS), CASES[0], "; ".join(FAILS)))
        return 1
    print("wakeup_reconcile_selfcheck: PASS (%d/%d)" % (CASES[0], CASES[0]))
    return 0


if __name__ == "__main__":
    srv = http.server.HTTPServer(("127.0.0.1", 0), _Sessions)
    API_URL = "http://127.0.0.1:%d/api/sessions" % srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        sys.exit(main())
    finally:
        srv.shutdown()
