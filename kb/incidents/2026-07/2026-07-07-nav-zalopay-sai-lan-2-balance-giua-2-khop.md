---
kind: incident
date: 2026-07-07
topic: nav-zalopay-sai-lan-2-balance-giua-2-khop
title: >-
  2026-07-07 (tối) — NAV ZaloPay sai LẦN 2 cùng ngày: balance chụp giữa 2 cú khớp
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-07 (tối) — NAV ZaloPay sai LẦN 2 cùng ngày: balance chụp giữa 2 cú khớp

**What happened:** đính chính đầu tiên (992.702.201đ) VẪN sai — user chỉ ra thiếu phần trừ
tiền MUA hôm nay và chỉ đích danh: "kiểm tra lại các field sẽ biết, tiền mua khớp T0 âm là
bao nhiêu."

**Root cause:** ngày ZaloPay VỪA BÁN VỪA MUA. Bản ghi balance dùng để tính NAV có ts
13:00:02 — đúng 20 giây TRƯỚC cú khớp mua VCB (13:00:22): totalCash lúc đó đã cộng tiền
bán MSH nhưng CHƯA trừ tiền mua VCB, trong khi mtm_stock (positions broker) đã đếm VCB
mới → double-count đúng 6.115.927đ. Đọc tươi 15:33 xác nhận cơ chế DNSE: khi lệnh mua khớp
T0, tiền chuyển totalCash → **secureAmount** (phong tỏa chờ cấn trừ batch tối ~20h):
totalCash 11.406.701 → 5.290.774, secureAmount 0 → 6.115.927 (khớp từng đồng).

**Fix:**
1. Invariant mới trong `daily_nav_snapshot.py`: bản ghi balance PHẢI mới hơn cú khớp FILL
   cuối cùng trong ngày — vi phạm → từ chối tính NAV (fail loudly), vì snapshot giữa 2 cú
   khớp lệch đúng bằng giá trị lệnh sau.
2. Bug phụ tự cắn khi test invariant: script chạy shell UTC → bản ghi balance tươi mang ts
   UTC, journal mang ts ICT → so sánh sai múi giờ. Fix: script tự set TZ=Asia/Ho_Chi_Minh
   + tzset() đầu tiến trình.
3. Số đúng verify 2 chiều: 992.702.201 − 6.115.927 = **986.586.274** = mtm 981.295.500 +
   totalCash tươi 5.290.774. Đính chính lần 2 đã gửi Trading report; history đã sửa.

**Lesson:** NAV ngày có giao dịch = hàm của THỜI ĐIỂM chụp balance, không chỉ nguồn dữ
liệu. "Đọc từ API thật" chưa đủ — phải đọc SAU sự kiện cuối cùng làm tiền dịch chuyển.
Cơ chế DNSE cash account: mua khớp T0 → totalCash→secureAmount trong vài phút (không đợi
batch tối); NAV cash component = totalCash (secureAmount là tiền sẽ rời đi trả cho cổ
phiếu ĐÃ được đếm trong stock — cộng nó vào là double-count). User là người bắt lỗi lần
thứ 3 trong 2 ngày — cả 3 lần đều là provenance/timing của số client-facing.
