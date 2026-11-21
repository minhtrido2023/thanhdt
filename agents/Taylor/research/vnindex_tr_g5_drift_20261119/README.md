# G5 drift — vì sao `k2_synth_pr` trôi cao hơn VN-Index (job Taylor_20261119_034548)

Chỉ đọc + phân tích. Không sửa code, ngưỡng, `data/benchmark/` hay chuỗi sealed.
Dữ liệu: BQ `tav2_bq.ticker` + `corporate_action` kéo 19/11 qua đúng `fetch_bq()` của
`mike/bin/vnindex_total_return.py` (`pull.py` → `bq_inputs_20260504.pkl`). Cửa sổ G5 = 60 phiên
15/08 → 11/11/2026, VN-Index chính thức +1,031%.

## KẾT LUẬN (đã chứng minh, trừ chỗ ghi "suy đoán")

Lệch G5 +0,516pp ngày 11/11 **không phải lỗi công thức** mà là **rổ thiếu vốn hoá**: bốn mã HOSE lớn
mới niêm yết bị rơi khỏi rổ một cách IM LẶNG vì BQ không có số CP (`OShares` NULL) hoặc không có dòng
giá. Ba mã trong số đó giảm mạnh sau khi niêm yết, nên VN-Index chính thức (có chúng) tăng ít hơn rổ.

| Bước | G5 11/11 (pp) | Thay đổi | Bằng chứng |
|---|---:|---:|---|
| Chuỗi CSV (dòng sealed) | **+0,516** | | `data/benchmark/vnindex_tr_daily.csv` |
| Dựng lại bằng BQ hôm nay, cùng code | +0,262 | −0,254 | `decomp.py`; cùng kết quả cho vintage 10-14 và latest |
| ↳ dựng lại nhưng bỏ LPS trước 12/10 | +0,520 | (khớp CSV, lệch tối đa 0,29bp/phiên) | `LPS` là nguyên nhân duy nhất của khoảng −0,254 |
| + DMX (BQ có giá, `OShares` NULL) | +0,102 | −0,160 | `counterfactual.py` |
| + GEL, CRV (không có dòng nào trong `tav2_bq.ticker`) | **+0,039** | −0,063 | `counterfactual.py` |

Phần còn lại 0,04pp nằm trong nhiễu lịch sử (2019–2024 G5 trung bình +0,02 … +0,14).

### Nguyên nhân 1: LPS vắng mặt trong dòng sealed 19/08 → 09/10 (−0,25pp) — ĐÃ CHỨNG MINH
- LPS (CK LPBank) niêm yết HOSE 18/08/2026, vốn hoá ~44,8 nghìn tỷ (≈0,55% rổ), giá **−46%** từ
  19/08 đến 09/10 trong khi VN-Index +0,2%.
- Dòng `ticker_financial` ĐẦU TIÊN của LPS: quý 2026Q3, `Release_Date` **2026-10-20**. Trước ngày đó
  `ticker.OShares` của LPS là NULL ⇒ `div_yield_daily` loại LPS (`S1 > 0` sai) — và **G8 không báo**,
  vì G8 chỉ bắt mã có `OShares` cũ để ffill (`S1_ff > 0`), mã mới niêm yết chưa từng có `OShares` thì
  vô hình.
- Các dòng 19/08–06/10 seal lúc dựng đầu 13/10; 07–09/10 seal 15–17/10 — đều trước 20/10. Dòng 12–13/10
  được restate 21/10 (vì lý do khác) nên đã có LPS: `mc` CSV lệch −0,4…−0,65% đến 09/10, rồi chỉ −0,04%.
- `--update` kiểm dòng sealed CHỈ bằng `y` (SEALED_Y_TOL) và `vnindex`; LPS không trả cổ tức trong kỳ
  nên `y` không đổi ⇒ không có gì báo dòng sealed đã cũ về `k2_synth_pr`/`n_members`/`mc`.

### Nguyên nhân 2: DMX vẫn vắng mặt từ khi niêm yết 06/08 (−0,16pp) — ĐÃ CHỨNG MINH (mức độ: ước lượng số CP)
- DMX (Đầu tư Điện Máy Xanh) niêm yết HOSE 06/08/2026. BQ có giá nhưng `OShares` NULL ở mọi dòng
  `ticker` và cả 2 dòng `ticker_financial` (2026Q2, 2026Q3). Bị loại khỏi rổ ở MỌI dòng, kể cả hôm nay.
- Vốn hoá 97,6 nghìn tỷ (VNDirect `/v4/ratios/latest` itemCode 51003, 18/11) ⇒ ~1,27 tỷ CP (**ước lượng**:
  giả định số CP không đổi trong cửa sổ) ≈ 1,2% rổ. Giá 89.800 (14/08) → 76.400 (11/11).
- Giá phản thực DMX/GEL/CRV lấy từ DNSE chart-api (có thể đã điều chỉnh cổ tức ⇒ phản thực có thể
  đánh giá THẤP tác động DMX một chút, vì không thấy cú rơi ngày GDKHQ 18/08 — suy đoán).

### Nguyên nhân 3: GEL, CRV không có dòng nào trong `tav2_bq.ticker` (−0,06pp) — ĐÃ CHỨNG MINH (ước lượng số CP)
- GEL (HOSE từ 06/02/2026, vốn hoá 21,4 nghìn tỷ), CRV (HOSE từ 10/10/2025, 15,7 nghìn tỷ): `SELECT ...
  FROM tav2_bq.ticker WHERE ticker IN (...)` trả 0 dòng. Lỗ hổng ingest, không phải lỗi rổ. README
  bước 4 đã ghi "rổ thiếu 47/406 mã HOSE nhỏ" — hai mã này KHÔNG nhỏ.

### Giả định cơ sở chưa kiểm trực tiếp (suy đoán)
VN-Index đưa mã mới niêm yết vào tính toán ngay sau vài phiên đầu (luật HOSE-Index chưa đọc lại trong
phiên này). Bằng chứng gián tiếp: thêm DMX/LPS từ ngày niêm yết làm G5 giảm về gần 0 — nếu VN-Index
không gồm chúng thì thêm vào phải làm lệch TĂNG.

## Trả lời 7 câu hỏi

| # | Câu hỏi | Trả lời | Bằng chứng |
|---|---|---|---|
| 1 | Hệ thống hay nhiễu? | **Hệ thống** (rổ thiếu 4 mã giảm giá). (a) lệch ngày tương quan +0,58 với lợi suất VN-Index (hồi quy d = 1,48bp × off% + 0,41bp; sau khi thêm 3 mã còn +0,49) — rổ nặng mã lớn hơn chính thức vì mẫu số thiếu vốn hoá. (b) tương quan với \|Δn\| −0,14 — yếu. (c) đúng: ngày mã VÀO rổ là nguồn gốc (LPS 19/08, DMX 06/08). (d) với y: +0,04 — không. (e) hồi quy lệch lên lợi suất vượt của 16 mã lớn: VIC dư trọng số +0,72pp (t=4,5, 138 phiên), đóng góp +0,17…+0,21pp — đúng với mẫu số thiếu ~2% vốn hoá (20,5% × ~3,5% ≈ 0,7pp), không phải lỗi `OShares` riêng của VIC (VIC `OShares` 7,762 tỷ, không đổi từ 05/05) | `resid.py`, `wreg.py`, `daily_diff_rebuild.csv` |
| 2 | `OShares` lệch? | Lệch đáng kể duy nhất là **NULL** (LPS trước 20/10, DMX tới nay). Cập nhật trễ sau phát hành nhỏ và không cùng dấu: VHM 1:1 GDKHQ 06/08 cập nhật 07/08; VPB 24/09; TPB +15% cập nhật 06/10 sau GDKHQ 02/10; VIC ISS 0,73% (10/07) chưa vào `OShares`. Thử dùng `OShares_t` thay `_{t-1}`: G5 0,262 → 0,281 (+0,02). Không có nguồn KL niêm yết HOSE trong kho (chỉ có vốn hoá VNDirect 51003, dùng cho phản thực) | `resid.py` (bảng cap-jump), lệnh trong `counterfactual.py` |
| 3 | Rổ/vintage? | Vintage KHÔNG ảnh hưởng: dựng lại bằng vintage 10-14 và latest cho G5 giống hệt (0,262, chênh 0,0bp). Bảng sàn ĐÚNG (có LPS, DMX, GEL, CRV); mã bị rơi ở bước sau (thiếu `OShares`/giá). 11/11: 408 mã HOSE, 347 vào rổ, 61 rơi (40 không có dòng ngày đó — chủ yếu mã nhỏ không giao dịch; 20 bị lọc t-1; 1 thiếu `OShares`) | `missing.py` |
| 4 | Close vs Price? | Synth dùng lợi suất `Close/Close_{t-1}` (điều chỉnh) trừ `y`, trọng số `Price_{t-1}×OShares_{t-1}`. Không có trộn lẫn làm sai lợi suất. Giá `Price` kẹt ngày GDKHQ (TRAP `ticker_price_stale_on_exdate.md`) làm trọng số sai 1 phiên (TRC 16/09: vốn hoá ×3,7; PHR 14/09; TPB 02/10). Thay `Price_{t-1}` bằng `Close_{t-1}×Price_t/Close_t`: G5 0,262 → 0,242 (−0,02) — nhỏ | `resid.py` |
| 5 | VN-Index đổi CP ở ngày hiệu lực, synth theo `OShares` hằng ngày? | Kiểm theo dấu: dùng `OShares_t` (cập nhật sớm hơn) làm G5 +0,02, ngược lại −0,02 — cỡ 0,02pp, không phải nguồn lệch dương 0,5 | như trên |
| 6 | Lệch có tăng theo thời gian? | Chuỗi CSV: G5 cuối tháng 2026 ≤ 0,12 tới tháng 7, rồi 0,29 (08) / 0,27 (09) / 0,34 (10) / 0,52 (11/11) — tăng từ khi LPS/DMX niêm yết. Bản dựng lại + 3 mã: \|G5\| tuần ≤ 0,10 suốt 08–11. Từ 2019: 15/1.966 phiên vượt 0,5, gồm 11 đợt, MỌI đợt trước đó chỉ 1–2 phiên = gai dữ liệu một ngày (vd 09/04/2025 BQ lặp giá; 04/03/2026 2,98). 11/11 là lần vượt đầu tiên kiểu TRÔI. ⇒ ngưỡng 0,5 có sức phân biệt: bắt đúng một lỗ hổng dữ liệu thật | `g5_rolling_rebuild.csv`, lệnh lịch sử trong phiên |
| 7 | `y` bị ô nhiễm? | Có, chủ yếu do **DMX cổ tức tiền mặt 4.000 đ/CP GDKHQ 18/08** không vào tử số (DMX bị loại). Σy cửa sổ: rebuild 34,04bp → hiệu chỉnh (+cổ tức DMX, +vốn hoá 3 mã ở mẫu số) 39,64bp ⇒ **TR gộp 60 phiên thấp khoảng 5,6bp** (ước lượng, số CP DMX giả định). Mẫu số thiếu ~2% làm `y` cao nhẹ (<1bp). Phần GIÁ của TR dùng nguyên VN-Index chính thức ⇒ lệch `k2_synth_pr` KHÔNG vào TR | phép tính trong phiên (README này) |

## Khuyến nghị (xếp hạng)

1. **Lấp dữ liệu (Winston/bq_admin, không cần đổi code):** `OShares` cho DMX (NULL cả `ticker` lẫn
   `ticker_financial`); nạp GEL, CRV vào `tav2_bq.ticker`. Mức chắc chắn: cao. Sau khi lấp, dòng 18/08
   sẽ đổi `y` ~+6bp ⇒ `--update` sẽ (đúng) từ chối vì dòng sealed đổi — cần `--restate-sealed 2026-08-18`
   + user duyệt.
2. **Vá điểm mù G8 (đổi code — cần user duyệt):** G8 chỉ thấy mã từng có `OShares`. Đề xuất cổng mới:
   mã ĐANG trong bảng sàn HOSE, có giá phiên t (hoặc không có dòng nào) mà không vào rổ ⇒ báo, kèm vốn
   hoá ngoài (VNDirect 51003) nếu lấy được; ngưỡng theo vốn hoá như G8. Cả LPS lẫn DMX lẽ ra phải bị bắt
   ngay từ phiên đầu.
3. **Kiểm dòng sealed rộng hơn `y` (đổi code — cần user duyệt):** VERIFY_SEALED chỉ so `y`/`vnindex`;
   thêm cảnh báo (không chặn) khi `n_members`/`mc` dựng lại lệch dòng sealed >0,3% — đó chính là dấu vết
   LPS (−0,4…−0,65% suốt 7 tuần).
4. **Restate 19/08–09/10 cho LPS: KHÔNG cần cho TR** (`y` không đổi, TR không đổi); chỉ làm G5 sạch lại.
   Nếu muốn ⇒ `--restate-sealed` + user duyệt. Nên gộp một lần với restate 18/08 sau bước 1.
5. **G5_TOL: KHÔNG đổi.** Bằng chứng: rổ đủ thì \|G5\| ≤ 0,10 cả cửa sổ; lần vượt 11/11 là cảnh báo
   ĐÚNG về lỗ hổng dữ liệu. Nới ngưỡng sẽ che đúng lớp lỗi này.

## Cần user duyệt
- Mọi `--restate-sealed` (18/08 sau khi có `OShares` DMX; tuỳ chọn 19/08–09/10).
- Đổi code G8 (mục 2) và kiểm sealed (mục 3).
- Ack G5 cho kỳ báo cáo chứa 11/11 trong lúc chờ: lệch là do rổ, phần GIÁ của TR vẫn đúng; sai số TR
  thực tế ≈ −5,6bp gộp (do cổ tức DMX), cho kỳ chứa 18/08.

## File
`pull.py` (BQ → pkl) · `decomp.py` (tái lập k2, khung theo mã; tái lập CSV tối đa 4,1bp/phiên ở dòng sealed
cũ = đúng hiệu ứng LPS) · `resid.py` (LOO, cap-jump, tương quan) · `wreg.py` (hồi quy Δw) · `missing.py`
(mã HOSE rơi khỏi rổ) · `counterfactual.py` (thêm DMX/GEL/CRV) · `g5_rolling_rebuild.csv` ·
`daily_diff_rebuild.csv`. Không ghi gì vào `data/benchmark/`.
