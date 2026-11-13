---
kind: local-file
status: DEPRECATED (bản sao lưu đông cứng — đừng wire mới; dùng cột `VNINDEX_PE` của data/VNINDEX.csv hoặc BQ mirror)
source: data/VNINDEX_pe_only.csv
group: research-caches
frozen_since: 2026-05-10
writer: rebuild_vnindex_csv.py (L50, shutil.copy của data/VNINDEX.csv CŨ trước khi rebuild) — không cron
registered: 2026-11-12 (Taylor, job Taylor_20261112_162001, Luồng D1e theo quant-skeptic live-gap-phase3)
---

# data/VNINDEX_pe_only.csv

**Status: DEPRECATED — bản sao lưu một lần, không ai cập nhật.**

⚠️ SUPERSEDED BY `data/VNINDEX.csv` (cột `VNINDEX_PE`) / BQ mirror ON 2026-05-10 (frozen_since; bổ sung dòng thiếu 2026-11-14 KB weekly review).

## Là gì
Bản copy `data/VNINDEX.csv` phiên bản CŨ (trước lần `rebuild_vnindex_csv.py` thay bằng OHLCV từ BQ).
Cột: `time,Open,High,Low,Close,Volume,Pe,trading_session,volume_session,ticker`. 3051 phiên non-null `Pe`,
**2014-01-02 → 2026-03-30**. mtime 2026-05-10 20:37 (+07) = lúc chạy rebuild (shutil.copy không giữ mtime gốc).

## Bằng chứng status (đo 2026-11-12, `wc_venv` pandas)
- Writer duy nhất: `rebuild_vnindex_csv.py:50` (`backup = .../VNINDEX_pe_only.csv; shutil.copy(VNINDEX.csv, backup)`).
  Không có trong crontab; không script nào khác ghi.
- So với `data/VNINDEX.csv` cột `VNINDEX_PE` (non-null **2006-03-30 → 2026-05-26**, 5008 phiên):
  2014–2018 **trùng 100%** (1245 phiên, max|Δ| 0); 2019–2026 khớp |Δ|<0,01 ở **85,0%** của 1803 phiên,
  max|Δ| 3,99, corr 0,989 — tức là 2019+ KHÔNG đồng nhất (nguồn PE được restate sau bản sao lưu).
- Reader còn sống: `mike/agents/Taylor/exp_market_prob/analyze.py:11`, `research/live_gap_phase3_20261112/analyze.py:389` (research).

## Bẫy
1. Lý do GĐ3 (12/11) đổi sang file này — "VNINDEX.csv chỉ có VNINDEX_PE, NULL trước 2016" — **SAI**:
   `VNINDEX_PE` trong VNINDEX.csv có từ 2006-03-30 (BQ mirror đã backfill 2026-07-29, xem
   [`../price-volume/vnindex_pe_mirror_col.md`](../price-volume/vnindex_pe_mirror_col.md)).
2. Dừng 2026-03-30 — mọi phân tích sau mốc đó sẽ ffill giá trị cũ.
3. 2019+ lệch VNINDEX_PE ở ~15% phiên ⇒ hai chuỗi không thay thế nhau khi cần tái lập số cũ: ghi rõ dùng chuỗi nào.

## Dùng thay
Cột `VNINDEX_PE` của `data/VNINDEX.csv` (offline, dừng ~2026-05-26) hoặc BQ mirror `t.VNINDEX_PE` (CANONICAL, floor 2008).
