# -*- coding: utf-8 -*-
"""
lagged_cache_adjusted.py — dựng lại earnings_px.pkl / lagged_pos_ov.pkl trên CƠ SỞ GIÁ ĐIỀU CHỈNH.

Vì sao kéo lại TOÀN lịch sử mỗi ngày, không append:
  `tav2_bq.ticker.Close/Open` là giá điều chỉnh HỒI TỐ — mỗi sự kiện quyền (cổ tức tiền, thưởng,
  chia tách) nhân lại MỌI phiên trước ngày GDKHQ của mã đó. Append dòng mới lên dòng cũ ⇒ dòng cũ
  kẹt ở cơ sở "điều chỉnh tới ngày fetch" ⇒ ngày GDKHQ thành cú rơi giả (vd PHR post_ret −45,8%).
  Cách duy nhất để mọi phiên cùng một cơ sở là kéo lại cả chuỗi của mỗi mã cùng một lúc.

Vì sao đọc BQ SỐNG, không đọc BQ_LOCAL_CACHE:
  `data/bq_cache/ticker/<năm>.parquet` chỉ tải lại năm hiện tại mỗi đêm; năm cũ chỉ tải lại khi
  LỆCH SỐ DÒNG (sync_bq_cache._drifted_years). Hồi tố giá không đổi số dòng ⇒ năm cũ trong cache
  kẹt cơ sở cũ. Đo 2026-11-10: 1.196 cặp (mã, năm) 2013–2025 có SUM(Close) cache ≠ BQ sống
  (research/lag_cache_adjusted_20261110/data/cache_vs_bq_close_mismatch.csv); cache cũng không có
  2011–2012. Chi phí BQ sống: xem doc kb/projects/lag-cache-adjusted-20261110.md §5 (16 truy vấn theo năm, số đo dry-run).

Không phụ thuộc corporate_action (cơ sở điều chỉnh do chính BQ tính).
"""
import os
import shutil
import tempfile
from datetime import datetime, timezone
import numpy as np
import pandas as pd

PX_COLS = ["ticker", "time", "Close"]
OV_COLS = ["ticker", "time", "Open", "Volume_3M_P50", "Price"]   # Price = giá THÔ (cơ sở của Volume_3M_P50, cho ADV)

# Ngưỡng kiểm (fail ⇒ KHÔNG ghi). Đặt theo số đo 2026-11-10, xem REPORT.
DEPTH_FRAC = 0.50        # phiên có số mã < 50% trung vị 60 phiên trước ⇒ thưa
DEPTH_FROM = "2014-01-01"  # trước 2014 thị trường mỏng/biến động số mã lớn — không kiểm tương đối
LOST_KEYS_MAX = 0.002    # tối đa 0,2% cặp (mã, phiên) của bản cũ biến mất ở bản mới
SESSION_DROP_MAX = 0.05  # phiên nào mất >5% số mã so với bản cũ ⇒ fail
CARRY_TICKERS_MAX = 20   # >20 mã MỚI bị BQ cắt lịch sử (chưa nằm trong `known_carried`) cùng lúc = sự cố nguồn ⇒ fail
# Độ phủ cột ADV (lag_adv_basis.adv_px rơi LẶNG LẼ về giá điều chỉnh khi Price NaN ⇒ phải chặn ở đây).
# Đo 2026-11-13 trên data/lagged_pos_ov.pkl (max 2026-11-11), loại mã mang sang: 60 phiên gần nhất NaN
# Price = 0, Volume_3M_P50 = 0; max theo phiên 2025–2026: Price 0,00% / V3 0,40%; max 2020+: 1,49% / 1,88%
# (cửa sổ 60 phiên 1,16% / 1,66%). Dòng mang sang (cơ sở cũ, không có Price) KHÔNG tính — đã biết, có log.
COVER_COLS = ("Price", "Volume_3M_P50")
COVER_SESSIONS = 60      # số phiên (T2–T6) gần nhất được kiểm
COVER_WIN_NAN_MAX = 0.02   # NaN trung bình cả cửa sổ > 2% ⇒ fail
COVER_SESS_NAN_MAX = 0.05  # một phiên bất kỳ NaN > 5% ⇒ fail


def live_bq(bq_fn):
    """Bọc bq() để đi BQ SỐNG (tạm gỡ BQ_LOCAL_CACHE). Xem docstring module."""
    def _q(sql):
        saved = os.environ.pop("BQ_LOCAL_CACHE", None)
        try:
            return bq_fn(sql)
        finally:
            if saved is not None:
                os.environ["BQ_LOCAL_CACHE"] = saved
    return _q


def copy_atomic(src, dst):
    """Chép ra tmp cùng thư mục rồi os.replace: bị kill giữa chừng không để lại bản cụt tại `dst`
    (`if not exists(.pre_adj)` sẽ không bao giờ tạo lại một bản cụt)."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dst) or ".", prefix=os.path.basename(dst) + ".", suffix=".tmp")
    os.close(fd)
    try:
        shutil.copy2(src, tmp); os.replace(tmp, dst)
    finally:
        if os.path.exists(tmp): os.remove(tmp)


def new_asof():
    """Mốc snapshot BQ cho MỌI khúc năm (UTC, giây). Giờ hệ thống không ảnh hưởng (UTC tường minh)."""
    return datetime.now(timezone.utc).replace(microsecond=0)


def asof_clause(asof):
    """FOR SYSTEM_TIME AS OF cố định ⇒ 16 khúc năm đọc CÙNG một snapshot (BQ sync/restate giữa chừng
    không làm khúc 2011 và khúc 2026 lệch cơ sở điều chỉnh). Đặt SAU `AS t`."""
    return "" if asof is None else f" FOR SYSTEM_TIME AS OF TIMESTAMP '{pd.Timestamp(asof).strftime('%Y-%m-%dT%H:%M:%SZ')}'"


def pull_adjusted(q, start, end, tickers, asof=None):
    """Kéo ticker/time/Close/Open/Volume_3M_P50/Price(thô), [start, end], chia khúc theo năm, cùng snapshot `asof`.
    `q` = hàm sql -> DataFrame (BQ sống). Trả DataFrame đã lọc theo `tickers`, sort (ticker, time)."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    parts = []
    for y in range(start.year, end.year + 1):
        a = max(start, pd.Timestamp(f"{y}-01-01")).date()
        b = min(end, pd.Timestamp(f"{y}-12-31")).date()
        df = q(f"""SELECT t.ticker, t.time, t.Close, t.Open, t.Volume_3M_P50, t.Price FROM tav2_bq.ticker AS t{asof_clause(asof)}
WHERE t.time BETWEEN DATE '{a}' AND DATE '{b}' AND t.Close > 0""")
        if df is None or not len(df):
            raise RuntimeError(f"BQ trả rỗng cho năm {y} ({a}..{b})")
        parts.append(df)
    d = pd.concat(parts, ignore_index=True)
    d["time"] = pd.to_datetime(d["time"]).astype("datetime64[ns]")
    d = d[d["ticker"].isin(set(tickers))]
    d = d.drop_duplicates(["ticker", "time"]).sort_values(["ticker", "time"]).reset_index(drop=True)
    return d


def carry_truncated(new, old, cols):
    """BQ đôi khi XOÁ lịch sử cũ của một mã (đo 2026-11-10: PMT, SSC, TLD, VFC, VTH chỉ còn từ
    2026-10-14 ⇒ 16.597 dòng). Kéo lại toàn bộ sẽ xoá theo. Luật: với mã mà dòng cũ BIẾN MẤT nằm
    TRƯỚC phiên đầu tiên BQ còn giữ (lịch sử bị cắt đầu) hoặc mã biến mất hẳn, mang các dòng cũ đó
    sang NGUYÊN TRẠNG (cơ sở cũ — log rõ). Lỗ hổng GIỮA chuỗi BQ không mang sang (validate tính mất).
    Trả (frame đã mang sang, DataFrame tóm tắt theo mã)."""
    first = new.groupby("ticker")["time"].min()
    o = old.merge(new[["ticker", "time"]], on=["ticker", "time"], how="left", indicator=True)
    o = o[o["_merge"] == "left_only"].drop(columns="_merge")
    f = o["ticker"].map(first)
    car = o[f.isna() | (o["time"] < f)]
    if not len(car):
        return new, pd.DataFrame(columns=["ticker", "rows", "first_old", "last_old", "bq_first"])
    summ = (car.groupby("ticker")["time"].agg(rows="count", first_old="min", last_old="max")
            .reset_index().assign(bq_first=lambda d: d["ticker"].map(first)))
    out = (pd.concat([new, car[[c for c in cols if c in car.columns]]], ignore_index=True)
           .sort_values(["ticker", "time"]).reset_index(drop=True))
    return out, summ


def thin_sessions(cnt):
    """Phiên có số mã < DEPTH_FRAC × trung vị 60 phiên TRƯỚC (shift(1): phiên đang xét không tự kéo trung vị)."""
    base = cnt.rolling(60, min_periods=20).median().shift(1)
    # dòng rác T7/CN (2025-05-04/11, 1 mã — có cả ở BQ) không phải phiên
    chk = cnt[(cnt.index >= pd.Timestamp(DEPTH_FROM)) & (cnt.index.dayofweek < 5)]
    return chk[chk < DEPTH_FRAC * base.reindex(chk.index)]


def coverage_problems(new, carried_tickers=()):
    """Độ phủ COVER_COLS ở COVER_SESSIONS phiên gần nhất (bỏ mã mang sang). Trả (problems, stats)."""
    P, S = [], {}
    miss = [c for c in COVER_COLS if c not in new.columns]
    if miss:
        return [f"thiếu cột {miss} trong bản mới"], S
    w = new[(new["time"].dt.dayofweek < 5) & ~new["ticker"].isin(set(carried_tickers))]
    sess = np.sort(w["time"].unique())[-COVER_SESSIONS:]
    w = w[w["time"].isin(sess)]
    if not len(w):
        return ["độ phủ: cửa sổ kiểm rỗng"], S
    for c in COVER_COLS:
        per = w[c].isna().groupby(w["time"]).mean()
        win, mx = float(w[c].isna().mean()), float(per.max())
        S[f"nan_{c}_win{COVER_SESSIONS}"] = round(win, 5); S[f"nan_{c}_sess_max"] = round(mx, 5)
        if win > COVER_WIN_NAN_MAX:
            P.append(f"{c} NaN {win:.2%} trên {len(sess)} phiên gần nhất (>{COVER_WIN_NAN_MAX:.0%})")
        if mx > COVER_SESS_NAN_MAX:
            bad = per[per > COVER_SESS_NAN_MAX]
            P.append(f"{c} NaN >{COVER_SESS_NAN_MAX:.0%} ở {len(bad)} phiên: "
                     + ", ".join(f"{pd.Timestamp(d).date()}={v:.0%}" for d, v in bad.tail(5).items()))
    return P, S


def validate(new, old, end, carried_tickers=()):
    """So bản mới (điều chỉnh) với bản cũ. Trả (problems: list[str], stats: dict). problems rỗng ⇒ ghi được."""
    P, S = [], {}
    end = pd.Timestamp(end)
    if not len(new):
        return ["bản mới rỗng"], S
    if new["Close"].isna().any() or (new["Close"] <= 0).any():
        P.append("Close NaN/<=0 trong bản mới")
    cp, cs = coverage_problems(new, carried_tickers)
    P.extend(cp); S.update(cs)
    S["new_max"] = str(new["time"].max().date()); S["old_max"] = str(old["time"].max().date())
    if new["time"].max() != end:
        P.append(f"max(time) bản mới {S['new_max']} != END {end.date()}")
    if new["time"].max() < old["time"].max():
        P.append(f"bản mới lùi ngày: {S['new_max']} < bản cũ {S['old_max']}")
    # độ sâu tương đối theo phiên
    cnt = new.groupby("time")["ticker"].nunique().sort_index()
    thin = thin_sessions(cnt)
    S["min_tickers_per_session_from_2026-06-01"] = int(cnt[cnt.index >= "2026-06-01"].min()) if (cnt.index >= "2026-06-01").any() else None
    if len(thin):
        P.append(f"{len(thin)} phiên thưa (<{DEPTH_FRAC:.0%} trung vị 60 phiên): "
                 + ", ".join(f"{d.date()}={n}" for d, n in thin.head(10).items()))
    # độ phủ so với bản cũ (chỉ trong [min new, end])
    o = old[(old["time"] >= new["time"].min()) & (old["time"] <= end)]
    k_old = pd.MultiIndex.from_frame(o[["ticker", "time"]])
    k_new = pd.MultiIndex.from_frame(new[["ticker", "time"]])
    lost = k_old.difference(k_new)
    S["old_keys"] = len(k_old); S["lost_keys"] = len(lost); S["added_keys"] = len(k_new.difference(k_old))
    if len(k_old) and len(lost) / len(k_old) > LOST_KEYS_MAX:
        P.append(f"mất {len(lost):,}/{len(k_old):,} cặp (mã,phiên) so với bản cũ (>{LOST_KEYS_MAX:.1%})")
    oc = o.groupby("time")["ticker"].nunique()
    j = pd.concat([oc.rename("old"), cnt.rename("new")], axis=1).fillna(0)
    j = j[j["old"] >= 50]                      # bỏ dòng rác cuối tuần (1 mã) của bản cũ
    drop = j[j["new"] < (1 - SESSION_DROP_MAX) * j["old"]]
    S["sessions_dropping"] = len(drop)
    if len(drop):
        P.append(f"{len(drop)} phiên mất >{SESSION_DROP_MAX:.0%} số mã so với bản cũ: "
                 + ", ".join(f"{d.date()} {int(r.old)}->{int(r.new)}" for d, r in drop.head(10).iterrows()))
    return P, S


def split_frames(new):
    px = new[PX_COLS].reset_index(drop=True)
    ov = new[OV_COLS].reset_index(drop=True)
    return px, ov


def one_day_jumps(px, top=20, since=None):
    """Top |ret 1 phiên| theo Close (để soát cú rơi giả ngày GDKHQ)."""
    p = px.sort_values(["ticker", "time"]).copy()
    p["ret"] = p.groupby("ticker")["Close"].pct_change()
    p["prev_time"] = p.groupby("ticker")["time"].shift(1)
    if since is not None:
        p = p[p["time"] >= pd.Timestamp(since)]
    p = p.dropna(subset=["ret"])
    return p.reindex(p["ret"].abs().sort_values(ascending=False).index).head(top)[["ticker", "prev_time", "time", "Close", "ret"]]


def build(q, old_px, old_ov, end, known_carried=(), asof=None):
    """Đường DUY NHẤT dựng bản điều chỉnh (refresh_lagged_caches dùng; research dùng y hệt).
    `known_carried` = mã đã được mang sang ở các lần chạy trước (state do refresh lưu): dòng mang sang đã nằm
    trong pkl cũ nên hôm sau lại "biến mất khỏi BQ" — chỉ mã MỚI bị cắt mới tính vào CARRY_TICKERS_MAX.
    Trả (px_new, ov_new, problems, stats, carried_summary). problems khác rỗng ⇒ KHÔNG được ghi."""
    asof = new_asof() if asof is None else asof   # mọi khúc năm CÙNG một snapshot BQ
    old_px = old_px.assign(time=pd.to_datetime(old_px["time"]).astype("datetime64[ns]"))
    old_ov = old_ov.assign(time=pd.to_datetime(old_ov["time"]).astype("datetime64[ns]"))
    old = old_px.merge(old_ov, on=["ticker", "time"], how="outer")
    tks = sorted(set(old["ticker"]))
    new = pull_adjusted(q, old["time"].min(), end, tks, asof=asof)
    new, carried = carry_truncated(new, old, PX_COLS + OV_COLS[2:])   # đủ cột: Close, Open, Volume_3M_P50, Price
    problems, stats = validate(new, old_px, end, carried_tickers=set(carried["ticker"]) if len(carried) else ())
    stats["carried_tickers"] = len(carried); stats["carried_rows"] = int(carried["rows"].sum()) if len(carried) else 0
    new_carried = sorted(set(carried["ticker"]) - set(known_carried)) if len(carried) else []
    stats["carried_new"] = len(new_carried); stats["asof"] = None if asof is None else str(pd.Timestamp(asof))
    if len(new_carried) > CARRY_TICKERS_MAX:
        problems.append(f"{len(new_carried)} mã MỚI bị BQ cắt lịch sử (>{CARRY_TICKERS_MAX}) — nghi sự cố nguồn")
    px_new, ov_new = split_frames(new)
    return px_new, ov_new, problems, stats, carried
