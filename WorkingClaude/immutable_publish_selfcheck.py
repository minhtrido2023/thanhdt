# -*- coding: utf-8 -*-
"""
immutable_publish_selfcheck.py — self-check cho `state_publish_immutable.py`.

CHẠY HOÀN TOÀN TRÊN BẢNG SANDBOX (`tav2_bq._ipsc_*`), KHÔNG BAO GIỜ chạm bảng production.
Sandbox được tạo bằng cách CLONE bảng production thật (`vnindex_5state`,
`vnindex_5state_dt5g_live`) nên test chạy trên đúng dữ liệu/hình dạng thật.

Phủ đúng 3 self-check bắt buộc của dispatch Taylor_20260730_013951 + các bất biến kèm theo:
  A. publisher mới trên dữ liệu HÔM NAY -> MỌI phiên đã chốt giống hệt bản đang có (0 diff)
  B. đuôi chưa chốt (25 phiên) khớp CHÍNH XÁC chuỗi tính theo công thức cũ
     (đây là thay đổi CÁCH GHI, không phải CÔNG THỨC)
  C. mô phỏng backfill upstream (viết lại 101 phiên đã chốt — đúng quy mô sự cố 2026-07-29):
     phần đã chốt KHÔNG đổi, và số phiên bị chặn được ĐẾM ĐÚNG
  D. idempotent: chạy lại 2 lần -> không đổi gì, asof_date không bị bump oan
  E. append phiên mới -> vào bảng, đúng asof_date, phần cũ nguyên vẹn
  F. seal rolling: phiên rơi ra khỏi cửa sổ 25 thì CHỐT (lần sau không đổi được nữa)
  G. fail-closed: chuỗi tính bị TỤT HẬU (stale) -> abort, KHÔNG xoá phiên đã công bố
  H. fail-closed: chuỗi ngắn hơn seal_n / có ngày trùng / có NULL -> abort
  I. publish_immutable nhận DataFrame trực tiếp (đúng đường publish_gated_state.py đang dùng
     sau khi đổi thứ tự: tính -> publish -> mới export CSV)
  J. export_published_csv: CSV == BẢNG ĐÃ CÔNG BỐ (không phải chuỗi tính lại), schema đúng
     3 cột, atomic (không để lại .tmp). Đây là vế chặn "CSV và BQ lệch nhau" — 7 script
     nghiên cứu đọc CSV này làm chuỗi DT5G.

Run: $DNA_PYEXE immutable_publish_selfcheck.py
"""
import os, sys, io, subprocess
from datetime import date, timedelta
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)          # sandbox test phải đọc BQ thật
os.environ["IMMUTABLE_NO_ALERT"] = "1"          # test cố ý kích alert -> KHÔNG spam Telegram đội

import state_publish_immutable as spi
from state_publish_immutable import (publish_immutable, snapshot_vintage, PublishAbort,
                                     _bq_query, PROJECT)

SEAL_N = 25
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def drop(tbl):
    subprocess.run(["bq", "rm", "-f", "-t", f"{PROJECT}:{tbl}"],
                   capture_output=True, text=True, timeout=180)


def clone(src, dst):
    drop(dst)
    _bq_query(f"CREATE TABLE `{PROJECT}.{dst}` AS SELECT time, state, state_raw "
              f"FROM `{PROJECT}.{src}`")


def fetch(tbl, cols="time, state, state_raw"):
    df = _bq_query(f"SELECT {cols} FROM `{PROJECT}.{tbl}` ORDER BY time")
    df["time"] = pd.to_datetime(df["time"])
    return df


def run_case(label, src_table, sandbox, new_csv):
    print(f"\n{'='*88}\n  {label}  (sandbox {sandbox} <- clone of {src_table})\n{'='*88}")
    clone(src_table, sandbox)
    baseline = fetch(sandbox)
    new = pd.read_csv(new_csv); new["time"] = pd.to_datetime(new["time"])
    new = new.sort_values("time").reset_index(drop=True)
    cutoff = pd.Timestamp(new["time"].iloc[-(SEAL_N + 1)])
    print(f"  baseline {len(baseline)} dòng {baseline['time'].iloc[0].date()}"
          f"->{baseline['time'].iloc[-1].date()} · cutoff (chốt tới) = {cutoff.date()}")

    # ── A. publish hôm nay -> vùng đã chốt 0 diff ────────────────────────────────────────
    st = publish_immutable(new_csv, sandbox, f"selfcheck {label}", seal_n=SEAL_N)
    after = fetch(sandbox)
    b_seal = baseline[baseline["time"] <= cutoff].reset_index(drop=True)
    a_seal = after[after["time"] <= cutoff].reset_index(drop=True)
    same = b_seal.equals(a_seal)
    check(f"A · {label} · vùng đã chốt (time<={cutoff.date()}) BẤT BIẾN, 0 diff",
          same and st["sealed_immutable"],
          f"{len(a_seal)} dòng, checksum khớp; upstream muốn đổi {st['n_sealed_diff']} phiên "
          f"nhưng đã bị CHẶN")

    # ── B. đuôi khớp chính xác chuỗi tính theo công thức cũ ─────────────────────────────
    a_tail = after[after["time"] > cutoff][["time", "state", "state_raw"]].reset_index(drop=True)
    n_tail = new[new["time"] > cutoff][["time", "state", "state_raw"]].reset_index(drop=True)
    check(f"B · {label} · đuôi {len(a_tail)} phiên == chuỗi tính công thức cũ (byte-for-byte)",
          a_tail.equals(n_tail), f"{len(n_tail)} phiên đối chiếu")

    # ── D. idempotent ────────────────────────────────────────────────────────────────────
    before2 = fetch(sandbox, "time, state, state_raw, asof_date")
    st2 = publish_immutable(new_csv, sandbox, f"selfcheck {label} rerun", seal_n=SEAL_N)
    after2 = fetch(sandbox, "time, state, state_raw, asof_date")
    check(f"D · {label} · idempotent (chạy lại lần 2 không đổi gì, kể cả asof_date)",
          before2.equals(after2) and st2["n_sealed_diff"] == st["n_sealed_diff"],
          "0 dòng đổi")

    # ── C. mô phỏng backfill upstream viết lại 101 phiên đã chốt (quy mô 2026-07-29) ────
    forged = new.copy()
    seal_idx = forged.index[forged["time"] <= cutoff]
    hit = list(seal_idx[-400:-299])                       # 101 phiên đã chốt, cách xa đuôi
    forged.loc[hit, "state"] = forged.loc[hit, "state"].map(lambda v: 1 if v != 1 else 5)
    forged.loc[hit, "state_raw"] = forged.loc[hit, "state_raw"].map(lambda v: 1 if v != 1 else 5)
    fpath = os.path.join(WORKDIR, f"data/_ipsc_forged_{sandbox.split('.')[-1]}.csv")
    f2 = forged.copy(); f2["time"] = f2["time"].dt.strftime("%Y-%m-%d"); f2.to_csv(fpath, index=False)
    pre_forge = fetch(sandbox)
    st3 = publish_immutable(fpath, sandbox, f"selfcheck {label} FORGED", seal_n=SEAL_N)
    post_forge = fetch(sandbox)
    check(f"C · {label} · backfill giả viết lại {len(hit)} phiên đã chốt -> KHÔNG lan vào bảng",
          pre_forge.equals(post_forge) and st3["sealed_immutable"],
          f"bảng không đổi 1 dòng nào; publisher ĐẾM ĐÚNG {st3['n_sealed_diff']} phiên bị chặn "
          f"(kỳ vọng {len(hit)})")
    check(f"C2 · {label} · telemetry đếm đúng số phiên upstream muốn viết lại",
          st3["n_sealed_diff"] == len(hit), f"n_sealed_diff={st3['n_sealed_diff']} == {len(hit)}")
    os.unlink(fpath)

    # ── E/F. append 30 phiên mới -> phiên cũ CHỐT dần, không đổi được nữa ───────────────
    # Dùng chính chuỗi FORGED (vẫn còn 101 phiên lịch sử sai) + 30 phiên mới ở đuôi.
    ext = forged.copy()
    last = ext["time"].iloc[-1]
    extra = pd.DataFrame({"time": pd.bdate_range(last + timedelta(days=1), periods=30),
                          "state": 2, "state_raw": 2})
    ext = pd.concat([ext, extra], ignore_index=True)
    epath = os.path.join(WORKDIR, f"data/_ipsc_ext_{sandbox.split('.')[-1]}.csv")
    e2 = ext.copy(); e2["time"] = e2["time"].dt.strftime("%Y-%m-%d"); e2.to_csv(epath, index=False)
    pre_ext = fetch(sandbox)
    st4 = publish_immutable(epath, sandbox, f"selfcheck {label} APPEND", seal_n=SEAL_N)
    post_ext = fetch(sandbox)
    added = post_ext[~post_ext["time"].isin(pre_ext["time"])]
    kept = post_ext[post_ext["time"].isin(pre_ext["time"])].reset_index(drop=True)
    old_common = pre_ext[pre_ext["time"].isin(post_ext["time"])].reset_index(drop=True)
    # 30 phiên mới: 25 vào qua MERGE đuôi, 5 rơi vào vùng đã chốt nhưng CHƯA TỪNG công bố ->
    # phải được GAP-FILL (append), nếu không chuỗi công bố thủng lỗ vĩnh viễn.
    check(f"E · {label} · append 30 phiên mới (25 đuôi + 5 gap-fill) -> đủ, phần đã công bố nguyên vẹn",
          len(added) == 30 and kept.equals(old_common) and st4["n_gapfilled"] == 5,
          f"{len(added)} dòng mới (gap-fill {st4['n_gapfilled']}); {len(kept)} dòng cũ không đổi")
    # F: 30 phiên mới đẩy cutoff tiến lên -> những phiên vừa rời cửa sổ 25 đã CHỐT; chuỗi
    #    forged vẫn sai 101 phiên lịch sử nhưng KHÔNG sửa được gì.
    check(f"F · {label} · cutoff tiến lên sau append, phần vừa chốt vẫn bất biến",
          st4["sealed_immutable"] and st4["cutoff"] > st["cutoff"],
          f"cutoff {st['cutoff']} -> {st4['cutoff']}")
    os.unlink(epath)

    # ── G. fail-closed khi chuỗi tính TỤT HẬU (stale compute) ───────────────────────────
    stale = ext.iloc[:-40].copy()
    spath = os.path.join(WORKDIR, f"data/_ipsc_stale_{sandbox.split('.')[-1]}.csv")
    s2 = stale.copy(); s2["time"] = s2["time"].dt.strftime("%Y-%m-%d"); s2.to_csv(spath, index=False)
    pre_stale = fetch(sandbox)
    try:
        publish_immutable(spath, sandbox, f"selfcheck {label} STALE", seal_n=SEAL_N)
        ok, why = False, "KHÔNG abort (nguy hiểm: sẽ xoá phiên đã công bố)"
    except PublishAbort as e:
        ok, why = True, f"abort đúng: {str(e)[:70]}"
    check(f"G · {label} · chuỗi tính tụt hậu -> fail-CLOSED, không xoá phiên đã công bố",
          ok and fetch(sandbox).equals(pre_stale), why)
    os.unlink(spath)
    drop(sandbox)


def run_guard_cases():
    print(f"\n{'='*88}\n  H · fail-closed trên input hỏng\n{'='*88}")
    sb = "tav2_bq._ipsc_guard"
    clone("tav2_bq.vnindex_5state_dt5g_live", sb)
    base = fetch(sb)
    cases = {
        "chuỗi ngắn hơn seal_n": base.head(10),
        "có ngày TRÙNG": pd.concat([base, base.tail(1)], ignore_index=True),
        "có state NULL": base.assign(state=base["state"].astype("float").mask(
            base.index == len(base) // 2)),
    }
    for name, df in cases.items():
        p = os.path.join(WORKDIR, "data/_ipsc_bad.csv")
        d = df.copy(); d["time"] = pd.to_datetime(d["time"]).dt.strftime("%Y-%m-%d")
        d.to_csv(p, index=False)
        pre = fetch(sb)
        try:
            publish_immutable(p, sb, f"selfcheck bad ({name})", seal_n=SEAL_N)
            ok, why = False, "KHÔNG abort"
        except PublishAbort as e:
            ok, why = True, f"abort đúng: {str(e)[:60]}"
        check(f"H · {name} -> fail-CLOSED", ok and fetch(sb).equals(pre), why)
        os.unlink(p)
    drop(sb)


def run_df_and_csv_cases():
    """I + J — đúng đường mà publish_gated_state.py dùng sau khi đổi thứ tự ghi."""
    print(f"\n{'='*88}\n  I/J · publish từ DataFrame + export CSV mirror từ BQ\n{'='*88}")
    sb = "tav2_bq._ipsc_dfcsv"
    clone("tav2_bq.vnindex_5state_dt5g_live", sb)
    base = fetch(sb)
    cutoff = pd.Timestamp(base["time"].iloc[-(SEAL_N + 1)])

    # ── I. publish trực tiếp từ DataFrame, KHÔNG qua file CSV ────────────────────────────
    # Dựng đúng hình dạng publish_gated_state.py tạo: cột time là STRING 'YYYY-MM-DD'.
    # Cố ý làm SAI 60 phiên đã chốt để chắc chắn nhánh DataFrame cũng được bảo vệ y như
    # nhánh CSV (nếu chỉ test đường CSV thì đường production thật lại không được phủ).
    df_in = base.copy()
    hit = list(df_in.index[df_in["time"] <= cutoff][-500:-440])
    df_in.loc[hit, "state"] = df_in.loc[hit, "state"].map(lambda v: 1 if v != 1 else 5)
    df_in["time"] = df_in["time"].dt.strftime("%Y-%m-%d")
    pre = fetch(sb)
    st = publish_immutable(df_in, sb, "selfcheck DF-input", seal_n=SEAL_N)
    post = fetch(sb)
    check("I · publish_immutable nhận DataFrame; 60 phiên đã chốt bị sửa -> KHÔNG lan vào bảng",
          pre.equals(post) and st["sealed_immutable"] and st["n_sealed_diff"] == len(hit),
          f"n_sealed_diff={st['n_sealed_diff']} (kỳ vọng {len(hit)}), bảng không đổi 1 dòng")

    # ── J. export CSV mirror TỪ BQ (không phải từ df_in đã bị làm sai) ───────────────────
    out_csv = os.path.join(WORKDIR, "data/_ipsc_mirror.csv")
    n = spi.export_published_csv(sb, out_csv)
    got = pd.read_csv(out_csv)
    want = fetch(sb)[["time", "state", "state_raw"]].copy()
    want["time"] = want["time"].dt.strftime("%Y-%m-%d")
    got_cmp = got.copy(); got_cmp["time"] = got_cmp["time"].astype(str)
    check("J1 · CSV == bảng đã công bố (byte-for-byte), KHÔNG phải chuỗi tính lại",
          n == len(want) and got_cmp.reset_index(drop=True).equals(want.reset_index(drop=True)),
          f"{n} dòng khớp tuyệt đối")
    check("J2 · CSV giữ đúng schema 3 cột [time,state,state_raw] (không đụng 7 consumer)",
          list(got.columns) == ["time", "state", "state_raw"], f"cols={list(got.columns)}")
    # Bằng chứng CSV KHÔNG mang 60 phiên sai của df_in: đây là mấu chốt của J.
    forged_dates = set(pd.to_datetime(base.loc[hit, "time"]).dt.strftime("%Y-%m-%d"))
    m = got[got["time"].isin(forged_dates)].merge(
        base.assign(time=base["time"].dt.strftime("%Y-%m-%d"))[["time", "state"]],
        on="time", suffixes=("_csv", "_orig"))
    check("J3 · CSV mang state ĐÃ CÔNG BỐ ở 60 phiên bị làm sai (không mang bản restate)",
          len(m) == len(hit) and (m["state_csv"] == m["state_orig"]).all(),
          f"{len(m)}/{len(hit)} phiên khớp bản đã công bố")
    check("J4 · atomic: không để lại file .tmp", not os.path.exists(out_csv + ".tmp"))
    os.unlink(out_csv)
    drop(sb)


if __name__ == "__main__":
    print("=" * 88)
    print("  IMMUTABLE PUBLISH SELF-CHECK  (sandbox tav2_bq._ipsc_*, KHÔNG chạm production)")
    print("=" * 88)
    run_case("BASE v3.4b", "tav2_bq.vnindex_5state", "tav2_bq._ipsc_base",
             os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_4b_full_history.csv"))
    run_case("DT5G live", "tav2_bq.vnindex_5state_dt5g_live", "tav2_bq._ipsc_dt5g",
             os.path.join(WORKDIR, "data/vnindex_5state_dt5g_live.csv"))
    run_guard_cases()
    run_df_and_csv_cases()

    n_ok = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{'='*88}\n  KẾT QUẢ: {n_ok}/{len(RESULTS)} PASS\n{'='*88}")
    for name, ok, _ in RESULTS:
        if not ok:
            print(f"  FAILED: {name}")
    sys.exit(0 if n_ok == len(RESULTS) else 1)
