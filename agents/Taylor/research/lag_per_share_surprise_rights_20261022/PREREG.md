# PREREG — LAG per-share surprise + rủi ro ex-date quyền mua (job Taylor_20261021_165514)

Viết TRƯỚC khi tính bất kỳ số outcome nào (chỉ mới kéo bảng thô ISS/AIS/OShares). PAPER-ONLY,
không wire, không đổi pin, không ghi registry.

## Step 0 — pre-flight (đã chạy)
`rnd_preflight_power.py --mean-bps 300 --sd-bps 1500 --obs-per-year 4 --n-available 60 --n-trials 3 --n-rule per-event`
⇒ **MARGINAL** (DSR 0,75; cần ~159 obs độc lập). Effect giả định là ƯỚC LƯỢNG (không từ mẫu).
Hệ quả chấp nhận trước: Q2 là CHẨN ĐOÁN, không phải tìm edge giao dịch; kết luận "không đủ dữ liệu"
là đầu ra hợp lệ. Q1/Q3 là mô tả (đếm, phân bố) — không cần power.

## Tập sự kiện U (mirror pt_v23_audit_2014.py §4, đọc code dòng 1053-1140)
- `data/earnings_events_classified.csv` merge `surprise_B_MA` từ `data/earnings_surprise_data.pkl`
  (FLOOR 1e9, clip ±5); walk prior_n_good / pa_HL3 (HL 3 năm) như engine (prior = sự kiện NP_R≥15
  có post_ret, xét trước theo thứ tự hàng).
- Gate: NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5 ∧ forensic ON (`data/forensic_flags.csv`, severity=exclude,
  Release_Date ≥ date). Nonop OFF (đúng mặc định).
- Entry = Release + 5 phiên (lịch phiên = VNINDEX trong `VNINDEX.csv`), entry ∈ [2014-01-01, cuối dữ liệu].
- Tầng: LAG_HI nếu surprise_B_MA > 0,5, ngược lại LAG_LO.
- Superset cho "đổi nhãn": C = prior_n_good≥4 ∧ pa_HL3≥5 ∧ không forbid (prior GIỮ theo định nghĩa
  production — chỉ thay nhãn của SỰ KIỆN HIỆN TẠI để cô lập tác động).

## Số cổ phiếu
- S_k = `ticker_financial.OShares` của dòng (ticker, quarter của P_k), k=0..4 (P_k = quý sự kiện lùi k quý).
  ⚠️ TRAP: cột bị restate (registry `fundamentals/ticker_financial_oshares.md`). Dùng cho TỈ LỆ thay đổi
  giữa các quý; độ tin cậy kiểm bằng corporate_action (dưới).
- g = S_0/S_4 (thay đổi thô năm-trên-năm).
- E = Π(1+exercise_ratio) các ISS `executed` có exright_date ∈ (time_P4, time_P0] (time = cột `time` dòng quý).
  "Giải thích được" nếu |g/E − 1| ≤ 2%. Nếu trong cửa sổ có ISS ratio 0/NULL (riêng lẻ/ESOP/chuyển đổi)
  ⇒ nhãn `ratio_missing` (không kết luận được bằng ratio). Còn lại ⇒ `unexplained`.
- B_k = Π(1+ratio) chỉ các ISS executed KHÔNG thu tiền (Trả cổ tức bằng CP, Cổ phiếu thưởng) với
  exright ∈ (time_Pk, time_P0].

## Biến thể (khai đủ: 2, không thêm)
- **PS2 (chính, kiểu IAS 33)**: NP*_k = NP_Pk × S_0 / (S_k × B_k). Cổ tức CP/thưởng hồi tố (không pha loãng);
  quyền mua/riêng lẻ/ESOP/chuyển đổi = pha loãng thật. (Phần "bonus element" của quyền mua KHÔNG hồi tố —
  bảo thủ, nghiêng về phạt pha loãng mạnh hơn IAS 33 thật.)
- **PS1 (thô)**: như PS2 nhưng B_k ≡ 1 (mọi tăng CP đều là pha loãng).
- NP_R_ps = NP*_0/NP*_4 − 1 (×100) khi NP_P4>0 ∧ NP_P0>0; ngược lại giữ NP_R production.
  surprise_ps = công thức production trên NP*_k (FLOOR 1e9, clip ±5).
- Thiếu S_k bất kỳ ⇒ giữ giá trị production, đánh dấu `no_share_data`.

## Nhóm
- L (thay đổi CP lớn): |g − 1| ≥ 10%. L2 (pha loãng thật sau hồi tố): S_0/(S_4·B_4) ≥ 1,10.

## Q2 outcome & thống kê
- y = post_ret (Close điều chỉnh R+30 / R+5 − 1, từ CSV) và y_ex = y − VNINDEX cùng cửa sổ. Outcome CHỈ là nhãn
  đo, không dùng làm filter.
- (a) Spearman IC của surprise production vs surprise_ps với y_ex trên U ∪ (C∩NP_R_ps≥15); IC của hiệu.
- (b) Nhóm đổi tầng HI→LO (theo PS2): mean y_ex so với HI giữ nguyên và LO giữ nguyên.
- (c) Nhóm rớt qualify (NP_R ≥15 nhưng NP_R_ps2 <15): mean y_ex so với U còn lại.
- CI: bootstrap cụm theo Release_Date (B=2000) + bản cụm theo mùa công bố (năm-quý của Release_Date).
- IS = entry 2014-2019, OOS = 2020+; LOYO cho hiệu chính.
- Luật kết luận (chốt trước): đề xuất đổi định nghĩa CHỈ KHI hiệu của nhóm đổi nhãn cùng dấu IS & OOS,
  CI 95% cụm-mùa không chứa 0, và N độc lập (số Release_Date) ≥ 30. Ngược lại: "không đủ dữ liệu / giữ nguyên".

## Q3 quyền mua
- Rights = ISS meth "Quyền mua CP cho Cổ đông hiện hữu", event_status ∈ {executed, announced}.
- (a) exright ∈ [entry, phiên entry+25] (cửa sổ giữ R+5→R+30). Trạng thái "đã công bố chưa có ngày tại entry":
  public_date < entry ≤ exright — ⚠️ public_date bị ghi đè (Bẫy 2b) ⇒ chỉ là xấp xỉ, ghi rõ.
- (b) K = total_value / issue_volumn khi cả hai > 0, ngược lại "không có K". P = `ticker.Price` (chưa điều chỉnh)
  phiên liền trước exright. adj = ((P + rK)/(1+r) − P)/P.
- (c) Tiền cần = r × K × số CP giữ; % NAV = slot% × r × K / P_entry (P_entry = Price chưa đ/c ngày entry; bỏ qua
  cổ tức CP xen giữa). slot 8% và 10%.
- (d) Không thực hiện/không bán quyền: lỗ vị thế = −adj (tỉ lệ), × slot% ra % NAV.
- (e) Kéo CAGR ước tính = Σ_{sự kiện trong cửa sổ} (lỗ % NAV) / số năm — nhãn ƯỚC LƯỢNG (giả định mọi sự kiện U
  đều được vào lệnh với slot 8-10%, trong khi engine bị giới hạn tiền ⇒ chặn trên).
