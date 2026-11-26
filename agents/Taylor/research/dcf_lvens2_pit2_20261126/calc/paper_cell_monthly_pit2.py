# -*- coding: utf-8 -*-
"""paper_cell_monthly_pit2.py — bản pit2 của dcf_vn_behavioral_20261125/calc/paper_cell_monthly.py (md5 gốc ghi ở REPORT; bản gốc KHÔNG sửa).
GHI NHẬN hằng tháng ô bốn-ô + hi52 (DISPLAY-ONLY, paper). KHÔNG sizing/gate/wire. Logic ô/hạng GIỮ NGUYÊN bản gốc; chỉ đổi phần sổ:
  - nguồn lv_ENS2 DUY NHẤT = parquet lvens2_pit2.py (--lvens2-from), kèm sidecar .json (mode pit, mc_pit, script_md5, inputs_md5).
  - ledger ghi thêm: mc_pit, lvens2_md5, lvens2_script_md5, frozen_manifest_md5, ca_md5, E_unexpl (cờ E ngân hàng không giải thích được).
  - fail-closed (rc=3): file khác tháng/ngày as-of/mode; mc_pit ≠ --expect-mc; ledger đã có tháng với mc_pit/script khác (đổi biến thể giữa chừng);
    cache chưa ĐỒNG BỘ tới D (lvens2_pit2.sync_state, cả lúc dựng lvens2 lẫn lúc ghi sổ); universe_pit không phủ D; hash khối dòng cũ đổi.
  - [v3] CỔNG CHẠY TRỄ: chỉ ghi khi cuối-tháng(ym) < hôm nay (ICT) ≤ cuối-tháng(ym) + 5 ngày lịch. Neo ở cuối tháng chứ không ở D: tháng Tết phiên cuối có thể
    sớm cả tuần (2025-01: D=01-24), neo D sẽ loại vĩnh viễn tháng đó dù không có phiên nào giữa D và cuối tháng. Chọn fail-closed thay vì cờ `late` trong dòng:
    sổ forward chỉ có giá trị khi không ai chọn được ghi/không ghi sau khi đã thấy giá; dòng trễ có cờ vẫn nằm trong sổ và phụ thuộc người đọc nhớ lọc.
    PCM_NOW_ICT (giờ giả, selfcheck) bị TỪ CHỐI với sổ tên paper_cell_ledger_pit2.csv; computed_at_ict luôn là giờ thật.
  - [v3] ghi ca_ratio_stepcar + ca_ratio_stepca (hệ số thô từ CA extract; stepcar phải khớp ca_ratio của parquet); bản sao parquet đầu vào lưu theo md5 ở
    <thư mục sổ>/ledger_inputs/ (không bao giờ ghi đè).
  - append-only THẬT: mở file chế độ 'a', không ghi lại cả file; sidecar <ledger>.blocks.jsonl giữ md5 từng khối tháng, kiểm lại trước mỗi lần ghi.
Dùng: python paper_cell_monthly_pit2.py --asof-ym 2026-10 --lvens2-from out/final/lvens2_2026-10_mcstepcar.parquet [--ledger PATH] [--expect-mc stepcar] [--dry-run]"""
import argparse, hashlib, os, sys, json, io, shutil
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd, duckdb
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lvens2_pit2 as L  # noqa: E402
WC = os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude"); HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = f"{WC}/data/bq_cache"
LEDGER = os.environ.get("PCM_LEDGER", os.path.join(HERE, "..", "out", "paper_cell_ledger_pit2.csv"))
_ICT = ZoneInfo("Asia/Ho_Chi_Minh"); MINGRP = 15; LATE_DAYS = 5; CANON_NAME = "paper_cell_ledger_pit2.csv"
COLS = ["asof_ym", "asof_date", "ticker", "route", "lv_ENS2", "hi52", "v_grp", "v_all", "a", "cell", "panel_time_match", "E_unexpl", "ca_ratio_stepcar", "ca_ratio_stepca", "computed_at_ict",
        "mc_pit", "lvens2_md5", "lvens2_script_md5", "frozen_manifest_md5", "ca_md5"]
CELL = {(1, 1): "RE_DUOC_THUA_NHAN", (1, 0): "RE_CHUA_THUA_NHAN", (0, 1): "DAT_CON_NEO", (0, 0): "DAT_DANG_NGUOI"}


def md5b(b):
    return hashlib.md5(b).hexdigest()


def md5(p):
    return md5b(open(p, "rb").read())


def fail(msg):
    print("FAIL-CLOSED: " + msg, file=sys.stderr); return 3


def block_bytes(lines_by_ym, ym):
    return "".join(lines_by_ym.get(ym, [])).encode()


def read_blocks(ledger):
    """Trả (header, {ym: [dòng thô]}) — đọc thô để băm đúng byte đã ghi."""
    lines = open(ledger, encoding="utf-8").read().splitlines(keepends=True)
    out = {}
    for ln in lines[1:]:
        out.setdefault(ln.split(",", 1)[0], []).append(ln)
    return lines[0] if lines else "", out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--asof-ym", required=True); ap.add_argument("--ledger", default=LEDGER)
    ap.add_argument("--lvens2-from", required=True); ap.add_argument("--expect-mc", default="stepcar"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(); ym = a.asof_ym; side = a.ledger + ".blocks.jsonl"
    # ---- sổ cũ: kiểm hash từng khối trước mọi thứ (append-only thật) ----
    prev = []
    if os.path.exists(a.ledger):
        hdr, blocks = read_blocks(a.ledger)
        if hdr.strip() != ",".join(COLS):
            return fail(f"header {a.ledger} khác COLS hiện tại")
        prev = [json.loads(x) for x in open(side)] if os.path.exists(side) else []
        if sorted(blocks) != sorted(p["asof_ym"] for p in prev):
            return fail(f"tập tháng trong sổ {sorted(blocks)} ≠ sidecar {sorted(p['asof_ym'] for p in prev)}")
        for p in prev:
            if md5b(block_bytes(blocks, p["asof_ym"])) != p["block_md5"]:
                return fail(f"khối {p['asof_ym']} trong sổ đã bị sửa (md5 khác sidecar)")
        if ym in blocks:
            print(f"SKIP: {ym} đã có trong {a.ledger} (append-only, idempotent)"); return 0
    # ---- cổng chạy trễ (giờ ICT) ----
    now = datetime.now(_ICT)
    fake = os.environ.get("PCM_NOW_ICT")
    if fake:
        if os.path.basename(a.ledger) == CANON_NAME:
            return fail(f"PCM_NOW_ICT={fake} không được dùng với sổ chính {CANON_NAME}")
        now = datetime.fromisoformat(fake).replace(tzinfo=_ICT)
        print(f"WARN: giờ giả PCM_NOW_ICT={fake} (chỉ selfcheck)", file=sys.stderr)
    me = L.month_end(ym); late = (now.date() - me).days
    if not a.dry_run and not (0 < late <= LATE_DAYS):
        return fail(f"hôm nay {now.date()} (ICT) cách cuối tháng {me} {late} ngày — chỉ ghi khi 1..{LATE_DAYS} ngày (không ghi bù, không ghi sớm)")
    # ---- file lvens2 + sidecar ----
    src = a.lvens2_from; js = src.replace(".parquet", ".json")
    if not (os.path.exists(src) and os.path.exists(js)):
        return fail(f"thiếu {src} hoặc {js} — chạy lvens2_pit2.py --asof-ym {ym} --mc-pit {a.expect_mc} trước")
    meta = json.load(open(js))
    if meta.get("mc_pit") != a.expect_mc or meta.get("mode") != "pit" or meta.get("cache_vintage") or meta.get("nocut") or not meta.get("eguard", False):
        return fail(f"sidecar mc_pit={meta.get('mc_pit')} mode={meta.get('mode')} vintage={meta.get('cache_vintage')} nocut={meta.get('nocut')} eguard={meta.get('eguard')} "
                    f"— cần mc_pit={a.expect_mc}, mode pit, cache hiện tại, không mutation, eguard bật")
    for p in prev:
        if p["mc_pit"] != a.expect_mc or p["lvens2_script_md5"] != meta["script_md5"]:
            return fail(f"sổ đã có {p['asof_ym']} với mc_pit={p['mc_pit']} script={p['lvens2_script_md5'][:8]} ≠ {a.expect_mc}/{meta['script_md5'][:8]} "
                        f"— đổi biến thể/script giữa chừng: mở sổ MỚI (tên file mới), không trộn")
    # ---- dữ liệu as-of ----
    c = duckdb.connect()
    px = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close FROM read_parquet('{CACHE}/ticker/*.parquet')
                       WHERE Close > 0 AND CAST(time AS DATE) >= DATE '{ym}-01' - INTERVAL 450 DAY AND strftime(CAST(time AS DATE), '%Y-%m') <= '{ym}'""").df()
    px["time"] = pd.to_datetime(px.time)
    D = px[px.time.dt.strftime("%Y-%m") == ym].time.max()
    if pd.isna(D):
        return fail(f"không có giá ngày nào của {ym}")
    ok, det = L.sync_state(CACHE, CACHE, ym, D)
    if not ok:
        return fail(f"cache chưa đồng bộ tới D {D.date()}: " + "; ".join(det["bad"]))
    fr = meta.get("freshness") or {}
    if fr.get("rule") != "sync-v2" or fr.get("ok") is not True:
        return fail(f"{js}: lvens2 không dựng trên cache đã qua cổng sync-v2 (freshness={fr.get('rule')}/{fr.get('ok')})")
    u = pd.read_parquet(f"{CACHE}/universe_pit/{D.year}.parquet", columns=["time", "ticker", "in_universe"]); u["time"] = pd.to_datetime(u.time)
    ud = u[u.time == D]
    if ud.empty:
        return fail(f"universe_pit không phủ {D.date()} (max {u.time.max().date()})")
    px = px.sort_values(["ticker", "time"]).reset_index(drop=True); g = px.groupby("ticker")
    px["hi52"] = np.log(px.Close) - np.log(g.Close.rolling(252, min_periods=120).max().reset_index(level=0, drop=True).sort_index().values)
    f = px[px.time == D][["ticker", "hi52"]]
    pan = pd.read_parquet(src, columns=["ticker", "ym", "time", "known", "route", "lv_ENS2", "asof_date", "mode", "mc_pit", "E_unexpl", "ca_ratio"])
    if set(pan.ym.astype(str)) != {ym} or set(pd.to_datetime(pan.asof_date)) != {D} or set(pan["mode"]) != {"pit"} or set(pan.mc_pit) != {a.expect_mc}:
        return fail(f"{src} ym={sorted(set(pan.ym.astype(str)))} asof={sorted(set(pan.asof_date.astype(str)))} mode/mc={sorted(set(pan['mode']))}/{sorted(set(pan.mc_pit))} không khớp {ym}/{D.date()}")
    cap, want = L.ca_cfg()
    if want != meta["inputs_md5"]["ca_extract"] or md5(cap) != want:
        return fail(f"extract CA {cap} md5 {md5(cap)[:8]} / LVENS2_CA_MD5 {want[:8]} ≠ extract đã dựng lvens2 {meta['inputs_md5']['ca_extract'][:8]}")
    ca = L.load_ca()
    rows = pan[["ticker"]].assign(known=pan.known.astype(L.NS), time=pan.time.astype(L.NS))
    pan["ca_ratio_stepcar"] = L.ca_factor(rows, ca, include_rights=True)[0]; pan["ca_ratio_stepca"] = L.ca_factor(rows, ca, include_rights=False)[0]
    if not np.allclose(pan.ca_ratio_stepcar.values, pan.ca_ratio.values, rtol=0, atol=1e-12):
        return fail(f"ca_ratio tính lại lệch parquet ở {int((~np.isclose(pan.ca_ratio_stepcar, pan.ca_ratio, rtol=0, atol=1e-12)).sum())} dòng")
    d = ud[ud.in_universe].merge(f, on="ticker").merge(pan[["ticker", "time", "route", "lv_ENS2", "E_unexpl", "ca_ratio_stepcar", "ca_ratio_stepca"]].rename(columns={"time": "ptime"}), on="ticker").dropna(subset=["hi52", "lv_ENS2"]).copy()
    if len(d) < 50:
        return fail(f"chỉ {len(d)} mã đủ dữ liệu ở {ym}")
    d["v_all"] = d.lv_ENS2.rank(pct=True); d["a"] = d.hi52.rank(pct=True); d["isb"] = d.route == "BANK"
    d["v_grp"] = d.groupby("isb").lv_ENS2.rank(pct=True); n = d.groupby("isb").ticker.transform("size"); d["v_grp"] = np.where(n >= MINGRP, d.v_grp, d.v_all)
    d["cell"] = [CELL[(int(v >= 0.5), int(x >= 0.5))] for v, x in zip(d.v_grp, d.a)]
    d["panel_time_match"] = (d.ptime == D); d["asof_ym"] = ym; d["asof_date"] = D.date()
    d["computed_at_ict"] = datetime.now(_ICT).strftime("%Y-%m-%d %H:%M"); d["mc_pit"] = a.expect_mc; d["lvens2_md5"] = md5(src)
    d["lvens2_script_md5"] = meta["script_md5"]; d["frozen_manifest_md5"] = meta["inputs_md5"]["frozen_manifest"]; d["ca_md5"] = meta["inputs_md5"]["ca_extract"]
    out = d[COLS].sort_values("ticker")
    print(f"{ym}: as-of {D.date()} n={len(out)} (BANK {int(d.isb.sum())}) mc={a.expect_mc} E_unexpl={int(out.E_unexpl.sum())}"); print(out.cell.value_counts().to_string())
    if a.dry_run:
        print("dry-run: không ghi"); return 0
    buf = io.StringIO(); out.to_csv(buf, index=False, header=False, lineterminator="\n"); body = buf.getvalue()
    os.makedirs(os.path.dirname(os.path.abspath(a.ledger)), exist_ok=True)
    new = not os.path.exists(a.ledger)
    keep = os.path.join(os.path.dirname(os.path.abspath(a.ledger)), "ledger_inputs"); os.makedirs(keep, exist_ok=True)   # bản sao đầu vào, trước khi ghi sổ
    for p_in in (src, js):
        dst = os.path.join(keep, f"lvens2_{ym}_{md5(src)[:8]}{os.path.splitext(p_in)[1]}")
        if not os.path.exists(dst):
            tmp = dst + f".{os.getpid()}.tmp"; shutil.copyfile(p_in, tmp); os.replace(tmp, dst)
        elif p_in == src and md5(dst) != md5(src):
            return fail(f"{dst} đã có nội dung khác — không ghi đè")
    with open(a.ledger, "a", encoding="utf-8") as fh:              # append thật — không ghi lại dòng cũ
        if new:
            fh.write(",".join(COLS) + "\n")
        fh.write(body); fh.flush(); os.fsync(fh.fileno())
    with open(side, "a") as fh:
        fh.write(json.dumps({"asof_ym": ym, "block_md5": md5b(body.encode()), "rows": len(out), "mc_pit": a.expect_mc, "lvens2_script_md5": meta["script_md5"],
                             "lvens2_md5": md5(src), "written_at_ict": datetime.now(_ICT).isoformat(timespec="seconds")}) + "\n")
    print("ĐÃ GHI", a.ledger); return 0


if __name__ == "__main__":
    sys.exit(main())
