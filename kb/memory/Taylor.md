# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Taylor ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Taylor/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Taylor_history.md` — không mất, không auto-load.

- [2026-11-14T02:34:48Z] [dd-pnj report 14/11] XONG job Taylor_20261114_022155: investor_report/ PDF 10tr md5 fea39145, chua gui email — CHO Mike doc kiem + user bao 'gui email'; dd_price_zones.json chua ghi
- [2026-11-14T06:57:01Z] [livermore-p0p1 14/11] XONG job Taylor_20261114_063556: 0/48 phan ky dat (G1 kich hoat), H2 R2 0.2-0.29 khong kich hoat; REPORT agents/Taylor/research/livermore_divergence_20261114/REPORT.md md5 850f0bec — CHO Mike quant-skeptic + chay kappa (tuy chon) + user chot thu hep vai/NO-GO
- [2026-11-14T07:37:53Z] [sweep 14/11] universe_pit_p3_selfcheck OPEN: cho universe_pit 13/11 dung bu (dispatch Winston bi chan quyen ghi BQ) — tu dong khi xanh; 3 cau khac CLOSED
- [2026-11-14T12:15:19Z] [dd-pat 14/11] XONG REPORT job Taylor_20261114_120425: tam 75.100 (sau CK thanh khoan 10%), gia 72.700 trong vung hop ly; REPORT md5 303958a8, assumptions d8783c94 — CHO Mike chay fundamental-skeptic; chua ghi dd_price_zones
- [2026-11-14T12:34:51Z] [dd-pat báo cáo NĐT 14/11] XONG job Taylor_20261114_122716: investor_report/ PDF 8tr; LƯU Ý giá 13/11 BQ = 71.000 (72.700 là 06/11) — CHỜ Mike xác nhận + user báo 'gửi email'; chưa ghi dd_price_zones
- [2026-11-15T14:49:54Z] [ai-momentum plan 15/11] XONG job Taylor_20261115_144310: kb/projects/ai-momentum-research-plan-20261115.md (md5 d72baef6), chua code/chua cron — CHO user tra 4 cau F (muc tieu G-proc vs G-fcst, vu tru, M2, topic) roi moi P0; INDEX.md chua them dong (Mike/consolidator)
- [2026-11-15T15:19:23Z] [ai-momentum P0 15/11] XONG job Taylor_20261115_150627: kb/projects/ai-momentum-p0-result-20261115.md (md5 5101c9cb), PREREG 5d3284d0b — CHO Mike quant-skeptic + user chot (2 nam hay noi nguong) + deepseek provider dang loi
- [2026-11-15T15:58:58Z] [ai-momentum P1 15/11] XONG job Taylor_20261115_154607: nhanh research/ai-momentum-p1-20261115 (b07a773b0) KHONG merge; kb/projects/ai-momentum-p1-build-20261115.md — CHO Mike arch-review/quant-skeptic + user quyet noi nguong x2 (PREREG v3) + Wags xong M2
- [2026-11-15T16:29:29Z] [ai-momentum P1-V3 15/11] XONG job Taylor_20261115_162439: nhanh research/ai-momentum-p1-20261115 (a09b71d5e) KHONG merge; kb/projects/ai-momentum-p1-v3-20261115.md; PREREG_v3 md5 d07ffcfd — CHO Mike arch-review/quant-skeptic + Wags xong M2 truoc khi cron
- [2026-11-15T16:46:25Z] [ai-momentum P1-M2-WIRE 15/11] XONG job Taylor_20261115_163050: nhanh research/ai-momentum-p1-20261115 (efd12cbcd, da merge wags/m2-wrapper) KHONG merge master/cron; M2 OK 2/2 retro that; kb/projects/ai-momentum-p1-v3-20261115.md muc M2 — CHO Mike arch-review + user duyet cron
- [2026-11-15T17:12:53Z] ĐANG DỞ: P1-ARCH-FIX vong2 job Taylor_20261115_170852 worktree agents/Taylor/wt-ai-momentum-p1 (B3 xong chua commit) | NEXT: rewrite ai_momentum_daily.py, wrapper bin/ai_momentum_cron.sh, PREREG_v3_2, selfcheck 3TZ, commit
- [2026-11-15T17:35:27Z] [ai-momentum ARCH-FIX v2 16/11] XONG job Taylor_20261115_170852: nhanh research/ai-momentum-p1-20261115 commit moi; CHO Mike smoke live --ledger-dir tam + arch-review vong 3 + quant-skeptic + user duyet cron
