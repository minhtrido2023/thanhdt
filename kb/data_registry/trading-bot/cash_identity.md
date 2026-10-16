---
kind: derived-check (không có file dữ liệu riêng; đọc một file lời xác nhận do người ghi)
status: CANONICAL cho câu hỏi "có biến động tiền nào chưa đối chiếu xong không" — merge master 2026-10-13 (nhánh feat/fund-cashflow-detect-20261012); lời xác nhận chưa ghi, xem policy quỹ mở
source: mike/bin/cash_identity.py (đọc nav_history_<account>.csv + dnse_raw_<ngày>.jsonl + account_cash_flows.json + corp_actions.json + cash_identity_acks.json)
group: trading-bot
role: đẳng thức tiền hằng tối — tự phát hiện dòng tiền ngoài (nạp/rút) mà sổ dòng tiền chưa có bản ghi khớp, và số lượng cổ phiếu đổi ngoài lệnh đã đọc
writer: "KHÔNG ghi sổ nào. Kết quả đi ra: (1) MỘT dòng trung tính ở dòng 💰 NAV của báo cáo ngày + `cash_flow_investor_line` của nav_period_returns.py; (2) chi tiết vận hành ở nav_snapshot_<account>_<ngày>.json (`cash_flow_warnings`, `cash_flow_ops`), stderr của nav_period_returns.py / report_delivery_gate.py, và tin nhắn Trading Daily do `cash_identity.py --notify-snapshot` gửi (bước này ghi trạng thái gửi vào chính nav_snapshot JSON)"
---

# Đẳng thức tiền — `mike/bin/cash_identity.py`

Bước 2/4 của chính sách "tài khoản = quỹ mở" (`kb/projects/fund-unit-performance-policy-20261010.md`).

## Là gì
Với MỖI cửa sổ giữa hai lần chụp NAV liên tiếp của một tài khoản:

    ΔK = bán − mua − phí − thuế bán + cổ tức + lãi Trứng vàng − khấu trừ rút Trứng vàng
         + [dòng tiền ngoài] + nhiễu
    K  = cash + cum_dividend_excl − margin_debt + offbook_assets + egg_assets   (cột nav_history)

K là "tôi SỞ HỮU bao nhiêu tiền" (§25), không phải sức mua. Vay/trả ký quỹ và chuyển tiền ↔ Trứng
vàng triệt tiêu trong K. Song song, ở MỌI cửa sổ, số lượng vị thế đổi phải bằng đúng lệnh đã đọc +
cổ phiếu thưởng/cổ tức cổ phiếu ĐÃ KÝ trong `data/corp_actions.json`.

Một cửa sổ MỞ (cần người xem) khi:
- số lượng cổ phiếu đổi mà lệnh + sự kiện đã ký không giải thích ⇒ nhãn **"không kết luận được"**
  (tiền của giao dịch không thấy có thể đang bù trừ đúng một khoản nạp/rút — phần dư tiền ~0 không
  chứng minh được gì); hoặc
- phần dư tiền sau khi trừ dòng tiền ĐÃ khai vượt **±0,05% NAV đầu cửa sổ** ⇒ nhãn **"cần xác nhận
  khoản nội bộ"** nếu một khoản nội bộ chưa mô hình hoá còn phủ được phần dư (lãi vay ghi dồn khi có
  dư nợ; khấu trừ rút Trứng vàng lớn hơn mức đã đo; cổ tức ghi và trả trong cùng cửa sổ), còn lại
  là **"nghi nạp/rút chưa khai"**.

Ngoài ra: tổng phần dư của 20 cửa sổ gần nhất (chỉ cửa sổ kiểm được, không đang mở và chưa có lời xác nhận khớp) vượt 0,05% ⇒
MỘT dòng **"phần dư trôi có hệ thống"** (khoản nhỏ lặp lại, hoặc một hằng số của đẳng thức đã cũ).

Module KHÔNG BAO GIỜ ghi vào [`account_cash_flows.md`](account_cash_flows.md).

## Ai thấy gì
| Nơi | Thấy gì |
|---|---|
| Báo cáo ngày/tuần/tháng gửi nhà đầu tư | tối đa MỘT dòng: "ℹ️ Có N khoản biến động tiền chưa đối chiếu xong (lớn nhất X đ); tỉ suất kỳ chứa ngày đó có thể được điều chỉnh." — chỉ khi còn cửa sổ mở |
| Trading Daily (`cash_identity.py --notify-snapshot`, do `eod_trading_report.sh` / `nav_sync_retry.sh` / `nav_snapshot_daily.sh` gọi sau khi NAV đã ghi) | chi tiết đầy đủ của cửa sổ kết thúc ĐÚNG ngày chụp; cửa sổ cũ gộp một dòng đếm mỗi tối (kể cả cửa sổ THIẾU BẰNG CHỨNG — không kiểm được / không đối chiếu được số lượng — trong 30 ngày qua; cửa sổ mốc khởi điểm không đếm); dòng trôi gửi chi tiết một lần. Gửi hỏng ⇒ stderr mang `NOTIFY_FAILED` |
| `nav_snapshot_<TK>_<ngày>.json` | `cash_flow_warnings` (mọi cửa sổ đang mở), `cash_flow_investor_line`, `cash_flow_ops` (`lines` + `status` gửi) |
| `nav_period_returns.py` | `cash_flow_investor_line` (chép vào báo cáo tuần/tháng) + `cash_flow_warnings` (cho người soạn, KHÔNG chép) |
| `report_delivery_gate.py` | stderr; nhắc khi báo cáo thiếu dòng trung tính hoặc mang dòng vận hành; không chặn |

## Ngưỡng 0,05% — đo, không lấy sẵn
135 cửa sổ thật (SpaceX 69, ZaloPay 66) tới 2026-10-12, sổ dòng tiền rỗng, |phần dư| theo % NAV:
trung vị 0,0000 · p90 0,0066 · p95 0,0115 · p99 0,0543 · max 0,1124; số cửa sổ vượt
0,005/0,01/0,02/0,05/0,1 = 18/11/4/2/1. Chọn 0,05 vì đó là cận dưới dải PHẢI SỬA của chính sách
(điểm 4) — ngưỡng cao hơn để lại dải mù mà chính sách buộc sửa. **Biên so với nhiễu thật chỉ ~1,7
lần**: hai cửa sổ dưới ngưỡng lớn nhất đạt 0,0294% (SpaceX 07-31→08-03) và 0,0217% (ZaloPay
08-27→08-28). Bảng từng ngày:
`agents/Taylor/research/fund_cashflow_detect_20261012/arch_review_ea9d6969a/ci_real_*.txt`.

## Đóng một cửa sổ (người làm, kèm bằng chứng)
- Đúng là nạp/rút ⇒ bản ghi deposit/withdraw có ngày + giờ rơi vào cửa sổ trong
  `data/account_cash_flows.json`; khai thiếu/thừa thì phần còn lại vẫn mở.
- Đã xem, không phải nạp/rút ⇒ một lời xác nhận trong **`data/cash_identity_acks.json`**
  (`{"<tài khoản>": [bản ghi]}`), mỗi bản ghi: `window` (`from`/`to` = đúng hai `balance_ts` của
  cửa sổ), `acked_residual_vnd` (phần dư đã xem, có dấu), `acked_qty_gaps` (`{mã: số lượng}` đổi
  ngoài lệnh đã xem, nếu có), `reason`, `evidence`, `confirmed_by`, `confirmed_date`. Chỉ có hiệu lực
  khi phần dư đo được lệch `acked_residual_vnd` không quá ngưỡng VÀ số lượng lệch đúng bằng số đã
  ghi; lệch hơn ⇒ cửa sổ mở lại và nêu phần chênh. File vắng mặt = chưa có lời xác nhận nào. File
  hỏng hoặc có MỘT bản ghi sai ⇒ không lời nào có hiệu lực + một dòng vận hành nêu file và lỗi.
- Bản ghi `market_only` của sổ dòng tiền KHÔNG đóng được cửa sổ nào ở đây (không mang số tiền nên
  từng che được khoản nạp bất kỳ cùng ngày). Nó vẫn mở cổng bước nhảy NAV 5% như trước.

## Bẫy
1. **Ba cửa sổ lịch sử đang mở** tới khi có `data/cash_identity_acks.json`: SpaceX 07-02→07-03
   (−539.935 đ, 0,054%, dòng 07-02 chụp giữa loạt lệnh sáng go-live); SpaceX 08-27→08-28 (MBB +110 cp
   ngoài lệnh, phần dư −1.107.515 đ) và ZaloPay 08-27→08-28 (MBB +20 cp, −206.656 đ): tiền đổi thành
   cổ phiếu ở giá vốn 10.000 đ/cp — KHÔNG phải rút tiền, KHÔNG phải "DNSE trừ dồn". Chưa xác minh
   bằng nguồn ngoài rằng đó là quyền mua phát hành thêm. Bản đề xuất đúng schema:
   `agents/Taylor/research/fund_cashflow_detect_20261012/proposed_acks.json`.
2. **Hằng số ĐO, không phải biểu phí**: `EGG_DAILY_RATE = 0,023397%/ngày` (80 cửa sổ, 08-19 →
   10-12); `EGG_WITHDRAW_COST = 0,2013% số rút` (2 lần rút 2026-09-17, cùng kỳ gửi 29 ngày ⇒ chưa
   phân biệt được "theo số rút" với "theo số ngày đã gửi"). DNSE đổi lãi suất/biểu phí ⇒ dòng "phần
   dư trôi" là chỗ báo; đo lại hằng số, không nâng ngưỡng.
3. **Không mô hình hoá** (nằm trong phần dư): lãi vay ký quỹ / phí ứng trước / lãi không kỳ hạn /
   phí lưu ký DNSE ghi DỒN theo kỳ; phí UPCOM thấp hơn HOSE; thuế bán cổ phiếu thưởng; cổ tức chốt
   quyền và chi trả trong cùng cửa sổ.
4. Dòng "phần dư trôi" không gắn cửa sổ nào nên KHÔNG có lời xác nhận nào đóng được nó; nó chỉ đi
   kênh vận hành (không vào báo cáo nhà đầu tư) và tự hết khi tổng 20 cửa sổ về dưới ngưỡng.
5. Một bản ghi `dnse_raw` không đọc được (JSON hỏng, sai kiểu) chỉ làm các cửa sổ chạm NGÀY đó
   thành "không kiểm được" (nêu file + số dòng + lỗi); bản ghi gắn rõ tài khoản khác không tính.
6. DNSE KHÔNG gửi email xác nhận nạp/rút (đo 2026-10-12: 251 thư từ dnse.com.vn từ 06-01, 0 thư
   nạp/rút); báo cáo tháng chỉ tháng 07 có mục "Sao kê chứng khoán - tiền" ⇒ không có nguồn chứng
   từ theo ngày để wire. Chi tiết: `agents/Taylor/research/fund_cashflow_detect_20261012/B_result.md`.

## Không phủ
- Nhãn "cổ tức ghi và trả trong cùng cửa sổ" (phần dư dương ≤ 15% giá trị cổ phiếu / 0,95) rộng: một khoản
  nạp thật nhỏ có thể mang nhãn nội bộ này. Cửa sổ vẫn MỞ (không âm tính giả) nhưng nhãn dễ dẫn người duyệt
  tới ack nhầm — cần bằng chứng (`cashDividendReceiving` > 0 gần đó) hoặc trần chặt hơn (arch-review vòng 2, N5, chưa làm).
- Bản ghi vị thế được nhận trong ±10 phút quanh lần chụp; ngoài khoảng đó = không đối chiếu được số lượng.
  Bản ghi vị thế RỖNG trong khi NAV có cổ phiếu = lỗi đọc của broker (đã thấy: dnse_raw_2026-08-20 SpaceX 19:07:16) ⇒ cũng không đối chiếu được.
- Chuyển CỔ PHIẾU vào/ra không kèm tiền: chỉ thấy ở dạng "số lượng đổi ngoài lệnh" (không biết giá
  trị thật) — lớp bắt chính vẫn là cổng bước nhảy NAV và cổng phần dư số lượng của
  `daily_nav_snapshot.py`.
- Nạp/rút đi kèm lệnh đặt NGOÀI bot trong cửa sổ KHÔNG đọc được vị thế ở một đầu (lịch sử thật:
  3/135 cửa sổ, đều là dòng chụp lại/chụp giữa phiên): chỉ có một dòng "không đối chiếu được số
  lượng" ở kênh vận hành của đúng lượt chụp đó.
- Nạp/rút đi kèm lệnh ngoài bot ở mã có sự kiện cổ phiếu thưởng đã ký CÙNG cửa sổ, với số lượng
  trùng đúng số cổ phiếu thưởng.
- Cửa sổ từ mốc khởi điểm tới dòng nav_history đầu tiên (không có số dư đầu): luôn liệt kê "không
  kiểm được", phải đối chiếu tay với sao kê.
- Trôi chậm đã quá 20 cửa sổ mà không ai xử lý.

## Nợ (chưa làm ở vòng 2, theo arch-review `arch_review_ea9d6969a/REVIEW.md`)
- **G1** `nav_unit_ledger_selfcheck.py` phần A2 đọc `data/` sống (số assertion tăng theo mỗi dòng
  nav_history mới); `nav_jump_flow_gate_selfcheck.py` ca N11 cần `data/account_inception.json` thật.
- **G2** mỗi lần gọi đọc lại toàn bộ `dnse_raw` (264 MB / 101 file: ~2 giây, tăng tuyến tính); nếu
  sau này archive `dnse_raw` thì mọi cửa sổ cũ có giao dịch thành cảnh báo giả ⇒ phải đóng băng kết
  quả các cửa sổ cũ trước khi archive.
- **G4** mã lệnh DNSE không duy nhất qua các ngày — code khoá theo ngày nên đúng; đừng dedupe theo
  mã toàn cục.
- **G5** subprocess `nav_period_returns.py` trong cổng giao báo cáo không có timeout và giữ `flock`.

## Dùng
    python3 mike/bin/cash_identity.py --account SpaceX [--asof YYYY-MM-DD] [--json]
    python3 mike/bin/cash_identity.py --account SpaceX --notify-snapshot YYYY-MM-DD [--channel trading_daily]
rc: 0 = không có gì đang mở · 3 = CÓ cửa sổ mở / phần dư trôi · 1 = không chạy được (hoặc có thứ
phải gửi mà không gửi được). Selfcheck khép kín (không broker, không BigQuery, không ghi data/,
không gửi tin): `python3 mike/bin/cash_identity_selfcheck.py`.
