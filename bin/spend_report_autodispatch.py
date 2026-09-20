#!/usr/bin/env python3
"""Dispatch Taylor to turn the weekly spend/token report into a routing-policy improvement
(user mandate 2026-09-20: "ARIA" feedback loop — báo cáo token hàng tuần phải tự nuôi cải tiến,
không chỉ đọc rồi để đó). Called by spend_report_weekly.py right after the report is generated.

Scope CỐ Ý hẹp: Taylor chỉ được sửa kb/mike_model_routing.md (chính sách ladder model/effort mà
MỌI dispatch fleet-wide tham chiếu tại thời điểm chọn --model/--effort) — không đụng dispatch.sh,
không đụng bất kỳ code production/trading nào. Rule 2-tuần-liên-tiếp (tránh áp chính sách theo
nhiễu 1 tuần): tuần đầu phát hiện 1 vấn đề → chỉ ghi <file>.proposed + bus finding (theo
coding_guidelines §13); CÙNG vấn đề lặp lại đúng ở tuần kế tiếp mới áp live, bắt buộc
arch-reviewer audit trước khi coi là done. Không có gì đáng nói (report sạch) → Taylor vẫn phải
post finding "reviewed, no action" (quiet-heartbeat, không được im lặng).

Idempotency: state/spend_report_routing_dispatch_<date>.json, ghi atomic ngay sau khi dispatch
thành công — rerun cùng ngày (cron chạy lại tay) sẽ skip.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # mike/


def parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--report", required=True, help="Đường dẫn report vừa sinh (reports/spend_report_weekly_<date>.md)")
    p.add_argument("--report-date", required=True, help="YYYY-MM-DD")
    p.add_argument("--state-dir", default=str(ROOT / "state"))
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args(argv)


def state_path(state_dir: str, report_date: str) -> Path:
    return Path(state_dir) / f"spend_report_routing_dispatch_{report_date}.json"


def already_dispatched(state_dir: str, report_date: str) -> bool:
    return state_path(state_dir, report_date).exists()


def mark_dispatched(state_dir: str, report_date: str, job_id: str) -> None:
    p = state_path(state_dir, report_date)
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"report_date": report_date, "job_id": job_id}, f, ensure_ascii=False, indent=2)
    os.replace(tmp, p)


PROMPT_TEMPLATE = """WEEKLY SPEND REPORT -> ROUTING POLICY REVIEW (tu dong, mandate user 2026-09-20).

Bao cao chi phi token/compute tuan vua sinh o: {report_path}
Ngay bao cao: {report_date}

Boi canh: user muon vong lap "bao cao token hang tuan -> tu cai thien" thay vi chi doc roi de do.
Ban (Taylor) la nguoi duy nhat duoc uy quyen cho vong nay, PHAM VI CO Y RAT HEP:

VIEC CAN LAM:
1. Doc {report_path} full, dac biet muc "Canh bao effort/model/retry", bang "Model / provider mix",
   bang so sanh WoW, va cot %opus/%fable trong state/spend_history.csv (xu huong nhieu tuan, khong
   chi 1 tuan).
2. Doc kb/mike_model_routing.md (chinh sach ladder model/effort MOI dispatch fleet-wide dang tham
   chieu) de biet huong dan hien tai la gi.
3. Danh gia: co dieu gi trong bao cao goi y ladder/huong dan hien tai dang bi ap dung SAI hoac can
   sua (vd %opus tang bat thuong cho task khong xung dang, canh bao effort/retry lap lai, mot loai
   task cu the luon bi route sai model) hay khong?
   - KHONG co gi dang sua -> post finding "reviewed, no action" len bus (KHONG duoc im lang, quiet-
     heartbeat bat buoc), DUNG lai, khong sua gi.
   - CO van de -> tiep tuc buoc 4.
4. Kiem tra bus (grep bus/inbox/Taylor.jsonl hoac dung mike_json.py) topic
   'spend-report-routing-review-<ngay-tuan-truoc>' (7 ngay truoc {report_date}) xem TUAN TRUOC ban
   (hoac ai do) co tung flag DUNG van de nay chua:
   - CHUA tung flag (quan sat lan DAU) -> CHI ghi de xuat vao kb/mike_model_routing.md.proposed
     (KHONG sua file live, dung theo coding_guidelines Sec 13), post bus finding topic
     'spend-report-routing-review-{report_date}' noi ro "quan sat lan dau, cho tuan sau xac nhan
     lai truoc khi ap dung" kem noi dung de xuat cu the. DUNG lai o day.
   - DA tung flag CUNG van de o tuan truoc (lan thu 2 lien tiep) -> ap dung THAT: sua truc tiep
     kb/mike_model_routing.md (chi sua doan lien quan, giu nguyen cau truc/style file, KHONG viet
     lai toan bo), commit ro rang (ghi truoc/sau trong message), post bus finding topic
     'spend-report-routing-review-{report_date}' kem before/after + so lieu 2 tuan dan chung.

RANH GIOI CUNG (khong duoc vuot, du bat ky ly do gi):
- CHI duoc sua kb/mike_model_routing.md. KHONG dung cham bin/dispatch.sh, khong dung cham bat ky
  file trading_bot/*, bot_execute.py, trading_rules.json, hay bat ky code production/thuc thi nao
  khac. Day la chinh sach VAN BAN huong dan nguoi dispatch chon model, khong phai config so.
- Neu sua live (truong hop lan 2 lien tiep o tren): BAT BUOC dispatch Agent(subagent_type=
  "arch-reviewer") tu audit diff TRUOC KHI coi la xong (file nay moi dispatch fleet-wide deu doc).
  NEEDS_CHANGES -> sua tiep, dung tu dong dong.
- Day KHONG phai R&D quant (khong can quant-skeptic), nhung VAN can arch-reviewer vi day la ha
  tang chia se dung chung.
- Neu khong chac chan day co phai "cung 1 van de" voi tuan truoc hay khong (vd tuan truoc flag
  A, tuan nay thay ca A lan B) -> coi la quan sat MOI, khong duoc tinh la "lan 2".

Sau khi xong (du la nhanh 'no action', nhanh 'proposed', hay nhanh 'applied'):
append_event.sh Taylor finding 'spend-report-routing-review-{report_date}' '<JSON tom tat: verdict
(no_action|proposed|applied), evidence, commit hash neu co>'
"""


def build_prompt(report_path: str, report_date: str) -> str:
    return PROMPT_TEMPLATE.format(report_path=report_path, report_date=report_date)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])

    if already_dispatched(args.state_dir, args.report_date):
        print(f"Đã dispatch review routing cho tuần {args.report_date} trước đó; bỏ qua.")
        return

    prompt = build_prompt(args.report, args.report_date)

    if args.dry_run:
        print("[dry-run] Sẽ dispatch Taylor với prompt:")
        print(prompt)
        return

    dispatch_sh = str(ROOT / "bin" / "dispatch.sh")
    cmd = [dispatch_sh, "Taylor", prompt, "--bg", "--timeout", "3600", "--effort", "high"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    job_id = None
    for line in result.stdout.splitlines():
        if line.startswith("JOB "):
            job_id = line.split()[1]
            break
    mark_dispatched(args.state_dir, args.report_date, job_id or "unknown")
    print(f"Đã dispatch Taylor review routing (job={job_id}) cho tuần {args.report_date}.")


if __name__ == "__main__":
    main()
