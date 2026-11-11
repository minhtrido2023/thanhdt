# Độ trễ rating 8L so với ngày công bố BCTC — nhóm LAG, mùa Q3/2026

Job `Taylor_20261111_011218` · 11/11/2026 · chỉ đo, không sửa code/cron/rules/plan.

## Kết luận

1. **Lỗ hổng M1 (cổng chấm bằng rating quý trước) đã đóng trong mùa Q3: 0/88 sự kiện** (Q2: 28/117).
   Tuy vậy hai phép đo không cùng phương pháp: Q2 là mô phỏng, Q3 là cờ live cộng time-travel BQ (xem §2).
   Thứ đóng lỗ hổng là **thứ tự giờ chạy** (re-rate 17:30 nay chạy TRƯỚC golive 19:00) cộng với việc chạy
   **mỗi ngày từ 14/10**, chứ không riêng chuyện nới đầu/đuôi cửa sổ.
2. **0 lệnh LAG đặt sai hay bỏ lỡ vì rating cũ.** Có 8 mã LAG được mua trong mùa (HT1, SCL, VPB, MCH, BSR, CSV,
   GAS, MSB), và rating cũ lẫn rating mới của cả 8 đều nằm cùng phía cổng.
3. **Có một lỗ hổng KHÁC lộ ra: rating của chính dòng Q3 bị trôi sau lần chấm đầu.** Trong 7 ngày đo được,
   6/88 sự kiện bị đổi rating, 4 trong số đó cắt qua ngưỡng 3/4 (FIC, HTN, SGD, VGS).
   - Ca thật VGS: ngày entry 06/11 bị cổng loại với 8L=4, sang 09/11 rating trôi về 3 thì quay lại danh sách ở
     ngày 3 của cửa sổ.
   - Hậu quả là 0 đồng, vì cổng DD (`LAG_DD_FLAG_NO_ACK`) vẫn đang giữ cả VGS lẫn HTN.
4. **Phần trễ thật còn lại nằm ở khâu ingest BQ, không ở khâu re-rate.**
   - VTE: công bố 21/10 nhưng tới 04/11 mới vào BQ (14 ngày lịch / 10 phiên).
   - TED: công bố 02/11, vào BQ 09/11 (7 ngày / 5 phiên).
   - Cả hai đều có rating ngay trong ngày ingest. Tuy vậy lúc vào BQ thì T+5 của VTE đã qua.

## 1. Mẫu và nguồn

- **Sự kiện:** `lag_live_schedule.live_lag_candidates` (đúng hàm golive dùng) trên pkl hiện tại, lấy
  `qualify=True` với Release_Date từ 10/10 đến 10/11. Được **88 sự kiện / 15 ngày công bố**.
  - Riêng 02/11 chiếm 30 sự kiện.
  - **N độc lập ≈ 15 cohort ngày công bố, không phải 88**, vì độ trễ do lịch chạy cron quyết định cho cả cohort.
  - 88 là số TRƯỚC sàn thanh khoản ADV3T ≥ 2 tỷ. Cổng 8L và cờ chỉ chấm mã đã qua sàn này.
- **Rating:** `tav2_bq.fa_ratings_8l`, qua hai đường:
  - Đọc hiện tại và `FOR SYSTEM_TIME AS OF` tại 08:30 / 17:25 / 18:55 ICT mỗi ngày 04/11–10/11. Time-travel
    BQ chỉ giữ 7 ngày, nên các ngày trước 04/11 không chụp lại được.
  - `ticker_financial` time-travel cùng các mốc, để lấy ngày ingest.
- **Gate thực tế:** dòng `[lag-rating]` và cờ `lag_rating_stale` trong `mike/logs/bq_freshness.log(.1.gz)`, ở 19 lượt
  golive từ 15/10 đến 10/11. Plan thật ở `data/trade_plans/plan_{SpaceX,ZaloPay}_*.json`.
- **File:**
  - `events_q3.csv` (md5 94874594…): bảng từng sự kiện.
  - `drift_q3.csv` (71f05c6c…).
  - `cohort_increments.csv` (bcb9004b…).
  - Script tái lập: `build_events.py`, `drift.py`, `cohort.sh`.

## 2. Độ trễ công bố → rating mới có hiệu lực

| Nhóm | n | Trễ (lịch / phiên) | Cách đo |
|---|---|---|---|
| Công bố 04–06/11 (SGD, TPC, MNB, DM7, NDT, PXS) | 6 | **0 / 0**: vào BQ trước 17:25, rating có lúc 18:55 cùng ngày | time-travel, chính xác |
| Công bố 03/11 (CLC, VC1) | 2 | ≤1 / ≤1 (đã có rating lúc 08:30 ngày 04/11) | time-travel, cận trên |
| Ingest muộn: TED, VTE | 2 | TED 7 / 5 · VTE 14 / 10. Tính từ lúc ingest thì cả hai đều 0 | time-travel |
| Công bố 16/10–02/11 (78 sự kiện) | 78 | **ước lượng** cohort: 19/10–30/10 phần lớn là D+1 (1 lịch / 1 phiên; cohort thứ Sáu sang thứ Hai là 3 lịch / 1 phiên); từ 02/11 thì cùng ngày | `cohort_increments.csv`, xem ghi chú dưới bảng |

Cách đọc `cohort_increments.csv`: so số dòng thêm ở mỗi lần re-rate với số dòng có `time` = ngày đó.
- Ví dụ D+1: 20/10 thêm +62 dòng, trong khi số dòng `time` 19/10 là 47.
- Ví dụ cùng ngày: 02/11 thêm +405, khớp 403 dòng `time` 02/11.
- Đây là bằng chứng cấp cohort, không gán được cho từng mã.

**Rating dùng tại cổng là quý nào:**
- Cả 19/19 lượt golive từ 15/10 đến 10/11 đều có `lag_rating_stale = 0` và không lỗi. Status 11/10 ghi
  `n_lag_rating_stale=0`, `lag_rating_stale_error=null`. Nghĩa là mọi sự kiện golive nhìn thấy đều được chấm
  bằng dòng rating Q3, tức `time ≥ Release_Date`.
- Kiểm độc lập bằng time-travel 18:55 các ngày 04–10/11: 0 sự kiện có trong `ticker_financial` mà chưa có rating Q3.

Vì sao khớp: golive làm mới pkl từ BQ sống lúc 19:00, sau re-rate 17:30. Một sự kiện chỉ lọt vào plan khi BQ
đã có nó, và lúc đó re-rate gần như chắc đã chạy rồi. Khe hở duy nhất là ingest rơi vào khoảng 17:30–19:00
(xem §4). Khe này quan sát được 0 lần.

**So với Q2:** Q2 bị 28/117. Lý do: golive 19:00 chạy trước re-rate 20:00, và re-rate dừng hằng ngày sau
31/07. Q3 bị 0/88.
- Hai con số đo khác cách: Q2 mô phỏng từ log refresh với giả định ingest = release+1 16:36, Q3 đo bằng cờ
  live và time-travel.
- Nếu áp đúng mô phỏng kiểu Q2 lên lịch chạy Q3, kết quả vẫn là 0, vì re-rate chạy mỗi ngày trước golive.

## 3. Ca có thể bị chấm sai chiều và hậu quả

**Nếu cổng đã dùng rating Q2** thì 14/88 sự kiện bị đổi phía:
- Cũ ≤3 → mới ≥4 (sẽ cho qua sai): DGW, DQC, FIC, L10, MDF, PTM, SGD.
- Cũ ≥4 → mới ≤3 (sẽ loại oan): HTN, MSR, NSH, PMP, UNI, VC7, VTE.

**Thực tế 0 ca xảy ra**, vì cổng luôn chấm bằng rating Q3 (§2). Hai mã đáng kể trong nhóm:
- MSR (4→3): vào UPCOMING, đến ngày entry 29/10 thì SKIP vì user DROP qua DD.
- VTE: ingest quá muộn, không bao giờ vào plan.

**Trôi rating của dòng Q3** (lỗ hổng mới; chỉ đo được 7 ngày, nên số thật có thể cao hơn):

| Mã | Công bố | Entry | Rating dòng Q3 theo thời gian | Hậu quả |
|---|---|---|---|---|
| VGS | 30/10 | 06/11 | 4 (02–08/11) → 3 (từ 09/11) | Bị cổng loại ở ngày entry 1–2. Quay lại ở ngày 3, rồi SKIP do DD chưa ack. 0 lệnh |
| HTN | 02/11 | 09/11 | 4 (log 02–03/11) → 3 (từ chiều 04/11) | Bị loại lúc UPCOMING. Đến entry thì qua cổng, rồi SKIP do DD chưa ack. 0 lệnh |
| FIC | 02/11 | 09/11 | 3 (sáng 04/11) → 4 (chiều 04/11) | Bị loại trước entry (FIC không có trong list `[lag-rating]`, có thể đã rớt sàn thanh khoản trước đó). 0 lệnh |
| SGD | 04/11 | 11/11 | 3 (04/11) → 4 (từ 05/11) | Bị loại trước entry, tương tự FIC. 0 lệnh |
| C69, CTW | 02/11 | — | 4→5 · 3→2 | Không đổi phía cổng |

Log còn cho thấy trôi trước 04/11 (TRC 4→5→4 quanh 23–26/10, HSG 4→5 ngày 02/11), nhưng không đo được theo từng mã.
Cơ chế (suy luận từ code, chưa kiểm riêng): rating xếp theo percentile trong quý/route, nên điểm của một mã đổi
khi cohort công bố đầy dần.

## 4. Cửa sổ nới có đủ không — lỗ hổng còn lại

- **M1 gốc (re-rate chưa chạy sau BCTC): ĐÓNG.**
- **(a) Khe 17:30–19:00:** nếu ingest rơi vào khe này thì golive vẫn thấy sự kiện kèm rating cũ. Cờ sẽ kêu,
  nhưng chỉ là cảnh báo. Quan sát được 0 lần trong 19 lượt.
- **(b) Ingest muộn sau khi cửa sổ đóng (10/11):** ngoài cửa sổ chỉ còn re-rate thứ Bảy, nên rating có thể trễ tới 6 ngày.
  - Hiện còn 142/1206 mã có Q2 mà chưa có Q3.
  - Trong 123 dòng Q3 vào BQ sau 04/11, 14 dòng có Release_Date tháng 10, tức ingest muộn ≥5 ngày. VTE là mã duy nhất trong số đó qualify LAG.
  - Rủi ro thực tế nhỏ: sự kiện ingest muộn thường đã quá T+5.
- **(c) Trôi rating dòng Q3:** đây không phải lỗi trễ, nên cờ `lag_rating_stale` không bắt được, vì `time` của dòng vẫn ≥ release.
  - Mức hiện tại là 4 lần cắt ngưỡng / 88 sự kiện / 7 ngày, 0 hậu quả tiền.
  - Hệ quả phụ cho backtest: backtest dùng rating đã trôi xong, còn live dùng rating tạm thời. Registry đã ghi
    "republish làm backtest as-of lệch nhẹ", nhưng chưa có số đo.

**Đề xuất tối thiểu (CHỈ đề xuất, chưa sửa gì):**
1. **P1 (rẻ, không đổi quyết định):** ghi `rating` và `rating_time` mà cổng dùng cho từng ứng viên LAG vào
   `golive_v23_status.json` (hoặc một CSV append theo ngày).
   - Lý do: hiện chỉ đo được trôi rating nhờ time-travel 7 ngày, và mùa sau sẽ mất bằng chứng.
2. **P2 (cần user, đổi cron):** sau khi cửa sổ đóng, chạy re-rate 17:30 có điều kiện "ticker_financial có dòng
   mới kể từ lần re-rate trước", thay vì chỉ chạy thứ Bảy. Cách này vá (b).
3. **Không đề xuất** siết cờ `lag_rating_stale` thành fail-closed (mục C của 13/10): cờ đã 0/19 lượt, nên siết không mua thêm gì.
   Với (c), chỉ nên bàn sau khi P1 đã cho số đo một mùa.

**Caveat:**
- N nhỏ: khoảng 15 cohort; time-travel chỉ có 7/32 ngày.
- Rating trôi trước 04/11 chưa đo theo từng mã.
- `qualify` tính trên pkl hôm nay. Prior ≥1 quý nên ổn định, nhưng chưa đối chiếu từng ngày.
- Một số dòng Q3 có Release_Date tháng 8 (ATA, DIC, POM…) hoặc NULL: lỗi dữ liệu vendor, nằm ngoài phạm vi, không có mã nào qualify LAG.
