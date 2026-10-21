# PREREG F3 — TRẦN THAM GIA NHÂN QUẢ THEO PHIÊN bằng DỰ BÁO giá trị khớp — job Taylor_20261021_012028, EXPLORATORY
Không sửa pin/registry/pin_ledger/engine thật; chỉ bản sao `eng/`. Không đề xuất đổi luật. md5 + commit TRƯỚC khi tính.
Nguồn: cache pin `.../ticker` (registry CANONICAL lịch sử; bẫy Price ngày GDKHQ — dv lệch 1 phiên, chấp nhận như V1E).

## 1. Dự báo (khai báo trước, KHÔNG chọn theo độ chính xác)
`dv(tk,d) = Volume × COALESCE(Price, Close)` (Volume=0 ⇒ 0). **Dự báo chính** `F(tk,t)` = trung vị `dv` trên 20 dòng cache liền TRƯỚC t,
**TÍNH ngày Volume=0 là 0** (khác V1E loại chúng), `min_periods=1`, không có dòng nào trước t ⇒ 0. Chỉ dữ liệu ≤ t−1.
**Hệ số ngày sự kiện LAG (PIT)** `m_Y`: với lệnh MUA LAG của PIN p30_pin0 (`raw/pin_4707bcbe.csv`, TX buy book LAG ngoài ETF_PARK) ở ngày
Volume>0 và F>0, tỷ số r = dv_thực / F; `m_Y` = trung vị r trên mọi lệnh có năm < Y (mở rộng dần; Y=2014 không có lịch sử ⇒ m=1).
Không cắt ngưỡng. Ngày thực thi LAG = phiên sau tín hiệu ⇒ biết trước phiên. Áp `m_Y` cho mọi phiên khớp lệnh MUA LAG (cửa sổ ≤5 phiên).
PIT: F hoàn toàn PIT; m_Y PIT (chỉ năm trước) nhưng ước từ CHÍNH tập lệnh pin (cùng hệ, không phải mẫu ngoài) — nêu rõ.
## 2. Kiểm độ chính xác dự báo (mô tả, sau khi khai)
Trên lệnh mua LAG pin p30_pin0 và lệnh mua BAL pin (ngày Volume>0): median log(dv_thực/dự báo), tỷ lệ dv_thực < dự báo ("vượt": trần
20%×dự báo > 20%×thực), tỷ lệ dự báo=0, cho: ADV3M pin (`Volume_3M_P50×Price`), V1E20 (trung vị loại 0), F, F×m_Y. Kèm theo năm.
## 3. Biến thể
`ZVF_MODE=block` (Volume=0 hôm nay ⇒ không khớp, ràng buộc vật lý user xác nhận) + trần MUA/ngày = **20% × F × m_Y THAY 20%×ADV3M**:
- **F3L (CHÍNH)**: chỉ simulate() `v23audit_LAG*`; BAL giữ trần pin (20%×ADV3M) và chỉ chịu ZVF block.
- **F3B**: LAG như F3L + BAL trần 20% × F (không m) — tách được ảnh hưởng BAL.
Bán: như V1A (chỉ hoãn ngày Volume=0, không trần, không F1). Knob: `F3_MODE=lag|both`, `F3_MULT="2014:1.0,2015:x,..."`.
## 4. Đo
4 chân × {F3L, F3B}: ΔCAGR/ΔSharpe/ΔMaxDD/ΔIS/ΔOOS so pin, nhãn sàn 0,46pp, book ref BAL/LAG, lô LAG, **% giá trị mua LAG > 20% giá trị
khớp THỰC cùng ngày** (đo hậu kỳ, v1de_describe), % ngày Volume=0 (phải 0). Trả lời "pin LAG thực thi được ở 50 tỷ?" theo quy tắc khai
trước: KHẢ THI nếu (i) % vượt 20% thực ≤ 10% giá trị mua LAG VÀ (ii) ΔCAGR(F3L−pin) ≥ −0,46pp ở ≥3/4 chân; KHÔNG khả thi nếu (ii) sai
ở ≥3/4 chân; còn lại = KHÔNG KẾT LUẬN ĐƯỢC.
## 5. Control + self-check: như PREREG_V1D §4.
## 6. Giới hạn
Dự báo trung vị 20 phiên không biết tin bất thường trong ngày; m_Y từ chính tập pin; trần 20% là quy ước không phải đo tác động giá;
không slippage. Phiên khớp lệnh mua LAG được nhận dạng bằng tên simulate (cả lượt base lẫn chính).
