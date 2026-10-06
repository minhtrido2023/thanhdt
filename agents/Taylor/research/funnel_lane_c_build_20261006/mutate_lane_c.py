#!/usr/bin/env python3
"""Đột biến các cổng của làn C (job Taylor_20261006_041048, vòng 2 Taylor_20261006_043550).

KHÔNG BAO GIỜ ghi vào file nguồn: mỗi đột biến chạy trên BẢN COPY trong tmpdir riêng
(funnel + selfcheck + 2 module cùng thư mục mà selfcheck nạp theo đường dẫn), `WC_ROOT` trỏ cây
canonical để module phụ/dữ liệu đọc như thường. Đích ghi nằm trong `mike/bin` canonical ⇒ TỪ CHỐI
chạy (vòng 1 ghi đè tại chỗ ⇒ sau merge sẽ là file production của cron 19:37 — arch-review r1).
Sống = selfcheck bản copy vẫn rc=0 (test không bắt được đột biến).

    $DNA_PYEXE agents/Taylor/research/funnel_lane_c_build_20261006/mutate_lane_c.py [--bin DIR] [-j N]
"""
import argparse
import concurrent.futures as cf
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BIN = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "bin"))
FILES = ["discretionary_candidate_funnel.py", "discretionary_candidate_funnel_selfcheck.py",
         "wc_paths.py", "daily_decision_topic.py"]
SRC_NAME, SC_NAME = FILES[0], FILES[1]


def wc_root(bin_dir):
    sys.path.insert(0, bin_dir)
    import wc_paths
    return wc_paths.find_wc_root(os.path.join(bin_dir, SRC_NAME))


def assert_safe_target(path, canonical_bin):
    """Đích ghi KHÔNG được nằm trong mike/bin canonical (so realpath) — raise SystemExit."""
    if os.path.realpath(os.path.dirname(path)) == os.path.realpath(canonical_bin):
        raise SystemExit(f"TỪ CHỐI: đích ghi {path} là mike/bin canonical — đột biến chỉ chạy trên "
                         f"bản copy tmpdir")


M = [
    ("YoY biên 30% VÀO", '(df["g_yoy"].astype(float) >= LANE_C_YOY_MIN - 1e-9)',
     '(df["g_yoy"].astype(float) > LANE_C_YOY_MIN + 1e-9)'),
    ("YoY ngưỡng 30→25%", "LANE_C_YOY_MIN = 0.30", "LANE_C_YOY_MIN = 0.25"),
    ("QoQ >0 → >=0", '& (df["g_qoq"].astype(float) > 0))', '& (df["g_qoq"].astype(float) >= 0))'),
    ("bỏ điều kiện QoQ", '& (df["g_qoq"].astype(float) > 0))', ')'),
    ("PE<=12 → <12", '(df["PE"] <= LANE_C_PE_MAX)', '(df["PE"] < LANE_C_PE_MAX)'),
    ("PE trần 12→13", "LANE_C_PE_MAX = 12.0", "LANE_C_PE_MAX = 13.0"),
    ("bỏ PE>0 làn C", 'lane_c = (quality & (df["PE"] > 0) & ', 'lane_c = (quality & '),
    ("bỏ vũ trụ chất lượng làn C", 'lane_c = (quality & (df["PE"] > 0)', 'lane_c = ((df["PE"] > 0)'),
    ("bỏ loại trừ BANNED/insider làn C", 'c = df[lane_c & clean].assign(lane="C"',
     'c = df[lane_c].assign(lane="C"'),
    ("PIT < → <=", 'f = f[f["known"] < asof_ts]', 'f = f[f["known"] <= asof_ts]'),
    ("ngày biết ưu tiên time thay Release",
     'known = rel.mask(early).fillna(pd.to_datetime(raw["time"], errors="coerce"))',
     'known = pd.to_datetime(raw["time"], errors="coerce").fillna(rel.mask(early))'),
    ("YoY bỏ NP_P4>0", 'np.where((p0 > 0) & (p4 > 0), p0 / p4 - 1, np.nan)', 'np.where(p0 > 0, p0 / p4 - 1, np.nan)'),
    ("QoQ bỏ NP_P1>0", 'np.where((p0 > 0) & (p1 > 0), p0 / p1 - 1, np.nan)', 'np.where(p0 > 0, p0 / p1 - 1, np.nan)'),
    ("quý mới nhất → cũ nhất", '.groupby("ticker").tail(1).set_index("ticker")', '.groupby("ticker").head(1).set_index("ticker")'),
    ("trần 5→6", "LANE_C_MAX_PER_DAY = 5 ", "LANE_C_MAX_PER_DAY = 6 "),
    ("ưu tiên: bỏ đẩy YoY cực lớn xuống", "return (_yoy_extreme(g), -g, str(r[\"ticker\"]))",
     "return (False, -g, str(r[\"ticker\"]))"),
    ("ưu tiên: YoY tăng dần", "return (_yoy_extreme(g), -g, str(r[\"ticker\"]))",
     "return (_yoy_extreme(g), g, str(r[\"ticker\"]))"),
    ("mã gộp A/B chiếm trần", 'd[2] == "NEW" and not d[3]]', 'd[2] == "NEW"]'),
    ("không nhận diện gộp A/B", 'decided.append([r, e, reason, lane_c and r["ticker"] in ab_today])',
     'decided.append([r, e, reason, False])'),
    ("QUEUED bị đánh dấu đã báo", '            e["queued"] = True\n        elif reason and',
     '            e["queued"] = True\n        if reason and'),
    ("hàng chờ không tranh lại", 'elif lane_c and continuous and e.get("queued"):', 'elif False:'),
    ("PBZ_DROP áp cả làn C", "if (not lane_c and pbz is not None", "if (pbz is not None"),
    ("state cũ: C coi như đã seed (flood)", 'seeded.update({"A": st["seeded_on"], "B": st["seeded_on"]})',
     'seeded.update({"A": st["seeded_on"], "B": st["seeded_on"], "C": st["seeded_on"]})'),
    ("làn lỗi vẫn seed", "        if lane not in unavailable_lanes:\n            seeded.setdefault",
     "        if True:\n            seeded.setdefault"),
    ("bỏ giữ liên tục qua phiên lỗi",
     'and e.get("last_seen") == ref_run:\n            e["last_seen"] = asof_s',
     'and e.get("last_seen") == ref_run:\n            pass'),
    ("run_daily không truyền làn lỗi", "update_state(state, cands, asof, unavailable)", "update_state(state, cands, asof)"),
    ("nhãn nền thấp > → >=", 'float(f"{g * 100:.0f}") > LANE_C_YOY_EXTREME * 100',
     'float(f"{g * 100:.0f}") >= LANE_C_YOY_EXTREME * 100'),
    ("nhãn nền thấp theo số THÔ (lệch số hiển thị)", 'float(f"{g * 100:.0f}") > LANE_C_YOY_EXTREME * 100',
     'g > LANE_C_YOY_EXTREME'),
    ("dòng C mất nhãn bắt buộc", 'f" · ⚠️ {lane_c_label(c.get(\'g_yoy\'))}")', 'f"")'),
    ("dòng A/B không gộp nhãn C", 'ctag = f" · +làn C: {lane_c_tag(also_c)}" if also_c else ""', 'ctag = ""'),
    ("log mất nhãn", 'rows["label"] = [lane_c_label(g) if l == "C" else ""', 'rows["label"] = [""'),
    ("cảnh báo fin không vào kết quả", "    warnings += fin_warn\n", "    pass\n"),
    ("khối không báo làn C KHÔNG CHẠY", "    if not c_ok:\n", "    if False:\n"),
    ("bỏ dòng 'còn N mã'", "    if queued:\n        lines.append(f\"… còn", "    if False:\n        lines.append(f\"… còn"),
    ("bỏ sàn số dòng fin", "    if len(raw) < FIN_MIN_ROWS:", "    if False:"),
    ("bỏ sàn số mã fin", '    if meta["tickers"] < FIN_MIN_TICKERS:', "    if False:"),
    ("bỏ cảnh báo cache cũ", "    if age > FIN_MAX_FILE_AGE_DAYS:", "    if False:"),
    ("bỏ cảnh báo dữ liệu cũ", "    if data_age > FIN_MAX_DATA_AGE_DAYS:", "    if False:"),
    ("bỏ cảnh báo phủ thấp", "        if cov < FIN_MIN_COVERAGE:", "        if False:"),
    ("fin thiếu cột ⇒ không chặn", "        if missing:\n            return None, meta, [f\"{path} thiếu cột",
     "        if False:\n            return None, meta, [f\"{path} thiếu cột"),
    ("khối seed C in '0 mới'", '    elif "C" not in seeded_today and not rep_cm:', "    elif True:"),
    # --- vòng 2 (arch-review r1): 3 đột biến reviewer thấy SỐNG + đột biến cho mọi sửa đổi vòng 2
    ("r1(a) bỏ dòng 'Làn C cũng bắt'", "    if rep_cm:\n", "    if False:\n"),
    ("r1(b) bỏ redflag khỏi vũ trụ chất lượng", ' & df["redflag"].isna()', ""),
    ("r1(b') bỏ redflag CHỈ ở làn C", 'lane_c = (quality & (df["PE"] > 0)',
     'lane_c = (((df["rating"] <= RATING_MAX) & df["golden_floor_pass"] & (df["liq_bn"] >= LIQ_MIN_BN))'
     ' & (df["PE"] > 0)'),
    ("r1(c) bỏ guard last_seen==ref_run phiên lỗi",
     'if e.get("lane") in unavailable_lanes and ref_run and e.get("last_seen") == ref_run:',
     'if e.get("lane") in unavailable_lanes:'),
    ("r1(c') guard chỉ còn ref_run",
     'if e.get("lane") in unavailable_lanes and ref_run and e.get("last_seen") == ref_run:',
     'if e.get("lane") in unavailable_lanes and ref_run:'),
    ("#3 try chỉ bắt OSError", "    except Exception as e:                                  # noqa: BLE001 — cô lập làn C",
     "    except OSError as e:                                  # noqa: BLE001 — cô lập làn C"),
    ("#3 except không tắt C", "        fin = None\n        warnings.append(f\"làn C lỗi khi tính",
     "        pass\n        warnings.append(f\"làn C lỗi khi tính"),
    ("#3 except nuốt im lặng", "        warnings.append(f\"làn C lỗi khi tính", "        (f\"làn C lỗi khi tính"),
    ("#4 log lane_c_ok luôn True", "    rows[\"lane_c_ok\"] = bool(lane_c_ok)", "    rows[\"lane_c_ok\"] = True"),
    ("#4 run_daily truyền cờ sai", "append_log(paths[\"log\"], cands, asof, rep_all, fin is not None)",
     "append_log(paths[\"log\"], cands, asof, rep_all, True)"),
    ("#5 '0 mới' cùng 'cũng bắt'", '    elif "C" not in seeded_today and not rep_cm:', '    elif "C" not in seeded_today:'),
    ("#6 bỏ guard Release<=cuối quý", "known = rel.mask(early).fillna(", "known = rel.fillna("),
    ("#6 guard < thay <=", "early = (rel <= qend)", "early = (rel < qend)"),
    ("#6 cuối quý lệch 1 tháng", '(m[1].astype(float) * 3)', '(m[1].astype(float) * 3 - 1)'),
    ("#6 meta đếm sai", 'meta["release_le_qend"] = int(early.sum())', 'meta["release_le_qend"] = 0'),
]


def run_one(m, bin_dir, root, canonical_bin, py, orig):
    """1 đột biến trong tmpdir riêng ⇒ ("CHẾT"|"SỐNG"|"SKIP-BAD-PATTERN", name, chi tiết)."""
    name, a, b = m
    n = 1 if a is None else orig.count(a)                    # a None = đối chứng, không đột biến
    if n != 1:
        return "SKIP-BAD-PATTERN", name, f"{n}x"
    tmp = tempfile.mkdtemp(prefix="mut_lanec_")
    try:
        dst = os.path.join(tmp, "bin")
        os.makedirs(dst)
        for fn in FILES:
            shutil.copy2(os.path.join(bin_dir, fn), os.path.join(dst, fn))
        target = os.path.join(dst, SRC_NAME)
        assert_safe_target(target, canonical_bin)
        with open(target, "w", encoding="utf-8") as f:
            f.write(orig if a is None else orig.replace(a, b))
        env = dict(os.environ, WC_ROOT=root, PYTHONDONTWRITEBYTECODE="1")
        p = subprocess.run([py, os.path.join(dst, SC_NAME)], capture_output=True, text=True,
                           timeout=300, env=env, cwd=tmp)
        last = (p.stdout.strip().splitlines() or [""])[-1]
        return ("CHẾT" if p.returncode != 0 else "SỐNG"), name, last
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", default=DEFAULT_BIN, help="thư mục chứa bản funnel GỐC để copy (chỉ đọc)")
    ap.add_argument("-j", type=int, default=6)
    args = ap.parse_args()
    bin_dir = os.path.abspath(args.bin)
    root = wc_root(bin_dir)
    canonical_bin = os.path.join(root, "mike", "bin")
    with open(os.path.join(bin_dir, SRC_NAME), encoding="utf-8") as f:
        orig = f.read()
    py = sys.executable
    # đối chứng: bản copy KHÔNG đột biến phải PASS (không thì mọi "CHẾT" vô nghĩa)
    st, _, last = run_one(("đối chứng", None, None), bin_dir, root, canonical_bin, py, orig)
    print(f"đối chứng (copy không đột biến): {st} — {last}")
    if st != "SỐNG":
        print("ĐỐI CHỨNG HỎNG — dừng")
        return 2
    dead = alive = 0
    with cf.ThreadPoolExecutor(max_workers=args.j) as ex:
        futs = [ex.submit(run_one, m, bin_dir, root, canonical_bin, py, orig) for m in M]
        for fu in futs:
            st, name, info = fu.result()
            if st == "CHẾT":
                dead += 1
            else:
                alive += 1
            print(f"{st:5s} {name}" + (f"  [{info}]" if st != "CHẾT" else ""))
    print(f"đột biến: {dead}/{len(M)} chết, {alive} sống")
    return 1 if alive else 0


if __name__ == "__main__":
    sys.exit(main())
