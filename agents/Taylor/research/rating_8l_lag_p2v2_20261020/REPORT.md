# Rating 8L — Phần 2 vòng 2: rating có tín hiệu riêng, tách khỏi PEAD không?

Job `Taylor_20261020_045201` · 2026-10-20 · read-only. Không đề xuất đổi gate/luật.

**PREREG**: `PREREG.md`, md5 `04939469af9a6850e872ed25d098af5c`, commit `a467963b9` (2026-10-20 11:54:00 +0700), commit
TRƯỚC lần chạy đầu tiên của `event_study_v2.py`. Thời điểm "~12:05" ghi trong file là ước lượng viết tay; giờ thật = giờ commit.

## Kết luận
| Nhóm | Verdict (đúng tiêu chí PREREG §6-7) | Lý do |
|---|---|---|
| **G1** ≥4→≤3 | **không có** (đạt (a), (c), (d), nhưng **trượt (b)**) | nửa 2014-19 cùng dấu nhưng p_boot 0,18 ([2,20]) / 0,19 ([2,40]) ≥ 0,10 |
| **G2** ≤3→≥4 | **không có** | (a) trượt: q 0,39 / 0,69; bản không khớp SUE cũng trượt (a) ⇒ không áp nhãn "không tách được khỏi PEAD" |
| Ngân hàng | không đủ N (thăm dò; G1 9, G2 4 sự kiện có ô khớp) | |

Đọc mô tả (KHÔNG phải verdict): G1 − G0* khớp SUE = **+1,06%** [2,20] / **+1,55%** [2,40]. Khớp thêm SUE làm hiệu ứng
nhỏ đi khoảng 17-18% so với bản chỉ khớp quý × mom × bank (+1,27% / +1,89%) ⇒ một phần drift của G1 là PEAD, phần còn
lại vẫn dương nhưng chỉ có ý nghĩa ở nửa 2020+.

## 1. Mẫu (`out_v2_stdout.txt`)
- G0/G1/G2 có eff trong [2014-07-01, 2026-07-31]: 40.720 / 3.455 / 3.374. Loại (a)-(c): 6.431 (5/7 ca trong danh sách nhìn
  trộm có trong cửa sổ eff). Loại theo cửa sổ: không có giá 17.790 · không in_universe tại phiên 0 9.916 · <80% phiên có
  giao dịch 5 · |r|>40% 11 ⇒ **13.396** (G0 11.333 · G1 1.029 · G2 1.034).
- SUE tính được 12.484/13.396 (thiếu: G0 772, G1 77, G2 63 — <6/8 quý lịch sử). Ô khớp có G0: G1 **938** (14 không có ô),
  G2 **957** (14). 48 quý lịch; 374/370 mã. G0 mỗi ô: trung vị 6, p10 1 (1.620 ô).
- SUE trung vị: G0 +0,10 · G1 +0,53 · G2 −0,26 ⇒ G1/G2 đúng là lệch về phía bất ngờ lợi nhuận (lý do phải khớp SUE).
- Kiểm giá điều chỉnh: VHM 2026-08-07 r(Price) −52,3% / r(Close) −5,3% ✓.
- Kiểm PIT SUE: 0 dòng lịch sử có Release_Date > eff (assert trong code).
- Chồng lấn cùng mã: khoảng cách nhỏ nhất giữa 2 sự kiện cùng mã = **45 phiên** ⇒ cửa sổ [2,40] KHÔNG chồng nhau; bản "loại
  sự kiện thứ 2 trong 40 phiên" bỏ 0 sự kiện, cho số y hệt bản chính.

## 2. Họ chính F1 (4 phép, BH-FDR q=0,05 riêng 4 phép) — δ = CAR_G − mean CAR_G0 cùng ô (quý × mom5 × SUE5 × bank), B3 loại chính mã

| Nhóm | Cửa sổ | N | δ | CI95 bootstrap quý | p_boot | **q_BH** | N_eff | p cluster-mã (K mã) |
|---|---|---|---|---|---|---|---|---|
| G1 | [2,20] | 938 | **+1,06%** | [+0,35; +1,78] | 0,008 | **0,032** | 881 | 0,007 (374) |
| G1 | [2,40] | 938 | **+1,55%** | [+0,22; +2,80] | 0,022 | **0,044** | 692 | 0,006 (374) |
| G2 | [2,20] | 957 | −0,36% | [−1,07; +0,33] | 0,294 | 0,392 | 989 | 0,37 (370) |
| G2 | [2,40] | 957 | −0,15% | [−1,06; +0,73] | 0,685 | 0,685 | 1.315 | 0,80 (370) |

## 3. Tiêu chí tái lập (`out_v2_criteria.csv`)

| Nhóm·cửa sổ | (a) q<0,05 | (b) IS 2014-19 | (b) OOS 2020+ | (c) bỏ 3 quý lớn nhất | (d) sau phí 0,2% / ADV≥5B (N=403/395) |
|---|---|---|---|---|---|
| G1 [2,20] | ✅ 0,032 | +0,75% p=0,18 N=323 ❌ | +1,22% p=0,006 N=615 | +0,59% (56%; 2021Q1, 2026Q1, 2020Q1) ✅ | +0,86% / ADV +1,80% → +1,60% ✅ |
| G1 [2,40] | ✅ 0,044 | +1,67% p=0,19 ❌ | +1,49% p=0,050 | +0,99% (64%; 2021Q1, 2024Q1, 2015Q1) ✅ | +1,35% / ADV +2,08% → +1,88% ✅ |
| G2 [2,20] | ❌ 0,39 | −0,74% p=0,035 | −0,16% p=0,72 ❌ | −0,09% (25%) ❌ | +0,16% / ADV −0,82% ✅ |
| G2 [2,40] | ❌ 0,69 | −0,56% p=0,36 ❌ | +0,06% p=0,97 ❌ | +0,22% (đổi dấu) ❌ | −0,05% ❌ |

G1 [2,40]: điểm ước lượng IS (+1,67%) ≈ OOS (+1,49%) — trượt (b) vì phương sai nửa IS (323 sự kiện, 22 quý), không vì đổi dấu.
Mức độ không phụ thuộc tên kém thanh khoản: tập ADV≥5B cho δ LỚN hơn toàn mẫu.

## 4. Thăm dò (không đổi verdict)
- **Đối chứng không khớp SUE** (cùng 12.484 sự kiện, ô quý × mom × bank, BH riêng 4 phép): G1 +1,27% q=0,004 / +1,89% q=0,006,
  đạt cả (a)-(d) (IS p<0,10). G2 −0,59% q=0,10 / −0,44% q=0,27. ⇒ Thêm SUE vào khớp chính là thứ đẩy nửa IS của G1 ra khỏi
  ngưỡng p<0,10: một phần drift G1 2014-19 là PEAD.
- Mọi sự kiện (kể cả thiếu SUE), ô quý × mom × bank: G1 +1,30% q=0,002 / +1,45% q=0,032; G2 −0,56% q=0,08 / −0,48% q=0,26.
- Phi ngân hàng (khớp SUE): như bản chính (G1 +1,05% q=0,028 / +1,55% q=0,042). Ngân hàng: G1 9, G2 4 sự kiện có ô ⇒ không đủ N.
- So với vòng 1 (G1 − G0 không khớp, B3 thường, [2,20] +1,34%): khớp momentum + SUE + B3 loại chính mã còn +1,06%.

## 5. Sai lệch / diễn giải so với PREREG (khai báo)
1. **Diễn giải** mục 7.3: bản đối chứng "không khớp SUE" chạy trên CÙNG tập sự kiện có SUE (để so sánh đúng một trục), không
   phải toàn bộ sự kiện; bản toàn bộ sự kiện in riêng ở §4. Không đổi verdict (G1 đạt (a) ở bản chính nên mục 7.3 không áp;
   G2 trượt (a) ở cả hai).
2. Phân vị momentum cho phép chính tính trên tập có SUE (`momq_s`), không trên toàn tập sự kiện hợp lệ như chữ PREREG §3
   ("toàn bộ sự kiện G0∪G1∪G2 hợp lệ"). Lý do: ô khớp phải nhất quán trong một tập. Chênh lệch giữa hai cách: 912/13.396
   sự kiện thiếu SUE; chưa chạy lại bản phân vị theo toàn tập (chưa đo ảnh hưởng).
3. ADV = trung vị Price×Volume của các phiên CÓ dòng giá trong [−20,−1] (phiên không giao dịch bỏ qua, không tính là 0).
4. Bootstrap coi trung bình G0 của ô là cố định trong mỗi quý được rút (rút theo quý ⇒ G0 cùng quý đi kèm); không tái lấy mẫu
   G0 bên trong ô.
5. Không có cột SUE PIT lưu sẵn ⇒ SUE tự dựng theo đúng công thức PREREG §3; NP là vintage hiện tại (restatement không PIT —
   cùng giới hạn với `fa_ratings_8l`).
6. `pull_vol.py` lần đầu bị ghi nhầm vào gốc `WorkingClaude/` (do `wc_env.sh` đổi thư mục), báo lỗi trước khi ghi dữ liệu; đã
   chuyển về thư mục này rồi chạy. Không ảnh hưởng số.

## 6. Điều kiện cần để kiểm chứng tiếp (không phải đề xuất)
- Kiểm (b) cho G1 cần thêm mẫu IS độc lập: hoặc thêm dữ liệu 2010-2014 (nếu `fa_ratings_8l` dựng lại được PIT cho giai đoạn
  đó), hoặc tích luỹ OOS mới sau 2026-07 (forward, khai trước từ bây giờ: G1 − G0* khớp SUE, [2,40], cùng code) — không được
  chọn lại cửa sổ.
- Nếu (b) đạt: backtest có phí (TC 0,1%/chiều) ở NAV 50B với ràng buộc ADV, walk-forward, DSR/PBO; cân nhắc chồng lấn với
  LAG (PEAD) — đo tương quan lợi suất với book LAG trước khi coi là nguồn edge riêng; quant-skeptic CONFIRMED.

## Tái lập
```bash
cd mike/agents/Taylor/research/rating_8l_lag_p2v2_20261020
$DNA_PYEXE pull_vol.py        # BQ -> raw/vol.parquet (đã kéo 2026-10-20 ~11:55 ICT, md5 8955f3832dcaec86148aeccb5cc9f7e3)
OMP_NUM_THREADS=1 $DNA_PYEXE event_study_v2.py > out_v2_stdout.txt
```
Đầu vào khác: raw vòng 1 (md5 trong PREREG §1), `data/earnings_surprise_data.pkl` md5 `42ab446b604768d6f4dbd19bb27a7430`.
md5 đầu ra: event_study_v2.py `a857d81b…`, out_v2_tests.csv `e291fc36…`, out_v2_criteria.csv `90f6f340…`, out_v2_events.csv `079db2ae…`.
