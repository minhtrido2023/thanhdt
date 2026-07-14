# World Cup + rổ lãi suất huy động (Pillar A′)
> Dự án đã đóng — tách khỏi context_pack 2026-07-13. Chi tiết gốc từ kb/current_ops.md.
> Status: CLOSED. ĐÓNG cả 2 hướng — N quá mỏng / 0-4 GO, không wire production.

## World Cup + rổ lãi suất huy động (Pillar A′) — ĐÓNG cả 2 hướng (2026-07-13)

User đề xuất 2 ý tưởng macro mới cùng ngày: (A) hiệu ứng năm World Cup, (B) rổ lãi suất huy động
Big-4 làm tín hiệu bổ sung Pillar A (SBV refi), tập trung xu hướng (6m-change) chứ không phải mức
tuyệt đối, và sau đó thêm ý tinh chỉnh: dùng lãi suất huy động THỰC (trừ CPI) để đo premium chính
xác hơn. Cả 2 hướng đã đo bằng số liệu thật và đóng — không wire gì vào production.

**Hướng A (World Cup) — ĐÓNG, N=4 quá mỏng, không có cơ chế**: đúng năm WC trung bình −10,6% cả
năm (khớp trí nhớ user), nhưng cửa sổ giải đấu THỰC TẾ không có hiệu ứng (trung bình −0,07%, 2/4 kỳ
dương) — điểm yếu luôn xảy ra TRƯỚC/SAU giải đấu chứ không phải TRONG lúc diễn ra (vd 2022: đáy sâu
nhất năm rơi đúng 5 ngày trước khai mạc WC Qatar, cửa sổ giải đấu lại là đoạn hồi phục +9,56%).
Không đủ cơ sở nhân quả để làm rule hay tín hiệu định tính. `probe_worldcup_vnindex_20260713.py`.

**Hướng B (deposit-rate gate, "Pillar A′") — ĐÓNG, 0/4 GO, quant-skeptic CONFIRMED (cao)**: family
pre-registered N=6 (D0 real-premium + D1 mirror-full + D2 strong-only + D3 blind-spot-only + S4/A5
read-only) qua đúng gate GO/NO-GO đã chốt trước khi biết kết quả:
- **D0 (real-premium = deposit − CPI)**: NO-GO ở N2 — fire SAI ở các đợt disinflation-bull
  (2012/2017/2019/2020-21/2025) và IM LẶNG hoàn toàn đúng cửa sổ sập 2022 cần fire nhất. Delta FULL
  −5,06pp. Đúng khớp kỳ vọng đã pre-register trước khi chạy.
- **D1/D2 (danh nghĩa)**: delta dương nhẹ (+0,17/+0,19pp) nhưng chết ở N1 — 100% phần thắng nằm
  trong cửa sổ Pillar A đã active (2023-02→04, redundant), phần tín hiệu MỚI thật sự (chu kỳ
  2025-26) lại TỐN TIỀN với VNINDEX forward dương sau de-risk (fail G2).
- **D3 (blind-spot-only, chỉ đo phần mới)**: cũng fail G2 — cùng lý do trên.
- **Phát hiện phụ hữu ích**: nỗi lo false-positive 2017 hóa ra SAI — DT5G hiếm khi lên BULL nên tier
  cap-NEUTRAL gần như vô hiệu lịch sử (chi phí 2017 = 0,00pp thực tế, dù chi phí "trên giấy" đo được
  ở D0's replica riêng biệt là −17,4pp — 2 số khác nhau vì D0 dùng replica in-fuse còn D1-D3 dùng
  overlay trên bảng published, xem plan §10.1 để hiểu khác biệt phương pháp).
- **Bonus hạ tầng (áp dụng cho MỌI experiment tương lai trên `pt_v23_audit_2014.py`)**: phát hiện +
  fix bug tie-break nondeterminism (DuckDB đổi row-order theo nội dung parquet state swap → NAV
  lệch ±0,5pp giữa các run "giống hệt"). Fix: stable-sort `(time,ticker)` + determinism-pair proof
  (md5 byte-identical). Từ nay bất kỳ ai chạy view-swap experiment trên harness này phải dùng pattern
  sort này (mẫu: `mike/agents/Taylor/run_depgate_variant_sorted.py`), nếu không delta <±0,5pp vô nghĩa.
- **Kết luận cuối**: 0/4 GO → hướng B đóng hoàn toàn theo đúng §9.2 đã duyệt trước (NO-GO = đóng,
  không tiến shadow-monitor). Muốn mở lại cần trial mới + N-budget mới, điều kiện thực chất duy nhất
  đáng mở lại: chu kỳ thắt chặt 2025-26 hiện tại kết thúc với bằng chứng point-in-time thật (không
  hồi tố) — Winston's data prerequisite (registry + routine tháng cho `deposit_rate_vn.py`/`cpi_vn.py`)
  vẫn có giá trị độc lập, không phụ thuộc GO/NO-GO của dự án này (2 consumer khác đang dùng
  `deposit_rate_vn.py` ở mức tuyệt đối: `rating_8l.py` deposit-lens LIVE hàng ngày + deposit-gate
  RECOVERY_PARK floor 7.5% dormant).

Artifact đầy đủ: `mike/agents/Taylor/plan_deposit_rate_signal_20260713.md` (§0-§11), registry
`data/results_registry.md` mục DEPOSIT-RATE-GATE, `mike/agents/Taylor/exp_depgate/`. Không đụng
production/paper/`macro_state_live.py`. R3 pin 27,84%/1,84/−18,2%/1,53 không đổi.
