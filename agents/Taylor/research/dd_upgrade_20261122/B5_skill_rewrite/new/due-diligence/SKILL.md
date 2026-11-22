---
name: due-diligence
description: Quy trình due diligence 1 mã cổ phiếu VN cho sleeve discretionary của fleet Mike (user yêu cầu "DD mã X", "mã X mới ra BCTC, phân tích cho tôi"). Thứ tự bắt buộc - lấy BCTC gốc từ website công ty, Bobby đọc ngành MÙ, Taylor DD, fundamental-skeptic phản biện, rồi mới trình user (email chỉ khi user báo). Dùng mỗi khi user yêu cầu DD/định giá sâu một mã sau BCTC hoặc case đặc biệt.
---

# Due diligence 1 mã — LUẬT HIỆN HÀNH (bản B5, 22/11/2026)

File này chỉ chứa luật đang áp, xếp theo thứ tự làm thật. Nguyên văn luật user, lý do, ca minh hoạ và số đo nằm ở
`SKILL_ext.md` cùng thư mục, mục §E1…§E13 (đọc khi cần, không nạp mặc định). Bảng đối chiếu luật cũ→mới:
`mike/agents/Taylor/research/dd_upgrade_20261122/B5_skill_rewrite/LAW_MAP.md`.

## Nguyên tắc chung
- Chỉ NGHIÊN CỨU: không đặt lệnh, không wire. Mua = user duyệt từng tranche.
- Có yếu tố pháp lý ⇒ vẫn phân tích bình thường, chỉ WARNING (user 27/09). Rủi ro vụ án chưa thấy trong KQKD KHÔNG vào base (dd-investor-report L19).
- BCTC gốc là nguồn số. Giả định tự đặt gắn "(ước lượng)". Thiếu số ⇒ "cần kiểm chứng", không bịa.
- Không làm lại từ đầu: phần ổn định tái dùng + dẫn nguồn; chỉ cập nhật phần có dữ kiện mới (§E3).

## Thứ tự bước (không đảo) — pha MÙ GIÁ trước, giá thị trường chỉ sau khoá
1. **Nhận việc + claim**: post lounge, `POST /api/claims resource=topic:dd-<MÃ>-<ngày>`; báo user ngay đã nhận.
   Cổng trần `bin/discretionary_dd_pick.py --claim` (sổ `data/discretionary_dd_ledger.jsonl`) có trong code nhưng CHƯA TỪNG dùng (sổ chưa tồn tại, kiểm 22/11) ⇒ KHÔNG phải bước hiện hành; dùng hay gỡ chờ Mike/user (§E12-f).
2. **BCTC gốc từ website công ty** (BQ/báo chí không làm nguồn chính). Lấy đủ bộ (danh sách §E1): quý mới HN + riêng, giải trình LNST, BCTC năm/bán niên kiểm toán-soát xét gần nhất, CBTT bất thường. Lưu `agents/Taylor/research/dd_<MÃ>_<yyyymmdd>/src/`. Mẹo tải AJAX + đọc PDF scan: §E1. Không có BCTC năm gần nhất đã kiểm toán ⇒ ghi nhận ngay (D5, bước 9).
3. **Snapshot vĩ mô** (Mike, MỘT lần; user 05/11 09:19): ghi ra thư mục TRUNG TÍNH `agents/Taylor/research/dd_macro_snapshots/macro_snapshot_<ngày>.md` — đường dẫn KHÔNG chứa mã, không ghi vào `dd_<MÃ>_*/`. rc=2 ⇒ nêu thẳng, không điền số. Lệnh + 4 quy tắc dùng: §E2.
4. **Bobby (macro-strategist) đọc NGÀNH MÙ** — trước mọi kết luận; chạy song song bước 2 được. Brief chỉ có mô tả ngành + đường dẫn snapshot + dòng nhắc chuẩn (§E2); CẤM mã/giá/BCTC/giả thuyết, kể cả chọn chỉ báo "vì mã này" (chọn theo NGÀNH). Brief qua `bin/dd_blind_lint.py <brief> --mode sector` (rc≠0 ⇒ sửa; lint chưa nối dispatch). Bobby ghi `kb/data_registry/market-state/sector_read_<ngành>_<ngày>.md` (blind: YES; nội dung bắt buộc §E2). Bobby ghi xong mới copy snapshot vào thư mục DD.
5. **Taylor DD — pha MÙ GIÁ**: dispatch `--bg --wakeup-ack --model opus --effort medium --timeout 5400 --thread $DISCORD_THREAD_ID` (prompt viết file rồi `"$(cat f)"`); nội dung brief bắt buộc: §E4. Brief KHÔNG chứa giá/vốn hoá/P/E/P/B hiện tại của mã; kiểm bằng `dd_blind_lint.py --mode valuation --ticker <MÃ>`. Template: `agents/Taylor/research/dd_redo_20261105/DDV/REPORT_r3.md` (đơn ngành), `.../FPT/REPORT_r3.md` (nhiều mảng).
   - Dựng giá trị nội tại từ nền tảng → ghi file khoá giả định + md5 → mới sang bước 6. Không truy vấn giá của mã trước khi khoá.
   - Khoá: `assumptions.json` v1 + `bin/dd_assumptions_lint.py`, **CẢNH BÁO 2 tuần** (rc=0; mốc chặn `DD_ASSUMPTIONS_LINT_ENFORCE_FROM` do Mike đặt). B4 ĐÃ merge master (`b242e616e`; schema `kb/schemas/dd_assumptions_v1.json`, lint `bin/dd_assumptions_lint.py`, ENFORCE_FROM 9999-12-31 = chỉ cảnh báo); DD chưa có file khoá ⇒ khoá bằng file nguồn + `assumptions_md5`.
6. **Pha SAU KHOÁ**: lúc này mới đọc giá (DNSE, không BQ), vốn hoá, P/E-P/B hiện tại, ADV; so giá với vùng; phản ứng giá quanh sự kiện; định giá ngược; chiết khấu thanh khoản theo ADV (luật V3). Không sửa giả định đã khoá vì thấy giá; muốn sửa ⇒ khoá lại có lý do (rev mới).
7. **Phản biện — BẮT BUỘC MỌI DD** (user 01/11 11:08): `python3 bin/dd_skeptic_run.py --dir <dir> --report <REPORT.md>` ⇒ `<dir>/skeptic/rN.json` (script ghi verdict, agent không tự ghi; brief tự qua blind lint `--mode skeptic`). `--mode DD_GENERAL` CHỈ dùng SAU khi user duyệt `~/.claude/agents/fundamental-skeptic.md.proposed` (B6); trước đó chạy không `--mode`. Gọi `Agent(subagent_type="fundamental-skeptic")` trực tiếp chỉ khi runner hỏng — không có `rN.json` ⇒ không ghi được CONFIRMED. Phạm vi kiểm: §E4.
   **HIỆN TRẠNG (22/11): brief của `bin/dd_skeptic_run.py` là template cố định trỏ khung fear-buy `calculated_fear_state_backstop.md`; `~/.claude/agents/fundamental-skeptic.md` hiện chạy THUẦN fear-buy, KHÔNG có từ "moat" ⇒ phạm vi kiểm moat/cân bằng/thiếu hạng mục (§E4, luật 3c + user 01/11) KHÔNG được truyền cho tới khi user duyệt `.proposed` (B6, `--mode DD_GENERAL`). Cách làm tạm: CHƯA THỐNG NHẤT — chờ user (đề xuất, không tự chọn: Mike tự thêm câu kiểm moat vào brief khi chạy tay).**
8. **Áp đính chính** vào REPORT (nêu minh bạch ở Phụ lục E nội bộ). REFUTED ở mức văn bản ⇒ sửa xong mới đóng gói. Sau khi sửa: TÂM dịch >5% so với tâm của bản skeptic đã đọc, HOẶC đổi lớp `verdict_label` ⇒ PHẢN BIỆN LẠI đầy đủ (B2). Dịch ≤5%, không đổi nhãn ⇒ "xác nhận cơ học" (§E10) — nhãn GIỮ `FIXED_UNVERIFIED`, không tự nâng (CONFIRMED-cơ-học chờ user chốt). Bảng việc: `bin/dd_reconfirm_plan.py`.
9. **Ghi sổ giá `kb/dd_price_zones.json`** — ngay sau bước 8, tức bản SAU phản biện đã áp đính chính; không đợi báo cáo NĐT/email. Trường + luật sổ: mục "Sổ mức giá" bên dưới.
10. **Báo cáo nhà đầu tư** (PDF + HTML) bằng skill `dd-investor-report`, chạy `send_dd_report_email.py --dry-run`. KHÔNG gửi thật — TRỪ khi user đã nói "DD <mã> rồi gửi email" trong CÙNG yêu cầu (= lệnh gửi một lần sau skeptic; xem dd-investor-report mục Gửi email).
11. **DỪNG + trình user qua Discord**: verdict 1 dòng + vùng giá + mốc kiểm chứng + điểm yếu + đính kèm PDF (`.ccdb-attachments`), nói rõ "chưa gửi email, báo 'gửi email' thì tôi gửi" — TRỪ ngoại lệ bước 10 (user đã nói "DD <mã> rồi gửi email" trong cùng yêu cầu ⇒ email đã gửi ở bước 10: báo ĐÃ GỬI + địa chỉ + hash PDF, không nói "chưa gửi"). Email theo dd-investor-report mục "Gửi email". Đóng bus question nếu có; ghi `kb/projects/<mã>-dd-<ngày>.md` (pointer, không dán cả báo cáo).
12. **Mã là vị thế discretionary** ⇒ thẻ luận điểm (mục "Loại deal" bên dưới).
Hồ sơ discretionary sleeve (`calculated_fear_state_backstop.md` §2.5, QUALIFY/NON) TÁCH RIÊNG, nội bộ, chỉ khi user xét mua; REPORT DD và báo cáo NĐT không phục vụ fear-buy.

## Khung nội dung DD (Taylor; đủ mục: §E5)
Kiểm chứng giả thuyết user bằng số · chất lượng LN theo mảng (một lần vs bền) · net cash THẬT (+ HTM − vay − tiền ứng khách phải tiêu) + CFO thật · ghi nhận DT/backlog thật · KH/cổ đông lớn/room/ADV (sau khoá) · sizing (V8) · pháp lý WARNING + "scandal di cư" + ý kiến kiểm toán · định giá có kịch bản trọng số + vùng giá + điều kiện đổi ("giá không rẻ" là chưa đủ) · 5F (V5) · mốc khoá trước + điều kiện đổi nhận định CẢ HAI chiều.

## Luật định giá
- **V1 Chi phí vốn (r)** (user 03/11 22:27): r = 13,5% tại điểm neo 03/11/2026 = lãi huy động 12T hiệu dụng `deposit_rate_vn` (effective = max(Big-4 12M, CCTG 12M); ghi số + ngày). r_mới = 13,5% + β×(lãi huy động mới − lãi tại neo), β=1 (giả định; độ nhạy β 0,5/1,0). Mỗi báo cáo ghi r, neo, độ nhạy ±50/±100bp (đ/cp, %). D4 (user 22/11 19:07): báo thêm hai đầu dải Ke nội địa 12,3–13,4%. THỨ TỰ ƯU TIÊN: 13,5% (neo + β×Δ lãi huy động) là r DÙNG CHO TÂM; dải 12,3–13,4% và 3 mốc đọc là phần BÁO KÈM; "không chốt một điểm" nghĩa là không CHỈ báo một điểm (kb/projects/dd-upgrade-final-action-20261122.md §4).
- **V2 Khung Ke nền DCF vô hạn** (user 29–30/10): rf chuẩn hoá ~6,75% (không lấy lãi huy động/TPCP 10Y thô làm rf); ERP nội địa, không cộng CRP Damodaran (15,8% chỉ là đầu trên "góc nhìn nước ngoài"); Ke β1,1 = 12,3–13,4% (dải 10,5–14,0%), không CHỈ báo một điểm (tâm dùng r của V1); ERP ghi đo so với rf nào, β ~1,1 (Blume, kèm β peer), rf dải 6,0–7,5%; phép thử: Ke > ~15% cho mọi doanh nghiệp ⇒ Ke lệch; báo vùng + 3 mốc đọc + độ nhạy g×Ke + tỉ trọng terminal; hạ Ke chỉ kèm g ≤ GDP danh nghĩa và RONIC ≥ Ke. Dòng tiền có thời hạn ⇒ lãi khớp kỳ hạn. Đủ số + ràng buộc: §E6.
- **V3 Thanh khoản** (user 03/11 22:27): báo giá trị TRƯỚC và SAU chiết khấu thanh khoản (phần bù/chiết khấu theo ADV trung vị, free float, số phiên thoát lệnh ở tỷ lệ tham gia 10–20%; cơ sở dữ liệu độc lập: BQ khối lượng/Amihud/độ rộng hoặc số liệu thực thi quỹ; không có ⇒ chỉ độ nhạy; §E6). Nhãn rẻ/đắt theo giá trị SAU chiết khấu; nêu quy mô vị thế áp dụng.
- **V4 Dự án/cam kết vốn**: (a) dự án TĂNG TRƯỞNG — base NPV = 0 ở giá sổ sách (user 03/11 17:06): cấm "đầu tư mới ⇒ giảm giá trị"; lệch khỏi 0 chỉ khi có cơ sở độc lập nêu nguồn, rủi ro cụ thể ⇒ kịch bản có xác suất, không vào base. (b) **D3 (user 22/11 19:07): capex TUÂN THỦ** (chi bắt buộc theo quy định, KHÔNG tạo doanh thu) = DÒNG TIỀN RA trong base — bổ sung, KHÔNG thay (a). Mọi khoản giảm trừ trong base phải có dòng "cơ sở dữ liệu" + nguồn, không có ⇒ chuyển sang độ nhạy. Chi tiết: §E7.
- **V5 Moat / 5F tầng (b)** (user 06/11 20:23): Taylor làm SAU sector read theo `/home/trido/thanhdt/WorkingClaude/5F.md`; REPORT có mục "Vị thế & lợi thế cạnh tranh (5F)": moat_tier WIDE/NARROW/NONE + moat_type + rủi ro số 1, có bằng chứng định lượng + nguồn. `data/moat_tags.csv` chỉ đọc/đề xuất, không sửa. Đầy đủ TỐI ĐA 1 lần/năm/mã (user 06/11 23:28); <12 tháng ⇒ tái dùng + 1–2 dòng kiểm nhanh. Chi tiết: §E3.
  - Bền (3 điều kiện §E3) ⇒ thưởng bằng tham số tường minh có cơ sở; RONIC terminal > Ke CHỈ khi WIDE có cơ chế.
  - NARROW/NONE/có đồng hồ cắt hào ⇒ không thưởng, KHÔNG TRỪ ở giai đoạn dự báo: không ép biên/ROE về TB ngành hay Ke (user 08/11 10:50). Terminal RONIC = Ke là giả định CUỐI KỲ (D4, user 22/11 19:07), không phải phép trừ (§E12-b).
  - Ngầm thưởng ⇒ ghi rõ + độ nhạy, không đổi headline; không đếm hai lần; độ nhạy WIDE/NARROW/NONE; cấm suy moat từ giá; 5F non-PIT ⇒ cấm backtest.
- **V6 Hai nền + cờ phân kỳ — chỉ HIỂN THỊ** (user 11/11): bảng V_ngắn / V_dài / D = |ln(V_ngắn/V_dài)|; tỷ lệ tái đầu tư g/ROE chặn [0; 0,8]; cờ D>ln2 / D>ln3; dòng C4 và D2 kèm nhãn "chưa qua tiêu chí khoá trước, chỉ theo dõi". Tâm/vùng/nhãn/luật 0,85×tâm vẫn từ mô hình DD; không trộn (blend w=0,5 bị bác). HỆ QUẢ CỜ (user 11/11 11:37; watch KHÔNG đọc D ⇒ miễn trừ chỉ sống trong lời viết DD): D>ln2 ⇒ giải thích nguồn chênh (capex chu kỳ, vốn lưu động, một-lần, số cổ phiếu, ROE<g làm V_ngắn sụp) + mở rộng vùng đọc thành [min,max] hai nền; D>ln3 ⇒ ghi "phân kỳ mạnh", luật 0,85×tâm KHÔNG tự kích hoạt, cần Mike/user phán đoán; FCFE≤0 hoặc trượt cổng CFO ⇒ chỉ V_ngắn + giải thích dòng tiền âm. Nếu D>ln2 ∧ V_dài<giá ∧ capex/CFO cao ⇒ ghi "FCFE thấp vì đầu tư tăng trưởng (capex)", ĐỪNG hiểu cờ là cảnh báo đắt (user 11/11 12:59, §E8). Giờ ICT: 11/11 11:37 (hai nền), 12:09 (chặn g/ROE 0,8; khi ROE≤g ghi "tái đầu tư bị chặn ở 80%"), 12:59 (C4), 17:23 (D2); không ghi `v_short/v_long/D`/C4/D2 vào sổ. Đủ luật + nhãn nguyên văn: §E8.
- **V7 Dùng snapshot vĩ mô**: chỉ dòng cờ `ok`; DISPLAY-ONLY; không đổi giá trị nội tại/biên an toàn/nhãn vì một chỉ báo (§E2).
- **V8 Sizing — CHƯA THỐNG NHẤT, chờ user (Q4, review 22/11 F22-d).** Ba mức đang cùng tồn tại: (i) skill cũ "tiền lệ ≤0,5–1,0% NAV"; (ii) `~/.claude/agents/fundamental-skeptic.md` "sleeve cap 2-4% NAV per name"; (iii) thực tế 5% NAV/mã (`kb/projects/disc-fpt-nnc-approval-20261105.md:4,7`, user 05/11 22:17 duyệt FPT/NNC). KHÔNG tự chọn; DD đụng sizing ⇒ nêu cả ba.

## Sổ mức giá `kb/dd_price_zones.json` (user 01/11 22:39 + A2/B2/D5 22/11)
- Append-only; rev cao nhất của (mã, dd_date) thắng. Trường cơ bản (danh sách đủ §E10) + trích nguyên văn dòng chứa vùng giá (số khớp nguồn) + `assumptions_md5` = md5 file nguồn/khoá; center_kind ưu tiên giá trị kỳ vọng trọng số kịch bản.
- Từ 2026-11-23 bắt buộc (`bin/dd_price_zones_selfcheck.py` chặn): `skeptic_final` ∈ {CONFIRMED, FIXED_UNVERIFIED, REFUTED_OPEN, NONE}, `audited_fy_missing` (bool), `skeptic_verdict_path` (file thật hoặc `null`, không đoán), `skeptic_final_basis` (`skeptic_run`|`user_confirmed`). Định nghĩa enum: §E10.
- `CONFIRMED` CHỈ ghi qua `bin/dd_ledger_append_confirmed.py --ticker <MÃ> --verdict <dir>/skeptic/rN.json --write` (verdict CONFIRMED thật, md5 báo cáo khớp). Vòng skeptic mới trên DD đã ghi sổ ⇒ rev mới + `correction_reason`, không sửa tại chỗ. Sửa nguồn sau khi ghi ⇒ rev mới (watch loại mã nếu md5 lệch).
- **D5** (user 22/11 19:07): thiếu BCTC năm gần nhất đã kiểm toán ⇒ VẪN ghi sổ với `audited_fy_missing=true`; không vào Bậc 1 watch; cổng LAG coi như chưa có DD. Hiện trạng code: watch ĐÃ loại mã `audited_fy_missing` khỏi Bậc 1 (A7, `bin/dd_price_zone_watch.py:115`, 22/11); cổng LAG chỉ chặn khi bật `LAG_DD_REQUIRE_CONFIRMED` (§E12-g).
- Sau khi ghi: `python3 mike/bin/dd_price_zones_selfcheck.py` 0 lỗi. Watch tối ghi chú mã giá dưới tâm ≥15% (chỉ để user cân nhắc). DD hết hạn khi có BCTC quý mới hơn hoặc 120 ngày.
- Backfill mơ hồ: `kb/projects/dd-ledger-ambiguous-queue-20261122.md` (hạn 29/11).

## Loại deal + thẻ luận điểm (D2, B3)
- Sổ `kb/thesis_cards.json`: `deal_type` ∈ {value_long, event_trade, fixed_rules}; append-only theo (ticker, rev). CHỈ hiển thị/nhắc (`bin/thesis_card_watch.py`), không đổi lệnh/luật thoát.
- "Discretionary sleeve không cần quy tắc thoát cố định" (user 22/11 19:27 ICT) — hiện CHỈ áp FPT (`value_long`). NNC/VGS GIỮ `fixed_rules` hiện hành (`data/discretionary_exit_rules.json`) CHỜ user xác nhận. Đổi luật thoát = rev thẻ mới + sửa JSON từng vị thế, có `approval_ref`.
- Thẻ nháp FPT/NNC/VGS + cron nhắc mốc: chờ user duyệt (22/11).

## Cổng LAG (B1/D1/D5)
`trading_bot/plan.py`: `LAG_DD_REQUIRE_CONFIRMED = False` (mặc định; bật tay). Khi True: mua LAG đòi `skeptic_final=CONFIRMED` và `audited_fy_missing≠true`. Đang False ⇒ D1/D5 CHƯA có hiệu lực ở cổng tiền thật cho tới khi bật.

## Chống làm đi làm lại (user chốt option B 08/11)
- Khoá giả định cốt lõi (nguồn BCTC, cơ sở TTM/quý, tham số moat, r) vào file nguồn TRƯỚC khi fan-out; sổ đòi `assumptions_md5`.
- Fan-out ≥5 mã ⇒ pilot 1 mã + skeptic xong rồi mới chạy phần còn lại.
- Mọi "bài học" đưa vào brief/skill kèm `evidence:` (file:dòng hoặc truy vấn) và đối chiếu `bigquery_dictionary.json` TRƯỚC khi fan-out.

## Bẫy đã cắn (chi tiết + ca: §E9)
- `ticker_financial`: `GPM_P0/NPM_P0/EBITM_P0/EBITDA_P0` là TTM, `Revenue_P0`/`NP_P0` là QUÝ; `Cash_P0` thiếu tiền gửi HTM. BQ chưa có quý mới ⇒ ghi lệch nguồn.
- Không kết luận trước khi Bobby đọc xong. ROIC đỉnh chu kỳ không phải bằng chứng hào.
