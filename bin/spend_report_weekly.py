#!/usr/bin/env python3
"""spend_report_weekly.py [--dry-run]

Weekly spend/usage report for CEO review.

The report reuses spend_report.py measurement logic, compares against the last
weekly row in state/spend_history.csv, generates PNG charts, and sends an HTML
email with the Markdown report attached. It is idempotent per report date via
state/spend_report_emailed.json.
"""
import argparse
import csv
import datetime
import json
import os
import subprocess
import sys
import time

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(BIN_DIR)

sys.path.insert(0, BIN_DIR)
import spend_report  # noqa: E402

CATEGORIES = ["research", "production", "ops-coordination", "other"]
CATEGORY_LABELS = {
    "research": "Research",
    "production": "Production",
    "ops-coordination": "Ops",
    "other": "Other",
}
HISTORY_COLUMNS = [
    "date", "days",
    "research_jobs", "research_kb", "research_h",
    "production_jobs", "production_kb", "production_h",
    "ops_jobs", "ops_kb", "ops_h",
    "other_jobs", "other_kb", "other_h",
    "sonnet_jobs", "opus_jobs", "fable_jobs", "default_jobs",
    "feat", "fix", "docs", "chore", "refactor", "test", "other_commits",
    "retried_jobs", "extra_attempts", "resume_jobs", "cache_hit_pct",
]
COMMIT_COLUMNS = ["feat", "fix", "docs", "chore", "refactor", "test", "other_commits"]


def today_ict():
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    except Exception:
        return datetime.date.today()


def parse_args(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("SPEND_REPORT_ROOT", DEFAULT_ROOT))
    ap.add_argument("--report-dir")
    ap.add_argument("--state-dir")
    ap.add_argument("--report-date", type=lambda s: datetime.date.fromisoformat(s))
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--dry-run", action="store_true")
    return ap.parse_args(argv)


def _num(row, key):
    try:
        return float(row.get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


def _int(row, key):
    return int(_num(row, key))


def compute_summary(root, days):
    since_ts = int(time.time()) - days * 86400
    spend_report.ROOT = root
    job_buckets, agent_effort, retry_stats = spend_report._scan_jobs(since_ts)
    cache_usage = spend_report._scan_cache_usage(since_ts)
    commit_counts, commit_total = spend_report._scan_commits(days)

    empty = {"jobs": 0, "log_bytes": 0, "duration_s": 0, "agents": {}, "models": {}}
    categories = {}
    total_jobs = 0
    total_hours = 0.0
    total_log_kb = 0
    total_models = {m: 0 for m in spend_report.MODELS + spend_report.PROVIDER_KEYS + ["other-provider"]}
    for cat in CATEGORIES:
        b = job_buckets.get(cat, empty)
        hours = b["duration_s"] / 3600
        log_kb = b["log_bytes"] // 1024
        categories[cat] = {
            "jobs": b["jobs"],
            "hours": hours,
            "log_kb": log_kb,
            "agents": b["agents"],
            "models": b["models"],
        }
        total_jobs += b["jobs"]
        total_hours += hours
        total_log_kb += log_kb
        for model, n in b["models"].items():
            total_models[model] = total_models.get(model, 0) + n

    claude_counts = {
        model: total_models.get(model, 0)
        for model in spend_report.MODELS
    }
    claude_jobs = sum(claude_counts.values())
    offload_jobs = sum(total_models.get(p, 0) for p in spend_report.PROVIDER_KEYS + ["other-provider"])
    offload_pct = 100 * offload_jobs / total_jobs if total_jobs else 0
    fable_pct = 100 * claude_counts.get("fable", 0) / claude_jobs if claude_jobs else 0

    warnings = []
    if fable_pct >= 30:
        warnings.append(
            f"Fable = {fable_pct:.0f}% of Claude dispatches — cao hơn ngưỡng 30%, "
            "cần rà soát model routing."
        )
    for agent in sorted(agent_effort, key=lambda a: -sum(agent_effort[a].values())):
        efforts = agent_effort[agent]
        n = sum(efforts.values())
        high_pct = 100 * efforts.get("high", 0) / n if n else 0
        if n >= 10 and high_pct >= 70:
            warnings.append(
                f"effort=high của {agent} là {high_pct:.0f}% (n={n}) — trên ngưỡng 70%."
            )
    retry_pct = (
        100 * retry_stats["extra_attempts"] / total_jobs
        if total_jobs and retry_stats["extra_attempts"]
        else 0
    )
    if total_jobs >= spend_report.RETRY_WARN_MIN_JOBS and retry_pct >= spend_report.RETRY_WARN_PCT:
        warnings.append(
            f"Có {retry_stats['retried_jobs']} job chạy attempt >1, "
            f"{retry_stats['extra_attempts']} lần compute thêm ({retry_pct:.0f}% của tổng job)."
        )

    return {
        "categories": categories,
        "agent_effort": agent_effort,
        "retry_stats": retry_stats,
        "cache_usage": cache_usage,
        "commit_counts": commit_counts,
        "commit_total": commit_total,
        "total_jobs": total_jobs,
        "total_hours": total_hours,
        "total_log_kb": total_log_kb,
        "total_models": total_models,
        "claude_counts": claude_counts,
        "claude_jobs": claude_jobs,
        "offload_jobs": offload_jobs,
        "offload_pct": offload_pct,
        "warnings": warnings,
    }


def read_history(state_dir):
    path = os.path.join(state_dir, "spend_history.csv")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def previous_row(rows, report_date):
    target = (report_date - datetime.timedelta(days=7)).isoformat()
    exact = [r for r in rows if r.get("date") == target]
    if exact:
        return exact[-1]
    older = [r for r in rows if r.get("date") and r["date"] < report_date.isoformat()]
    if not older:
        return None
    return sorted(older, key=lambda r: r["date"])[-1]


def row_from_summary(report_date, days, summary):
    cat = summary["categories"]
    c = summary["claude_counts"]
    cc = summary["commit_counts"]
    cache_hit = summary["cache_usage"]["hit_pct"]
    return {
        "date": report_date.isoformat(),
        "days": days,
        "research_jobs": cat["research"]["jobs"],
        "research_kb": cat["research"]["log_kb"],
        "research_h": f"{cat['research']['hours']:.1f}",
        "production_jobs": cat["production"]["jobs"],
        "production_kb": cat["production"]["log_kb"],
        "production_h": f"{cat['production']['hours']:.1f}",
        "ops_jobs": cat["ops-coordination"]["jobs"],
        "ops_kb": cat["ops-coordination"]["log_kb"],
        "ops_h": f"{cat['ops-coordination']['hours']:.1f}",
        "other_jobs": cat["other"]["jobs"],
        "other_kb": cat["other"]["log_kb"],
        "other_h": f"{cat['other']['hours']:.1f}",
        "sonnet_jobs": c.get("sonnet", 0),
        "opus_jobs": c.get("opus", 0),
        "fable_jobs": c.get("fable", 0),
        "default_jobs": c.get("default", 0),
        "feat": cc.get("feat", 0),
        "fix": cc.get("fix", 0),
        "docs": cc.get("docs", 0),
        "chore": cc.get("chore", 0),
        "refactor": cc.get("refactor", 0),
        "test": cc.get("test", 0),
        "other_commits": cc.get("other", 0),
        "retried_jobs": summary["retry_stats"]["retried_jobs"],
        "extra_attempts": summary["retry_stats"]["extra_attempts"],
        "resume_jobs": summary["retry_stats"]["resume_jobs"],
        "cache_hit_pct": f"{cache_hit:.1f}" if cache_hit is not None else "",
    }


def _ensure_history_header(path):
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        try:
            header = next(csv.reader(f))
        except StopIteration:
            header = []
    missing = [col for col in HISTORY_COLUMNS if col not in header]
    if not missing:
        return
    tmp = path + ".tmp"
    with open(path, encoding="utf-8") as f, open(tmp, "w", encoding="utf-8") as out:
        writer = csv.writer(out)
        first = True
        for row in csv.reader(f):
            if first:
                writer.writerow(header + missing)
                first = False
            else:
                writer.writerow(row + [""] * len(missing))
    os.replace(tmp, path)


def append_history(state_dir, row):
    path = os.path.join(state_dir, "spend_history.csv")
    os.makedirs(state_dir, exist_ok=True)
    rows = read_history(state_dir)
    if any(r.get("date") == row["date"] for r in rows):
        return False
    _ensure_history_header(path)
    is_new = not os.path.isfile(path)
    with open(path, "a", encoding="utf-8") as f:
        if is_new:
            f.write(",".join(HISTORY_COLUMNS) + "\n")
        writer = csv.DictWriter(f, fieldnames=HISTORY_COLUMNS)
        writer.writerow(row)
    return True


def _save_grouped_bar(path, labels, current, previous, title, ylabel):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"Không tạo được chart do thiếu matplotlib: {exc}", file=sys.stderr)
        return False
    width = 0.35
    x = list(range(len(labels)))
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=150)
    ax.bar([i - width / 2 for i in x], current, width, label="This week", color="#1f6f78")
    if previous is not None:
        ax.bar([i + width / 2 for i in x], previous, width, label="Prev week", color="#d8a14a")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return True


def _save_pie(path, labels, values, title):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"Không tạo được chart do thiếu matplotlib: {exc}", file=sys.stderr)
        return False
    if not values or sum(values) <= 0:
        return False
    colors = ["#1f6f78", "#d8a14a", "#7a5c8e", "#4f7a9c", "#9a8f75", "#b0555a"]
    fig, ax = plt.subplots(figsize=(5.4, 4.0), dpi=150)
    ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=90, colors=colors[:len(values)])
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return True


def make_charts(report_date, summary, previous, report_dir):
    charts_dir = os.path.join(report_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)
    base = f"spend_report_weekly_{report_date.isoformat()}"

    labels = [CATEGORY_LABELS[c] for c in CATEGORIES]
    hours = [summary["categories"][c]["hours"] for c in CATEGORIES]
    jobs = [summary["categories"][c]["jobs"] for c in CATEGORIES]
    prev_hours = None
    prev_jobs = None
    prev_commits = None
    if previous:
        prev_hours = [
            _num(previous, c + "_h")
            for c in ["research", "production", "ops", "other"]
        ]
        prev_jobs = [
            _int(previous, c + "_jobs")
            for c in ["research", "production", "ops", "other"]
        ]
        prev_commits = [_int(previous, c) for c in COMMIT_COLUMNS]

    hour_path = os.path.join(charts_dir, base + "_hours.png")
    job_path = os.path.join(charts_dir, base + "_jobs.png")
    model_path = os.path.join(charts_dir, base + "_models.png")
    commit_path = os.path.join(charts_dir, base + "_commits.png")

    _save_grouped_bar(hour_path, labels, hours, prev_hours, "Compute hours by category", "Hours")
    _save_grouped_bar(job_path, labels, jobs, prev_jobs, "Jobs by category", "Jobs")

    model_labels = []
    model_values = []
    for model in spend_report.MODELS + spend_report.PROVIDER_KEYS:
        n = summary["total_models"].get(model, 0)
        if n:
            model_labels.append(model)
            model_values.append(n)
    _save_pie(model_path, model_labels, model_values, "Model/provider mix")

    commit_labels = COMMIT_COLUMNS
    commit_values = [summary["commit_counts"].get(c, 0) for c in COMMIT_COLUMNS]
    _save_grouped_bar(commit_path, commit_labels, commit_values, prev_commits, "Commits by type", "Commits")

    return {
        "hours": "charts/" + os.path.basename(hour_path),
        "jobs": "charts/" + os.path.basename(job_path),
        "models": "charts/" + os.path.basename(model_path),
        "commits": "charts/" + os.path.basename(commit_path),
    }


def _md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return lines


def _pct(cur, prev):
    if prev in (None, 0):
        return "N/A"
    return f"{(cur - prev) / prev * 100:+.0f}%"


def _model_mix_str(models):
    if not models:
        return "N/A"
    return ", ".join(f"{k}={100*v/sum(models.values()):.0f}%" for k, v in sorted(models.items()))


def build_report(report_date, summary, previous, charts):
    lines = [
        f"# Tổng kết sử dụng tuần qua ({report_date.isoformat()})",
        "",
        "Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ "
        "`bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần "
        "trước được tạo tự động.",
        "",
        "## Tóm tắt",
        "",
    ]
    summary_rows = [
        ["Số job headless dispatch", summary["total_jobs"]],
        ["Compute ước tính", f"{summary['total_hours']:.1f}h"],
        ["Log KB", summary["total_log_kb"]],
        ["Offload provider khác Claude", f"{summary['offload_jobs']} job ({summary['offload_pct']:.0f}%)"],
        ["Retry / compute thêm", f"{summary['retry_stats']['extra_attempts']} attempt"],
        ["Commits", summary["commit_total"]],
    ]
    lines += _md_table(["Chỉ số", "Giá trị"], summary_rows)
    lines.append("")

    prev_date = previous.get("date") if previous else None
    lines.append("## So sánh với tuần trước")
    lines.append("")
    if previous:
        prev_jobs = _int(previous, "research_jobs") + _int(previous, "production_jobs") + \
            _int(previous, "ops_jobs") + _int(previous, "other_jobs")
        prev_hours = _num(previous, "research_h") + _num(previous, "production_h") + \
            _num(previous, "ops_h") + _num(previous, "other_h")
        prev_kb = _int(previous, "research_kb") + _int(previous, "production_kb") + \
            _int(previous, "ops_kb") + _int(previous, "other_kb")
        prev_commits = sum(_int(previous, c) for c in COMMIT_COLUMNS)
        rows = [
            ["Số job", summary["total_jobs"], prev_jobs, f"{summary['total_jobs'] - prev_jobs:+d}", _pct(summary["total_jobs"], prev_jobs)],
            ["Compute h", f"{summary['total_hours']:.1f}", f"{prev_hours:.1f}", f"{summary['total_hours'] - prev_hours:+.1f}", _pct(summary["total_hours"], prev_hours)],
            ["Log KB", summary["total_log_kb"], prev_kb, f"{summary['total_log_kb'] - prev_kb:+d}", _pct(summary["total_log_kb"], prev_kb)],
            ["Commits", summary["commit_total"], prev_commits, f"{summary['commit_total'] - prev_commits:+d}", _pct(summary["commit_total"], prev_commits)],
        ]
        for model in ["sonnet", "opus", "fable", "default"]:
            cur = summary["claude_counts"].get(model, 0)
            pv = _int(previous, model + "_jobs")
            rows.append([f"Claude {model}", cur, pv, f"{cur - pv:+d}", _pct(cur, pv)])
        lines += _md_table(["Chỉ số", "Tuần này", f"Tuần trước ({prev_date})", "Thay đổi", "%"], rows)
    else:
        lines.append("Chưa có dữ liệu lịch sử cho tuần trước. Báo cáo này sẽ trở thành baseline "
                     "cho lần so sánh tuần sau.")
    lines.append("")

    lines += [
        "## Phân bổ compute / job theo nhóm",
        "",
        f"![Compute hours by category]({charts['hours']})",
        "",
        f"![Jobs by category]({charts['jobs']})",
        "",
    ]

    lines.append("## Chi tiết theo nhóm")
    lines.append("")
    detail_rows = []
    for cat in CATEGORIES:
        c = summary["categories"][cat]
        detail_rows.append([
            CATEGORY_LABELS[cat],
            c["jobs"],
            f"{c['hours']:.1f}",
            c["log_kb"],
            _model_mix_str(c["models"]),
        ])
    lines += _md_table(["Nhóm", "Jobs", "Compute h", "Log KB", "Model mix"], detail_rows)
    lines.append("")

    lines.append("## Model / provider mix")
    lines.append("")
    lines.append(f"![Model/provider mix]({charts['models']})")
    lines.append("")

    lines.append("## Commits by type")
    lines.append("")
    lines.append(f"![Commits by type]({charts['commits']})")
    lines.append("")

    lines.append("## Token / retry watch")
    lines.append("")
    cache = summary["cache_usage"]
    if cache["prompt_tokens"]:
        lines.append(
            "- Cache hit: "
            f"**{cache['hit_pct']:.0f}%** của prompt tokens "
            f"({cache['cache_read_tokens']:,} read / {cache['prompt_tokens']:,} total)."
        )
    else:
        lines.append("- Cache hit: chưa có dữ liệu transcript trong cửa sổ.")
    retry = summary["retry_stats"]
    lines.append(
        f"- Retry / duplicate compute: **{retry['retried_jobs']} job** chạy attempt >1, "
        f"**{retry['extra_attempts']} attempt** thêm; "
        f"{retry['resume_jobs']} job có prompt resume/re-dispatch."
    )
    lines.append("")

    lines.append("## Cảnh báo effort / model / retry")
    lines.append("")
    if summary["warnings"]:
        for w in summary["warnings"]:
            lines.append(f"- ⚠ {w}")
    else:
        lines.append("- Không có cảnh báo nào vượt ngưỡng effort, fable hoặc retry.")
    lines.append("")

    lines.append("## Nhận xét của quản lý")
    lines.append("")
    lines.append("Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:")
    lines.append("")
    lines.append("- **Mức sử dụng**: tổng compute ước tính là "
                 f"**{summary['total_hours']:.1f}h** trên {summary['total_jobs']} job, "
                 f"offload provider khác Claude chiếm {summary['offload_pct']:.0f}% job.")
    if previous:
        prev_jobs = _int(previous, "research_jobs") + _int(previous, "production_jobs") + \
            _int(previous, "ops_jobs") + _int(previous, "other_jobs")
        prev_hours = _num(previous, "research_h") + _num(previous, "production_h") + \
            _num(previous, "ops_h") + _num(previous, "other_h")
        lines.append(
            "- **So với tuần trước**: job "
            f"{'tăng' if summary['total_jobs'] >= prev_jobs else 'giảm'} "
            f"{abs(summary['total_jobs'] - prev_jobs)} và compute "
            f"{'tăng' if summary['total_hours'] >= prev_hours else 'giảm'} "
            f"{abs(summary['total_hours'] - prev_hours):.1f}h. "
            "Cần theo dõi nếu compute tăng nhanh hơn số job."
        )
    lines.append("- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, "
                 "báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn "
                 "xu hướng thay vì chỉ đọc bảng số.")
    if summary["warnings"]:
        lines.append("- **Bất thường cần hành động**: " + "; ".join(summary["warnings"]) + ".")
    else:
        lines.append("- **Bất thường**: chưa phát hiện bất thường lớn ngoài biến động thường "
                     "theo khối lượng công việc.")
    lines.append("- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ "
                 "dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau "
                 "script sẽ tự so tiếp với tuần này để phát hiện drift sớm.")
    lines.append("")
    lines.append("---")
    lines.append("Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra "
                 "`state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.")
    lines.append("")
    return "\n".join(lines)


def load_sent_state(state_dir):
    path = os.path.join(state_dir, "spend_report_emailed.json")
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def is_sent(state_dir, report_date):
    data = load_sent_state(state_dir)
    return report_date.isoformat() in data.get("sent", {})


def mark_sent(state_dir, report_date, report_path, subject):
    os.makedirs(state_dir, exist_ok=True)
    path = os.path.join(state_dir, "spend_report_emailed.json")
    data = load_sent_state(state_dir)
    data.setdefault("sent", {})[report_date.isoformat()] = {
        "report": os.path.basename(report_path),
        "subject": subject,
        "sent_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def send_email(report_path, subject, dry_run=False):
    cmd = [
        sys.executable,
        os.path.join(BIN_DIR, "send_report_email.py"),
        report_path,
        "--subject", subject,
        "--skip-return-gate", "spend/usage report",
    ]
    if dry_run:
        print(f"[dry-run] Sẽ gửi email: {subject}")
        return
    subprocess.run(cmd, check=True)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    root = os.path.abspath(args.root)
    report_dir = os.path.abspath(args.report_dir or os.path.join(root, "reports"))
    state_dir = os.path.abspath(args.state_dir or os.path.join(root, "state"))
    report_date = args.report_date or today_ict()

    if not args.dry_run and is_sent(state_dir, report_date):
        print(f"Báo cáo tuần {report_date.isoformat()} đã gửi trước đó; bỏ qua.")
        return

    summary = compute_summary(root, args.days)
    rows = read_history(state_dir)
    previous = previous_row(rows, report_date)

    os.makedirs(report_dir, exist_ok=True)
    charts = make_charts(report_date, summary, previous, report_dir)
    report_path = os.path.join(report_dir, f"spend_report_weekly_{report_date.isoformat()}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(build_report(report_date, summary, previous, charts))
    print(f"Đã tạo {report_path}")

    row = row_from_summary(report_date, args.days, summary)
    if not args.dry_run:
        appended = append_history(state_dir, row)
        if appended:
            print(f"Đã thêm lịch sử {report_date.isoformat()} vào state/spend_history.csv")

    subject = f"Tổng kết sử dụng tuần qua ({report_date.isoformat()})"
    if args.dry_run:
        send_email(report_path, subject, dry_run=True)
        print("[dry-run] Không gửi email, không ghi sent-state.")
        return

    send_email(report_path, subject)
    mark_sent(state_dir, report_date, report_path, subject)
    print("Đã gửi email và ghi sent-state.")


if __name__ == "__main__":
    main()
