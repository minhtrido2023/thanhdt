#!/usr/bin/env python3
"""Selfcheck cho commodity_nowcast_block.py: >=25 assertion thật + 4 mutant (mỗi mutant PHẢI làm suite đỏ).
Không chạm BQ/mạng (runner giả). Đối chiếu tay c_yoy DPM/DRI 2025Q3 với b2_panel.csv (nghiên cứu độc lập, pandas).
Chạy: python3 bin/commodity_nowcast_block_selfcheck.py   (và `env -u TZ ...`, `TZ=Pacific/Kiritimati ...` — §16)
"""
import importlib.util, json, math, os, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "commodity_nowcast_block.py")
ICT = timezone(timedelta(hours=7))
NOW = datetime(2026, 10, 26, 17, 0, tzinfo=ICT)
RES = os.path.join(os.path.dirname(HERE), "agents/Taylor/research/commodity_cycle_te_20261026")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def synth(fn, start="2023-01-02", end="2026-10-23"):
    d = datetime.fromisoformat(start); e = datetime.fromisoformat(end); out = []
    while d <= e:
        if d.weekday() < 5:
            out.append((d.strftime("%Y-%m-%d"), fn(d.strftime("%Y-%m-%d"))))
        d += timedelta(days=1)
    return out


def to_csv(series):
    return "metric_key,observation_date,value\n" + "\n".join(
        f"{k},{d},{v}" for k, obs in series.items() for d, v in obs) + "\n"


def suite(M, tmp):
    """-> list[(name, ok)]. M = module (gốc hoặc mutant)."""
    R = []
    def chk(name, cond):
        R.append((name, bool(cond)))
    # --- dữ liệu giả: urea/rubber tăng bậc thang, brent giảm, sulfur tăng; mọi series OK trừ 'sugar'
    lvl = lambda base, step: (lambda d: base if d < "2025-07-01" else step)
    series = {"urea": synth(lvl(100.0, 100.0)),            # phẳng => c_yoy 0 => trung tính
              "rubber": synth(lambda d: 100.0 if d < "2025-07-01" else 150.0),   # Q3/26 vs Q3/25 phẳng 150/150 => 0
              "brent": synth(lambda d: 100.0 if d < "2026-07-01" else 60.0),     # Q3/26 60 vs Q3/25 100 => log(.6) producer
              "sulfur": synth(lambda d: 100.0 if d < "2026-07-01" else 200.0),   # consumer: +log2 => nhãn BẤT LỢI
              "steel": synth(lambda d: 100.0 if d < "2026-07-01" else 120.0),    # +0.182 thuận
              "sugar": synth(lambda d: 100.0),                                    # bị STALE trong freshness
              "yellow_phosphorus": synth(lambda d: 100.0 if d < "2026-07-01" else 130.0)}   # sunsirs, KHÔNG có trong freshness
    runner_sql = []
    def runner(sql):
        runner_sql.append(sql); return to_csv(series)
    fresh = {f"{k}|trading_economics|daily": {"status": "OK", "last_obs": "2026-10-23"} for k in series if k != "yellow_phosphorus"}
    fresh["sugar|trading_economics|daily"]["status"] = "STALE"
    fp = os.path.join(tmp, "fresh.json")
    json.dump({"generated_at": NOW.isoformat(), "series": fresh}, open(fp, "w"))
    mp = os.path.join(tmp, "map.csv")
    open(mp, "w").write(
        "ticker,family,te_metric_key,sign,tier,note\n"
        "AAA1,urea,urea,1,A,n\nBBB1,crude,brent,1,A,n\nCCC1,sulfur_c,sulfur,-1,B,n\nDDD1,steel_cn,steel,1,A,n\n"
        "EEE1,sugar,sugar,1,A,n\nFFF1,phos,steel,1,D,BAY ten\nGGG1,urea,urea,1,A,n\n-,coffee,coffee,1,D,n\n"
        "DGC,p4_yellow,yellow_phosphorus,1,D,n\nPAT,p4_yellow,yellow_phosphorus,1,D,n\n")
    M.MAP_CSV, M.FRESH_JSON = mp, fp

    # --- A. map / tiện ích
    cm = M.load_map()
    chk("map: bỏ ticker '-'", "-" not in cm)
    chk("map: sign đọc đúng producer +1 / consumer -1", cm["BBB1"][0]["sign"] == 1 and cm["CCC1"][0]["sign"] == -1)
    chk("label: |c|<0,05 trung tính", M.label(0.049) == "trung tính" and M.label(-0.049) == "trung tính")
    chk("label: >=0,05 thuận / <=-0,05 bất lợi", M.label(0.06) == "thuận" and M.label(-0.06) == "bất lợi")
    chk("label: None => không đủ dữ liệu", M.label(None) == "không đủ dữ liệu")
    chk("fmt: -0,00 không lộ dấu âm", M._fmt(-0.001) == "+0,00")

    # --- B. metrics
    mt = M.metrics(series["brent"])
    chk("metrics: quý hoàn tất gần nhất = Q3/2026 (last_obs 23/10 ở Q4)", mt["rq"] == (2026, 3))
    chk("metrics: c_yoy brent = log(60/100)", abs(mt["c_yoy_raw"] - math.log(0.6)) < 1e-9)
    chk("metrics: R/MA252 trong (0;1) khi giá vừa rớt", 0 < mt["r_ma"] < 1)
    chk("metrics: phân vị TB63 thấp khi giá ở đáy lịch sử", mt["pct"] < 0.35)
    chk("metrics: <252 quan sát => None", M.metrics(series["brent"][:100]) is None)
    chk("metrics: quý-đến-nay có số khi quý đang chạy", mt["qtd_raw"] is not None)

    # --- C. run() / khối text
    out = M.run(["AAA1", "BBB1", "CCC1", "DDD1", "EEE1", "FFF1", "ZZZ9", "DGC", "PAT"], runner=runner, now=NOW)
    blk = lambda t: out.split(f"**{t}**")[1].split("\n•")[0] if f"**{t}**" in out else ""
    chk("run: có khối + header", out.startswith("🛢️"))
    chk("run: footer bắt buộc ở cuối", out.rstrip().endswith(M.FOOTER) and "nowcast IC 0,44" in out and "không phải tín hiệu mua/bán" in out)
    chk("run: mã ngoài map (ZZZ9) bị bỏ", "ZZZ9" not in out)
    chk("run: urea phẳng => trung tính", "trung tính" in blk("AAA1"))
    chk("run: brent giảm => 'bất lợi' cho producer", "bất lợi" in blk("BBB1"))
    chk("run: brent có cảnh báo dầu thô IC~0", "IC với LN ~0 (hợp đồng trễ)" in blk("BBB1"))
    chk("run: sulfur tăng, consumer => 'bất lợi' (dấu ngược)", "bất lợi" in blk("CCC1") and "-0,69" in blk("CCC1"))
    chk("run: steel +log1.2 producer => 'thuận'", "thuận" in blk("DDD1") and "+0,18" in blk("DDD1"))
    chk("run: STALE => 'KHÔNG ĐỦ TƯƠI', không in số", "KHÔNG ĐỦ TƯƠI" in blk("EEE1") and "YoY" not in blk("EEE1"))
    chk("run: ngày dữ liệu cuối được in", "giá tới 2026-10-23" in blk("AAA1"))
    chk("run: nhóm D chỉ mô tả, không nhãn", "nhóm D: chỉ mô tả" in blk("FFF1") and "hàng hoá nói" not in blk("FFF1"))
    chk("run: cảnh báo dầu thô chỉ ở họ crude", "dầu thô" not in blk("AAA1"))
    chk("run: nhãn nêu rõ là mô tả, không phải tín hiệu", "không phải tín hiệu" in out.split("\n")[0])
    # --- P4 sunsirs (DGC/PAT)
    chk("P4: DGC in số mô tả (không nhãn)", "yellow_phosphorus" in blk("DGC") and "YoY +0,26" in blk("DGC") and "hàng hoá nói" not in blk("DGC"))
    chk("P4: DGC có cảnh báo gãy từ 2024 + không phải tín hiệu + không sizing",
        "GÃY từ 2024" in blk("DGC") and "0,46-0,50" in blk("DGC") and "-0,21 từ 2024" in blk("DGC") and "không sizing" in blk("DGC"))
    chk("P4: PAT cũng có cảnh báo P4", "GÃY từ 2024" in blk("PAT") and "YoY +0,26" in blk("PAT"))
    chk("P4: cảnh báo pháp lý chỉ ở DGC, không ở PAT", "pháp lý/quản trị" in blk("DGC") and "pháp lý" not in blk("PAT"))
    real = M.load_map(os.path.join(RES, "commodity_map_te.csv"))      # map THẬT (+ override trong module), không dùng map giả
    chk("P4: map thật — DGC/PAT không có sulfur/phosphorus TE, chỉ yellow_phosphorus",
        all(r["key"] == "yellow_phosphorus" and r["tier"] == "D" for t in ("DGC", "PAT") for r in real[t])
        and all(len(real[t]) == 1 for t in ("DGC", "PAT")))
    chk("P4: map thật — DDV/LAS vẫn giữ sulfur (override không lan)",
        any(r["key"] == "sulfur" for r in real["DDV"]) and any(r["key"] == "sulfur" for r in real["LAS"]))
    M.MAP_CSV = os.path.join(RES, "commodity_map_te.csv")
    real_out = M.run(["DGC", "PAT"], runner=runner, now=NOW)
    M.MAP_CSV = mp
    chk("P4: khối render từ map thật không có lưu huỳnh", "sulfur" not in real_out.lower() and "lưu huỳnh" not in real_out.lower()
        and "yellow_phosphorus" in real_out)
    # cuối tuần sunsirs: hàng T7/CN spike không được ảnh hưởng số
    wk = dict(series)
    wk["yellow_phosphorus"] = sorted(series["yellow_phosphorus"] + [
        (d, 9999.0) for d in ("2026-10-17", "2026-10-18", "2026-09-05", "2026-09-06", "2026-08-01", "2026-08-02")])
    ow = M.run(["DGC"], runner=lambda s: to_csv(wk), now=NOW)
    base = M.run(["DGC"], runner=runner, now=NOW)
    chk("P4: hàng cuối tuần bị loại (kết quả y hệt khi có/không có hàng T7/CN spike)", ow == base and "YoY +0,26" in ow)
    # truy vấn SQL
    sql = runner_sql[-1]
    chk("SQL: TE tường minh source='trading_economics' + cadence='daily'", "source='trading_economics'" in sql and "cadence='daily'" in sql)
    chk("SQL: P4 lấy source='sunsirs' từ 2018, không lẫn TE", "source='sunsirs' AND metric_key IN ('yellow_phosphorus') AND observation_date >= '2018-01-01'" in sql
        and "'yellow_phosphorus'" not in sql.split("source='sunsirs'")[0])
    chk("SQL: sunsirs lọc cuối tuần DAYOFWEEK BETWEEN 2 AND 6", "EXTRACT(DAYOFWEEK FROM observation_date) BETWEEN 2 AND 6" in sql)
    chk("SQL: KHÔNG dùng commodity_latest/unified", "commodity_latest" not in sql and "unified" not in sql and "commodity_prices" in sql)
    # freshness thiếu / cũ
    json.dump({"generated_at": (NOW - timedelta(hours=100)).isoformat(), "series": fresh}, open(fp, "w"))
    o2 = M.run(["AAA1"], runner=runner, now=NOW)
    chk("freshness file cũ >72h => KHÔNG ĐỦ TƯƠI, không số", "KHÔNG ĐỦ TƯƠI" in o2 and "YoY" not in o2)
    o2p = M.run(["DGC"], runner=runner, now=NOW)
    chk("freshness file cũ => P4 cũng KHÔNG ĐỦ TƯƠI, không số (nhất quán TE)", "KHÔNG ĐỦ TƯƠI" in o2p and "YoY" not in o2p and "sunsirs" in o2p)
    os.remove(fp)
    o3 = M.run(["AAA1"], runner=runner, now=NOW)
    chk("freshness file mất => KHÔNG ĐỦ TƯƠI, không số", "KHÔNG ĐỦ TƯƠI" in o3 and "YoY" not in o3)
    fresh["urea|trading_economics|daily"]["status"] = "FROZEN"
    json.dump({"generated_at": NOW.isoformat(), "series": fresh}, open(fp, "w"))
    chk("freshness FROZEN => KHÔNG ĐỦ TƯƠI", "KHÔNG ĐỦ TƯƠI" in M.run(["AAA1"], runner=runner, now=NOW))
    # P4 quá cũ (>7 ngày so với NOW) => KHÔNG ĐỦ TƯƠI nhưng vẫn kèm cảnh báo
    old = dict(series); old["yellow_phosphorus"] = synth(lambda d: 100.0, end="2026-10-10")
    o4 = M.run(["DGC"], runner=lambda s: to_csv(old), now=NOW)
    chk("P4 cũ >7 ngày => KHÔNG ĐỦ TƯƠI, không số, vẫn cảnh báo", "KHÔNG ĐỦ TƯƠI" in o4 and "YoY" not in o4 and "GÃY từ 2024" in o4)
    # fail-open
    def boom(sql): raise RuntimeError("BQ chết")
    try:
        r = M.run(["AAA1"], runner=boom, now=NOW); ok = (r == "")
    except Exception:
        ok = False
    chk("fail-open: BQ chết => '' không ném", ok)
    try:
        r = M.run(["AAA1"], runner=lambda s: "garbage,,\n1,2", now=NOW); ok = (r == "" or isinstance(r, str))
    except Exception:
        ok = False
    chk("fail-open: dữ liệu rác => không ném", ok)
    M.MAP_CSV = os.path.join(tmp, "khong_co.csv")
    try:
        ok = (M.run(["AAA1"], runner=runner, now=NOW) == "")
    except Exception:
        ok = False
    chk("fail-open: thiếu file map => ''", ok)
    return R


def hand_recompute():
    """Tái tính tay (pandas, độc lập module) c_yoy 2025Q3 của DPM (urea) và DRI (rubber) vs b2_panel.csv; module khớp cả hai."""
    import pandas as pd
    M = load(SRC, "orig_for_hand")
    d = pd.read_parquet(f"{RES}/te_daily.parquet")
    T = d.pivot(index="observation_date", columns="metric_key", values="value").sort_index()
    panel = pd.read_csv(f"{RES}/b2_panel.csv")
    R = []
    for tk, key in (("DPM", "urea"), ("DRI", "rubber")):
        s = T[key].dropna()
        q = s.resample("QE").mean(); n = s.resample("QE").count()
        a, b = q[pd.Timestamp("2025-09-30")], q[pd.Timestamp("2024-09-30")]
        assert n[pd.Timestamp("2025-09-30")] >= 40 and n[pd.Timestamp("2024-09-30")] >= 40
        hand = math.log(a / b)
        panel_v = float(panel[(panel.ticker == tk) & (panel.quarter == "2025Q3")].c_yoy.iloc[0])
        obs = [(i.strftime("%Y-%m-%d"), float(v)) for i, v in s[s.index <= "2025-09-30"].items()]
        mod_v = M.metrics(obs)["c_yoy_raw"]
        R.append((f"hand {tk}: tay == b2_panel ({hand:+.6f})", abs(hand - panel_v) < 1e-9))
        R.append((f"hand {tk}: module == b2_panel ({mod_v:+.6f})", abs(mod_v - panel_v) < 1e-9))
    return R


def tz_invariance():
    code = ("import sys,os; sys.path.insert(0,%r); import commodity_nowcast_block as M\n"
            "from datetime import datetime,timezone,timedelta\n"
            "print(M.load_fresh(path=sys.argv[1], now=datetime(2026,10,26,17,0,tzinfo=timezone(timedelta(hours=7))))[1])\n") % HERE
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "f.json")
        json.dump({"generated_at": "2026-10-26T16:58:16+07:00", "series": {}}, open(p, "w"))
        outs = []
        for tz in (None, "America/Los_Angeles", "Pacific/Kiritimati"):
            env = {k: v for k, v in os.environ.items() if k != "TZ"}
            if tz: env["TZ"] = tz
            outs.append(subprocess.run([sys.executable, "-c", code, p], capture_output=True, text=True, env=env).stdout)
    return [("TZ: load_fresh cùng kết quả dưới env -u TZ / LA / Kiritimati", len(set(outs)) == 1 and outs[0].strip() == "")]


MUTANTS = [
    ("M1 đổi dấu vai trò", 'sign=int(r["sign"])', 'sign=-int(r["sign"])'),
    ("M2 đọc commodity_latest", "FROM tav2_bq.commodity_prices \"\n         \"WHERE cadence='daily' AND",
     "FROM tav2_bq.commodity_latest \"\n         \"WHERE 1=1 AND"),
    ("M5 bỏ cảnh báo P4", "            if r[\"key\"] == P4_KEY:\n                lines.append(\"    \" + P4_WARN)\n    if not lines:", "            pass\n    if not lines:"),
    ("M6 P4 luôn tươi", "return ((now or datetime.now(ICT)).date() - last).days <= P4_MAX_AGE_D", "return True"),
    ("M3 bỏ kiểm freshness", 'return st.get("status") == "OK"', "return True"),
    ("M4 bỏ fail-open", 'warn(f"{type(e).__name__}: {e}")\n        return ""', "raise"),
]


def main():
    R = []
    with tempfile.TemporaryDirectory() as tmp:
        R += suite(load(SRC, "orig"), tmp)
    R += hand_recompute()
    R += tz_invariance()
    for n, ok in R:
        print(("PASS " if ok else "FAIL ") + n)
    npass = sum(ok for _, ok in R)
    print(f"-- {npass}/{len(R)} assertion PASS")
    src = open(SRC, encoding="utf-8").read()
    killed = 0
    for name, old, new in MUTANTS:
        assert old in src, f"mutant {name}: không tìm thấy đoạn gốc để đột biến"
        with tempfile.TemporaryDirectory() as tmp:
            mp = os.path.join(tmp, "mut.py"); open(mp, "w", encoding="utf-8").write(src.replace(old, new, 1))
            try:
                mr = suite(load(mp, "mut_" + name[:2]), tmp)
                dead = any(not ok for _, ok in mr)
            except Exception:                       # mutant làm suite nổ cũng tính là bị giết
                dead = True
        print(("KILLED   " if dead else "SURVIVED ") + name)
        killed += dead
    print(f"-- {killed}/{len(MUTANTS)} mutant bị giết")
    return 0 if npass == len(R) and len(R) >= 25 and killed == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main())
