#!/usr/bin/env python3
"""Tầng 3 auto-dispatch cho code_quality_weekly.sh (user chốt 2026-09-17, xem
kb/projects/code-quality-review-plan-20260823.md § CẬP NHẬT 2026-09-17).

Đọc findings đã verify (JSON của code_quality_weekly.sh), phân nhóm:
  - ESCALATE: finding chạm file "hot-core tiền thật" — MỌI severity escalate (không tin severity
    LLM tự khai làm cổng cho code chạm tiền thật/NAV sống — arch-review round 2 bác bỏ việc tách
    riêng 1 tầng "NAV-scale chỉ escalate medium/high", vì boundary gốc trong MIKE.md/current_ops.md
    ("KHÔNG tự sửa logic đặt lệnh") không hề có ngoại lệ theo severity). Nguồn hard-boundary = HỢP
    (union) 2 nguồn, không nguồn nào thay thế nguồn kia:
      (1) Danh sách tay `EXEC_HARD_BOUNDARY_PREFIXES`/`_EXACT` — prefix `trading_bot/` (mọi file
          dưới thư mục này, không liệt tên — tránh trôi khi thêm module mới) + vài file cụ thể
          ngoài đó (`bot_execute.py`, `dnse_api.py`, `mike/bin/run_bot.sh`, ...).
      (2) `kb/production_manifest.json`, lọc theo `roots[]` (MỌI root với tới được, KHÔNG PHẢI
          `tier_root` — xem lý do dưới) ∈ `ORDER_WRITING_ROOTS`, trừ `SAFE_TOOLING_ALLOWLIST`
          (`load_manifest_order_writing()`) — nguồn CƠ HỌC sinh từ crontab thật
          (`production_manifest.py`), bắt được file KHÔNG có trong danh sách tay — arch-review
          round 3 killer objection: danh sách tay chỉ phủ 10/34 file T0 có commit trong 1 tuần đo
          thật, bỏ sót `mike/bin/merge_park_orders.py` (ghi thẳng orders[] vào plan). Manifest đọc
          lỗi/thiếu ⇒ rơi về set rỗng + warning (KHÔNG throw, KHÔNG im lặng — xem hàm), danh sách
          tay (1) vẫn là nền — không có kịch bản nào escalation bị GIẢM so với chỉ dùng (1).
          ⚠️ **2 lần đổi 2026-09-18 (user chốt: "tăng tỉ lệ tự sửa")**:
          - Lần 1: bản đầu dùng CẢ tier T0 (107 file, gồm cả file KHÔNG chạm tiền như
            `dispatch.sh`/`eod_trading_report.sh` — `tier=T0` nghĩa là "với tới được từ MỘT cron
            gốc gắn nhãn T0", không phải "chính nó ghi lệnh") → đổi sang lọc theo `tier_root`.
          - Lần 2 (SỬA LỖI lần 1, cùng ngày): `tier_root` hoá ra KHÔNG PHẢI "root chịu trách nhiệm
            ngữ nghĩa" như tưởng — nó chỉ là tie-break theo THỨ TỰ DÒNG CRONTAB giữa các root
            CÙNG tier (`production_manifest.py:618`, so sánh chặt `<`). `bq_freshness_check.sh`
            (T0, dòng 48) đứng trên `run_bot.sh` (dòng 61) nên thắng `tier_root` của 44/107 file
            T0, làm 20 file VẪN reachable từ root ghi lệnh (`signal_holds.py`,
            `lag_rating_filter.py` — gate rating≤3 user khoá 07-27, `corp_action_lib.py`,
            `dnse_fee_rates.py`...) bị rớt khỏi escalation — tái lập đúng killer round 3. Đổi
            sang lọc `roots[]` (71 file, phục hồi đủ 20 file) + `SAFE_TOOLING_ALLOWLIST` tường
            minh (`dispatch.sh`, `notify_thread.sh`, `append_event.sh`, `mike_json.py`,
            `discord_channel.sh`) để vẫn đạt mục tiêu ban đầu (4 file user muốn bỏ escalate oan)
            mà không dựa vào hiện vật thứ tự crontab. `macro_state_live.py`/
            `publish_gated_state.py` (DT5G `get_gated_state()`) liệt tay vào (1) vì roots[] của
            chúng không khớp `ORDER_WRITING_ROOTS`.
    HOẶC owner không phải Taylor/Wags (rỗng/"Mike"/lạ) — fail-safe khi không rõ owner.
    KHÔNG dispatch — ghi bus question + ack `triaged-needs-human:` (khỏi bị wags_autofix đốt
    job vô ích, xem arch-review round 1 "Long-term ops") + Discord.
  - Taylor / Wags: dispatch --bg với prompt build từ chính finding (surgical, ràng buộc ranh
    giới cứng + kỷ luật git add, selfcheck theo phạm vi, arch-reviewer/quant-skeptic bắt buộc).
    `--write-scope` truyền theo đường dẫn REPO-RELATIVE (so với `--wc-root`) — arch-review round 2:
    path TUYỆT ĐỐI làm vô hiệu cả job-write-scope-conflict lẫn commit-collision-gate. File dưới
    `mike/` (git repo RIÊNG lồng trong WorkingClaude) khai CẢ 2 dạng (`mike/bin/x.py` VÀ
    `bin/x.py`, xem `write_scope_variants()`) — arch-review round 3: đo thật fleet dùng lẫn lộn cả
    2 quy ước, khai 1 dạng duy nhất bỏ lỡ phần lớn khả năng khớp thật.

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
    # DT5G regime gate (`get_gated_state()`) — cap exposure theo trạng thái thị trường, KHÔNG
    # phải file lệnh trực tiếp nhưng roots[] của nó (bq_freshness_check.sh, check_sbv_weekly.sh,
    # daily_refresh_v34b_linux.sh, papertrade_daily.sh) không khớp ORDER_WRITING_ROOTS nên cơ chế
    # manifest bên dưới không tự bắt được — liệt tay (arch-review gate-narrowing round, 2026-09-18).
    "macro_state_live.py",
    "deploy_golive_dt5g_v4/publish_gated_state.py",
    # Ghi lại orders[] của plan SỐNG qua `signal_holds.py --enforce` (atomic tmp+replace) —
    # arch-review gate-narrowing round 2 killer cùng lớp: caller thực sự gọi --enforce lên plan,
    # trong khi callee (mike/bin/signal_holds.py, cũng nạp bởi trading_bot/plan.py) đã được
    # ORDER_WRITING_ROOTS/roots[] phủ. Không thêm root vì sẽ kéo theo dna_report.py/moat_5f.py/
    # value_radar.py (display-only, không ghi lệnh) — liệt tay đúng 1 file cho gọn.
    "mike/bin/send_plan_report.sh",
)
VALID_SEVERITIES = {"low", "medium", "high"}

# Root cron TRỰC TIẾP ghi lệnh/vị thế/margin — dùng để lọc `roots[]` của
# kb/production_manifest.json (xem load_manifest_order_writing()). KHÔNG gồm root chỉ báo cáo/
# kiểm tra freshness (eod_trading_report.sh, bq_freshness_check.sh, check_report_cadence.sh,
# kb_nightly.sh, ops_health_check.sh...) — những root đó khiến `tier=T0` bao trùm cả tooling an
# toàn để tự sửa (đo thật 2026-09-18: dispatch.sh/bus_question_audit.py lọt vào T0 dù không ghi
# lệnh gì, chỉ vì "với tới được" từ run_bot.sh qua 1 nhánh gọi phụ). Tên rút từ chính basename
# trong `production_manifest.py::ROOT_TIER` — đối chiếu lại nếu script đó đổi tên root
# (`load_manifest_order_writing()` tự cảnh báo nếu 1 tên ở đây không khớp root nào trong manifest).
#
# ⚠️ LỌC THEO `roots[]` (mọi root với tới được), KHÔNG PHẢI `tier_root` (bản đầu 2026-09-18 dùng
# `tier_root` — SAI: đó chỉ là tie-break theo THỨ TỰ DÒNG CRONTAB giữa các root CÙNG tier
# (production_manifest.py:618, so sánh chặt `<`), không phải "root chịu trách nhiệm ngữ nghĩa".
# bq_freshness_check.sh đứng dòng 48 (trên run_bot.sh dòng 61) nên thắng tier_root của 44/107 file
# T0, làm 20 file VẪN reachable từ root ghi lệnh (signal_holds.py, lag_rating_filter.py,
# corp_action_lib.py, dnse_fee_rates.py...) bị rớt khỏi escalation — tái lập đúng killer "bỏ sót
# file ghi lệnh" mà cơ chế manifest này sinh ra để chặn. Đã đo lại: lọc theo `roots[]` cho 71 file,
# phục hồi đủ 20 file đó.
ORDER_WRITING_ROOTS = frozenset({
    "run_bot.sh", "bot_execute.py", "merge_park_daily.sh", "inject_discretionary_orders.sh",
    "park_trim_daily.sh", "jit_unpark_daily.sh", "corp_action_auto_confirm.py",
    "discretionary_margin_check_exits_daily.sh", "compute_active_nav_all.sh",
    "late_plan_catchup.sh",  # chạy park_trim→jit_unpark→merge_park --write→inject_discretionary
    "preflight_check.sh",  # gate HOLD plan chưa duyệt — chính nó quyết có đặt lệnh hay không
    # Autoheal khởi động lại bot_execute.py --auto-otp (cron */5 giờ giao dịch, CẢ 2 account tiền
    # thật) — toàn bộ guard chống restart sai thời điểm (plan done/nghỉ trưa/ngoài giờ/pgrep liveness)
    # nằm TRONG chính file này; nới nhầm 1 điều kiện = chạy trùng bot_execute, đúng lớp sự cố
    # double-buy 2026-07-02 (arch-review gate-narrowing round 2 killer objection, 2026-09-18).
    "bot_heartbeat.sh",
})

# Tooling GENERIC dùng chung mọi nơi (kể cả bởi root ghi lệnh) nhưng KHÔNG tự nó ghi lệnh/vị thế —
# trừ khỏi kết quả `roots[]`-match phía trên để không escalate oan (đây là mục tiêu user 2026-09-18
# "tăng tỉ lệ tự sửa": lọc theo roots[] rộng hơn tier_root, nên cần allowlist tường minh, review
# được — thay vì dựa vào hiện vật thứ tự crontab như bản tier_root đã bị bác). File này VẪN qua
# arch-reviewer bắt buộc như mọi finding khác (bảng owner §6) — chỉ không phải ESCALATE-cho-người.
SAFE_TOOLING_ALLOWLIST = frozenset({
    "mike/bin/dispatch.sh", "mike/bin/notify_thread.sh", "mike/bin/append_event.sh",
    "mike/bin/mike_json.py", "mike/bin/discord_channel.sh",
})


def _root_basename(root_str: str) -> str:
    """'cron `0 3 * * 0` merge_park_daily.sh' -> 'merge_park_daily.sh'. Chuỗi rỗng/lạ -> ''."""
    return (root_str or "").rsplit(" ", 1)[-1]


def load_manifest_order_writing(root: Path) -> tuple[set[str], str | None]:
    """Đọc thêm `kb/production_manifest.json` (đã tồn tại, do `production_manifest.py` sinh CƠ
    HỌC từ crontab thật — xem docstring file đó) làm NGUỒN THỨ 2, HỢP (union) với
    EXEC_HARD_BOUNDARY_* thay vì thay thế — arch-review round 3 killer objection: danh sách tay
    chỉ phủ 10/34 file T0 có commit trong scope tuần đo thật (bỏ sót mike/bin/merge_park_orders.py
    — ghi thẳng orders[] vào plan — và tương tự).

    Lọc theo `roots[]` (MỌI root với tới được file đó) ∈ ORDER_WRITING_ROOTS, trừ đi
    SAFE_TOOLING_ALLOWLIST — user chốt 2026-09-18 sau khi thấy bản dùng cả tier T0 (107 file)
    escalate oan cả tooling an toàn, ngược mục tiêu "tăng tỉ lệ tự sửa, giảm việc treo không cần
    thiết". Bản đầu dùng `tier_root` (root DUY NHẤT gán cho tier) bị arch-review bác vì đó là
    hiện vật thứ tự dòng crontab (xem comment tại ORDER_WRITING_ROOTS), không phải ngữ nghĩa
    "chạm tiền" — dùng `roots[]` mới đúng câu hỏi "file này CÓ THỂ bị root ghi lệnh gọi tới không".

    Trả (set, warning). Lỗi đọc bất kỳ (thiếu file/JSON hỏng/thiếu field) ⇒ set RỖNG + warning nêu
    ĐÚNG lý do đọc được (không đoán, §29) — arch-review round 4 killer objection: bản trước nuốt
    exception thành set() IM LẶNG, không log/không Discord, khiến "gate đang bảo vệ" và "gate đã
    tắt" không phân biệt được từ output. Caller BẮT BUỘC đưa warning này vào summary + Discord.
    Cũng cảnh báo (cùng field) nếu 1 tên trong ORDER_WRITING_ROOTS không khớp root nào trong
    manifest — root đổi tên/gõ sai sẽ làm set co lại IM LẶNG nếu không kiểm."""
    manifest_path = root / "kb" / "production_manifest.json"
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except OSError as e:
        return set(), f"không đọc được {manifest_path}: {e}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return set(), f"JSON hỏng ở {manifest_path}: {e}"
    files = data.get("files")
    if not isinstance(files, dict):
        return set(), f"{manifest_path} thiếu field 'files' hợp lệ (schema đổi?)"

    seen_root_names: set[str] = set()
    matched: set[str] = set()
    for rel, meta in files.items():
        if not isinstance(meta, dict):
            continue
        roots = meta.get("roots") or []
        names = {_root_basename(r) for r in roots if isinstance(r, str)}
        seen_root_names |= names
        if names & ORDER_WRITING_ROOTS:
            matched.add(rel)
    matched -= SAFE_TOOLING_ALLOWLIST

    unmatched_roots = ORDER_WRITING_ROOTS - seen_root_names
    if unmatched_roots:
        return matched, (
            f"{sorted(unmatched_roots)} trong ORDER_WRITING_ROOTS không khớp root nào trong "
            f"{manifest_path} (đổi tên/gõ sai?) — set order-writing có thể THIẾU, xem lại code."
        )
    return matched, None


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


def classify(findings: list[dict], wc_root: Path, manifest_order_writing: set[str] | None = None) -> dict[str, list[dict]]:
    manifest_order_writing = manifest_order_writing or set()
    groups: dict[str, list[dict]] = {"escalate": [], "taylor": [], "wags": []}
    for f in findings:
        rel = to_repo_relative(str(f.get("file") or ""), wc_root)
        owner = str(f.get("owner") or "").strip().lower()
        is_exec_hard = (
            rel.startswith(EXEC_HARD_BOUNDARY_PREFIXES)
            or rel in EXEC_HARD_BOUNDARY_EXACT
            or rel in manifest_order_writing
        )
        if is_exec_hard:
            reason = "hard_boundary_manifest_order_writing" if rel in manifest_order_writing and rel not in EXEC_HARD_BOUNDARY_EXACT and not rel.startswith(EXEC_HARD_BOUNDARY_PREFIXES) else "hard_boundary_tien_that"
            groups["escalate"].append({**f, "_escalate_reason": reason, "_rel": rel})
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


def build_prompt(owner: str, findings: list[dict], report_date: str, report_file: str, escalate_files_rel: set[str]) -> str:
    n = len(findings)
    blocks = "\n\n".join(_finding_block(f) for f in findings)
    no_touch = ""
    # So trên "_rel" (đã chuẩn hoá) CẢ HAI VẾ — arch-review round 3: bản trước so escalate_files_rel
    # (đã chuẩn hoá ở run()) với f.get("file") (path THÔ, thường tuyệt đối) ⇒ luôn rỗng, cảnh báo
    # "cùng file đang escalate" thành code chết (§28: chuẩn hoá cả 2 vế trước khi so).
    same_file_escalate = sorted(escalate_files_rel & {f.get("_rel") for f in findings})
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


def write_scope_variants(rel: str) -> list[str]:
    """1 file có thể cần khai theo NHIỀU dạng để khớp guard của fleet — arch-review round 3: đo
    thật trên `bus/jobs/*.json` cho thấy 98 giá trị --write-scope khác nhau (bin/…, mike/…, ../…,
    tuyệt đối); `mike/` là git repo RIÊNG lồng trong WorkingClaude nên staged-diff của NÓ (đọc bởi
    `bin/repo_commit_gate.sh`, hook CHỈ cài ở repo `mike/`) tính từ toplevel `mike/` (vd
    `bin/foo.py`), không phải từ WC (`mike/bin/foo.py`). Trả cả 2 dạng cho file dưới `mike/` để
    khớp cả `job-write-scope-conflict` (so chuỗi khai báo, không quan tâm toplevel) lẫn
    `repo_commit_gate.sh` (so staged-diff CỦA REPO mike). File ngoài `mike/` — arch-review round 4
    đo lại: `WorkingClaude` KHÔNG PHẢI git toplevel của chính nó (`git rev-parse --show-toplevel`
    ở đó trả `/home/trido/thanhdt`, staged path thật dạng `WorkingClaude/foo.py`) nên câu "WC là
    toplevel của chính nó" ở bản trước SAI — nhưng vô hại vì `repo_commit_gate.sh` không cài hook
    ở repo ngoài `mike/`, `job-write-scope-conflict` không quan tâm toplevel git; KHÔNG thêm biến
    thể `WorkingClaude/<rel>` vì chưa đo được lợi ích thật, chỉ sửa lại câu khẳng định cho đúng."""
    if rel.startswith("mike/"):
        return [rel, rel[len("mike/"):]]
    return [rel]


def run(args) -> dict:
    root = Path(args.root)
    wc_root = Path(args.wc_root) if args.wc_root else Path(args.root).parent
    manifest_order_writing, manifest_warning = load_manifest_order_writing(root)
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
    groups = classify(valid, wc_root, manifest_order_writing)
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
        write_scope_set: set[str] = set()
        for f in flist:
            if f.get("_rel"):
                write_scope_set.update(write_scope_variants(f["_rel"]))
        write_scope = ",".join(sorted(write_scope_set))
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
        "n_manifest_order_writing": len(manifest_order_writing),
        "manifest_warning": manifest_warning,
        "escalate_failed": escalate_failed,
        "results": results,
        "generated_at": now_ict_iso(),
    }

    if not args.dry_run:
        dispatch_msg_lines = [f"**Code review auto-dispatch ({args.date})** — báo cáo `{args.report_file}`:"]
        if manifest_warning:
            # arch-review round 4 killer objection: gate hard-boundary phải QUAN SÁT ĐƯỢC khi
            # phần manifest-union không đọc được — trước đó im lặng trả set rỗng, không ai biết
            # "gate đang bảo vệ" hay "gate đã tắt" từ output.
            #
            # `manifest_warning` giờ mang 2 NGHĨA KHÁC NHAU (arch-review gate-narrowing round 2):
            # (a) manifest không đọc được/hỏng ⇒ manifest_order_writing RỖNG, union thật sự tắt;
            # (b) manifest đọc OK nhưng 1 tên trong ORDER_WRITING_ROOTS không khớp root nào (đổi
            # tên/gõ sai) ⇒ manifest_order_writing VẪN CÓ dữ liệu (có thể thiếu 1 phần, không phải
            # rỗng). Trước đây in CHUNG 1 câu "KHÔNG có phần bổ sung" cho cả 2 ca — sai với ca (b),
            # đúng dạng §29 "khẳng định nguyên nhân chưa đọc bằng chứng". Rẽ nhánh theo
            # len(manifest_order_writing) thay vì đoán loại warning từ text.
            if manifest_order_writing:
                dispatch_msg_lines.append(
                    f"⚠️ {manifest_warning} — union manifest VẪN ĐANG chạy với "
                    f"{len(manifest_order_writing)} file (có thể THIẾU phần ứng với tên root lệch),"
                    f" danh sách tay không đổi. Kiểm lại ORDER_WRITING_ROOTS trong code."
                )
            else:
                dispatch_msg_lines.append(
                    f"⚠️ Không đọc được kb/production_manifest.json ({manifest_warning}) — tuần này "
                    f"ranh giới cứng CHỈ dùng danh sách tay (EXEC_HARD_BOUNDARY_*), KHÔNG có phần bổ "
                    f"sung từ manifest. Danh sách tay vẫn đứng nguyên, không tắt hẳn."
                )
        dispatch_msg_lines.append(
            f"Phân loại: {len(escalate)} escalate / {len(taylor_f)} Taylor / {len(wags_f)} Wags "
            f"(danh sách ghi lệnh/vị thế từ manifest đang có {len(manifest_order_writing)} file)."
        )
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
    if args.dry_run:
        # --dry-run không dispatch/escalate gì thật ⇒ "kết quả" luôn là preview thành công, không
        # có khái niệm rc≠0 ở đây (arch-review round 3: bản trước rơi vào nhánh "any dispatch fail"
        # vì kết quả dry-run không có job_id/returncode, khiến preview THÀNH CÔNG vẫn báo rc=1).
        return 0
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
