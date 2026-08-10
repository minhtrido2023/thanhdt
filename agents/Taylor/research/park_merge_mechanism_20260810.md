# Cơ chế merge L1 park_trim + L2 jit_unpark vào `orders[]` — thiết kế + prototype

**Job** `Taylor_20260810_131833` · 2026-08-10 · Taylor
**Prototype**: `mike/agents/Taylor/pending_park_merge_20260810/` (README = tài liệu duyệt).
Tài liệu này giữ phần **phân tích** và **cách tái lập**; không lặp lại README.

---

## 1. Hai sự cố, một nguyên nhân gốc

| Ngày | Triệu chứng | Cơ chế hỏng |
|---|---|---|
| 2026-08-06 | 0 lệnh cả 2 account đúng phiên entry chuẩn 6 mã LAG | cổng `if not h["reconcile"]["ok"]` chặn **cả tài khoản** vì 1 mã lệch sổ (VHM chia CP chưa vào registry) |
| 2026-08-07 | thừa 1.200cp SpaceX + 400cp ZaloPay, phát hiện trước giờ lệnh 15' | merge tay ghi lệnh gộp nhưng **không xoá** lệnh JIT gốc |

Cách đọc SAI: "một lần cổng quá chặt, một lần script quên xoá — hai lỗi rời rạc."
Cách đọc ĐÚNG: **khâu L1/L2 → `orders[]` không có cơ chế, chỉ có script tay.** Script tay hỏng
theo cả hai hướng — quá chặt (mất phiên) và quá lỏng (bán trùng) — vì mỗi lần viết lại là một lần
đoán lại các bất biến. Bản vá kế toán 08-10 sửa hướng "quá chặt"; bản này sửa hướng "quá lỏng"
**và** đóng luôn khả năng phải viết script mới lần sau.

## 2. Vì sao dedup theo `id` không thể đúng

```
merge_three_in_one_20260807.py  →  id = SELL-{TK}-PARK-{i:02d}     (đánh số CHẠY theo rổ)
approve_plan_with_jit.sh        →  id = SELL-JIT-PARK-{TK}-01
                                    dedup: if oid in existing_ids: continue
```

Ba khuyết tật độc lập, mỗi cái đủ để hỏng:

1. **Hai namespace.** Dedup theo id chỉ đúng khi mọi writer dùng CÙNG quy tắc đặt tên. Không có
   gì cưỡng chế điều đó — và thực tế hai script do hai người/hai lượt viết ra đã lệch nhau.
2. **Id đánh số chạy `{i:02d}`.** Rổ đổi 1 mã ⇒ toàn bộ số thứ tự dịch ⇒ cùng một lệnh kinh tế
   mang id khác ở hai lần chạy. Dedup theo id hỏng **ngay cả khi chỉ có một writer**.
3. **`continue` là "thêm nếu chưa có".** Ngữ nghĩa đó không bao giờ SỬA được một lệnh đã sai; nó
   chỉ biết thêm. Artifact tính lại với qty mới ⇒ giữ nguyên qty cũ, im lặng.

⇒ Danh tính phải là **`(ticker, side, nguồn)`**, và phép ghi phải là **thay thế**, không phải thêm.

## 3. Thiết kế: sở hữu một vùng, dựng lại mỗi lần

```
orders[]  =  [ lệnh merge sinh ra (dựng lại từ L1/L2) ]  +  [ lệnh của writer khác (giữ nguyên) ]
                        ▲ vùng SỞ HỮU                              ▲ bất khả xâm phạm (bất biến I5)
```

`is_owned(o)` — hai nhánh CỐ Ý tách rời:
- `merge_owner == "park_merge_v1"` — dấu tường minh của cơ chế này;
- `side=sell ∧ book=PARK ∧ play_type ∈ {PARK_TRIM, JIT_UNPARK, PARK_TRIM+JIT_UNPARK}` —
  **nhận nuôi** lệnh do script one-off cũ ghi (không có dấu).

Nhánh 2 là thứ khiến chạy merge mới trên một plan đã bị script cũ làm hỏng **hội tụ** thay vì
nhân đôi. Bỏ nhánh 2 = mở lại đúng lỗ hổng 08-07.

### Vì sao cần CẢ hai lớp bảo vệ (số đo, không phải lập luận)

Dựng lại trạng thái hỏng 08-07 từ artifact thật rồi đo:

| Account | Thừa | Có vi phạm trần `sellable` không? | Ai bắt được |
|---|---|---|---|
| SpaceX | +1.200cp (6.900 → 8.100) | **KHÔNG** — dư địa sellable còn đủ | chỉ **nhận nuôi** (lớp 2) |
| ZaloPay | +400cp (2.500 → 2.900) | **CÓ** — VHM 400 > 300 | cả **bất biến I2** (lớp 3) |

Nếu chỉ có bất biến sellable, ca SpaceX **lọt hoàn toàn khỏi cơ chế này** — bán thừa 1.200cp mà
không cờ nào của merge bật. Nếu chỉ có nhận nuôi, lệnh thừa do một writer xa lạ (book khác) ghi vào
vẫn lọt. Hai lớp che hai lối khác nhau; đây là số đo trên chính dữ liệu sự cố, không phải lập luận
phòng xa.

⚠️ **Đính chính phạm vi (quant-skeptic 2026-08-10):** "không cờ nào bật" đúng **trong phạm vi merge**,
KHÔNG đúng trên toàn hệ. `mike/bin/preflight_check.sh:73-93` đã có `MERGE_STALE_SRC` +
`SELL_GT_SELLABLE` từ **chính ngày 08-07**, và nhánh `MERGE_STALE_SRC` **bắt được** ca SpaceX (hai
lệnh cùng `(sell, ticker)` trong đó có lệnh mang `merged_from`). Khác biệt là **tầng**: preflight
phát hiện lúc thực thi, merge ngăn lúc soạn. Chúng ăn khớp — merge ghi
`merged_from.sellable_at_calc`, đúng field nhánh (b) của preflight bám vào. Cơ chế này là lưới
**thứ hai**, không phải lưới duy nhất; bản nháp đầu của tài liệu đã trình bày sai điểm này.

## 4. Cổng đối soát: từ chối theo TẦNG, không theo tài khoản

```
chấp nhận tầng  ⇔  decision đúng ∧ (reconcile_ok is True ∨ reconcile_partial is True)
```

- Không kế thừa `assert l2["reconcile_ok"] is True` (`merge_three_in_one_20260807.py:32`) — assert
  đó sẽ dừng sai đúng ngày PARTIAL mà bản vá 08-10 vừa cứu được.
- L1 bị từ chối **không** khoá L2 và ngược lại (ca `P3`). Đây là bài học 08-06 ở dạng bất biến
  test được, không phải ghi chú trong văn xuôi.
- `decision ∈ {BLOCKED_RECONCILE, NO_JIT, …}` hoặc artifact thiếu hẳn ⇒ tầng đó đóng góp 0 lệnh,
  **không** phải lỗi (ca `P4`).

## 5. Các quyết định thiết kế khác và lý do

| Quyết định | Lý do |
|---|---|
| `ref_price` L1≠L2 ⇒ **cảnh báo + lấy giá thấp**, không dừng | script cũ `assert` bằng nhau ⇒ một chênh giá vô hại dừng cả plan = lại đúng lớp lỗi 08-06. Giá thấp = ước tính tiền bán thận trọng; executor định giá lại từ `ref_price`+urgency. |
| Cắt **L1 trước, L2 sau** khi vượt `sellable` | L1 hoãn được 1 phiên, hướng sai là "trim ít hơn" = an toàn. L2 cắt ⇒ P0 `check_plan_funding` chặn ⇒ **mất phiên entry**. |
| Cắt vào L2 ⇒ `jit_underfunded=true` trên lệnh mua | để người duyệt thấy TRƯỚC, không để P0 phát hiện hộ lúc 09:05. |
| Merge **không đổi qty lệnh mua** kể cả khi `buy_amendments.qty_final` khác | đổi cỡ lệnh mua là việc của L2/DollarBill; merge chỉ gộp lệnh bán. Lệch ⇒ cảnh báo (ca `V7`). |
| Id `PARKMERGE-SELL-{TK}`, **không đánh số chạy** | 1 mã ⇔ 1 id, ổn định qua mọi lần chạy — diệt khuyết tật (2) ở §2. |
| Fail-closed: bất biến hỏng ⇒ trả plan **nguyên vẹn**, không ghi | §5 idempotent side effects: không được để lại file nửa vời. Ghi bằng `tmp` + `os.replace`. |
| Lõi là **hàm thuần**, I/O tách ra CLI | test được không cần file thật; gọi lại được từ bước pipeline khác. |
| `priority` lệnh bán được phép **ÂM** | `priority` chỉ là khoá sắp xếp tăng dần (`executor.py:1232`, `plan.py:124` — đã grep, không nơi nào dùng làm chỉ số/số không âm). Clamp `max(0,…)` khiến lệnh mua ở priority 0 làm bán = mua ⇒ I3 hỏng ⇒ từ chối cả plan. Xem §5b. |
| I3 chỉ ràng buộc lệnh bán **do merge sinh ra**; lệnh bán của writer khác sai thứ tự ⇒ **cảnh báo (I3b)** | vấn đề CÓ SẴN, merge không làm nặng thêm ⇒ từ chối cả plan = lấy plan làm con tin cho lỗi mình không gây ra. Khác ca S6 (lệnh ngoài vùng đã vượt sellable) — ở đó **chạy tiếp làm vi phạm nặng thêm** nên mới fail-closed. |

## 5b. Hai khuyết tật quant-skeptic bắt được (2026-08-10) — đã sửa

Vòng 1 verdict **CONFIRMED (medium)**. Cơ chế đứng vững (tái lập độc lập khớp tới từng cp), nhưng
hai khuyết tật sống sót đợt tấn công. Cả hai đáng ghi lại vì chúng là **hai lớp lỗi khác nhau**:

### (1) Selfcheck PASS vô căn cứ — lỗi của lớp KIỂM CHỨNG, không phải của code

Ca `V1b` bản đầu:

```python
pv, _ = merge_park_orders(plan([buy_order(pri=0)]), L1_0807, None)
check("...", all(o["priority"] == 0 for o in pv["orders"] if o["side"] == "sell"))
```

Plan đó bị **REFUSED** ⇒ trả về nguyên vẹn ⇒ **0 lệnh bán** ⇒ `all([])` = `True` ⇒ ✔ xanh.
Ca test tuyên bố phủ đúng ca biên priority-0 và trên thực tế **che mất** một REFUSED cả plan.

**Bài học tổng quát hơn ca này:** mọi assert dạng `all(... for ... if <lọc>)` đều **PASS vô căn cứ**
khi bộ lọc trả rỗng. Ca test phải khẳng định **tập khác rỗng** trước, rồi mới khẳng định tính chất
trên tập đó. Đây là họ hàng gần của §23 hệ luận 1 (test tự vô hiệu theo thời gian) — chỉ khác là
nó tự vô hiệu ngay từ lúc viết.

### (2) Lệnh MUA ở priority 0 ⇒ TỪ CHỐI CẢ PLAN — tái lập đúng hình dạng 08-06

`sell_pri = max(0, min(buy_pri) - 1)`. Buy ở priority 0 ⇒ sell_pri = 0 ⇒ `max(sell) < min(buy)`
sai ⇒ I3 hỏng ⇒ REFUSED ⇒ **0 lệnh bán PARK** ⇒ lệnh mua được JIT tài trợ chết đói. Chính là hình
dạng mất-phiên 08-06, trong đúng cơ chế viết ra để diệt nó.

Sửa: bỏ clamp (priority âm hợp lệ) + tách I3b. Chứng minh ngược — khôi phục clamp rồi chạy lại:

```
✘ V1b lệnh mua priority=0 ⇒ KHÔNG từ chối plan (status OK) — ['I3: priority lệnh bán merge [0] không < mua [0]']
✘ V1b vẫn sinh đủ 3 lệnh bán (tập KHÁC RỖNG) — 0 lệnh bán
✘ V1b bán ở priority −1 < mua 0 — []
```

Phơi nhiễm thực tế: quant-skeptic đo **0/42 plan thật** chạm ca này (buy priority 1–34, mode 5)
⇒ tiềm ẩn, chưa từng nổ. Vẫn phải sửa: nó mâu thuẫn với chính học thuyết "từ chối theo tầng".

Số ca selfcheck: bản ghi bus đầu nói "47"; số thật lúc đó **54**; tôi báo "62" sau ba bản vá —
**cũng sai**, số thật **61**; sau bản vá thứ 4 (V12): **64**. Nguyên nhân đếm sai: `grep -c "^  [✔✘]"`
trên output dôi 1 vì `print_report()` cũng in một dòng `  ✘`. Đếm đúng = bọc chính hàm `check()`.
Đây là lần thứ hai trong cùng một job một khẳng định bị sai do **bộ lọc/phép đếm gián tiếp** thay
vì đo trực tiếp thứ cần đo — cùng họ với khuyết tật (1) ở trên.

## 6. Vì sao KHÔNG đưa vào `trading_bot/plan.py`

`plan.py` là module đọc plan lúc **thực thi** (`load_plan` ← `bot_execute.py`). Merge là bước
**soạn** plan. Nhét vào đó ⇒ mỗi lần bot chạy đều mang theo code có khả năng ghi đè plan (sai
tầng), và kéo **21 selfcheck phụ thuộc** (§23) cho một việc không thuộc về nó. Giữ là script riêng
ở `mike/bin/` + lõi hàm thuần = 0 selfcheck production phụ thuộc, blast radius bằng 0.

⚠️ **Hệ quả cần biết** (§24): `load_plan()` chỉ giữ key nằm trong `dataclasses.fields(PlannedOrder)`
⇒ `merge_owner`, `merged_from`, `sellable`, `jit_underfunded` **executor không bao giờ thấy**.
Đúng ý đồ — chúng là siêu dữ liệu của tầng soạn plan, sống trong JSON để merge lần sau và người
duyệt đọc. Nhưng **không được** dựa vào chúng để cưỡng chế bất cứ thứ gì ở tầng thực thi.

## 7. Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/pending_park_merge_20260810
python3 merge_park_orders_selfcheck.py            # 47/47 PASS
TZ=America/New_York python3 merge_park_orders_selfcheck.py   # PASS (không phụ thuộc TZ)
env -i /usr/bin/python3 merge_park_orders_selfcheck.py       # PASS (env trống)
```

A/B trên dữ liệu thật 2026-08-07 (chỉ đọc; bản sao ra `/tmp`, không đụng plan thật):

```bash
cd /home/trido/thanhdt/WorkingClaude
mkdir -p /tmp/pmtest
cp data/trade_plans/{plan,park_trim,jit_unpark}_{SpaceX,ZaloPay}_2026-08-07.json /tmp/pmtest/
python3 - <<'EOF'
import json, copy, sys
sys.path.insert(0, 'mike/agents/Taylor/pending_park_merge_20260810')
from merge_park_orders import merge_park_orders
for a in ('SpaceX', 'ZaloPay'):
    plan = json.load(open(f'/tmp/pmtest/plan_{a}_2026-08-07.json'))
    l1 = json.load(open(f'/tmp/pmtest/park_trim_{a}_2026-08-07.json'))
    l2 = json.load(open(f'/tmp/pmtest/jit_unpark_{a}_2026-08-07.json'))
    human = {o['ticker']: o['qty'] for o in plan['orders'] if o['side'] == 'sell'}
    plan['approved_by'] = None            # bản thật đã ký; bỏ chữ ký để so CƠ CHẾ
    # chân A — plan người đã sửa đúng
    pa, _ = merge_park_orders(copy.deepcopy(plan), l1, l2)
    auto = {o['ticker']: o['qty'] for o in pa['orders'] if o['side'] == 'sell'}
    # chân B — dựng lại trạng thái HỎNG: thêm lại lệnh JIT gốc (id namespace khác)
    broken = copy.deepcopy(plan)
    for jo in l2['orders']:
        broken['orders'].insert(0, {"id": f"SELL-JIT-PARK-{jo['ticker']}-01",
            "ticker": jo['ticker'], "side": "sell", "qty": jo['qty'],
            "ref_price": jo['ref_price'], "book": "PARK",
            "play_type": "JIT_UNPARK", "priority": 0})
    pb, rb = merge_park_orders(copy.deepcopy(broken), l1, l2)
    fixed = {o['ticker']: o['qty'] for o in pb['orders'] if o['side'] == 'sell'}
    print(a, 'A khớp:', auto == human, '| B khớp:', fixed == human,
          '| Σ tay/hỏng/auto:', sum(human.values()),
          sum(o['qty'] for o in broken['orders'] if o['side'] == 'sell'),
          sum(fixed.values()))
EOF
```

Kết quả đo được:

```
SpaceX  A khớp: True | B khớp: True | Σ tay/hỏng/auto: 6900 8100 6900
ZaloPay A khớp: True | B khớp: True | Σ tay/hỏng/auto: 2500 2900 2500
```

Chênh chân B = **+1.200cp SpaceX / +400cp ZaloPay** — đúng bằng con số sự cố đã ghi nhận trên bus
và Discord Trading Daily 05:48 ICT 2026-08-07.

## 8. Giới hạn — cái này KHÔNG giải quyết

- **Không** làm cho đề xuất L1/L2 đúng hơn. Nó chỉ chuyển đề xuất vào `orders[]` một cách đáng
  tin cậy. Sai từ L1/L2 vẫn đi thẳng vào plan.
- **Không** thay thế P0 `check_plan_funding` hay L2 JIT-unpark. Trần `sellable` ở đây là lưới thứ
  hai độc lập, không phải lý do nới lỏng gate hạ nguồn.
- **Không** tự chạy L1/L2. Chưa có cron cho hai script đó ⇒ tự động hoá vẫn dở dang (README §"việc
  phải làm trước khi wire" mục 2).
- **`sellable` là ảnh chụp lúc L1/L2 chạy** (`sellable_at_calc`). Giữa lúc chạy và giờ đặt lệnh
  T+2 có thể giải phóng thêm — merge dùng số **cũ hơn** ⇒ hướng sai an toàn (bán ít hơn dư địa
  thật), nhưng nếu artifact quá cũ thì nó cũng có thể **quá lỏng** theo hướng ngược lại nếu có
  lệnh bán ngoài kế hoạch chen vào. Đây là lý do bất biến I2 tính trên **toàn bộ** `orders[]` chứ
  không chỉ phần merge sinh ra.
- **n=1 ngày dữ liệu thật.** A/B đứng trên đúng phiên 2026-08-07 (2 account). Không có ý nghĩa
  thống kê nào ở đây và cũng không cần — đây là bất biến cơ chế, không phải edge.
