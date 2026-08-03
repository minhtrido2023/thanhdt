# -*- coding: utf-8 -*-
"""lag_forensic_filter.py — GATE QUẢN TRỊ (BANNED vĩnh viễn + cờ forensic) cho book LAG.

VÌ SAO CÓ FILE NÀY (job Taylor_20260803_015850 §7 → user duyệt, job Taylor_20260803_035250):
engine backtest ĐÃ có gate forensic từ 2026-06-20 (`pt_v23_audit_2014.py:1035`,
`LAG_FORENSIC_GATE=1` mặc định ON) nhưng ĐƯỜNG LIVE thì KHÔNG có gì — `grep forensic|BANNED`
trong `golive_recommend_v23.py` + `lag_live_schedule.py` trả 0 kết quả. Hệ quả đo được ngày
2026-08-03: **VVS** (BANNED vĩnh viễn trong `mike/kb/KNOWLEDGE.md` VÀ `forensic_flags.csv`
severity=`exclude`) và **BFC** (forensic `exclude`) đi qua TOÀN BỘ gate LAG tự động và nằm
trong 84 ứng viên sống. Ngày 2026-07-30 VVS chỉ bị chặn BẰNG TAY (DollarBill ghi "VVS=BANNED"
trong plan note) ⇒ lớp phòng thủ khi đó là TRÍ NHỚ của người/LLM lập plan, không phải cơ chế.
Đúng loại lỗ hổng mà `filter_lag_rating_orders` (P1) đã được xây để vá ở tầng lệnh.

BẢN CHẤT = CỔNG AN TOÀN/QUẢN TRỊ, KHÔNG PHẢI THAM SỐ TỐI ƯU LỢI NHUẬN. Không có ngưỡng nào
được dò từ dữ liệu; danh sách BANNED là quyết định của user, cờ forensic là phán quyết thủ công
đã ghi ngày. Vì vậy DSR/PBO không áp dụng. Gate này KHÔNG đổi một chữ số nào của số pin R3:
trong cửa sổ backtest (`AUDIT_END=2026-06-19`) mọi cờ forensic đều ghi ngày 2026-06-20 ⇒ drop 0
event (đã verify lại, job Taylor_20260803_035250).

HAI NGUỒN, HAI NGỮ NGHĨA KHÁC NHAU:
  1. `BANNED` (hằng số dưới) — cấm VĨNH VIỄN, KHÔNG có ngày hiệu lực ⇒ áp mọi lúc. Nguồn chuẩn
     tắc = `mike/kb/KNOWLEDGE.md` ("Cổ phiếu BANNED vĩnh viễn"). Hằng số này được nhân bản
     (giống `mike/bin/build_universe_pit_quality.py:71`) vì module này phải chạy được không cần
     BQ client; self-check ĐỐI CHIẾU CƠ HỌC cả 2 nguồn để không trôi lệch âm thầm.
  2. `data/forensic_flags.csv` severity=`exclude` — CÓ NGÀY hiệu lực (`date`). Áp khi
     `date <= asof` (asof = NGÀY RA QUYẾT ĐỊNH, live = hôm nay). KHÔNG hồi tố: replay một ngày
     trong quá khứ sẽ KHÔNG thấy cờ được gắn sau ngày đó. severity=`watch` KHÔNG loại.

     ⚠️ **CỐ Ý KHÁC engine — mốc so sánh là `asof`, KHÔNG phải `Release_Date`.** Engine
     (`pt_v23_audit_2014.py:1051`) so `Release_Date >= date` vì trong replay lịch sử thời điểm
     ra quyết định ≈ Release_Date, nên đó chính là "không hindsight" ĐÚNG cho engine. Ở đường
     LIVE thì thời điểm quyết định là HÔM NAY: một event công bố 2026-05-04 của mã bị gắn cờ
     2026-06-20 mà hôm nay mới xét mua thì PHẢI chặn — hôm nay ta ĐÃ biết mã đó bị loại. Đây
     không phải chi tiết lý thuyết: kiểm tra trực tiếp trên rổ thật 2026-08-03 cho thấy tiêu chí
     `Release_Date` sẽ **KHÔNG chặn BFC** (release gần nhất 2026-05-04 < ngày cờ) — đúng ca mà
     job Taylor_20260803_015850 §7 nêu là lỗ hổng. Hai mốc trùng nhau trong mọi ca event mới
     (release ≥ ngày cờ), chỉ khác ở event cũ — và ở đó `asof` mới là đáp án đúng.

FAIL-SAFE (khác nhau theo nguồn, có chủ ý):
  · `BANNED` là hằng số trong code ⇒ KHÔNG THỂ hỏng ⇒ luôn áp, fail-closed tuyệt đối.
  · Đọc `forensic_flags.csv` hỏng (thiếu file/hỏng định dạng) → GIỮ NGUYÊN danh sách + trả
    error string (fail-open) để `status.json` phân biệt "không có mã nào bị cờ" vs "gate không
    chạy được". Fail-CLOSED ở đây sẽ phải chặn TOÀN BỘ book LAG vì một file lỗi — thiệt hại lớn
    hơn hẳn rủi ro, và tầng BANNED vẫn giữ nguyên hiệu lực làm sàn. Cùng nguyên tắc với
    `lag_rating_filter.lag_filter_low_rating` (fail-open khi CẢ NGUỒN hỏng, fail-closed từng mã).
  · `asof` không đọc được/thiếu → coi như "mọi cờ đều đã hiệu lực" (fail-closed): thà chặn nhầm
    một mã bị gắn cờ còn hơn để lọt. BANNED không phụ thuộc `asof`.

PHẠM VI = CHỈ book LAG (tầng sinh tín hiệu). BAL/CAPIT/custom30V có cơ chế riêng đang chạy
(`anomaly_excluded` cho pool CAPIT, golden floor + BANNED đã nằm trong `universe_pit_quality`
cho custom30V) — KHÔNG đụng. Tầng LỆNH của LAG hiện chỉ có lưới rating
(`trading_bot.plan.filter_lag_rating_orders`); một lưới forensic/BANNED tương ứng ở tầng lệnh
CHƯA có — nằm ngoài phạm vi job này, đã nêu làm việc mở.

Consumer: deploy_golive_dt5g_v4/golive_recommend_v23.py.
Self-check: lag_forensic_filter_selfcheck.py
"""
import os

import pandas as pd

# Cấm VĨNH VIỄN — nguồn chuẩn tắc `mike/kb/KNOWLEDGE.md` ("Cổ phiếu BANNED vĩnh viễn").
# Bản sao thứ hai: `mike/bin/build_universe_pit_quality.py:71`. Self-check so khớp cả 2 nguồn.
BANNED = frozenset({"PC1", "VVS", "KSF", "NKG", "HSG", "HVN", "VJC", "NVL", "GEG", "SBA",
                    "DMC", "IMP", "TRA", "TOS", "VTP"})

FORENSIC_CSV = "data/forensic_flags.csv"
EXCLUDE_SEVERITY = "exclude"
BANNED_TAG = "BANNED vĩnh viễn (mike/kb/KNOWLEDGE.md)"


def _load_forensic_excludes(csv_path):
    """{ticker: Timestamp ngày hiệu lực} cho các dòng severity=exclude. Ném lỗi nếu đọc hỏng."""
    ff = pd.read_csv(csv_path)
    out = {}
    for _, r in ff.iterrows():
        if str(r["severity"]).strip().lower() != EXCLUDE_SEVERITY:
            continue
        tk = str(r["ticker"]).strip()
        d = pd.Timestamp(r["date"])
        # Cùng mã có nhiều cờ exclude → lấy ngày SỚM NHẤT (bảo thủ: chặn từ cờ đầu tiên).
        if tk not in out or d < out[tk]:
            out[tk] = d
    return out


def lag_filter_forensic_banned(cand, asof, workdir=None, csv_path=None):
    """Loại ứng viên LAG thuộc danh sách BANNED hoặc bị cờ forensic severity=exclude.

    Tham số:
      cand      DataFrame ứng viên LAG (cần cột `ticker`).
      asof      NGÀY RA QUYẾT ĐỊNH (live: phiên dữ liệu mới nhất). Cờ forensic chỉ áp khi
                `flag_date <= asof` — xem docstring module về việc CỐ Ý khác engine.
      workdir   thư mục gốc repo để dựng đường dẫn `data/forensic_flags.csv` (mặc định = cwd).
      csv_path  ghi đè hẳn đường dẫn CSV (dùng cho self-check).

    KHÔNG nhận `bq` (khác 2 filter anh em): cả 2 nguồn đều là dữ liệu cục bộ, không truy vấn BQ.

    Trả (cand đã lọc, list dict mô tả mã bị loại, lỗi-nguồn|None). Mỗi dict:
    {"ticker", "kind" ("banned"|"forensic"), "flag_date" (str|None), "reason"}.
    """
    if cand is None or not len(cand):
        return cand, [], None
    path = csv_path or os.path.join(workdir or "", FORENSIC_CSV)
    src_err = None
    forx = {}
    try:
        forx = _load_forensic_excludes(path)
    except Exception as ex:
        src_err = f"{type(ex).__name__}: {ex}"
        print(f"  WARNING: không đọc được {path} ({ex}) — cờ forensic KHÔNG được áp (fail-open); "
              f"danh sách BANNED vĩnh viễn VẪN áp. Xem lag_forensic_filter_error trong status.json")
    try:
        asof_ts = pd.Timestamp(asof)
        if pd.isna(asof_ts):
            raise ValueError("asof là NaT")
    except Exception:
        asof_ts = pd.Timestamp.max      # fail-closed: mọi cờ coi như đã hiệu lực
    # Cờ đã hiệu lực TÍNH TỚI asof (điều kiện duy nhất — không dùng Release_Date, xem docstring).
    active = {tk for tk, fd in forx.items() if fd <= asof_ts}

    dropped = []
    for tk in sorted(set(str(t).strip() for t in cand["ticker"])):
        if tk in BANNED:
            dropped.append({"ticker": tk, "kind": "banned", "flag_date": None,
                            "reason": f"BANNED_TICKER — {BANNED_TAG}"})
        elif tk in active:
            fd = forx[tk].date()
            dropped.append({"ticker": tk, "kind": "forensic", "flag_date": str(fd),
                            "reason": f"FORENSIC_EXCLUDE — cờ {fd} ≤ asof {asof_ts.date()}, "
                                      f"{FORENSIC_CSV} severity={EXCLUDE_SEVERITY}"})
    if dropped:
        bad = {d["ticker"] for d in dropped}
        cand = cand[~cand["ticker"].astype(str).str.strip().isin(bad)].copy()
    return cand, dropped, src_err
