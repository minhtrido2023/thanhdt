# CAPIT tranche-hóa — thiết kế VẬN HÀNH (không phải quyết định)

**Job:** DollarBill_20260726_125529 · **Ngày:** 2026-07-26 · **Người hỏi:** user (qua Mike)
**Phạm vi:** NẾU CAPIT chuyển từ single-shot sang tranche 3 bước thì QUY TRÌNH LẬP PLAN/BÁO CÁO
nên thế nào. KHÔNG kết luận tranche tốt hơn hay không (Taylor + quant-skeptic trả lời bằng số).
KHÔNG sửa code — chỉ đề xuất, chờ duyệt.

---

## 0. Cơ chế CAPIT hiện tại (mỏ neo để so sánh) — từ `pt_capitulation_shadow.py` + `golive_v23_status.json`

- **Tín hiệu (level):** oversold breadth = % `ticker_prune` có `D_RSI<0.30` ≥ **30%** (WASHOUT).
- **Sizing:** `base × grind`. base theo DT5G state: CRISIS 1.00 · NEUTRAL 0.75 · BULL/EXB 0.50 ·
  BEAR 0.50 (chỉ khi dd52w>-25% hoặc VIX nguội, else 0). grind = 0.50 nếu có washout trước đó
  20–90 phiên, else 1.00. (Hiện tại `capit_size=0.75`, `breadth_oversold=0.408`.)
- **Thực thi:** fire **1 LẦN** tại ngày tín hiệu → **freeze basket point-in-time** (8L quality+golden,
  giá đóng băng ngày signal) → hold **60 phiên** → bán về cash. Sau khi deploy, ngày-qua-ngày KHÔNG
  còn quyết định nào ngoài đồng hồ hold 60 phiên.
- **Ramp 3 phiên hiện tại KHÔNG phải tranche** — nó là *execution smoothing của một size đã chốt*
  (giảm impact), **không** phải quyết định mới. Đây là điểm mấu chốt phân biệt (xem §1).

## Điểm mấu chốt: ramp cơ học ≠ tranche

| | Ramp 3 phiên hiện tại | Tranche T1/T2/T3 |
|---|---|---|
| Bản chất | 1 quyết định, trải 3 phiên | **3 quyết định độc lập** |
| Thông tin giữa các bước | không có (size đã chốt) | **có — chờ bằng chứng mới** (breadth ổn định / state xác nhận) |
| Trạng thái phải theo dõi | chỉ đồng hồ hold 60 phiên | **episode nhiều tuần: đang tranche mấy / trigger kế tiếp / basket policy / đồng hồ hold phân mảnh** |
| Chi phí vận hành | ~0 (stateless) | **toàn bộ nằm ở quản lý statefulness + conditionality qua nhiều ngày** |

Toàn bộ chi phí vận hành của tranche-hóa = phải mang một **"CAPIT campaign" có trạng thái sống
qua nhiều phiên EOD** thay vì một sự kiện gọn 3 phiên. 4 câu trả lời dưới đây đều xoay quanh việc
quản lý trạng thái đó cho an toàn (không mất dấu, không double-fire, idempotent).

---

## 1. Quy trình lập plan T+1 cần thay đổi gì

### 1a. Cần một FILE TRẠNG THÁI EPISODE sống qua nhiều ngày
Hiện single-shot không cần nhớ gì giữa các ngày. Tranche thì cần một bản ghi episode bền, ghi
atomic (`tmp`+`os.replace`, coding_guidelines §5), đọc mỗi lần lập plan EOD. Đề xuất tên
non-canonical (không bị `load_plan()` nạp nhầm, không bị EOD clobber — như file discretionary TV1):
`data/capit_campaigns/capit_episode_<account>_<signal_date>.json`.

Mỗi ngày lập plan EOD, generator chạy thêm 1 nhánh:
1. **Có episode nào ĐANG MỞ không?** (đọc file episode, status != closed/expired).
2. Nếu có và tranche kế tiếp = pending → **đánh giá trigger** (§1b). Trigger đạt → chèn lệnh tranche
   vào `plan_<account>_<T+1>.json` (book=`CAPIT`); chưa đạt → emit dòng "holding, chờ T2 trigger,
   ngày thứ N của episode".
3. Nếu không có episode mở → chạy logic phát-tín-hiệu washout như cũ; fire = **mở episode mới +
   deploy T1** (KHÔNG deploy full size).

### 1b. Trigger đọc field gì MỖI NGÀY để quyết "hôm nay có thêm T2 không"
- **T1 (fire ngay):** washout đã kích (oversold ≥30%) + DT5G state hợp lệ → deploy tranche 1.
- **T2 ("khi ổn định"):** cần bằng chứng breadth ĐANG HỒI, không phải mức tuyệt đối. Đề xuất đọc
  **xu hướng oversold**: oversold đã tạo đáy và **giảm ≥ K điểm % trong ≥ M phiên liên tiếp**
  (vd off-đỉnh ≥8pp, giữ ≥3 phiên) = "hết rơi tự do". (breadth là metric BQ tính overnight trên
  `ticker_prune` — đọc T-1 từ BQ là ĐÚNG, KHÔNG vi phạm bright-line same-day; chỉ **ref price của
  lệnh** mới bắt buộc DNSE live.)
- **T3 ("xác nhận mạnh"):** DT5G state **cải thiện** (vd rời CRISIS→NEUTRAL, hoặc NEUTRAL→BULL) và
  giữ ≥ cap_commit phiên, HOẶC breadth về ngưỡng lành (vd % trên MA200 hồi qua mốc). Đọc
  `vnindex_5state_dt5g_live` qua `get_gated_state()` — TUYỆT ĐỐI không bare `vnindex_5state`
  (bẫy base, planning_mini + coding_guidelines §9).
- **Ngưỡng cụ thể (K/M/cap_commit) là tham số Taylor phải backtest** — tôi chỉ nêu *đọc field nào*,
  không tự chốt số.

### 1c. Quyết định basket-freeze (fork thật, ảnh hưởng trực tiếp cách lập plan)
- **Freeze-at-T1 (khuyến nghị vận hành):** T2/T3 chỉ **top-up thêm CÙNG rổ** đã đóng băng ở T1, lên
  tỷ trọng cao hơn. Dễ theo dõi nhất. Ngoại lệ: mã nào redflag/anomaly_gate bật SAU T1 thì KHÔNG
  top-up (loại khỏi tranche kế, giữ nguyên phần đã mua). Một đồng hồ hold.
- **Refresh-per-tranche:** mỗi tranche re-run 8L selection tại ngày của nó → responsive hơn nhưng
  **đồng hồ hold 60 phiên phân mảnh**: mỗi tranche có ngày vào + ngày ra riêng → phải theo dõi 3
  ngày exit độc lập, và đuôi campaign kéo dài xa quá 60 phiên gốc (T3 vào muộn giữ tới ~signal+90+).
  Chi phí theo dõi cao gấp bội. → Nếu chọn hướng này phải chấp nhận exit staggered làm rõ trong
  file episode.

---

## 2. Rủi ro vận hành thực tế

### 2a. Episode kéo dài nhiều tuần/tháng → nguy cơ MẤT DẤU
Single-shot xong trong ~3 phiên nên không cần "nhớ". Campaign tranche mở nhiều tuần → **bắt buộc**
báo cáo hàng ngày mang 1 dòng trạng thái bền để không bao giờ mất dấu "đang ở tranche mấy". Trường
mới cần trong file episode (xem §4). Rủi ro cụ thể phải chặn:
- **Double-fire:** EOD chạy lại (crash giữa chừng) không được deploy lại tranche đã deploy → mỗi
  tranche có `status: pending|filled` + `deployed_date`, ghi atomic ngay sau khi chèn lệnh
  (idempotent, coding_guidelines §5). Không chắc tranche đã fire chưa → fail-safe dừng + báo người,
  không đoán-rồi-deploy.
- **Grind self-suppression:** logic grind hiện tại (washout 20–90 phiên trước → nửa size) sẽ tự coi
  chính campaign đang mở là "washout trước đó" và bóp một tín hiệu mới thật. Nếu tranche-hóa, phải
  làm rõ grind tính theo *episode* chứ không theo từng lần deploy, kẻo campaign tự bóp mình.

### 2b. T2/T3 KHÔNG BAO GIỜ kích (thị trường cứ xấu dần) → vốn nằm im bao lâu?
Hai hướng thất bại, xử lý khác nhau:
- **Xấu dần / breadth càng oversold:** đây KHÔNG phải lỗi — dry powder chờ đáy sâu hơn đúng tinh
  thần "mua khi sợ hãi có tính toán". NHƯNG cần luật rõ: washout **sâu hơn** (oversold vượt đỉnh
  cũ) nên (i) *đẩy nhanh* deploy (gộp T2+T3 vào 1 nhịp "all-in nỗi sợ") hay (ii) coi là **episode
  MỚI**? — quyết định chính sách, escalate, đừng tự chọn. Mặc định an toàn: coi là cùng episode,
  cho phép accelerate nhưng KHÔNG mở episode chồng episode (tránh double-count size).
- **Sideway vô định (không hồi, không sâu thêm):** vốn earmark cho T2/T3 nằm im. **CẦN time-out.**
  Đề xuất: nếu tranche kế không trigger trong **N phiên** kể từ signal (N = tham số Taylor chốt, vd
  ~40–60 phiên ≈ đúng bằng hold horizon), thì **hết hạn**: hủy các tranche còn lại, giải phóng vốn
  earmark về LAG/parking. Không giữ tiền chờ vô thời hạn. Ghi `expiry_session` trong file episode
  ngay khi mở, để deadline minh bạch từ đầu, không phải quyết định mờ về sau.

## 3. Tương thích "Trứng vàng" — CÓ CẢNH BÁO CHẶN

⚠️ **Tiền đề "user rút Trứng vàng khi CAPIT fire" HIỆN KHÔNG CÒN HIỆU LỰC.** Theo KB
(planning_mini + memory): SpaceX + ZaloPay đều `manual_offbook_assets_vnd=0` — Trứng vàng **đã
rút hết vĩnh viễn**, không phải ATM nạp-lại-theo-nhu-cầu. **Không được** thiết kế tranche dựa trên
giả định rút thêm Trứng vàng ở T1/T2/T3. Nguồn vốn CAPIT phải làm rõ TRƯỚC (escalate) — nhiều khả
năng là **cash trong book** (LAG NAV) chứ không phải off-book.

Với giả định nguồn = cash trong book, 2 phương án staging:
- **(A) Earmark full 1 lần, giữ phần chưa dùng ở dạng cash chờ T2/T3** — ưu: 1 thao tác, tiền SẴN
  SÀNG fire same-day ngay khi trigger đạt (không phụ thuộc người có mặt đúng ngày T2 để chuyển
  tiền); nhược: cash idle ăn lãi ~0% (drag nhỏ vì sleeve chỉ 1 phần NAV), và làm phồng cash book,
  cần đánh dấu "earmarked, không cho allocator/parking xài nhầm".
- **(B) Rút/earmark từng tranche khi fire** — ưu: vốn còn sinh lợi tới sát lúc cần; nhược: chèn
  **human-in-the-loop** vào mỗi trigger — nếu người không rảnh đúng ngày T2, tranche trượt, **mất
  cửa** (mà cửa mua trong sợ hãi thường rất hẹp). Rủi ro lỡ nhịp > lợi ích lãi chờ.

**Khuyến nghị vận hành:** ưu tiên **(A)** — vốn phải AVAILABLE dạng cash-earmark TRƯỚC khi trigger,
để tranche fire same-day trên tín hiệu, không kẹt bước cấp vốn thủ công. Drag lãi-chờ là nhỏ và tối
ưu riêng được. NHƯNG điều kiện tiên quyết vẫn là làm rõ nguồn vốn (Trứng vàng đã hết) — escalate.

## 4. Đề xuất field/format cụ thể

### 4a. File episode `data/capit_campaigns/capit_episode_<account>_<signal_date>.json` (atomic write)
```json
{
  "artifact_type": "CAPIT_CAMPAIGN_STATE",
  "not_canonical_daily_plan": true,
  "account": "SpaceX", "account_no": "0002023347",
  "episode_id": "CAPIT_SpaceX_20260726",
  "signal_date": "2026-07-26",
  "dt5g_state_at_signal": "NEUTRAL",
  "oversold_at_signal_pct": 31.2,
  "total_target_pct_nav": 0.75,          // = base×grind như hiện tại, chia cho các tranche
  "funding_source": "book_cash_LAG",      // KHÔNG mặc định trứng vàng — phải xác nhận
  "basket_policy": "freeze_at_T1",        // hoặc "refresh_per_tranche"
  "expiry_session": "2026-09-20",         // time-out: tranche chưa fire sau mốc này bị hủy
  "grind_scope": "per_episode",           // để campaign không tự bóp mình
  "status": "open",                        // open | completed | expired
  "current_tranche": 1,
  "deployed_pct_nav": 0.30,
  "tranches": [
    {"n":1,"planned_pct":0.30,"status":"filled","trigger":"washout_fired","deployed_date":"2026-07-27","hold_exit_target":"2026-10-20"},
    {"n":2,"planned_pct":0.25,"status":"pending","trigger":"oversold off-peak >=8pp for >=3 sessions"},
    {"n":3,"planned_pct":0.20,"status":"pending","trigger":"DT5G state improves >=1 step, hold cap_commit"}
  ],
  "basket_frozen": ["...tickers point-in-time..."]
}
```

### 4b. Trong `plan_<account>_<T+1>.json` — thêm block tóm tắt để bot/Mafee thấy ngay
```json
"capit_campaign": {
  "episode_id": "CAPIT_SpaceX_20260726",
  "action_today": "deploy_tranche_2" ,     // hoặc "hold_waiting_T2" / "none"
  "tranche": 2, "of": 3,
  "deployed_pct": 0.55, "target_pct": 0.75,
  "day_of_episode": 18,
  "next_trigger": "DT5G state improves >=1 step",
  "expiry_session": "2026-09-20"
}
```

### 4c. Trading Daily / plan report — 1 dòng bền (mỗi ngày, kể cả ngày không hành động)
> `CAPIT campaign CAPIT_SpaceX_20260726 · MỞ · tranche 2/3 · đã giải ngân 55%/75% target ·
> ngày 18/episode · chờ trigger T3 (DT5G lên ≥1 bậc) · hết hạn 2026-09-20`

Ngày không có episode: `CAPIT: không có campaign mở`. Im lặng hoàn toàn = không phân biệt được với
pipeline chết (quiet-heartbeat convention) → LUÔN có dòng này.

---

## Tóm tắt cho người quyết
- Ramp cơ học hiện tại là *execution smoothing*, tranche là *3 quyết định gated bằng bằng chứng mới* —
  chi phí vận hành nằm TRỌN ở việc mang một campaign có trạng thái sống qua nhiều tuần.
- Cần: (1) file episode bền, atomic, non-canonical; (2) nhánh mới trong plan-gen đọc episode + đánh
  giá trigger mỗi ngày (breadth-trend T-1 từ BQ OK; ref price DNSE live); (3) time-out chống giữ tiền
  vô định; (4) dòng trạng thái bền trong report chống mất dấu.
- **2 chặn cứng:** (a) Trứng vàng ĐÃ HẾT — không được lấy làm nguồn vốn tranche; nguồn vốn phải xác
  nhận trước (escalate). (b) Grind + basket-freeze + hold-clock phân mảnh là 3 fork chính sách, không
  tự chốt — Taylor cho số, user/Mike quyết.
- Đây là "NẾU tranche hóa thì vận hành thế nào", chưa khẳng định nên tranche. Chờ backtest Taylor.
