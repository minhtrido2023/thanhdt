# Cửa sổ NHÌN LÙI của cổng chứng nhận AIS — job `Taylor_20260820_062330`

## Kết quả chuẩn tắc
**`final_diff.txt`** — TRƯỚC = `main` (297eae30) · SAU = `/tmp/wc_certwt` (bản sao ĐÚNG BẰNG
md5 với code cuối cùng của worktree `wt-oshares-cert`). Đây là con số phải trích dẫn.

## ⚠️ Bẫy provenance — 3 snapshot "sau", chỉ MỘT cái là code cuối
Chúng được sinh ở 3 mốc khác nhau TRONG lúc bản vá còn đang viết dở. Ghi lại ở đây vì md5 của
chúng khác nhau, và người đọc sau sẽ tưởng cùng một code cho ra hai kết quả (nondeterminism) —
không phải, code khác nhau thật:

| File | Code | Dùng được? |
|---|---|---|
| `snap_after_20260301.json` (13:44) | **TRƯỚC** khi `_unabsorbed_iss` nhận `verdicts` | ❌ trung gian |
| `snap_variant_20260301.json` (13:51) | có `_unabsorbed_iss`, khác code cuối ở COMMENT | ~ tương đương |
| `snap_final_20260301.json` (13:59) | **= code cuối** (md5 `e5c6973e…`) | ✅ chuẩn tắc |

Hai mã lệch giữa `snap_after` và `snap_final` — và cả hai lệch đều là bằng chứng cho bước
`_unabsorbed_iss`, không phải nhiễu:
* **TCB**: `AIS_EXACT 7.064.851.739` → `ANCHOR_ONLY 7.086.240.414`. Không có bước
  `_unabsorbed_iss` thì ESOP ex 2025-08-04 (21.388.675 CP) bị coi là ĐÃ niêm yết ⇒ dòng quý bị
  loại ⇒ phục vụ số THẤP hơn sự thật 0,30%. AIS 2026-08-05 xác nhận 7.086.240.414. Ca này đóng
  băng thành `LB6`/`LB6b`.
* **DTD**: cùng SỐ, chỉ đổi nhãn `FIN_FALLBACK`/`verified=False` → `ANCHOR_ONLY`/`verified=True`.

Chỉ có `n_universe`/số đếm từ chối là giống nhau (263 · 17 · 6) nên **log không đủ để phân
biệt** — phải so nội dung. Đó là lý do có bảng này.

## Delta trên rổ 263 mã (asof 2026-03-01, PIT + LIVE)
* **PIT**: từ chối 28 → 17 (**+11 mã được phủ**). Cả 11 đều là `None → số` (CỨU).
  **KHÔNG mã nào đổi từ số này sang số khác.**
* **LIVE**: từ chối 7 → 6 (+1: TCB). 4 mã còn lại cùng SỐ, chỉ đổi nhãn.
* **Chi phí look-ahead KHÔNG ĐỔI**: PIT 4 → 4 (`ABB/HAH/NVL/TDC`), LIVE 5 → 5
  (+`KBC`). Thêm: `[]` · bớt: `[]` ở cả hai nhánh.

## Tái lập
```bash
cd <WC>/mike/agents/Taylor/research/oshares_live_anchor_20260820
python3 snapshot_probe.py --asof 2026-03-01 --out <snap.json>   # (bản trong ../oshares_lookback_20260820)
python3 ../oshares_lookback_20260820/diff_snapshots.py <before.json> <after.json>
```
