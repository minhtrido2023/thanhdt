#!/usr/bin/env python3
"""Idempotently deliver one client-facing report to Discord and email.

Completion is fail-closed: the artifact must pass the return gate and both
destinations must have durable, hash-bound success evidence.
"""
from __future__ import annotations

import argparse
import calendar
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


# Gốc CANONICAL, KHÔNG phải cây đang chạy. `state/` bị gitignore nên mỗi worktree/clone chạy
# bản sao script này sẽ giữ một SỔ GIAO HÀNG RIÊNG, trong khi `check_report_cadence.sh:44` chỉ
# đọc sổ canonical ⇒ lần giao hàng từ cây phụ là vô hình với cadence check ⇒ GỬI TRÙNG báo cáo
# cho nhà đầu tư (đã xảy ra thật: monthly 2026-08 gửi 28/08 từ `mike_paseo`, gửi lại 02/09 từ
# canonical). Lock file bám theo state_path nên cũng tự về canonical ⇒ hai cây loại trừ nhau.
# Ba script con bên dưới (return gate, notify, email) CỐ Ý cũng chạy bản canonical: 14 worktree
# đang giữ bản TIỀN-VÁ của `report_return_gate.py` (sự cố 2026-09-12) và giao hàng từ đó sẽ tái
# hiện lỗi. Đánh đổi, nói đúng phạm vi: notify/email có cờ override (`--notify-script`,
# `--email-script`); RETURN GATE thì KHÔNG — muốn thử bản sửa đổi của nó thì chạy thẳng
# `bin/report_return_gate.py --report <file>`, như `report_return_gate_selfcheck.py` vẫn làm.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wc_paths import find_mike_canonical_root  # noqa: E402

ROOT = Path(find_mike_canonical_root(__file__))
RUNNING_TREE = Path(__file__).resolve().parent.parent
if RUNNING_TREE != ROOT:
    # Hệ quả của việc ghim: sổ canonical giờ là sổ SẢN XUẤT với MỌI cây, nên một lần "chạy thử"
    # từ worktree cũng đóng dấu "đã gửi" vào đó. Đã có tiền lệ đúng lớp này: entry stub
    # `SpaceX_daily_report_not-a-date.md` (discord+email delivered) trong sổ lạc của một worktree.
    print(f"⚠️  report_delivery_gate: chạy từ {RUNNING_TREE} nhưng GHI SỔ THẬT + gọi script con "
          f"của cây canonical {ROOT} — đây không phải sandbox", file=sys.stderr)
DEFAULT_STATE = ROOT / "state" / "report_delivery.json"
LEGACY_EMAIL_STATE = ROOT / "state" / "report_emailed.json"
# Standalone cron/Discord sessions do not always source wc_env.sh.
_gcloud_bin = Path("/home/trido/google-cloud-sdk/bin")
if _gcloud_bin.is_dir():
    os.environ["PATH"] = f"{_gcloud_bin}:{os.environ.get('PATH', '')}"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path, missing):
    if not path.exists():
        return missing
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"state malformed: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"state malformed: {path}: root must be an object")
    return data


def save_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)


def channel_done(record: dict, channel: str, sha: str) -> bool:
    value = record.get(channel)
    return (isinstance(value, dict) and value.get("status") == "delivered"
            and value.get("sha256") == sha and bool(value.get("delivered_at")))


def complete(record: dict, sha: str) -> bool:
    return (record.get("sha256") == sha
            and bool(record.get("artifact_validated_at"))
            and channel_done(record, "discord", sha)
            and channel_done(record, "email", sha))


def run_checked(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


# Period-return gate (D3, job Taylor_20260919_033902) — chỉ áp báo cáo SpaceX investor-facing.
# Bug đã xác nhận: weekly 09-14->09-18 báo "Từ khi bắt đầu hoạt động −1,66%" trong khi canonical
# (nav_period_returns.py, dùng vốn khởi điểm thật 1B thay vì dòng đầu nav_history) = −2,177%.
# ZaloPay KHÔNG áp (kênh nội bộ, không gửi nhà đầu tư ngoài) — xem coding_guidelines §21/§28.
PERIOD_RETURN_TOL_PP = 0.05  # điểm % — nhỏ hơn rounding hiển thị (2 chữ số) nhưng đủ rộng cho làm tròn


def _is_spacex_investor_report(report: Path) -> bool:
    name = report.name
    if "SpaceX" in name and "ZaloPay" not in name:
        return True
    try:
        head = report.read_text(encoding="utf-8", errors="ignore")[:2000]
    except OSError:
        return False
    m = re.search(r"\*\*Đối tượng:\*\*\s*(.+)", head)
    return bool(m and "nhà đầu tư ngoài" in m.group(1) and "không" not in m.group(1).lower())


def _extract_report_date(name: str) -> str | None:
    """Ngày dùng làm --report-date cho nav_period_returns.py, suy từ TÊN FILE (không đọc BQ)."""
    full_dates = re.findall(r"\d{4}-\d{2}-\d{2}", name)
    if full_dates:
        return max(full_dates)  # weekly "..._to_YYYY-MM-DD": lấy ngày cuối kỳ (so sánh chuỗi ISO OK)
    ym = re.search(r"(\d{4})-(\d{2})(?!-\d)", name)
    if ym:
        year, month = int(ym.group(1)), int(ym.group(2))
        last_day = calendar.monthrange(year, month)[1]
        return f"{year:04d}-{month:02d}-{last_day:02d}"
    return None


def _parse_inception_return_pct(text: str) -> float | None:
    """Đọc dòng 'Từ khi bắt đầu hoạt động' trong bảng '### 3.2 Hiệu suất lũy kế', cột SpaceX
    (cột thứ 2). Định dạng thật: '| Từ khi bắt đầu hoạt động (01/07 → 18/09) | −1,66% | ... |'
    (dấu trừ Unicode U+2212, thập phân dấu phẩy)."""
    for line in text.splitlines():
        stripped = line.strip()
        if "Từ khi bắt đầu hoạt động" in stripped and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 2:
                return None
            m = re.search(r"([+\-−]?[\d.,]+)\s*%", cells[1])
            if not m:
                return None
            num = m.group(1).replace("−", "-").replace(",", ".")
            try:
                return float(num)
            except ValueError:
                return None
    return None


def _check_period_returns(report: Path) -> None:
    """BLOCK nếu 'Từ khi bắt đầu hoạt động' lệch canonical (nav_period_returns.py) >= tolerance.
    Mọi trường hợp KHÔNG xác định được (không phải SpaceX investor-facing, không suy được
    report-date, không parse được bảng, nav_period_returns.py lỗi/thiếu data) → WARN, KHÔNG BLOCK
    (fail-open — coding_guidelines §28: không suy diễn từ sự vắng mặt/thiếu dữ liệu)."""
    if not _is_spacex_investor_report(report):
        return

    report_date = _extract_report_date(report.name)
    if report_date is None:
        print(f"report_delivery_gate: WARN period-return check — không suy được report-date từ "
              f"tên file {report.name}, bỏ qua", file=sys.stderr)
        return

    try:
        text = report.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"report_delivery_gate: WARN period-return check — không đọc được {report}: {exc}",
              file=sys.stderr)
        return

    reported_pct = _parse_inception_return_pct(text)
    if reported_pct is None:
        print(f"report_delivery_gate: WARN period-return check — không parse được dòng 'Từ khi "
              f"bắt đầu hoạt động' trong bảng Hiệu suất lũy kế của {report.name}, bỏ qua",
              file=sys.stderr)
        return

    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "nav_period_returns.py"),
             "--account", "SpaceX", "--report-date", report_date],
            check=True, capture_output=True, text=True)
        canonical = json.loads(proc.stdout)["inception"]["return_pct"]
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as exc:
        print(f"report_delivery_gate: WARN period-return check — nav_period_returns.py lỗi/thiếu "
              f"data ({exc}), bỏ qua (fail-open)", file=sys.stderr)
        return

    diff = abs(reported_pct - canonical)
    if diff >= PERIOD_RETURN_TOL_PP:
        raise RuntimeError(
            f"period-return BLOCK ({report.name}): bảng ghi 'Từ khi bắt đầu hoạt động' = "
            f"{reported_pct:+.2f}%, canonical (nav_period_returns.py --account SpaceX "
            f"--report-date {report_date}) = {canonical:+.3f}% — lệch {diff:.3f}pp >= "
            f"{PERIOD_RETURN_TOL_PP}pp tolerance")
    print(f"report_delivery_gate: period-return PASS ({report.name}): {reported_pct:+.2f}% vs "
          f"canonical {canonical:+.3f}% (lệch {diff:.3f}pp)")


def deliver(report: Path, state_path: Path, topic: str, notify_script: Path,
            email_script: Path, skip_validation: bool = False) -> int:
    report = report.resolve()
    if not report.is_file() or report.suffix.lower() != ".md":
        print(f"report_delivery_gate: invalid report: {report}", file=sys.stderr)
        return 2

    state_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            state = load_json(state_path, {"version": 1, "reports": {}})
            reports = state.setdefault("reports", {})
            if not isinstance(reports, dict):
                raise RuntimeError("state malformed: reports must be an object")
            sha = digest(report)
            key = report.name
            record = reports.get(key, {})
            if not isinstance(record, dict) or record.get("sha256") != sha:
                record = {"path": str(report), "sha256": sha, "created_at": now(),
                          # cây nào đã giao — sổ dùng chung thì provenance phải nằm trong entry,
                          # không suy lại được từ trạng thái đĩa về sau
                          "delivered_by_tree": str(RUNNING_TREE)}
                reports[key] = record

            if complete(record, sha):
                print(f"report_delivery_gate: COMPLETE (idempotent) {key}")
                return 0

            if not record.get("artifact_validated_at"):
                if not skip_validation:
                    run_checked([sys.executable, str(ROOT / "bin" / "report_return_gate.py"),
                                 "--report", str(report)])
                    _check_period_returns(report)
                record["artifact_validated_at"] = now()
                save_atomic(state_path, state)

            if not channel_done(record, "discord", sha):
                body = report.read_text(encoding="utf-8")
                run_checked([str(notify_script), body, topic])
                record["discord"] = {"status": "delivered", "delivered_at": now(),
                                     "sha256": sha, "topic": topic}
                save_atomic(state_path, state)

            if not channel_done(record, "email", sha):
                # The exact hash already passed the same return gate above while this process
                # holds the delivery lock. Avoid running the expensive BQ gate a second time;
                # send_report_email records this explicit, auditable bypass reason.
                run_checked([sys.executable, str(email_script), str(report),
                             "--skip-return-gate",
                             f"report_delivery_gate already validated sha256={sha}"])
                record["email"] = {"status": "delivered", "delivered_at": now(),
                                   "sha256": sha}
                save_atomic(state_path, state)
                # Keep the old email backstop idempotent during migration.
                legacy = load_json(LEGACY_EMAIL_STATE, {})
                legacy[key] = dt.datetime.now().astimezone().date().isoformat()
                save_atomic(LEGACY_EMAIL_STATE, legacy)

            record["completed_at"] = now()
            save_atomic(state_path, state)
            print(f"report_delivery_gate: COMPLETE {key} (validated + Discord + email)")
            return 0
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            print(f"report_delivery_gate: INCOMPLETE — {exc}", file=sys.stderr)
            return 1


def status(report: Path, state_path: Path) -> int:
    try:
        sha = digest(report)
        state = load_json(state_path, {"reports": {}})
        record = state.get("reports", {}).get(report.name, {})
    except (OSError, RuntimeError) as exc:
        print(f"INCOMPLETE: {exc}", file=sys.stderr)
        return 1
    if complete(record, sha):
        print(f"COMPLETE {report.name}")
        return 0
    print(f"INCOMPLETE {report.name}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("report", type=Path)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--state", type=Path, default=DEFAULT_STATE)
    ap.add_argument("--topic", default="trading_report")
    ap.add_argument("--notify-script", type=Path, default=ROOT / "bin" / "notify_thread.sh")
    ap.add_argument("--email-script", type=Path, default=ROOT / "bin" / "send_report_email.py")
    ap.add_argument("--skip-validation", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    return status(args.report.resolve(), args.state.resolve()) if args.status else deliver(
        args.report, args.state.resolve(), args.topic, args.notify_script.resolve(),
        args.email_script.resolve(), args.skip_validation)


if __name__ == "__main__":
    raise SystemExit(main())
