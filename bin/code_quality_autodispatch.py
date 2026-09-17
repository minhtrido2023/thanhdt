#!/usr/bin/env python3
"""Tầng 3 auto-dispatch cho code_quality_weekly.sh (user chốt 2026-09-17, xem
kb/projects/code-quality-review-plan-20260823.md § CẬP NHẬT 2026-09-17).

Đọc findings đã verify (JSON của code_quality_weekly.sh), phân nhóm:
  - ESCALATE: finding chạm file "hot-core tiền thật" (trading_bot/{plan,executor,brokers,
    config,plan_funding_gate}.py, bot_execute.py) VỚI severity medium/high, HOẶC owner không
    phải Taylor/Wags (owner=Mike hoặc thiếu/lạ) — ranh giới cứng MIKE.md "KHÔNG tự sửa logic
    đặt lệnh" + fail-safe khi không rõ owner. KHÔNG dispatch, chỉ ghi bus question + Discord.
  - Taylor / Wags: dispatch --bg với prompt build từ chính finding (surgical, có selfcheck +
    arch-reviewer/quant-skeptic bắt buộc theo bảng owner §6 của plan).

Bài học 2026-09-17 (lượt dispatch tay đầu tiên, xem plan doc): script này CHÍNH LÀ nơi duy nhất
tự động dispatch cho 1 báo cáo — không có tác nhân nào khác chạy song song cho cùng report_date,
nên không cần grep bus tìm "đã có ai fix chưa" (khác tình huống Mike dispatch TAY cho báo cáo cũ).
Guard duy nhất cần: idempotency nếu CHÍNH script này bị chạy 2 lần cùng ngày (state file).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent  # mike/
ICT = ZoneInfo("Asia/Ho_Chi_Minh")

HARD_BOUNDARY_SUFFIXES = (
    "trading_bot/plan.py",
    "trading_bot/executor.py",
    "trading_bot/brokers.py",
    "trading_bot/config.py",
    "trading_bot/plan_funding_gate.py",
    "bot_execute.py",
)


def now_ict_iso() -> str:
    return datetime.now(ICT).isoformat()


def classify(findings: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {"escalate": [], "taylor": [], "wags": []}
    for f in findings:
        file_ = str(f.get("file") or "").replace("\\", "/")
        severity = str(f.get("severity") or "").lower()
        owner = str(f.get("owner") or "").strip().lower()
        is_hard = severity in ("medium", "high") and any(
            file_.endswith(suf) for suf in HARD_BOUNDARY_SUFFIXES
        )
        if is_hard:
            f = {**f, "_escalate_reason": "hard_boundary_order_or_nav_logic"}
            groups["escalate"].append(f)
        elif owner == "taylor":
            groups["taylor"].append(f)
        elif owner == "wags":
            groups["wags"].append(f)
        else:
            f = {**f, "_escalate_reason": f"owner_khong_ro_hoac_khong_phai_taylor_wags:{owner or '(rỗng)'}"}
            groups["escalate"].append(f)
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
owner đề xuất: {owner}. Đây là dispatch TỰ ĐỘNG từ cron `code_quality_weekly.sh` (Tầng 3 auto-dispatch,
user chốt 2026-09-17, xem kb/projects/code-quality-review-plan-20260823.md).

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


def dispatch(dispatch_bin: Path, owner: str, prompt: str, thread_id: str | None, timeout: int, dry_run: bool) -> dict:
    cmd = [str(dispatch_bin), owner, prompt, "--bg", "--effort", "medium", "--timeout", str(timeout)]
    if thread_id:
        cmd += ["--thread", thread_id]
    if dry_run:
        return {"owner": owner, "dry_run": True, "cmd_preview": cmd[:3] + ["<prompt omitted, len=%d>" % len(prompt)] + cmd[4:]}
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    job_id = None
    m = re.search(r"JOB (\S+)", proc.stdout)
    if m:
        job_id = m.group(1)
    return {
        "owner": owner,
        "returncode": proc.returncode,
        "job_id": job_id,
        "stdout_tail": proc.stdout[-800:],
        "stderr_tail": proc.stderr[-800:],
    }


def post_escalation(root: Path, findings: list[dict], report_date: str, report_file: str, dry_run: bool, arch_thread: str | None) -> None:
    if not findings:
        return
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
    else:
        subprocess.run(
            [str(root / "bin" / "append_event.sh"), "code-reviewer", "question", topic, payload_json],
            check=False, cwd=str(root),
        )
    msg_lines = [f"**Code review auto-dispatch ({report_date}) — {len(findings)} finding CẦN NGƯỜI QUYẾT, KHÔNG tự dispatch:**", ""]
    for f in findings:
        msg_lines.append(f"- `{f.get('file')}:{f.get('line', 0)}` ({f.get('severity')}, {f.get('_escalate_reason')}): {f.get('summary', '')[:200]}")
    msg_lines.append("")
    msg_lines.append(f"Chi tiết đầy đủ: `{report_file}`. Bus question: `{topic}`.")
    msg = "\n".join(msg_lines)
    if dry_run:
        print(f"[dry-run] would notify_thread.sh to '{arch_thread or 'architecture'}':\n{msg}")
    else:
        subprocess.run(
            [str(root / "bin" / "notify_thread.sh"), msg, arch_thread or "architecture"],
            check=False, cwd=str(root),
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verified", required=True, help="Path tới verified.json (findings đã qua verify)")
    ap.add_argument("--date", required=True, help="Ngày báo cáo YYYY-MM-DD")
    ap.add_argument("--report-file", required=True)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--dispatch-bin", default=None)
    ap.add_argument("--state-file", default=None)
    ap.add_argument("--arch-thread", default=None, help="ID hoặc tên topic Discord cho escalate/dispatch summary (mặc định 'architecture')")
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    dispatch_bin = Path(args.dispatch_bin) if args.dispatch_bin else root / "bin" / "dispatch.sh"
    state_file = Path(args.state_file) if args.state_file else root / "state" / f"code_quality_weekly_dispatch_{args.date}.json"

    if state_file.exists() and not args.dry_run:
        prev = json.loads(state_file.read_text(encoding="utf-8"))
        print(json.dumps({"skipped": True, "reason": "state_file_exists", "previous": prev}, ensure_ascii=False))
        return 0

    data = json.loads(Path(args.verified).read_text(encoding="utf-8"))
    findings = data.get("findings", [])
    if not findings:
        result = {"n_escalate": 0, "n_taylor": 0, "n_wags": 0, "note": "0 finding, không có gì để dispatch"}
        print(json.dumps(result, ensure_ascii=False))
        return 0

    groups = classify(findings)
    escalate, taylor_f, wags_f = groups["escalate"], groups["taylor"], groups["wags"]
    escalate_files = {f.get("file") for f in escalate}

    post_escalation(root, escalate, args.date, args.report_file, args.dry_run, args.arch_thread)

    results: dict[str, dict] = {}
    for owner, flist in (("Taylor", taylor_f), ("Wags", wags_f)):
        if not flist:
            continue
        prompt = build_prompt(owner, flist, args.date, args.report_file, escalate_files)
        write_scope = ",".join(sorted({f.get("file", "") for f in flist if f.get("file")}))
        thread_id = args.arch_thread or "architecture"
        res = dispatch(dispatch_bin, owner, prompt, thread_id, args.timeout, args.dry_run)
        res["n_findings"] = len(flist)
        res["write_scope"] = write_scope
        results[owner] = res

    summary = {
        "date": args.date,
        "n_escalate": len(escalate),
        "n_taylor": len(taylor_f),
        "n_wags": len(wags_f),
        "results": results,
        "generated_at": now_ict_iso(),
    }
    if not args.dry_run:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        dispatch_msg_lines = [f"**Code review auto-dispatch ({args.date})** — báo cáo `{args.report_file}`:"]
        for owner, res in results.items():
            if res.get("job_id"):
                dispatch_msg_lines.append(f"- {owner}: {res['n_findings']} finding, job `{res['job_id']}` (chạy nền, sẽ tự báo).")
            else:
                dispatch_msg_lines.append(f"- {owner}: {res['n_findings']} finding, DISPATCH LỖI (rc={res.get('returncode')}) — cần kiểm tay: {res.get('stderr_tail', '')[-300:]}")
        if not results:
            dispatch_msg_lines.append("- Không có finding nào thuộc Taylor/Wags lượt này (toàn bộ đã escalate).")
        subprocess.run(
            [str(root / "bin" / "notify_thread.sh"), "\n".join(dispatch_msg_lines), args.arch_thread or "architecture"],
            check=False, cwd=str(root),
        )

    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
