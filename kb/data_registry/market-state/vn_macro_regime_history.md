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
| 2018 Q1-Q4 | Điều chỉnh thị trường, ngoại lực | CONFIDENCE_LIQUIDITY | EXTERNAL_CYCLE (đính chính 08-30) | **0.5** (ambiguous severity) |
| 2020-2021 COVID | Cú sốc ngoại sinh | CONFIDENCE_LIQUIDITY | CONTAINABLE | **1** |
| 2022-05 SCB/Fed | Cú sốc niềm tin + FX | CONFIDENCE_LIQUIDITY | CONTAINABLE | **1** |
| **TỔNG** | | | | **~3.5** độc lập thật |

Bất kỳ phân tích nào dùng N=7 (đếm tất cả các "episode" riêng biệt) đều overestimate N_effective
một cách đáng kể. N_effective ≈ 3-4 là ước lượng đúng hơn.

---

## Chưa phân loại độc lập — cần dispatch macro-strategist riêng nếu cần entry chính thức

Sau bản phân tích toàn diện 2026-08-25, tất cả các episode chính đã được phân loại. Entry này còn
lại chỉ cho các giai đoạn:

- **2000-2006 (pre-WTO):** Không phải episode khủng hoảng. Giai đoạn tăng trưởng ổn định. GDP
  6-7.5%/năm. CPI moderate. SBV đang xây dựng thể chế. Không cần phân loại crisis.
- **2013-2019 (hậu khủng hoảng → growth):** Không phải episode khủng hoảng. Giai đoạn recovery rồi
  growth. Các năm lẻ trong giai đoạn này không có triggers rõ ràng.

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

