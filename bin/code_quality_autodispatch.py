#!/usr/bin/env python3
"""Tầng 3 auto-dispatch cho code_quality_weekly.sh (user chốt 2026-09-17, xem
kb/projects/code-quality-review-plan-20260823.md § CẬP NHẬT 2026-09-17).

Đọc findings đã verify (JSON của code_quality_weekly.sh), phân nhóm:
  - ESCALATE: finding chạm file "hot-core tiền thật" — 2 tầng:
      (a) EXEC (đặt lệnh trực tiếp): trading_bot/{plan,executor,brokers,config,
          plan_funding_gate}.py, bot_execute.py — MỌI severity escalate (không tin severity
          LLM tự khai làm cổng cho code chạm tiền thật).
      (b) NAV-scale (nuôi số NAV dùng để scale vốn sống): mike/bin/{compute_active_nav,
          daily_nav_snapshot}.py, trading_bot/strategies.py — chỉ severity medium/high escalate
          (thực tế đã kiểm ngày 2026-09-17: nhiều finding low/dead-code ở compute_active_nav.py
          được Wags tự sửa + arch-review an toàn).
    HOẶC owner không phải Taylor/Wags (rỗng/"Mike"/lạ) — fail-safe khi không rõ owner.
    KHÔNG dispatch — ghi bus question + ack `triaged-needs-human:` (khỏi bị wags_autofix đốt
    job vô ích, xem arch-review round 1 "Long-term ops") + Discord.
  - Taylor / Wags: dispatch --bg với prompt build từ chính finding (surgical, ràng buộc ranh
    giới cứng + kỷ luật git add, selfcheck theo phạm vi, arch-reviewer/quant-skeptic bắt buộc).

Bài học 2026-09-17 (lượt dispatch tay đầu tiên, xem plan doc): script này CHÍNH LÀ nơi duy nhất
tự động dispatch cho 1 báo cáo — không có tác nhân nào khác chạy song song cho cùng report_date,
nên không cần grep bus tìm "đã có ai fix chưa" (khác tình huống Mike dispatch TAY cho báo cáo cũ).

State file (`state/code_quality_weekly_dispatch_<date>.json`) ghi NGUYÊN TỬ (tmp+os.replace)
NGAY sau mỗi side-effect thành công (escalation, mỗi dispatch) — không gom cuối. Rerun (cron
chạy lại tay, hoặc lần trước chết giữa chừng) chỉ làm lại phần CHƯA thành công — arch-review
round 1: ghi state cuối cùng + ghi cả khi dispatch rc≠0 khiến rerun bỏ sót finding vĩnh viễn.
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
ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# (a) đặt lệnh trực tiếp — MỌI severity escalate.
EXEC_HARD_BOUNDARY_SUFFIXES = (
    "trading_bot/plan.py",
    "trading_bot/executor.py",
    "trading_bot/brokers.py",
    "trading_bot/config.py",
    "trading_bot/plan_funding_gate.py",
    "bot_execute.py",
)
# (b) nuôi công thức NAV scale vốn sống — chỉ medium/high escalate.
NAV_HARD_BOUNDARY_SUFFIXES = (
    "mike/bin/compute_active_nav.py",
    "mike/bin/daily_nav_snapshot.py",
    "trading_bot/strategies.py",
)
VALID_SEVERITIES = {"low", "medium", "high"}


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
        ok.append(f)
    return ok, invalid


def classify(findings: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {"escalate": [], "taylor": [], "wags": []}
    for f in findings:
        file_ = str(f.get("file") or "").replace("\\", "/")
        severity = str(f.get("severity") or "").lower()
        owner = str(f.get("owner") or "").strip().lower()
        is_exec_hard = any(file_.endswith(suf) for suf in EXEC_HARD_BOUNDARY_SUFFIXES)
        is_nav_hard = severity in ("medium", "high") and any(
            file_.endswith(suf) for suf in NAV_HARD_BOUNDARY_SUFFIXES
        )
        if is_exec_hard:
            groups["escalate"].append({**f, "_escalate_reason": "hard_boundary_dat_lenh_truc_tiep"})
        elif is_nav_hard:
            groups["escalate"].append({**f, "_escalate_reason": "hard_boundary_nav_scale_von_song"})
        elif owner == "taylor":
            groups["taylor"].append(f)
        elif owner == "wags":
            groups["wags"].append(f)
        else:
            groups["escalate"].append(
                {**f, "_escalate_reason": f"owner_khong_ro_hoac_khong_phai_taylor_wags:{owner or '(rỗng)'}"}
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
        return {"owner": owner, "dry_run": True, "cmd_preview": cmd[:3] + ["<prompt omitted, len=%d>" % len(prompt)] + cmd[4:]}
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
    dispatch_bin = Path(args.dispatch_bin) if args.dispatch_bin else root / "bin" / "dispatch.sh"
    state_file = Path(args.state_file) if args.state_file else root / "state" / f"code_quality_weekly_dispatch_{args.date}.json"

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
    groups = classify(valid)
    escalate = groups["escalate"] + invalid
    taylor_f, wags_f = groups["taylor"], groups["wags"]
    escalate_files = {f.get("file") for f in escalate if isinstance(f.get("file"), str)}

    # Toàn bộ nhóm ĐÃ xong ở state trước đó (rerun đúng nghĩa duplicate) ⇒ skip sạch, không đụng gì.
    need_escalate = bool(escalate) and not state.get("escalate", {}).get("posted")
    need_taylor = bool(taylor_f) and "taylor" not in state
    need_wags = bool(wags_f) and "wags" not in state
    if not (need_escalate or need_taylor or need_wags):
        return {"skipped": True, "reason": "state_file_da_du_moi_nhom", "previous": state}

    if need_escalate:
        ok = post_escalation(root, escalate, args.date, args.report_file, args.dry_run, args.arch_thread)
        if ok and not args.dry_run:
            state["escalate"] = {"posted": True, "n": len(escalate), "at": now_ict_iso()}
            atomic_write_json(state_file, state)

    results: dict[str, dict] = {}
    for key, owner, flist, need in (("taylor", "Taylor", taylor_f, need_taylor), ("wags", "Wags", wags_f, need_wags)):
        if not need:
            if key in state:
                results[owner] = {**state[key], "skipped_already_done": True}
            continue
        prompt = build_prompt(owner, flist, args.date, args.report_file, escalate_files)
        write_scope = ",".join(sorted({f.get("file", "") for f in flist if f.get("file")}))
        thread_id = args.arch_thread or "architecture"
        res = dispatch(dispatch_bin, owner, prompt, thread_id, write_scope, args.timeout, args.dry_run)
        res["n_findings"] = len(flist)
        res["write_scope"] = write_scope
        results[owner] = res
        # CHỈ ghi state khi THẬT SỰ thành công (rc==0 và bắt được job_id) — rc≠0/job_id=None để
        # NGUYÊN trong state (không ghi key), rerun kế tiếp sẽ thử lại ĐÚNG nhóm này (arch-review
        # round 1: ghi state vô điều kiện làm rerun bỏ sót finding vĩnh viễn khi dispatch fail).
        if not args.dry_run and res.get("returncode") == 0 and res.get("job_id"):
            state[key] = {"job_id": res["job_id"], "n_findings": res["n_findings"], "write_scope": write_scope, "at": now_ict_iso()}
            atomic_write_json(state_file, state)

    summary = {
        "date": args.date,
        "n_escalate": len(escalate),
        "n_taylor": len(taylor_f),
        "n_wags": len(wags_f),
        "results": results,
        "generated_at": now_ict_iso(),
    }

    if not args.dry_run:
        dispatch_msg_lines = [f"**Code review auto-dispatch ({args.date})** — báo cáo `{args.report_file}`:"]
        any_fail = False
        for owner, res in results.items():
            if res.get("skipped_already_done"):
                dispatch_msg_lines.append(f"- {owner}: đã dispatch xong ở lần chạy trước (job `{res.get('job_id')}`), không lặp lại.")
            elif res.get("job_id") and res.get("returncode") == 0:
                dispatch_msg_lines.append(f"- {owner}: {res['n_findings']} finding, job `{res['job_id']}` (chạy nền, sẽ tự báo).")
            else:
                any_fail = True
                dispatch_msg_lines.append(
                    f"- {owner}: {res['n_findings']} finding, DISPATCH LỖI (rc={res.get('returncode')}, job_id={res.get('job_id')}) "
                    f"— SẼ THỬ LẠI lần chạy sau (chưa ghi state). Chi tiết: {res.get('output_tail', '')[-400:]}"
                )
        if not results and not escalate:
            dispatch_msg_lines.append("- Không có finding nào thuộc Taylor/Wags lượt này (toàn bộ đã escalate).")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
