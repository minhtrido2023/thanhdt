#!/usr/bin/env python3
"""production_manifest.py — sinh danh sách file PRODUCTION thật của ARIA bằng bằng chứng CƠ HỌC.

Việc C của review ARIA (agents/Mike/research/aria_review_response_20260913.md, user duyệt
2026-09-13, job Wags_20260913_053331). Bước 1 CHỈ là manifest — không di chuyển/đổi tên file.

Cách làm (không đoán theo tên file):
  1. GỐC = mọi dòng `crontab -l` + systemd user unit `mike*`/`ccdb*`/`paseo*` đang load + hook
     trong `.claude/settings*.json` (WorkingClaude, mike, mike/agents/<id>).
  2. ĐÓNG BAO tới điểm bất động (BFS, ghi depth nhỏ nhất):
     - Python: AST import (Import/ImportFrom, cả relative) resolve thành file trong repo;
       + chuỗi hằng dạng đường dẫn `*.py|*.sh` (subprocess/Path) resolve được thành file thật.
     - Bash: token `*.py|*.sh` trên dòng lệnh (bỏ comment, echo/printf, heredoc văn bản);
       heredoc chạy bằng python được parse như Python; `python3 -m mod` resolve như import.
     Chỉ nhận cạnh resolve ra FILE CÓ THẬT trong WorkingClaude và ngoài vùng loại trừ.
  3. TẦNG = nhỏ nhất theo các gốc với tới file, KHÔNG đi xuyên entry script của gốc khác (và
     dispatch.sh với gốc ngoài T2): T0 money-path, T1 dữ liệu/regime/paper, T2 fleet-ops.
     `blast_tier` = nhỏ nhất theo mọi gốc KHÔNG rào (ai gọi tới được, kể cả nhánh lỗi/phụ). Tầng của GỐC lấy từ bảng ROOT_TIER dưới đây (tường minh, review được);
     gốc mới chưa phân loại => tầng "T?" và selfcheck FAIL cho tới khi thêm vào bảng.
     T3 = file tên chứa `selfcheck` (không với tới từ gốc) mà import/exec TRỰC TIẾP file T0-T2.
  File ngoài 4 tầng = research, không liệt kê.

GIỚI HẠN ĐÃ BIẾT (ghi vào manifest): không thấy đường chạy ĐỘNG — agent được dispatch tự chọn
script (vd bq_freshness_check.sh dispatch DollarBill), đường dẫn ghép từ biến runtime, importlib
theo chuỗi tính toán. Không liệt kê file dữ liệu/config (.json) — chỉ .py/.sh.

Dùng:
  python3 mike/bin/production_manifest.py              # ghi kb/production_manifest.{json,md}
  python3 mike/bin/production_manifest.py --stdout-json # in JSON, không ghi (selfcheck dùng)
  python3 mike/bin/production_manifest.py --crontab F   # đọc crontab từ file (test)
"""
import argparse
import ast
import datetime
import glob
import json
import os
import re
import subprocess
import sys
from collections import deque

WC = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MIKE = os.path.join(WC, "mike")
OUT_JSON = os.path.join(MIKE, "kb", "production_manifest.json")
OUT_MD = os.path.join(MIKE, "kb", "production_manifest.md")
REGEN_CMD = "python3 mike/bin/production_manifest.py"

# Loại trừ tường minh: mirror mike_paseo (cố ý của user, KHÔNG phải production), mọi worktree,
# venv/cache. Khớp theo THÀNH PHẦN đường dẫn tương đối gốc WC.
EXCLUDE_PART = re.compile(r"^(mike_paseo|wt-.*|worktrees|\.git|__pycache__|node_modules|\.?venv|wc_venv|site-packages)$")

# Thư mục thêm vào "sys.path" khi resolve import — đo từ repo (grep sys.path.insert 2026-09-13):
# WORKDIR/WC_ROOT (281+31+…), stockquery (9), mike/bin (8). Thư mục của file đứng đầu.
IMPORT_BASES = [WC, os.path.join(WC, "stockquery"), os.path.join(MIKE, "bin"), MIKE]
# Gốc resolve đường dẫn tương đối trong lệnh ($ROOT/bin/x.sh => mike/bin/x.sh …).
REF_BASES = [WC, MIKE, os.path.join(MIKE, "bin")]

# Tầng của GỐC theo basename script gốc (hoặc tên unit/hook). Phân loại theo VAI TRÒ dòng cron.
T0, T1, T2 = "T0", "T1", "T2"
ROOT_TIER = {
    # T0 — đặt lệnh / plan / NAV / báo cáo gửi nhà đầu tư
    "run_bot.sh": T0, "bot_heartbeat.sh": T0, "session_announce.sh": T0,
    "compute_active_nav_all.sh": T0, "inject_discretionary_orders.sh": T0,
    "send_plan_report.sh": T0, "preflight_check.sh": T0, "eod_trading_report.sh": T0,
    "park_trim_daily.sh": T0, "jit_unpark_daily.sh": T0, "merge_park_daily.sh": T0,
    "late_plan_catchup.sh": T0, "nav_sync_retry.sh": T0, "nav_snapshot_daily.sh": T0, "check_report_cadence.sh": T0,
    "corp_action_auto_confirm.py": T0, "discretionary_margin_check_exits_daily.sh": T0,
    "bq_freshness_check.sh": T0,  # EOD pipeline + dispatch lập plan
    "plan_approval_reminder.sh": T0,  # tái dùng approval_block_reason() của bot_execute.py — phần của chuỗi approval-gate T0
    # T1 — pipeline dữ liệu / regime / feed / paper
    "papertrade_daily.sh": T1, "pt_8l_daily.sh": T1, "telegram_run_daily.sh": T1,
    "daily_refresh_v34b_linux.sh": T1, "auto_update_commodity_wb.sh": T1,
    "rubber_weekly.sh": T1, "update_shares_live.sh": T1, "insider_flags.py": T1,
    "sync_bq_cache_daily.sh": T1, "fetch_new_listings_daily.sh": T1,
    "check_sbv_weekly.sh": T1, "hit_details_daily.sh": T1,
    "paper_programs_daily_report.sh": T1, "dc_book_waterfall_paper.py": T1,
    "vcb_fx_feed.py": T1, "hog_price_feed.py": T1, "newdeals_daily_report.py": T1,
    "paper_main_probe_plan.py": T1, "bot_execute.py": T0,  # dòng cron `--account main` là paper, nhưng FILE là engine đặt lệnh live
    "paper_main_early_check.sh": T1, "refresh_fa_ratings_8l.sh": T1,
    "refresh_fa_ratings.sh": T1, "fa_ratings_earnings_window_daily.sh": T1,
    "refresh_deposit_rate_vn.sh": T1, "dcf_refresh_gate.py": T1,
    "fearbuy_weekly_scan.sh": T1, "paper_late_feeds.sh": T1, "bq_monthly_pin.sh": T1,
    "custom30v_rebalance_watch.sh": T1, "corp_action_daily.sh": T1,
    "snapshot_corp_action_daily.py": T1, "capture_upcom_vwap_eod.sh": T1,
    "c1_shadow_paper.py": T1, "vn_realestate_monthly_check.sh": T1, "oni_index_feed.py": T1,
    # Thêm 2026-09-19 (weekly ops audit): 4 gốc cron mới 09-15..09-18, cả 4 là feed/monitor
    # WARN-ONLY — không ghi lệnh/plan/NAV/báo cáo nhà đầu tư, và KHÔNG nằm trong
    # `code_quality_autodispatch.ORDER_WRITING_ROOTS` (ranh giới tự-sửa là frozenset tường minh
    # ở file đó, độc lập với bảng này) nên phân T1 không nới ranh giới nào.
    "corp_action_feed_canary.py": T1,          # canary drift giá trị feed vendor corporate_action
    "fiinprox_harvest_tick.sh": T1,            # wrapper cron harvest FiinPro-X
    "fiinprox_harvest_tick.py": T1,            # hàng đợi harvest FiinPro-X (ghi file raw)
    "treasury_buyback_window_monitor.py": T1,  # monitor cửa sổ tuân thủ mua cổ phiếu quỹ
    "paper_corp_action.py": T1,  # công cụ ĐO corp-action cho sổ PaperBroker, không chạm tiền thật/đường đặt lệnh
    # Thêm 2026-09-26 (weekly ops audit): 2 gốc cron mới 09-25/09-26, cả hai là QUAN SÁT-ONLY
    # của chương trình paper (order_book_execution_shadow / ORB intraday). Kiểm CƠ HỌC trước khi
    # phân tầng: grep `place_order|PlannedOrder|trade_plans|nav_history|send_report|
    # report_delivery` trên cả 3 file (kể cả orb_normstat.py đi kèm) ⇒ **0 hit**; docstring hai
    # file tự khai "KHÔNG đặt lệnh" / "CHỈ GIÁM SÁT, không ghi file production nào". Cả hai
    # KHÔNG nằm trong `code_quality_autodispatch.ORDER_WRITING_ROOTS` nên T1 không nới ranh
    # giới tự-sửa nào — cùng lập luận đã dùng cho 4 gốc thêm ngày 2026-09-19.
    "opening_window_l2_poll.py": T1,  # poll L2 cửa sổ đầu phiên, quote_only=True, không đặt lệnh
    "orb_drift_monitor.py": T1,       # cảnh báo sớm lệch kỳ vọng paper ORB, chỉ log + bus question
    # T2 — fleet-ops (dispatch/bus/consolidate/health/backup/audit/hook)
    "consolidate.sh": T2, "watchdog.sh": T2, "discover_sessions.py": T2,
    "resume_pending.py": T2, "fleet_backup.sh": T2, "start.sh": T2,
    "ops_health_check.sh": T2, "kb_nightly.sh": T2, "worktree_cleanup_daily.sh": T2,
    "daily_retro.sh": T2, "fleet_housekeeping.sh": T2, "weekly_ops_audit.sh": T2,
    "cron_health_check_daily.sh": T2, "paper_checkpoint_escalation.sh": T2,
    "selfcheck_weekly_baseline_check.sh": T2, "spend_report_weekly.sh": T2,
    "code_quality_weekly.sh": T2, "backup_freshness_check.sh": T2,
    "session_start.sh": T2, "stop.sh": T2, "user_prompt_submit.sh": T2,
    "unit:ccdb-mike.service": T2, "unit:paseo.service": T2,
    "pkill": T0,  # dừng bot giờ trưa — không có file
}
# dispatch.sh = bàn giao việc cho 1 agent. Bao đóng CỦA dispatch.sh (consolidate.sh -> kb_nightly.sh
# -> …) là hạ tầng fleet chạy SAU khi agent xong, không phải đường tiền của gốc gọi nó. Đo 2026-09-13:
# không có rào này, bq_freshness_check.sh (T0) kéo ~toàn bộ fleet-ops lên T0 qua đúng 1 cạnh
# dispatch.sh -> consolidate.sh. Bản thân dispatch.sh VẪN nhận tầng của người gọi (T0 — khớp luật
# arch-review bắt buộc khi sửa dispatch.sh). Gốc T2 đi xuyên qua bình thường.
DISPATCH_BARRIER = {"mike/bin/dispatch.sh"}
# Wrapper trong suốt: tầng lấy theo script được bọc, không theo wrapper.
WRAPPERS = {"for_each_live_account.sh"}

PATH_TOKEN = re.compile(r"[A-Za-z0-9_./${}~\"'-]*[A-Za-z0-9_-]\.(?:py|sh)(?![A-Za-z0-9_])")
PY_MOD_FLAG = re.compile(r"python3?\S*\s+(?:-\S+\s+)*-m\s+([A-Za-z_][\w.]*)")
HEREDOC = re.compile(r"<<-?\s*['\"]?([A-Za-z_]\w*)['\"]?")
IMPORT_LINE = re.compile(r"^\s*(?:from\s+([.\w]+)\s+import\s+([\w, ()*]+)|import\s+([\w., ]+))")


def rel(p):
    return os.path.relpath(p, WC)


_TRACKED = None
UNTRACKED_HITS = set()


def tracked():
    """File đã track trong git (repo WorkingClaude + repo lồng mike). Arch-review 2026-09-13 F1: quét
    filesystem thì bắt cả WIP untracked của job song song (loan_package_multi_account_selfcheck.py
    của Taylor_20260913_050827) => manifest commit lệch ngay khi job kia dọn file."""
    global _TRACKED
    if _TRACKED is None:
        _TRACKED = set()
        for repo, prefix in ((WC, ""), (MIKE, "mike/")):
            r = subprocess.run(["git", "-C", repo, "ls-files", "-z"], capture_output=True, text=True, check=True)
            _TRACKED.update(prefix + x for x in r.stdout.split("\0") if x)
    return _TRACKED


def in_scope(p):
    p = os.path.realpath(p)
    if not p.startswith(WC + os.sep) or not os.path.isfile(p):
        return False
    rp = rel(p)
    if any(EXCLUDE_PART.match(part) for part in rp.split(os.sep)[:-1]):
        return False
    if rp not in tracked():
        UNTRACKED_HITS.add(rp)
        return False
    return True


def resolve_ref(token, ctx_dirs):
    """Token lệnh/chuỗi -> file trong repo hoặc None."""
    t = token.strip("\"'")
    t = t.replace("${HOME}", os.path.expanduser("~")).replace("$HOME", os.path.expanduser("~"))
    t = os.path.expanduser(t)
    if t.startswith("/"):
        return os.path.realpath(t) if in_scope(t) else None
    # bỏ tiền tố biến ($ROOT/, ${WC_ROOT}/, "$HERE"/ …) — thử phần còn lại trên các gốc
    t = re.sub(r"^(\$\{?\w+\}?/?)+", "", t)
    t = re.sub(r"^(\./)+", "", t)
    if "$" in t or not t:
        t = t.rsplit("}", 1)[-1].lstrip("/")
        if "$" in t or not t:
            return None
    for base in list(ctx_dirs) + REF_BASES:
        c = os.path.join(base, t)
        if in_scope(c):
            return os.path.realpath(c)
    return None


def resolve_module(mod, level, file_dir, names=()):
    """Tên module -> danh sách file trong repo (module + submodule nếu `from pkg import sub`)."""
    if level:
        base = file_dir
        for _ in range(level - 1):
            base = os.path.dirname(base)
        bases = [base]
    else:
        bases = [file_dir] + IMPORT_BASES
    parts = mod.split(".") if mod else []
    out = []
    for b in bases:
        stem = os.path.join(b, *parts) if parts else b
        hit = None
        for c in (stem + ".py", os.path.join(stem, "__init__.py")):
            if parts and in_scope(c):
                hit = c
                break
        if hit or (not parts and os.path.isdir(stem)):
            if hit:
                out.append(os.path.realpath(hit))
                # các package cha cũng chạy __init__
                for i in range(1, len(parts)):
                    ini = os.path.join(b, *parts[:i], "__init__.py")
                    if in_scope(ini):
                        out.append(os.path.realpath(ini))
            for n in names:
                sub = os.path.join(stem, n + ".py")
                if in_scope(sub):
                    out.append(os.path.realpath(sub))
            if out:
                break
    return out


def scan_sh_line(line, st):
    """Quét 1 dòng bash, MANG trạng thái ngoặc sang dòng sau (arch-review 2026-09-13 F2: prompt nhiều
    dòng gửi agent — ops_autofix.sh:172, refresh_deposit_rate_vn.sh:82 — trước bị coi là lệnh).
    Trả dòng đã: bỏ comment; thay chuỗi trong ngoặc CÓ khoảng trắng (thông điệp/prompt) bằng ' ';
    giữ chuỗi không khoảng trắng ("$ROOT/bin/x.sh"), chuỗi chứa `$(` và đối số của `bash -c`.
    Thân `python3 -c '…'` được đẩy vào st["pysrc"] để parse như Python."""
    out, i, n = [], 0, len(line)
    if st["q"] is None and line.lstrip().startswith("#"):
        return ""
    while i < n:
        ch = line[i]
        if st["q"]:
            if ch == "\\" and st["q"] == '"' and i + 1 < n:
                st["seg"].append(line[i:i + 2])
                i += 2
                continue
            if ch == "'" and st["q"] == "'":
                # idiom nối biến vào thân single-quote: '…'"$ROOT"'…' — vẫn là CÙNG một chuỗi
                m = re.match(r"'\".*?\"'", line[i:])
                if m:
                    st["seg"].append(m.group(0)[1:-1].strip('"'))
                    i += m.end()
                    continue
            if ch == st["q"]:
                seg = "".join(st["seg"])
                if st["dash_c"] == "py":
                    st["pysrc"].append(seg)
                    out.append(" ")
                elif st["dash_c"] == "sh":
                    st["shsrc"].append(seg)
                    out.append(" ")
                elif not re.search(r"\s", seg) or (st["q"] == '"' and "$(" in seg):
                    out.append(seg)
                else:
                    out.append(" ")
                st.update(q=None, seg=[], dash_c=None)
            else:
                st["seg"].append(ch)
            i += 1
            continue
        if ch == "\\" and i + 1 < n:
            out.append(line[i + 1])
            i += 2
            continue
        if ch == "#" and (i == 0 or line[i - 1] in " \t;"):
            break
        if ch == '"' and line.startswith("$(", i + 1):
            # "$(…)" = command substitution: ngoặc kép bọc ngoài KHÔNG phải chuỗi văn bản — quét bên trong
            # như lệnh thường để `python3 -c "…"`/heredoc lồng trong nó được nhận (arch-review vòng 2 N1:
            # session_announce.sh:21 PROGRESS="$(cd "$WC_ROOT" && python3 - … << 'PYEOF').
            st["dq_subst"] += 1
            i += 1
            continue
        if ch == ")" and st["dq_subst"] and line.startswith('"', i + 1):
            st["dq_subst"] -= 1
            out.append(")")
            i += 2
            continue
        if ch in "'\"":
            before = "".join(out)
            dc = None
            if re.search(r"(^|\s)-c\s*$", before):
                dc = "py" if re.search(r"python3?\S*(\s+-\S+)*\s+-c\s*$", before) else "sh"
            st.update(q=ch, seg=[], dash_c=dc)
            i += 1
            continue
        out.append(ch)
        i += 1
    if st["q"]:
        st["seg"].append("\n")
    return "".join(out)


NON_CMD_SEG = re.compile(r"^\s*(?:\w+=)?[$({\s]*(?:echo|printf|log|say|warn|info)\b")


def edges_python_src(src, path_dir):
    """(target, kind) từ mã Python."""
    out = []
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        # fallback regex cho file lỗi cú pháp/heredoc cắt dở
        for m in IMPORT_LINE.finditer(src):
            if m.group(1):
                names = [n.strip(" ()") for n in m.group(2).split(",")]
                lvl = len(m.group(1)) - len(m.group(1).lstrip("."))
                for f in resolve_module(m.group(1).lstrip("."), lvl, path_dir, names):
                    out.append((f, "import"))
            else:
                for n in m.group(3).split(","):
                    n = n.strip().split(" ")[0]
                    for f in resolve_module(n, 0, path_dir):
                        out.append((f, "import"))
        return out
    parent = {}
    for node in ast.walk(tree):
        for ch in ast.iter_child_nodes(node):
            parent[ch] = node
    for node in ast.walk(tree):
        if in_selftest(node, parent):
            continue
        if isinstance(node, ast.Import):
            for a in node.names:
                for f in resolve_module(a.name, 0, path_dir):
                    out.append((f, "import"))
        elif isinstance(node, ast.ImportFrom):
            names = [a.name for a in node.names if a.name != "*"]
            for f in resolve_module(node.module or "", node.level, path_dir, names):
                out.append((f, "import"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = node.value.strip()
            if "\n" in v or len(v) > 300 or not path_context(node, parent):
                continue
            if re.fullmatch(r"[\w./${}~-]+\.(py|sh)", v):
                cands = [v]
            elif re.match(r"^(python3?|bash|sh|/|\$)", v):
                cands = PATH_TOKEN.findall(v)
            else:
                continue
            for c in cands:
                f = resolve_ref(c, [path_dir])
                if f:
                    out.append((f, "exec"))
    return out


NON_EXEC_CALLS = {"print", "log", "warn", "warning", "info", "error", "debug", "write", "notify",
                  "format", "startswith", "endswith", "find", "replace", "search", "match", "fail", "ok"}


# Chỉ tên đúng dạng hàm tự-kiểm (`_selfcheck`, `selftest`) — KHÔNG nuốt cổng production như
# corp_action_daily.py `gate_selfcheck()` (arch-review vòng 2 N2).
SELFTEST_FN = re.compile(r"^_?self_?(check|test)$", re.I)


def in_selftest(node, parent):
    """Import/chuỗi nằm trong hàm tự-kiểm nội tuyến (`def _selfcheck()`) là phụ thuộc của TEST, không
    phải đường chạy production. Arch-review 2026-09-13 F4: report_return_gate.py `_selfcheck()` import
    newdeals_daily_report kéo nó lên T0."""
    p = parent.get(node)
    while p is not None:
        if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)) and SELFTEST_FN.search(p.name):
            return True
        p = parent.get(p)
    return False


def path_context(node, parent):
    """Chuỗi hằng chỉ tính là cạnh exec khi nằm trong ngữ cảnh DỰNG ĐƯỜNG DẪN/LỆNH: Path / "x.py",
    đối số hàm (os.path.join, subprocess), phần tử list/tuple lệnh, gán biến. Loại so sánh
    (`"x.py" in text`), dict, f-string và đối số hàm in/log — đo 2026-09-13: cạnh giả
    bus_question_housekeeping.py -> report_delivery_gate.py đến từ `"..py" in gate.read_text()`."""
    p = parent.get(node)
    if isinstance(p, (ast.Compare, ast.Dict, ast.JoinedStr, ast.FormattedValue)):
        return False
    if isinstance(p, (ast.List, ast.Tuple)):
        p = parent.get(p)
    if isinstance(p, ast.Call):
        fn = p.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
        return name not in NON_EXEC_CALLS
    return isinstance(p, (ast.BinOp, ast.Assign, ast.AnnAssign, ast.keyword, ast.Return))


def edges_shell_src(src, path_dir, _depth=0):
    out = []
    lines = src.splitlines()
    i = 0
    in_array = False
    st = {"q": None, "seg": [], "dash_c": None, "pysrc": [], "shsrc": [], "dq_subst": 0}
    while i < len(lines):
        q_start = st["q"]
        line = scan_sh_line(lines[i], st)
        hd = HEREDOC.search(line) if st["q"] is None else None
        if hd is None and q_start is None and st["q"] == '"' and re.search(r"\$\(.*<<", lines[i]):
            # heredoc mở BÊN TRONG "$(… <<'PY'" — REPORT="$(python3 - … <<'PYEOF'" (eod_trading_report.sh:275)
            seg = "".join(st["seg"])
            hd = HEREDOC.search(seg)
            if hd:
                st["seg"] = [seg[: hd.start()]]
                line = line + " " + seg.rstrip("\n")
                hd = HEREDOC.search(line)
        if hd:
            tag = hd.group(1)
            body = []
            j = i + 1
            while j < len(lines) and lines[j].strip() != tag:
                body.append(lines[j])
                j += 1
            if re.search(r"python3?\b", line[: hd.start()]):
                out += edges_python_src("\n".join(body), path_dir)
            line = line[: hd.start()]
            i = j
        s = re.sub(r"^\s*[^\s()]*[*|][^\s()]*\)", " ", line)  # nhánh `case` (*x.py|*y.py)) là mẫu khớp
        # Bỏ đúng ĐOẠN lệnh echo/printf/log trong pipeline, giữ vế sau `|` (F3: `printf … | python3
        # "$ROOT/bin/dispatch_question_hint.py"` ở dispatch.sh:1612 trước bị mất cả dòng).
        s = " ; ".join(seg for seg in re.split(r"\|\||&&|[|;\n]", s) if not NON_CMD_SEG.match(seg)).strip(" ;")
        if s:
            cds = [os.path.join(path_dir, d) for d in re.findall(r"\bcd\s+([^\s;&|]+)", s)]
            cds = [resolve_dir(d) for d in cds]
            ctx = [d for d in cds if d] + [path_dir]
            # Mảng bash (`FILES=(` … `)`) là DANH SÁCH đường dẫn (vd scope code_quality_weekly.sh), không
            # phải lệnh — vẫn là phụ thuộc thật (vòng lặp đọc/chạy) nên giữ cạnh, nhãn `ref`.
            arr = re.match(r"^(?:local\s+|declare\s+-a\s+)?\w+=\(", s)
            kind = "ref" if (in_array or arr) else "exec"
            if arr and not re.search(r"\)\s*$", s):
                in_array = True
            elif in_array and re.search(r"\)\s*$", s):
                in_array = False
            for tok in PATH_TOKEN.findall(s):
                f = resolve_ref(tok, ctx)
                if f:
                    out.append((f, kind))
            for m in PY_MOD_FLAG.finditer(s):
                for f in resolve_module(m.group(1), 0, ctx[0]):
                    out.append((f, "exec"))
        for code in st["pysrc"]:
            out += edges_python_src(code, path_dir)
        if _depth < 3:
            for code in st["shsrc"]:
                out += edges_shell_src(code, path_dir, _depth + 1)
        st["pysrc"], st["shsrc"] = [], []
        i += 1
    return out


def resolve_dir(d):
    d = d.strip("\"'")
    for k, v in (("$WC_ROOT", WC), ("${WC_ROOT}", WC), ("$ROOT", MIKE), ("$HOME", os.path.expanduser("~"))):
        d = d.replace(k, v)
    if "$" in d:
        return None
    d = os.path.realpath(os.path.expanduser(d))
    return d if os.path.isdir(d) else None


def file_edges(path):
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    d = os.path.dirname(path)
    if path.endswith(".py"):
        return edges_python_src(src, d)
    return edges_shell_src(src, d)


_EDGE_CACHE = {}


def cached_edges(path):
    if path not in _EDGE_CACHE:
        _EDGE_CACHE[path] = file_edges(path)
    return _EDGE_CACHE[path]


def command_edges(cmd):
    """Edges từ 1 dòng lệnh gốc (cron/unit/hook)."""
    return edges_shell_src(cmd, WC)


# ---------------------------------------------------------------- gốc
def strip_sh_comment(line):
    """Bỏ comment cuối 1 dòng lệnh cron, giữ nguyên ngoặc (lệnh còn được quét lại bởi edges_shell_src)."""
    q = None
    for i, ch in enumerate(line):
        if q:
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
        elif ch == "#" and i > 0 and line[i - 1] in " \t;":
            return line[:i]
    return line


def cron_roots(crontab_text):
    roots = []
    for line in crontab_text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or re.match(r"^[A-Za-z_]\w*=", s):
            continue
        if s.startswith("@"):
            sched, cmd = s.split(None, 1)
        else:
            f = s.split(None, 5)
            if len(f) < 6:
                continue
            sched, cmd = " ".join(f[:5]), f[5]
        cmd = strip_sh_comment(cmd).strip()
        roots.append({"kind": "cron", "schedule": sched, "command": cmd})
    return roots


def unit_roots():
    try:
        r = subprocess.run(["systemctl", "--user", "list-units", "mike*", "ccdb*", "paseo*",
                            "--all", "--no-legend", "--plain", "--no-pager"],
                           capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    roots = []
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        unit = line.split()[0]
        ex = subprocess.run(["systemctl", "--user", "show", "-p", "ExecStart", "--value", unit],
                            capture_output=True, text=True, timeout=20).stdout
        m = re.search(r"argv\[\]=([^;]*)", ex)
        cmd = (m.group(1) if m else ex).strip()
        roots.append({"kind": "unit", "schedule": unit, "command": cmd})
    return roots


def hook_roots():
    roots, seen = [], set()
    files = sorted(glob.glob(os.path.join(WC, ".claude", "settings*.json"))
                   + glob.glob(os.path.join(MIKE, ".claude", "settings*.json"))
                   + glob.glob(os.path.join(MIKE, "agents", "*", ".claude", "settings*.json")))
    for fp in files:
        # settings.local.json KHÔNG track git nhưng Claude Code vẫn nạp hook từ nó => đọc thẳng
        if any(EXCLUDE_PART.match(part) for part in rel(fp).split(os.sep)[:-1]):
            continue
        try:
            hooks = json.load(open(fp)).get("hooks", {})
        except (OSError, ValueError):
            continue
        for ev, groups in sorted(hooks.items()):
            for g in groups:
                for h in g.get("hooks", []):
                    cmd = h.get("command", "")
                    # gộp hook giống nhau chỉ khác tham số agent id
                    key = (ev, re.sub(r"\s+\w+$", "", cmd))
                    if key in seen:
                        continue
                    seen.add(key)
                    roots.append({"kind": "hook", "schedule": ev, "command": key[1]})
    return roots


def root_label(r):
    return f"{r['kind']} `{r['schedule']}` {root_script(r)}"


def root_script(r):
    if r["kind"] == "unit":
        return "unit:" + r["schedule"]
    toks = [os.path.basename(t.strip("\"'")) for t in PATH_TOKEN.findall(r["command"])]
    if r["command"].lstrip().startswith("pkill"):
        return "pkill"
    toks = [t for t in toks if t not in WRAPPERS and t != "wc_env.sh"]
    if toks:
        return toks[-1] if len(toks) > 1 and "for_each_live_account.sh" in r["command"] else toks[0]
    return r["command"].split()[0] if r["command"] else "?"


# ---------------------------------------------------------------- build
TIER_ORDER = {"T0": 0, "T1": 1, "T2": 2, "T?": 9, "T3": 3}


def build(crontab_text):
    roots = cron_roots(crontab_text)
    units = unit_roots()
    roots += units or []
    roots += hook_roots()

    for r in roots:
        r["script"] = root_script(r)
        r["tier"] = ROOT_TIER.get(r["script"], "T?")
        r["label"] = root_label(r)
        r["start"] = command_edges(r["command"])
        r["in_repo_files"] = sorted({rel(f) for f, _ in r["start"]})
    # Entry script của MỖI gốc = rào: gốc khác đi tới nó thì KHÔNG thêm nó vào bao đóng của mình —
    # file đó (và bao đóng của nó) lấy tầng từ CHÍNH gốc của nó. Đo 2026-09-13: run_bot.sh -> ops_autofix.sh -> ops_health_check.sh
    # -> wags_autofix.sh …, run_bot.sh -> consolidate.sh là cạnh THẬT (gọi khi lỗi/sau việc) nhưng
    # kéo toàn bộ fleet-ops lên T0 nếu tính blast radius thuần. Blast radius vẫn ghi ở `blast_tier`.
    entries = {f for r in roots for f, _ in r["start"]
               if os.path.basename(f) == r["script"] and os.path.basename(f) not in WRAPPERS}

    def walk(r, barrier):
        own = {f for f, _ in r["start"]}
        seen = {}
        q = deque()
        for f, kind in r["start"]:
            if f not in seen:
                seen[f] = (0, kind, "(root)")
                q.append(f)
        while q:
            f = q.popleft()
            if barrier and rel(f) in DISPATCH_BARRIER and r["tier"] != T2:
                continue  # bàn giao cho agent — không kế thừa tầng người gọi (xem DISPATCH_BARRIER)
            d = seen[f][0]
            for g, k in cached_edges(f):
                if barrier and g in entries and g not in own:
                    continue  # entry của gốc khác: nó (và bao đóng) lấy tầng từ chính gốc của nó
                if g != f and g not in seen:
                    seen[g] = (d + 1, k, rel(f))
                    q.append(g)
        return seen

    files = {}  # abs -> {depth, tier, via, parent, roots:set, blast_tier}
    for r in roots:
        for f in walk(r, barrier=False):
            e = files.setdefault(f, {"depth": None, "via": None, "parent": None, "roots": set(),
                                     "tier": "T?", "blast_tier": r["tier"]})
            if TIER_ORDER[r["tier"]] < TIER_ORDER[e["blast_tier"]]:
                e["blast_tier"] = r["tier"]
    for r in roots:
        for f, (d, k, par) in walk(r, barrier=True).items():
            e = files[f]
            if e["depth"] is None or d < e["depth"]:
                e.update(depth=d, via=k, parent=par)
            if not e["roots"] or TIER_ORDER[r["tier"]] < TIER_ORDER[e["tier"]]:
                e.update(tier=r["tier"], tier_root=r["label"], tier_parent=par)
            e["roots"].add(r["label"])
    for f, e in files.items():  # chỉ với tới qua rào (không gốc nào đi thẳng tới) -> tầng blast
        if not e["roots"]:
            e.update(tier=e["blast_tier"], via="via-barrier", parent="?")

    root_untracked = sorted(UNTRACKED_HITS)  # chụp TRƯỚC khi quét ứng viên T3 (glob gồm cả WIP)
    # T3: selfcheck không với tới từ gốc, import/exec trực tiếp file T0-T2
    reached = set(files)
    cands = set()
    for pat in ("*selfcheck*.py", "*selfcheck*.sh"):
        cands.update(glob.glob(os.path.join(WC, pat)))
        cands.update(glob.glob(os.path.join(MIKE, "bin", pat)))
        cands.update(glob.glob(os.path.join(MIKE, "agents", "*", pat)))
        cands.update(glob.glob(os.path.join(WC, "trading_bot", pat)))
    for c in sorted(cands):
        c = os.path.realpath(c)
        if c in reached or not in_scope(c):
            continue
        tgts = sorted({rel(g) for g, _ in cached_edges(c) if g in reached and g != c})
        if tgts:
            files[c] = {"depth": None, "via": "selfcheck", "parent": tgts[0], "roots": set(), "blast_tier": "T3",
                        "tier": "T3", "covers": tgts}

    out_files = {}
    for f, e in sorted(files.items(), key=lambda kv: rel(kv[0])):
        d = {"tier": e["tier"], "blast_tier": e.get("blast_tier", e["tier"]), "depth": e["depth"],
             "tier_root": e.get("tier_root"), "tier_parent": e.get("tier_parent"), "via": e["via"], "parent": e["parent"],
             "roots": sorted(e["roots"])}
        if "covers" in e:
            d["covers"] = e["covers"]
        out_files[rel(f)] = d
    out_roots = [{k: r[k] for k in ("kind", "schedule", "script", "tier", "in_repo_files")}
                 | {"command": r["command"][:240]} for r in roots]
    return {
        "generated_by": REGEN_CMD,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "units_status": "ok" if units is not None else "unavailable",
        "exclusions": ["mike_paseo/", "wt-*/ (mọi worktree)", ".claude/worktrees/", "venv/__pycache__/node_modules"],
        "roots": out_roots,
        "files": out_files,
        # tham khảo, KHÔNG diff: file có thật được tham chiếu TỪ BAO ĐÓNG GỐC nhưng chưa track git
        "untracked_refs": root_untracked,
    }


def render_md(m):
    files = m["files"]
    cnt = {t: sum(1 for v in files.values() if v["tier"] == t) for t in ("T0", "T1", "T2", "T3", "T?")}
    L = [
        "---", "kind: reference", "title: Production manifest ARIA — tự sinh, ĐỪNG sửa tay",
        f"generated_by: {m['generated_by']}", f"generated_at: {m['generated_at']}", "---", "",
        "# Production manifest (auto-generated — sửa `mike/bin/production_manifest.py`, không sửa file này)", "",
        f"Tái sinh: `cd /home/trido/thanhdt/WorkingClaude && {m['generated_by']}` · Kiểm drift: "
        "`bash mike/bin/production_manifest_selfcheck.sh` (lệch bản commit = FAIL).", "",
        f"**{len(files)} file** — T0 money-path **{cnt['T0']}** · T1 dữ liệu/regime/paper **{cnt['T1']}** · "
        f"T2 fleet-ops **{cnt['T2']}** · T3 selfcheck **{cnt['T3']}**"
        + (f" · ⚠️ CHƯA PHÂN LOẠI **{cnt['T?']}**" if cnt["T?"] else "")
        + f" · gốc: {len(m['roots'])} (systemd: {m['units_status']}).", "",
        "Phương pháp: gốc = `crontab -l` + systemd user units + hook `.claude/settings*.json`; đóng bao "
        "AST import + tham chiếu exec `*.py|*.sh` resolve ra file có thật, lặp tới điểm bất động. "
        "Tầng = nhỏ nhất theo các gốc với tới, KHÔNG đi xuyên entry script của gốc khác (và dispatch.sh "
        "với gốc ngoài T2) — tầng blast radius thuần nằm ở `blast_tier` trong JSON. T3 = selfcheck ngoài bao đóng import/exec "
        "trực tiếp file T0–T2. Loại trừ: " + ", ".join(m["exclusions"]) + ".", "",
        "**Giới hạn (không thấy được cơ học):** script do agent tự chọn khi được dispatch, kể cả script "
        "được NÊU TÊN trong prompt gửi agent (vd kb_nightly.sh bảo agent chạy data_registry_audit.sh, "
        "daily_retro.sh bảo chạy wakeup_audit.py); lệnh nằm trong chuỗi có khoảng trắng không phải "
        "`bash -c`/`python3 -c`; đường dẫn ghép từ biến runtime; `importlib.import_module`; import trong "
        "hàm tự-kiểm nội tuyến (`def _selfcheck`) CỐ Ý bỏ; file chưa track git CỐ Ý bỏ (liệt kê ở "
        "`untracked_refs` trong JSON); file config/dữ liệu (.json). Cạnh `ref` = đường dẫn trong mảng bash.", "",
        "**Chủ sở hữu + nhịp:** Wags. Lệch = FAIL của `production_manifest_selfcheck.sh` trong "
        "`run_selfchecks.sh` ⇒ `weekly_ops_audit.sh` thấy MỖI TUẦN (bộ dò đỏ hằng ngày chỉ báo 1 lần/file "
        "vì `known_red`). Thay đổi cố ý (thêm/đổi cron, import mới) ⇒ tái sinh + commit cùng lúc. File không có ở đây "
        "KHÔNG chắc chắn là research — manifest là cận dưới của production.", "",
        "| path | tầng | depth | cách vào | gốc quyết định tầng (+ số gốc khác) |", "|---|---|---|---|---|",
    ]
    for t in ("T0", "T1", "T2", "T?", "T3"):
        for p, v in files.items():
            if v["tier"] != t:
                continue
            rs = v["roots"]
            rtxt = (v.get("tier_root") or (rs[0] if rs else "")) + (f" (+{len(rs) - 1})" if len(rs) > 1 else "")
            if t == "T3":
                rtxt = "phủ: " + ", ".join(v["covers"][:2]) + (f" (+{len(v['covers']) - 2})" if len(v["covers"]) > 2 else "")
            dep = "-" if v["depth"] is None else str(v["depth"])
            L.append(f"| `{p}` | {t} | {dep} | {v['via']} | {rtxt.replace('|', '/')} |")
    L += ["", "## Gốc", "", "| loại | lịch/sự kiện/unit | script | tầng | file trong repo |", "|---|---|---|---|---|"]
    for r in m["roots"]:
        L.append(f"| {r['kind']} | `{r['schedule']}` | {r['script']} | {r['tier']} | "
                 f"{', '.join('`%s`' % x for x in r['in_repo_files']) or '(ngoài repo / không file)'} |")
    return "\n".join(L) + "\n"


def diff_manifests(old, new):
    """Danh sách dòng lệch (rỗng = khớp). So membership + tầng file và (kind, lịch, script, tầng) gốc;
    bỏ qua generated_at/depth/parent (đổi thứ tự duyệt không phải drift). Gốc systemd chỉ so khi
    CẢ HAI bản đọc được systemd (cron/headless không có D-Bus user session)."""
    out = []
    of, nf = old.get("files", {}), new.get("files", {})
    for p in sorted(set(nf) - set(of)):
        w = "WARN " if nf[p]["tier"] == "T3" else ""
        out.append(f"{w}+ {p} [{nf[p]['tier']}] (mới vào production, từ {nf[p]['parent']})")
    for p in sorted(set(of) - set(nf)):
        w = "WARN " if of[p]["tier"] == "T3" else ""
        out.append(f"{w}- {p} [{of[p]['tier']}] (rời production)")
    for p in sorted(set(of) & set(nf)):
        if of[p]["tier"] != nf[p]["tier"]:  # kể cả T3 <-> T0-T2: đổi vai trò thật, vẫn FAIL
            out.append(f"~ {p} tầng {of[p]['tier']} -> {nf[p]['tier']}")
    units_ok = old.get("units_status") == "ok" and new.get("units_status") == "ok"
    key = lambda r: (r["kind"], r["schedule"], r["script"], r["tier"])
    ro = {key(r) for r in old.get("roots", []) if units_ok or r["kind"] != "unit"}
    rn = {key(r) for r in new.get("roots", []) if units_ok or r["kind"] != "unit"}
    for k in sorted(rn - ro):
        out.append(f"+ gốc {k}")
    for k in sorted(ro - rn):
        out.append(f"- gốc {k}")
    for p, v in sorted(nf.items()):
        if v["tier"] == "T?":
            out.append(f"? {p} thuộc gốc CHƯA PHÂN LOẠI — thêm script gốc vào ROOT_TIER")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crontab", help="đọc crontab từ file thay vì `crontab -l`")
    ap.add_argument("--stdout-json", action="store_true")
    ap.add_argument("--check", metavar="COMMITTED_JSON",
                    help="tái sinh rồi so với bản manifest cho trước; lệch => in diff, exit 1")
    a = ap.parse_args()
    if a.crontab:
        text = open(a.crontab).read()
    else:
        text = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=True).stdout
    m = build(text)
    if a.check:
        alld = diff_manifests(json.load(open(a.check, encoding="utf-8")), m)
        d = [x for x in alld if not x.startswith("WARN ")]
        warns = [x for x in alld if x.startswith("WARN ")]
        if warns:
            # T3 (selfcheck) thêm/bớt gần như mỗi ngày — chỉ nhắc, không FAIL (arch-review vòng 2 N3)
            print(f"WARN {len(warns)} selfcheck T3 vào/rời — tái sinh khi tiện:")
            print("\n".join(warns[:30]))
        if d:
            print(f"DRIFT {len(d)} dòng — manifest commit lệch thực tế. Nếu thay đổi là CỐ Ý: chạy "
                  f"`{REGEN_CMD}` rồi commit kb/production_manifest.{{json,md}}.")
            print("\n".join(d[:80]))
            sys.exit(1)
        print(f"OK manifest khớp ({len(m['files'])} file, units={m['units_status']})")
        return
    if a.stdout_json:
        json.dump(m, sys.stdout, ensure_ascii=False, indent=1, sort_keys=True)
        print()
        return
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(m))
    t = {k: sum(1 for v in m["files"].values() if v["tier"] == k) for k in ("T0", "T1", "T2", "T3", "T?")}
    print(f"OK {len(m['files'])} file {t} roots={len(m['roots'])} units={m['units_status']} -> {rel(OUT_JSON)}, {rel(OUT_MD)}")


if __name__ == "__main__":
    main()
