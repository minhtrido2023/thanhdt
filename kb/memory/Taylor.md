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

- [2026-10-08T16:12:58Z] ĐANG DỞ job Taylor_20261008_155435 repin park0 dep1m: 4 chân + control xong, REPORT.md viết xong (research/repin_park0_dep1m_20261008) | NEXT: m_p0 xong → điền §1.2, registry .proposed, bus finding repin-r3-park0-dep1m
- [2026-10-08T16:19:15Z] [repin park0 dep1m 10-08] DONE 555bd103; neo DD giữ −25,2% (park0 đo −23,9%); registry .proposed chờ Mike/user. Rerun còn treo: sàn nhiễu park0, chân không-bắc-cầu park0.
- [2026-10-08T16:32:32Z] ĐANG DỞ job Taylor_20261008_163222 bal-maxpos-lag-idle: bắt đầu cổng 0 | NEXT: đọc engine MAX_POS_V11 + 2 file động cơ, đếm ứng viên rank13-20 phiên LAG idle
- [2026-10-08T16:58:55Z] [bal-maxpos-lag-idle 10-09] NO-GO c604cd1e (nới trần BAL 16/20 −1,1…−2,1pp, không chạm cash LAG vì 2 sổ cái độc lập). Worktree wt-balmaxpos-1009 dọn được. Hướng duy nhất còn lại = allocator động (không khuyến nghị).
- [2026-10-08T17:26:05Z] ĐANG DỞ job Taylor_20261008_172556 rerun nhóm B (Q-sleeve/fincap/L1 pool) trên engine sửa double-count: bắt đầu | NEXT: đọc review 2.B + registry 07-12/07-14/09-09
- [2026-10-08T17:33:34Z] ĐANG DỞ job Taylor_20261008_172556 rerun nhóm B: PREREG b0fe4df4, 28 chân park0,7 đang chạy (research/rerun_groupB_fixed_20261009, legs.txt/legs_rest.txt) | NEXT: analyze.py → compare_sandbox.sh → REPORT.md + registry .proposed + bus finding rerun-groupB-fixed-engine
- [2026-10-08T18:07:44Z] [rerun nhóm B 10-09] DONE c8e096e7: Q8/Q12 hết ý nghĩa, claim breadth phải sửa (registry .proposed chờ Mike/user); chờ quant-skeptic. Việc tiếp nếu lãi hạ: c30 vs l1b@0,3 prereg mới.
- [2026-10-09T03:08:10Z] ĐANG DỞ job Taylor_20261009_030802 cash-div first_disclosure_datetime validation (read-only): bắt đầu | NEXT: data_registry corporate_action + query snapshots
- [2026-10-09T03:16:52Z] [cash-div fd 10-09] Kết luận C (d9361ee4): first_disclosure_datetime không PIT; giữ mốc 2027-08. Registry .proposed Bẫy 5 corporate_action_snapshots chờ Mike duyệt.
- [2026-10-09T09:34:03Z] ĐANG DỞ job Taylor_20261009_093353 selfcheck-red owner sweep 9 file: bắt đầu | NEXT: chạy lại 9 selfcheck, phân loại
- [2026-10-09T09:38:42Z] ĐANG DỞ job Taylor_20261009_093353 sweep: custom30 CLOSED; 8 file phân loại xong (atc/basket/cpi/lag_gov/freshness=b, rating8l/capit/cctg=d live CSV) | worktree /home/trido/thanhdt/wt-screds-1009 branch fix/selfcheck-red-sweep-1009 | NEXT: sửa+chạy xanh, merge, close, finding
- [2026-10-09T09:46:11Z] [selfcheck-red sweep 10-09] 9/9 CLOSED (6a73ef82). Nợ: rating8l --bq BQ2-4 pin số 09-27 (HDG đã lật POWER); nhãn cctg_6m cho dòng 12M.
