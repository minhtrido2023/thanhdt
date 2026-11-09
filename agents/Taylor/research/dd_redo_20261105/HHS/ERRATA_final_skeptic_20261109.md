# Errata cuối — HHS (09/11/2026). Không đổi tâm/P10/P90/nhãn trừ khi ghi rõ.

- dd_HHS_20261101/GAPS_FILL.md:57 còn 'đáo hạn 18/11/2026' (gốc lỗi lẫn năm; vay 390 tỷ đã trả); hhs_r3.py mỗi lần chạy lại sinh lại chuỗi sai vào SUMMARY.json:368 (đang vá tay) — chạy lại là lỗi quay về.
- SUMMARY_5F.json: new.label còn TRONG; TONGHOP_FINAL_20261108.md:9 dòng HHS còn r2 (10.387, TRONG).
- REPORT_r3.md:75 (G10): nếu biên 52% áp trên tổng chi phí thì chi phí hoàn thiện làm thặng dư TĂNG; rủi ro thật là biên cao tầng HH1–HH4.
- Nhận định: BĐSĐT base 100% theo giá trị PPA nội bộ nhóm, mâu thuẫn REPORT_r2:60 ('không phải giá trị kinh tế'); trục 0/50/100 ⇒ tâm 13.492 (−477), nhãn giữ.
- Chưa quét tin 01–08/11.
- QUY ƯỚC CẦN USER PHÁN XỬ: nhãn DƯỚI dựa hoàn toàn vào CK holding base 0% (+3.1–3.2k đ/cp, ~85% đoạn 10.193→13.969); giá đang ngụ ý CK holding ~33,5%; bản CK holding 27% [UL] cho 10.761 TRONG (36,6% dưới giá). HHS đang forensic_flags exclude ⇒ loại khỏi candidate plan bất kể nhãn.
