#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bộ mutant cho code MỚI của nhánh feat/fund-history-lock-20261014 (kho bất biến + cổng chốt/K3 +
đính chính sổ; fund_restatement.py; giá thay --from-raw).

Mỗi mutant: chép bin/ của worktree sang /tmp, thay ĐÚNG MỘT chỗ (chuỗi phải xuất hiện đúng 1 lần),
chạy selfcheck liên quan với WC_ROOT trỏ sandbox RỖNG (không có data/) và TZ đã gỡ. Mutant "chết"
khi ít nhất một selfcheck rc != 0. In từng mutant; mutant SỐNG in kèm ghi chú.

Dùng: python3 mutants.py [--only L1,F3] [--tz Pacific/Kiritimati]
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

WT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-fundlock-1014"
EMPTY_ROOT = "/tmp/fundlock_1014/empty"
L, F, S = "nav_unit_ledger.py", "fund_restatement.py", "daily_nav_snapshot.py"
VAULT, REST, UNIT = ("nav_ledger_vault_selfcheck.py", "fund_restatement_selfcheck.py",
                     "nav_unit_ledger_selfcheck.py")

M = [
    # ---------------- kho bất biến: manifest + md5
    ("L1", L, 'if rec["md5_before"] != prev or rec["seq"] != len(out) + 1:', 'if False:',
     "bỏ kiểm chuỗi manifest", (VAULT,)),
    ("L2", L, 'if rec["md5_before"] != prev or rec["seq"] != len(out) + 1:',
     'if rec["md5_before"] != prev:', "manifest: không kiểm seq", (VAULT,)),
    ("L3", L, '    if have != last["md5"]:\n        seen =', '    if False:\n        seen =',
     "không kiểm md5 file sổ == manifest", (VAULT,)),
    ("L4", L, 'if have != last["md5_before"]:', 'if False:',
     "file lệch bất kỳ được coi là lần chốt dở", (VAULT,)),
    ("L5", L, 'if _md5(want) != last["md5"]:', 'if False:',
     "hoàn tất lần chốt dở dù dựng lại ra md5 khác", (VAULT,)),
    ("L6", L, '    if not new:\n        raise NothingToSeal(', '    if False:\n        raise NothingToSeal(',
     "chốt lần hai không có dòng mới KHÔNG bị từ chối", (VAULT,)),
    ("L7", L, 'cutoff = today - datetime.timedelta(days=1)', 'cutoff = today',
     "cho chốt dòng của HÔM NAY", (VAULT,)),
    ("L8", L, 'if asof is not None and asof > cutoff:', 'if False:',
     "--asof >= hôm nay không bị từ chối", (VAULT,)),
    ("L9", L, 'if gap not in have and _acf._is_session_day(gap):', 'if False:',
     "cổng: bỏ kiểm thiếu phiên", (VAULT,)),
    ("L10", L, 'if gap not in have and _acf._is_session_day(gap):', 'if gap not in have:',
     "cổng: cuối tuần/ngày nghỉ bị coi là thiếu phiên", (VAULT,)),
    ("L11", L, 'if session and snap < datetime.datetime.combine(d, _acf.SESSION_CLOSE_ICT):',
     'if False:', "cổng: bỏ nhánh chụp-trước-đóng-cửa (rơi xuống nhánh K3)", (VAULT,)),
    ("L12", L, 'if session and snap < datetime.datetime.combine(d, _acf.SESSION_CLOSE_ICT):',
     'if session and snap <= datetime.datetime.combine(d, _acf.SESSION_CLOSE_ICT):',
     "cổng: biên — chụp ĐÚNG 14:45:00 bị coi là trước đóng cửa", (VAULT,)),
    ("L13", L, '        elif seen != want:', '        elif False:',
     "cổng: bỏ điều kiện K3 (dòng chụp sau khi phiên kế đã đóng cửa)", (VAULT,)),
    ("L14", L, 'for key in sorted(set(accept_preclose) - set(accepted)):', 'for key in []:',
     "--accept-preclose gõ nhầm ngày không bị bắt", (VAULT,)),
    ("L15", L,
     '    _append_manifest(path, rec)                 # manifest TRƯỚC: chết ở đây ⇒ lần sau hoàn tất\n'
     '    _atomic_write(path, data)\n    return sealed, new',
     '    _atomic_write(path, data)\n    _append_manifest(path, rec)\n    return sealed, new',
     "seal: ghi file sổ TRƯỚC manifest", (VAULT,)),
    ("L16", L, '    immutable = immutable or real\n', '    pass\n',
     "thư mục dữ liệu thật không tự bật kho bất biến", (VAULT, UNIT)),
    ("L17", L, '    if real and not real_data:\n        raise SealRefused(\n            f"TỪ CHỐI chốt sổ',
     '    if False:\n        raise SealRefused(\n            f"TỪ CHỐI chốt sổ',
     "seal vào thư mục thật không cần --real-data", (VAULT, UNIT)),
    ("L18", L, '    if real and not real_data:\n        raise SealRefused(\n            f"TỪ CHỐI đính chính sổ',
     '    if False:\n        raise SealRefused(\n            f"TỪ CHỐI đính chính sổ',
     "restate vào thư mục thật không cần --real-data", (VAULT,)),
    ("L19", L, 'if not str(reason or "").strip() or not str(approved_by or "").strip():', 'if False:',
     "restate không cần lý do / người duyệt", (VAULT,)),
    ("L20", L, '            if got != want:', '            if False:',
     "restate nhận báo cáo tác động của thay đổi khác", (VAULT,)),
    ("L21", L, '            if got != want:', '            if got[:2] != want[:2]:',
     "restate: không ràng md5 sổ SAU đính chính", (VAULT,)),
    ("L22", L, '            if got != want:', '            if got[1:] != want[1:]:',
     "restate: không ràng tài khoản của báo cáo tác động", (VAULT,)),
    ("L23", L, '            if existing is None:\n                _atomic_write(archive, old)',
     '            if False:\n                _atomic_write(archive, old)',
     "restate không lưu sổ cũ", (VAULT,)),
    ("L24", L, '            if not diffs:\n                raise NothingToSeal(',
     '            if False:\n                raise NothingToSeal(',
     "restate khi không có gì khác vẫn ghi", (VAULT,)),
    ("L25", L, 'problems, accepted = seal_gate(ledger, rows[0]["date"], rows, ask)',
     'problems, accepted = [], {}', "restate bỏ qua cổng chốt", (VAULT,)),
    ("L26", L, 'if existing is not None and existing != old:', 'if False:',
     "restate: file lưu trùng tên nội dung khác không bị bắt", (VAULT,)),
    ("L27", L, 'snap = snap.astimezone(ICT).replace(tzinfo=None)', 'snap = snap.replace(tzinfo=None)',
     "balance_ts có múi giờ không quy về ICT", (VAULT,)),
    ("L28", L,
     '        _, sealed, _, _ = _vault_state(path, ledger, write=False)\n'
     '        diffs = diff_against_sealed(ledger, sealed)\n        if diffs:',
     '        _, sealed, _, _ = _vault_state(path, ledger, write=False)\n'
     '        diffs = diff_against_sealed(ledger, sealed)\n        if False:',
     "đối chiếu chỉ-đọc kho bất biến không báo lệch dòng", (VAULT,)),
    ("L29", L,
     '    diffs = diff_against_sealed(ledger, sealed)\n    if diffs:\n        raise LedgerDriftError(path, diffs)\n'
     '    if resumed and manifest[-1]["kind"] == "seal":',
     '    diffs = diff_against_sealed(ledger, sealed)\n    if False:\n        raise LedgerDriftError(path, diffs)\n'
     '    if resumed and manifest[-1]["kind"] == "seal":',
     "seal kho bất biến không báo lệch dòng đã chốt", (VAULT,)),
    ("L30", L, '        if not write:\n            raise SealIntegrityError(',
     '        if False:\n            raise SealIntegrityError(',
     "lệnh CHỈ-ĐỌC tự hoàn tất lần chốt dở (ghi file)", (VAULT,)),
    ("L31", L, 'if row["balance_ts"] is None and d == ledger[0]["date"]:', 'if row["balance_ts"] is None:',
     "cổng: dòng thiếu balance_ts được bỏ qua", (VAULT,)),
    ("L32", L, '    if not manifest:\n        if old is not None:', '    if not manifest:\n        if False:',
     "file sổ không có manifest được nhận", (VAULT,)),
    ("L33", L, 'today = datetime.datetime.now(ICT).date()', 'today = datetime.date.today()',
     "hôm nay theo TZ máy thay vì ICT (chạy cả TZ lạ)", (VAULT,)),
    ("L34", L, '    if resumed and manifest[-1]["kind"] == "seal":', '    if False:',
     "sau khi hoàn tất lần chốt dở vẫn chốt tiếp", (VAULT,)),
    ("L35", L, 'if resumed and manifest[-1]["kind"] == "restate":', 'if False:',
     "sau khi hoàn tất lần đính chính dở vẫn đính chính tiếp", (VAULT,)),
    ("L36", L, 'ask = dict(carried, **(accept_preclose or {}))', 'ask = dict(accept_preclose or {})',
     "restate quên lời nhận chụp-trước-đóng-cửa của các lần chốt trước", (VAULT,)),
    ("L37", L, '        immutable = os.path.exists(manifest_path(path))', '        immutable = False',
     "thư mục đã có manifest không tự bật kho bất biến", (VAULT,)),
    ("L38", L, '               accepted_preclose=accepted,\n               sealed_at_ict',
     '               accepted_preclose={},\n               sealed_at_ict',
     "seal không ghi lời nhận chụp-trước-đóng-cửa vào manifest", (VAULT,)),
    # ---------------- fund_restatement
    ("F1", F, 'if dev < TIER_NOTE_FROM:', 'if dev <= TIER_NOTE_FROM:', "biên 0,05 thành bậc 1", (REST,)),
    ("F2", F, 'if dev <= TIER_REISSUE_ABOVE:', 'if dev < TIER_REISSUE_ABOVE:', "biên 0,5 thành bậc 3", (REST,)),
    ("F3", F, '        return 3                    # không đo được', '        return 0                    # không đo được',
     "độ lệch không đo được xếp bậc 0", (REST,)),
    ("F4", F, 'TIER_REISSUE_ABOVE = 0.5 ', 'TIER_REISSUE_ABOVE = 5.0 ', "ngưỡng bậc 3 = 5", (REST,)),
    ("F5", F, '        devs.append(abs(nav_dev))\n        for key in HEADLINE_KEYS[kind]:',
     '        for key in HEADLINE_KEYS[kind]:', "số chính không tính lệch NAV cuối kỳ", (REST,)),
    ("F6", F, 'devs.append(abs(b[key] - a[key]))', 'devs.append(b[key] - a[key])',
     "lệch tỉ suất không lấy trị tuyệt đối", (REST,)),
    ("F7", F, '"daily": ("day", "wtd", "mtd", "inception")', '"daily": ("wtd", "mtd", "inception")',
     "báo cáo ngày không đo tỉ suất ngày", (REST,)),
    ("F8", F, 'out["headline_dev"] = max(devs) if devs else 0.0', 'out["headline_dev"] = min(devs) if devs else 0.0',
     "số chính lấy min thay vì max", (REST,)),
    ("F9", F, 'wdevs += [abs(nav_dev), abs(ret_dev)]', 'wdevs += [abs(nav_dev)]',
     "window không tính lệch tỉ suất ngày", (REST,)),
    ("F10", F, 'if meta and account in meta["who"]:', 'if meta:', "§12: báo cáo của tài khoản khác bị tính", (REST,)),
    ("F11", F, 'wdevs.append(abs(rn["nav"] / nav_old - 1) * 100 if rn else float("inf"))', 'pass',
     "báo cáo trích nguyên NAV cũ ngoài kỳ không tính vào window", (REST,)),
    ("F12", F, 'or (bool(structural) and out["tier_headline"] < 2))', 'or False)',
     "kỳ có dòng thêm/bỏ không gọi người xem", (REST,)),
    ("F13", F, '(out["tier_window"] >= 2 and out["tier_window"] > out["tier_headline"])',
     '(out["tier_window"] >= 3 and out["tier_window"] > out["tier_headline"])',
     "window bậc 2 không gọi người xem", (REST,)),
    ("F14", F, '        if bad:\n            raise RestatementError(', '        if False:\n            raise RestatementError(',
     "không kiểm expect của dòng bị sửa", (REST,)),
    ("F15", F, 'if abs(parts["nav"] - want) > NAV_INVARIANT_TOL:', 'if False:',
     "không kiểm bất biến NAV của dòng sau sửa", (REST,)),
    ("F16", F, '    if who != account:', '    if False:', "§12: file đính chính áp chéo tài khoản", (REST,)),
    ("F17", F, '            and not args.real_data):', '            and False):',
     "apply vào thư mục thật không cần --real-data", (REST,)),
    ("F18", F, 'if (bound[0], bound[1]) != (args.account, correction_md5):', 'if False:',
     "apply nhận báo cáo tác động của file đính chính khác", (REST,)),
    ("F19", F, 'if (_md5(cur_bytes), _md5(new_bytes)) != (bound[2], bound[3]):', 'if False:',
     "apply khi nav_history đã đổi từ lúc đo", (REST,)),
    ("F20", F, '    if not pending:\n        with open(log, "a"', '    if True:\n        with open(log, "a"',
     "chạy lại sau khi chết ghi bản ghi nhật ký thứ hai", (REST,)),
    ("F21", F, 'return "\\r\\n" if b"\\r\\n" in data else "\\n"', 'return "\\n"',
     "ghi lại nav_history mất CRLF", (REST,)),
    ("F22", F, '        if item["date"] in seen:', '        if False:', "một ngày hai đính chính", (REST,)),
    ("F23", F, 'for key in ("date", "reason", "evidence"):', 'for key in ("date",):',
     "đính chính không cần lý do/bằng chứng", (REST,)),
    ("F24", F, 'reissue = [r for r in affected if r["tier_headline"] == 3]',
     'reissue = [r for r in affected if r["tier_headline"] == 4]', "bậc 3 không vào hàng đợi user", (REST,)),
    ("F25", F, '"note_next_report": [r["report"] for r in affected if r["tier_headline"] == 2]',
     '"note_next_report": [r["report"] for r in affected if r["tier_headline"] >= 2]',
     "bậc 3 lẫn vào danh sách ghi chú", (REST,)),
    ("F26", F, 'if _md5(cur_bytes) == bound[3] and all(c.get("already") for c in changes):', 'if False:',
     "apply lần hai không nhận ra đã áp", (REST,)),
    ("F27", F, '"restated_md5": _md5(nul._content(new.ledger, sealed[-1]["date"])),',
     '"restated_md5": _md5(sealed_bytes),', "ledger_binding ghi sai md5 sổ sau đính chính", (REST, VAULT)),
    ("F28", F, '    if not str(args.approved_by or "").strip():', '    if False:',
     "apply không cần người duyệt", (REST,)),
    ("F29", F, 'start = end - datetime.timedelta(days=end.weekday())', 'start = end',
     "báo cáo tuần tên 1 ngày: kỳ chỉ còn 1 ngày", (REST,)),
    ("F30", F, '            if cur == new:\n', '            if False:\n',
     "replace đã áp sẵn không được nhận là already", (REST,)),
    ("F31", F, "        if a.get(d) != b.get(d):", "        if (a.get(d) or {}).get('nav') != (b.get(d) or {}).get('nav'):",
     "changed_dates chỉ so cột nav", (REST,)),
    ("F32", F, '    if dates != sorted(dates) or len(set(dates)) != len(dates):', '    if False:',
     "nav_history ngày lộn xộn/trùng được nhận", (REST,)),
    ("F33", F, '"fix_forward_only": [r["report"] for r in affected if r["tier_headline"] <= 1]',
     '"fix_forward_only": [r["report"] for r in affected if r["tier_headline"] <= 2]',
     "bậc 2 lẫn vào 'chỉ sửa từ nay'", (REST,)),
    ("F34", F, '            if item["op"] == "delete":\n                changes.append({"op": "delete", "date": item["date"], "old": None, "new": None,\n'
               '                                "already": True})\n                continue\n',
     '', "delete dòng không tồn tại không còn idempotent (ném lỗi)", (REST,)),
    # ---------------- daily_nav_snapshot --raw-price-override
    ("S1", S, '    if out and not from_raw:', '    if False:', "giá thay dùng được ở đường live", (VAULT,)),
    ("S2", S, '    if out and not str(evidence or "").strip():', '    if False:', "giá thay không cần bằng chứng", (VAULT,)),
    ("S3", S, 'not (price == price and 0 < price < float("inf"))', 'not (price == price)',
     "giá thay <= 0 / inf được nhận", (VAULT,)),
    ("S4", S, 'out[ticker.strip().upper()] = price', 'out[ticker.strip()] = price', "mã không quy về chữ hoa", (VAULT,)),
    ("S5", S, '        unknown = sorted(set(price_overrides) - set(tickers))', '        unknown = []',
     "main: giá thay cho mã không giữ không bị từ chối", (VAULT, "daily_nav_snapshot_from_raw_selfcheck.py")),
    ("S6", S, '            prices[t] = p_new\n', '            pass\n',
     "main: giá thay không được áp vào giá", (VAULT, "daily_nav_snapshot_from_raw_selfcheck.py")),
]


def run(mid, fname, old, new, desc, checks, tzs):
    tmp = tempfile.mkdtemp(prefix=f"mut_{mid}_", dir="/tmp/fundlock_1014")
    try:
        shutil.copytree(os.path.join(WT, "bin"), os.path.join(tmp, "bin"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        path = os.path.join(tmp, "bin", fname)
        with open(path, encoding="utf-8") as f:
            src = f.read()
        if src.count(old) != 1:
            return "LỖI-MUTANT", f"chuỗi gốc xuất hiện {src.count(old)} lần"
        with open(path, "w", encoding="utf-8") as f:
            f.write(src.replace(old, new))
        for tz in tzs:
            env = {k: v for k, v in os.environ.items() if k not in ("TZ", "WC_ROOT")}
            env["WC_ROOT"] = EMPTY_ROOT
            if tz:
                env["TZ"] = tz
            for chk in checks:
                p = subprocess.run([sys.executable, os.path.join(tmp, "bin", chk)], env=env,
                                   capture_output=True, text=True, timeout=900)
                if p.returncode != 0:
                    out = (p.stdout + p.stderr).strip().splitlines()
                    first = next((ln for ln in out if "FAIL" in ln or "Error" in ln), out[-1] if out else "")
                    return "chết", f"{chk} TZ={tz or 'gỡ'} rc={p.returncode}: {first[:150]}"
        return "SỐNG", ""
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--tz", action="append", default=[])
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None
    alive = bad = n = 0
    for mid, fname, old, new, desc, checks in M:
        if only and mid not in only:
            continue
        tzs = [None] + args.tz + (["Pacific/Kiritimati", "America/Los_Angeles"] if mid == "L33" else [])
        verdict, why = run(mid, fname, old, new, desc, checks, tzs)
        n += 1
        alive += verdict == "SỐNG"
        bad += verdict == "LỖI-MUTANT"
        print(f"{mid:4s} {verdict:10s} {fname:24s} {desc}" + (f"\n       ↳ {why}" if why else ""), flush=True)
    print(f"\nTỔNG: {n} mutant — {n - alive - bad} chết, {alive} SỐNG, {bad} lỗi dựng mutant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
