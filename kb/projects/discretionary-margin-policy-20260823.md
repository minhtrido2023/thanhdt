# Chính sách margin đơn mã cho sleeve fear-buy discretionary
> Chốt 2026-08-23 (user duyệt, sau khi đóng sổ `margin-valuation-spread-20260823.md`).
> Status: **IMPLEMENTED 2026-08-29, sleeve cap RESYNC 2026-08-30** — gate/checker
> `mike/bin/discretionary_margin_gate.py` (arm/exit độc lập với `plan.py`/`executor.py`, KHÔNG
> chạm bot tự trade — sleeve này là quy trình arm TAY + checker exit hằng ngày). Khác
> `capit_margin_lever` (đã LIVE, hệ thống, dd52≤−20%, CAPIT sleeve): đây là **đơn mã,
> discretionary, xét từng case**, không có backtest vì N không thể đủ lớn theo bản chất
> (due-diligence sâu không scale). Quyết bằng rào chắn rủi ro + duyệt người từng ca, không phải
> bằng thống kê.
>
> **RESYNC 2026-08-30 (`decided_by: user`, 11:52 ICT)** — sau
> `agents/Taylor/research/discretionary_sleeve_correlation_risk_20260830.md` (correlation risk
> crisis thật ρ≈0,18-0,25, risk-auditor CONDITIONAL-APPROVE), user chốt:
> - **Sleeve cap tổng: 5% → 10% NAV exposure** (per-name cap GIỮ NGUYÊN 5% NAV, không đổi).
> - **Điều kiện TRIGGER xem xét lại 15%** (không phải tự động nâng): ≥3 case marginable ĐỒNG THỜI
>   THẬT (đã xác nhận marginability qua Mafee cho từng case, không phải giả định/dự phóng) →
>   escalate lên Mike/user để CÂN NHẮC nới 15%. Chưa đủ 3 case thật → KHÔNG tự nâng.
> - Mã hoá trong code: `bin/discretionary_margin_gate.py` `SLEEVE_CAP_PCT = 0.10`. Selfcheck
>   (`bin/discretionary_margin_gate_selfcheck.py`) đã cập nhật test breach mốc 10% mới, 23/23 PASS.
>
> **RESYNC 2026-08-29 (`decided_by: user`, 23:03 ICT)** — sau nghiên cứu lại
> `agents/Taylor/research/discretionary_margin_sizing_20260829.md` (bus finding
> `discretionary-margin-sizing-20260829`), user chốt:
> - **Sleeve cap tổng: GIỮ 5% NAV exposure** (đề xuất nâng 15% bị **REJECT ở thời điểm này** — lý
>   do: chỉ có 2 case biết trước TV1/DGC, không đủ để lấp đầy 15% nếu per-name vẫn ở mức cũ, và
>   nới sleeve một mình gần như vô hại nhưng cũng không giải quyết vấn đề gì thật — xem điều kiện
>   mở lại ở cuối mục "Rào chắn rủi ro").
> - **Per-name: 3% → 5% NAV exposure** (user duyệt, chấp nhận CONDITIONAL-APPROVE của
>   risk-auditor 2026-08-23 ở mức cao hơn).
> - **Exit −20% từ giá arm: giữ nguyên, tự áp** (không đổi, không dựa vào broker).
> - **6 điều kiện cứng bắt buộc** (từ risk-auditor verdict trong research 08-29, đã áp dụng vào
>   mục "Rào chắn rủi ro" dưới + code hoá trong gate): (1) thống nhất cơ sở EXPOSURE cho MỌI %NAV
>   trong cả 2 tài liệu chính sách (mục này + `margin_cap_recovery_forensic_20260825.md`); (2)
>   hard-cap **f=1,3** (đồng quy ước `capit_margin_lever`), KHÔNG dùng broker-max f=2,0; (3) ràng
>   buộc %ADV per-name ≤10% ADV-3-tháng; (4) max-loss công bố per-case ~1,5% NAV cho mã mỏng (đã
>   haircut slippage + lãi vay), không trích 1,0% trần lý thuyết; (5) Mafee verify marginability
>   từng case TRƯỚC khi arm — điều kiện bắt buộc, đã có sẵn ở "Cổng vào" mục 4, gate code enforce
>   lại; (6) re-sync mandate Loại-2 (`kb/projects/discretionary-margin-policy-20260823.md` §"Sleeve
>   Loại-2" dưới) — số đơn mã KHÔNG đổi giá trị neo (Loại-2 vẫn dùng ≤1%/≤3% NAV câu chữ CŨ của
>   08-23, không tự động theo per-name mới 5% — xem note trong mục đó).

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

## Rào chắn rủi ro (risk-auditor 2026-08-23, RESYNC user 2026-08-29 — mọi %NAV dưới đây là
## **EXPOSURE** (giá trị vị thế), KHÔNG phải vốn tự có, trừ khi ghi rõ khác — cùng quy ước với
## `margin_cap_recovery_forensic_20260825.md` sau khi vá §1 file đó)
- **Trần MỘT vị thế (per-name): exposure ≤5% NAV** (đổi từ 3%→5% NAV, `decided_by: user` 08-29,
  chấp nhận CONDITIONAL-APPROVE của risk-auditor). Hard-cap đòn bẩy **f=1,3** (đồng quy ước
  `capit_margin_lever` — KHÔNG dùng f=2,0 broker-max như câu chữ 08-23 từng ngầm định), tức vốn tự
  có tối thiểu ≈76,9% giá trị vị thế cho phần có margin. **Trần cứng tuyệt đối**, kể cả sau khi giá
  tăng (không để lãi tự nới trần). So với name-cap hệ thống 10% NAV — thấp hơn nhiều, đúng lý do
  không có diversification + rủi ro đuôi do due-diligence có thể sai.
- **Ràng buộc %ADV per-name (mới, điều kiện cứng #3 risk-auditor 08-29): exposure ≤10% ADV-3-tháng**
  (trung bình `Trading_Value` 3 tháng gần nhất, đọc từ `data/bq_cache/ticker/<year>.parquet`) —
  ràng buộc THÊM vào trần %NAV, không thay thế. Với mã thanh khoản như TV1 (ADV ~700-840tr/ngày ở
  NAV SpaceX hiện tại), %ADV có thể chặt hơn %NAV; ràng buộc nào chặt hơn quyết định size thật.
  Enforce trong code (`bin/discretionary_margin_gate.py`), không chỉ ghi trong tài liệu.
- **Trần TỔNG sleeve** (tách biệt hoàn toàn với `capit_margin_lever`): mọi vị thế discretionary-có-
  margin đồng thời **≤10% NAV exposure** (nâng từ 5% → 10%, `decided_by: user` 2026-08-30 11:52
  ICT, sau `agents/Taylor/research/discretionary_sleeve_correlation_risk_20260830.md` — correlation
  crisis thật ρ≈0,18-0,25, risk-auditor CONDITIONAL-APPROVE). **Điều kiện TRIGGER xem xét nới 15%**
  (không phải tự động nâng): ≥3 case marginable ĐỒNG THỜI THẬT (Mafee xác nhận marginability cho
  từng case, không phải giả định) trong danh sách QUALIFY → escalate lên Mike/user để CÂN NHẮC —
  chưa đủ 3 case thật thì không tự nâng lại 15%.
- **Max-loss công bố per-case: ~1,5% NAV cho mã mỏng kiểu TV1** (haircut slippage khi thoát trong
  hoảng loạn + lãi vay margin tích luỹ trong thời gian giữ vị thế — KHÔNG trích con số lý thuyết
  1,0% NAV = 5%×20% làm số công bố cho người duyệt, vì đó bỏ qua 2 cấu phần chi phí thật đã biết
  từ research 08-29 §4). Số lý thuyết 1,0% NAV vẫn dùng làm SÀN tính trần equity (xem dưới), chỉ
  khác là số NÓI CHO NGƯỜI DUYỆT nghe phải cộng thêm haircut.
- **PHÁT HIỆN QUAN TRỌNG — margin call của DNSE KHÔNG phải lưới an toàn ở quy mô này**: DNSE netting
  ký quỹ ở CẤP TÀI KHOẢN, không phải cấp vị thế. Ở trần đề xuất, dù vị thế đơn lẻ về −50% (mất trọn
  vốn tự có ~1% NAV), tỷ lệ ký quỹ TOÀN ACCOUNT vẫn ~98% ≫ 40% ⇒ broker KHÔNG can thiệp. Tính RIÊNG
  vị thế đó, nó lẽ ra chạm maintenance (40%) ở **−16,7%** và liquidation (30%) ở **−28,6%** (số này
  ứng với f=2,0 broker-max; ở hard-cap f=1,3 thật của sleeve này, maintenance chạm ở **−61,5%**,
  liquidation ở **−67,0%** — càng xa hơn) — nhưng netting cấp account làm các mốc này vô hiệu trong
  thực tế dù ở f nào. **⇒ Kỷ luật thoát phải TỰ ÁP, không dựa vào broker.**
- **Kỷ luật thoát — BẮT BUỘC, đặt CHẶT hơn ngưỡng lý thuyết**: de-lever bắt buộc tại **−20% từ giá
  lúc arm margin** (trước cả mốc maintenance lý thuyết) **HOẶC** rating 8L tụt >2, mốc nào tới
  trước. **Cấm average-down trên margin** mà không chạy lại due-diligence + fundamental-skeptic từ
  đầu. Checker tự động (`bin/discretionary_margin_gate.py check-exits`, cron hằng ngày) đọc giá DNSE
  mới nhất so với giá arm và alert Discord khi chạm −20% — đây là CẢNH BÁO, quyết định thoát thật
  vẫn là hành động người (không có auto-sell).

## Vận hành
- **Marginability xác nhận TỪNG CASE bởi Mafee TRƯỚC KHI arm** — điều kiện bắt buộc (đã có ở "Cổng
  vào" mục 4), gate code (`discretionary_margin_gate.py arm --marginability-confirmed-by "..."`)
  chặn cứng nếu thiếu field này, không suy đoán marginable từ tên sàn niêm yết.
- Cổng duyệt người mỗi lần arm — sổ riêng `data/discretionary_margin_arms.json`, KHÔNG dùng chung
  file `margin_approval_*` của CAPIT (khác trần, khác cơ chế cấp phép).
- Chỉ account **SpaceX** (có margin); ZaloPay cash-only ngoài phạm vi — gate code chặn cứng account
  khác SpaceX.
- **Implementation HOÀN TẤT 2026-08-29**: `bin/discretionary_margin_gate.py` (subcommand `arm` /
  `check-exits` / `exit` / `list`). KHÔNG chạm `plan.py`/`executor.py`/`trading_rules.json` — đây là
  quy trình arm TAY + checker đọc-only, không phải nhánh cấp phép tự động trong bot (khác
  `capit_margin_lever`, vốn wire thẳng vào cascade `apply_capit_lever`). Selfcheck:
  `bin/discretionary_margin_gate_selfcheck.py`.

## Trạng thái áp dụng hôm nay
- **TV1**: KHÔNG áp dụng — UPCOM, không marginable. Tranche hiện tại (500cp, LO≤20.640) giữ nguyên
  vốn tự có, không đổi.
- **DGC**: ZaloPay EXCLUDED (hạn chế HOSE), SpaceX case cần kiểm marginable trước khi xét.
- Chưa có case nào đủ điều kiện áp dụng ngay — chính sách chờ case tương lai (vd cổ phiếu UPCOM
  uplist HOSE kiểu DRI, hoặc case QUALIFY mới marginable).

## Sleeve Loại-2 washout — CHÍNH SÁCH BỔ SUNG (xác nhận 2026-08-25, user + risk-auditor Spyros)
> Khác chính sách đơn mã trên: áp cho **portfolio-level**, khi cả thị trường vào Loại-2 Bobby.
> Cơ sở số: `margin_cap_recovery_forensic_20260825.md` (Taylor A5) + Spyros CONDITIONAL-APPROVE.
> Framework đầy đủ: `crisis_margin_framework_adaptive_20260825.md`.
> **ĐÍNH CHÍNH 2026-08-29** (research `discretionary_margin_sizing_20260829.md` §1, `decided_by:
> user`): công thức A5 gọi nhầm `equity_cap` là cơ sở tính `equity_loss(d) = exposure_0 × |d|` —
> đúng ra phải nhân với **exposure_cap**, không phải equity_cap, vì biến động giá dồn hết vào vốn
> tự có bất kể f. Ở f=1,3: exposure_cap = 5%×1,3 = 6,5% NAV ⇒ max loss thật tại exit −20% =
> **6,5%×20% = 1,3% NAV**, KHÔNG PHẢI 1,0% NAV như công bố gốc (thiếu 30%). Sửa số dưới.

- **Trần equity sleeve tổng: ≤5% NAV vốn tự có** (GIỮ NGUYÊN giá trị — không đổi bởi resync 08-29).
- **Trần exposure: ≤6,5% NAV** (= 5% × f=1,3 của `capit_margin_lever` thật — KHÔNG phải ≤5% exposure)
- **Max loss thật tại exit −20%: 1,3% NAV** (= exposure_cap 6,5% × 20% — SỬA từ 1,0% NAV, xem đính
  chính trên; công thức `equity_cap×20%` gốc chỉ đúng khi equity_cap≡exposure_cap, tức f=1, không
  phải trường hợp của sleeve này).
- **Bobby confidence "ambiguous" → size giảm 50%** (≤2,5% NAV equity): bắt case 2018-style
- **Exit −20% từ arm là intent, không phải guaranteed price** — basket CAPIT trong panic có slippage
- **Payload escalate PHẢI có combined exposure field** (main V2.4 + sleeve đề xuất vs allocation bình
  thường — người duyệt cần thấy tổng, không chỉ sleeve đơn lẻ)
- Chỉ SpaceX (margin account); KHÔNG code vào production cho đến khi có task triển khai riêng
- **RE-SYNC 2026-08-29 — mandate Loại-2 KHÔNG tự động kế thừa per-name mới của chính sách đơn mã**
  (per-name 3%→5% NAV exposure ở mục "Rào chắn rủi ro" trên): mục "Trần đơn mã (nếu chọn từng mã
  riêng trong basket)" của `margin_cap_recovery_forensic_20260825.md` §A5 TRÍCH DẪN trực tiếp số
  per-name 08-23 (1%/3%) làm cơ sở neo — số per-name đơn mã đã đổi (nay 5% NAV exposure) nhưng
  trần Loại-2 GIỮ NGUYÊN giá trị NEO CŨ theo quyết định user 08-29 (lý do: Loại-2 chưa được
  risk-auditor/user duyệt lại với số per-name mới — đổi ngầm sẽ để 2 tài liệu lệch nhau, `decided_by:
  user`). Muốn đổi trần Loại-2 theo per-name mới cần MỘT vòng risk-auditor + user riêng, không tự
  suy diễn từ resync này.

## Liên quan
- `dgc-tv1-fearbuy-discretionary.md` — nguồn case QUALIFY, lịch sử đảo verdict 2 lần.
- `margin-valuation-spread-20260823.md` §"Hướng còn mở" — đề xuất gốc dẫn tới chính sách này.
- `kb/incidents/` postshock_base_formation (Taylor, cùng ngày) — lý do không backtest bộ lọc thô.
- `kb/data_registry/trading-bot/dnse_openapi_v2_calling_guideline.md` — số margin gói 1840 thật.
- `crisis_margin_framework_adaptive_20260825.md` — framework 3 điều kiện + payload escalate đầy đủ.
- `margin_cap_recovery_forensic_20260825.md` — cơ sở trần mới + forensic recovery-entry (NO-GO).
