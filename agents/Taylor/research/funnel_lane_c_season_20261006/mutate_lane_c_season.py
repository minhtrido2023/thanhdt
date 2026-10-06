#!/usr/bin/env python3
"""Đột biến funnel làn C sau bản mùa vụ/FIFO/quý mới nhất/dọn state (job Taylor_20261006_052500).

Dùng lại NGUYÊN harness của `../funnel_lane_c_build_20261006/mutate_lane_c.py` (mỗi đột biến chạy
trên BẢN COPY tmpdir riêng, đích ghi trong mike/bin canonical ⇒ SystemExit; đối chứng copy không
đột biến phải PASS). Danh sách = toàn bộ đột biến cũ (mẫu đã đổi được cập nhật theo code mới) +
đột biến cho mọi thay đổi của job này. Sống = selfcheck bản copy vẫn rc=0.

    $DNA_PYEXE agents/Taylor/research/funnel_lane_c_season_20261006/mutate_lane_c_season.py [--bin DIR] [-j N]
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "mutate_lane_c", os.path.join(HERE, "..", "funnel_lane_c_build_20261006", "mutate_lane_c.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)
H.DEFAULT_BIN = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "bin"))

# Mẫu cũ đã đổi chữ ở code mới ⇒ thay bằng mẫu tương đương (cùng ý đột biến).
RENAMED = {
    "QoQ >0 → >=0": (', df["g_qoq"].astype(float) > 0)', ', df["g_qoq"].astype(float) >= 0)'),
    "bỏ điều kiện QoQ": ("              & qoq_ok)", "              )"),
    "bỏ PE>0 làn C": ('c_base = quality & (df["PE"] > 0) & ', "c_base = quality & "),
    "bỏ vũ trụ chất lượng làn C": ('c_base = quality & (df["PE"] > 0)', 'c_base = (df["PE"] > 0)'),
    "r1(b') bỏ redflag CHỈ ở làn C": (
        'c_base = quality & (df["PE"] > 0)',
        'c_base = ((df["rating"] <= RATING_MAX) & df["golden_floor_pass"] & (df["liq_bn"] >= LIQ_MIN_BN))'
        ' & (df["PE"] > 0)'),
    "PIT < → <=": ('f = f[(f["known"] < asof_ts) & f["p"].notna()]', 'f = f[(f["known"] <= asof_ts) & f["p"].notna()]'),
    "quý mới nhất → cũ nhất": ('latest = f.groupby("ticker").tail(1)', 'latest = f.groupby("ticker").head(1)'),
    "ưu tiên: bỏ đẩy YoY cực lớn xuống": ('return (since, _yoy_extreme(g), -g, str(r["ticker"]))',
                                          'return (since, False, -g, str(r["ticker"]))'),
    "ưu tiên: YoY tăng dần": ('return (since, _yoy_extreme(g), -g, str(r["ticker"]))',
                              'return (since, _yoy_extreme(g), g, str(r["ticker"]))'),
    "không nhận diện gộp A/B": ('decided.append([r, e, reason, lane_c and r["ticker"] in ab_today, since])',
                                'decided.append([r, e, reason, False, since])'),
    "QUEUED bị đánh dấu đã báo": ('            e["queued_since"] = since\n        elif reason and',
                                  '            e["queued_since"] = since\n        if reason and'),
    "dòng C mất nhãn bắt buộc": ('f"{season_tag(c)} · ⚠️ {lane_c_label(c.get(\'g_yoy\'))}")', 'f"{season_tag(c)}")'),
}
OLD = [(n, *RENAMED[n]) if n in RENAMED else (n, a, b) for n, a, b in H.M]

NEW = [
    # --- mùa vụ
    ("S1 bỏ thay QoQ cho mã mùa vụ",
     'qoq_ok = np.where(seas, df["g_qoq_adj"].astype(float) > 0, df["g_qoq"].astype(float) > 0)',
     'qoq_ok = df["g_qoq"].astype(float) > 0'),
    ("S2 mã mùa vụ dùng cả QoQ thô (AND)",
     'qoq_ok = np.where(seas, df["g_qoq_adj"].astype(float) > 0, df["g_qoq"].astype(float) > 0)',
     'qoq_ok = np.where(seas, (df["g_qoq_adj"].astype(float) > 0) & (df["g_qoq"].astype(float) > 0), '
     'df["g_qoq"].astype(float) > 0)'),
    ("S3 ngưỡng η² 0,6→0,5", "SEASON_ETA2_MIN = 0.6", "SEASON_ETA2_MIN = 0.5"),
    ("S4 ngưỡng η² 0,6→0,7", "SEASON_ETA2_MIN = 0.6", "SEASON_ETA2_MIN = 0.7"),
    ("S5 >=3 năm/cặp → >=2", "SEASON_MIN_PER_PAIR = 3", "SEASON_MIN_PER_PAIR = 2"),
    ("S6 cửa sổ 20→24 quý", "SEASON_WINDOW_Q = 20", "SEASON_WINDOW_Q = 24"),
    ("S7 chuẩn mùa trung vị → trung bình", '"med": g.median()', '"med": g.mean()'),
    ("S8 lịch sử gồm cả quý hiện tại", '(h["p"] < h["ticker"].map(p0))', '(h["p"] <= h["ticker"].map(p0))'),
    ("S9 bỏ yêu cầu đủ 4 cặp quý", '.where(npair == 4, 0)', ''),
    ("S10 log-QoQ không cần NP>0", '& (h["NP_P0"] > 0) & (h["np_prev"] > 0)]', ']'),
    ("S11 cặp quý theo quý trước", 'qn=h["p"] % 4)', 'qn=(h["p"] - 1) % 4)'),
    ("S12 chuẩn mùa lấy cặp quý kế", 'med.get((t, int(p) % 4), np.nan)', 'med.get((t, (int(p) + 1) % 4), np.nan)'),
    ("S13 QoQ đ/c mùa sai chiều", 'p0 / p1 / np.exp(norm) - 1', 'p0 / p1 * np.exp(norm) - 1'),
    ("S14 seasonal tính cả mã không có trong fin", 'seas = j["seasonal"].eq(True).to_numpy()',
     'seas = j["seasonal"].ne(False).to_numpy()'),
    ("S15 η² biên >= → >", '& (out["season_eta2"] >= SEASON_ETA2_MIN - 1e-12)',
     '& (out["season_eta2"] > SEASON_ETA2_MIN + 1e-12)'),
    ("S16 dòng C mất nhãn mùa vụ", '    if not c.get("seasonal"):\n        return ""',
     '    if True:\n        return ""'),
    ("S17 không in giải thích mùa vụ", '    if any("· mùa vụ η²" in x for x in lines):', '    if False:'),
    ("S18 luôn in giải thích mùa vụ", '    if any("· mùa vụ η²" in x for x in lines):', '    if True:'),
    ("S19 _rec mất cờ mùa vụ", 'out[k] = bool(v is True or v is np.True_)', 'out[k] = False'),
    ("S20 n_lane_c_seasonal sai", '& cands["seasonal"].eq(True)).sum())', '& cands["seasonal"].eq(False)).sum())'),
    ("S21 log mất cột mùa vụ", ',\n            "seasonal", "season_eta2", "season_norm_qoq", "g_qoq_adj"]', ']'),
    # --- quý mới nhất theo kỳ / thiếu NP
    ("Q1 quý theo ngày biết (cũ)", '.sort_values(["ticker", "p", "known"]).drop_duplicates(',
     '.sort_values(["ticker", "known", "p"]).drop_duplicates('),
    ("Q2 cùng kỳ: bản biết sớm thắng", '["ticker", "p"], keep="last")', '["ticker", "p"], keep="first")'),
    ("Q3 thiếu NP ⇒ lùi về quý cũ", 'f = f[(f["known"] < asof_ts) & f["p"].notna()]',
     'f = f[(f["known"] < asof_ts) & f["p"].notna() & f["NP_P0"].notna()]'),
    ("Q4 không ghi loại np_missing", "excluded = pd.concat([ex_a, ex_b, ex_c, ex_np]", "excluded = pd.concat([ex_a, ex_b, ex_c]"),
    ("Q5 mất cảnh báo thiếu NP", "            if len(npm):", "            if False:"),
    ("Q6 phủ tính cả mã thiếu NP", 'pool.isin(fin.index[~fin["np_missing"]])', 'pool.isin(fin.index)'),
    ("Q7 bỏ lọc quý sai dạng", 'f = f[(f["known"] < asof_ts) & f["p"].notna()]', 'f = f[(f["known"] < asof_ts)]'),
    ("Q8 meta không đếm quý sai", 'meta["bad_quarter"] = int(f["p"].isna().sum())', 'meta["bad_quarter"] = 0'),
    # --- FIFO
    ("F1 bỏ FIFO", 'return (since, _yoy_extreme(g), -g, str(r["ticker"]))',
     'return ("", _yoy_extreme(g), -g, str(r["ticker"]))'),
    ("F2 không giữ ngày chờ cũ", 'since = e.get("queued_since") or asof_s', 'since = asof_s'),
    ("F3 không lưu queued_since", '            e["queued_since"] = since\n', '            pass\n'),
    ("F4 báo xong không rời hàng chờ", '            e.pop("queued", None)\n            e.pop("queued_since", None)\n',
     '            e.pop("queued", None)\n'),
    # F5 ("rời làn vẫn giữ chỗ chờ" qua `since` mặc định) ĐÃ GỠ: sau vá B1 (Mike, arch-review r1) mục C
    # rời làn bị gỡ queued_since ngay phiên đó ⇒ `since` mặc định chỉ còn gặp mục không có queued_since
    # ⇒ đột biến TƯƠNG ĐƯƠNG trên mọi state đạt được; ý đột biến nay do Q1 phủ.
    # --- dọn state
    ("P1 bỏ dọn STALE", '    if not unavailable_lanes:\n        today = ', '    if False:\n        today = '),
    ("P2 dọn STALE khi làn lỗi", '    if not unavailable_lanes:\n        today = ', '    if True:\n        today = '),
    ("P3 STALE theo làn C thay vì mọi làn", 'today = set(cands["ticker"]) if len(cands) else set()',
     'today = set(cands.loc[cands["lane"] == "C", "ticker"]) if len(cands) else set()'),
    ("P4 STALE bỏ cooldown",
     'lr is None or (asof_d - dt.date.fromisoformat(lr)).days >= COOLDOWN_DAYS):', 'True):'),
    ("P5 STALE cooldown >= → >",
     'lr is None or (asof_d - dt.date.fromisoformat(lr)).days >= COOLDOWN_DAYS):',
     'lr is None or (asof_d - dt.date.fromisoformat(lr)).days > COOLDOWN_DAYS):'),
    ("P6 bỏ hết hạn hàng chờ",
     'if e.get("queued") and qs and (asof_d - dt.date.fromisoformat(qs)).days >= QUEUE_MAX_DAYS:', 'if False:'),
    ("P7 hàng chờ >= → >",
     'if e.get("queued") and qs and (asof_d - dt.date.fromisoformat(qs)).days >= QUEUE_MAX_DAYS:',
     'if e.get("queued") and qs and (asof_d - dt.date.fromisoformat(qs)).days > QUEUE_MAX_DAYS:'),
    ("P8 hết hạn hàng chờ cả khi làn lỗi", '    if not unavailable_lanes:\n        for key, e in list(entries.items()):\n            qs',
     '    if True:\n        for key, e in list(entries.items()):\n            qs'),
    ("P9 mã hết hạn vẫn được xét phiên đó", "        if key in skip:\n            continue", "        if False:\n            continue"),
    ("P10 chạy lại không đọc prune_log", 'skip = {x["key"] for x in plog if x.get("asof") == asof_s and x.get("reason") == "QUEUE_EXPIRED"}',
     'skip = set()'),
    ("P11 prune_log không cắt", "    del plog[:-PRUNE_LOG_MAX]\n", "    pass\n"),
    ("P12 mất cảnh báo hàng chờ hết hạn", "    if qexp:\n", "    if False:\n"),
    ("P13 state_pruned rỗng", '"state_pruned": pruned,', '"state_pruned": [],'),
    # arch-review r1 (Mike vá B1 + NB-1 X1)
    ("Q1 rời làn C vẫn giữ chỗ chờ (B1)", 'if e.get("lane") == "C" and e.get("last_seen") != asof_s:', "if False:"),
    ("Q2 gỡ chỗ chờ cả khi làn C lỗi", '    if "C" not in unavailable_lanes:\n        for e in entries.values():',
     '    if True:\n        for e in entries.values():'),
    ("Q3 chưa từng báo không dọn STALE (X1)", "lr is None or (asof_d", "(lr is not None) and (asof_d"),
]
H.M = OLD + NEW

if __name__ == "__main__":
    sys.exit(H.main())
