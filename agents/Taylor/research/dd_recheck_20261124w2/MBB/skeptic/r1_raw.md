**Verdict: INCONCLUSIVE (medium confidence).** The model reproduces, and the r-sensitivity table is correct. The recheck still misses one material item that could cut the centre, and it leaves the main downside sensitivity un-rerun. Against that, the ROE fade looks more conservative than the stock's own history supports. I judged without any market data: the report's price of 19,250 was not used.

**What I recomputed myself** (from `notes_read.md` HN-Q3 and the r3 model code, restored from git `14ad1c925^` to `/tmp/ddrestore_MBB`):
- **Book value per share at 30/09:** (164,141.6 − 7,124.8) / 10,068.75m shares = **15,594 đ**. Trailing ROE is **20.7%**.
- **Share count:** charter capital rose by +20,137.5 bn, which splits exactly into a 15% stock dividend (12,082) plus the 805.5m-share rights issue (8,055). So the share base already includes the rights issue. The only issuance still outside the model is the 200m-share private placement. At or below book value it costs about −1% to −2%, under the 5% threshold.
- **Base-case value (CO_SO scenario at its central parameters):** **20,984 đ** before the liquidity discount. The headline 21,069 is the scenario-weighted grid average, so this matches in order of magnitude.
- **Ke 12.3%:** **+12.3%**, the same as the report's +12.30%.

**Pushing the centre down (too high):**
1. **Welfare/bonus fund is missing (attack 8).** I inferred this from the HN-Q3 retained-earnings movement:
   - 2025 profit used: 28,463.
   - Minus cash dividend 8,557, minus 15% stock dividend 12,082, minus the increase in in-equity reserves 5,446.
   - That leaves about **2,378 bn unexplained (≈8.9% of 2025 profit)**. It most likely went to the bonus/welfare fund, which is a liability, not equity.
   - The residual-income model assumes all profit stays with shareholders. Leaking 5% to 8.9% of profit lowers the centre by **−6.5% to −11.4%**.
   - The figure is an inference from a residual, not a filing line, so this is INCONCLUSIVE rather than REFUTED.
2. **Permanent ROE premium.** The model keeps a 2.5pp gap (ROE_T 16% vs Ke) forever on the 2029 book, while also labelling the moat "NARROW, not durable". With no terminal premium the value is **18,061 (−14%)**. The "3c chặt" sensitivity (17,677, fading ROE to the sector median) was still run on the old r2 base and was never rerun on r3.
3. **Capital needs not linked to growth.** Management targets 30–35% credit growth, and CAR at 30/06 was 10.28% (separate) / 10.7% (consolidated). Profit retained at 70% grows equity only about 12.6% a year against 18% loan growth in the base case, so more dilution or slower growth is likely. Not modelled.
4. **Asset-quality and balance items, mostly small:**
   - Restoring coverage to 93.7% would need about 1,940 bn more provisions, ≈ −0.9% of the centre.
   - Neither the 30/09 balance of the 11,248 bn MBV debt-sale receivable nor CAR at 30/09 was checked.

**Pushing the centre up (too low):**
1. **ROE fade.** The base path starts at 18.5% in 2027, against trailing 20.7% and management's 22–24% target. Holding 20/19/18% with a 17% terminal gives **+8.5%**.
2. **Ke at 12.3%** gives +12.3%. It is reported, and r is anchored by rule, so this one stays out of the headline.
3. **Q4/26 assumption.** Pre-tax profit is assumed 7% below Q4/25 while the first nine months ran +32%. The effect is small.
4. **Q4 provisions.** The base case assumes 5,500 bn in Q4, while the 9-month credit cost of 1.46% suggests a lower run-rate. Small.
5. **MBV axis.** It is now symmetric at ±3,500, so it has no bias.
6. **g_RI = 0 in every branch.** This is a conservative convention.

**Other attacks:**
- **Legal (attack 2):** the legal scan has not been redone since 05/11. The report flags this as a WARNING.
- **Flip-flop (attack 6):** passes. The centre is unchanged from r3, and the r2→r3 changes came from documented skeptic corrections.
- **Attacks 1, 5, 7:** not applicable. The only sizing claim is a 2% NAV suggestion, with no fear-buy claim.

<<<VERDICT_JSON>>>
{
  "case_topic": "MBB — DD recheck đợt 2 (24/11/2026), tâm 21.069 / vùng 14.729–27.577, r 13,5%",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không claim fear-buy/§2.5 (fear_buy_eligible_2_5=False ở r2)",
    "scandal_migration_risk": "fail(soft) — pháp lý chưa quét lại sau 05/11 (§4.4, §5 WARNING); nghĩa vụ hỗ trợ MBV (cờ HARD ABANDON ≥15.688) chưa có văn bản; không thấy bằng chứng di chuyển nhưng cũng chưa kiểm",
    "optimistic_comp_sotp_bias": "fail(soft) — không có comp; nhưng RI giữ ROE_T 16% > Ke vĩnh viễn trên BV 2029 dù moat 'NARROW không bền': bỏ chênh terminal → 18.061 (−14%); độ nhạy '3c chặt' 17.677 vẫn trên base r2, chưa chạy lại r3",
    "data_provenance": "pass — BV, NCI, VĐL, SH, NI9, LT9, nhóm 2–5, xoá nợ 7.877 đều truy tới notes_read.md HN-Q3; VĐL +20.137,5 = 15% CP thưởng 12.082 + quyền mua 8.055 (khớp LCTT 'quyền mua ≈8.055 đã thu Q3', SKEPTIC_20261031 #2); CAR 30/06 và private placement chỉ là nguồn thứ cấp (đã gắn cờ)",
    "liquidity_capacity_realism": "na — sizing 2% NAV, CK 5 tỷ = 0,19% với ADV250 349 tỷ; không có claim khớp lệnh",
    "confirmation_bias_flipflop": "pass — tâm không đổi so với r3 (21.069); các lần đổi r2→r3 do đính chính skeptic 08/11 có bridge từng bước; không mở sổ vùng giá theo ràng buộc mù",
    "exit_discipline_gap": "na — không phải fear-buy; cờ HARD ABANDON MBV 15.688 được nêu",
    "missing_items": "fail — (1) Quỹ khen thưởng–phúc lợi / clean-surplus: phần dùng LNCPP 28.463 − cổ tức tiền 8.557 − CP thưởng 15% 12.082 − tăng quỹ trong VCSH 5.446 = dư ~2.378 tỷ (~8,9% LN 2025) suy ra ra khỏi VCSH; mô hình cộng 100% LN×70% vào BV → tâm có thể cao 6,5–11,4% (ước, chưa trích dòng BCTC) ⇒ material, chưa định lượng chắc; (2) private placement 200tr CP chưa vào mô hình (−1 đến −2%); (3) CAR/Tier1 30/09 chưa kiểm, kế hoạch tín dụng 30–35% vs giữ lại 70% ⇒ nhu cầu vốn/pha loãng thêm chưa mô hình; (4) số dư phải thu MBV 30/09 chưa kiểm; (5) ý kiến kiểm toán FY2025 chỉ ở WARNING; (6) khoản một lần trong 9T26 (thu bảo hiểm, CK) chưa tách; NPL/nhóm 2/bao phủ đã đóng cờ — pass; LDR/CASA chỉ từ web",
    "symmetry": "{too_high_checked: 7, too_low_checked: 7, too_low_items: ['Ke 12,3% → +12,3% (đúng, ngoài headline theo luật neo r)', 'ROE fade 18,5% 2027 vs ROE TTM 20,7% và mục tiêu BLĐ 22–24% → giữ 20/19/18, T17 = +8,5%', 'LNTT Q4/26 giả định −7% YoY dù 9T +32% (nhỏ)', 'DP Q4 5.500 vs chi phí tín dụng 9T 1,46% (nhỏ)', 'trục MBV đối xứng ±3.500 — không lệch', 'g_RI=0 mọi nhánh (bảo thủ quy ước)', 'payout tiền 30% khớp thực tế 2025 (8.557/26.779=32%) — không lệch']}"
  },
  "independent_verification": "Tự tính lại từ notes_read.md + code r3: BVPS 30/09 = 15.594 đ, ROE TTM 20,7%; giá trị CO_SO tham số trung tâm trước CK = 20.984 (cùng cỡ tâm lưới 21.069); độ nhạy Ke 12,3% = +12,3% khớp báo cáo +12,30%; VĐL +20.137,5 = 12.082 (CP thưởng 15%) + 8.055 (quyền mua 805,5tr × 10.000) ⇒ SH 10.068,75tr đã gồm quyền mua — khớp.",
  "killer_objection": "Mô hình RI giả định clean-surplus (toàn bộ LN giữ lại vào VCSH), nhưng biến động LNCPP HN-Q3 để lại ~2.378 tỷ (~8,9% LN 2025) không giải thích được, nhiều khả năng là quỹ khen thưởng–phúc lợi (nợ phải trả); nếu đúng thì tâm cao ~6,5–11%, cộng thêm chênh ROE_T−Ke vĩnh viễn (bỏ = −14%) chưa được đo lại trên r3.",
  "recommended_followups": [
    "Đọc thuyết minh phân phối LN 2025 (Nghị quyết ĐHCĐ 2026 / BCTC HN-Q3 thuyết minh VCSH) để lấy số trích quỹ KTPL thật; nếu ≥5% LN thì đưa hệ số rò vào ROE cổ đông",
    "Chạy lại độ nhạy '3c chặt' (fade ROE_T về trung vị ngành) và phương án 'không chênh terminal' trên base r3",
    "Lấy CAR/Tier1 30/09 từ thuyết minh hoặc CBTT và kiểm tính nhất quán giữa tăng trưởng tín dụng 18% và VCSH tăng ~12,6%/năm; mô hình hoá private placement 200tr CP",
    "Kiểm số dư phải thu MBV 11.248 tại 30/09 và quét pháp lý sau 05/11",
    "Thêm kịch bản ROE giữ gần lịch sử (≥20%) để cân hai chiều (+8,5%)"
  ],
  "summary": "Mô hình RI tái lập được, đầu vào truy đúng về BCTC HN-Q3, số CP đã gồm quyền mua 805,5tr, và bảng độ nhạy r chính xác (Ke 12,3% = +12,3%). Kết luận 'tâm không đổi 21.069' đúng về mặt cơ học nhưng chưa đứng vững về dữ kiện: (1) chiều ĐẮT — giả định clean-surplus bỏ qua phần LN ~8,9% có vẻ chảy ra quỹ KTPL (ước −6,5 đến −11%), chênh ROE_T 16% so với Ke 13,5% giữ vĩnh viễn dù moat NARROW không bền (bỏ = −14%; '3c chặt' chưa chạy lại trên r3), CAR 30/09 và nhu cầu vốn/pha loãng chưa mô hình; (2) chiều RẺ — ROE 2027 18,5% fade mạnh so với TTM 20,7% và mục tiêu 22–24% (giữ gần lịch sử +8,5%), Q4/26 thận trọng. Hạng mục thiếu material nhưng chỉ ước được từ phần dư ⇒ INCONCLUSIVE cho tới khi đọc số trích quỹ KTPL thật."
}
<<<END_VERDICT>>>