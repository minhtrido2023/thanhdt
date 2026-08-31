---
kind: registry
status: CANONICAL
source: macro-strategist (native agent) — độc lập với Taylor/backtest, đọc BLIND đến forward-return
group: market-state
writer: macro-strategist, dispatch từng episode, một entry/episode
role: Sổ phân loại NGUYÊN NHÂN VĨ MÔ của mỗi episode khủng hoảng VNINDEX (2 trục: STRUCTURAL vs
  CONFIDENCE/LIQUIDITY; nếu CONFIDENCE — CONTAINABLE vs EXTERNAL-CYCLE) — tách biệt khỏi việc chạy
  backtest để không bị "outcome shape the read" (xem MIKE.md routing table, sự cố 2026-08-24)
last_full_analysis: 2026-08-25 (Bobby — phân tích toàn diện 2000-2026, thêm 5 episode mới)
last_update: 2026-08-30 (Bobby — bản đồ pha trong-năm 2009/2018 ở file con vn_macro_regime_history_2009_2018_phases.md; ĐÍNH CHÍNH trục 2 EP-2018-01 CONTAINABLE→EXTERNAL_CYCLE)
last_update_2: 2026-08-31 (Bobby — addendum granular cửa sổ 2008Q4-2009Q3: đường lãi suất SBV theo ngày, tín dụng 37,53% vs mục tiêu 21-23%, CPI YoY tháng qua cpi_vn.py, FDI 7T/2009; XÁC NHẬN LẠI EP-2008-09 MIXED/EXTERNAL_CYCLE, không đổi verdict)
last_update_3: 2026-08-31 (Bobby — 5 episode mới, BLIND, dispatch riêng: EP-2014-09 OPEC/oil CONFIDENCE_LIQUIDITY/EXTERNAL_CYCLE clean; EP-2015-07 China devaluation CONFIDENCE_LIQUIDITY ambiguous/EXTERNAL_CYCLE clean; EP-2023-09 FX-defense/margin/VIC-VHM CONFIDENCE_LIQUIDITY clean/CONTAINABLE dominant+EXTERNAL_CYCLE phụ ambiguous; EP-2025-03 Liberation Day tariff CONFIDENCE_LIQUIDITY clean/CONTAINABLE(tranh chấp)+EXTERNAL_CYCLE(nền) ambiguous; EP-2026-01 credit/BĐS+chiến tranh dầu MIXED ambiguous, N/A trục 2 hai timeline — nghi vấn CHƯA XÁC NHẬN liên hệ với episode 07/2026 đã có trong fleet)
---

# VN Macro Regime History — sổ phân loại nguyên nhân vĩ mô từng episode khủng hoảng

**Status: CANONICAL.** Đây là sổ DUY NHẤT ghi lại kết luận đọc-vĩ-mô-độc-lập cho từng episode
khủng hoảng VNINDEX dùng trong backtest/margin-timing của Taylor. Quy tắc nền tảng (xem
`~/.claude/agents/macro-strategist.md`): **agent phân loại KHÔNG BAO GIỜ được biết forward-
return/kết quả backtest của episode đang đọc** — chỉ biết ngày + hành động giá đã kích hoạt
episode đó (arm/trigger date, dd52 threshold). Vi phạm quy tắc này là chính sự cố 2026-08-24
khiến vai trò này ra đời.

> **File con (2026-08-30):** `vn_macro_regime_history_2009_2018_phases.md` — bản đồ pha TRONG-NĂM
> 2009 & 2018 + bộ chỉ báo real-time (tần suất/độ trễ), phân biệt PIT vs hindsight.

## Khung phân loại (tóm tắt, đầy đủ ở agent definition)
- **Trục 1 — Root cause**: `STRUCTURAL` (CPI/tín dụng nội địa đã xấu đi NHIỀU QUÝ trước episode,
  cần 1.5-3+ năm siết chính sách để giải quyết) hay `CONFIDENCE_LIQUIDITY` (trigger cụ thể — bank
  run, scandal 1 công ty, dòng vốn ngoại rút, đại dịch, hoảng loạn thị trường ngoài VN — KHÔNG tự
  nó là bằng chứng mất cân đối vĩ mô nội địa)?
- **Trục 2** (chỉ áp dụng nếu trục 1 = `CONFIDENCE_LIQUIDITY`): `CONTAINABLE` (giải quyết bằng
  MỘT hành động chính sách nhắm đúng mục tiêu, tuần-tháng) hay `EXTERNAL_CYCLE` (gắn xu hướng bên
  ngoài VN không kiểm soát được, không có mốc VN tự quyết được thời điểm kết thúc)?
- **Confidence**: `clean` (bằng chứng đồng thuận nhiều chỉ tiêu độc lập) hay `ambiguous` (bằng
  chứng trộn lẫn — vẫn là câu trả lời hợp lệ, không phải thất bại).

---

## BẢN ĐỒ MACRO REGIME TỔNG THỂ 2000-2026

| Giai đoạn | Tên | Trạng thái | GDP YoY | CPI | Đặc điểm chính |
|---|---|---|---|---|---|
| 2000-2006 | Ổn định hậu Đổi Mới, chuẩn bị WTO | GROWTH | 6.2-7.5% | 3-9% | Tín dụng tăng trưởng bình thường, SBV phục hồi thể chế |
| 2007-2008 | Sốt tín dụng hậu WTO, lạm phát bùng nổ | CRISIS | 6.2-8.5% | 8-23% | Tín dụng 53%, CA thâm hụt -12% GDP, CPI đỉnh 23.1% |
| H2 2008-H1 2009 | Khủng hoảng tài chính toàn cầu chồng chéo | CRISIS+EXTERNAL | 3.9-6.2% | 2-23% | Lehman Shock, xuất khẩu sụt, kích thích tài khóa bắt đầu |
| 2009-2012 | Sóng lạm phát thứ 2 + khủng hoảng ngân hàng | CRISIS | 5.0-6.8% | 6-23% | Kích thích 5% GDP → tín dụng tái bùng nổ → NPL 17% |
| 2013-2016 | Tái cơ cấu ngân hàng, ổn định dần | RECOVERY | 5.4-6.7% | 0.6-6.6% | VAMC, giải quyết NPL, CPI về gần 0% (2015) |
| 2016-2019 | Tăng trưởng chế tạo/FDI, vĩ mô bình thường | GROWTH | 6.2-7.5% | 2-4% | FDI bùng nổ, xuất khẩu điện tử, CA thặng dư |
| 2020-2021 | COVID đại dịch, rồi sóng Delta | EXTERNAL/RECOVERY | -6%(Q3'21)/+2.9%(2020) | 1.8-3.2% | Lockdown cứng Q3 2021, SBV cắt lãi suất 150-200bp |
| 2022 | Sốc SCB+Fed+TPDN, áp lực tỷ giá | STRESS | 8.0% | 3.16% | Vụ Trương Mỹ Lan, TPDN đóng băng, SBV nâng lãi +200bp |
| 2023-2024 | Nới lỏng tiền tệ, phục hồi dần | RECOVERY | 5.0-7.1% | 3.2-4.1% | SBV cắt 4 lần 2023 (-150bp), xuất khẩu phục hồi |
| 2025-2026 | Tăng trưởng cao, tín dụng lành mạnh | GROWTH | 7.8-8.0% | 3.2% | GDP 8.02% (2025), tín dụng 18%, không có stress rõ ràng |

---

## PHÂN TÍCH CHUỖI KHỦNG HOẢNG 2007-2012: ĐỘC LẬP HAY SÓNG LIÊN TIẾP?

### Kết luận chính (đọc trước các entry chi tiết)

**Ba "episode" 2007-2008, 2009-2011, và 2011-2013 KHÔNG phải các khủng hoảng độc lập. Chúng là
BA SÓNG LIÊN TIẾP của MỘT cuộc khủng hoảng cơ cấu duy nhất kéo từ đầu 2007 đến cuối 2012.**

Lý do kết luận này quan trọng: nếu đếm là 3 episode độc lập, N = 3 (cộng thêm 2020, 2022 = N=5),
toàn bộ phân tích thống kê so sánh các loại "khủng hoảng ngắn vs dài" sẽ có N_effective thấp hơn
nhiều (khoảng 3-4 cụm độc lập, không phải 5-7).

**Bằng chứng liên tục cơ cấu — giữa Wave 1 và Wave 2 KHÔNG có giai đoạn về "trạng thái bình thường
cơ cấu":**
1. **NPL từ vay 2007-2010 CHƯA được xử lý trong giai đoạn 2009 (tạm lắng).** Báo cáo SBV 2012 xác
   nhận NPL hệ thống đạt 17.21% cuối Q3 2012 — toàn bộ do các khoản vay từ giai đoạn tăng trưởng
   tín dụng 2007-2010 (bất động sản, xây dựng). Không có cơ chế nào xử lý được khối nợ xấu này
   trong giai đoạn "tạm ổn" 2009.
2. **Kích thích tài khóa 2009 (~5% GDP, US$8 tỷ) BÔI THÊM lên imbalance cũ**, không giải quyết nó.
   Tín dụng tái bùng nổ: +36% (2009), +32.4% (2010). Đây là nguyên nhân trực tiếp của làn sóng lạm
   phát thứ 2 (CPI 23% tháng 08/2011).
3. **Đô la hóa và vàng hóa (dollarization/goldization) không giảm trong giai đoạn 2009.** Trái lại,
   người dân mất niềm tin vào VND khi VND bị phá giá nhiều lần (2008-2010), dẫn đến tích lũy USD/vàng
   tiếp diễn — bằng chứng imbalance cơ cấu vẫn nguyên vẹn.
4. **Quy trình giải quyết cơ cấu thật (Decision 254/2012 + VAMC 2013) chỉ BẮT ĐẦU từ 2012-2013**,
   nghĩa là từ 2007-2012 VN không bao giờ thực sự rời khỏi trạng thái "imbalance chưa giải quyết".

**Tiêu chí kiểm tra "có thật sự về bình thường không":** Nếu giữa 2 episode mà SBV CÓ THỂ cắt lãi
suất và tín dụng tái tăng mà KHÔNG tái tạo inflation ngay → đó là bình thường thực sự. Giai đoạn
2009: SBV cắt lãi suất → tín dụng tái tăng → CPI leo lại ngay lập tức → KHÔNG phải bình thường thực
sự, chỉ là "tạm lắng khi commodity giá toàn cầu giảm sau Lehman Shock".

**Kết luận N_effective:**
- Mega-cú sốc STRUCTURAL 2007-2012: 1 episode (không phải 3)
- COVID 2020-2021: 1 episode
- SCB/Fed-hiking 2022: 1 episode
- Điều chỉnh thị trường 2018: ambiguous (không đến mức "khủng hoảng macro")
- **N_effective ≈ 3 (có thể 4 nếu tính 2018) — không phải 5-7.**

---

## EP-2007-01 — WTO Credit Boom to Structural Overheating (Wave 1 of 2007-2012 mega-episode)

**Cửa sổ episode:** 01/2007 (tín dụng và dòng vốn bùng nổ sau WTO) → 09/2008 (CPI đỉnh, SBV siết
cực đại). Đây là Wave 1 của cụm khủng hoảng cơ cấu 2007-2012.

**Trigger đã biết PIT:** VN gia nhập WTO chính thức 11/01/2007 → dòng vốn ngoài (FDI + portfolio)
ồ ạt vào → tín dụng tăng 53-54% trong năm 2007 (nguồn IMF/World Bank: gấp 3-4 lần mức bình thường)
→ giá bất động sản và chứng khoán bong bóng → CPI leo từ 8.36% (2007) lên 22.97% (2008).

### Trục 1: `STRUCTURAL` — confidence: **clean**

- **Tín dụng tăng trưởng 53-54% năm 2007** — gấp 3-4 lần target bình thường, không bị kiểm soát.
  Nguồn: [IMF/World Bank Vietnam economic reports 2007-2008]; World Bank "Taking Stock" Dec 2008.
- **CPI xấu đi nhiều quý TRƯỚC điểm nhận ra:** Lạm phát leo dần từ Q3 2007 (YoY ~7%) → Q1 2008 (YoY
  ~16%) → đỉnh 08/2008 (23.1%), không phải cú nhảy đột ngột — đúng mẫu STRUCTURAL.
  Nguồn: GSO/Trading Economics Vietnam Inflation Rate.
- **Thâm hụt tài khoản vãng lai -9.9% GDP (2007) → -11.7% GDP (2008)** — dấu hiệu tích lũy mất cân
  đối nhiều năm, không phải biến động tạm thời. Nguồn: IMF WEO Oct 2008.
- **Tín dụng ngân hàng cổ phần nhỏ (JSBs) tăng ~100%** trong giai đoạn này — không được SBV kiểm
  soát đủ, bơm tiền vào bất động sản và chứng khoán. Nguồn: World Bank/ADB Vietnam assessment.
- **SBV tăng lãi suất từ 7.5% → 13% chỉ trong 1 tháng (04→05/2008)** — độ dốc phản ứng cho thấy
  mức độ overheating đã tích lũy mà SBV cần phản ứng mạnh. Nguồn: MacroMicro/CEIC Vietnam Refi Rate.
- **VN-Index đạt đỉnh ~1,170 điểm tháng 3/2007 rồi mất >70% đến tháng 11/2008** — bong bóng tài sản
  đồng thời với tín dụng, phù hợp mẫu STRUCTURAL domestic excess. Nguồn: World Bank 2008 cited above.

**Kết luận trục 1:** CPI, tín dụng, và tài khoản vãng lai đều xấu đi nhiều quý TRƯỚC episode —
đây là overheating tích lũy nội địa, không phải cú sốc niềm tin bên ngoài. ⇒ `STRUCTURAL`.

### Trục 2: Không áp dụng (STRUCTURAL tự thân là MULTI_YEAR)

Bằng chứng về thời gian giải quyết: banking NPL từ thời kỳ này chỉ được đưa vào VAMC từ 07/2013,
xử lý kéo dài đến 2015-2016. Tổng thời gian: 2007 (bùng nổ) → 2015-2016 (banking NPL về mức an
toàn) = **8-9 năm**. Riêng giai đoạn lạm phát cao (CPI>10%) kéo 2007→2013 = 6 năm.

### Tổng kết EP-2007-01
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `STRUCTURAL` | clean |
| 2. Resolution type | `MULTI_YEAR_STRUCTURAL` | clean |

- **shock_origin:** 01/2007 (WTO accession + capital inflow surge)
- **policy_response_start:** 04/2008 (SBV bắt đầu nâng refi rate mạnh)
- **recovery_confirmed:** 2013 (CPI về <7%) / 2015 (hệ thống tín dụng về bình thường)
- **chain_classification:** `WAVE_OF:MEGA_2007_2012` (Wave 1)

---

## EP-2008-09 — Global Financial Crisis External Overlay (Compound with Wave 1)

**Cửa sổ episode:** 09/2008 (Lehman Brothers sụp đổ) → 06/2009 (xuất khẩu bắt đầu phục hồi, GDP
tăng tốc lại). Đây là cú sốc NGOẠI kết hợp với khủng hoảng STRUCTURAL đang diễn ra.

**Trigger đã biết PIT:** Lehman Brothers bankruptcy 15/09/2008 → global demand collapse → Vietnam
exports fell -7.7% in 2009 from 2008 peak → GDP slowed to 6.2% (2008) → 5.3% (2009). Chính phủ VN
phản ứng bằng gói kích thích tài khóa US$8 tỷ (~5% GDP), bắt đầu Q4 2008.

### Trục 1: `MIXED` — confidence: **clean** cho phân loại MIXED

Đây là episode HIẾM có 2 lớp nguyên nhân chồng chéo nhau:
- **Lớp 1 (cơ cấu trong nước, đã từ EP-2007-01):** Khủng hoảng tín dụng và lạm phát nội địa đang
  diễn ra khi Lehman Shock xảy ra. SBV đang trong chu kỳ THẮT CHẶT vì lý do nội địa (CPI 23%).
- **Lớp 2 (ngoại sinh):** Sụp đổ cầu bên ngoài — xuất khẩu VN rơi 7.7%, FDI disbursement chậm lại,
  dòng vốn portfolio rút.

**Phân biệt:** Lạm phát VN GIẢM nhanh từ đỉnh 23% (08/2008) xuống 6.5% (2009) KHÔNG phải vì SBV
thành công — mà vì giá hàng hóa toàn cầu (dầu, lương thực) sụp đổ sau Lehman Shock làm áp lực
import-inflation tạm biến mất. Đây là "giảm tạm thời do external shock" chứ không phải "ổn định
cơ cấu". Bằng chứng: khi SBV nới lỏng và tín dụng tái tăng 2009-2010, lạm phát quay lại ngay.

### Tổng kết EP-2008-09
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `MIXED` (STRUCTURAL đang chạy + EXTERNAL_SHOCK mới) | clean |
| 2. Resolution | N/A — external shock resolved by global recovery; domestic structural unresolved | — |

- **shock_origin:** 15/09/2008 (Lehman Brothers)
- **policy_response_start:** Q4 2008 (gói kích thích tài khóa US$8 tỷ)
- **recovery_confirmed:** Q2 2009 (global trade stabilized, VN exports recovering)
- **chain_classification:** `WAVE_OF:MEGA_2007_2012` (external shock tạo "window" giữa 2 wave lạm phát,
  nhưng KHÔNG giải quyết imbalance cơ cấu trong nước)
- **analyst_notes:** Đây là điểm tinh tế nhất — giai đoạn 2009 trông như "recovery" vì CPI giảm, nhưng
  đó là do commodity giá toàn cầu sụp đổ, không phải do VN giải quyết được imbalance tín dụng/NPL.
  Gói kích thích 5% GDP thực tế THÊM dầu vào lửa cho Wave 2 (2009-2012).

---

## EP-2009-09 — Second Inflation Wave and Banking NPL Crisis (Wave 2 of 2007-2012 mega-episode)

**Cửa sổ episode:** 09/2009 (tín dụng và lạm phát tái tăng tốc) → 12/2012 (CPI về <7%, banking
restructuring đã có framework). Đây là Wave 2/3 của cụm khủng hoảng cơ cấu 2007-2012.

**Trigger đã biết PIT:** Gói kích thích tài khóa Q4 2008 → tín dụng tăng 36% (2009), 32.4% (2010)
→ CPI leo lại từ 6.5% (2009) lên 9.23% (2010) → đỉnh 23% tháng 08/2011. Bong bóng bất động sản
tiếp diễn → NPL crystallize 2012 (17.21% hệ thống per SBV assessment Q3/2012).

### Trục 1: `STRUCTURAL` — confidence: **clean**

- **Tín dụng tăng 36% (2009) + 32.4% (2010)** sau gói kích thích — tái tạo chính xác mẫu hình
  overheating như 2007. Nguồn: IMF Vietnam Article IV 2010; World Bank Vietnam Update 2012.
- **CPI leo dần nhiều quý liên tiếp:** 6.5% (2009) → 9.23% (2010) → đỉnh 23% (08/2011) → 18.68%
  bình quân năm 2011. Đây không phải spike đột ngột mà là build-up tích lũy = STRUCTURAL.
  Nguồn: GSO; Trading Economics Vietnam CPI; nghiên cứu ANU về lạm phát VN.
- **NPL hệ thống ngân hàng đạt 17.21% cuối Q3/2012** (SBV reassessment) = hậu quả trực tiếp của
  tín dụng bơm vào bất động sản 2007-2011 chưa được xử lý. Nguồn: SBV Banking Supervision Report;
  World Bank Lexology NPL analysis.
- **Resolution 11/NQ-CP ngày 24/02/2011** — cap tín dụng <20%, siết tài khóa, ưu tiên sản xuất vs
  bất động sản/chứng khoán — là phản ứng MACRO-STABILIZATION toàn hệ thống (không phải nhắm 1 tổ
  chức). Nguồn: [luatvietnam.vn Resolution 11/NQ-CP 2011-02-24](https://english.luatvietnam.vn/resolution-no-11-nq-cp-dated-february-24-2011-of-the-government-on-major-solutions-for-controlling-inflation-stabilizing-the-macro-economy-and-ensu-59598-doc1.html).
- **SBV nâng refi rate lên 15% vào tháng 11/2011** (đỉnh lịch sử) — chính sách thắt chặt cực mạnh
  cần thiết cho STRUCTURAL overheating, không phải "1 hành động nhắm đúng 1 trigger". Nguồn:
  MacroMicro/CEIC Vietnam Policy Rate.
- **Thời gian giải quyết thực tế: Decision 254 (03/2012) → VAMC (07/2013) → NPL cleanup kéo đến
  2015-2016** — tổng 4-5 năm kể từ khi NPL crystallized. Nguồn: World Bank Vietnam Banking Sector
  Soundness report; ADB Vietnam Financial Sector Assessment.

**Kết luận trục 1:** Tín dụng và CPI đã tích lũy xấu đi từ nhiều quý trước + Resolution 11 là
macro-stabilization toàn hệ thống + banking NPL cần 4-5 năm giải quyết. ⇒ `STRUCTURAL`.

### Tổng kết EP-2009-09
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `STRUCTURAL` | clean |
| 2. Resolution type | `MULTI_YEAR_STRUCTURAL` | clean |

- **shock_origin:** Q4 2008 (fiscal stimulus bắt đầu bơm); Q3 2009 (tín dụng tăng tốc rõ ràng)
- **policy_response_start:** 24/02/2011 (Resolution 11/NQ-CP — chính sách macro-stabilization chính thức)
- **recovery_confirmed:** 12/2012 (CPI về <7%); 2015-2016 (banking NPL resolved, VAMC operational)
- **chain_classification:** `WAVE_OF:MEGA_2007_2012` (Wave 2+3)
- **analyst_notes:** Một số nguồn phân loại đây là "2011 inflation crisis" riêng biệt với "2007-2008
  crisis" — phân loại đó SAI về mặt cơ cấu. Imbalance gốc (NPL từ 2007-2010, đô la hóa, thiếu cơ
  chế kiểm soát tín dụng ngân hàng cổ phần nhỏ) không bao giờ được giải quyết giữa 2 episode, làm
  cho 2009 "recovery" chỉ là bề mặt.

---

## ADDENDUM — 2026-08-31: đọc lại chi tiết cửa sổ 2008Q4→2009Q3 (Bobby, BLIND)

**Yêu cầu:** một dispatch riêng yêu cầu đọc chi tiết đúng 12 tháng 10/2008→09/2009 (SBV lãi suất
theo quý+ngày cụ thể, gói kích cầu, tỷ giá/GIR, FDI/FII, thanh khoản liên ngân hàng/tín dụng/M2),
**redact tường minh** diễn biến VNINDEX sau giai đoạn — tuân thủ đúng luật BLIND của vai trò này.
Đây KHÔNG phải episode mới — trùng hoàn toàn với `EP-2008-09` ở trên + đầu Pha 1A/1B của
`vn_macro_regime_history_2009_2018_phases.md`. Addendum này CHỈ bổ sung số liệu granular mới tìm
được (đường lãi suất theo NGÀY, số tín dụng/FDI cụ thể) — không đổi phân loại đã chốt, chỉ làm nó
sắc hơn.

### Đường lãi suất cơ bản SBV theo ngày (bổ sung so với "14%→7% (02/2009)" đã có)

Đỉnh thắt chặt: **14%/năm từ 06/2008** (đáp lại CPI 23%). Từ cuối 10/2008 SBV đảo chiều, cắt
**5 lần liên tiếp trong ~2 tháng**:
- **Quyết định 3161/QĐ-NHNN**, hạ từ 10% → **8,5%/năm, hiệu lực 22/12/2008**
  ([Báo Chính phủ, 2008-12-19](https://baochinhphu.vn/tu-22-12-2008-lai-suat-co-ban-giam-con-85-nam-10212509.htm)).
- Tiếp tục cắt đầu 2009, về **7%/năm từ 02/2009** — mức này giữ nguyên suốt Pha 1B/1C (đến khi
  nâng lại 25/11/2009), khớp file cha EP-2008-09/Phases §Pha 1A.
- Đồng thời: hạ dự trữ bắt buộc VND + cho phép biên độ tỷ giá nới — hướng đi xác nhận qua nhiều
  nguồn tổng hợp nhưng KHÔNG tìm được quyết định/ngày chính xác qua search vòng này (đánh dấu
  **chưa xác minh mức %/ngày cụ thể** — khác biệt với đường lãi suất đã có ngày rõ).
- Nguồn tổng hợp chuỗi cắt: search tổng hợp nhiều báo VN (VnEconomy/Tuổi Trẻ/luatvietnam) +
  1 nguồn quốc tế xác nhận "cắt 400bp từ cuối 10/2008... về 7% trong vài tháng."

### Tín dụng & M2 — con số granular mới

- **Tăng trưởng tín dụng CẢ NĂM 2009 đạt 37,53%, so với mục tiêu ban đầu 21-23%** — vượt mục tiêu
  ~1,6-1,8 lần. Đây chính là cơ chế tái tích lũy STRUCTURAL đã nêu ở EP-2008-09/Phases §Pha 1B,
  nay có con số cụ thể. (Nguồn: tổng hợp qua search, đối chiếu số liệu SBV thường được trích trong
  các nghiên cứu học thuật; **confidence: medium** — chưa fetch được bản gốc IMF Article IV 2010
  do trang chặn truy cập tự động 403, cần verify lại nếu dùng làm số PIN.)
- Đối chứng: **năm 2007 mục tiêu M2 20-23%, thực tế 46,12%** — cho thấy mẫu hình "mục tiêu bị vượt
  xa" đã có TRƯỚC episode này (từ 2007), củng cố thêm luận điểm STRUCTURAL của mega-episode
  2007-2012 (không phải điểm mới của riêng cửa sổ 2008Q4-2009Q3).

### CPI YoY theo tháng, xác nhận bằng BQ (`cpi_vn.py`, PIT nhưng gắn cờ backfill)

Chạy `cpi_vn.cpi_monthly_df()` (dataset nội bộ, cột `is_backfill_2007_2010=True` /
`is_real_nso=False` cho giai đoạn này — **nghĩa là số liệu backfill/ước tính, KHÔNG phải bản gốc
GSO nạp trực tiếp — dùng để XÁC NHẬN xu hướng, không dùng để PIN số chính xác từng tháng**):

| Tháng | CPI YoY | Tháng | CPI YoY |
|---|---|---|---|
| 09/2008 | 27,90% | 04/2009 | 9,23% |
| 10/2008 | 26,74% | 05/2009 | 5,65% |
| 11/2008 | 24,22% | 06/2009 | 3,67% |
| 12/2008 | 19,89% | 07/2009 | 3,31% |
| 01/2009 | 17,49% | 08/2009 | 2,27% |
| 02/2009 | 14,81% | **09/2009** | **0,68%** ← cuối cửa sổ được hỏi |
| 03/2009 | 11,19% | 10/2009 | −0,02% (đáy) |

Ngay SAU cửa sổ được hỏi (không dùng để classify, chỉ để thấy điểm gãy đã ghi ở Phases §Pha 1C):
11/2009 = 4,35%, 12/2009 = 6,52% — đảo chiều dốc đứng đúng như đã chốt trước đó.

**Đọc đúng nghĩa của con số 0,68% (09/2009) khi KHÔNG biết trước điều gì xảy ra sau đó:** đây là
đáy lạm phát so-sánh-cùng-kỳ do cơ số cao của 2008 (base effect) + giá hàng hóa toàn cầu sụp —
KHÔNG phải bằng chứng ổn định cơ cấu. Người đọc real-time CÓ THỂ nghi ngờ điều này ngay tại thời
điểm 09/2009 bằng 3 chỉ báo độc lập cùng có sẵn: (a) tín dụng đã vượt mục tiêu từ giữa năm
(SBV công bố định kỳ), (b) cán cân thương mại đã đảo sang thâm hụt từ Q2/2009 (GSO/Hải quan trễ
2-4 tuần), (c) premium tỷ giá chợ đen bắt đầu nới rộng (quan sát hàng ngày, trễ 0) — cả ba đã ghi
trong `vn_macro_regime_history_2009_2018_phases.md` §Pha 1B.

### FDI — bổ sung xu hướng (chưa xác minh được số tuyệt đối 2008 do nguồn mâu thuẫn)

- **2009 (7 tháng đầu năm):** ~US$10,1 tỷ đăng ký (53% dự án cấp mới, 46% vốn bổ sung), giải ngân
  thực tế ~US$4,6 tỷ trong cùng kỳ; mục tiêu cả năm công bố lúc đó: US$20 tỷ đăng ký / US$8 tỷ giải
  ngân ([Vietnam Embassy US, 2009-08](https://vietnamembassy-usa.org/news/2009/08/nation-attracts-over-10-billion-usd-fdi)).
- Đối chiếu 2008: một nguồn cho giải ngân 2008 ~US$11,5 tỷ (tăng từ ~US$8,1 tỷ năm 2007), một
  nguồn khác cho ~US$10,5 tỷ — **hai nguồn lệch nhau, KHÔNG chốt số chính xác** (search vòng này
  không tiếp cận được ADB working paper gốc do lỗi fetch). Hướng đi nhất quán ở mọi nguồn: FDI
  ĐĂNG KÝ giảm mạnh 2008→2009 (từ mức kỷ lục ~US$71 tỷ đăng ký 2008 — số quy mô lớn phần nhiều
  do vài dự án siêu lớn — về mặt bằng thấp hơn hẳn 2009-2014, theo mô tả định tính "quanh
  US$8-9 tỷ/năm 2009-2014"). **FII/portfolio flow theo quý: KHÔNG tìm được số cụ thể** cho đúng
  cửa sổ này qua search vòng này — cần dispatch riêng nếu cần con số chính xác (gợi ý: SSC/HOSE
  báo cáo khối ngoại, hoặc IMF BOP data qua CEIC).

### Phân loại — XÁC NHẬN LẠI, không đổi, cho đúng cửa sổ 2008Q4-2009Q3 hẹp

| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `MIXED` — lớp NGOẠI (Lehman/cầu xuất khẩu sụp) chiếm ưu thế Ở ĐẦU cửa sổ; lớp NỘI ĐỊA (tín dụng tái tăng vượt mục tiêu, thương mại đảo thâm hụt, premium chợ đen nới) đã bắt đầu tái xuất hiện, QUAN SÁT ĐƯỢC ngay trong cửa sổ, TRƯỚC khi cửa sổ kết thúc (09/2009) | clean |
| 2. Containability (áp dụng cho lớp ngoại) | `EXTERNAL_CYCLE`, KHÔNG phải `CONTAINABLE` — dù VN phản ứng nhanh/đơn lẻ (gói lãi suất 4% + cắt lãi suất 5 lần trong ~2 tháng), NGUYÊN NHÂN GỐC (cầu xuất khẩu toàn cầu sụp) chỉ hết khi thương mại thế giới phục hồi — một chu kỳ ngoài tầm quyết định của VN, không phải 1 hành động chính sách VN chấm dứt được nó | clean |

**Điểm bước ngoặt (inflection points) theo trình tự thời gian, thuần chính sách/vĩ mô, KHÔNG
tham chiếu giá cổ phiếu:**
1. **15/09/2008** — Lehman Brothers sụp đổ (khởi phát cú sốc ngoại, không phải hành động chính
   sách VN nhưng là mốc kích hoạt).
2. **Cuối 10/2008 → 22/12/2008** — SBV đảo chiều 180°, cắt lãi suất cơ bản 5 lần liên tiếp
   (14%→10%→8,5% theo QĐ 3161/QĐ-NHNN hiệu lực 22/12/2008).
3. **23/01/2009 (ký) / 01/02/2009 (hiệu lực)** — QĐ 131/QĐ-TTg, gói bù lãi suất 4%/năm vay ngắn
   hạn ≤8 tháng, quy mô ~17 nghìn tỷ VND — hành động tài khóa CỤ THỂ đầu tiên, nhắm đúng mục tiêu
   (không phải macro-stabilization rộng như Resolution 11/2011 sau này).
   Nguồn: [MOF](https://irt.mof.gov.vn/webcenter/portal/btcen/pages_r/l/newsdetails?dDocName=BTC078876).
4. **02/2009** — lãi suất cơ bản chạm đáy chu kỳ 7%/năm.
5. **04/04/2009** — QĐ 443/QĐ-TTg mở rộng bù lãi suất sang vay trung-dài hạn (mở rộng gói kích
   cầu, không phải gói mới).
6. **04/2009** — Thủ tướng công bố quy mô đầy đủ gói kích thích ~US$8 tỷ (≈5% GDP).
7. **Giữa 2009 (quan sát được real-time, không phải hindsight)** — tín dụng vượt mục tiêu 21-23%
   (SBV công bố định kỳ trễ ~1 tháng); cán cân thương mại đảo sang thâm hụt từ Q2 (GSO/Hải quan);
   premium tỷ giá chợ đen bắt đầu nới (quan sát hàng ngày) — ba tín hiệu ĐỘC LẬP cùng chiều, đủ để
   một người đọc kỷ luật nghi ngờ tính bền vững của "ổn định" cuối cửa sổ 09/2009, MÀ KHÔNG CẦN
   biết trước điều gì xảy ra tháng 11/2009.
8. **09/2009 — kết thúc cửa sổ được hỏi.** CPI YoY chạm đáy 0,68% (BQ `cpi_vn.py`, backfill/PIT-
   proxy) — điểm này bản thân nó KHÔNG phải bước ngoặt chính sách, chỉ là điểm quan sát cuối của
   yêu cầu; bước ngoặt chính sách TIẾP THEO (25/11/2009, ngoài cửa sổ được hỏi) đã ghi ở file
   Phases §Pha 1C, không lặp lại ở đây.

**Kết luận cho câu hỏi Loại-1/Loại-2 của mandate margin (2026-08-25):** cửa sổ 2008Q4-2009Q3
đọc RIÊNG LẺ trông giống Loại-2 (có policy anchor rõ: QĐ 131 + chuỗi cắt lãi suất, phản ứng
nhanh trong vài tháng) — nhưng đây là ĐỌC THIẾU NGỮ CẢNH nếu tách khỏi mega-episode 2007-2012.
Đặt đúng trong chuỗi, nó là "cửa sổ tạm nghỉ do external shock" bên TRONG một khủng hoảng
STRUCTURAL chưa giải quyết (đã chốt ở EP-2008-09/EP-2009-09) — root cause tổng thể vẫn `STRUCTURAL`,
KHÔNG đủ điều kiện Loại-2 cho mục đích margin sizing. Không đổi verdict `WAVE_OF:MEGA_2007_2012`.

*Soạn: macro-strategist (Bobby), 2026-08-31, dispatch BLIND (redact tường minh diễn biến
VNINDEX sau cửa sổ). Nguồn mới bổ sung: Báo Chính phủ (QĐ 3161, 2008-12-19), search tổng hợp
đường lãi suất VN 2008 (nhiều báo trong nước, chưa fetch được bản SBV gốc), Vietnam Embassy US
(FDI 7 tháng 2009), BQ nội bộ `cpi_vn.cpi_monthly_df()`. Giới hạn đã nêu rõ: FII/portfolio flow
theo quý KHÔNG xác minh được vòng này; số FDI tuyệt đối 2008 có 2 nguồn lệch nhau; dự trữ bắt
buộc không tìm được % + ngày cụ thể; IMF Article IV 2010 (cr10281.pdf) — nguồn đã trích ở
EP-2008-09/Phases nhưng KHÔNG fetch lại được trực tiếp vòng này (HTTP 403), số liệu tín dụng
37,53%/21-23% lấy qua search tổng hợp, đối chiếu — khuyến nghị Taylor/Winston verify lại bằng
nguồn IMF gốc nếu cần dùng làm số PIN cho phân tích định lượng.

---

## EP-2014-09 — OPEC Output Freeze / Global Oil Price Collapse (VNINDEX −19,12%, 2014-09-03→2014-12-17)

**Cửa sổ episode (do caller cung cấp, dd52/arm-trigger, KHÔNG kèm forward-return):** VNINDEX
giảm −19,12% trong 75 phiên, 2014-09-03 → 2014-12-17.

**Trigger đã biết PIT (công khai tại thời điểm đó):** Brent bắt đầu trượt dốc từ đỉnh ~$115
(06/2014) xuống dưới $80 (10/2014); cú sốc quyết định là cuộc họp OPEC **27/11/2014** — nhóm giữ
nguyên trần sản lượng 30 triệu thùng/ngày bất chấp dư cung toàn cầu → Brent rơi thẳng từ $77,75
xuống **$70,15** ngay hôm sau, tiếp tục về dưới $60 cuối 12/2014 — [CNN Money,
2014-11-27](https://money.cnn.com/2014/11/27/investing/oil-prices-opec-crude/); [Business
Standard, 2014-11-28](https://www.business-standard.com/amp/article/reuters/brent-near-four-year-low-after-opec-decides-against-output-cut-114112800074_1.html).
Việt Nam là nước xuất khẩu dầu thô ròng (PVN đóng góp ngân sách nhà nước, cổ phiếu dòng dầu khí
PVD/PVS/GAS chiếm tỷ trọng lớn trên sàn) — kênh truyền dẫn dự đoán được: doanh thu ngân sách từ
dầu thô + lợi nhuận nhóm dầu khí niêm yết.

### Trục 1: `CONFIDENCE_LIQUIDITY` (đọc đúng hơn: cú sốc giá hàng hoá ngoại sinh, không phải mất
cân đối tín dụng/lạm phát nội địa) — confidence: **clean**

Bằng chứng nền vĩ mô VN NGAY TRƯỚC và TRONG episode — tất cả đi NGƯỢC hướng với mẫu STRUCTURAL:
- **CPI YoY giảm đều đặn, không xấu đi.** Chuỗi tháng qua `cpi_vn.py` (BQ nội bộ): 6,00% (12/2013)
  → 5,50% (01/2014) → 3,83% (06/2014) → **2,81% (09/2014, đầu episode)** → **1,80% (12/2014, cuối
  episode)** → tiếp tục về 0,60% (12/2015). Đây là DISINFLATION đều, không phải tích lũy lạm phát
  nhiều quý trước episode — đối lập trực tiếp với mẫu 2007/2011 (CPI leo dần TRƯỚC đỉnh khủng
  hoảng). Nguồn: `cpi_vn.cpi_monthly_df()`, cột `is_real_nso=False` (giai đoạn này là số tổng hợp
  không phải bản gốc NSO trực tiếp — dùng để xác nhận XU HƯỚNG, khớp hướng với GSO/Trading
  Economics công khai).
- **Tín dụng cả năm 2014 = 14,2%** — dưới/ngang mục tiêu SBV (SBV thời điểm đó phàn nàn tín dụng
  "thấp hơn kỳ vọng", KHÔNG phải vượt trần). Nguồn: FiinRatings Banking Sector report (tổng hợp);
  World Bank Taking Stock Dec 2014 xác nhận "credit growth continues to come in below
  expectation" — [World Bank Vietnam Taking Stock Dec
  2014](https://www.worldbank.org/en/country/vietnam/publication/takingstockdecember2014).
- **Lãi suất huy động (`deposit_rate_vn.py`) tiếp tục giảm đều, không có spike:** 7,0% (01/2014) →
  6,3% (07/2014) → 5,5% (01/2015) — hướng đi hoàn toàn NGƯỢC với một cú sốc thanh khoản/bank-run
  (lẽ ra phải thấy lãi suất huy động NHẢY lên để giữ tiền gửi). Không có dấu hiệu căng thẳng liên
  ngân hàng đồng thời với episode giá cổ phiếu.
- **GDP Q3/2014 tăng 6,2% YoY, 9 tháng đầu năm 5,6%** — tăng tốc, không suy giảm. Ngân sách nhà
  nước 9 tháng đầu năm tăng 17% YoY. Cán cân vãng lai thặng dư, dự trữ ngoại hối tăng. Nguồn: World
  Bank Taking Stock Dec 2014 (trên).
- **PVN đã hoàn thành nộp ngân sách 2014 từ đầu tháng 11/2014** (trước khi giá dầu chạm đáy) và
  VƯỢT kế hoạch năm — nộp 178.100 tỷ VND, vượt kế hoạch 37.600 tỷ VND — [Vietnam Energy Magazine,
  2014-12-30](https://vietnamenergy.vn/petrovietnam-has-handed-in-the-budget-a-vnd-376-thousand-billion-sum-over-the-plan-11376.html).
  Nghĩa là: tác động ngân sách 2014 THỰC TẾ chưa đến (đã nộp đủ trước khi giá sập); cú sốc là dự
  báo FORWARD (lo ngại ngân sách/lợi nhuận PVN 2015), không phải tổn thất đã hiện thực hóa cho
  2014 — càng khẳng định đây là phản ứng THỊ TRƯỜNG với 1 biến số giá hàng hóa cụ thể, không phải
  phát hiện ra một imbalance vĩ mô nội địa đang tồn tại.

**Kết luận trục 1:** Không có bất kỳ chỉ tiêu nào (CPI, tín dụng, lãi suất huy động, GDP, cán cân
vãng lai) xấu đi trước hay trong episode — nền vĩ mô nội địa VN 2014 lành mạnh, đang trong xu
hướng ổn định hóa hậu 2011-2012. Trigger là MỘT quyết định cụ thể của MỘT tổ chức bên ngoài (OPEC,
27/11/2014) tác động qua kênh giá hàng hóa/kỳ vọng lợi nhuận nhóm dầu khí — không phải bằng chứng
mất cân đối macro VN. ⇒ `CONFIDENCE_LIQUIDITY` (đọc đúng bản chất: cú sốc giá hàng hóa ngoại sinh,
không phải khủng hoảng niềm tin ngân hàng kiểu 2022, nhưng cùng nhóm "trigger cụ thể, không tự nó
là bằng chứng imbalance nội địa" theo khung phân loại).

### Trục 2: `EXTERNAL_CYCLE` — confidence: **clean**

- **Không có MỘT hành động chính sách VN nào có thể "sửa" giá dầu thế giới.** Đây là khác biệt cơ
  bản với case CONTAINABLE (SCB 2022: SBV kiểm soát đặc biệt 1 ngân hàng cụ thể; COVID 2020: vaccine
  + reopening) — không có đòn bẩy chính sách trong nước tương đương cho một cuộc chiến thị phần
  dầu mỏ toàn cầu (OPEC vs. đá phiến Mỹ).
  Nguồn (bối cảnh chiến lược OPEC): [CNBC,
  2018-05-15](https://www.cnbc.com/2018/05/15/oil-prices-have-rebounded-since-opec-refused-to-cut-output-in-2014.html)
  — "OPEC bet thấp giá sẽ buộc nhà sản xuất đá phiến Mỹ giảm sản lượng" — chiến lược đa năm, không
  phải sự kiện giải quyết được trong vài tuần/tháng.
- **Chu kỳ giá dầu thấp kéo dài nhiều năm, không phải một cú sốc rồi hồi phục nhanh.** Brent tiếp
  tục rơi xuống đáy $27,10/thùng vào 01/2016 — nghĩa là bản thân chu kỳ giá dầu (nguyên nhân gốc
  của episode) CHƯA kết thúc ngay cả 13 tháng sau điểm bắt đầu episode này; nó là một hiện tượng
  thị trường hàng hóa toàn cầu đa năm, VN hoàn toàn là bên nhận (price-taker), không kiểm soát
  được thời điểm kết thúc.
- Phản ứng chính sách VN quan sát được chỉ là ĐIỀU CHỈNH THEO (Bộ Tài chính hạ giả định giá dầu
  trong dự toán ngân sách 2015, Petrolimex điều chỉnh giá bán lẻ xăng dầu trong nước theo biến động
  giá thế giới) — đây là thích ứng bị động, KHÔNG phải một hành động NHẮM ĐÚNG MỤC TIÊU để giải
  quyết nguyên nhân gốc (giống refi rate cut cho COVID hay kiểm soát đặc biệt SCB).

**Kết luận trục 2:** Không có cơ chế chính sách VN nào giải quyết trực tiếp nguyên nhân gốc (chu
kỳ giá dầu toàn cầu do quyết định OPEC + cạnh tranh đá phiến Mỹ); thời điểm kết thúc chu kỳ không
do VN quyết định. ⇒ `EXTERNAL_CYCLE`.

### Tổng kết EP-2014-09
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `CONFIDENCE_LIQUIDITY` (cú sốc giá hàng hóa ngoại sinh) | clean |
| 2. Containability | `EXTERNAL_CYCLE` | clean |

- **shock_origin:** 06/2014 (Brent bắt đầu trượt dốc từ đỉnh); 27/11/2014 (quyết định OPEC — điểm
  gãy dứt khoát nhất)
- **policy_response_start:** N/A (không có macro-stabilization action; chỉ điều chỉnh thụ động giả
  định ngân sách + giá bán lẻ xăng dầu trong nước)
- **recovery_confirmed:** không xác định trong phạm vi phân tích BLIND này (đọc dừng ở
  17/12/2014, không tra cứu diễn biến giá cổ phiếu sau đó theo đúng luật BLIND của vai trò)
- **chain_classification:** `INDEPENDENT`
- **analyst_notes:** Case này khác 2018 (EM risk-off đa nguyên nhân) ở chỗ trigger ở đây có MỘT
  ngày cụ thể, MỘT quyết định của MỘT tổ chức (OPEC 27/11/2014) — sạch hơn về mặt nhận diện nguyên
  nhân so với 2018. Điểm chung với 2018: cả hai đều xảy ra trên nền vĩ mô nội địa VN LÀNH MẠNH
  (CPI thấp, tín dụng trong tầm kiểm soát, không có dấu hiệu overheating) — nhóm case này (2014,
  2018) nên được sizing/đọc khác với nhóm STRUCTURAL (2007-2012) khi dùng cho phân tích thống kê
  N_effective.

---

## EP-2015-07 — China Yuan Devaluation / Global "Black Monday" Risk-Off (VNINDEX −17,50%, 2015-07-14→2015-08-24)

**Cửa sổ episode (do caller cung cấp, dd52/arm-trigger, KHÔNG kèm forward-return):** VNINDEX
giảm −17,50% trong 29 phiên, 2015-07-14 → 2015-08-24.

**Trigger đã biết PIT (công khai tại thời điểm đó):** Chứng khoán Trung Quốc đã giảm mạnh từ
tháng 06/2015 (Shanghai Composite mất ~43% trong hơn 2 tháng June→Aug 2015). PBOC phá giá NDT
**11/08/2015** gần 2% — mức phá giá lớn nhất trong 2 thập kỷ, làm dấy lên lo ngại tăng trưởng TQ
yếu hơn dự báo và kích hoạt bán tháo lan rộng >US$5 nghìn tỷ vốn hóa toàn cầu — [CNN Money,
2015-08-11](https://money.cnn.com/2015/08/11/news/economy/china-yuan-devaluation-stocks-market/index.html).
Đỉnh điểm là "Black Monday" toàn cầu **24/08/2015** (đúng ngày cuối episode) khi Shanghai Composite
rơi 8,5% trong 1 phiên — [Business Standard,
2015-08-24](https://www.business-standard.com/amp/article/news-cm/asia-pacific-market-market-crashes-to-multi-month-lows-115082401471_1.html).
Kênh truyền dẫn tới VN dự đoán được: TQ là đối tác thương mại lớn nhất VN (VN nhập siêu từ TQ
~US$32-33 tỷ năm 2015 — [Vinachem tổng
hợp](https://www.vinachem.com.vn/content/market-and-product-vnc/vietnam-trade-deficit-with-china-hits-150bn-after-five-years.html))
→ NDT rẻ đi đe dọa sức cạnh tranh xuất khẩu VN + áp lực phá giá cạnh tranh (currency-war) trong cả
khu vực châu Á.

### Trục 1: `CONFIDENCE_LIQUIDITY` — confidence: **ambiguous**

Đa số chỉ tiêu độc lập cho thấy nền vĩ mô nội địa VN lành mạnh, KHÔNG có tích lũy mất cân đối
trước episode — nhưng có MỘT chỉ tiêu (tín dụng) cho tín hiệu trái chiều, nên đánh dấu ambiguous
thay vì clean:

- **CPI YoY cực thấp, gần giảm phát trong chính episode:** `cpi_vn.py` — **0,93% (07/2015)** →
  **0,87% (08/2015)** — hoàn toàn không có áp lực cầu kéo nội địa. Đây là mức lạm phát thấp lịch
  sử, đối lập hoàn toàn với mẫu STRUCTURAL (CPI phải xấu đi TRƯỚC episode).
- **Lãi suất huy động ổn định tuyệt đối suốt cả năm:** `deposit_rate_vn.py` giữ nguyên **5,5%**
  từ 01/2015 đến hết 2016 — không có bất kỳ dấu hiệu căng thẳng thanh khoản/huy động vốn nào đồng
  thời với episode. Đây là bằng chứng mạnh CHỐNG lại giả thuyết bank-run/thanh khoản nội địa.
- **Điểm ambiguous — tín dụng cả năm 2015 vượt mục tiêu:** tăng trưởng tín dụng đạt **17,02%** tính
  đến 18/12/2015 — mức cao nhất kể từ 2011, VƯỢT mục tiêu SBV đề ra ~13-15% cho năm đó (nguồn tổng
  hợp qua search, đối chiếu VietnamNews/SBV báo cáo cuối năm — **chưa fetch được văn bản mục tiêu
  gốc của SBV đầu năm 2015, dùng số tổng hợp báo chí**). Đây là con số CẢ NĂM (tích lũy đến giữa
  tháng 12), không phải số tại-thời-điểm-episode (giữa 07-08/2015) — không xác định được phần nào
  của mức vượt này đã xảy ra TRƯỚC episode hay tích lũy dần suốt nửa cuối năm. Khác với 2007
  (tín dụng 53-54%, vượt gấp 3-4 lần target) hay 2009 (36-37% vượt xa so với 21-23%), mức vượt
  17,02% vs 13-15% ở đây NHỎ hơn nhiều về độ lớn VÀ không đi kèm CPI leo thang (CPI vẫn <1% suốt
  episode và cả năm) — nghĩa là tín dụng tăng không truyền dẫn thành lạm phát, khác hẳn cơ chế
  STRUCTURAL đã thấy ở 2007-2012.
- **Không có sự kiện/tổ chức trong nước nào bị nêu tên** (không bank run, không scandal công ty) —
  trigger hoàn toàn là 2 sự kiện bên ngoài VN có ngày cụ thể (PBOC 11/08, Black Monday toàn cầu
  24/08).

**Kết luận trục 1:** Đa số bằng chứng (CPI cực thấp, lãi suất huy động ổn định, không trigger nội
địa) chỉ ra `CONFIDENCE_LIQUIDITY` với trigger ngoại sinh rõ ràng — nhưng tín dụng vượt mục tiêu cả
năm là một tín hiệu trái chiều CHƯA thể loại trừ hoàn toàn (không đủ dữ liệu tần suất cao hơn để
tách phần vượt trước/sau episode). ⇒ `CONFIDENCE_LIQUIDITY`, confidence **ambiguous**.

### Trục 2: `EXTERNAL_CYCLE` — confidence: **clean**

- **SBV PHẢN ỨNG rất nhanh với MỘT kênh cụ thể (tỷ giá):** nới biên độ giao dịch VND/USD từ ±1%
  lên ±2% ngày **12/08/2015** (ngay sau NDT phá giá 1 ngày), rồi tiếp tục phá giá tỷ giá trung tâm
  thêm 1% VÀ nới biên độ lên ±3% ngày **19/08/2015** — [Bloomberg,
  2015-08-19](https://www.bloomberg.com/news/articles/2015-08-19/vietnam-s-central-bank-devalues-dong-for-third-time-this-year);
  [Fox News/AP,
  2015-08](https://www.foxnews.com/world/vietnam-doubles-currency-trading-band-to-spur-exports-after-china-devalues-yuan).
  Đây LÀ một hành động nhắm đúng kênh truyền dẫn cụ thể (tỷ giá), tương tự tinh thần "1 hành động
  nhắm đúng mục tiêu" — nhưng KHÔNG giải quyết được nguyên nhân gốc (xem dưới).
- **NHƯNG áp lực tỷ giá KHÔNG dừng lại sau hành động tháng 08/2015** — VND tiếp tục yếu thêm hết
  năm: "the dong weakened 4.5 percent in interbank... against the SBV's pledge to let it slip only
  2 percent in 2015", kết năm ở 22.495đ/USD, yếu hơn 2,7% so với tỷ giá tham chiếu 31/12 —
  [VOA/Reuters tổng
  hợp](https://www.voanews.com/a/vietnam-devalues-currency-as-inflation-bites-115883724/167035.html).
  Nguyên nhân là ÁP LỰC KÉP tiếp diễn: (a) chu kỳ giảm tốc/phá giá cạnh tranh của TQ (đa năm, VN
  không kiểm soát), (b) kỳ vọng Fed nâng lãi suất lần đầu kể từ khủng hoảng 2008 (thực hiện
  16/12/2015) — cả hai đều là xu hướng BÊN NGOÀI VN, không có mốc thời gian VN tự quyết được.
- **Áp lực buộc VN phải THAY ĐỔI CƠ CHẾ (không chỉ 1 hành động đơn lẻ):** từ **04/01/2016** SBV bỏ
  cơ chế tỷ giá trung tâm cố định/điều chỉnh rời rạc, chuyển sang cơ chế **tỷ giá trung tâm hàng
  ngày neo theo rổ 8 đồng tiền** — một thay đổi CẤU TRÚC (structural policy redesign), không phải
  "một hành động dập tắt 1 trigger" như kiểm soát đặc biệt SCB (2022) hay vaccine rollout (2020).
  Việc phải redesign cả khung chính sách (thay vì chỉ 1 lần can thiệp) là dấu hiệu rõ nguyên nhân
  gốc KHÔNG kết thúc trong episode — nó là một phần của chu kỳ đa năm (căng thẳng tỷ giá châu Á
  2015-2016 gắn với chu kỳ thắt chặt Fed, tiếp diễn đến tận 2016).

**Kết luận trục 2:** SBV có phản ứng nhanh và cụ thể về tỷ giá, nhưng bản thân stress indicator
(áp lực phá giá VND) KHÔNG hạ nhiệt trong vòng vài tuần/tháng sau hành động — nó tiếp tục đến hết
năm và buộc phải redesign cơ chế đầu 2016. Nguyên nhân gốc (chu kỳ TQ + kỳ vọng Fed) là xu hướng
đa năm ngoài tầm kiểm soát VN. ⇒ `EXTERNAL_CYCLE`.

### Tổng kết EP-2015-07
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `CONFIDENCE_LIQUIDITY` | ambiguous (tín dụng cả năm vượt target, không đi kèm CPI) |
| 2. Containability | `EXTERNAL_CYCLE` | clean |

- **shock_origin:** 06/2015 (TTCK Trung Quốc bắt đầu sụp — cảnh báo sớm); 11/08/2015 (PBOC phá
  giá NDT — điểm gãy dứt khoát nhất); 24/08/2015 (Black Monday toàn cầu — trùng ngày cuối episode)
- **policy_response_start:** 12/08/2015 (SBV nới biên độ ±1%→±2%); 19/08/2015 (phá giá tỷ giá
  trung tâm 1% + nới biên độ ±2%→±3%)
- **recovery_confirmed:** không xác định trong phạm vi phân tích BLIND này (đọc dừng ở
  24/08/2015 theo đúng luật BLIND) — riêng CHỈ với stress indicator tỷ giá (macro, không phải giá
  cổ phiếu): áp lực phá giá VND tiếp diễn hết 2015, buộc đổi cơ chế 04/01/2016 — bằng chứng
  EXTERNAL_CYCLE nêu trên tự nó đã trả lời câu hỏi "có hạ nhiệt nhanh không" mà không cần biết giá
  cổ phiếu.
- **chain_classification:** `INDEPENDENT`
- **analyst_notes:** So với EP-2014-09 (oil, cùng nhóm CONFIDENCE_LIQUIDITY/EXTERNAL_CYCLE, cùng
  năm liền kề): điểm khác biệt là episode này có MỘT phản ứng chính sách trong nước NHANH VÀ CỤ THỂ
  (SBV hành động trong vòng 1-8 ngày) — nhưng phản ứng đó chỉ xử lý được TRIỆU CHỨNG (tỷ giá tức
  thời), không xử lý được NGUYÊN NHÂN GỐC (chu kỳ TQ + Fed) — đây là lý do phân biệt với case
  CONTAINABLE thật (SCB 2022: hành động NHẮM ĐÚNG nguyên nhân gốc — 1 ngân hàng cụ thể — và stress
  indicator liên quan hạ nhiệt trong vài tháng). Bài học phương pháp: "có phản ứng chính sách
  nhanh" KHÔNG tự động nghĩa là CONTAINABLE — phải kiểm tra thêm liệu STRESS INDICATOR có thực sự
  hạ nhiệt sau đó hay tiếp tục đến mức phải redesign cơ chế.

---

## EP-2018-01 — US-China Trade War / EM Risk-Off Correction

**Cửa sổ episode:** 01/2018 (thị trường VN correction bắt đầu từ đỉnh ~1200) → 12/2018 (giá ổn
định lại ở mức thấp hơn). **Lưu ý quan trọng: Đây KHÔNG phải khủng hoảng macro VN — đây là điều
chỉnh thị trường do ngoại lực trong bối cảnh vĩ mô VN rất khỏe.**

**Trigger đã biết PIT:** VN-Index đạt đỉnh ~1200 (04/2018) → correction mạnh. Bối cảnh ngoại sinh:
lo ngại thương mại Mỹ-Trung leo thang từ tháng 3/2018, Fed tighten (4 lần nâng lãi suất 2018),
EM-wide selloff (USD mạnh lên, vốn rút khỏi EM). Bối cảnh VN: GDP 7.08% (cao nhất 10 năm), lạm
phát bình quân 3.5% — macro rất khỏe.

### Trục 1: `CONFIDENCE_LIQUIDITY` — confidence: **ambiguous**

Phân loại AMBIGUOUS vì:
- **Không có bằng chứng CPI/tín dụng nội địa xấu trước:** VN GDP 7.1% (2018), lạm phát 3.5%,
  không có dấu hiệu overheating nội địa. Nguồn: World Bank Vietnam Economic Update 2018.
- **SBV KHÔNG thay đổi chính sách tiền tệ thực chất** trong năm 2018 để ứng phó — bằng chứng SBV
  không thấy đây là khủng hoảng macro nội địa.
- **Tuy nhiên trigger là ngoại sinh (trade war + Fed cycle)** = external shock, không phải confidence
  shock VN-specific có trigger cụ thể (không có "SCB" hay "Tân Hoàng Minh" tương đương).
- **VN thực tế ĐƯỢC LỢI từ trade war** (diverting trade flows từ Trung Quốc sang VN) — làm yếu lập
  luận "external shock gây macro crisis VN". Nguồn: ISEAS Perspective 2019-102.

**Phân loại thực dụng:** `CONFIDENCE_LIQUIDITY / EXTERNAL_SHOCK` với mức độ nghiêm trọng thấp.
Đây chủ yếu là market correction (valuation reset sau run-up 2017), không phải macro crisis.

### Trục 2: `EXTERNAL_CYCLE` — confidence: **clean** (ĐÍNH CHÍNH 2026-08-30, Bobby, đọc BLIND)

**Nhãn cũ `CONTAINABLE` (2026-08-25) SAI so với định nghĩa khung.** Khung định nghĩa CONTAINABLE
= "giải quyết bằng MỘT hành động chính sách VN tự thực thi trong tuần-tháng"; EXTERNAL_CYCLE =
"gắn xu hướng ngoài VN không kiểm soát được, không có mốc VN tự quyết thời điểm kết thúc".
2018 thuộc vế SAU một cách rõ ràng:
- Nguồn áp lực = chu kỳ Fed-hiking (4 lần nâng 2018: 21/03, 13/06, 26/09, 19/12) + trade war
  Mỹ-Trung (Section 301 22/03/2018 → thuế 06/07 → US$200 tỷ 24/09) — cả hai đa-tháng/đa-năm,
  ngoài tầm VN.
- KHÔNG tồn tại hành động chính sách VN nào kết thúc được áp lực (SBV chỉ phòng thủ tỷ giá);
  áp lực chỉ hạ khi Fed pivot đầu 2019 — sự kiện NGOẠI, VN không quyết được thời điểm.
- Nhãn cũ đã trộn 2 khái niệm: "VN không bị kéo vào vòng xoáy tự cộng dồn" (đúng — đó là kết
  luận TRỤC 1: không structural) với "containable" (sai — trục 2 hỏi AI kiểm soát được trigger).
Lưu ý sizing: theo mandate margin Loại-2 (2026-08-25), EXTERNAL_CYCLE KHÔNG thỏa điều kiện
"policy anchor rõ" — 2018 không phải Loại-2 chuẩn như 2020/2022.

### Tổng kết EP-2018-01
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `CONFIDENCE_LIQUIDITY` (external shock EM-wide) | ambiguous |
| 2. Containability | `EXTERNAL_CYCLE` (Fed cycle + trade war, VN không kiểm soát; đính chính 2026-08-30) | clean |

- **shock_origin:** 03/2018 (thương mại Mỹ-Trung leo thang đầu tiên)
- **policy_response_start:** N/A (không cần phản ứng macro-stabilization)
- **recovery_confirmed:** Q1 2019 (thị trường ổn định, GDP vẫn >7%)
- **chain_classification:** `INDEPENDENT`
- **analyst_notes:** Episode này là NGOẠI LỆ quan trọng — nó KHÔNG nằm trong cụm 2007-2012 vì VN's
  macro fundamentals năm 2018 rất tốt (GDP 7.1%, inflation 3.5%, current account surplus, growing FX
  reserves). Nếu dùng episode này trong phân tích statistical về "macro stress → return", cần ĐÁNH
  DẤU THẤP hơn về severity so với 2007-2012 hay 2022 vì nền kinh tế thực không bị stress.

---

## EP-2020-02 — COVID-19 External Pandemic Shock

**Cửa sổ episode:** 02/2020 (VN xác nhận ca COVID đầu tiên, lockdown quốc gia lần 1) → 12/2021
(vaccine coverage đủ để tái mở cửa, GDP phục hồi). Gồm 2 giai đoạn: giai đoạn kiểm soát tốt 2020
và giai đoạn Delta Wave Q3 2021.

**Trigger đã biết PIT:** COVID-19 pandemic (ngoại sinh hoàn toàn). VN kiểm soát tốt ban đầu: GDP
+2.9% năm 2020 (một trong những nền kinh tế tốt nhất châu Á). Delta wave tấn công Q3 2021 → GDP
quý -6.17% QoQ (lockdown cứng TP.HCM và các tỉnh phía Nam). Vaccine rollout bắt đầu H1 2021, đủ
coverage để mở cửa Q4 2021.

### Trục 1: `CONFIDENCE_LIQUIDITY` — confidence: **clean**

- **CPI KHÔNG có dấu hiệu xấu trước episode:** lạm phát 2019 = 2.79%, 2020 = 3.21% — hoàn toàn bình
  thường, không có tích lũy imbalance cơ cấu trước khi COVID tấn công.
- **Tín dụng KHÔNG bùng nổ trước COVID:** tăng trưởng tín dụng 2019 khoảng 13.5%, trong target bình
  thường của SBV. Không có dấu hiệu overheating nội địa.
- **Trigger là đại dịch ngoại sinh** — đúng mẫu "confidence/disruption shock với trigger CỤ THỂ".
- **Tính chất recovery phân biệt rõ:** VN 2020 là một trong ít nước GDP dương — nếu đây là STRUCTURAL
  thì đã không thể tăng trưởng được trong năm 2020. Nguồn: IMF Vietnam Article IV 2021.
- **SBV phản ứng với refi rate cut 150bp + disc rate cut 200bp** trong March-October 2020 — KHÔNG
  phải macro-stabilization program, mà là stimulus để support demand. Nguồn: IMF Vietnam 2021 report.

**Kết luận trục 1:** COVID là external shock thuần túy vào một nền kinh tế macro lành mạnh. ⇒
`CONFIDENCE_LIQUIDITY`.

### Trục 2: `CONTAINABLE` — confidence: **clean**

- **Cơ chế giải quyết TRỰC TIẾP và có tên gọi cụ thể:** vaccine + reopening. VN bắt đầu vaccine
  rollout từ Q1 2021, đạt coverage đủ để mở cửa Q4 2021/Q1 2022.
- **GDP phục hồi nhanh:** từ -6.17% (Q3 2021) → +5.22% (Q4 2021) → 8.02% (cả năm 2022). Thời gian
  từ đáy Delta wave đến recovery: ~2 quý. Nguồn: S&P Global/GSO Vietnam GDP.
- **SBV chính sách KHÔNG cần kéo dài nhiều năm:** rate cuts 2020 → giữ nguyên 2021-2022 (trước khi
  SCB shock buộc nâng lại) — không có "multi-year tightening cycle" cần thiết cho STRUCTURAL.
- **Stress indicator (lãi suất huy động) KHÔNG leo thang sau COVID** — trái hoàn toàn với 2007-2012
  và 2022. Deposit rates tương đối ổn định 2020-H1 2022. Nguồn: `deposit_rate_vn.py` (BQ).

**Kết luận trục 2:** Giải quyết được bằng "một biện pháp cụ thể" (vaccine + reopening), thời gian
từ đáy đến recovery rõ ràng trong vòng 2-3 quý. ⇒ `CONTAINABLE`.

### Tổng kết EP-2020-02
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `CONFIDENCE_LIQUIDITY` | clean |
| 2. Containability | `CONTAINABLE` | clean |

- **shock_origin:** 01-02/2020 (COVID first cases VN, global pandemic declared 03/2020)
- **policy_response_start:** 03/2020 (SBV first rate cut; government lockdowns/support packages)
- **recovery_confirmed:** Q4 2021 (GDP growth resumed); 2022 (GDP 8.02%)
- **chain_classification:** `INDEPENDENT`
- **analyst_notes:** Có điểm tương đồng VỀ HÌNH THỨC với 2022 (cả hai là CONFIDENCE_LIQUIDITY /
  CONTAINABLE) nhưng CƠ CHẾ PHỤC HỒI hoàn toàn khác: COVID phục hồi nhờ vaccine (chính sách y tế),
  SCB/2022 phục hồi nhờ chính sách tiền tệ (rate cuts) + giải quyết trực tiếp 1 ngân hàng cụ thể.
  Đừng gộp chung — thời gian và mechanism hoàn toàn khác.

---

## EP-2022-05 — Tan Hoang Minh / SCB bank-run / Fed-hiking FX pressure

**Cửa sổ episode (do caller cung cấp, giá đã biết công khai tại thời điểm đó):** VNINDEX dd52
chạm ≤−20% khoảng tháng 05/2022, kéo dài tới giữa tháng 11/2022.

**Trigger đã biết PIT tại thời điểm episode** (công khai, không phải hindsight): vụ Tân Hoàng
Minh hủy 9 lô trái phiếu (04/2022); Trương Mỹ Lan/Vạn Thịnh Phát bị bắt (08/10/2022) → bank-run
SCB; SBV nâng lãi suất điều hành 2 lần liên tiếp 09-10/2022 (+100bp mỗi lần); Fed tăng lãi suất
mạnh gây áp lực VND; thị trường TPDN đóng băng sau Nghị định 65/2022.

### Trục 1: `CONFIDENCE_LIQUIDITY` — confidence: **clean**

Bằng chứng (đồng thuận, không mâu thuẫn nhau):
- **CPI KHÔNG vượt trần mục tiêu.** GSO: CPI bình quân cả năm 2022 = **3,16%** (trần Quốc hội
  giao là ~4%) — [Vietnam Inflation Rate — Trading Economics/GSO](https://tradingeconomics.com/vietnam/inflation-cpi).
- **Tín dụng KHÔNG vượt trần đáng kể.** SBV đặt mục tiêu tăng trưởng tín dụng 14% cho 2022, thực
  tế đạt **14,5%** — [SBV sets credit growth target to 14 per cent in 2022 — VIR](https://vir.com.vn/sbv-sets-credit-growth-target-to-14-per-cent-in-2022-90311.html).
- **Lãi suất huy động KHÔNG leo thang TRƯỚC episode.** `deposit_rate_vn.py`: lãi suất 12M đứng yên
  **5,5%** suốt 01/2021→01/2022, chỉ nhảy lên **6,8%** từ **10/2022** — XẢY RA SAU khi episode bắt
  đầu (05/2022) 5 tháng.
- **2 đợt nâng lãi suất điều hành (09-10/2022) để BẢO VỆ TỶ GIÁ**, không phải kiềm chế lạm phát
  nội địa — [Reuters/US News, 2022-10-24](https://money.usnews.com/investing/news/articles/2022-10-24/vietnam-cenbank-raises-policy-rates-by-100-bps).
  SBV bán >20 tỷ USD dự trữ ngoại hối để bảo vệ VND.
- Trigger có TÊN CỤ THỂ: 1 công ty bất động sản (Tân Hoàng Minh) + 1 ngân hàng cụ thể (SCB) + 1
  cá nhân (Trương Mỹ Lan).

**Kết luận trục 1:** ⇒ `CONFIDENCE_LIQUIDITY`.

### Trục 2: `CONTAINABLE` — confidence: **clean**

Ba nhánh trigger, MỖI nhánh có MỘT hành động chính sách nhắm đúng mục tiêu:
1. **SCB bank-run (08/10/2022)** → SBV đặt SCB vào "kiểm soát đặc biệt" ngay, bơm thanh khoản
   riêng cho NGÂN HÀNG ĐÓ — [CNBC/AsiaFinancial, 2024-04-17](https://www.cnbc.com/2024/04/17/vietnam-mounts-unprecedented-24-billion-rescue-for-bank-engulfed-in-giant-fraud-documents-show.html).
2. **Đóng băng TPDN** → Nghị định 08/2023 (05/03/2023) nới lỏng điều kiện gia hạn trái phiếu —
   hành động pháp quy nhắm đúng 1 thị trường — [Allens/KPMG, 2023-03](https://www.allens.com.au/insights-news/insights/2023/03/Vietnams-new-regulations-on-corporate-bonds).
3. **Áp lực Fed-hiking** → SBV nâng 09-10/2022 rồi CẮT ngay 15/03/2023 (lần đầu từ 2020) —
   "Vietnam was one of the first countries in the world to cut policy rates while many other central
   banks were still tightening" — [Bao Chinh Phu, 2023-03-15](https://en.baochinhphu.vn/central-bank-cuts-rates-for-first-time-in-two-years-111230315105215919.htm).

**Kết luận trục 2:** ⇒ `CONTAINABLE`.

### Tổng kết EP-2022-05
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `CONFIDENCE_LIQUIDITY` | clean |
| 2. Containability | `CONTAINABLE` | clean |

- **shock_origin:** 04/2022 (Tân Hoàng Minh vụ trái phiếu)
- **policy_response_start:** 08/10/2022 (SBV kiểm soát đặc biệt SCB); 09-10/2022 (rate hike FX
  protection)
- **recovery_confirmed:** 03/2023 (SBV rate cut, signaling stress over); 06/2023 (CPI về 2%)
- **chain_classification:** `INDEPENDENT`
- **analyst_notes:** So sánh với 2011-2012: trong 2022, CPI và tín dụng ở mức bình thường TRƯỚC và
  TRONG episode — đây là điểm khác biệt cơ bản với 2011-2012 (lạm phát đã tích lũy nhiều quý trước
  khi đạt đỉnh). Mức độ nghiêm trọng của vụ SCB (tổng tài sản ~1.1 triệu tỷ VND) rất lớn, nhưng
  việc giải quyết theo cơ chế "1 ngân hàng cụ thể bị kiểm soát đặc biệt" vẫn là CONTAINABLE —
  không lây lan thành systemic banking crisis.

---

## EP-2023-09 — VND FX-Defense Liquidity Drain / VIC-VHM Overhang / Margin Unwind (VNINDEX −17,45%, 2023-09-06→2023-10-31)

**Cửa sổ episode (do caller cung cấp, dd52/arm-trigger, KHÔNG kèm forward-return):** VNINDEX
giảm −17,45% trong 39 phiên, 2023-09-06 → 2023-10-31.

**Trigger đã biết PIT (công khai tại thời điểm đó, nguồn contemporaneous — VinaCapital Economist's
Note, xuất bản 09/11/2023, tức chỉ ~1 tuần sau khi episode kết thúc — trích dẫn CHỈ phần nguyên
nhân nhân quả, KHÔNG trích phần dự báo/khuyến nghị đầu tư của báo cáo để giữ đúng luật BLIND):**
3 yếu tố đặc thù VN + 1 yếu tố toàn cầu, theo VinaCapital
([PDF, 2023-11-09](https://vinacapital.com/wp-content/uploads/2023/11/VinaCapital-Insights-Reasons-for-VN-Indexs-Steep-Correction-of-16.pdf)):
1. **Áp lực phá giá VND** → lo ngại SBV sẽ thắt chặt tiền tệ mạnh (kể cả khả năng nâng lãi suất
   điều hành) → một phần bán ra của khối ngoại.
2. **Trái phiếu chuyển đổi (CB) USD250 triệu của Vingroup** (công bố 26/10/2023, hoán đổi sang cổ
   phiếu Vinhomes-VHM) — VIC+VHM chiếm ~10% VN-Index; sự kiện 1 công ty cụ thể.
3. **Margin call của các CTCK** từ đầu tháng 09/2023 + tin đồn thanh tra 1 nguồn cho vay margin phi
   chính thức, dẫn tới thanh lý vị thế đòn bẩy nhanh ngày 17/10/2023.
4. **Yếu tố toàn cầu:** lợi suất trái phiếu Kho bạc Mỹ kỳ hạn 10 năm tăng 60bp (giữa 09→cuối
   10/2023, đúng khung "higher for longer" của Fed) + căng thẳng địa chính trị → MSCI-EM Index
   giảm 5% cùng kỳ. VinaCapital ghi nhận rõ VNINDEX **giảm mạnh hơn ĐÁNG KỂ** so với nhóm EM khu
   vực (THB/PHP/IDR/MYR) trong cùng cửa sổ — cho thấy yếu tố ĐẶC THÙ VN (mục 1-3) là driver chính,
   yếu tố toàn cầu là driver phụ.

### Trục 1: `CONFIDENCE_LIQUIDITY` — confidence: **clean**

- **CPI hoàn toàn trong tầm kiểm soát, KHÔNG xấu đi nhiều quý trước episode.** `cpi_vn.py`: CPI
  YoY chạm đáy 2,0% (06/2023) rồi nhích nhẹ lên **2,80% (09/2023)** → **3,07% (10/2023)** — vẫn
  cách xa trần mục tiêu Quốc hội ~4,5%. Đây là mức phục hồi từ đáy thấp, KHÔNG phải tích lũy
  overheating multi-quarter.
- **Tín dụng YẾU, không phải bùng nổ** — tăng trưởng tín dụng giảm tốc từ 9,4% YoY (08/2023) xuống
  **8,7% YoY (09/2023)**, thấp hơn nhiều so với chuẩn thông thường (~13-14%/năm) — "excess
  liquidity in banking system", đối lập hoàn toàn với mẫu STRUCTURAL (tín dụng phải VƯỢT trần).
- **SBV đang trong chu kỳ CẮT lãi suất, không phải thắt chặt** — cắt tổng **150bp** từ tháng
  03→06/2023 (5,5%→4,5%), đúng lúc Fed vẫn giữ lãi suất cao — chính SỰ KHÁC BIỆT chính sách này
  (không phải lạm phát nội địa) mới là nguồn gốc áp lực tỷ giá: "the SBV's aggressive rate cuts in
  H1 left short term interest rates in Vietnam a record 500bps below short-term USD interest
  rates" — VinaCapital (trên).
- **Lãi suất huy động (`deposit_rate_vn.py`) giảm đều suốt cả năm 2023:** 7,2% (03/2023) → 6,3%
  (06/2023) → 5,5% (09/2023) → 5,0% (12/2023) — hướng đi hoàn toàn ngược với một cú sốc bank-
  run/thanh khoản nội địa (lẽ ra lãi suất huy động phải NHẢY LÊN để giữ tiền gửi).
- **GDP đang phục hồi rõ rệt trong episode, không suy thoái:** 3,3% (Q1) → 4,1% (Q2) → **5,3%
  (Q3/2023)** YoY — nền kinh tế thực đang cải thiện đồng thời với đợt bán tháo cổ phiếu, một dấu
  hiệu kinh điển của "cú sốc niềm tin/thanh khoản trên nền vĩ mô ổn định" chứ không phải khủng
  hoảng thực.
- Cả 3 yếu tố đặc thù VN đều có TÊN CỤ THỂ (SBV/tỷ giá, 1 công ty — Vingroup/Vinhomes, margin của
  CTCK) — không phải bằng chứng mất cân đối vĩ mô lan tỏa.

**Kết luận trục 1:** Không có chỉ tiêu STRUCTURAL nào (CPI, tín dụng, lãi suất huy động) xấu đi —
ngược lại tất cả đang trong xu hướng NỚI LỎNG/phục hồi. Trigger là tổ hợp: áp lực tỷ giá do CHÊNH
LỆCH LÃI SUẤT (bản thân là hệ quả của một lựa chọn chính sách cắt lãi suất, không phải lạm phát),
1 sự kiện phát hành trái phiếu của 1 công ty, và 1 đợt thanh lý margin. ⇒ `CONFIDENCE_LIQUIDITY`.

### Trục 2: `CONTAINABLE` (dominant) pha trộn với 1 thành phần `EXTERNAL_CYCLE` phụ — confidence:
**ambiguous**

Bằng chứng CONTAINABLE (3 yếu tố đặc thù VN, mỗi yếu tố có cơ chế tự giải quyết/công cụ nhắm đúng
mục tiêu trong episode hoặc ngay sau đó):
- **SBV hút ròng ~USD9 tỷ thanh khoản VND qua kênh tín phiếu (OMO) từ 21/09/2023 đến hết
  10/2023** — công cụ CỤ THỂ, nhắm đúng mục tiêu (bảo vệ tỷ giá qua thanh khoản, KHÔNG cần nâng lãi
  suất điều hành) — VinaCapital: "the SBV drained nearly USD9 billion... but it did not hike
  policy interest rates to protect the currency."
- **Nới biên độ giao dịch tỷ giá từ ±3% lên ±5%** ngày **17/10/2023** — một cơ chế linh hoạt hóa cụ
  thể, tương tự logic 2015 nhưng lần này ĐI KÈM bằng chứng ổn định hóa NHANH: theo báo cáo xuất
  bản chỉ 1 tuần sau khi episode kết thúc, "the USD-VND exchange rate has stabilized at current
  levels for the past several weeks without the SBV having to resort to rate hikes" — khác hẳn
  case 2015 (phải redesign cơ chế 4 tháng sau, phá giá tiếp tục cả năm).
- **Margin liquidation là cơ chế TỰ GIỚI HẠN** — theo đúng bản chất một đợt xả đòn bẩy: một khi vị
  thế bị thanh lý hết, áp lực bán tự nhiên chấm dứt, không cần một hành động chính sách riêng.
- **Overhang trái phiếu chuyển đổi VIC/VHM là sự kiện 1 lần** — VinaCapital ghi nhận "hedge selling
  by CB arb funds tends to be temporary."

Bằng chứng KÉO NGƯỢC về `EXTERNAL_CYCLE` (lý do đánh dấu ambiguous, không phải clean):
- **Một phần nguyên nhân gốc của áp lực tỷ giá là "higher for longer" — chu kỳ lãi suất Fed đa
  năm mà VN không kiểm soát được thời điểm kết thúc.** DXY tăng 6-7% (giữa 07→đầu 10/2023) + UST
  10Y +60bp cùng kỳ là bối cảnh toàn cầu, không phải VN tự quyết. Nếu Fed tiếp tục "cao hơn lâu
  hơn", SBV có thể phải quay lại thắt chặt bất cứ lúc nào — đây chính xác là loại rủi ro
  EXTERNAL_CYCLE (không có mốc VN tự quyết định thời điểm kết thúc).
- **VNINDEX giảm mạnh hơn EM peer trung bình ~2 lần** (per chart VinaCapital: EM peers ~−5% vs
  VNINDEX −16% cùng cửa sổ) — nghĩa là yếu tố ĐẶC THÙ VN (CONTAINABLE) chiếm phần LỚN hơn, nhưng
  không loại trừ hoàn toàn thành phần EXTERNAL_CYCLE.

**Kết luận trục 2:** Phần lớn cường độ episode (VN underperform EM ~2×) đến từ 3 yếu tố CONTAINABLE
có công cụ/cơ chế giải quyết cụ thể và có bằng chứng ổn định hóa nhanh (vài tuần) — nhưng một phần
thực sự gắn với chu kỳ Fed "higher for longer" ngoài tầm kiểm soát VN. ⇒ `CONTAINABLE` (chiếm ưu
thế), confidence **ambiguous** do có hợp phần EXTERNAL_CYCLE thật không tách rời được hoàn toàn.

### Tổng kết EP-2023-09
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `CONFIDENCE_LIQUIDITY` | clean |
| 2. Containability | `CONTAINABLE` (dominant, pha trộn EXTERNAL_CYCLE phụ — Fed "higher for longer") | ambiguous |

- **shock_origin:** giữa 09/2023 (áp lực VND bắt đầu rõ + margin call sớm từ CTCK); 21/09/2023
  (SBV bắt đầu hút ròng thanh khoản qua tín phiếu — điểm chính sách rõ nhất)
- **policy_response_start:** 21/09/2023 (hút thanh khoản qua tín phiếu); 17/10/2023 (nới biên độ
  tỷ giá ±3%→±5%)
- **recovery_confirmed:** không xác định trong phạm vi phân tích BLIND này (đọc dừng ở
  31/10/2023) — RIÊNG với stress indicator tỷ giá (macro, không phải giá cổ phiếu): báo cáo
  contemporaneous (09/11/2023, ~1 tuần sau episode) đã xác nhận tỷ giá "ổn định vài tuần" mà không
  cần nâng lãi suất điều hành — khác biệt rõ với case 2015 (phải đổi cơ chế 4 tháng sau).
- **chain_classification:** `INDEPENDENT`
- **analyst_notes:** Case pha trộn hiếm — vừa có thành phần CONTAINABLE rõ ràng (công cụ SBV cụ
  thể + tự giới hạn của margin/CB overhang, tương tự tinh thần 2022 SCB) vừa có thành phần
  EXTERNAL_CYCLE thật (Fed "higher for longer", tương tự 2018). Khác 2015 (cũng có phản ứng chính
  sách nhanh nhưng KHÔNG ngăn được stress tiếp diễn) — 2023 có bằng chứng ổn định hóa NHANH và
  THẬT trong vòng vài tuần, đây là điểm phân biệt hai case tưởng giống nhau về hình thức (đều là
  "SBV phản ứng nhanh với tỷ giá") nhưng khác nhau về HIỆU QUẢ đo được. Không nên gộp case này với
  2018/2015 (EXTERNAL_CYCLE clean) hay với 2022 (CONTAINABLE clean) — nó nằm giữa, và gắn nhãn
  ambiguous là lựa chọn trung thực hơn ép về một cực.

---

## EP-2025-03 — Trump "Liberation Day" Reciprocal Tariff Shock (VNINDEX −18,11%, 2025-03-17→2025-04-09, chỉ 16 phiên)

**Cửa sổ episode (do caller cung cấp, dd52/arm-trigger, KHÔNG kèm forward-return):** VNINDEX
giảm −18,11% trong CHỈ 16 phiên, 2025-03-17 → 2025-04-09 — tốc độ giảm nhanh nhất trong 5 episode
được giao lần này.

**Trigger đã biết PIT:** Một câu chuyện DUY NHẤT, tiến triển liên tục suốt cả cửa sổ, không phải
2 sự kiện tách rời:
- **Giữa 02→giữa 03/2025:** S&P 500 giảm từ đỉnh 19/02, chính thức vào vùng "correction" (−10,1%)
  ngày **13/03/2025**, do lo ngại chiến tranh thương mại toàn cầu và nguy cơ suy thoái Mỹ từ các
  đe dọa thuế quan của Trump — [Oakmark
  Funds](https://oakmark.com/news-insights/the-sp-500-has-corrected-now-what-u-s-equity-market-commentary-1q-2025/);
  Forbes ghi nhận "growing fears of higher tariffs and a trade war... increase the odds of a
  policy-induced recession" — [Forbes,
  2025-03-16](https://www.forbes.com/sites/bill_stone/2025/03/16/facts-about-the-stock--corrections-tariffs-and-consumer-confidence/).
  Đây là bối cảnh NGAY TRƯỚC ngày bắt đầu episode (17/03/2025) — cùng MỘT mạch nguyên nhân, không
  phải nguyên nhân riêng.
- **02/04/2025 ("Liberation Day"):** Chính quyền Trump công bố thuế đối ứng cơ sở 10% cho hầu hết
  các nước, kèm mức thuế "đối ứng" cao hơn cho các nước có thặng dư thương mại lớn với Mỹ — Việt
  Nam nhận mức **46%**, cao thứ 5 toàn cầu (Trung Quốc 34%, Ấn Độ 26%) — [Yahoo
  Finance/CBS News tổng
  hợp](https://finance.yahoo.com/news/heres-every-country-facing-reciprocal-tariffs-announced-by-trump-on-liberation-day-231329935.html).
- **09/04/2025:** mức thuế 46% CHÍNH THỨC có hiệu lực — trùng NGÀY CUỐI episode. VNINDEX mất
  87,99 điểm (−6,68%) trong phiên, mức giảm mạnh nhất lịch sử tính theo điểm — [Vietnam News,
  "Stock market plunges as US imposes 46%
  tariff"](https://vietnamnews.vn/economy/1695173/stock-market-plunges-as-us-imposes-46-tariff.html);
  [The Investor,
  2025-04](https://theinvestor.vn/vietnams-benchmark-vn-index-records-sharpest-fall-in-history-following-president-trumps-tax-announcement-d15138.html).
  Cùng ngày, Phó Thủ tướng Hồ Đức Phớc gặp trực tiếp USTR Jamieson Greer tại Washington — [Radio
  Free Asia,
  2025-04-10](https://www.rfa.org/english/vietnam/2025/04/10/us-trade-talks-tariff-cuts/).

### Trục 1: `CONFIDENCE_LIQUIDITY` — confidence: **clean**

- **CPI hoàn toàn trong tầm kiểm soát, không có tích lũy trước episode:** CPI Q1/2025 = **3,22%**
  YoY, lạm phát lõi 3,01% — mức bình thường, cách xa trần mục tiêu — [Vietnam Briefing, "Vietnam's
  Economy in H1
  2025"](https://www.vietnam-briefing.com/news/vietnams-economic-performance-in-h1-2025-inflation-trade-fdi.html/).
- **Lãi suất huy động vẫn THẤP VÀ ỔN ĐỊNH tại thời điểm episode:** `deposit_rate_vn.py` — 4,7%
  (04/2024) → **4,8% (01/2025, ngay trước episode)**, chỉ bắt đầu nhích lên 5,2% từ 09/2025 — TẠI
  THỜI ĐIỂM episode (03-04/2025) hoàn toàn KHÔNG có dấu hiệu căng thẳng huy động vốn — khác biệt rõ
  với EP-2026-01 (nơi lãi suất huy động đã tăng liên tục 12 tháng trước episode).
- **SBV đang trong chính sách NỚI LỎNG, không phải thắt chặt:** "SBV maintaining policy rates near
  record lows since early 2023 to support the recovery" — [Vietnam Briefing/OECD tổng
  hợp](https://www.vietnam-briefing.com/news/vietnam-gdp-fdi-and-trade-2025.html/).
- **GDP tăng trưởng khỏe:** 7,52% (H1/2025), nối tiếp đà 7,09% (2024) — nền kinh tế thực đang tốt,
  không có dấu hiệu suy yếu nội tại đồng thời với episode.
- **Tín dụng ĐANG tăng tốc (15% năm 2024 → 19% YoY tháng 06/2025) nhưng CHƯA tạo ra funding stress
  quan sát được tại thời điểm episode** (lãi suất huy động còn thấp, ổn định) — khác EP-2026-01 rõ
  rệt: ở đây xu hướng tăng tốc tín dụng mới ở giai đoạn ĐẦU, chưa đủ thời gian (nhiều quý) để
  crystallize thành một chỉ báo STRUCTURAL độc lập với CPI/lãi suất huy động. Ghi nhận đây là điểm
  CẦN THEO DÕI cho các episode SAU episode này trong chuỗi 2025-2026 (khớp với việc EP-2026-01, chỉ
  9-10 tháng sau, đã cho thấy đúng chỉ báo funding-stress này crystallize).
- **Trigger có tên, có ngày, có con số cụ thể: 1 quyết định chính sách thương mại của TỔNG THỐNG
  MỘT NƯỚC KHÁC** (Trump, 02/04/2025, 46% cho VN) — không phải bằng chứng mất cân đối vĩ mô nội
  địa dưới bất kỳ hình thức nào.

**Kết luận trục 1:** Không một chỉ tiêu STRUCTURAL nào (CPI, lãi suất huy động, chính sách SBV)
cho thấy dấu hiệu xấu đi trước hay trong episode; nền vĩ mô nội địa lành mạnh, chính sách tiền tệ
đang nới lỏng. Trigger 100% ngoại sinh, có tên cụ thể. ⇒ `CONFIDENCE_LIQUIDITY`.

### Trục 2: `CONTAINABLE` (cho tranh chấp cụ thể) pha trộn `EXTERNAL_CYCLE` (cho rủi ro nền) —
confidence: **ambiguous**

Bằng chứng CONTAINABLE — khác biệt cốt lõi so với EP-2014-09 (OPEC, VN hoàn toàn không có đòn bẩy
đàm phán) và giống EP-2022-05 (SCB) về CẤU TRÚC phản ứng (có MỘT kênh xử lý cụ thể, nhắm đúng mục
tiêu):
- **VN có quan hệ song phương trực tiếp với Mỹ và sử dụng ngay lập tức:** Phó Thủ tướng Hồ Đức
  Phớc gặp Bộ trưởng Tài chính Bessent + Bộ trưởng Thương mại Lutnick tại Washington **09-
  11/04/2025**, đúng ngày/hôm sau khi thuế có hiệu lực — [Bloomberg,
  2025-04-11](https://www.bloomberg.com/news/articles/2025-04-11/vietnam-deputy-pm-meets-bessent-lutnick-to-push-trade-deal).
  Ngày 11/04/2025, VN chính thức lập đoàn đàm phán riêng — [Chính phủ VN, tổng hợp qua RFA/globalsecurity].
- **Cơ chế tạm hoãn 90 ngày cho phép một cửa sổ đàm phán cụ thể, có deadline rõ** — không phải một
  chu kỳ đa năm không có điểm neo thời gian.
- **Kênh xử lý (đàm phán song phương Việt-Mỹ) khác về BẢN CHẤT với EP-2014-09 (OPEC — VN không là
  thành viên, không có ghế đàm phán) và khác EP-2015-07/2018/EP-2023-09-phần-Fed (chính sách tiền
  tệ Mỹ — VN hoàn toàn là bên nhận, không đàm phán được với Fed).** Ở đây VN LÀ một bên trực tiếp
  trong tranh chấp, có kênh ngoại giao song phương chính thức để tác động vào chính KẾT QUẢ của
  trigger — không chỉ ứng phó hậu quả (như can thiệp tỷ giá) mà có thể thay đổi CHÍNH mức thuế gốc.

Bằng chứng kéo về `EXTERNAL_CYCLE` (lý do đánh dấu ambiguous):
- **Nguyên nhân gốc (chính sách thương mại đơn phương, khó đoán của một chính quyền Mỹ cụ thể) là
  rủi ro TÁI DIỄN, không phải một sự kiện một lần.** Bản chất "thuế quan theo quyết định hành pháp,
  có thể thay đổi bất cứ lúc nào" khác về cấu trúc với "1 ngân hàng cụ thể vỡ nợ rồi được kiểm soát
  đặc biệt" (SCB) — không có gì đảm bảo tranh chấp thuế quan mới không phát sinh lại (đã có tín
  hiệu cho thấy chủ đề thuế quan Mỹ-VN tiếp tục xuất hiện trong tin tức các quý sau đó — không đi
  sâu vào đây vì đó là thông tin SAU cửa sổ episode, chỉ ghi nhận như một đặc điểm CẤU TRÚC của
  loại rủi ro này, không phải bằng chứng forward-return).
- **VN không kiểm soát được QUYẾT ĐỊNH GỐC** (mức thuế 46% là do Nhà Trắng đơn phương ấn định) —
  chỉ có thể đàm phán để GIẢM NHẹ sau khi đã bị áp, không ngăn được từ đầu. Khác hẳn SCB (VN toàn
  quyền quyết định thời điểm/cách xử lý ngân hàng của chính mình).

**Kết luận trục 2:** Với ĐÚNG tranh chấp cụ thể trong episode này, VN có kênh đàm phán song phương
trực tiếp và đã sử dụng ngay — cấu trúc CONTAINABLE. Nhưng bản chất rủi ro nền (chính sách thương
mại đơn phương khó đoán từ 1 cường quốc) là một loại EXTERNAL_CYCLE mà VN không quyết định được
liệu có tái diễn. ⇒ `CONTAINABLE` (cho đúng tranh chấp này), confidence **ambiguous** (do tính chất
tái diễn của loại rủi ro nền).

### Tổng kết EP-2025-03
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `CONFIDENCE_LIQUIDITY` | clean |
| 2. Containability | `CONTAINABLE` (đúng tranh chấp cụ thể; rủi ro nền mang tính EXTERNAL_CYCLE tái diễn) | ambiguous |

- **shock_origin:** giữa 02/2025 (S&P 500 bắt đầu điều chỉnh vì lo ngại thuế quan); **02/04/2025**
  ("Liberation Day" — điểm gãy dứt khoát nhất, có tên, có số cụ thể: 46% cho VN)
- **policy_response_start:** **09/04/2025** (Phó TT Hồ Đức Phớc gặp Bessent/Greer tại Washington,
  đúng ngày thuế có hiệu lực); **11/04/2025** (VN lập đoàn đàm phán chính thức)
- **recovery_confirmed:** không xác định trong phạm vi phân tích BLIND này về mặt CHỈ SỐ THỊ
  TRƯỜNG (đọc dừng ở 09/04/2025) — riêng về mặt CHÍNH SÁCH THUẾ QUAN (đây là stress indicator của
  chính trigger, không phải giá cổ phiếu, nên hợp lệ theo phương pháp trục 2 của khung phân loại):
  cơ chế tạm hoãn 90 ngày tạo cửa sổ đàm phán rõ ràng — không đi sâu hơn để tránh chạm thông tin
  SAU episode không cần thiết cho việc phân loại 2 trục.
- **chain_classification:** `INDEPENDENT`
- **analyst_notes:** Case này là minh chứng RÕ NHẤT cho việc "trigger 100% ngoại sinh" KHÔNG tự
  động đồng nghĩa EXTERNAL_CYCLE ở trục 2 — điểm phân biệt quyết định là VN có phải MỘT BÊN có ghế
  đàm phán trực tiếp trong chính trigger đó hay không (có ở đây và ở SCB 2022; không có ở OPEC 2014
  hay chu kỳ Fed 2015/2018/2023). Đây cũng là episode NHANH NHẤT (16 phiên) trong 5 episode được
  giao — tốc độ nhanh phù hợp với một cú sốc chính sách CÓ NGÀY HIỆU LỰC CỤ THỂ (không phải một quá
  trình tích lũy dần như STRUCTURAL). So với EP-2026-01 (9-10 tháng sau): tại thời điểm episode này
  (03-04/2025), tín dụng đang tăng tốc NHƯNG CHƯA đủ thời gian tích lũy để tạo funding stress quan
  sát được — một minh họa hữu ích cho việc XU HƯỚNG credit boom cần NHIỀU QUÝ mới chuyển từ "đang
  tăng tốc" (chưa đủ bằng chứng STRUCTURAL) sang "đã tạo áp lực huy động rõ ràng" (đủ bằng chứng).

---

## EP-2026-01 — Domestic Credit/Real-Estate Build-up + Middle East War Oil Shock (VNINDEX −16,38%, 2026-01-13→2026-03-23)

**Cửa sổ episode (do caller cung cấp, dd52/arm-trigger, KHÔNG kèm forward-return; đọc BLIND, KHÔNG
tham chiếu diễn biến sau 23/03/2026 kể cả đỉnh 18/05/2026 hay episode "07/2026" của fleet):** VNINDEX
giảm −16,38% trong 44 phiên, 2026-01-13 → 2026-03-23.

**Trigger đã biết PIT — HAI lớp riêng biệt, khác thời điểm bắt đầu:**
- **Lớp nội địa (đã tích lũy TRƯỚC episode, không phải phát sinh trong episode):** tín dụng hệ
  thống 2025 đạt **~19%** — cao nhất 5 năm, vượt mục tiêu thường lệ ~15% — [The Investor,
  "Vietnam's credit growth to hit 19% in 2025, highest in many years: central
  bank"](https://theinvestor.vn/vietnams-credit-growth-to-hit-19-in-2025-highest-in-many-years-central-bank-d17989.html).
  Riêng **tín dụng bất động sản tăng ~36% trong 2025** — [tổng hợp báo chí ngành BĐS/lãi suất
  2026]. SBV phản ứng bằng cách **giới hạn tín dụng BĐS quý 1/2026 ở mức 25% hạn mức cả năm** và
  siết kiểm soát riêng lĩnh vực này, đặt mục tiêu tín dụng cả năm 2026 hạ về ~15% — [VietnamNet,
  "Vietnam targets 15% credit growth in 2026 with tighter real estate
  control"](https://vietnamnet.vn/en/vietnam-targets-15-credit-growth-in-2026-with-tighter-real-estate-control-2480915.html).
- **Lớp ngoại sinh (bắt đầu ~đầu 03/2026, muộn hơn nhiều so với đầu episode 13/01/2026):** chiến
  tranh Israel-Iran-Mỹ leo thang đầu tháng 03/2026 → Brent vượt $100/thùng (từ ~$70-80 trước đó) →
  VN nhập khẩu ~50% dầu thô, ~70% LPG, gần như toàn bộ LNG từ khu vực Trung Đông — kênh truyền dẫn
  chi phí nhập khẩu trực tiếp — [The Investor, 2026-03-12, "Middle East tensions weigh on
  Vietnam's stock market
  outlook"](https://theinvestor.vn/middle-east-tensions-weigh-on-vietnams-stock-market-outlook-d18574.html).
  VNINDEX giảm >115 điểm phiên 09/03/2026, giảm ~12% chỉ trong 6 phiên đầu tháng 3 — [Vietnam.vn,
  2026-03-12, "Chứng khoán tháng 3/2026: Vượt bão giá dầu, đón sóng nâng
  hạng"](https://www.vietnam.vn/en/chung-khoan-thang-3-2026-vuot-bao-gia-dau-don-song-nang-hang).

### Trục 1: `MIXED` (STRUCTURAL_ACCUMULATION giai đoạn sớm-giữa đang chạy + cú sốc dầu/chiến tranh
ngoại sinh mới) — confidence: **ambiguous**

Bằng chứng lớp STRUCTURAL đã tích lũy NHIỀU QUÝ trước episode (khác hẳn 3 episode trước — 2014,
2015, phần lớn 2023 — vốn có nền vĩ mô lành mạnh):
- **Tín dụng hệ thống 19% (2025) + tín dụng BĐS 36% (2025)** — đây là mức tăng KHÔNG bình thường,
  đủ để SBV phải ban hành biện pháp macro-prudential HỆ THỐNG (trần 25% hạn mức quý cho tín dụng
  BĐS toàn ngành, không phải xử lý 1 ngân hàng cụ thể) — đúng mẫu phản ứng STRUCTURAL (so sánh
  Resolution 11/2011: cap tín dụng toàn hệ thống <20%).
- **Lãi suất huy động TĂNG LIÊN TỤC suốt cả năm trước episode** — `deposit_rate_vn.py`: 4,8%
  (01/2025) → 5,2% (09/2025) → **6,0% (01/2026, đầu episode)** → 6,8% (06/2026) — hướng đi NGƯỢC
  HẲN với mọi episode CONFIDENCE_LIQUIDITY sạch đã phân loại trước đó (2014/2015/2020/phần lớn
  2023 đều có lãi suất huy động ổn định hoặc giảm). Xu hướng tăng bắt đầu từ ĐẦU 2025 — 12+ tháng
  trước episode — đúng tiêu chí "xấu đi nhiều quý trước, không phải phát sinh trong episode."
  Nguyên nhân: mortgage rate thương mại đã leo lên 12-13%/năm nửa đầu 2026 dù SBV giữ nguyên refi
  rate 4,5% — dấu hiệu tín dụng tăng nhanh hơn huy động (cầu vốn > cung vốn), đặc trưng giai đoạn
  cuối chu kỳ tín dụng bùng nổ.
- **GDP rất nóng:** 8,46% (Q4/2025) → 7,83% (Q1/2026) — mức tăng trưởng cao kéo dài, lịch sử VN
  (2007, 2010) cho thấy tốc độ ~8%/năm kéo dài thường đi kèm rủi ro tích lũy tín dụng/tài sản.
- **CPI tăng tốc RÕ RỆT ngay trong episode, một phần độc lập với cú sốc dầu:** `cpi_vn.py`: 2,53%
  (01/2026) → 3,35% (02/2026, TRƯỚC khi chiến tranh nổ ra ~đầu 03) → **4,65% (03/2026, mức YoY
  tháng 3 cao nhất 5 năm)**. Riêng bước nhảy 01→02/2026 (+0,82pp) xảy ra TRƯỚC cú sốc dầu, không
  thể quy hết cho chiến tranh — phù hợp với báo cáo contemporaneous 12/03/2026 ghi nhận "nền kinh
  tế đang bước vào giai đoạn thắt chặt thanh khoản và lãi suất tăng" do "áp lực từ số dư ngân khố
  nhà nước tại NHTM" và "tăng trưởng tiền gửi chậm lại đầu năm" — nguyên nhân THANH KHOẢN NỘI ĐỊA,
  không phải giá dầu.
- Khớp với đánh giá độc lập trước đó của chính vai trò này (không dùng làm bằng chứng chính, chỉ
  đối chiếu tính nhất quán): `kb/projects/vn-realestate-structural-risk-20260826.md` — phân loại
  **STRUCTURAL_ACCUMULATION giai đoạn sớm-giữa, KHÔNG CONTAINABLE bằng 1 can thiệp**, credit/GDP
  145%, BĐS/tổng dư nợ 25,5% (cận dưới).

Bằng chứng lớp NGOẠI SINH (khiến không thể gọi thẳng là STRUCTURAL thuần, phải là MIXED):
- **Chiến tranh Israel-Iran-Mỹ là sự kiện địa chính trị CỤ THỂ, có ngày, VN hoàn toàn không liên
  quan** — không phải hệ quả của chính sách hay mất cân đối nào của VN.
- **CPI ngay cả ở kịch bản xấu (Brent $100) vẫn được ước tính trong/quanh trần mục tiêu Chính phủ
  4-4,5%** (kịch bản 4,12-5,06% tùy giá dầu, theo báo cáo 12/03/2026) — không phải runaway
  inflation kiểu 2007-2008 (CPI 20%+).
- **Đánh giá chuyên gia contemporaneous (SSI Research, trích trong Vietnam.vn 12/03/2026):** "đợt
  bán tháo chủ yếu do yếu tố tâm lý/cảm xúc chứ không dựa trên biến số vĩ mô thực" — một đánh giá
  độc lập tại thời điểm đó nghiêng về CONFIDENCE/tâm lý hơn là fundamentals xấu đi.

**Kết luận trục 1:** Đây là case HIẾM thứ 2 (sau EP-2008-09) có 2 lớp nguyên nhân chồng chéo: một
imbalance tín dụng/BĐS nội địa ĐANG tích lũy (không phải mới, đã chạy suốt 2025) VÀ một cú sốc giá
dầu/chiến tranh ngoại sinh hoàn toàn mới xảy ra muộn hơn trong episode. Khác 2008-09 ở ĐỘ LỚN
(19%/36% tín dụng vẫn nhỏ hơn nhiều so với 53%/2007 hay 36-37%/2009; CPI 4,65% vẫn trong tầm kiểm
soát so với 23-28%/2008) — mức độ "sớm-giữa" chứ chưa "khủng hoảng đã crystallize". ⇒ `MIXED`,
confidence **ambiguous** (2 lớp nguyên nhân thật, không lớp nào chiếm ưu thế tuyệt đối trong đúng
44 phiên của episode — lớp nội địa giải thích ~2/3 đầu episode, lớp dầu/chiến tranh giải thích
~1/3 cuối).

### Trục 2: Không áp dụng thuần túy (MIXED tự thân có 2 timeline khác nhau)

- **Hợp phần ngoại sinh (dầu/chiến tranh):** giống cấu trúc `EXTERNAL_CYCLE`/2014 — VN không có
  đòn bẩy chính sách nào "sửa" được chiến tranh Trung Đông hay giá dầu toàn cầu; thời điểm kết
  thúc hoàn toàn phụ thuộc diễn biến địa chính trị bên ngoài.
- **Hợp phần nội địa (tín dụng/BĐS):** giống cấu trúc `MULTI_YEAR_STRUCTURAL` — biện pháp SBV (cap
  25% hạn mức quý cho BĐS, mục tiêu hạ tín dụng cả năm 2026 về 15%) là một chương trình
  macro-prudential ĐA QUÝ/ĐA NĂM (khớp với đánh giá timeline 3-7 năm ở
  `vn-realestate-structural-risk-20260826.md`), không phải một hành động dập tắt 1 trigger trong
  vài tuần như SCB 2022.

**Kết luận trục 2:** N/A theo đúng khung 2 trục thuần túy (chỉ áp dụng khi trục 1 = CONFIDENCE_
LIQUIDITY) — giống tiền lệ EP-2008-09. Ghi nhận tường minh 2 timeline khác nhau thay vì ép về 1
nhãn.

### Tổng kết EP-2026-01
| Trục | Kết luận | Confidence |
|---|---|---|
| 1. Root cause | `MIXED` (STRUCTURAL_ACCUMULATION nội địa đang chạy + EXTERNAL_SHOCK dầu/chiến tranh mới) | ambiguous |
| 2. Resolution | N/A — hợp phần ngoại sinh phụ thuộc diễn biến địa chính trị; hợp phần nội địa cần chương trình đa năm (không containable bằng 1 hành động) | — |

- **shock_origin:** trong-năm-2025 (tín dụng/BĐS bắt đầu tích lũy, không có 1 ngày cụ thể);
  đầu 03/2026 (chiến tranh Israel-Iran-Mỹ leo thang — điểm gãy ngoại sinh dứt khoát nhất)
- **policy_response_start:** đầu 2026 (SBV cap tín dụng BĐS quý 1 ở 25% hạn mức năm; mục tiêu tín
  dụng cả năm hạ về ~15%) — hành động PHÒNG NGỪA, không phải phản ứng với 1 sự kiện đã crystallize
- **recovery_confirmed:** không xác định trong phạm vi phân tích BLIND này (đọc dừng ở
  23/03/2026, KHÔNG tham chiếu đỉnh 18/05/2026 hay episode 07/2026 theo đúng luật BLIND)
- **chain_classification:** `INDEPENDENT` (nhưng ĐÁNH DẤU liên hệ tiềm năng với episode 07/2026
  đã có trong fleet — nếu cùng gốc tín dụng/BĐS nội địa tiếp diễn, có thể cần xem lại là 1 chuỗi
  sóng liên tiếp giống mega-2007-2012, nhưng việc đó KHÔNG thuộc phạm vi phân tích BLIND này và
  phải do một dispatch khác xác nhận bằng dữ liệu forward, không phải bởi vai trò macro-strategist)
- **analyst_notes:** Đây là episode ĐẦU TIÊN trong 5 episode được giao (cùng đợt 31/08) có tín
  hiệu STRUCTURAL thật, không phải CONFIDENCE_LIQUIDITY sạch — khác hẳn 2014/2015/2023. Điểm khác
  biệt cốt lõi so với các case CONFIDENCE_LIQUIDITY khác: lãi suất huy động ĐANG TĂNG (không phải
  ổn định/giảm) trong suốt 12+ tháng trước episode — đây là chỉ báo đơn lẻ dễ tách nhất, nên dùng
  làm bộ lọc nhanh khi phân loại các episode tương lai (huy động tăng dần = nghi ngờ STRUCTURAL,
  huy động ổn định/giảm = nghiêng CONFIDENCE_LIQUIDITY).

---

## TRẠNG THÁI HIỆN TẠI 2023-2026 (không phải episode khủng hoảng)

**Macro regime:** GROWTH / NEUTRAL (không có dấu hiệu stress nào rõ ràng)

**Bằng chứng:**
- **GDP growth:** 5.05% (2023) → 7.09% (2024) → 8.02% (2025) → Q1 2026: +7.83% YoY. Nguồn:
  GSO/Trading Economics.
- **Tín dụng:** ~18% (2025), target 15% (2026). Trong range bình thường-cao nhưng không vượt ngưỡng
  báo động. Nguồn: SBV/Vietnam Briefing 2025.
- **Lạm phát:** CPI core 3.27% (12/2025), bình quân 2025 ~3.21%. Dưới trần Quốc hội ~4.5-5%.
  Nguồn: OECD Vietnam Survey 2025; IMF Vietnam Article IV 2025.
- **SBV chính sách:** Refi rate 4.5% (từ 08/2023, giữ nguyên). Không có tín hiệu tăng lãi suất.
  Nguồn: SBV official statements.
- **Rủi ro tiềm tàng:** Tín dụng 18% trong bối cảnh bất động sản chưa hoàn toàn phục hồi sau vụ SCB
  (2022-2024) → cần theo dõi NPL ratio ngân hàng. IMF 2025 cảnh báo "fiscal expansion and
  accommodative monetary policy may generate inflationary pressures through stronger domestic demand."
  Nguồn: IMF Vietnam 2025 Article IV.

**Kết luận:** Chưa có đủ bằng chứng xếp vào STRESS hay CRISIS. Trạng thái GROWTH với rủi ro tiềm
ẩn cần theo dõi (tín dụng cao, bất động sản recovery chưa đồng đều).

---

## TỔNG HỢP CUỐI: N_EFFECTIVE CHO PHÂN TÍCH THỐNG KÊ

| Episode | Loại | Trục 1 | Trục 2 | N_effective |
|---|---|---|---|---|
| MEGA-2007-2012 (3 sóng) | Khủng hoảng cơ cấu | STRUCTURAL | MULTI_YEAR | **1** cụm |
| 2014-09 OPEC/oil crash | Cú sốc giá hàng hóa ngoại sinh | CONFIDENCE_LIQUIDITY (clean) | EXTERNAL_CYCLE (clean) | **1** |
| 2015-07 China devaluation | Cú sốc niềm tin/tỷ giá ngoại sinh | CONFIDENCE_LIQUIDITY (ambiguous — tín dụng vượt target) | EXTERNAL_CYCLE (clean) | **0.75** |
| 2018 Q1-Q4 | Điều chỉnh thị trường, ngoại lực | CONFIDENCE_LIQUIDITY | EXTERNAL_CYCLE (đính chính 08-30) | **0.5** (ambiguous severity) |
| 2020-2021 COVID | Cú sốc ngoại sinh | CONFIDENCE_LIQUIDITY | CONTAINABLE | **1** |
| 2022-05 SCB/Fed | Cú sốc niềm tin + FX | CONFIDENCE_LIQUIDITY | CONTAINABLE | **1** |
| 2023-09 FX-defense/margin/VIC-VHM | Cú sốc niềm tin + FX + đòn bẩy | CONFIDENCE_LIQUIDITY (clean) | CONTAINABLE dominant + EXTERNAL_CYCLE phụ | **0.75** |
| 2025-03 Liberation Day tariff | Cú sốc chính sách thương mại ngoại sinh | CONFIDENCE_LIQUIDITY (clean) | CONTAINABLE (tranh chấp) + EXTERNAL_CYCLE (rủi ro nền) | **0.75** |
| 2026-01 Credit/BĐS + chiến tranh dầu | Pha trộn 2 lớp nguyên nhân | MIXED (ambiguous) | N/A — 2 timeline riêng | **0.5** (chưa rõ có nối vào 1 chuỗi lớn hơn với episode 07/2026 hay không — CẦN dispatch riêng, không BLIND, để xác nhận) |
| **TỔNG** | | | | **~7.75** độc lập thật (trước đây ~3.5, +5 episode phân tích 2026-08-31) |

Bất kỳ phân tích nào dùng N=12 (đếm tất cả các "episode" riêng biệt, gồm cả 5 episode mới) đều
overestimate N_effective một cách đáng kể so với ~7,75. Lưu ý: 2014-09 và 2015-07 LIỀN KỀ NHAU
(cùng thuộc giai đoạn hậu-taper-tantrum/thương phẩm 2014-2016) và EP-2026-01 có khả năng nối vào
episode 07/2026 đã có trong fleet nếu cùng gốc tín dụng/BĐS — nếu xác nhận, N_effective còn giảm
thêm. Đây là ước lượng SƠ BỘ, không phải con số cuối — Taylor/quant-skeptic cần tự đánh giá lại
khi dùng cho phân tích thống kê thật (số N quá nhỏ để domain này chịu được sai số cộng dồn).

---

## Chưa phân loại độc lập — cần dispatch macro-strategist riêng nếu cần entry chính thức

Sau đợt phân tích 2026-08-31 (5 episode mới: 2014-09, 2015-07, 2023-09, 2025-03, 2026-01), các
episode chính đã biết trong lịch sử VNINDEX đã được phân loại. Entry này còn lại:

- **2000-2006 (pre-WTO):** Không phải episode khủng hoảng. Giai đoạn tăng trưởng ổn định. GDP
  6-7.5%/năm. CPI moderate. SBV đang xây dựng thể chế. Không cần phân loại crisis.
- **2013-2019 (hậu khủng hoảng → growth, TRỪ 2014/2015 nay đã có entry riêng, TRỪ 2018):** Không
  phải episode khủng hoảng. Các năm lẻ còn lại trong giai đoạn này không có triggers rõ ràng.
- **Episode "07/2026" (đã có trong nghiên cứu khác của fleet, SAU đỉnh VNINDEX 2026-05-18):**
  CHƯA được macro-strategist phân loại độc lập theo đúng khung 2 trục của registry này (nghiên cứu
  hiện có tập trung phần giá/backtest). Ghi nhận NGHI VẤN (chưa xác nhận): EP-2026-01 (01-03/2026,
  MIXED — có hợp phần STRUCTURAL_ACCUMULATION tín dụng/BĐS đang chạy) và episode 07/2026 CÓ THỂ là
  2 sóng của CÙNG một chuỗi cơ cấu (giống mega-2007-2012), nếu hợp phần tín dụng/BĐS nội địa của
  EP-2026-01 tiếp tục xấu đi thay vì được SBV kiểm soát thành công qua trần tín dụng BĐS 2026. XÁC
  NHẬN việc này đòi hỏi đọc dữ liệu SAU 2026-03-23 (ngoài phạm vi BLIND) — phải giao cho một dispatch
  macro-strategist RIÊNG, không phải suy luận thêm từ đây.

Nếu phát hiện episode mới cần phân loại: dispatch macro-strategist với ngày + hành động giá,
KHÔNG kèm forward-return/giả thuyết backtest.


---

## APPENDIX: MACRO CONTEXT 2016-2019 — GROWTH REGIME (không phải episode khủng hoảng)

**Phân tích thêm ngày 2026-08-25** — theo yêu cầu xác định đặc trưng vĩ mô giai đoạn này để làm
nền cho phân tích sector rotation. Đây KHÔNG phải entry phân loại khủng hoảng (không có crisis
trigger) — mà là hồ sơ regime để tránh nhầm lẫn khi đọc dữ liệu 2017-2020 trong backtest context.

### Chỉ số vĩ mô chính xác (PIT-dateable, có nguồn)

| Chỉ tiêu | 2017 | 2018 | 2019 |
|---|---|---|---|
| GDP growth | 6.81% (beat target 6.7%) | 7.08% (10-year high) | ~7.02% |
| CPI bình quân | ~3.53% | ~3.54% | 2.79% |
| SBV refi rate | 6.5% → **6.25%** (cut July 2017) | 6.25% (held stable) | 6.25% → 6.0% (cut Sep 2019) |
| Tín dụng | ~18-19% (trong target SBV 17-18%) | ~14% (siết chuẩn bị Basel II) | ~13% |
| Tài khoản vãng lai | Thặng dư ~5-7% GDP | Thặng dư ~6.8% GDP (Q1) | Thặng dư |
| FX reserves | Tích lũy thêm ~US$12.5 tỷ | Đạt ~US$63 tỷ (H1 2018, 3.6 tháng nhập khẩu) | Tiếp tục tăng |
| FDI đăng ký | ~US$29 tỷ | ~US$29 tỷ | ~US$29 tỷ |

Nguồn:
- GDP, CPI: [IMF Executive Board 2017 Article IV](https://www.imf.org/en/News/Articles/2017/07/05/pr17262-vietnam-imf-executive-board-completes-the-2017-article-iv-consultation); [IMF 2018 Article IV PR](https://www.imf.org/en/news/articles/2018/07/10/pr18284-vietnam-imf-executive-board-concludes-the-2018-article-iv-consultation); IMF 2019 Article IV
- SBV rate cut July 2017: [Central Banking "Vietnamese central bank cuts rates, despite IMF credit warning"](https://www.centralbanking.com/central-banks/monetary-policy/3269231/vietnamese-central-bank-cuts-rates-despite-imf-credit-warning); xác nhận giữ nguyên: [Vietnam News "VN central bank makes first key rate cut since 2017" ~2019](https://vietnamnews.vn/economy/535383/vn-central-bank-makes-first-key-rate-cut-since-2017.html)
- CA surplus, FX reserves: [World Bank Vietnam Taking Stock June 2018](https://documents1.worldbank.org/curated/en/821801561652657954/pdf/Taking-Stock-Recent-Economic-Developments-of-Vietnam-Special-Focus-Vietnams-Tourism-Developments-Stepping-Back-from-the-Tipping-Point-Vietnams-Tourism-Trends-Challenges-and-Policy-Priorities.pdf)
- FDI: Multiple sources confirm ~$29B registered across 2017-2019

### Nhận định macro regime

**Nhãn đúng cho 2017-2019: ACCOMMODATIVE LOW-RATE MANUFACTURING/FDI-LED GROWTH**

Đặc trưng phân biệt rõ với 2007-2012 (STRUCTURAL):
- SBV CẮT lãi suất tháng 7/2017 (bất chấp IMF khuyến cáo giữ nguyên vì lo tín dụng) — nghĩa là tiền tệ NỚI LỎNG chủ động, không phải "lãi suất cao"
- Lãi suất thực = 6.25% - 3.5% CPI = ~2.75% — THẤP theo chuẩn lịch sử VN
- Tín dụng ~18% năm 2017 — trong target SBV, không phải tăng vọt ngoài kiểm soát như 53% (2007)
- Thâm hụt CA không tồn tại — trái lại thặng dư lớn và tích lũy FX reserves → KHÔNG có dấu hiệu mất cân đối macro nội địa
- Driver tăng trưởng = FDI sản xuất điện tử/dệt may (Samsung, LG, Intel...) → xuất khẩu phi thương mại, KHÔNG phải tín dụng trong nước bơm bất động sản

**Mô tả sai cần tránh:** "lãi suất cao, thanh khoản hạn chế" — đây là miêu tả 2011-2012, không phải 2017-2019.

### Các đợt niêm yết ngân hàng lớn 2017-2018 (gây supply effect)

| Ngân hàng | Mã | Ngày niêm yết | Sàn | Market cap xấp xỉ |
|---|---|---|---|---|
| VPBank | VPB | 17/08/2017 | HOSE | ~VND 52 tỷ (xếp hạng tư nhân cao nhất) |
| HDBank | HDB | 05/01/2018 | HOSE | ~VND 32.4 tỷ |
| Techcombank | TCB | 04/06/2018 | HOSE | ~$900M (~VND 20 nghìn tỷ) — IPO lớn nhất VN đến thời điểm đó |
| TPBank | TPB | 04/2018 | HOSE | ~VND 17 nghìn tỷ (555 triệu cổ phần) |

Nguồn: [FinanceAsia VPBank IPO](https://www.financeasia.com/article/vpbank-markets-key-vietnamese-banking-ipo/436386); [VIR "VPBank making its debut on HoSE"](https://vir.com.vn/vpbank-making-its-debut-on-hose-51304.html); [Techcombank official listing announcement 04/06/2018](https://techcombank.com/en/information/updates/techcombank-chinh-thuc-niem-yet-tai-so-giao-dich-chung-khoan-tp-ho-chi-minh-vao-ngay-04-06-2018); [VNEconomicTimes "HDBank lists on HoSE"](https://vneconomictimes.com/article/banking-finance/hdbank-lists-on-hose).

Trong 12 tháng (August 2017 - June 2018): ~VND 120+ nghìn tỷ market cap ngân hàng mới gia nhập HOSE.
Đây là cú supply shock đáng kể đối với nhóm banking đã có sẵn trên sàn.

### Banking sector fundamentals 2016-2017 (Oxford Business Group, 2017)

- ROE hệ thống: 5-7% (vs. 14.56% trước 2012) — đang hồi phục nhưng chậm
- ROA: 0.4-0.5% (vs. 1.29% trước 2012)
- NPL: VND 350 nghìn tỷ đã giải quyết qua VAMC từ 2013, còn VND 230 nghìn tỷ đang nằm tại VAMC
- Ngân hàng quốc doanh (VCB/BID/CTG) chiếm >46% tổng tài sản → bị constrain bởi yêu cầu tỷ lệ vốn nhà nước + chuẩn bị Basel II (Circular 41/2016 của SBV)
- Nguồn: [Oxford Business Group Vietnam 2017 Banking Sector](https://oxfordbusinessgroup.com/reports/vietnam/2017-report/economy/turning-point-banking-sector)

