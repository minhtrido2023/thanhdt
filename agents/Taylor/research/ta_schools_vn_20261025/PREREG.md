# PREREG — Trường phái phân tích kỹ thuật: có edge cơ học trên dữ liệu VN không?
Job `Taylor_20261025_115318` · 2026-10-25 · READ-ONLY / PAPER-ONLY. File này KHÔNG được sửa sau khi có kết quả.

## 0. Dữ liệu (đã tra `kb/data_registry/`)
- Giá: `data/bq_cache/ticker/*.parquet` (mirror `tav2_bq.ticker`, CANONICAL cho lịch sử). Dùng `Open/High/Low/Close`
  (đã điều chỉnh cổ tức+chia tách, cùng hệ số — đã kiểm AAA 2014-08-26: O/H/L/C nhân cùng ratio), `Volume` (THÔ,
  không điều chỉnh), `Price` (thô, chỉ để tính ADV và phát hiện corp-action). KHÔNG dùng cột `profit_*`, `Open_1D`.
- Universe: `tav2_mike.universe_pit` (mirror cache `data/bq_cache/universe_pit`, ruleset v1) `in_universe=True` tại ngày tín hiệu. KHÔNG `ticker_prune`.
- Benchmark: dòng `ticker='VNINDEX'` cùng bảng (giá chỉ số, không TR).
- Khối ngoại / tự doanh: KHÔNG có cột trong `tav2_bq.ticker` (feeds chỉ CANDIDATE, `feeds/foreign_flow_*`) ⇒ **không đo được**, ghi rõ trong REPORT.
- Kỳ: tín hiệu 2014-01-02 → hết dữ liệu (2026-10-23); lợi suất tương lai tính được đến hết dữ liệu (NaN nếu thiếu cửa sổ).
- IS = năm tín hiệu 2014–2019; OOS = 2020+. (Tách trước/sau FTSE 21/09/2026: bỏ, mẫu không đủ.)

## 1. Quy ước sự kiện và đo lường
- Ký hiệu phiên tín hiệu t (đóng cửa). Vào lệnh tại **Open phiên t+1**. Thoát tại **Close phiên t+h**, h ∈ {5,10,20,40} phiên.
  `R_h = Close[t+h] / Open[t+1] − 1` (giá điều chỉnh). Chỉ LONG.
- Hợp lệ khi: (i) phiên t+1 cách t ≤ 5 ngày lịch; (ii) phiên t+h cách t ≤ 1,7·h+10 ngày lịch (chống đình chỉ dài);
  (iii) trong cửa sổ (t+1..t+h) không có ngày |Close/Close_prev − 1| > 50% (lỗi dữ liệu) ⇒ R_h = NaN;
  (iv) **ADV20 ≥ 1 tỷ VND**, ADV20 = trung bình 20 phiên (t−19..t) của `Price×Volume` thô;
  (v) `in_universe` tại t.
- **Sự kiện corp-action**: ngày có |Δ(Close/Price)/(Close/Price)| > 3% so với phiên trước. Sự kiện tín hiệu bị loại nếu có
  ngày như vậy trong (t−25..t) (Volume thô bị nhiễu quanh chia tách). Kiểm ca chia tách thật (AAA 2014-08-26) trong REPORT.
- **Cooldown**: với mỗi (mã, tín hiệu) giữ sự kiện đầu, bỏ các sự kiện trong 10 phiên kế tiếp (giảm chồng lấn).
- Chi phí khứ hồi: phí 0,097%/chiều ×2 + trượt giá 0,1%/chiều ×2 = **0,394%**. Trừ MỘT lần vào lợi suất ròng.
- Excess (a) vs VNINDEX: `R_h − R_VNI_h − 0,00394`, R_VNI_h = `VNI_Close[t+h]/VNI_Open[t+1] − 1` (nếu thiếu Open → Close[t]).
- **F1 (đối chứng ngẫu nhiên khớp NGÀY + thanh khoản)**: control(i,t,h) = trung bình `R_h` của các mã hợp lệ (iv,v + R_h không NaN)
  CÙNG ngày t, CÙNG tertile ADV20 (chia trong tập hợp lệ của ngày đó), TRỪ chính mã i (đây là kỳ vọng chính xác của việc
  bốc ngẫu nhiên vô hạn lần). `exF1 = R_h − control` (chi phí triệt tiêu vì cùng khứ hồi). Tertile cần ≥ 10 mã, không thì NaN.
- **F2c (đối chứng xu hướng)**: như F1 nhưng chỉ lấy các mã đang ở trạng thái F2 (xem dưới) cùng ngày/tertile (≥ 5 mã, trừ chính i).
  `exF2 = R_h − control_F2`. Đây là phép thử "tín hiệu có thêm gì so với chỉ đang ở xu hướng tăng không".
- **F2** = (Close > MA50) ∧ (MA50[t] > MA50[t−10]); sự kiện F2 = ngày chuyển từ sai→đúng. **F3** = Close[t] > max Close(t−252..t−1) ∧ Vol[t] > 1,5·V20.
  F2, F3 được đo như hai "tín hiệu" tham chiếu (cùng pipeline).

## 2. Định nghĩa cơ học (tham số cố định, KHÔNG tune)
Ký hiệu: o,h,l,c = OHLC điều chỉnh; vol = Volume thô; V20 = mean(vol[t−20..t−1]); vr = vol[t]/V20; S20 = mean(h−l)[t−20..t−1];
rng = h−l; body = |c−o|; pos = (c−l)/rng; MA20/MA50 = trung bình c; cần rng>0.

**A. Ichimoku (9/26/52)**: tenkan=(max h9+min l9)/2, kijun=(max h26+min l26)/2; SSA_t=((tenkan+kijun)/2)[t−26], SSB_t=((max h52+min l52)/2)[t−26]
(mây tại t dùng giá đến t−26 ⇒ không nhìn trước); top=max(SSA,SSB). Chikou xác nhận: c[t] > c[t−26].
 - A1: c[t−1] ≤ top[t−1] ∧ c[t] > top[t].
 - A2: tenkan[t−1] ≤ kijun[t−1] ∧ tenkan[t] > kijun[t] ∧ c[t] > top[t].
 - A3: A1 ∧ tenkan[t] > kijun[t] ∧ c[t] > c[t−26].

**B. Nến** (rngok: rng ≥ 0,5·S20). Mỗi mẫu hình × bối cảnh {unc: vô điều kiện; dt: đóng cửa[t−1] < MA20[t−1] ∧ vị trí c[t−1] trong
khoảng min l/max h 60 phiên ≤ 20% thấp} × volume {any; vol: vr>1,5} = 12 cấu hình.
 - Engulfing: c[t−1]<o[t−1] ∧ c[t]>o[t] ∧ o[t] ≤ c[t−1] ∧ c[t] ≥ o[t−1] ∧ body[t]>body[t−1] ∧ rngok.
 - Hammer: min(o,c)−l ≥ 2·body ∧ h−max(o,c) ≤ 0,1·rng ∧ rngok.
 - Morning star: c[t−2]<o[t−2] ∧ body[t−2] ≥ 0,6·rng[t−2]; body[t−1] ≤ 0,3·body[t−2] ∧ max(o,c)[t−1] < c[t−2]; c[t]>o[t] ∧ c[t] > (o[t−2]+c[t−2])/2 ∧ rngok.

**C. VSA** (downrun = c[t−1]/c[t−6]−1 ≤ −5%):
 - C1 Stopping volume: vr>2 ∧ rng ≥ 1,2·S20 ∧ pos ≥ 0,5 ∧ downrun.
 - C2a No-supply: vr<0,7 ∧ c<o ∧ rng ≤ 0,8·S20. C2b = C2a ∧ c>MA50.
 - C3 Upthrust (đo như tín hiệu NÉ, kỳ vọng excess ÂM): h>max h(t−20..t−1) ∧ pos ≤ 0,3 ∧ vr>1,5 ∧ rng ≥ 1,0·S20.
 - C4 Test: vr<0,7 ∧ rng ≤ 0,8·S20 ∧ l ≤ min l(t−10..t−1) ∧ pos ≥ 0,5 ∧ có C1 trong (t−20..t−1) cùng mã.

**D. Darvas**: top = max h(t−20..t−1); ổn định ≥3 phiên: phiên đạt top nằm ≤ t−4 (top không đổi ≥3 phiên). Breakout: c[t] > top ∧ c[t−1] ≤ top(t−1) (mới phá).
 - D1 = breakout ∧ vr>1,5. D2 = breakout (không volume).

**E. Dòng tiền**:
 - E1 CMF(20) chuẩn (Σ MFV/Σ vol, MFV=((c−l)−(h−c))/rng·vol): CMF[t−1] ≤ 0 ∧ CMF[t] > 0.
 - E2 OBV (cộng dồn sign(Δc)·vol): OBV[t] > max OBV(t−60..t−1) ∧ c[t] ≤ max c(t−60..t−1).
 - E3 MFI(14) chuẩn (typical price (h+l+c)/3): MFI[t−1] < 20 ∧ MFI[t] ≥ 20.
 - E4 Khối ngoại/tự doanh: KHÔNG ĐO ĐƯỢC (không có cột).

Tổng: 3 (A) + 12 (B) + 5 (C1,C2a,C2b,C3,C4) + 2 (D) + 3 (E) + 2 tham chiếu (F2,F3) = **27 cấu hình × 4 horizon = 108 trials**
(mỗi trial có 1 p-value vs F1 và 1 vs F2c).

## 3. Thống kê
- Đơn vị độc lập: sự kiện cùng ngày/cùng tháng tương quan mạnh ⇒ **bootstrap theo cụm THÁNG LỊCH** (5000 lần, seed cố định):
  resample tháng có hoàn lại, tính lại trung bình sự kiện; p hai phía từ phân phối bootstrap (min(P(≤0),P(≥0))·2).
  Báo N sự kiện, N ngày tín hiệu khác nhau, N cụm (mã,tháng), N tháng.
- Một cấu hình-horizon "đủ mẫu" nếu N ≥ 100 ∧ N tháng ≥ 24; không thì "KHÔNG ĐỦ MẪU" (không tính vào kết luận có/không).
- BH-FDR (q=0,10) trên toàn họ trial đủ mẫu, 2 họ riêng: p(exF1) và p(exF2). Số trial khai theo mục 2.
- Báo: tỉ lệ hit (R_h−0,00394>0), trung vị R_h ròng, trung vị exF1, trung bình exF1 (IS / OOS / toàn kỳ), excess vs VNINDEX trung vị,
  leave-one-year-out cho exF1@20 (bỏ lần lượt từng năm: trung bình tối thiểu; và tỉ trọng 2 năm lớn nhất trong Σ).

## 4. Tiêu chí đạt (cố định)
Cấu hình **"CÓ BẰNG CHỨNG (so F1)"** ⇔ tại h=20, đồng thời:
 (a) đủ mẫu; (b) trung bình exF1 cùng dấu kỳ vọng ở cả IS và OOS (đổi dấu = loại; C3 kỳ vọng ÂM, còn lại DƯƠNG);
 (c) BH q < 0,10 trong họ exF1 (p từ toàn kỳ); (d) leave-one-year-out: không năm nào bỏ ra làm đổi dấu trung bình, và 2 năm lớn nhất < 60% tổng;
 (e) trung bình excess vs VNINDEX ròng chi phí cùng dấu kỳ vọng.
**"VƯỢT XU HƯỚNG (so F2)"** ⇔ đạt trên + trung bình exF2@20 cùng dấu kỳ vọng ở IS và OOS + BH q<0,10 trong họ exF2.
Trường phái không qua (a)–(e) = "không có giá trị gia tăng". Đa số không edge là kết quả hợp lệ.

## 5. Self-check bắt buộc
Tính lại bằng vòng lặp thuần Python (không vectorized) cho 1 mã/1 tín hiệu: danh sách sự kiện, R_h, control F1 cho 1 sự kiện, khớp engine tới 1e-9.
Kiểm corp-action: mã chia tách thật, so R_h trên giá điều chỉnh vs giá thô (thô phải cho dư địa lệch giả).
