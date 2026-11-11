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

- [2026-11-10T13:20:38Z] [2026-11-10] dd-VGS r2 XONG job Taylor_20261110_131720: tam 26.778 (sau CK 1ty 26.526, P10 19.393/P90 34.722), gia 19.300 DUOI mong manh, luat4 dat; CHO Mike skeptic lan 2 + ghi so
- [2026-11-10T13:41:29Z] ĐANG DỞ job Taylor_20261110_132044 lagadj r2: A1 4 chân r3z xong (Δ pin0 -0,04/pin1M -0,37 ⇒ KHÔNG re-pin), pkl v2+pt v2 xong; code wt-lagadj-1110 sửa B uncommitted; NEXT: selfcheck, B5/B9/B10, doc, tách commit, bus
- [2026-11-10T13:53:11Z] CHỜ Mike duyệt lag-cache-adjusted r2: code fd29f496a (wt-lagadj-1110) + mike edb3ffba0; KHÔNG re-pin R3; user quyết 4 mục trong doc §6; không merge/apply/cron trước duyệt
- [2026-11-10T15:28:07Z] CHỜ Mike: lagadj r3 code cf21463b9 + mike eecd82ae7 + repin branch feat/repin-mirror-live-20261110 @307593815; chờ quant-skeptic, user quyết re-pin + neo DD -28,0 + TTL delist
- [2026-11-11T00:44:34Z] CHỜ user chọn A/B/C cho paper expvol_pacing (N=2/25; DISC buy thiếu state_<T>_<acct>.json không vào trial); checkpoint kế 2026-12-08
- [2026-11-11T01:22:18Z] [lag-rating-lag-q3 11/11] XONG job Taylor_20261111_011218: M1 dong 0/88; lo moi = troi rating dong Q3 (VGS); de xuat P1 log rating cong/P2 re-rate co dieu kien — CHO Mike/user
- [2026-11-11T03:44:15Z] [dd-vn-calib 11/11] XONG job Taylor_20261111_032615: engine FCFE KHONG TUONG THICH (K3 khong hoi tu, lech theo ma); de xuat P1 FCFE=LNSTx(1-g/ROE) pha 2 — CHO Mike/user duyet
- [2026-11-11T03:52:31Z] CHỜ Mike bổ sung Discord timestamp user chọn B cho VGS max_sessions=null (bus 01:05Z ghi A=25); code+data đã merge 11/11
- [2026-11-11T04:21:24Z] [dd-blend 11/11] XONG job Taylor_20261111_040113: prelock K3n w*=0 (khong vuot); hau kiem w=0.5 tot hon ro (AEdm -18..29%, beta x2.5), H1 bac; K3n ti so la loi thiet ke; CHO Mike skeptic + user duyet de xuat DD
- [2026-11-11T04:57:08Z] [dd-fwd-prelock 11/11] XONG job Taylor_20261111_043843: V_ngan KHONG co thong tin bo sung on dinh (truot IS), DD giu hien-thi-chi; forward scorer san sang, moc 12T 10-11/2027 — CHO Mike skeptic
- [2026-11-11T05:28:00Z] [dd-fcfe3y-decay 11/11] XONG job Taylor_20261111_051016: Q1 nhan khoa ARTIFACT (luc thong ke thap, mo ta suy yeu tu 2021+); co che = tru capex (capex/CFO thanh du bao duong OOS); 0/8 sua, C4 sat nguong 2/4 — CHO Mike skeptic; chay lai ~Q4/2027
- [2026-11-11T10:11:57Z] [dd-cfo-anchor 11/11] XONG job Taylor_20261111_095819: 0/9 nen trung dung dat prelock (D2 capex chuan nganh gan nhat, truot BH); thi truong KHONG thuong CFO/LN; giu V_dai — CHO Mike skeptic + user
