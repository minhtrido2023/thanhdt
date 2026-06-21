---
name: moat-must-be-audited-2026
description: "Standing rule — moat data must pass /competitive-analysis + /comps-analysis audit before being used to rate or gate; never trust stale tags or GPM/ROE proxy as \"moat\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1c1b7354-9b91-42a1-8dd3-a9d16382f9e8
---

User ([REDACTED]14): thông tin moat đang dùng trong hệ 8L "có vẻ out of date". **RULE: nếu dùng thông tin moat thì PHẢI trải qua audit kiểu `/competitive-analysis` + `/comps-analysis` rồi mới được sử dụng** — moat là phán quyết cạnh tranh định tính, biến thiên theo thời gian, KHÔNG phải tag tĩnh hay tỷ-số tài-chính.

**Why:** moat hiện được dùng 2 chỗ, cả 2 chưa-audit và không đáng tin làm input quyết định:
1. `moat_tag()` trong `rating_8l.py` = proxy ĐỊNH LƯỢNG (GPM level + GPM-CV ổn định + ROE5Y) → **trực tiếp nâng hạng 36 mã** (note "moat↑1": 3→2/2→1). Bằng chứng SAI: **HAG bị gắn moat STRONG** (GPM/ROE cao nhất-thời) và được moat↑1 — proxy không phân biệt moat thật vs biên-cao-tạm-thời. → một phép tính tỷ-số KHÔNG phải moat.
2. `data/moat_tags.csv` = registry 5F hand-curated (40 dòng, sửa tay [REDACTED]07; gate ở rank_8l/dna_card/screener) — hand-edited, không dấu vết audit, dễ stale.

**How to apply (STANDING RULE — đã codify trong `rating_8l.py` docstring header [REDACTED]14):**
- **"MOAT UPGRADE REQUIRES AUDIT"**: moat chỉ được NÂNG HẠNG rating (notch +1) khi đã qua 5F audit ghi trong `data/moat_tags.csv` với `moat_tier=WIDE`. NARROW/NONE → KHÔNG notch. Mã NGOÀI registry → notch quant chỉ là **placeholder tạm (audit dần), KHÔNG phải upgrade tin được**; ngay khi mã đó thành screener/decision-relevant (liquid, lên list) → **PHẢI 5F-audit (thêm vào moat_tags.csv) TRƯỚC** khi tin upgrade.
- Audit = **/competitive-analysis** (5 lực Porter + vị thế + đe dọa) + **/comps-analysis** (benchmark biên/ROIC/bội số vs peer thật, kiểm pricing-power CÒN đúng), date-stamp + re-audit định kỳ.
- Stale/chưa-audit → moat **TRUNG TÍNH (không nâng hạng)**. Proxy GPM/ROE (`moat_tag`) là PROXY, KHÔNG thay được 5F audit. KHÔNG nới quyền của moat-notch mà thiếu entry moat_tags.csv tương ứng.

**✅ TRIỂN KHAI XONG ([REDACTED]14)** — wire 5F governance vào rating, rule cuối = **"SIẾT A-mềm"**:
- **KHÔNG làm lại 5F**: audit cũ sẵn `data/moat_tags.csv` (39 mã, src=5f_validated_compet, asof [REDACTED]03..05, 3-tier WIDE/NARROW/NONE + risk1 5F + comps through-cycle). Chỉ **3 WIDE: VNM/TLG/DHG**; 33 NARROW; 3 NONE (DRC/KSF/SGP). GMD/VGC "quant STRONG overstated" đã ghi sẵn → đủ căn cứ, không pull comps mới.
- **RULE CUỐI (user chốt qua 2 vòng) = SIẾT A-mềm**: moat **notch +1 (đẩy prelim 2/3 lên đỉnh) CHỈ WIDE được hưởng**; registry **NARROW/NONE → KHÔNG notch** (NARROW erode được, vd FPT −40% vì AI dù KQKD chưa giảm → không xứng AAA). **NHƯNG quant-fortress (core_score≥10 → prelim 1) GIỮ rating 1 độc-lập-moat** (notch chỉ áp prelim 2-3, nên SAB/BMP/NNC/NCT/VLB/TV1/TRA core≥10 giữ 1). **Ngoài-registry → giữ quant notch (audit dần)**. [đã thử rule Y/N "NARROW-genuine giữ +1" rồi user siết tiếp → chỉ-WIDE-notch].
- **Wired** `rating_8l.py` (snapshot, MOAT_TIER gate notch theo tier==WIDE) + `rating_8l_history.py` (publisher→fa_ratings_8l, PIT-gated eff>=2025-06-01) + `build_rating_8l_history.py`. Gate dùng `moat_tier` (cột `moat_upgrade` Y/N giữ làm doc, không dùng cho notch nữa).
- **Kết quả LIVE (verified BQ + snapshot)**: moat-lifted NARROW rớt **1→2**: FPT,MCH,SCS,FOX,VCS,DVP,DBD,FOC,DHA,SAS,HTI; VGC 1→2; GMD 2→3, SGP 2→3 (NONE). **Giữ 1**: WIDE (VNM,TLG,DHG) + quant-fortress NARROW core≥10 (SAB,BMP,NNC,NCT,VLB,TV1,TRA). Non-registry giữ quant. Parking gate≤3 membership KHÔNG đổi (các mã rớt vẫn ≤2-3) — fix sắc-hóa quality-rank + buy-now.
- ⚠️ 45 mã non-registry vẫn rating 1 (chưa audit, giữ quant) — tier-1 tạm "ngược" (audited-NARROW bị siết, unaudited giữ), đa số illiquid; audit dần khi vào screener. Multi-copy `8l_package/`+`release_8l*/` CHƯA sync (stale/archive) → bước 3. Live = root rating_8l.py + rating_8l_history.py (synced).

**✅ BƯỚC 2 XONG ([REDACTED]14) — screener/bot mặc định = giao 2-TRỤC**: `rating_8l.py` thêm output canonical `data/rating_8l_screener.csv` (universe rating≤3 moat-AUDITED × pb_z × liq≥3B) chia 3 zone: **🟢 BUY-NOW** (pb_z≤−0.3 + book-OK, 26 mã: ACV/VNM/DGC/VGC/SCS/VHC/NT2/CTR/IDC...), **🟡 ACCUMULATE** (định giá hợp lý, 38: FPT pb_z−0.09...), **🔴 WATCH-RICH** (pb_z>0.6 chất-lượng-nhưng-đắt ĐỪNG ĐUỔI, 50: MCH/VTP/SAB/BMP/VCB...). Cột moat5f = 5F tier. `bot_8l_commands.format_topn` repoint từ rank_8l-composite → screener 2-trục này (composite giữ làm `_format_rank_composite`/`/rank`). Giải đúng phê bình user: list quality-only đưa MCH/VTP (top-0.2% PB) lên đầu = vô-giá-trị; giờ MCH/VTP nằm WATCH-RICH. cheap_pb_floor.py vốn đã 2-trục (khớp BUY-NOW zone).

**✅ BƯỚC 3 XONG ([REDACTED]14) — reconcile copies + audit-dần queue:**
- **Điều tra đường live**: scheduled task `8L_Daily_Alert` → `pt_8l_daily.bat` (WORKDIR root) → `python rating_8l.py` = **ROOT** (đã edit đầy đủ). `_build_zips.py` chỉ đóng gói OUTPUT `data/rating_8l.csv`, không phải script. **KHÔNG script/task nào chạy `8l_package/rating_8l.py`** (orphan). `release_8l*/` = bundle versioned đã ship (frozen archive).
- **Reconcile**: `cp rating_8l.py → 8l_package/rating_8l.py` (giờ IDENTICAL với root, compile OK) — diệt hazard "chạy nhầm copy stale ghi đè data". Để nguyên `release_8l*/` (sửa release đã ship = sai; rebuild từ root khi cần ship mới). Live single-source = root.
- **Audit-dần queue = RỖNG cho screener**: 45 mã non-registry rating-1 = 22 đạt 1 bằng core≥10 (quant-fortress, KHÔNG cần moat audit) + 18 nhờ moat↑1 chưa-audit NHƯNG **tất cả illiquid (liq max 0.3B, không vào screener)**. → 0 mã liquid/quyết-định nào dựa moat chưa-audit; rule moat-phải-audit đã thỏa toàn bộ vùng quyết định. 18 mã illiquid chỉ audit khi thành screener-relevant (defer đúng).
- ⚠️ Maintenance: root rating_8l.py là single source; nếu sửa sau phải nhớ `cp` lại 8l_package (hoặc tốt hơn: cho packager copy-from-root lúc build). Live pipeline KHÔNG bị ảnh hưởng (chỉ root chạy).

**→ XONG cả 3 bước (moat audit → screener 2-trục → reconcile). Hệ 8L giờ: rating moat-AUDITED (chỉ WIDE→tier1), screener/bot mặc định 2-trục, single-source root, no un-audited-moat trong vùng liquid.**

**✅ RE-VALIDATE POST-FIX ([REDACTED]14) — không bất thường**: chạy lại custompitg sweep sau khi đổi fa_ratings_8l (regime_size + parking gate đọc nó PIT). Delta full-history NHỎ (đúng vì governance PIT-gated eff≥2025-06): **50B 25.66→25.87 (+0.21) · 100B 23.07→23.82 (+0.75) · 200B 21.02→21.28 (+0.26) · 500B 18.93→18.83 (−0.10)**. Sharpe/DD/Calmar ổn định-hoặc-nhỉnh (100B Sh1.66→1.70), self-check 0 VND mọi NAV, spot-check PASS (rổ rebuild 0.00). Net dương nhẹ = loại HAG-type khỏi parking + halve mã EQ-gate-5 trong BEAR/CRISIS. KHÔNG breakage/anomaly. ⚠ bq transient crash 0xC0000142 vẫn thỉnh thoảng (run-thứ-3/4) → chạy lại fresh-shell là OK (đã thành pattern).

**Còn treo (thứ tự user):** (2) đổi screener sang giao-2-trục quality×value; (3) reconcile copies rating_8l.py. Liên quan [[rating_8l_credit_scale_2026]], [[moat_5f_8l_bridge_2026]], [[hag_earnings_forensic_2026]].
