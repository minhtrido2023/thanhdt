# Cổng DD trước plan cho book LAG — job Taylor_20261021_151302

Nhánh `feat/lag-dd-gate-20261021` (worktree `WorkingClaude/wt-lag-dd-gate-20261021`), CHƯA merge.
User duyệt 21/10 22:10 ICT (thread plan DollarBill): FLAG chưa trả lời ⇒ đứng ngoài plan;
CLEARED = DD cơ bản không có cờ nào; thí điểm HT1/SCL/VPB.

## 1. Thí điểm (ĐO — asof 2026-10-21, release 2026-10-19, vào lệnh ~2026-10-26)

Lệnh: `python3 wt-lag-dd-gate-20261021/bin/lag_dd_pack.py --tickers HT1,SCL,VPB --release-date 2026-10-19 --entry-date 2026-10-26 --asof 2026-10-21 --dry-run` (rc=2).
Đường tự động `--signal-date 2026-10-21` (đọc CSV golive) ra đúng 3 mã, release tự suy = 2026-10-19, 49,5s, RSS 310MB.

| Mã | Status | Cờ | Bằng chứng chính |
|---|---|---|---|
| HT1 | **CLEARED** | — | ADV3T 2,88 tỷ; 8L qua, không cũ; DCF CHEAP MoS +48,0% robust; NP Q3 99,4 tỷ YoY +16,0%; ΣCFO 4Q 1.086,6 tỷ / ΣNP 400,4 tỷ = 2,71×; phải thu −30,8% YoY, tồn kho +11,4% vs doanh thu +18,8%; NPM 4,8% < EBITM 6,9%; không insider / ex-date / anomaly / forensic |
| SCL | **FLAG** | `EQ_PHAI_THU_TANG` | AR_P0 203,5 tỷ vs 78,5 tỷ (2025Q3) = +159% vs doanh thu +88,8% (chênh +70,6pp > 30pp). ⚠ Mâu thuẫn cần đọc: DSO của vendor P0 40,7 ngày < P4 67,2 ngày (ngược chiều AR thô). Còn lại sạch: ΣCFO/ΣNP 4Q 0,80; NP YoY +136%; tồn kho +110% (chênh 20,9pp < ngưỡng); DCF NOT_COMPUTED (fcfe_negative_buildout), lens 8L 2/5, EY 9,8% |
| VPB | **FLAG** | `BAT_THUONG_ANOMALY` | `data/anomaly_flags.json`: tier H, IDIOCRASH, last_alert 2026-09-18 (bản ghi đã >1 tháng; DD echo mọi bản ghi còn trong file). NP YoY +18,8%; Gordon P/B 1,20 vs hợp lý 1,22 (CHEAP); ADV3T 361,8 tỷ; NPL FiinPro 2026Q2 3,341% vs 4,058% 2025Q2, LLR 56,2% vs 52,2% (CHỈ thông tin — không phải quý Q3) |

Status do thiếu dữ liệu: **0/3** — hai FLAG đều là cờ thật, không phải `*_NA`.
Không post Discord (thí điểm). Gói: `data/lag_dd/{HT1,SCL,VPB}_2026-10-19.json`.

## 2. Định nghĩa cờ (cơ học, `lag_dd_pack.FLAG_CODES`)

- DD cơ bản: echo 5 cờ đỏ của `due_diligence` + các mức ⚠ (ADV < 2 tỷ, quality_flag, quý lỗ
  trong nền, anomaly, insider bán ròng, ex-date ≤25 ngày) + forensic exclude/watch + 8L fail/cũ + DCF RICH.
- Pháp lý (`forensic_flags.flag_type` ∈ fraud_confirmed/legal/...) ⇒ `PHAP_LY_WARNING`, severity WARNING, vẫn FLAG.
- Chất lượng lợi nhuận: `EQ_NEN_THAP`, `EQ_CFO_YEU`, `EQ_NGOAI_HOAT_DONG` (proxy NPM>EBITM), `EQ_PHAI_THU_TANG`,
  `EQ_TON_KHO_TANG`. Ngưỡng 0,5 / 0,5 / 30pp là **ước lượng, đặt tay, chưa backtest**.
- Fail-closed: 11 cờ `*_NA` (fin, release, ADV, universe, anomaly, insider, corp feed, forensic, rating, định giá).
- Ngân hàng: CFO/vốn lưu động/NPM-EBITM = "không áp dụng"; NPL/LLR chỉ là thông tin.

## 3. Cổng plan (Việc B)

`lag_plan_consistency_check.py` thêm `LAG_DD_GATE_VIOLATION` (ĐỎ) cho lệnh MUA LAG không ở `CLEARED` / `ACK_PROCEED`,
và dòng "⏳ Chờ DD" cho mã trong `lag_analysis` đứng ngoài plan. Đã nằm sẵn trong hook `send_plan_report.sh`
(không sửa hook). Thử dry-run trên plan thật 22/10 của cả 2 account: ✅ + 2 dòng chờ DD (SCL, VPB).
Hợp đồng DollarBill: `kb/context_planning_mini.md` mục "CỔNG DD TRƯỚC PLAN".

Ack: `bin/lag_dd_ack.py --ticker SCL --release-date 2026-10-19 --decision PROCEED|DROP|RESEARCH --decided-by user --at <ISO+07:00> --source "<link>"`.
Ack khoá vào `flags_hash` của gói ⇒ gói sinh lại ra bộ cờ khác thì ack cũ hết hiệu lực (`ACK_STALE`).

## 4. Đề xuất móc vào chuỗi 19:00 (CHƯA cài — Mike duyệt)

Không cần dòng cron mới. Thêm 1 bước WARN-only vào `bin/bq_freshness_check.sh`, NGAY SAU
`_assert_fresh_artifact "golive_v23_recommendations ..."` và TRƯỚC `[pipeline-4] dispatch DollarBill`:

```bash
# [pipeline-3b] gói DD LAG trước plan (user duyệt 21/10) — WARN-only, KHÔNG chặn DollarBill:
# thiếu gói ⇒ cổng coi là NO_PACK ⇒ mã đứng ngoài plan (fail-closed sẵn ở checker).
echo; echo "--- [pipeline-3b] lag_dd_pack ---"
_dd_out="$(timeout "${LAG_DD_PACK_TIMEOUT_S:-420}" python3 "$ROOT/bin/lag_dd_pack.py" --notify 2>&1)"; _dd_rc=$?
echo "$_dd_out" | tail -20
if [ "$_dd_rc" -ne 0 ] && [ "$_dd_rc" -ne 2 ]; then
  "$ROOT/bin/notify_thread.sh" "🟡 LAG DD PACK WARN ($TODAY $NOW_ICT): lag_dd_pack rc=$_dd_rc — $(echo "$_dd_out" | tail -2 | tr '\n' ' ' | cut -c1-300). Mã LAG không có gói sẽ ĐỨNG NGOÀI plan." "$DISCORD_STALE_CHANNEL" || true
fi
```

- Timeout 420s: đo 49,5s/3 mã; mùa cao điểm ~15 mã ⇒ ước lượng ~4 phút (chưa đo).
- Chạy mỗi tối T2-T6 ⇒ ứng viên lộ diện từ T-4 có gói ngay tối đó; tin Discord idempotent theo
  (mã, release, bộ cờ) nên không lặp. Vòng CN (`sunday_plan_round.sh`) không cần bước riêng: gói thứ Sáu còn hiệu lực ≤30 ngày.
- Sau khi cài: thêm dòng vào `kb/cron_registry.md` cạnh mục 19:00 bq_freshness (§11).

## 5. Có nên chặn cứng không — khuyến nghị (để Mike hỏi user)

Hiện chỉ cảnh báo ĐỎ trong report duyệt. Lỗ hổng: nếu user duyệt plan mà không đọc khối đỏ,
lệnh LAG có cờ vẫn được bot đặt. **Khuyến nghị chặn cứng ở tầng ORDER** (như `filter_lag_rating_orders`
trong `trading_bot/plan.py`: loại lệnh MUA LAG có `dd_gate` ∉ {CLEARED, ACK_PROCEED} trước khi đặt,
fail-closed) — KHÔNG chặn ở `send_plan_report` (chặn 21:00 làm user không thấy plan). Việc này chạm
đường thực thi ⇒ ngoài phạm vi dispatch, cần user duyệt + arch-review riêng.

## 6. Rủi ro còn lại

1. Ngưỡng chất lượng lợi nhuận là ước lượng; tỷ lệ FLAG thật trong mùa chưa đo (thí điểm 2/3 FLAG).
2. `BAT_THUONG_ANOMALY` echo mọi bản ghi còn trong `anomaly_flags.json`, không lọc theo tuổi
   (VPB: bản ghi 09-18) — đúng định nghĩa "không cờ nào" nhưng có thể gây FLAG lặp mỗi mùa.
3. `EXDATE_SAP_TOI` là cảnh báo CHI PHÍ (BHAR không ý nghĩa ở nhóm ADV cao) nhưng đang làm FLAG theo
   định nghĩa user ⇒ có thể nhiều FLAG quanh mùa cổ tức.
4. Không có cột LNTT/thu nhập khác ⇒ `EQ_NGOAI_HOAT_DONG` chỉ là proxy NPM>EBITM.
5. Ứng viên lộ diện muộn (T+1) ⇒ không kịp hỏi user ⇒ đứng ngoài plan (đúng fail-closed, nhưng mất slot).
6. Gói đọc `bq_cache` (DD cơ bản, trễ ≤1 phiên) + BQ live (ticker_financial/8L); không phải số trong ngày.
7. Hạn trả lời giả định không có lễ giữa tuần (ghi rõ trong tin).
8. Lệnh LAG nằm trong `deferred_orders[]` (WAIT_CASH) không bị cổng kiểm cho tới khi được đưa vào `orders[]`
   và plan gửi lại (checker chạy lại lúc gửi).
