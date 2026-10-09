# REPLAY lịch sử — cổng giá trong phiên + cutloss 4 chế độ (SHADOW)

Job `Taylor_20261009_094633` · 09/10/2026 · PAPER-ONLY. Không sửa watcher live, không đổi crontab,
không đổi ngưỡng. Mọi đề xuất bên dưới **chỉ là đề xuất**, chờ user + quant-skeptic.

## TL;DR

1. **Logic chạy đúng spec** — 0 crash qua ~25.400 lượt quét / 690 phiên. Đối chứng: replay 06–09/10
   tái tạo **3/3 kích hoạt PNJ** của shadow thật, cùng ngày (2/3 khớp đúng phút; 06/10 lệch 10'
   do bar 1' vs quote). Bản vá fsync của replay cho output **giống từng byte** trên 10/10 phiên
   kiểm tra.
2. **Cutloss THUA giữ nguyên, tính trung bình.** Kịch bản agent kết luận GÃY ⇒ bán hết, N = **347 ca /
   210 ngày / 256 episode** trên mã đang giữ (2023-09 → 2026-10). Tính theo giá bán ròng so với giá
   nếu giữ: T+0 **−1,93%** CI[−2,43; −1,47] · T+1 **−1,45%** CI[−2,10; −0,80] · T+5 −0,59% CI[−1,71; +0,64]
   · T+20 −0,83% CI[−2,78; +1,08]. Bán oan (sau đó giá hồi lên trên giá đã bán) **≈ 51–54%**.
   Lớp xấp xỉ theo ngày 2014–2026 (N lớn hơn) cho cùng chiều, cả IS lẫn OOS.
3. **Ngưỡng quá TRỄ chứ không quá nhạy.** Lúc kích hoạt, giá đã đi được ~90% quãng giảm của cả
   ngày (trung vị ret T0 −6,15%, đáy ngày −6,96%, đóng cửa −6,33%). Trên HOSE, ngưỡng −5% chỉ cách
   giá sàn −7% có 2 điểm %, nên ca nào cũng vào chế độ rút gọn và 233/347 ca leo lên chế độ 3-Khẩn.
   Trễ quy trình (điều tra 10–20' + chờ trả lời) **không** phải nguyên nhân: bán ngay tại T0 cho kết
   quả gần như y hệt (T+1 −1,51%).
4. **Có 3 lỗ hổng thiết kế** (không phải bug code): gộp "cả thị trường" chỉ đếm trong TỪNG lượt
   quét; CHẠM SÀN bỏ qua bộ lọc idio; ca kích hoạt sau 14:00 bị hoãn sang ATO phiên sau. Chi tiết ở §5.
5. **Khuyến nghị: CHƯA chuyển live. Tiếp tục SHADOW** và đưa user quyết các đề xuất ở §6. Riêng
   HOSE + book BAL/custom30V thì kết quả trung tính đến hơi dương, nhưng CI vẫn chứa 0.

## 1. Đã replay cái gì (đọc code thật, không viết lại công thức)

`replay.py` gọi **`intraday_price_watch.run_tick(now, deps)` mỗi phút 09:00–14:59**, đúng như cron.
Chỉ thay `deps.market` bằng `HistMarket` (giá lịch sử), notifier khô, `dispatch=None`. Toàn bộ phần
quyết định là code production: `trigger_check`, `market_wide_reason`, mở ca, hạn phán quyết và hạn
trả lời, `default_action` theo book, hoãn sau 14:00, 4 chế độ bán `step_execution`, carryover qua
đêm, excluded/`no_auto_sell`.

Ngưỡng **HÀNH ĐỘNG** đang hiệu lực, đọc từ engine:
- Điều kiện kích hoạt: `ret ≤ −5% ∧ idio ≤ −4%` (idio = ret − ret VNINDEX), **HOẶC** chạm giá sàn.
- Ngưỡng tương đối HOSE −3% / HNX −4,5% / UPCOM −7% (idio −3%) **chỉ ghi log**, không hành động
  (mặc định an toàn (d)). Đề bài dispatch gọi đó là "ngưỡng hiện hành" — không đúng.
- Gộp cả thị trường khi: ≥3 mã kích hoạt trong 1 lượt quét, hoặc ≥2 mã chạm sàn, hoặc thiếu VNINDEX.
- Không có phán quyết agent ⇒ **GIỮ** (`NON_AGENT_DEFAULT`).

Ba kịch bản phán quyết (user luôn im lặng ⇒ áp mặc định khi hết hạn):

| Kịch bản | Mô tả | Hành động |
|---|---|---|
| `NONE` | đúng như shadow đang chạy (`--no-dispatch`) | luôn GIỮ, nên không có lệnh nào |
| `BROKEN` | agent kết luận GÃY ngay trước hạn | BÁN hết |
| `UNCLEAR` | agent kết luận CHƯA RÕ | BÁN 50% (book V2.4) |

Kịch bản NHIỄU = GIỮ, cho kết quả giống hệt `NONE`.

## 2. Nguồn giá trong phiên — độ phủ THẬT

Tra `data_registry/research-caches` rồi đo trực tiếp (`coverage.py`).

| Nguồn | Khoảng | Phủ |
|---|---|---|
| `data/intraday_full.pkl` (bar 15', giá điều chỉnh) | 2023-09-11 → 2026-05-12 | 66,2% số (ngày, mã) đang giữ |
| vnstock/VCI bar 15' (`cache/vn15`, 178 mã thiếu/sau 05-12) | 2023-09-11 → 2026-10-09 | 26,0% |
| **Không có bar nào** | — | **7,8%** (watcher thấy QUOTE_ERROR ⇒ mã đó không được quét). 6 mã không có bar ngày nào: DXG, ELC, PAN, REE, TIG, VDS |
| DNSE bar 1' cổ phiếu | **chỉ 2026-07-09 → 2026-10-09** (64 phiên; DNSE chỉ giữ khoảng 3 tháng) | vị thế thật SpaceX/ZaloPay |
| DNSE bar 1' VNINDEX | 2023-09-11 → 2026-10-09 (768 phiên) | đủ |

**Không có** lịch sử sổ lệnh và bar 1 phút cổ phiếu trước tháng 07/2026. Vì vậy:
- 2023-09 → 2026-06 dùng **bar 15'**, quy về giá thô theo `Price_BQ/close bar cuối`. Mỗi bar chỉ
  "thấy được" sau khi đóng, nên không nhìn trước.
- Sổ mua là **giả định**: 3 bước giá dưới giá khớp, mỗi bước = 0,5 × KL khớp trung bình/phút của
  15' gần nhất. Tại giá sàn: chỉ có 1 mức nếu phút gần nhất có khớp.
- Sàn giao dịch lấy theo DNSE hiện tại (không point-in-time).
- Vùng trống 2026-06-20 → 07-08 không replay được.
- Lớp xấp xỉ theo ngày `daily_approx.py` (2014-02 → 2026-06) dùng Low ngày làm giá kích hoạt và
  Close ngày làm giá thoát. Lớp này chỉ để có N lớn, không phải replay driver.

Danh mục:
- 2023-09 → 2026-06: ledger R3 pin `4707bcbe` point-in-time (BAL/LAG + custom30V bung theo quý khi
  có park), quy về NAV 1 tỷ.
- 2026-07 → 10: vị thế thật SpaceX/ZaloPay (verified_snapshot ngày trước).

## 3. Mẫu sự kiện (N = số sự kiện ĐỘC LẬP)

- Kích hoạt trên mã **đang giữ**: 378 ca, **220 ngày, 265 episode** (cùng mã, các kích hoạt cách
  nhau ≤5 phiên tính là 1 episode). 365 ca theo giá, 13 ca chỉ do chạm sàn. HOSE 204 / HNX 90 /
  UPCOM 84. Chỉ 7 ca từ vị thế thật.
- Kích hoạt trên mã KHÔNG giữ (WATCH, chủ yếu PNJ excluded) không tính vào phần đánh giá cutloss.
- CI là bootstrap theo **cụm ngày**, vì các ca cùng ngày tương quan với nhau.
- Toàn bộ cửa sổ intraday (2023-09+) nằm trong giai đoạn OOS. Không tune tham số nào, nên DSR/PBO
  không áp dụng: đây là đánh giá mô tả chính sách đã duyệt.

### (a) Các phiên VNINDEX giảm mạnh (≤ −3% hoặc ≤ p2 = −2,64%): 16 phiên — `out/vni_big_down_days.csv`

- **Gộp cả thị trường đúng** khi có nhiều mã giảm cùng lúc: 03/04/2025, 08–09/04/2025, 20/10/2025,
  09/03/2026 (41 mã một lượt). Sau mỗi lần gộp không có hành động và không dispatch.
- **Lọt gộp**: 26/10/2023 (VNI −4,19%) **mở 11 ca riêng**, 0 lượt gộp, vì kích hoạt rải ra
  09:30–14:30, mỗi lượt quét ≤2 mã. Cũng lọt ở 25/09/2023 (5 ca riêng + 1 lượt gộp), 29/07/2025
  (3 ca riêng), 20/03/2026 (3 ca). Trên toàn mẫu có 30 ngày mở ≥3 ca riêng (124 ca).
- **Chạm sàn mở ca riêng dù idio không sâu**: VHM 22/07/2026 (ret −7,0%, idio chỉ −3,6%, VNI −3,3%),
  VHM 12/12/2025, NHA/VOS 05/08/2024. Ở kịch bản GÃY, VHM 22/07 bị bán 127,6k sáng hôm sau rồi
  hồi lên 138–140k: **−8 đến −9%** so với giữ, trên **cả 2 tài khoản**.

### (b) Mã giảm riêng khi VNINDEX bình thường — nhánh chưa từng chạy live

Nhóm VNI cả ngày > −0,5% có 183 ca: cutloss T+1 trung bình **−2,28%** (trung vị −1,92%), T+20 +0,55%.
Đây là nhánh mà trước giờ shadow chưa kiểm được. Kết quả cho thấy idio sâu trong phiên **chủ yếu
hồi lại** trong 1–5 phiên.

## 4. Kết quả cutloss vs GIỮ — `out/summary_exec.csv`, `out/exec_all.csv`

E = giá bán ròng / giá nếu giữ − 1, **dương = cutloss thắng**. Giá bán là giá khớp mô phỏng trừ
0,097% bán, 0,097% mua lại/tái phân bổ và trượt giá 0,5·σ20·√(KL/ADV20). Giá nếu giữ = giá thô ngày
D đã điều chỉnh corp-action tới D+k. Không dùng cột `profit_*`.

| Nhóm (BROKEN, bán hết) | N ca/ngày | T+1 | T+5 | T+20 | Bán oan T+5 |
|---|---|---|---|---|---|
| Tất cả | 347/210 | −1,45 [−2,10; −0,80] | −0,59 [−1,71; +0,64] | −0,83 [−2,78; +1,08] | 54% |
| Bán ngay tại T0 (lý tưởng, không trễ) | 347/210 | −1,51 | −0,60 | −0,82 | 54% |
| Book BAL | 87/60 | +0,83 | +1,57 [−0,54; +3,67] | +2,74 [−0,67; +5,88] | 44% |
| Book CUSTOM30V | 86/68 | −0,14 | +1,29 [−0,54; +3,19] | +2,72 [−0,08; +5,50] | 44% |
| Book LAG | 174/118 | **−3,25** [−4,19; −2,40] | **−2,60** [−3,97; −1,06] | **−4,37** [−6,69; −1,82] | 64% |
| HOSE | 200 | −0,48 | +0,43 | +0,26 | — |
| HNX | 75 | −2,01 | −2,48 | −2,05 | — |
| UPCOM | 72 | −3,61 | −1,44 | −2,57 | — |
| Hoãn sau 14:00 (bán ATO phiên sau) | 98/77 | −1,58 | **−2,15** [−3,86; −0,39] | −1,63 | 62% |
| Chỉ chạm sàn (idio > −4%) | 14/10 | +0,24 | −0,09 | −4,48 [−12,1; +4,2] | 43% |
| Vị thế thật (DNSE 1') | 9/5 | −0,83 | +0,73 | −4,42 | 44% |

UNCLEAR (bán 50%): tính trên mỗi cổ phiếu đã bán thì giống BROKEN. Tính trên toàn vị thế:
T+1 −0,63% [−0,93; −0,33], T+20 −1,11% [−1,99; −0,20].

Thực thi:
- Tỉ lệ khớp trung bình 92,5%. 38/347 ca còn EXECUTING đến cuối mẫu (kẹt sàn hoặc mã kém thanh
  khoản), và ca đang EXECUTING chặn mã đó kích hoạt lại.
- Trượt giá: trung vị 0,03%, nhưng p90 tới **2,27%** (mã nhỏ HNX/UPCOM trong book LAG).
- Giá bán trung bình −6,17% so tham chiếu, ≈ giá lúc T0 (−6,14%).

Lớp xấp xỉ ngày 2014–2026 (`out/daily_approx_summary.csv`), ca riêng theo ngưỡng hiện hành:
- T+1 −1,51% [−1,86; −1,16], N = 1.462 ca / 1.132 ngày.
- IS 2014–19: −1,59%. OOS 2020–26: −1,42%. Cùng chiều với replay intraday.
- Ca thuộc ngày gộp cả thị trường: T+20 −2,59%, nên **không hành động là đúng**.
- Ngưỡng tương đối (chỉ log): T+1 −0,15% [−0,30; 0,00]. Ít tệ hơn nhưng **cũng không có lợi**.

## 5. Logic có chạy đúng thiết kế không

**Code: đúng.**
- 0 CRASH qua ~25.400 lượt quét.
- Mọi trường hợp không có phán quyết agent đều áp GIỮ đúng (1.104 VERDICT / 1.103 DEFAULT_APPLIED;
  chênh 1 là ca còn chờ trả lời ở cuối shard).
- Leo thang chế độ, hoãn sau 14:00 và carryover qua đêm đều chạy.
- Excluded (PNJ) chỉ ở dạng WATCH, không mở lệnh.

**Lỗ hổng THIẾT KẾ** (đúng spec nhưng kết quả không như ý):
1. **Gộp cả thị trường chỉ đếm trong 1 lượt quét.** Khi cú sập trải ra nhiều lượt quét, mỗi mã mở
   ca riêng (26/10/2023: 11 ca, VNI −4,19%). Idio −4% so với VNINDEX không trung hoà beta, nên nhóm
   chứng khoán (SHS/VIX/VND 20/07/2026) và bất động sản rơi lọt qua.
2. **CHẠM SÀN kích hoạt bất kể idio.** Một mã chạm sàn duy nhất trong ngày VNI −3% vẫn mở ca riêng
   (VHM 22/07/2026, idio −3,6%).
3. **Ngưỡng trễ và nằm sát sàn trên HOSE.** Trung vị T0/đáy ngày = 0,90 (UPCOM 1,00). Kích hoạt
   gần đáy nên bán vào vùng hồi. Ca kích hoạt sau 14:00 bị hoãn sang ATO phiên sau, cho kết quả T+5
   tệ nhất (−2,15%).
4. Phụ: lượt quét 09:15 thấy giá ATO của cổ phiếu trước khi DNSE có bar 1' VNINDEX, nên rơi vào gộp
   "thiếu VNINDEX" (5 lượt). Đây là fail-safe, chỉ trễ 15', không phải lỗi.

## 6. Kết luận và đề xuất (CHỈ ĐỀ XUẤT — không đổi gì, chờ user)

- **Có nên chuyển live không: CHƯA.** Với chính sách hiện tại, bán tự động khi agent nói GÃY/CHƯA RÕ
  cho kỳ vọng âm. Kết luận này đúng cả trong replay intraday 2023–26 lẫn lớp ngày 2014–26 (IS và OOS
  cùng chiều).
- **Đề xuất A**: giữ mặc định GIỮ khi không có agent (đúng như hiện tại). Cân nhắc **chỉ cho phép tự
  bán ở book BAL/custom30V trên HOSE**, nơi kết quả trung tính đến dương. Book LAG và HNX/UPCOM thì
  bỏ tự bán, vì giảm sâu trong phiên ở đó chủ yếu hồi lại. Phân tách này **chưa** đủ ý nghĩa để wire
  (CI chứa 0, chia nhóm sau khi đã thấy kết quả): cần pre-register rồi kiểm lại.
- **Đề xuất B**: gộp cả thị trường theo **số mã kích hoạt luỹ kế trong ngày**, hoặc trong cửa sổ trượt
  60', thay vì trong 1 lượt quét. Thêm điều kiện "chạm sàn ∧ VNI ≤ −2% ⇒ gộp".
- **Đề xuất C**: không tự bán ca kích hoạt sau 14:00 qua ATO phiên sau. Để agent/user xét lại khi
  mở phiên.
- **Shadow thêm**: thêm cờ ghi `vni_day`/`ret_close` vào log EOD để các ca live tích luỹ thành bộ
  out-of-sample thật. Hiện mới có 9 ca vị thế thật.

## 7. Giới hạn

- Bar 15' trước 07/2026: kích hoạt có thể trễ tới 15' so với live (quét quote). Sổ lệnh là giả định,
  mức depth 0,5× chưa chạy độ nhạy.
- 7,8% (ngày, mã) không có bar nên bị bỏ qua.
- Sàn giao dịch không point-in-time.
- Danh mục ledger (book LAG nhiều mã nhỏ) chưa chắc giống danh mục đang giữ.
- "Giữ nguyên" tới T+20 bỏ qua việc chiến lược cũng sẽ tự thoát vị thế.
- KL bán được = KL giữ (bỏ qua ràng buộc T+2).
- Phán quyết agent là giả định: luôn GÃY hoặc luôn CHƯA RÕ. Agent thật có thể phân biệt tốt hơn.
  Đó là chỗ duy nhất cutloss còn cửa thắng, và replay này không đo được.

## Tái lập

```bash
PY=/home/trido/thanhdt/wc_venv/bin/python
$PY build_inputs.py && $PY fetch_vnstock.py          # cache/ (BQ + DNSE inquiry + vnstock)
./run_none.sh                                         # NONE: live + 4 shard ledger (--resume nếu bị cắt)
./run_verdicts.sh                                     # BROKEN/UNCLEAR trên ledger_case_days_*.txt
$PY replay.py --scenario BROKEN --days live_case_days.txt --out runs/live_BROKEN_d0.5   # (+ UNCLEAR)
$PY analyze.py runs/*_d0.5 && $PY final_tables.py && $PY daily_approx.py && $PY coverage.py
```
