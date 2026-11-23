# BÀN GIAO — topic "DD vs Value Radar — kiểm định thiên lệch định giá + skeptic PAT/TCH/VGS" (thread 1574470111769796668)
Từ Mike (topic DD vòng 3 1574365262965121136, 24/11/2026 00:0x ICT). Topic cũ dừng. HHS/CK holding ở topic 1574394938161111083 — KHÔNG đụng.

## User yêu cầu 24/11 00:00 ICT
1. Chạy skeptic cho 3 mã (PAT, TCH, VGS — đang FIXED_UNVERIFIED, chưa có verdict skeptic thật).
2. "DD cho thấy hầu hết định giá đều rất thấp, tỉ lệ mã trong vùng hoặc giá rẻ cực thấp. Value radar ở mốc thấp nhất 10 năm; kết quả định giá là thị trường hầu hết đang định giá sai rất cao so với giá trị thật. Khá mâu thuẫn. Hãy suy nghĩ thật kỹ và tìm giải pháp khắc phục."

## Số đã kiểm (Mike, 24/11 00:00)
- Radar (value_radar.py, display-only): 🟢 2,3 RẺ — P/E 9,66 (p0), P/B 1,68 (p2), spread EY−CCTG12T +2,96pp (p5 sau đảo chiều). Top-100 vốn hoá, capped 10%, P/E TTM, rolling 10Y. Phụ lục C của chính radar: 0/17 lăng kính qua đa kiểm định; đầu RẺ không đơn điệu.
- Sổ DD (36 mã, entry cuối): giá ref so vùng DƯỚI 4 / TRONG 22 / TRÊN 10; trung vị giá/tâm 1,085; chỉ 7/36 (19%) đạt luật 4 (giá ≤0,85×tâm). Nhóm CONFIRMED (17) trung vị 0,92; nhóm REFUTED_OPEN (15) trung vị ≈1,46. ⇒ "mâu thuẫn" vừa nhỏ hơn cảm nhận (đa số TRONG vùng) vừa tập trung ở nhóm vừa dựng lại 23/11.

## Giả thuyết của Mike (cần TEST, không kết luận)
Về phía MẪU: (G1) 36 mã không phải mẫu thị trường — nhóm LAG-candidate chọn theo động lượng lợi nhuận (giá đã tăng), VCB/PNJ là tên phổ biến trả premium; REFUTED_OPEN dồn vào nhóm này.
Về phía RADAR (cách đo): (H1) P/E TTM thấp vì EPS ở đỉnh chu kỳ (value trap kinh điển); (H2) top-100 cap-weight bị ngân hàng + Vingroup chi phối, khác tập DD (phi ngân hàng, vốn hoá vừa); (H3) radar so với LỊCH SỬ (10Y) còn DD so với TUYỆT ĐỐI (r≈13,5% neo lãi huy động, g_T cap 5,5%, ROE fade, NPV0) — hai thước đo khác nhau: với r cao hiện nay, P/E 'công bằng' kiểu DD có thể chỉ ~8–12 ⇒ P/E 9,66 gần công bằng chứ không rẻ; (H4) dữ liệu PE/PB bẫy cột; (H5) chế độ sau FTSE 21/09/2026.
Về phía DD (thiên lệch phương pháp): (G2) chồng nhiều haircut một chiều (r cao, ROE fade về TB, NPV0, CK thanh khoản/quản trị/holding, quỹ KTPL/ESOP/NCI, capex tuân thủ V4, kịch bản xấu có trọng số) — mỗi cái hợp lý riêng nhưng cộng lại hạ tâm hệ thống; (G3) không có hiệu chuẩn mức: nếu proxy DD trong lịch sử cũng cho giá/tâm trung vị ≈1,3 thì 1,085 là RẺ; (G4) skeptic đối xứng trên giấy nhưng 'quá thấp' thường đi vào độ nhạy chứ không vào base.
Hướng khắc phục (chỉ ĐỀ XUẤT sau khi có số): S1 nhãn theo PHÂN VỊ giá/tâm so lịch sử thay vì ngưỡng tuyệt đối (giữ định giá MÙ GIÁ); S2 tâm = kỳ vọng có trọng số gồm kịch bản TĂNG có cơ sở; S3 NPV>0 có điều kiện cho franchise có ROIC-spread bền đo từ lịch sử; S4 r hiệu chỉnh theo ERP bằng chứng; S5 hiển thị 2 nhãn (nội tại mù giá vs so-với-lịch-sử). Mọi thứ chạm quy tắc user (V4, NPV0, mù giá) = chờ user quyết.

## Job đang chạy (--thread 1574470111769796668, --no-followup; dispatch 24/11 00:0x ICT)
- Skeptic (sonnet): PAT=Taylor_20261123_170306 · TCH=…170308 · VGS=…170311 → skeptic/rN.json + LEDGER_PROPOSAL (rev+1) + finding dd-skeptic-<MÃ>-20261124. Không dựng rev báo cáo.
- R1 (opus/medium)=Taylor_20261123_170313 — phía radar (H1–H5) → REPORT_R1.md, finding dd-vs-radar-R1-20261124.
- D1 (opus/medium)=Taylor_20261123_170315 — phía DD (G1–G5, proxy cơ học PIT, waterfall haircut, đối xứng skeptic, đề xuất khắc phục) → REPORT_D1.md, finding dd-vs-radar-D1-20261124.
Prompt: PROMPT_SK.txt / PROMPT_R1.txt / PROMPT_D1.txt cùng thư mục này (agents/Taylor/research/dd_vs_radar_20261124/).

## Việc của phiên topic này
1. Poll từng job (claim-reply trước; status cùng lượt; usage_limited ≠ chết — grep -l <id> bus/jobs/*); kỷ luật ScheduleWakeup ~600s, post tiến độ thật vào topic.
2. Skeptic xong → verify (r mới nhất, md5 khớp, LEDGER_PROPOSAL, selfcheck) rồi áp sổ trong worktree riêng (git worktree add ../wt-1574470111769796668 -b session/1574470111769796668 từ master MỚI NHẤT; mẫu /tmp/apply_cont.py — đổi W + SPEC 3 mã; rsync artifact nhẹ loại src/pdf/png/jpg/xlsx/img*; verdict CONFIRMED ⇒ entry FIXED_UNVERIFIED rồi bin/dd_ledger_append_confirmed.py; khác ⇒ REFUTED_OPEN; selfcheck sạch; xoá untracked trùng + git checkout file trùng ở cây chính trước merge). Lưu ý topic CK holding cũng sẽ thêm entry HHS vào kb/dd_price_zones.json ⇒ rebase/merge cẩn thận (conflict là chuyện append — giữ cả hai).
3. R1 + D1 xong → verify artifact; chạy quant-skeptic (Agent subagent_type=quant-skeptic hoặc bin/verify_finding.sh) lên phần ĐO (look-ahead, N độc lập, bẫy mcap, survivorship, proxy ≠ DD đầy đủ); Mike tổng hợp MEMO duy nhất: (a) chẩn đoán xếp hạng nguyên nhân + phần mâu thuẫn mỗi nguyên nhân giải thích; (b) đề xuất khắc phục có chi phí/rủi ro; (c) mục cần user quyết; báo vào topic. KHÔNG tự đổi DD/radar/skill/sổ theo kết luận; KHÔNG wire.
4. Cập nhật bin/remember.sh Mike; KHÔNG email.

## KHÔNG
Không email; không tự đổi quy tắc user (mù giá, V4, NPV0); không ghi sổ DD khi job chạy; không đụng topic 1574394938161111083 (HHS) và 1574365262965121136.
