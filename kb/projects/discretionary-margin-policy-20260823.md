# Chính sách margin đơn mã cho sleeve fear-buy discretionary
> Chốt 2026-08-23 (user duyệt, sau khi đóng sổ `margin-valuation-spread-20260823.md`).
> Status: **POLICY DUYỆT — CHƯA CODE, CHƯA WIRE.** Khác `capit_margin_lever` (đã LIVE, hệ thống,
> dd52≤−20%, CAPIT sleeve): đây là **đơn mã, discretionary, xét từng case**, không có backtest vì
> N không thể đủ lớn theo bản chất (due-diligence sâu không scale). Quyết bằng rào chắn rủi ro +
> duyệt người từng ca, không phải bằng thống kê.

## Nguồn gốc — vì sao KHÔNG backtest được
Cùng ngày, `postshock-base-formation` (Taylor) test đúng ý tưởng "sập nhanh + rating vẫn ổn (lọc thô
8L) = tạo đáy" trên 1.614 sự kiện — kết quả **excess return ÂM mọi khung** (H60 −5,9% / H120 −8,8% /
H250 −20,1%), kể cả nhóm RATING_OK. REFUTED, đóng sổ cùng ngày.

Khác biệt làm chính sách này KHÔNG bị bác bỏ bởi kết quả trên: bộ lọc thô (chỉ rating số) không phân
biệt được "hoảng loạn phi lý" với "doanh nghiệp thật sự xấu đi" — quy trình fear-buy discretionary
(DGC/TV1) có thêm **due-diligence sâu + fundamental-skeptic phản biện** để làm đúng việc đó. Nhưng
due-diligence sâu không scale ra hàng trăm ca lịch sử, và phân loại hồi tố luôn nhiễm hindsight bias
(người phân loại đã biết kết quả) — nên đây LÀ câu hỏi chính sách/underwriting, không phải câu hỏi
định lượng như margin-theo-spread vừa đóng.

## Cổng vào — MỌI điều kiện đều bắt buộc
1. **QUALIFY** qua quy trình fear-buy discretionary hiện có (`calculated_fear_state_backstop.md`).
2. **fundamental-skeptic CONFIRMED** — không dùng verdict sơ bộ một mình (tiền lệ: DGC/TV1 đã đảo
   verdict 2 lần, xem `dgc-tv1-fearbuy-discretionary.md` — anchoring-bias là rủi ro THẬT, không giả định).
3. **Rating 8L ≤2 XÁC NHẬN LẠI SAU sự kiện** (không dùng rating trước cú sốc — có thể đã stale).
4. **Marginable trên DNSE xác nhận TỪNG CASE** (không phải điều kiện tiên quyết loại bỏ ý tưởng —
   TV1 hiện tại ở UPCOM nên KHÔNG áp dụng được ngay, nhưng case tương lai uplist HOSE (kiểu DRI) hoặc
   case mới trên HOSE/HNX marginable sẽ đủ điều kiện).

## Rào chắn rủi ro (risk-auditor, 2026-08-23, neo số NAV SpaceX thật 977,1tr ngày 2026-08-21)
- **Trần MỘT vị thế**: vốn tự có ≤1,0% NAV (khớp mức Taylor tự chốt cho case QUALIFIED unlevered),
  đòn bẩy gói 1840 (initial 50%) → exposure tối đa ≈2,0% NAV, **trần cứng tuyệt đối 3% NAV** kể cả
  sau khi giá tăng (không để lãi tự nới trần). So với name-cap hệ thống 10% NAV — thấp hơn nhiều,
  đúng lý do không có diversification + rủi ro đuôi do due-diligence có thể sai.
- **Trần TỔNG sleeve** (tách biệt hoàn toàn với `capit_margin_lever`): mọi vị thế discretionary-có-
  margin đồng thời ≤5% NAV exposure, tổng dư nợ vay ≤2,5% NAV (~tối đa 2 case song song ở trần).
- **PHÁT HIỆN QUAN TRỌNG — margin call của DNSE KHÔNG phải lưới an toàn ở quy mô này**: DNSE netting
  ký quỹ ở CẤP TÀI KHOẢN, không phải cấp vị thế. Ở trần đề xuất, dù vị thế đơn lẻ về −50% (mất trọn
  vốn tự có ~1% NAV), tỷ lệ ký quỹ TOÀN ACCOUNT vẫn ~98% ≫ 40% ⇒ broker KHÔNG can thiệp. Tính RIÊNG
  vị thế đó, nó lẽ ra chạm maintenance (40%) ở **−16,7%** và liquidation (30%) ở **−28,6%** — nhưng
  netting cấp account làm 2 mốc này vô hiệu trong thực tế. **⇒ Kỷ luật thoát phải TỰ ÁP, không dựa
  vào broker.**
- **Kỷ luật thoát — BẮT BUỘC, đặt CHẶT hơn ngưỡng lý thuyết**: de-lever bắt buộc tại **−20% từ giá
  lúc arm margin** (trước cả mốc maintenance lý thuyết −16,7%) **HOẶC** rating 8L tụt >2, mốc nào tới
  trước. **Cấm average-down trên margin** mà không chạy lại due-diligence + fundamental-skeptic từ đầu.

## Vận hành
- Cổng duyệt người mỗi ngày có vị thế margin discretionary — tái dùng pattern `approve_margin_day.py`
  (không dùng chung file với CAPIT — sổ riêng, trần riêng).
- Chỉ account **SpaceX** (có margin); ZaloPay cash-only ngoài phạm vi.
- Implementation (code, wire vào `plan.py`/`executor.py`) là bước RIÊNG, cần rigor tương đương
  `capit_margin_lever` (selfcheck, arch-review vì chạm execution path) — **CHƯA làm trong lượt này**,
  chỉ chốt chính sách + rào chắn số. Không code trước phiên giao dịch Thứ Hai 24/08 để tránh rủi ro
  thay đổi execution path sát giờ mở cửa không kịp test kỹ.

## Trạng thái áp dụng hôm nay
- **TV1**: KHÔNG áp dụng — UPCOM, không marginable. Tranche hiện tại (500cp, LO≤20.640) giữ nguyên
  vốn tự có, không đổi.
- **DGC**: ZaloPay EXCLUDED (hạn chế HOSE), SpaceX case cần kiểm marginable trước khi xét.
- Chưa có case nào đủ điều kiện áp dụng ngay — chính sách chờ case tương lai (vd cổ phiếu UPCOM
  uplist HOSE kiểu DRI, hoặc case QUALIFY mới marginable).

## Liên quan
- `dgc-tv1-fearbuy-discretionary.md` — nguồn case QUALIFY, lịch sử đảo verdict 2 lần.
- `margin-valuation-spread-20260823.md` §"Hướng còn mở" — đề xuất gốc dẫn tới chính sách này.
- `kb/incidents/` postshock_base_formation (Taylor, cùng ngày) — lý do không backtest bộ lọc thô.
- `kb/data_registry/trading-bot/dnse_openapi_v2_calling_guideline.md` — số margin gói 1840 thật.
