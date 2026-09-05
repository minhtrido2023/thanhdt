# Đề cương nghiên cứu — Conditional Conviction Sizing (CCS)
> Mike soạn 2026-09-05, theo yêu cầu user (Discord 20:18 ICT). Trạng thái: PROPOSAL — chờ user duyệt trước khi dispatch Taylor.

## 1. Bối cảnh — vì sao đặt lại cách tiếp cận là ĐÚNG với lịch sử research của chúng ta

Kiến trúc production hiện tại (V2.4, live từ 2026-07-01):
- **2 book hệ thống**: BAL (momentum SIGNAL_V11 + yieldcombo 1/PE+1/PCF) + LAG (PEAD/earnings drift). Allocator w_LAG theo regime {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}.
- **DT5G** = chốt rủi ro fail-safe (cap trần trạng thái), KHÔNG phải công cụ tăng lợi nhuận — toàn bộ edge ròng từ 1 lần siết 2023, năm bull 2025 tốn −0,89pp.
- **CAPIT** = sleeve washout riêng, là chỗ DUY NHẤT margin đã qua được gate: `capit_margin_lever` LIVE 08-24, điều kiện dd52 ≤ −20%, trigger cấp SỰ KIỆN/CỔ PHIẾU chứ không phải cấp regime.
- **Sleeve discretionary** (DGC/TV1-style): per-name ≤5% NAV, sleeve ≤10% NAV, f≤1,3, exit −20% — hạ tầng margin đơn mã ĐÃ WIRED (commit 022c48e7, phễu 714b5889).
- **AlphaLens paper**: FPT/ACB/MBB/HDB, tracking đến 2026-09-30.

Lịch sử margin cấp REGIME — cả 3 lần đều NO-GO, kết luận nhất quán:
1. **V2.5 leverage** (lever MGE=1.5 theo regime): NO-GO 07-12 — edge là IS-artifact.
2. **Margin theo khoảng cách định giá** (valuation-spread sizing): NO-GO 08-23 — nhiễu harness 0,385pp ≫ hiệu ứng 0,009pp, 5 vòng + quant-skeptic.
3. **Crisis sleeve Loại-2**: chỉ mở đường ESCALATE có điều kiện (Bobby blind + PIT + overreaction), không auto.

Nhưng khi đóng margin-valuation-spread, chính chúng ta đã ghi: **"hướng mở duy nhất = margin cấp CỔ PHIẾU trong sleeve fear-buy"**. Đề xuất của user hôm nay chính là tổng quát hoá hướng mở đó: thay vì hỏi "KHI NÀO cả danh mục nên dùng margin" (đã bác 3 lần), hỏi "**TRADE NÀO trong các book hiện có xứng đáng sizing cao hơn, và Ở TRẠNG THÁI THỊ TRƯỜNG NÀO**" — đúng cấu trúc đã cho CAPIT qua gate.

## 2. Câu hỏi nghiên cứu

> Trong các entry mà BAL / LAG / AlphaLens ĐÃ tạo ra (không đổi logic chọn), có tồn tại **discriminator ex-ante, PIT** nào tách được nhóm entry có win-rate/expectancy cao hơn phần còn lại một cách bền OOS không? Nếu có, **overlay sizing** (tăng tỷ trọng nhóm đó, giảm phần còn lại — chưa cần margin) có cải thiện CAGR/Calmar so với pin R3 28,86% vượt sàn nhiễu harness ~0,4pp không? Và chỉ SAU KHI cash-only survive mới hỏi tiếp: biến thể margin f≤1,3 trong trạng thái được duyệt có đáng không?

## 3. Bẫy đã biết — thiết kế phải né TỪ ĐẦU

1. **Các tilt ĐÃ BỊ BÁC không được chạy lại dưới dạng vô điều kiện**: LAG SUE-tilt 3 tầng (−0,66pp), composite v3 entry-selector (NO), gq_score gate (−IC), liq-tilt custom30 (REFUTED), stability floor (−0,45pp), deep-discount sleeve (PARKED). Điểm MỚI duy nhất được phép test là **tương tác với market state** (conditional ≠ unconditional — câu hỏi khác).
2. **Multiple testing**: trade-feature × state là tổ hợp nổ. → Pre-register TOÀN BỘ hypothesis trước khi nhìn số (danh sách §5), khai N trials, DSR ≥ 0,95, PBO < 0,5, per-year leave-one-out.
3. **N độc lập ≠ số trade**: trade cụm theo ngày/regime. Đếm N theo EPISODE độc lập; bucket < ~30 episode → chỉ mô tả, không kết luận.
4. **Sàn nhiễu harness 0,385pp** (đo thật ở margin-valuation-spread): hiệu ứng < ~0,4pp CAGR = coi như 0.
5. **Chữ ký reshuffle-luck**: edge dồn vào 2020-2021 = loại (per-year LOO bắt buộc).
6. **PIT tuyệt đối**: universe_pit, breadth t−1, cấm mọi cột `profit_*`; trục 2 mặc định = breadth-tercile PIT (quy ước 08-22).
7. **Capacity**: nhóm được upsize vẫn phải qua %ADV cap hiện có; nhớ caveat mô hình fill 20% ADV chưa neo (lag-adv-filter đang tracking đến 12-15).

## 4. Thiết kế — 4 phase, gate cứng giữa các phase

### Phase 0 — Trade ledger + feasibility (Taylor, ~1 dispatch)
Trích từ harness R3 (đúng config pin, universe_pit, threads=1) **bảng per-trade**: mỗi entry của BAL/LAG với feature PIT tại ngày vào — book, rank/score tín hiệu, 1/PE tercile, 8L rating, dd52 của mã, %ADV, sector, DT5G state, breadth-tercile (t−1), tuổi tín hiệu — và outcome (return tới exit, R-multiple, holding days). AlphaLens: chỉ descriptive (N=4 mã, không đủ thống kê).
**Gate ra**: bảng tồn tại + self-check tổng NAV khớp pin 0 VND + đếm N episode độc lập per bucket. Không đủ N → dừng, báo lại.

### Phase 1 — Conditional expectancy map (Taylor + Bobby độc lập)
Win-rate / expectancy / avg-R cho TỪNG hypothesis pre-registered (§5), cắt theo DT5G-state × breadth-tercile. Bobby (macro-strategist) đọc các cửa sổ "upsize được" ĐỘC LẬP, KHÔNG cho xem forward-return trước (bài học margin-valuation-spread §Đính chính — tránh đồng thuận sớm).
**Gate ra**: tối đa 2-3 hypothesis sống (IS + OOS cùng dấu, N đủ, không dồn 1-2 năm).

### Phase 2 — Overlay sizing CASH-ONLY (không margin)
Với hypothesis sống: backtest **reallocation nội book** — nhóm conviction nhận trọng số ×k (k∈{1,25; 1,5}), phần còn lại giảm tương ứng, tổng exposure KHÔNG đổi. Tách bạch "chọn đúng chỗ dồn tiền" khỏi "vay thêm tiền".
**Gate ra**: ΔCAGR > +0,4pp (sàn nhiễu), Calmar không xấu đi, IS/OOS cùng dấu, DSR/PBO đạt, quant-skeptic CONFIRMED.

### Phase 3 — Biến thể margin (CHỈ nếu Phase 2 survive)
Nhóm conviction được phép f≤1,3 trong đúng các state đã map ở Phase 1, tái dùng NGUYÊN hạ tầng discretionary-margin-policy (trần per-name 5% / sleeve 10% NAV exposure, exit −20%, %ADV≤10%) — không xây cơ chế mới. Sau đó: paper tracking ≥1 quý trước khi bàn wire; wire cần user duyệt như mọi thay đổi production.

## 5. Hypothesis pre-registered (chốt TRƯỚC khi nhìn số — N trials = 6)

| # | Discriminator (PIT tại entry) | Cơ sở tiên nghiệm |
|---|---|---|
| H1 | dd52 của mã ≤ −20% tại entry (washout cấp mã, CAPIT-analog trong BAL/LAG) | Cơ chế duy nhất đã qua gate margin; overreaction cấu trúc thị trường 90% retail |
| H2 | 1/PE tercile rẻ nhất × trạng thái recovery (BEAR→NEUTRAL upgrade hoặc breadth thoát tercile đáy) | Conviction đã ghi của user: edge bất đối xứng = recovery + cheap; 1/PE IC +0,125 dominant |
| H3 | Breadth-tercile đáy → quay đầu (t−1) | Trục 2 canonical; recovery timing |
| H4 | LAG: độ lớn surprise tercile cao × 1/PE rẻ (TƯƠNG TÁC — khác SUE-tilt vô điều kiện đã bác) | PEAD mạnh hơn khi định giá chưa phản ánh |
| H5 | DT5G vừa upgrade (≤10 phiên sau commit lên state cao hơn) | Cam kết bất đối xứng của DT-gate: ra khỏi phòng thủ là tín hiệu giá đã xác nhận |
| H6 | Rank score tín hiệu tercile đầu trong book (conviction nội tại của chính signal) | Kiểm tra rẻ nhất: signal tự xếp hạng có thông tin sizing không |

Ngoài 6 hypothesis này KHÔNG thêm trong lúc chạy; muốn thêm = amend đề cương + tăng N trials công khai.

## 6. Chi phí & mốc
- Phase 0: 1 dispatch Taylor (~1 buổi). Phase 1: 1 dispatch Taylor + 1 Bobby song song. Phase 2: 1-2 dispatch. Phase 3: chỉ khi survive.
- Mỗi phase ghi bus finding riêng; quant-skeptic bắt buộc trước mọi kết luận Phase 2/3.
- Kỳ vọng thực tế: xác suất cao nhất là chỉ 1-2 hypothesis sống đến Phase 2 (lịch sử tilt của chúng ta khắc nghiệt) — nhưng H1/H2 có cơ sở cấu trúc mạnh nhất vì cùng cơ chế với CAPIT đã qua gate.

## 7. Điều KHÔNG nằm trong scope
- Không đổi logic chọn tín hiệu của BAL/LAG (không phải entry-selector mới).
- Không re-tune DT5G, không đổi allocator w_LAG.
- Không auto-trade margin: mọi kích hoạt margin thật vẫn qua approve_margin_day / escalate như hiện hành.
