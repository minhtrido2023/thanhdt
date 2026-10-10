#!/usr/bin/env python3
"""Bộ ĐỘT BIẾN cho bản vá chuẩn tỉ suất tổng 2026-10-10 (GIPS/tax-lot).

Mỗi đột biến đảo ĐÚNG MỘT dòng vá trong `dividend_adjusted_return.py` / `report_return_gate.py`
về hành vi cũ, rồi chạy selfcheck nhúng của file đó trên BẢN SAO: selfcheck phải ĐỎ. Đột biến
sống = một dòng vá không có assertion nào canh.

Không nằm trong `run_selfchecks.sh` (tên file cố ý KHÔNG khớp `*selfcheck*`): chạy N lần selfcheck
nên chậm, và nó kiểm bộ TEST chứ không kiểm code. Chạy tay khi sửa hai file trên:

    python3 mike/bin/total_return_mutants.py            # rc=0 ⇔ baseline xanh VÀ mọi đột biến chết
"""
import os
import shutil
import subprocess
import sys
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
DAR, RRG = "dividend_adjusted_return.py", "report_return_gate.py"

# (tên, ca, file, đoạn gốc — phải xuất hiện ĐÚNG 1 lần, đoạn thay)
MUTANTS = [
    ("noise_never", "CA1", DAR, "NOISE_AMP_MULT = 1.5\n", "NOISE_AMP_MULT = 0.0\n"),
    ("noise_on_lookup_error", "CA1", DAR,
     "            continue                               # KHÔNG tra được ⇒ không được phép gọi là nhiễu\n",
     "            row = None\n"),
    ("noise_any_size", "CA1", DAR,
     "              and 0 < adj.ratio_jump <= NOISE_AMP_MULT * adj.ratio_noise_amp):",
     "              and True):"),
    ("solver_no_vendor_witness", "CA1", DAR,
     "            if val <= 0 or not (ok_ratio or ok_vendor):", "            if val <= 0 or not ok_ratio:"),
    ("solver_no_sanity", "CA1", DAR,
     "            if val <= 0 or not (ok_ratio or ok_vendor):", "            if val <= 0:"),
    ("unverified_old_definition", "CA1", DAR,
     'return [a for a in self.adjustments if not getattr(a, "resolved", False)]',
     'return [a for a in self.adjustments if a.kind != "CASH_CONFIRMED"]'),
    ("no_vendor_union", "CA1", DAR,
     "    warnings = _add_vendor_only_events(adjs, tickers, start, end)\n", "    warnings = []\n"),
    ("lagged_jump_not_merged", "CA1", DAR,
     "                and _lag_completes(v, looked[id(v)][0], adj):", "                and False:"),
    ("lagged_jump_merged_blindly", "CA1", DAR,
     "    return abs(got / want - 1.0) <= LAG_TOL\n", "    return True\n"),
    ("a2_ignores_vendor_cash", "CA1", DAR, "            changed = []\n", "            pass\n"),
    ("div_not_rebased", "CA4", DAR,
     "        return self.cash_per_share / self.frame_factor\n", "        return self.cash_per_share\n"),
    ("cost_not_rebased", "CA4", DAR, "            cost = cost / mult\n", "            pass\n"),
    ("frame_guess_when_undeclared", "CA4", DAR,
     '        if cost_frame not in ("purchase", "current"):', "        if False:"),
    ("frame_excludes_own_leg", "CA4", DAR,
     "            for j, ok in zip(evs[i:], known[i:]):", "            for j, ok in zip(evs[i + 1:], known[i + 1:]):"),
    ("rights_counted_as_free", "CA4", DAR, "            if method in FREE_SHARE_ISS:", "            if True:"),
    ("mult_conflict_ignored", "CA4", DAR,
     "        if abs(adj.share_multiplier - (1.0 + free)) > MULT_TOL:", "        if False:"),
    ("unknown_later_event_ok", "CA4", DAR,
     "            return False                               # không nguồn nào nói nó là tiền hay cổ phiếu\n",
     "            return True\n"),
    ("nonfree_iss_called_stock", "CA4", DAR, '                        else "ISS_NONFREE")', '                        else "STOCK_CONFIRMED")'),
    ("vendor_multiplier_dropped", "CA4", DAR,
     "    elif free > 0:\n        adj.share_multiplier = 1.0 + free\n", "    elif False:\n        pass\n"),
    ("stock_step_loose_tolerance", "CA2", DAR,
     "        elif abs(c1 - c0) <= max(1.0, 1e-3 * q1):", "        elif abs(c1 - c0) <= max(p1, 1.0):"),
    ("blank_reads_kept", "CA2", DAR,
     "    return {sym: _drop_blank_reads(rows) for sym, rows in out.items()}\n", "    return out\n"),
    ("entitled_falls_to_exdate", "CA2", DAR,
     '        if adj.last_cum_date in getattr(qmap, "days", ()):', "        if False:"),

    ("noise_treated_as_event", "CA1", RRG,
     '        if getattr(a, "kind", "") == "RATIO_NOISE":\n            continue', "        if False:\n            continue"),
    ("gate_issues_expectation_anyway", "CA2", RRG, "            if tk in blockers:\n", "            if False:\n"),
    ("unresolved_event_not_blocked", "CA2", RRG,
     '        if not getattr(a, "resolved", a.cash_per_share > 0):', "        if False:"),
    ("unclaimed_step_ignored", "CA2", RRG,
     '            if i in claimed.get(tk, set()) or st["kind"] not in ("cash", "stock", "cash+stock"):',
     "            if True:"),
    ("resolved_vs_broker_step_unchecked", "CA2", RRG, "            if bad_cash or bad_mult:", "            if False:"),
    ("unobservable_treated_as_clean", "CA2", RRG,
     '    if not covered or any(st["kind"] in ("buy", "other") for _, st in win):',
     '    if any(st["kind"] in ("buy", "other") for _, st in win):'),
    ("lookup_failed_always_blocks", "CA2", RRG, '            if obs["kind"] != "none":', "            if True:"),
    ("claim_order_by_date_only", "CA2", RRG,
     '    for a in sorted(adjs, key=lambda x: (not getattr(x, "resolved", False), x.ex_date)):',
     "    for a in sorted(adjs, key=lambda x: x.ex_date):"),
    ("prose_unresolved_not_blocked", "CA2", RRG,
     "        elif tk in unresolved_tk and unresolved_tk[tk] not in unresolved_published:", "        elif False:"),
    ("pre_ex_any_amount", "CA2", RRG, '                and abs(cash - step["cash"]) <= 1.0:', "                and True:"),
    ("pre_ex_counts_income", "CA2", RRG,
     '            deducted[tk] = deducted.get(tk, 0.0) + g\n            notes.append(f"{tk}: broker đã trừ',
     '            deducted[tk] = deducted.get(tk, 0.0) + g\n            out[tk] = out.get(tk, 0.0) + g\n'
     '            notes.append(f"{tk}: broker đã trừ'),
    ("addback_ignored", "CA2", RRG,
     "    raw_cost = cost_price + addback_ps\n", "    raw_cost = cost_price + gross_ps\n"),
    ("lookback_fixed_120d", "CA2", RRG,
     "    return min(floor, days[0]) if days else floor\n", "    return floor\n"),
    ("price_always_close", "CA2", RRG,
     '    return (price, "Price") if later_events else (close, "Close")\n', '    return (close, "Close")\n'),
    ("excluded_skipped", "CA3", RRG,
     "            if tk in excl:\n                excluded_keys[key] = lb\n",
     "            if tk in excl:\n                continue\n"),
    ("excluded_in_total", "CA3", RRG,
     "            if tk not in excl:\n                tot_pl += pl\n", "            if True:\n                tot_pl += pl\n"),
    ("excluded_prose_checked", "CA3", RRG,
     "        if key not in excluded_keys:\n            by_ticker.setdefault(key[0], []).append((lb, exp))\n",
     "        if True:\n            by_ticker.setdefault(key[0], []).append((lb, exp))\n"),
    ("gate_div_not_rebased", "CA4", RRG,
     "        g = a.cash_per_share_now * phi\n", "        g = a.cash_per_share * phi\n"),
    ("no_dilution", "CA4", RRG, '            phi *= st["q0"] / st["q1"]\n', "            phi *= 1.0\n"),
    ("closed_holding_counted", "CA4", RRG,
     "        if cur and a.ex_date < cur[0][0][:10]:\n", "        if False:\n"),
    ("ticker_regex_letters_only", "TV1", RRG, '_TK = r"[A-Z][A-Z0-9]{2}"\n', '_TK = r"[A-Z]{3}"\n'),
]


def _selfcheck(workdir: str, fname: str) -> int:
    env = dict(os.environ, PYTHONPATH=BIN + os.pathsep + os.environ.get("PYTHONPATH", ""),
               MIKE_BOT_TEST_MODE="1")
    return subprocess.run([sys.executable, os.path.join(workdir, fname), "--selfcheck"],
                          env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode


def main() -> int:
    # bản sao nằm DƯỚI bin/ để `wc_paths.find_wc_root(__file__)` của cổng vẫn tìm ra gốc
    work = tempfile.mkdtemp(prefix=".total_return_mutants_", dir=BIN)
    src = {f: open(os.path.join(BIN, f), encoding="utf-8").read() for f in (DAR, RRG)}
    survivors, broken = [], []
    try:
        for f, text in src.items():
            open(os.path.join(work, f), "w", encoding="utf-8").write(text)
        base = {f: _selfcheck(work, f) for f in (DAR, RRG)}
        print(f"baseline (không đột biến): {base}")
        if any(base.values()):
            print("❌ baseline ĐỎ — mọi kết luận 'đột biến chết' phía dưới sẽ vô nghĩa, dừng.")
            return 2
        for name, case, f, old, new in MUTANTS:
            n = src[f].count(old)
            if n != 1:
                broken.append(name)
                print(f"  ?? {name:34s} [{case}] đoạn gốc xuất hiện {n} lần (cần 1) — đột biến HỎNG")
                continue
            open(os.path.join(work, f), "w", encoding="utf-8").write(src[f].replace(old, new))
            # đột biến ở `dar` có thể chỉ lộ qua selfcheck của cổng (cổng import bản sao `dar`)
            rcs = [_selfcheck(work, f)] + ([_selfcheck(work, RRG)] if f == DAR else [])
            open(os.path.join(work, f), "w", encoding="utf-8").write(src[f])
            dead = any(rcs)
            if not dead:
                survivors.append(name)
            print(f"  {'CHẾT' if dead else 'SỐNG'} {name:34s} [{case}] {f} rc={rcs}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"\n{len(MUTANTS)} đột biến: {len(MUTANTS) - len(survivors) - len(broken)} chết, "
          f"{len(survivors)} SỐNG {survivors}, {len(broken)} hỏng {broken}")
    return 1 if (survivors or broken) else 0


if __name__ == "__main__":
    sys.exit(main())
