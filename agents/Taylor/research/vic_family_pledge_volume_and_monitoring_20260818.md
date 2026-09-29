# VIC-family: (1) khối lượng cầm cố cổ phiếu, (2) theo dõi định kỳ tin "chuyển nhượng cổ phiếu
đảm bảo trái phiếu" — 2026-08-18

Job Taylor_20260818_040013 (dispatch Mike, follow-up 2 câu hỏi mở cuối
`vic_pinning_hypothesis_and_creditrate_proxy_20260818.md`, đã được John duyệt).

---

## (a) Tổng khối lượng cầm cố cổ phiếu VIC-family / free float

**KHÔNG XÁC MINH ĐƯỢC con số tổng hợp một lần** — đúng như dự đoán trong dispatch: đây là dữ liệu
phân tán theo từng đợt công bố riêng lẻ ở VN, không có 1 nguồn tổng hợp công khai tìm được qua
WebSearch. Không có cổng tra cứu tổng hợp "collateral pledge summary" nào của HOSE/SSC/công ty
chứng khoán xuất hiện trong 6 lượt WebSearch (đã thử: tìm trực tiếp "cầm cố cổ phiếu tổng hợp",
tìm riêng VIC/VHM/VRE/VPL, tìm theo tên Phạm Nhật Vượng).

**Cận dưới đo được (KHÔNG phải đầy đủ) — chỉ 2 case đã có từ báo cáo trước, không tìm thêm được
case thứ 3:**

| Mã | Sự kiện | Khối lượng | % / tổng số CP lưu hành | % / free float |
|---|---|---:|---:|---:|
| VIC | 40 triệu CP VIC làm TSĐB cho 2 lô trái phiếu VHM12605+12606 (4.000 tỷ) | 40.000.000 | **0,52%** | **1,89%** |
| VHM | Chuyển nhượng 15,2 triệu (06/2026) + ~5 triệu (08/2026) CP VHM, lý do công bố "đảm bảo nghĩa vụ thanh toán trái phiếu" | 20.200.000 | **0,49%** | **1,45%** |

Cơ sở tính: VIC ~7,76 tỷ CP lưu hành (suy từ vốn hoá 1.672.751,2 tỷ ÷ giá 215.500đ 12/08/2026,
KHÔNG phải số công bố trực tiếp — coi là ước tính); VHM 4.107.412.004 CP lưu hành (30/09/2025,
Vietstock). Free float dùng lại từ báo cáo trước (VIC 27,32%, VHM 33,81%).

**Đọc con số này thế nào — quan trọng, đừng hiểu nhầm:** 0,5-1,9% nghe NHỎ nhưng đây là **cận
dưới của cận dưới** — chỉ tính các sự kiện ĐÃ công bố công khai và WebSearch tìm ra được, không
phải tổng thể mọi giao dịch cầm cố (ngân hàng nhận thế chấp cổ phiếu thường không công bố nếu
dưới ngưỡng phải báo cáo, và không có cơ chế tổng hợp toàn thị trường). Số liệu bổ sung tìm được
trong job này (KHÔNG có trong báo cáo trước, đáng ghi nhận riêng dù ngoài khung "cầm cố cổ phiếu"):
- **VIC tổng dư nợ vay đạt 357.821 tỷ đồng (Q1/2026)**, lãi suất bình quân **11,1%/năm** — số này
  RỘNG HƠN phần trái phiếu đã đo ở Phần B báo cáo trước (bao gồm cả vay ngân hàng), khớp chiều
  hướng với đòn bẩy cao đã ghi nhận nhưng là chỉ báo QUY MÔ NỢ, không phải tài sản đảm bảo.
- 24/06/2026: HĐQT Vingroup duyệt dùng tài sản của tập đoàn bảo lãnh cho lô trái phiếu Vinhomes
  tối đa 3.000 tỷ, đáo hạn 2029 — **KHÔNG xác nhận được** loại tài sản bảo lãnh có phải cổ phiếu
  hay không (search không cho chi tiết), nên KHÔNG cộng vào bảng cận dưới trên — chỉ ghi nhận có
  thêm 1 giao dịch bảo lãnh cùng mạch, cần xác minh riêng nếu muốn tính vào.
- Không tìm thêm được case nào cho VRE/VPL (2 mã còn lại trong nhóm) — VRE có vay hợp vốn dài hạn
  Techcombank+Deutsche Bank tăng từ 2.523 tỷ lên 6.380 tỷ nhưng không có thông tin cổ phiếu làm
  TSĐB.

**Kết luận (a):** cận dưới đo được ~0,5-1,9% cổ phiếu/free float mỗi mã — nhỏ về tỷ lệ, nhưng là
cận dưới của một hiện tượng không đo được đầy đủ. Muốn có con số tổng hợp thật cần tra công bố
thông tin định kỳ từng đợt trên HOSE/UBCKNN trực tiếp theo mã (ngoài phạm vi 1 job WebSearch) —
nếu user muốn, đây là job riêng, tốn nhiều lượt tra hơn.

---

## (b) Theo dõi định kỳ — đã đủ từ khoá chưa, có sửa gì không

**Đánh giá test nêu trong dispatch: "nếu tin hôm 04-05/08/2026 (~5 triệu CP VHM) xảy ra LẦN NỮA
tuần tới, nhóm từ khoá c) hiện có bắt được không?"**

Nhóm c) (`mike/bin/fearbuy_weekly_scan.sh`, thêm hôm nay commit `38b8c835`) TRƯỚC khi sửa gồm:
`giải chấp cổ phiếu · call margin cổ đông lớn · cầm cố cổ phiếu Vingroup`. Đây là prompt cho 1
agent LLM chạy WebSearch (không phải regex/exact-match) nên về nguyên tắc LLM có thể suy luận
ngữ nghĩa "chuyển nhượng cổ phiếu đảm bảo nghĩa vụ trái phiếu" gần với "cầm cố cổ phiếu" — nhưng
cách diễn đạt công bố thật (nguồn báo 08-2026) dùng đúng cụm **"chuyển nhượng cổ phiếu ... đảm bảo
nghĩa vụ thanh toán trái phiếu"** và **"giao dịch cổ phiếu của tổ chức có liên quan của người nội
bộ"**, khác hẳn 3 cụm sẵn có về mặt từ vựng bề mặt — rủi ro là agent tìm kiếm theo từ khoá LITERAL
trên Google có thể không trúng nếu chỉ query đúng 3 cụm cũ.

**Đã sửa (code change thật, không phải chỉ đánh giá)** — commit `68ff3998`, thêm 2 cụm khớp SÁT
đúng cách công bố thật đã quan sát:
```diff
-      giải chấp cổ phiếu · call margin cổ đông lớn · cầm cố cổ phiếu Vingroup
+      giải chấp cổ phiếu · call margin cổ đông lớn · cầm cố cổ phiếu Vingroup ·
+      chuyển nhượng cổ phiếu đảm bảo nghĩa vụ trái phiếu · giao dịch cổ phiếu người liên quan nội bộ Vingroup
```
Test: `bash -n bin/fearbuy_weekly_scan.sh` → OK. Cùng lý do không chạy full dispatch thật như Phần
A báo cáo trước (chi phí + không đổi logic điều khiển, chỉ thêm text heredoc tĩnh).

## (c) Tần suất giám sát — ĐỀ XUẤT, KHÔNG tự cài

**Hiện trạng đã đủ, không cần cron mới:** script này đã chạy **2 lần/tuần** (Thứ Sáu 08:10 ICT +
Thứ Hai 08:00 ICT, xem `kb/cron_registry.md` dòng 93/99/102/103), không phải 1 lần/tuần như dispatch
mô tả ban đầu. Loại tin "chuyển nhượng cổ phiếu đảm bảo nghĩa vụ trái phiếu" trong dữ liệu đã quan
sát (2 đợt: 06/2026 và 08/2026, cách nhau ~6 tuần) có tần suất tự nhiên ở mức TUẦN-THÁNG, không
phải NGÀY — cadence 2 lần/tuần hiện tại đã đủ để bắt sớm loại tin này với độ trễ tối đa ~3-4 ngày
(khoảng cách 2 lượt chạy Thứ Hai/Thứ Sáu), không cần tăng tần suất.

**Đề xuất (nếu user muốn chặt hơn, KHÔNG tự cài):** nếu lo ngại riêng về tốc độ diễn biến
margin-call (khác với tin công bố định kỳ — margin call có thể diễn ra trong vài giờ-vài ngày),
phương án hợp lý hơn KHÔNG PHẢI tăng tần suất WebSearch scan (chi phí cao hơn, tin margin-call cấp
tốc thường không kịp lên báo trước khi giá đã phản ánh), mà là dựa vào cơ chế giá/khối lượng đã có
sẵn (`anomaly_scan.py` IDIOCRASH/FLOOR2, đã chạy trong CÙNG script mục 1) — đây là kênh phát hiện
NHANH HƠN tin tức cho biến động giá thật, WebSearch chỉ bổ sung NGUYÊN NHÂN. Không đề xuất cron
mới; giữ nguyên 2 lần/tuần hiện tại là đủ cho tín hiệu loại "công bố định kỳ" đang theo dõi.

---

## Tóm tắt cho (d) trong báo cáo trước

1. **Tổng khối lượng cầm cố / free float**: KHÔNG xác minh được số tổng hợp (đúng dự đoán). Cận
   dưới đo được: VIC 40 triệu CP (0,52% tổng/1,89% free float), VHM 20,2 triệu CP (0,49%/1,45%).
   Không tìm thêm case mới cho VRE/VPL. Muốn con số đầy đủ hơn cần job riêng tra HOSE/SSC theo mã.
2. **Theo dõi định kỳ**: ĐÃ đủ hạ tầng (2 lần/tuần), đã bổ sung 2 cụm từ khoá khớp sát cách công
   bố thật (commit `68ff3998`). Không cần cron mới — đề xuất giữ nguyên tần suất, dựa vào
   `anomaly_scan.py` giá/khối lượng cho tốc độ nhanh hơn nếu lo margin-call cấp tốc.
