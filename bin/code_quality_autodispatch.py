#!/usr/bin/env python3
"""Tầng 3 auto-dispatch cho code_quality_weekly.sh (user chốt 2026-09-17, xem
kb/projects/code-quality-review-plan-20260823.md § CẬP NHẬT 2026-09-17).

Đọc findings đã verify (JSON của code_quality_weekly.sh), phân nhóm:
  - ESCALATE: finding chạm file "hot-core tiền thật" — MỌI severity escalate (không tin severity
    LLM tự khai làm cổng cho code chạm tiền thật/NAV sống — arch-review round 2 bác bỏ việc tách
    riêng 1 tầng "NAV-scale chỉ escalate medium/high", vì boundary gốc trong MIKE.md/current_ops.md
    ("KHÔNG tự sửa logic đặt lệnh") không hề có ngoại lệ theo severity):
      - mọi path dưới thư mục `trading_bot/` (prefix, không phải liệt kê tên file — tránh trôi
        mỗi lần thêm module mới, đúng góp ý arch-review round 2)
      - `bot_execute.py`, `dnse_api.py` (gọi place_order/ppse trực tiếp)
      - `mike/bin/run_bot.sh`, `mike/bin/compute_jit_unpark.py`,
        `mike/bin/discretionary_margin_gate.py`, `mike/bin/compute_active_nav.py`,
        `mike/bin/daily_nav_snapshot.py`
    HOẶC owner không phải Taylor/Wags (rỗng/"Mike"/lạ) — fail-safe khi không rõ owner.
    KHÔNG dispatch — ghi bus question + ack `triaged-needs-human:` (khỏi bị wags_autofix đốt
    job vô ích, xem arch-review round 1 "Long-term ops") + Discord.
  - Taylor / Wags: dispatch --bg với prompt build từ chính finding (surgical, ràng buộc ranh
    giới cứng + kỷ luật git add, selfcheck theo phạm vi, arch-reviewer/quant-skeptic bắt buộc).
    `--write-scope` truyền theo đường dẫn REPO-RELATIVE (so với WC_ROOT) — arch-review round 2:
    truyền path TUYỆT ĐỐI làm vô hiệu cả job-write-scope-conflict lẫn commit-collision-gate vì
    toàn fleet khai write-scope theo dạng tương đối.

Bài học 2026-09-17 (lượt dispatch tay đầu tiên, xem plan doc): script này CHÍNH LÀ nơi duy nhất
tự động dispatch cho 1 báo cáo — không có tác nhân nào khác chạy song song cho cùng report_date,
nên không cần grep bus tìm "đã có ai fix chưa" (khác tình huống Mike dispatch TAY cho báo cáo cũ).

State file (`state/code_quality_weekly_dispatch_<date>.json`) ghi NGUYÊN TỬ (tmp+os.replace)
NGAY sau mỗi side-effect thành công (escalation, mỗi dispatch) — không gom cuối. Rerun (cron
chạy lại tay, hoặc lần trước chết giữa chừng) chỉ làm lại phần CHƯA thành công — cơ chế này CHỈ có
ý nghĩa nếu `--verified` trỏ tới 1 file BỀN (`code_quality_weekly.sh` giờ copy `verified.json` ra
`reports/code_quality/verified_<date>.json` thay vì để trong `mktemp -d` bị `trap rm -rf EXIT` xoá
— arch-review round 2 killer objection: bản v2 tự nhận "sẽ thử lại lần sau" trong khi input đã bị
xoá, không có "lần sau" nào đọc lại được). Dispatch/escalation fail ở lần chạy đầu ⇒ Discord in
sẵn lệnh rerun tay trỏ đúng file bền đó, KHÔNG tự nhận sẽ tự động thử lại.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent  # mike/
WC_ROOT_DEFAULT = ROOT.parent  # WorkingClaude/
ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# Hot-core tiền thật — MỌI severity escalate (arch-review round 2: severity là nhãn LLM tự khai,
# không đủ tin làm cổng cho code chạm tiền thật; boundary gốc MIKE.md không phân biệt severity).
EXEC_HARD_BOUNDARY_PREFIXES = ("trading_bot/",)  # mọi file dưới thư mục này, không liệt kê tên
EXEC_HARD_BOUNDARY_EXACT = (
    "bot_execute.py",
    "dnse_api.py",
    "mike/bin/run_bot.sh",
    "mike/bin/compute_jit_unpark.py",
    "mike/bin/discretionary_margin_gate.py",
    "mike/bin/compute_active_nav.py",
    "mike/bin/daily_nav_snapshot.py",
)
VALID_SEVERITIES = {"low", "medium", "high"}


def to_repo_relative(file_abs: str, wc_root: Path) -> str:
    """Chuẩn hoá 1 path (thường tuyệt đối, do code-reviewer trả về) thành repo-relative so với
    WC_ROOT — dùng CẢ cho gate hot-core (prefix "trading_bot/" chỉ đúng khi so với gốc này) LẪN
    cho --write-scope (arch-review round 2: path tuyệt đối làm vô hiệu job-write-scope-conflict +
    commit-collision-gate, cả 2 đều so khớp theo dạng repo-relative). Không resolve được (path
    ngoài WC_ROOT, hoặc lỗi filesystem) ⇒ trả nguyên bản gốc, KHÔNG đoán — caller tự quyết fail-safe."""
    try:
        p = Path(file_abs)
        if p.is_absolute():
            return str(p.relative_to(wc_root)).replace("\\", "/")
    except ValueError:
        pass
    return file_abs.replace("\\", "/")


def now_ict_iso() -> str:
    return datetime.now(ICT).isoformat()


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def sanitize_findings(raw: list) -> tuple[list[dict], list[dict]]:
    """Tách finding HỢP LỆ khỏi finding hỏng schema (thiếu/sai kiểu 'file'/'severity') — finding
    hỏng KHÔNG được vào classify() bình thường, phải escalate với lý do rõ ràng (fail-safe thay
    vì crash — arch-review round 1: `None` trong 'file' làm sorted() ném TypeError SAU khi đã
    post escalation cho các finding khác, bus question trùng lặp ở lần rerun)."""
    ok, invalid = [], []
    for f in raw:
        if not isinstance(f, dict):
            invalid.append({"_raw": repr(f)[:200], "_escalate_reason": "finding_khong_phai_object"})
            continue
        file_ = f.get("file")
        severity = str(f.get("severity") or "").strip().lower()
        if not isinstance(file_, str) or not file_.strip():
            invalid.append({**f, "_escalate_reason": "thieu_hoac_sai_kieu_field_file"})
            continue
        if severity not in VALID_SEVERITIES:
            invalid.append({**f, "_escalate_reason": f"severity_khong_hop_le:{f.get('severity')!r}"})
            continue
        # Ghi lại severity ĐÃ chuẩn hoá (strip+lower) vào chính finding — arch-review round 2:
        # sanitize dùng .strip().lower() để validate nhưng classify() trước đây chỉ .lower() để so
        # sánh ⇒ " medium " (khoảng trắng thừa) qua được validate nhưng KHÔNG khớp so sánh, dispatch
        # thay vì escalate. Chuẩn hoá 1 lần duy nhất ở đây, các nơi khác chỉ đọc lại.
        ok.append({**f, "severity": severity})
    return ok, invalid


def classify(findings: list[dict], wc_root: Path) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {"escalate": [], "taylor": [], "wags": []}
    for f in findings:
        rel = to_repo_relative(str(f.get("file") or ""), wc_root)
        owner = str(f.get("owner") or "").strip().lower()
        is_exec_hard = rel.startswith(EXEC_HARD_BOUNDARY_PREFIXES) or rel in EXEC_HARD_BOUNDARY_EXACT
        if is_exec_hard:
            groups["escalate"].append({**f, "_escalate_reason": "hard_boundary_tien_that", "_rel": rel})
        elif owner == "taylor":
            groups["taylor"].append({**f, "_rel": rel})
        elif owner == "wags":
            groups["wags"].append({**f, "_rel": rel})
        else:
            groups["escalate"].append(
                {**f, "_escalate_reason": f"owner_khong_ro_hoac_khong_phai_taylor_wags:{owner or '(rỗng)'}", "_rel": rel}
            )
    return groups


def _finding_block(f: dict) -> str:
    lines = [
        f"### {f.get('file')}:{f.get('line', 0)} — {f.get('category')} ({f.get('severity')})",
        f"- {f.get('summary', '')}",
        f"- Bằng chứng: {f.get('evidence', '')}",
    ]
    if f.get("suggested_fix"):
        lines.append(f"- Hướng sửa đề xuất (từ code-reviewer, tự xác minh lại trước khi áp): {f.get('suggested_fix')}")
    if f.get("verified"):
        lines.append("- Đã qua verify độc lập: sống sót phản biện.")
    return "\n".join(lines)


def build_prompt(owner: str, findings: list[dict], report_date: str, report_file: str, escalate_files: set[str]) -> str:
    n = len(findings)
    blocks = "\n\n".join(_finding_block(f) for f in findings)
    no_touch = ""
    same_file_escalate = sorted(escalate_files & {f.get("file") for f in findings})
    if same_file_escalate:
        no_touch = (
            "\n\n⚠️ CÙNG FILE có finding khác đang ESCALATE (chờ user/Mike quyết, KHÔNG thuộc việc này): "
            + ", ".join(same_file_escalate)
            + " — ĐỪNG động vào vùng của những finding đó, chỉ sửa đúng dòng được liệt dưới đây."
        )
    return f"""Xử lý {n} finding sau từ báo cáo code-quality-weekly tự động `{report_file}` ({report_date}),
owner đề xuất: {owner}. Đây là dispatch TỰ ĐỘNG KHÔNG GIÁM SÁT TRỰC TIẾP từ cron
`code_quality_weekly.sh` (Tầng 3 auto-dispatch, user chốt 2026-09-17, xem
kb/projects/code-quality-review-plan-20260823.md).

⚠️ RANH GIỚI CỨNG (đọc trước khi làm gì khác — vi phạm mục này nghiêm trọng hơn finding gốc):
TUYỆT ĐỐI KHÔNG đụng vào trade plan, trading_rules.json, logic đặt lệnh, dòng cron thực thi,
xoá dữ liệu, hay bất kỳ gì ngoài đúng finding được liệt dưới đây — nếu trong lúc sửa thấy CẦN
đổi thứ thuộc nhóm đó để fix cho đúng, DỪNG LẠI và ghi vào tổng kết là "cần escalate", đừng tự ý
mở rộng phạm vi.

⚠️ KỶ LUẬT GIT (bắt buộc — đây là dispatch DUY NHẤT bắn 2 agent [Taylor+Wags] vào CÙNG repo gần
như CÙNG LÚC): `git status` TRƯỚC `git add`; CHỈ `git add` đúng (các) file bạn thực sự sửa theo
danh sách dưới; TUYỆT ĐỐI KHÔNG `git add -A` / `git add .` (rủi ro commit nhầm thay đổi của
agent kia đang chạy song song).

Sửa SURGICAL từng finding RIÊNG (coding_guidelines §2/§3 — không refactor thêm ngoài finding đã nêu).
Sau mỗi fix chạy selfcheck THEO PHẠM VI file đã đổi (§23, `bin/selfcheck_scope_map.sh` + `grep -rl`).
`mike/bin/*` LUÔN cần Agent(subagent_type="arch-reviewer") xác nhận trước khi coi là xong (bảng owner
§6 của plan). `trading_bot/*`/`bot_execute.py` cũng LUÔN cần arch-reviewer, thêm quant-skeptic nếu
finding đổi sizing/tín hiệu/công thức NAV.{no_touch}

Danh sách finding:

{blocks}

Nếu 1 finding hoá ra ĐÃ được fix từ trước (kiểm bằng `git log -- <file>` trước khi sửa, bài học
2026-09-17: đừng giả định báo cáo còn đúng với code hiện tại) — ghi rõ trong tổng kết, đừng sửa lại.
Sau khi xong (hoặc dừng ở finding nào vì lý do chính đáng), ghi 1 bus finding tổng kết (fixed/skip+lý
do/arch-reviewer verdict/commit hash) topic `cq-{report_date}-{owner.lower()}-autodispatch`, và post 1
tin tóm tắt vào Discord topic `architecture` (dùng `bin/notify_thread.sh "<nội dung>" architecture`)."""


def dispatch(dispatch_bin: Path, owner: str, prompt: str, thread_id: str | None,
             write_scope: str, timeout: int, dry_run: bool) -> dict:
    cmd = [str(dispatch_bin), owner, prompt, "--bg", "--effort", "high", "--timeout", str(timeout)]
    if thread_id:
        cmd += ["--thread", thread_id]
    if write_scope:
        cmd += ["--write-scope", write_scope]
    if dry_run:
        # cmd[2] LÀ prompt — cmd[:3] trước đây vô tình giữ nguyên prompt thật (dù ghi "omitted")
        # VÀ làm rơi "--bg" (cmd[3]) khỏi preview (arch-review round 2). cmd[:2] = [dispatch_bin,
        # owner]; cmd[3:] bắt đầu đúng từ "--bg" trở đi.
        return {"owner": owner, "dry_run": True, "cmd_preview": cmd[:2] + ["<prompt omitted, len=%d>" % len(prompt)] + cmd[3:]}
    try:
        # stderr=STDOUT: dispatch.sh in dòng "JOB <id> ..." ra STDERR (bin/dispatch.sh:1154) —
        # gộp luồng để parse job_id không phụ thuộc dispatch.sh đổi stream nào (arch-review round 1
        # killer objection: parse chỉ từ stdout khiến job_id LUÔN None kể cả khi dispatch THÀNH CÔNG).
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            cwd=str(ROOT), timeout=90,
        )
        combined = proc.stdout or ""
        returncode = proc.returncode
    except subprocess.TimeoutExpired as e:
        combined = (e.stdout or "") + "\n[TIMEOUT sau 90s chờ dispatch.sh --bg trả job_id — bất thường, dispatch.sh --bg phải return ngay]"
        returncode = -1
    job_id = None
    m = re.search(r"JOB (\S+)", combined)
    if m:
        job_id = m.group(1)
    return {
        "owner": owner,
        "returncode": returncode,
        "job_id": job_id,
        "output_tail": combined[-1200:],
    }


def post_escalation(root: Path, findings: list[dict], report_date: str, report_file: str,
                     dry_run: bool, arch_thread: str | None) -> bool:
    """True nếu post thành công (hoặc dry-run) — caller chỉ ghi state khi True."""
    if not findings:
        return True
    payload = {
        "report": report_file,
        "n_escalated": len(findings),
        "findings": [
            {
                "file": f.get("file"), "line": f.get("line"), "category": f.get("category"),
                "severity": f.get("severity"), "summary": f.get("summary"),
                "reason": f.get("_escalate_reason"),
            }
            for f in findings
        ],
        "owner_hint": "Mike",
    }
    payload_json = json.dumps(payload, ensure_ascii=False)
    topic = f"cq-{report_date}-hard-boundary"
    if dry_run:
        print(f"[dry-run] would append_event.sh code-reviewer question '{topic}' with {len(findings)} finding(s)")
        print(f"[dry-run] would ack '{topic}' with triaged-needs-human: (suppress_days=14)")
    else:
        rc1 = subprocess.run(
            [str(root / "bin" / "append_event.sh"), "code-reviewer", "question", topic, payload_json],
            check=False, cwd=str(root),
        ).returncode
        # Ack NGAY bằng chính pipeline này — ranh giới cứng là CHỦ Ý (không phải anomaly chưa ai
        # xem), Wags cấu trúc KHÔNG có quyền quyết tiền thật nên để ops_health_check tự đốt
        # wags_autofix 2 lần/ngày cho topic này là vòng lặp vô ích (arch-review round 1). Trần
        # suppress 14 ngày (ACK_MAX_SUPPRESS_DAYS, ops_health_check.sh) — vẫn hiện trong báo cáo
        # sức khỏe, chỉ tắt auto-dispatch wags_autofix.
        ack_payload = json.dumps({"suppress_days": 14, "auto_ack_by": "code_quality_autodispatch.py"}, ensure_ascii=False)
        rc2 = subprocess.run(
            [str(root / "bin" / "append_event.sh"), "code-reviewer", "status", f"triaged-needs-human: {topic}", ack_payload],
            check=False, cwd=str(root),
        ).returncode
        if rc1 != 0 or rc2 != 0:
            return False
    msg_lines = [f"**Code review auto-dispatch ({report_date}) — {len(findings)} finding CẦN NGƯỜI QUYẾT, KHÔNG tự dispatch:**", ""]
    for f in findings:
        msg_lines.append(f"- `{f.get('file')}:{f.get('line', 0)}` ({f.get('severity')}, {f.get('_escalate_reason')}): {f.get('summary', '')[:200]}")
    msg_lines.append("")
    msg_lines.append(f"Chi tiết đầy đủ: `{report_file}`. Bus question: `{topic}` (đã ack triaged-needs-human, không đốt wags_autofix).")
    msg = "\n".join(msg_lines)
    if dry_run:
        print(f"[dry-run] would notify_thread.sh to '{arch_thread or 'architecture'}':\n{msg}")
        return True
    subprocess.run(
        [str(root / "bin" / "notify_thread.sh"), msg, arch_thread or "architecture"],
        check=False, cwd=str(root),
    )
    return True


def notify_failure(root: Path, arch_thread: str | None, err: str, dry_run: bool) -> None:
    msg = f"🔴 **code_quality_autodispatch.py CRASH** — bước Tầng 3 auto-dispatch KHÔNG chạy được tuần này, cần kiểm tay:\n```\n{err[-1500:]}\n```"
    if dry_run:
        print(f"[dry-run] would notify failure:\n{msg}")
        return
    subprocess.run(
        [str(root / "bin" / "notify_thread.sh"), msg, arch_thread or "architecture"],
        check=False, cwd=str(root),
    )


def run(args) -> dict:
    root = Path(args.root)
    wc_root = Path(args.wc_root) if args.wc_root else WC_ROOT_DEFAULT
    dispatch_bin = Path(args.dispatch_bin) if args.dispatch_bin else root / "bin" / "dispatch.sh"
    state_file = Path(args.state_file) if args.state_file else root / "state" / f"code_quality_weekly_dispatch_{args.date}.json"
    rerun_cmd = (f"python3 {root}/bin/code_quality_autodispatch.py --verified {args.verified} "
                 f"--date {args.date} --report-file {args.report_file}")

    state: dict = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            state = {}

    data = json.loads(Path(args.verified).read_text(encoding="utf-8"))
    raw_findings = data.get("findings", [])
    if not raw_findings:
        return {"n_escalate": 0, "n_taylor": 0, "n_wags": 0, "note": "0 finding, không có gì để dispatch"}

    valid, invalid = sanitize_findings(raw_findings)
    groups = classify(valid, wc_root)
    escalate = groups["escalate"] + invalid
    taylor_f, wags_f = groups["taylor"], groups["wags"]
    escalate_files_rel = {f.get("_rel") for f in escalate if f.get("_rel")}

    # Toàn bộ nhóm ĐÃ xong ở state trước đó (rerun đúng nghĩa duplicate) ⇒ skip sạch, không đụng gì.
    need_escalate = bool(escalate) and not state.get("escalate", {}).get("posted")
    need_taylor = bool(taylor_f) and "taylor" not in state
    need_wags = bool(wags_f) and "wags" not in state
    if not (need_escalate or need_taylor or need_wags):
        return {"skipped": True, "reason": "state_file_da_du_moi_nhom", "previous": state}

    escalate_failed = False
    if need_escalate:
        ok = post_escalation(root, escalate, args.date, args.report_file, args.dry_run, args.arch_thread)
        if ok and not args.dry_run:
            state["escalate"] = {"posted": True, "n": len(escalate), "at": now_ict_iso()}
            atomic_write_json(state_file, state)
        elif not ok:
            # arch-review round 2: post_escalation() trả False TRƯỚC khi return False im lặng —
            # đây LÀ nhóm quan trọng nhất (finding chạm tiền thật). Phải nổ chuông riêng, không
            # để main() trả rc=0 như trước.
            escalate_failed = True
            notify_failure(
                root, args.arch_thread,
                f"post_escalation() THẤT BẠI cho {len(escalate)} finding hard-boundary "
                f"({args.date}) — append_event.sh lỗi, bus question KHÔNG được ghi. Rerun tay:\n{rerun_cmd}",
                args.dry_run,
            )

    results: dict[str, dict] = {}
    for key, owner, flist, need in (("taylor", "Taylor", taylor_f, need_taylor), ("wags", "Wags", wags_f, need_wags)):
        if not need:
            if key in state:
                results[owner] = {**state[key], "skipped_already_done": True}
            continue
        prompt = build_prompt(owner, flist, args.date, args.report_file, escalate_files_rel)
        write_scope = ",".join(sorted({f.get("_rel", "") for f in flist if f.get("_rel")}))
        thread_id = args.arch_thread or "architecture"
        res = dispatch(dispatch_bin, owner, prompt, thread_id, write_scope, args.timeout, args.dry_run)
        res["n_findings"] = len(flist)
        res["write_scope"] = write_scope
        results[owner] = res
        # CHỈ ghi state khi THẬT SỰ thành công (rc==0 và bắt được job_id) — rc≠0/job_id=None để
        # NGUYÊN trong state (không ghi key), rerun kế tiếp (BẰNG TAY, dùng rerun_cmd) sẽ thử lại
        # ĐÚNG nhóm này (arch-review round 1: ghi state vô điều kiện làm rerun bỏ sót finding).
        if not args.dry_run and res.get("returncode") == 0 and res.get("job_id"):
            state[key] = {"job_id": res["job_id"], "n_findings": res["n_findings"], "write_scope": write_scope, "at": now_ict_iso()}
            atomic_write_json(state_file, state)

    summary = {
        "date": args.date,
        "n_escalate": len(escalate),
        "n_taylor": len(taylor_f),
        "n_wags": len(wags_f),
        "escalate_failed": escalate_failed,
        "results": results,
        "generated_at": now_ict_iso(),
    }

    if not args.dry_run:
        dispatch_msg_lines = [f"**Code review auto-dispatch ({args.date})** — báo cáo `{args.report_file}`:"]
        any_fail = escalate_failed
        for owner, res in results.items():
            if res.get("skipped_already_done"):
                dispatch_msg_lines.append(f"- {owner}: đã dispatch xong ở lần chạy trước (job `{res.get('job_id')}`), không lặp lại.")
            elif res.get("job_id") and res.get("returncode") == 0:
                dispatch_msg_lines.append(f"- {owner}: {res['n_findings']} finding, job `{res['job_id']}` (chạy nền, sẽ tự báo).")
            else:
                any_fail = True
                # KHÔNG tự nhận "sẽ thử lại lần sau" (arch-review round 2 killer objection: không
                # có cơ chế thật đứng sau nếu không ai chạy rerun_cmd tay) — in thẳng lệnh rerun.
                dispatch_msg_lines.append(
                    f"- {owner}: {res['n_findings']} finding, DISPATCH LỖI (rc={res.get('returncode')}, job_id={res.get('job_id')}) "
                    f"— CẦN RERUN TAY (input đã lưu bền, không tự động): `{rerun_cmd}`. "
                    f"Chi tiết: {res.get('output_tail', '')[-400:]}"
                )
        if not results and not escalate:
            dispatch_msg_lines.append("- Không có finding nào thuộc Taylor/Wags lượt này (toàn bộ đã escalate).")
        if escalate_failed:
            dispatch_msg_lines.append(f"⚠️ Escalation cho {len(escalate)} finding hard-boundary CŨNG lỗi — xem thông báo CRASH riêng.")
        if any_fail:
            dispatch_msg_lines.insert(0, "⚠️")
        subprocess.run(
            [str(root / "bin" / "notify_thread.sh"), "\n".join(dispatch_msg_lines), args.arch_thread or "architecture"],
            check=False, cwd=str(root),
        )

    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verified", required=True, help="Path tới verified.json (findings đã qua verify)")
    ap.add_argument("--date", required=True, help="Ngày báo cáo YYYY-MM-DD")
    ap.add_argument("--report-file", required=True)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--wc-root", default=None, help="WorkingClaude root (mặc định = parent của --root) — dùng để chuẩn hoá path hot-core + write-scope")
    ap.add_argument("--dispatch-bin", default=None)
    ap.add_argument("--state-file", default=None)
    ap.add_argument("--arch-thread", default=None, help="ID hoặc tên topic Discord cho escalate/dispatch summary (mặc định 'architecture')")
    ap.add_argument("--timeout", type=int, default=5400)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    try:
        summary = run(args)
    except Exception as e:  # noqa: BLE001 — cron unattended: PHẢI báo ra Discord, không chỉ traceback vào log câm
        import traceback
        err = traceback.format_exc()
        root = Path(args.root)
        notify_failure(root, args.arch_thread, f"{type(e).__name__}: {e}\n{err}", args.dry_run)
        print(json.dumps({"crashed": True, "error": str(e)}, ensure_ascii=False))
        return 1

    print(json.dumps(summary, ensure_ascii=False))
    # rc≠0 khi có bất kỳ side-effect quan trọng nào lỗi — code_quality_weekly.sh log WARN thay vì
    # "Auto-dispatch xong" (arch-review round 2: trước đây rc luôn 0 kể cả khi escalation/dispatch
    # thất bại hoàn toàn, không phân biệt được với thành công ở log cron).
    if summary.get("escalate_failed"):
        return 1
    if any(
        not r.get("skipped_already_done") and not (r.get("job_id") and r.get("returncode") == 0)
        for r in summary.get("results", {}).values()
    ):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
