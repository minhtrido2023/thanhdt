#!/usr/bin/env python3
"""Đột biến các cổng MỚI của làn C (job Taylor_20261006_041048) — mỗi đột biến: thay 1 chuỗi (phải
khớp ĐÚNG 1 lần), chạy selfcheck, khôi phục file. Sống = selfcheck vẫn rc=0 (test không bắt được).
    $DNA_PYEXE agents/Taylor/research/funnel_lane_c_build_20261006/mutate_lane_c.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "bin"))
SRC = os.path.join(BIN, "discretionary_candidate_funnel.py")
SC = os.path.join(BIN, "discretionary_candidate_funnel_selfcheck.py")

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
     'known = pd.to_datetime(raw["Release_Date"], errors="coerce").fillna(\n        pd.to_datetime(raw["time"], errors="coerce"))',
     'known = pd.to_datetime(raw["time"], errors="coerce").fillna(\n        pd.to_datetime(raw["Release_Date"], errors="coerce"))'),
    ("YoY bỏ NP_P4>0", 'np.where((p0 > 0) & (p4 > 0), p0 / p4 - 1, np.nan)', 'np.where(p0 > 0, p0 / p4 - 1, np.nan)'),
    ("QoQ bỏ NP_P1>0", 'np.where((p0 > 0) & (p1 > 0), p0 / p1 - 1, np.nan)', 'np.where(p0 > 0, p0 / p1 - 1, np.nan)'),
    ("quý mới nhất → cũ nhất", '.groupby("ticker").tail(1).set_index("ticker")', '.groupby("ticker").head(1).set_index("ticker")'),
    ("trần 5→6", "LANE_C_MAX_PER_DAY = 5 ", "LANE_C_MAX_PER_DAY = 6 "),
    ("ưu tiên: bỏ đẩy YoY cực lớn xuống", "return (g > LANE_C_YOY_EXTREME, -g, str(r[\"ticker\"]))",
     "return (False, -g, str(r[\"ticker\"]))"),
    ("ưu tiên: YoY tăng dần", "return (g > LANE_C_YOY_EXTREME, -g, str(r[\"ticker\"]))",
     "return (g > LANE_C_YOY_EXTREME, g, str(r[\"ticker\"]))"),
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
    ("nhãn nền thấp > → >=", "if g is not None and g > LANE_C_YOY_EXTREME:", "if g is not None and g >= LANE_C_YOY_EXTREME:"),
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
    ("khối seed C in '0 mới'", '    elif "C" not in seeded_today:', "    elif True:"),
]


def main():
    orig = open(SRC, encoding="utf-8").read()
    py = sys.executable
    dead = alive = 0
    try:
        for name, a, b in M:
            n = orig.count(a)
            if n != 1:
                print(f"SKIP-BAD-PATTERN ({n}x): {name}")
                alive += 1
                continue
            with open(SRC, "w", encoding="utf-8") as f:
                f.write(orig.replace(a, b))
            rc = subprocess.run([py, SC], capture_output=True, text=True, timeout=300).returncode
            if rc != 0:
                dead += 1
                print(f"CHẾT  {name}")
            else:
                alive += 1
                print(f"SỐNG  {name}")
    finally:
        with open(SRC, "w", encoding="utf-8") as f:
            f.write(orig)
    print(f"đột biến: {dead}/{len(M)} chết, {alive} sống")
    return 1 if alive else 0


if __name__ == "__main__":
    sys.exit(main())
