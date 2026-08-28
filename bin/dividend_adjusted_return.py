#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tỉ suất lợi nhuận ĐÃ ĐIỀU CHỈNH CỔ TỨC cho một vị thế — BẮT BUỘC dùng trong mọi báo cáo.

KIẾN TRÚC 4 TẦNG — mỗi tầng một vai trò, KHÔNG lẫn lộn (sửa 2026-08-02, phản biện của user)
-------------------------------------------------------------------------------------------
    TẦNG 1 · PHÁT HIỆN (BigQuery `Close/Price`)   → "mã nào, ngày nào có sự kiện"
    TẦNG 2 · ĐO LƯỜNG (tiền mặt broker DNSE)      → "bao nhiêu đồng/cp"  ← SỐ GỘP (GROSS)
    TẦNG 3 · ĐỐI SOÁT CHẬM (`Dividend_1Y` delta)  → xác nhận độc lập, trễ theo quý
    TẦNG 4 · THUẾ TNCN 5%                         → "về túi bao nhiêu"   ← SỐ VÀO BÁO CÁO

`tav2_bq.ticker` có 2 cột giá:
  * `Price` — giá THÔ, đúng giá thật trên bảng điện (báo cáo mark-to-market dùng cột này).
  * `Close` — giá ĐÃ ĐIỀU CHỈNH cổ tức/chia tách, hồi tố từ HÔM NAY về quá khứ.

Tỉ số `Close/Price` là HẰNG SỐ giữa hai ex-date liên tiếp và NHẢY VỀ 1.0 đúng ngày ex-date của
sự kiện gần nhất. Đây là phép NHÂN, không phải phép trừ — hiệu `Close - Price` biến thiên theo
mức giá nên KHÔNG dùng hiệu số để suy ra cổ tức (ví dụ SAB: hiệu chạy −3.110 → −3.000 trong khi
cổ tức thật là đúng 3.000đ/cp).

    ratio_per_share = P_last_cum × (1 − ratio_last_cum / ratio_ex)   ← ƯỚC LƯỢNG, không phải số liệu

⚠️ NHƯNG TỈ SỐ CHỈ NÓI "CÓ SỰ KIỆN", KHÔNG NÓI "LOẠI GÌ". Cổ tức tiền mặt, cổ tức cổ phiếu, thưởng
CP, chia tách, phát hành thêm — tất cả làm tỉ số nhảy y hệt nhau. Suy ngược ra "đồng/cp" từ tỉ số là
ÁP một giả định (rằng sự kiện này là tiền mặt) mà chính dữ liệu đó KHÔNG kiểm chứng được. Vì vậy
`ratio_per_share` chỉ dùng để (a) khoanh cửa sổ ngày đi tra broker, (b) làm LƯỚI AN TOÀN phát hiện
phương trình bị nhiễm. Con số vào báo cáo là `per_share`, giải ra từ TIỀN THẬT (tầng 2).

BIGQUERY KHÔNG CÓ CỘT RAW PER-EVENT (đã quét toàn bộ 5 dataset, 2026-08-02)
Có đúng MỘT bảng đúng hình dạng cần tìm — `tav2_bq.shares_outstanding_live` (`ex_date` +
`cash_div_per_share` + `stock_div_ratio`) — nhưng chỉ có 4 DÒNG (ACB/HDC/EVG/DDV, tháng 6/2026), do
Winston chạy tay `update_shares_live.py` khi cần override `OShares`, KHÔNG phải chuỗi lịch sử cổ tức.
Dùng làm ưu tiên 1 KHI CÓ (đã phân loại sẵn tiền/cổ phiếu), nhưng không coi là nguồn có sẵn.
(Grep cột theo chuỗi 'divid' sẽ BỎ SÓT `cash_div_per_share` — lỗi này đã xảy ra thật.)

TẦNG 2 LÀ MỘT HỆ PHƯƠNG TRÌNH, KHÔNG PHẢI PHÉP CHIA
DNSE ghi cổ tức phải thu vào `balances.stock.cashDividendReceiving`. Delta DƯƠNG = tiền cổ tức mới
ghi nhận, nhưng là của TOÀN TÀI KHOẢN theo NGÀY, KHÔNG tách theo mã — nhiều mã cùng ngày chốt quyền
rơi chung một delta, nên KHÔNG chia được `delta / qty`:

    với mỗi (tài khoản a, ngày d):   delta(a,d) = Σ_mã  qty(a, mã) × per_share(mã)

Hai tài khoản SpaceX/ZaloPay có tỉ lệ nắm giữ KHÁC nhau → hai phương trình độc lập → hệ 2×2 của
ngày 23/07 (CTG và VCB cùng ex-date) có nghiệm DUY NHẤT, suy hoàn toàn từ tiền thật:

    2300·CTG + 1300·VCB = 1.620.000   (SpaceX)     ⇒ CTG = 450
    1050·CTG +  800·VCB =   832.500   (ZaloPay)    ⇒ VCB = 450

Giải theo từng THÀNH PHẦN LIÊN THÔNG. Đủ hạng + dư số ~0 ⇒ CASH_CONFIRMED. Vô định (nhiều mã trùng
ex-date mà chỉ 1 tài khoản nắm giữ) ⇒ giữ UNVERIFIED, CẤM đưa vào báo cáo — KHÔNG lấp bằng tỉ số.

Hai lỗi thật đã xảy ra trong báo cáo tháng 7/2026 (xem `mike/kb/data_registry/price-volume/
ticker_close_vs_price_dividend_adj.md`):
  1. Lấy `(Price_cuối kỳ − giá vốn)/giá vốn` mà QUÊN cộng cổ tức đã nhận → % lãi/lỗ THẤP HƠN
     thực tế (NCT báo −11,6% trong khi thật là −3,1%).
  2. Lấy `Close` (đã điều chỉnh) trừ giá vốn THÔ → phạt cổ tức HAI LẦN.

TẦNG 4 · THUẾ TNCN 5% — SỐ BROKER LÀ GỘP, TIỀN VỀ TÚI LÀ RÒNG (thêm 2026-08-02)
Cổ tức tiền mặt của cá nhân cư trú chịu thuế TNCN **5%** (thu nhập từ đầu tư vốn), khấu trừ TẠI
NGUỒN bởi tổ chức chi trả — nhà đầu tư không phải tự kê khai. Căn cứ: Thông tư 111/2013/TT-BTC
Điều 10 (thuế suất 5%) + Điều 25 (khấu trừ tại nguồn); Luật Thuế TNCN số 109/2025/QH15 (hiệu lực
01/07/2026, tức ĐANG chi phối các sự kiện tháng 7/2026 này) GIỮ NGUYÊN mức 5%.

⚠️ `cashDividendReceiving` của DNSE ghi số **GỘP (gross)** theo mệnh giá công bố; thuế bị trừ ở
thời điểm **CHI TRẢ THẬT** vào tiền mặt. KHÔNG phải giả định — đo được bằng tiền thật:

    Hằng đẳng thức đã kiểm (khớp từng đồng 16/07, 17/07, 20/07):
        totalCash == availableCash + cashDividendReceiving + depositInterest

    SpaceX, cổ tức MBB chi trả 17/07/2026 (2.400cp × 1.000đ):
        khoản phải thu xoá :  3.255.000 → 855.000        = −2.400.000  (GỘP, đúng mệnh giá)
        tiền vào availableCash:   2.925 → 2.282.925      = +2.280.000  (RÒNG)
        chênh lệch                                        =   120.000  = 5,00% CHÍNH XÁC

    Không có nhiễu: `positions` 16/07 vs 17/07 KHÔNG đổi một mã nào (không lệnh khớp), lãi tiền
    gửi chỉ +37đ. Khoản rút 302.108.211đ cùng kỳ KHÔNG phải giả định để ép số khớp — xác nhận
    ĐỘC LẬP bởi `data/execution_logs/nav_snapshot_SpaceX_2026-07-17.json`
    (`offbook_assets`, chuyển Trứng vàng, job Mafee_20260716_164743) và bằng
    `withdrawableCash` 16/07 = đúng 302.108.211.

Hệ quả cho báo cáo:
  * `Adjustment.per_share` / `.cash_per_share` là **GỘP** — giữ nguyên nghĩa, đó là số giải ra
    từ sổ broker và là số đối chiếu được với mệnh giá công bố.
  * Tỉ suất lợi nhuận công bố dùng **RÒNG** (`pl_total`, `pct_total_return`) — đó mới là tiền
    nhà đầu tư thực sự giữ. Nhưng LUÔN in kèm số gộp + số thuế, không thay số lặng lẽ.
  * **Khoản còn ở dạng phải thu vẫn đang ghi GỘP** ⇒ NAV/`totalCash` đang cao hơn thực tế đúng
    5% của phần chưa chi trả. Số nhỏ nhưng có thật — báo cáo phải nói ra, đừng lặng lẽ bỏ qua.
  * Thuế suất là THAM SỐ (`--div-tax-rate`), không hardcode vào công thức: tài khoản tổ chức/
    quỹ có chế độ khác (Luật 109/2025 còn giảm 50% thuế cho lợi tức từ quỹ đầu tư chứng khoán/
    bất động sản). SpaceX + ZaloPay đều là tài khoản CÁ NHÂN ⇒ 5%.

⚠️ CƠ SỞ THỰC NGHIỆM LÀ n=1 (mới đúng một sự kiện chi trả thật tính tới 02/08/2026 — 5 sự kiện
còn lại vẫn nằm ở khoản phải thu). Mức 5% có căn cứ pháp lý vững và số đo khớp tuyệt đối, nhưng
sự kiện chi trả THỨ HAI phải được đối chiếu lại theo đúng cách trên trước khi coi là quy luật
đã đóng. Xem `_selfcheck()` mục 15 (đã ghim số thật của ca 17/07).

QUY TẮC
-------
* Giá vốn (`cost`) là giá khớp THẬT đã trả — số THÔ, chưa điều chỉnh.
* Giá cuối kỳ dùng `Price` (thô) — đúng thứ nhà đầu tư thấy trên bảng điện.
* Cổ tức tiền mặt CỘNG VÀO TỬ SỐ (số RÒNG sau thuế), mẫu số giữ nguyên giá vốn gốc:
      total_return = (P_end + D×(1 − thuế) − cost) / cost
  KHÔNG dùng `Close_end/Close_start` để so với giá vốn: chuỗi `Close` được hồi tố từ vintage
  HÔM NAY nên mức giá của nó không cùng hệ quy chiếu với một giá khớp thô. (`Close/Close` chỉ
  đúng khi so hai NGÀY với nhau — ví dụ "mã X tăng bao nhiêu trong tuần" — không phải để so với
  giá vốn.)

⚠️ CỔ TỨC TIỀN MẶT vs CHIA TÁCH/CỔ PHIẾU THƯỞNG: tỉ số `Close/Price` KHÔNG phân biệt được hai
loại. Chia tách làm TĂNG SỐ LƯỢNG cổ phiếu (giá trị không đổi, không có tiền về); cổ tức tiền mặt
giữ nguyên số lượng và trả tiền. Vì vậy mọi sự kiện phát hiện từ BQ mặc định là `UNVERIFIED`, và
`solve_from_broker()` mới nâng lên `CASH_CONFIRMED` (giải ra từ `cashDividendReceiving` của DNSE)
hoặc hạ xuống `STOCK_SUSPECTED` (số lượng cổ phiếu đổi tại ex-date). KHÔNG đưa số `UNVERIFIED` vào
báo cáo gửi nhà đầu tư — dùng `Adjustment.cash_per_share` (trả 0 khi chưa xác minh), đừng đọc thẳng
`per_share` (trường này còn giữ ước lượng tỉ số cho mục đích chẩn đoán).

CLI
---
    # Làm báo cáo: GIẢI CẢ RỔ — mới đủ phương trình tách những ngày nhiều mã cùng chốt quyền.
    python3 mike/bin/dividend_adjusted_return.py --resolve MBB,BID,CTG,VCB,NCT,SAB \
        --from 2026-07-01 --to 2026-08-01
    python3 mike/bin/dividend_adjusted_return.py --ticker NCT --from 2026-07-21 --to 2026-07-31 \
        --cost 94360 --qty 500 --account SpaceX
    python3 mike/bin/dividend_adjusted_return.py --selfcheck
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

BQ_PROJECT = "lithe-record-440915-m9"
# bq có thể không có trong PATH khi gọi từ cron — dùng full path nếu cần
_GCP_SDK_BIN = "/home/trido/google-cloud-sdk/bin"
_BQ_BIN = shutil.which("bq") or f"{_GCP_SDK_BIN}/bq"
# bq cần cả gcloud trong PATH + CLOUDSDK_CONFIG cho auth; wc_env.sh set cái này
# nhưng cron không source wc_env.sh → tự bổ sung vào env subprocess
_GCP_ENV = {**os.environ,
            "CLOUDSDK_CONFIG": os.environ.get("CLOUDSDK_CONFIG",
                                              "/home/trido/thanhdt/gcloud_dtienthanh"),
            "PATH": os.environ.get("PATH", "") + f":{_GCP_SDK_BIN}"}
EXEC_LOG_DIR = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"
ACCOUNTS = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}

# Thuế TNCN trên cổ tức tiền mặt của CÁ NHÂN cư trú — khấu trừ tại nguồn lúc chi trả.
# TT 111/2013/TT-BTC Đ.10 + Đ.25; Luật TNCN 109/2025/QH15 (hiệu lực 01/07/2026) giữ nguyên 5%.
# Đo được đúng 5,00% trên ca chi trả thật MBB 17/07/2026 (xem docstring TẦNG 4).
# THAM SỐ, không phải hằng số bất biến: tài khoản tổ chức/quỹ có chế độ khác → `--div-tax-rate`.
PIT_DIVIDEND_RATE = 0.05

# Nhiễu làm tròn: `Close` được làm tròn tới 10 VND nên tỉ số dao động ~10/Price.
# Ngưỡng 0,3% đủ rộng để bỏ qua nhiễu, đủ hẹp để bắt cổ tức nhỏ nhất đã gặp (450đ/34.000 = 1,3%).
RATIO_JUMP_MIN = 0.003

# Dư số chấp nhận được của một phương trình broker (VND) — làm tròn số dư + phí lẻ.
EQ_TOL_ABS, EQ_TOL_REL = 10.0, 0.005
# Nghiệm lệch quá ngưỡng này so với ước lượng tỉ số ⇒ nghi phương trình bị nhiễm bởi một sự kiện
# chưa phát hiện rơi cùng delta ⇒ hạ về UNVERIFIED (tầng 1 làm LƯỚI AN TOÀN, không làm nguồn số).
SANITY_REL = 0.01


@dataclass
class Adjustment:
    """Một sự kiện điều chỉnh giá (cổ tức tiền mặt HOẶC chia tách — chưa phân biệt)."""

    ticker: str
    ex_date: str
    last_cum_date: str
    last_cum_price: float
    per_share: float          # sau tầng 1 = ƯỚC LƯỢNG tỉ số; tầng 2 GHI ĐÈ bằng số từ tiền thật
    kind: str = "UNVERIFIED"  # UNVERIFIED | CASH_CONFIRMED | STOCK_SUSPECTED
    note: str = ""
    ratio_per_share: float = 0.0    # TẦNG 1 — giữ lại để chẩn đoán/sanity, KHÔNG vào báo cáo
    source: str = "unresolved"      # unresolved | broker_solved | bq_corp_action
    fin_check: str = "unavailable"  # TẦNG 3: match | mismatch | unavailable
    fin_note: str = ""
    # --- nguồn VENDOR per-event (tav2_bq.corporate_action, thêm 2026-08-13) ---
    vendor_cash: float = 0.0        # DIV.value_per_share (GỘP, đồng/cp) — 0 nếu không có
    vendor_stock: float = 0.0       # tổng ISS.exercise_ratio cùng ex-date — 0 nếu không có
    vendor_check: str = "unavailable"   # match | mismatch | vendor_only | broker_only | unavailable
    vendor_note: str = ""

    @property
    def cash_per_share(self) -> float:
        """Số đồng/cp ĐƯỢC PHÉP cộng vào tỉ suất. 0 nếu chưa xác minh — KHÔNG suy diễn từ tỉ số.

        Mọi consumer làm báo cáo phải đọc trường này, KHÔNG đọc thẳng `per_share`.

        CHỈ `CASH_CONFIRMED` (giải ra từ TIỀN BROKER THẬT) được qua cổng. `CASH_VENDOR` — số lấy
        từ `tav2_bq.corporate_action` khi broker không giải được — CỐ Ý bị chặn ở đây: nguồn vendor
        chưa từng được kiểm chứng độ chính xác/độ trễ so với tiền thật về tài khoản, và §21 nói
        báo cáo gửi nhà đầu tư chỉ nhận số đã đối soát được với sổ broker. Số vendor vẫn hiện ra ở
        `vendor_cash`/`per_share` để người đọc thấy và để quant-skeptic đánh giá — **mở cổng cho
        `CASH_VENDOR` là quyết định CHÍNH SÁCH của user, không phải quyết định kỹ thuật của code
        này** (coding_guidelines §22: tách chính sách khỏi kỹ thuật).
        """
        return self.per_share if self.kind == "CASH_CONFIRMED" else 0.0


@dataclass
class PositionReturn:
    """`dividend_per_share` nhận số **GỘP** (như sổ broker ghi); thuế được trừ ở đây.

    Hai bộ số song song, CỐ Ý không giấu bộ nào:
      * `*_gross` — cổ tức danh nghĩa theo mệnh giá công bố, đối chiếu được với sổ broker.
      * mặc định (`pl_total`, `pct_total_return`) — RÒNG sau thuế = tiền thật về túi ⇒ số công bố.
    """

    ticker: str
    qty: int
    cost_per_share: float
    end_price: float
    dividend_per_share: float          # GỘP (trước thuế)
    adjustments: list = field(default_factory=list)
    tax_rate: float = PIT_DIVIDEND_RATE

    @property
    def cost_total(self) -> float:
        return self.qty * self.cost_per_share

    @property
    def pl_price(self) -> float:
        """Lãi/lỗ do GIÁ (chưa gồm cổ tức) — vẫn là 'lãi/lỗ chưa thực hiện' đúng nghĩa."""
        return self.qty * (self.end_price - self.cost_per_share)

    @property
    def dividend_total_gross(self) -> float:
        return self.qty * self.dividend_per_share

    @property
    def dividend_tax(self) -> float:
        return self.dividend_total_gross * self.tax_rate

    @property
    def dividend_total(self) -> float:
        """RÒNG sau thuế — số được cộng vào tỉ suất công bố."""
        return self.dividend_total_gross - self.dividend_tax

    @property
    def pl_total_gross(self) -> float:
        return self.pl_price + self.dividend_total_gross

    @property
    def pl_total(self) -> float:
        return self.pl_price + self.dividend_total

    @property
    def pct_price_only(self) -> float:
        return self.pl_price / self.cost_total * 100.0

    @property
    def pct_total_return_gross(self) -> float:
        return self.pl_total_gross / self.cost_total * 100.0

    @property
    def pct_total_return(self) -> float:
        return self.pl_total / self.cost_total * 100.0

    @property
    def unverified(self) -> list:
        return [a for a in self.adjustments if a.kind != "CASH_CONFIRMED"]


# `bq query` mặc định CHỈ trả 100 dòng và cắt ÂM THẦM (không lỗi, không cảnh báo). Đã cắn thật
# 2026-08-02: truy vấn batch nhiều mã chỉ nhận về 4 mã đầu bảng chữ cái → bỏ sót ex-date NCT/VCB
# (nav_cum_dividend_selfcheck.py bắt được). Đặt trần rõ ràng + RAISE khi chạm trần.
BQ_MAX_ROWS = 200_000


def _bq(sql: str) -> list:
    """Chạy BQ, trả về list[dict]. Không dùng cache env (§11) — đây là tra cứu lịch sử thuần."""
    out = subprocess.run(
        [_BQ_BIN, "query", "--use_legacy_sql=false", f"--project_id={BQ_PROJECT}",
         f"--max_rows={BQ_MAX_ROWS}", "--format=json", sql],
        capture_output=True, text=True, timeout=300, env=_GCP_ENV,
    )
    if out.returncode != 0:
        # bq in lỗi ra STDOUT (đo thật 2026-08-29: rc=2, stderr rỗng, thông điệp nằm ở stdout);
        # chỉ đọc stderr ⇒ "bq query failed: " rỗng, mù nguyên nhân (§29 coding_guidelines).
        msg = (out.stderr.strip() or out.stdout.strip())[:500]
        raise RuntimeError(f"bq query failed: {msg}")
    body = out.stdout.strip()
    # bq đôi khi in dòng cảnh báo trước JSON
    start = body.find("[")
    rows = json.loads(body[start:]) if start >= 0 else []
    if len(rows) >= BQ_MAX_ROWS:
        raise RuntimeError(f"bq trả về đúng trần {BQ_MAX_ROWS} dòng — gần như chắc chắn bị CẮT, "
                           f"không dùng kết quả có thể thiếu.")
    return rows


def _price_ratio_rows(tickers, start: str, end: str) -> list:
    """Chuỗi (ticker, ngày, Price, Close) cho nhiều mã trong MỘT truy vấn BQ."""
    inlist = ",".join(f"'{t}'" for t in sorted(set(tickers)))
    return _bq(f"""
        SELECT t.ticker AS tk, t.time AS d, t.Price AS price, t.Close AS close
        FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
        WHERE t.ticker IN ({inlist})
          AND t.time BETWEEN DATE_SUB(DATE '{start}', INTERVAL 10 DAY) AND DATE '{end}'
          AND t.Price > 0 AND t.Close > 0
        ORDER BY t.ticker, t.time
    """)


def _scan_jumps(ticker: str, rows: list, start: str) -> list:
    """Cú nhảy tỉ số Close/Price → sự kiện điều chỉnh giá. MỘT bản cài đặt duy nhất cho cả
    đường single-ticker lẫn batch (đừng nhân bản vòng lặp này ra chỗ khác)."""
    events, prev = [], None
    for r in rows:
        d = str(r["d"])[:10]
        price, close = float(r["price"]), float(r["close"])
        ratio = close / price
        if prev is not None:
            pd_, pprice, pratio = prev
            # ex-date phải nằm SAU 'start' (sự kiện trước khi mua vị thế không liên quan)
            if ratio / pratio - 1.0 > RATIO_JUMP_MIN and d > start:
                est = round(pprice * (1.0 - pratio / ratio), 2)
                events.append(Adjustment(
                    ticker=ticker, ex_date=d, last_cum_date=pd_, last_cum_price=pprice,
                    per_share=est, ratio_per_share=est,
                ))
        prev = (d, price, ratio)
    return events


def detect_adjustments(ticker: str, start: str, end: str) -> list:
    """Mọi sự kiện điều chỉnh giá có ex-date trong (start, end]. Mặc định kind=UNVERIFIED."""
    return _scan_jumps(ticker, _price_ratio_rows([ticker], start, end), start)


def detect_adjustments_batch(tickers, start: str, end: str):
    """Như `detect_adjustments` nhưng cho NHIỀU mã trong MỘT truy vấn BQ.

    Trả về `(events_by_ticker, max_date_in_bq)`. `max_date_in_bq` là phiên MỚI NHẤT mà BQ đã
    có dữ liệu — người gọi BẮT BUỘC phải xem nó: cú nhảy tỉ số chỉ lộ ra ĐÚNG Ở phiên ex, nên
    khi BQ chưa có phiên nào sau ngày đang xét thì "không thấy sự kiện" KHÔNG đồng nghĩa với
    "không có sự kiện" (đây chính là tình huống chạy live lúc 19:10 — BQ mới sync tới hôm qua).
    """
    rows = _price_ratio_rows(tickers, start, end)
    by_ticker, max_date = {}, ""
    for r in rows:
        by_ticker.setdefault(r["tk"], []).append(r)
        d = str(r["d"])[:10]
        if d > max_date:
            max_date = d
    return ({tk: _scan_jumps(tk, rs, start) for tk, rs in by_ticker.items()}, max_date)


def _broker_records(kind: str, account_no: str):
    """Duyệt bản ghi dnse_raw theo `kind`, ĐÃ LỌC account (coding_guidelines §12)."""
    for path in sorted(glob.glob(os.path.join(EXEC_LOG_DIR, "dnse_raw_*.jsonl"))):
        for line in open(path):
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("kind") != kind:
                continue
            if str(rec.get("account_no")) != str(account_no):
                continue
            yield rec


# ======================================================================================
# TẦNG 2 · ĐO LƯỜNG — số đồng/cp CHÍNH THỨC, giải ra từ TIỀN BROKER THẬT
# ======================================================================================

def bq_corp_action(ticker: str, ex_date: str, include_announced: bool = False):
    """Nguồn VENDOR per-event: `tav2_bq.corporate_action` — {cash, stock, titles} tại (mã, ex-date).

    Đây là "cột raw per-event" mà `ticker_close_vs_price_dividend_adj.md` (viết 2026-08-02) kết
    luận là KHÔNG tồn tại trên BQ — bảng chỉ được tạo 2026-08-12. Nó giải Bẫy (4): `Close/Price`
    không phân biệt được cổ tức TIỀN MẶT với cổ tức CỔ PHIẾU, còn ở đây `event_code` nói thẳng
    (`DIV` = tiền, `ISS` = cổ phiếu) và `value_per_share` cho luôn đồng/cp.

    Ba cái bẫy của bảng, xử lý ngay tại đây:
      * `event_status` — mặc định chỉ lấy `executed`; loại `not_executed` (đã huỷ) và `announced`
        (mới công bố, chưa chắc xảy ra, ngày có thể đổi). **Mặc định này ĐÚNG cho §21** (đo lợi
        nhuận trên sự kiện ĐÃ XẢY RA) và KHÔNG đổi.
        `include_announced=True` mở thêm `announced` — chỉ dành cho người hỏi "HÔM NAY có gì chốt
        quyền", vì vendor chỉ đổi `announced → executed` trong lần reload rơi vào ~22:2x ICT CỦA
        CHÍNH NGÀY ĐÓ (đo thật 2026-08-13: exright 08-13 là DHN/HGM/SAC/BCF, cả 4 đều
        `announced`; exright 08-11 đã `executed`). Hỏi ngày hôm nay bằng bộ lọc mặc định ⇒ 0 dòng
        MỖI NGÀY. Người gọi bật cờ này PHẢI mang nhãn "dự kiến, chưa xác nhận" theo con số.
        Thêm 2026-08-13 (quant-skeptic REFUTED vòng 1 của `corp_action_daily`); mặc định giữ
        nguyên nên mọi caller cũ không đổi hành vi một chút nào.
      * dòng TRÙNG `(ticker, exright_date, event_code)` — có thể là nhiều đợt THẬT chốt cùng ngày
        (MBB 2026-08-11: quyền mua 10% VÀ cổ tức CP 15%) hoặc bản đính chính của cùng một sự kiện.
        Dedup theo `(event_code, issue_method_name_vi, value_per_share, exercise_ratio)` rồi mới
        SUM: hai đợt khác loại/khác tỉ lệ đều sống, hai dòng y hệt nhau gộp làm một.
      * `category` LUÔN NULL — đừng đọc, dùng `event_code`.

    Trả None khi không có sự kiện nào. KHÔNG ném exception khi BQ lỗi — người gọi vẫn phải chạy
    được đường broker (nguồn chuẩn tắc), bảng này chỉ là lớp bổ sung.
    """
    try:
        rows = _bq(f"""
            SELECT event_code, value_per_share, exercise_ratio,
                   issue_method_name_vi, event_title_vi
            FROM `{BQ_PROJECT}.tav2_bq.corporate_action`
            WHERE ticker = '{ticker}' AND exright_date = DATE '{ex_date}'
              AND event_status IN {"('executed', 'announced')" if include_announced
                                   else "('executed')"}
              AND event_code IN ('DIV', 'ISS')
        """)
    except Exception:
        return None
    if not rows:
        return None

    seen, cash, stock, titles = set(), 0.0, 0.0, []
    for r in rows:
        key = (r["event_code"], r.get("issue_method_name_vi"),
               str(r.get("value_per_share")), str(r.get("exercise_ratio")))
        if key in seen:
            continue
        seen.add(key)
        titles.append((r.get("event_title_vi") or "")[:60])
        if r["event_code"] == "DIV" and r.get("value_per_share") is not None:
            cash += float(r["value_per_share"])
        elif r["event_code"] == "ISS" and r.get("exercise_ratio") is not None:
            stock += float(r["exercise_ratio"])

    return {"cash": cash if cash > 0 else None,
            "stock": stock if stock > 0 else None,
            "titles": "; ".join(titles),
            "n_rows": len(rows), "n_dedup": len(seen)}


def broker_cash_deltas(account_no: str) -> dict:
    """{ngày: tổng delta DƯƠNG của `cashDividendReceiving`} — tiền cổ tức mới được ghi nhận.

    Delta ÂM = khoản phải thu đã chi trả về `totalCash` (không phải sự kiện mới) → bỏ.
    Bỏ bản ghi "khối stock TOÀN SỐ 0" — lỗi API tạm thời đã biết của DNSE (cùng lỗi làm sai NAV
    ZaloPay 27/07); giữ lại sẽ tạo cú sụt rồi bật giả trong chuỗi và hỏng phép lấy delta.
    """
    series = []
    for rec in _broker_records("balances", account_no):
        stock = rec.get("payload", {}).get("stock") or {}
        cd = stock.get("cashDividendReceiving")
        if cd is None:
            continue
        if all((stock.get(k) or 0) == 0 for k in
               ("totalCash", "availableCash", "depositInterest", "cashDividendReceiving")):
            continue
        series.append((rec.get("ts") or "", cd))
    series.sort()
    out = {}
    for (_, prev_cd), (ts, cd) in zip(series, series[1:]):
        if cd > prev_cd:
            out[ts[:10]] = out.get(ts[:10], 0.0) + (cd - prev_cd)
    return out


def broker_qty(account_no: str) -> dict:
    """{(mã, ngày): số lượng cuối ngày} từ bản ghi positions (đã lọc account, §12)."""
    out = {}
    for rec in _broker_records("positions", account_no):
        ts = rec.get("ts") or ""
        for it in rec.get("payload", {}).get("positions", []):
            if str(it.get("accountNo")) != str(account_no):
                continue
            key = (it["symbol"], ts[:10])
            if key not in out or ts >= out[key][0]:
                out[key] = (ts, it.get("openQuantity"))
    return {k: v[1] for k, v in out.items()}


def _qty_at(qmap: dict, adj) -> float:
    """Số lượng hưởng quyền: ưu tiên ngày cuối còn quyền, thiếu thì lấy chính ex-date."""
    q = qmap.get((adj.ticker, adj.last_cum_date))
    if q is None:
        q = qmap.get((adj.ticker, adj.ex_date))
    return float(q or 0.0)


def _connected(equations: list, n: int) -> list:
    """Gom (phương trình, ẩn) thành thành phần liên thông. equations = [(cols, rhs, label)]."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for cols, _, _ in equations:
        for c in cols[1:]:
            ra, rb = find(cols[0]), find(c)
            if ra != rb:
                parent[ra] = rb
    groups = {}
    for eq in equations:
        root = find(eq[0][0])
        eqs, cols = groups.setdefault(root, ([], set()))
        eqs.append(eq)
        cols.update(eq[0])
    return [(eqs, sorted(cols)) for eqs, cols in groups.values()]


def solve_from_broker(adjustments: list, accounts: dict, deltas=None, qtys=None) -> list:
    """Giải `per_share` của từng sự kiện TỪ TIỀN BROKER THẬT.

    Đặt `kind=CASH_CONFIRMED` + `source='broker_solved'` khi giải được; ngược lại giữ
    `kind='UNVERIFIED'` (giá trị `per_share` ước lượng từ tỉ số vẫn nằm đó cho mục đích chẩn đoán,
    nhưng `.cash_per_share` trả 0 nên KHÔNG thể lọt vào báo cáo).

    `deltas`/`qtys` cho phép tiêm dữ liệu giả lập trong selfcheck (chạy offline).
    """
    import numpy as np

    deltas = deltas or {lb: broker_cash_deltas(no) for lb, no in accounts.items()}
    qtys = qtys or {lb: broker_qty(no) for lb, no in accounts.items()}
    for adj in adjustments:
        adj.source = getattr(adj, "source", "unresolved")

    # (a) Nghi CHIA TÁCH/THƯỞNG CP: số lượng đổi ngay tại ex-date → không sinh tiền, loại khỏi hệ.
    live = []
    for adj in adjustments:
        changed = [f"{lb} {qtys[lb][(adj.ticker, adj.last_cum_date)]}→{qtys[lb][(adj.ticker, adj.ex_date)]}"
                   for lb in accounts
                   if (adj.ticker, adj.last_cum_date) in qtys[lb] and (adj.ticker, adj.ex_date) in qtys[lb]
                   and qtys[lb][(adj.ticker, adj.last_cum_date)] != qtys[lb][(adj.ticker, adj.ex_date)]]
        # ⚠️ DƯƠNG TÍNH GIẢ ĐÃ BIẾT: dấu hiệu này KHÔNG phân biệt được "thưởng CP" với "nhà đầu tư
        # vừa mua/bán đúng ngày đó". Một lệnh khớp thật quanh ex-date sẽ nén cổ tức tiền mặt thật
        # xuống 0. Sai theo hướng AN TOÀN (thiếu, không bao giờ thừa) nên giữ nguyên; xem selfcheck
        # mục 13. Muốn tách đúng phải có lịch sử lệnh khớp, không suy được từ số lượng cuối ngày.
        if changed:
            adj.kind = "STOCK_SUSPECTED"
            adj.note = ("số lượng cổ phiếu đổi tại ex-date (" + "; ".join(changed)
                        + ") — nghi chia tách/thưởng, KHÔNG cộng như tiền")
        else:
            live.append(adj)

    # (b) Dựng hệ. DNSE ghi khoản phải thu tối ngày cuối còn quyền, đôi khi trượt sang chính ex-date
    # → cửa sổ 2 ngày. Nhưng khoản đó chỉ được ghi MỘT LẦN, nên mỗi sự kiện chỉ được gán vào ĐÚNG
    # MỘT ngày trong cửa sổ (ngày SỚM NHẤT có delta dương), nếu không nó sẽ bị đếm ở cả hai.
    # Bẫy thật: ex-date của NCT (27/07) trùng ngày-cuối-còn-quyền của SAB (27/07) — để cửa sổ rộng
    # thì NCT bị cộng vào cả delta 24/07 lẫn 3.300.000 của 27/07, hệ mâu thuẫn, cả hai mã hỏng.
    equations = []
    for lb in accounts:
        by_day = {}
        for i, adj in enumerate(live):
            if _qty_at(qtys[lb], adj) <= 0:
                continue
            for day in (adj.last_cum_date, adj.ex_date):
                if deltas[lb].get(day, 0) > 0:
                    by_day.setdefault(day, []).append(i)
                    break
        for day, cols in sorted(by_day.items()):
            equations.append((cols, float(deltas[lb][day]), (lb, day)))

    # (c) Giải từng thành phần liên thông độc lập.
    for eqs, cols in _connected(equations, len(live)):
        pos = {c: j for j, c in enumerate(cols)}
        A = np.zeros((len(eqs), len(cols)))
        b = np.zeros(len(eqs))
        for i, (ecols, rhs, (lb, _)) in enumerate(eqs):
            b[i] = rhs
            for c in ecols:
                A[i, pos[c]] = _qty_at(qtys[lb], live[c])

        names = ", ".join(f"{live[c].ticker}@{live[c].ex_date}" for c in cols)
        shape = f"{len(eqs)} phương trình / {len(cols)} ẩn: {names}"
        if np.linalg.matrix_rank(A) < len(cols):
            for c in cols:
                live[c].note = (f"hệ VÔ ĐỊNH ({shape}) — nhiều mã cùng ngày chốt quyền mà không đủ "
                                "tài khoản có tỉ lệ nắm giữ khác nhau để tách")
            continue

        x = np.round(np.linalg.lstsq(A, b, rcond=None)[0])
        resid = A @ x - b
        bad = [f"{lb} {d}" for i, (_, _, (lb, d)) in enumerate(eqs)
               if abs(resid[i]) > max(EQ_TOL_ABS, EQ_TOL_REL * abs(b[i]))]
        if bad:
            for c in cols:
                live[c].note = ("nghiệm KHÔNG khớp tiền broker tại " + ", ".join(bad)
                                + " — có thể còn mã khác cùng ngày chưa phát hiện")
            continue

        for c in cols:
            adj, val = live[c], float(x[pos[c]])
            ref = float(getattr(adj, "ratio_per_share", adj.per_share) or 0.0)
            if val <= 0 or (ref > 0 and abs(val - ref) > SANITY_REL * ref):
                adj.note = (f"nghiệm broker {val:,.0f}đ/cp LỆCH XA ước lượng tỉ số {ref:,.0f}đ/cp — "
                            "nghi phương trình bị nhiễm bởi sự kiện chưa phát hiện")
                continue
            adj.per_share, adj.kind, adj.source = val, "CASH_CONFIRMED", "broker_solved"
            adj.note = f"giải từ tiền mặt broker thật ({shape})"

    for adj in adjustments:
        if adj.kind == "UNVERIFIED" and not adj.note:
            adj.note = ("không có bản ghi broker khớp — chưa nắm giữ tại ngày chốt quyền, "
                        "hoặc log không phủ ngày đó")
    return adjustments


# ======================================================================================
# TẦNG 3 · ĐỐI SOÁT CHẬM — xác nhận độc lập, KHÔNG BAO GIỜ ghi đè số của tầng 2
# ======================================================================================

def crosscheck_dividend_1y(adjustments: list) -> list:
    """Đối soát với delta `Dividend_1Y` giữa hai kỳ báo cáo quý liên tiếp.

    ĐỘ TRỄ LÀ BẢN CHẤT: `Dividend_1Y` chỉ đổi khi có báo cáo quý mới, nên sự kiện xảy ra SAU kỳ gần
    nhất chưa xuất hiện (SAB ex-date 28/07 > kỳ 23/07 → `unavailable`). Nó còn là tổng TRAILING nên
    delta có thể ÂM khi một cổ tức cũ rơi khỏi cửa sổ 1 năm. Vì vậy tầng này CHỈ xác nhận thêm,
    KHÔNG BAO GIỜ ghi đè số của tầng 2.
    """
    for adj in adjustments:
        rows = _bq(f"""
            SELECT t.time AS d, t.Dividend_1Y AS d1y
            FROM `{BQ_PROJECT}.tav2_bq.ticker_financial` AS t
            WHERE t.ticker = '{adj.ticker}' AND t.Dividend_1Y IS NOT NULL
              AND t.time >= DATE_SUB(DATE '{adj.ex_date}', INTERVAL 400 DAY)
            ORDER BY t.time
        """)
        after = [i for i, r in enumerate(rows) if str(r["d"])[:10] > adj.ex_date]
        if not after or after[0] == 0:
            adj.fin_check, adj.fin_note = "unavailable", (
                "chưa có kỳ báo cáo quý nào sau ex-date (độ trễ theo quý) — KHÔNG kết luận gì")
            continue
        i = after[0]
        # bq --format=json trả MỌI giá trị dưới dạng STRING — phải ép kiểu trước khi định dạng số.
        prev_d1y, cur_d1y = float(rows[i - 1]["d1y"]), float(rows[i]["d1y"])
        delta = cur_d1y - prev_d1y
        ref = float(adj.per_share or 0.0)
        span = f"Dividend_1Y {prev_d1y:,.0f}→{cur_d1y:,.0f} (delta {delta:+,.0f})"
        if ref > 0 and abs(delta - ref) <= max(1.0, 0.01 * ref):
            adj.fin_check, adj.fin_note = "match", span
        else:
            adj.fin_check, adj.fin_note = "mismatch", (
                f"{span} ≠ {ref:,.0f} — là tổng TRAILING, một cổ tức cũ có thể vừa rơi khỏi cửa sổ "
                "1 năm; KHÔNG dùng để bác số tầng 2")
    return adjustments


# ======================================================================================
# API cho báo cáo
# ======================================================================================

def resolve_dividends(tickers, start: str, end: str, accounts: dict = None,
                      with_crosscheck: bool = True) -> list:
    """Chạy đủ 3 tầng cho một RỔ mã. LÀM BÁO CÁO PHẢI DÙNG BẢN NÀY — giải cả rổ mới đủ phương trình
    để tách những ngày nhiều mã cùng chốt quyền."""
    accounts = ACCOUNTS if accounts is None else accounts
    adjs = []
    for tk in tickers:
        adjs.extend(detect_adjustments(tk, start, end))

    # TIỀN BROKER THẬT VẪN LÀ NGUỒN SỐ (tầng 2). Bảng vendor `corporate_action` chạy SAU, làm 3
    # việc khác nhau — cố ý KHÔNG cho nó ghi đè một nghiệm đã giải ra từ tiền thật:
    #   1. PHÂN LOẠI sự kiện (DIV/ISS) — thay cho phép suy yếu từ biến động `openQuantity`, vốn
    #      vừa bỏ sót thưởng CP vừa dương tính giả khi có lệnh khớp trùng cửa sổ ex-date (Bẫy 4).
    #   2. ĐỐI SOÁT CHÉO nghiệm broker — hai nguồn độc lập lệch nhau là tín hiệu phải điều tra.
    #   3. LẤP chỗ broker không giải được (hệ vô định / ngoài cửa sổ dnse_raw từ 06/07/2026),
    #      nhưng gắn nhãn RIÊNG `CASH_VENDOR` — xem `cash_per_share`: KHÔNG tự động vào báo cáo.
    todo = [a for a in adjs if a.source == "unresolved"]
    if todo:
        solve_from_broker(todo, accounts)

    for adj in adjs:
        row = bq_corp_action(adj.ticker, adj.ex_date)
        if not row:
            adj.vendor_check = "unavailable"
            adj.vendor_note = "không có sự kiện executed nào ở (mã, ex-date) trong corporate_action"
            continue
        adj.vendor_cash = float(row.get("cash") or 0.0)
        adj.vendor_stock = float(row.get("stock") or 0.0)
        adj.vendor_note = row.get("titles", "")

        if adj.kind == "CASH_CONFIRMED":
            # broker đã cho số chính thức — vendor chỉ được phép XÁC NHẬN hoặc BÁO ĐỘNG
            if adj.vendor_cash <= 0:
                adj.vendor_check = "broker_only"
            elif abs(adj.vendor_cash - adj.per_share) <= max(1.0, 0.01 * adj.per_share):
                adj.vendor_check = "match"
            else:
                adj.vendor_check = "mismatch"
                adj.vendor_note = (f"vendor {adj.vendor_cash:,.0f}đ/cp ≠ tiền broker "
                                   f"{adj.per_share:,.0f}đ/cp — ĐIỀU TRA trước khi dùng số nào")
        elif adj.vendor_cash > 0 and adj.vendor_stock <= 0:
            # thuần tiền mặt theo vendor, broker chưa giải được ⇒ có SỐ nhưng chưa có BẰNG CHỨNG TIỀN
            adj.per_share, adj.source, adj.kind = adj.vendor_cash, "bq_corp_action", "CASH_VENDOR"
            adj.vendor_check = "vendor_only"
        elif adj.vendor_stock > 0:
            # phân loại chắc chắn: có phát hành CP ⇒ không được cộng như tiền mặt
            adj.kind = "STOCK_CONFIRMED"
            adj.vendor_check = "vendor_only"
            adj.note = (f"corporate_action: ISS tỉ lệ {adj.vendor_stock:.4f}"
                        + (f" + DIV {adj.vendor_cash:,.0f}đ/cp" if adj.vendor_cash > 0 else ""))

    if with_crosscheck:
        crosscheck_dividend_1y(adjs)
    return adjs


def position_total_return(ticker, qty, cost_per_share, start, end, end_price=None,
                          account_no=None, tax_rate: float = PIT_DIVIDEND_RATE) -> PositionReturn:
    """Tỉ suất TỔNG (giá + cổ tức tiền mặt) của một vị thế giữ từ `start` tới `end`.

    `start` = ngày mua (chỉ tính cổ tức có ex-date SAU ngày này).
    `end_price` bỏ trống → tự lấy `Price` (thô) phiên `end`.
    `account_no` có truyền → GIẢI cổ tức từ tiền mặt broker của CHÍNH tài khoản đó.

    ⚠️ Đường một-mã/một-tài-khoản này chỉ giải được khi delta của ngày chốt quyền CHỈ chứa mã này.
    Nhiều mã cùng ngày → dư số không khớp → giữ UNVERIFIED (fail-closed, không ra số sai). Làm báo
    cáo thì gọi `resolve_dividends()` cho CẢ RỔ để đủ phương trình mà tách.
    """
    if end_price is None:
        rows = _bq(f"""SELECT t.Price AS price FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
                       WHERE t.ticker='{ticker}' AND t.time = DATE '{end}'""")
        if not rows:
            raise RuntimeError(f"{ticker}: không có giá phiên {end} trong tav2_bq.ticker")
        end_price = float(rows[0]["price"])

    adjs = detect_adjustments(ticker, start, end)
    if account_no:
        label = next((lb for lb, no in ACCOUNTS.items() if no == str(account_no)), str(account_no))
        solve_from_broker(adjs, {label: str(account_no)})
    # CHỈ số đã xác minh mới được cộng — `cash_per_share` trả 0 cho UNVERIFIED/STOCK_SUSPECTED.
    div = sum(a.cash_per_share for a in adjs)
    return PositionReturn(ticker, qty, float(cost_per_share), float(end_price), div, adjs,
                          tax_rate=tax_rate)


# --------------------------------------------------------------------------------------
# Selfcheck — số liệu thật đã đối soát ba chiều (BQ ↔ cashDividendReceiving ↔ costPrice broker)
# trong `mike/agents/Taylor/research/dividend_adjusted_returns_20260802.md`.
# --------------------------------------------------------------------------------------
_SELFCHECK_CASES = [
    # ticker, last_cum_price, last_cum_ratio, ex_ratio, expected div/share
    ("MBB", 26000.0, 25000.0 / 26000.0, 1.0, 1000.0),
    ("BID", 39300.0, 0.9885496183206107, 1.0, 450.0),
    ("CTG", 29700.0, 29250.0 / 29700.0, 1.0, 450.0),
    ("NCT", 92800.0, 84800.0 / 92800.0, 1.0, 8000.0),
    ("SAB", 46600.0, 43600.0 / 46600.0, 1.0, 3000.0),
]

# Fixture TẦNG 2 — chạy OFFLINE (không cần BQ, không cần log broker) để selfcheck không phụ thuộc
# môi trường. Số liệu dưới đây là SỐ THẬT trích từ dnse_raw_*.jsonl
# (xem `mike/agents/Taylor/exp_div_broker_solve/reconcile_july.txt`).
_QTY = {
    "SpaceX": {("CTG", "2026-07-22"): 2300, ("VCB", "2026-07-22"): 1300,
               ("NCT", "2026-07-24"): 500, ("SAB", "2026-07-27"): 1100,
               ("MBB", "2026-07-08"): 2400, ("BID", "2026-07-16"): 1900},
    "ZaloPay": {("CTG", "2026-07-22"): 1050, ("VCB", "2026-07-22"): 800,
                ("NCT", "2026-07-24"): 373, ("SAB", "2026-07-27"): 744,
                ("BID", "2026-07-16"): 900},
}
_DELTA = {
    "SpaceX": {"2026-07-09": 2_400_000.0, "2026-07-16": 855_000.0, "2026-07-22": 1_620_000.0,
               "2026-07-24": 4_000_000.0, "2026-07-27": 3_300_000.0},
    "ZaloPay": {"2026-07-16": 405_000.0, "2026-07-22": 832_500.0,
                "2026-07-24": 2_984_000.0, "2026-07-28": 2_232_000.0},
}
_EVENTS = [  # ticker, ex_date, last_cum_date, giá cuối còn quyền, ước lượng tỉ số
    ("MBB", "2026-07-09", "2026-07-08", 26000.0, 1000.0),
    ("BID", "2026-07-17", "2026-07-16", 39300.0, 450.0),
    ("CTG", "2026-07-23", "2026-07-22", 29700.0, 450.0),
    ("VCB", "2026-07-23", "2026-07-22", 54500.0, 450.0),
    ("NCT", "2026-07-27", "2026-07-24", 92800.0, 8000.0),
    ("SAB", "2026-07-28", "2026-07-27", 46600.0, 3000.0),
]


def _mk(tk, ex, cum, price, ratio_ps):
    return Adjustment(ticker=tk, ex_date=ex, last_cum_date=cum, last_cum_price=price,
                      per_share=ratio_ps, ratio_per_share=ratio_ps)


def _solve_offline(adjs, accounts, qty=None, delta=None):
    return solve_from_broker(
        adjs, accounts,
        deltas={lb: (delta or _DELTA).get(lb, {}) for lb in accounts},
        qtys={lb: (qty or _QTY).get(lb, {}) for lb in accounts})


def _selfcheck() -> int:
    passed = failed = 0

    def check(name, got, want, tol=0.51):
        nonlocal passed, failed
        ok = abs(got - want) <= tol
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got:,.2f} want={want:,.2f}")
        passed, failed = passed + ok, failed + (not ok)

    print("1) Công thức nhân (KHÔNG phải hiệu số) suy đúng cổ tức/cp:")
    for tk, p, r0, r1, want in _SELFCHECK_CASES:
        check(f"{tk} div/share", p * (1.0 - r0 / r1), want)

    print("2) Hiệu số Close−Price KHÔNG bằng cổ tức (chứng minh vì sao phải dùng tỉ số):")
    # SAB phiên 24/07: Price 46.500, Close 43.510 → hiệu 2.990 ≠ cổ tức thật 3.000
    check("SAB hiệu số tại 24/07 lệch so với 3.000", 46500.0 - 43510.0, 2990.0, tol=0.5)

    print("3) Tỉ suất tổng của vị thế (số thật SpaceX 31/07) — ba mức: giá / gộp / ròng sau thuế:")
    for tk, qty, cost, px, div, want_px, want_gross, want_net in [
        ("NCT", 500, 94360, 83400, 8000, -11.61, -3.14, -3.56),
        ("SAB", 1100, 47368, 43550, 3000, -8.06, -1.73, -2.04),
        ("MBB", 2400, 25850, 22500, 1000, -12.96, -9.09, -9.28),
    ]:
        pr = PositionReturn(tk, qty, cost, px, div)
        check(f"{tk} % chỉ-giá", pr.pct_price_only, want_px, tol=0.01)
        check(f"{tk} % tổng GỘP", pr.pct_total_return_gross, want_gross, tol=0.01)
        check(f"{tk} % tổng RÒNG (sau thuế 5%)", pr.pct_total_return, want_net, tol=0.01)

    print("4) Tổng danh mục SpaceX 31/07 (giá vốn 986.725.443):")
    check("lãi/lỗ gồm cổ tức GỘP", -62_610_443 + 12_175_000, -50_435_443, tol=1)
    check("% tổng GỘP", (-62_610_443 + 12_175_000) / 986_725_443 * 100, -5.11, tol=0.01)
    check("thuế TNCN 5% trên 12.175.000", 12_175_000 * PIT_DIVIDEND_RATE, 608_750, tol=1)
    check("lãi/lỗ gồm cổ tức RÒNG", -62_610_443 + 12_175_000 * 0.95, -51_044_193, tol=1)
    check("% tổng RÒNG", (-62_610_443 + 12_175_000 * 0.95) / 986_725_443 * 100, -5.17, tol=0.01)

    print("5) Vị thế KHÔNG có cổ tức thì hai con số phải trùng khít:")
    pr = PositionReturn("PVT", 3500, 17100, 18300, 0)
    check("PVT % chỉ-giá == % tổng", pr.pct_total_return - pr.pct_price_only, 0.0, tol=1e-9)

    print("6) Cờ chưa-xác-minh phải nổi khi thiếu đối soát broker:")
    pr = PositionReturn("XXX", 100, 10000, 9000, 500,
                        [Adjustment("XXX", "2026-07-01", "2026-06-30", 10000, 500)])
    check("số sự kiện UNVERIFIED", len(pr.unverified), 1, tol=0)

    def same(name, got, want):
        nonlocal passed, failed
        ok = got == want
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got!r} want={want!r}")
        passed, failed = passed + ok, failed + (not ok)

    print("7) TẦNG 2 giải ĐÚNG cả 6 sự kiện tháng 7 từ TIỀN BROKER THẬT (không dùng tỉ số):")
    adjs = [_mk(*e) for e in _EVENTS]
    _solve_offline(adjs, ACCOUNTS)
    for a, (tk, _, _, _, want) in zip(adjs, _EVENTS):
        check(f"{tk} per_share", a.per_share, want)
        same(f"{tk} kind/source", (a.kind, a.source), ("CASH_CONFIRMED", "broker_solved"))

    print("8) Ngày 23/07 CTG+VCB trùng ex-date: chỉ tách được nhờ hệ 2 tài khoản (2pt/2ẩn):")
    two = [_mk(*e) for e in _EVENTS if e[0] in ("CTG", "VCB")]
    _solve_offline(two, ACCOUNTS)
    check("CTG", two[0].per_share, 450.0)
    check("VCB", two[1].per_share, 450.0)
    print("     kiểm tra ngược: 2300·450+1300·450 và 1050·450+800·450 phải khớp delta thật")
    check("SpaceX 22/07", 2300 * 450 + 1300 * 450, 1_620_000, tol=1)
    check("ZaloPay 22/07", 1050 * 450 + 800 * 450, 832_500, tol=1)

    print("9) HỆ VÔ ĐỊNH (1 tài khoản, 2 ẩn) ⇒ giữ UNVERIFIED, KHÔNG lấp bằng ước lượng tỉ số:")
    two2 = [_mk(*e) for e in _EVENTS if e[0] in ("CTG", "VCB")]
    _solve_offline(two2, {"SpaceX": ACCOUNTS["SpaceX"]})
    same("CTG kind", two2[0].kind, "UNVERIFIED")
    check("CTG cash_per_share (không được lọt vào báo cáo)", two2[0].cash_per_share, 0.0, tol=1e-9)
    print(f"     lý do ghi lại: {two2[0].note[:70]}…")

    print("10) Ước lượng tỉ số SAI ⇒ hạ về UNVERIFIED (tầng 1 là lưới an toàn, không phải nguồn số):")
    bad = _mk("NCT", "2026-07-27", "2026-07-24", 92800.0, 5000.0)   # tỉ số lệch 60%
    _solve_offline([bad], ACCOUNTS)
    same("NCT kind khi tỉ số lệch xa", bad.kind, "UNVERIFIED")
    check("NCT cash_per_share", bad.cash_per_share, 0.0, tol=1e-9)

    print("11) Số lượng cổ phiếu đổi tại ex-date ⇒ STOCK_SUSPECTED, KHÔNG cộng như tiền:")
    xxx = _mk("XXX", "2026-07-23", "2026-07-22", 10000.0, 500.0)
    _solve_offline([xxx], {"SpaceX": ACCOUNTS["SpaceX"]},
                   qty={"SpaceX": {("XXX", "2026-07-22"): 1000, ("XXX", "2026-07-23"): 1150}},
                   delta={"SpaceX": {"2026-07-22": 500_000.0}})
    same("XXX kind", xxx.kind, "STOCK_SUSPECTED")
    check("XXX cash_per_share", xxx.cash_per_share, 0.0, tol=1e-9)

    print("12) Delta ÂM (chi trả khoản phải thu) KHÔNG được coi là sự kiện mới:")
    # SpaceX 17/07 có delta −2.400.000 (trả cổ tức MBB) — nếu bị tính, BID sẽ sai.
    bid = _mk("BID", "2026-07-17", "2026-07-16", 39300.0, 450.0)
    _solve_offline([bid], ACCOUNTS)
    check("BID per_share vẫn đúng 450 (delta âm 17/07 đã bị loại)", bid.per_share, 450.0)

    print("13) DƯƠNG TÍNH GIẢ đã biết: MUA/BÁN THẬT đúng cửa sổ ex-date cũng làm đổi openQuantity")
    # quant-skeptic 2026-08-02: dấu hiệu `openQuantity` đổi KHÔNG phân biệt được "thưởng CP" với
    # "nhà đầu tư vừa khớp lệnh". Kết quả là NÉN cổ tức tiền mặt thật xuống 0 — sai theo hướng AN
    # TOÀN (thiếu, không bao giờ thừa), nhưng phải có test ghim lại để không ai tưởng là bug mới.
    traded = _mk("CTG", "2026-07-23", "2026-07-22", 29700.0, 450.0)
    _solve_offline([traded], {"SpaceX": ACCOUNTS["SpaceX"]},
                   qty={"SpaceX": {("CTG", "2026-07-22"): 2300, ("CTG", "2026-07-23"): 2800}},
                   delta={"SpaceX": {"2026-07-22": 1_035_000.0}})
    same("CTG bị gắn nhầm STOCK_SUSPECTED khi vừa mua thêm", traded.kind, "STOCK_SUSPECTED")
    check("→ cash_per_share = 0 (fail-closed: THIẾU cổ tức, không bao giờ THỪA)",
          traded.cash_per_share, 0.0, tol=1e-9)

    print("14) Tổng cộng lại phải khớp tiền cổ tức thật từng tài khoản (GỘP, như sổ broker ghi):")
    check("SpaceX tổng", 2400 * 1000 + 1900 * 450 + 2300 * 450 + 1300 * 450 + 500 * 8000 + 1100 * 3000,
          12_175_000, tol=1)
    check("ZaloPay tổng (không có MBB — mua sau ex-date 09/07)",
          900 * 450 + 1050 * 450 + 800 * 450 + 373 * 8000 + 744 * 3000, 6_453_500, tol=1)
    check("SpaceX RÒNG sau thuế 5%", 12_175_000 * (1 - PIT_DIVIDEND_RATE), 11_566_250, tol=1)
    check("ZaloPay RÒNG sau thuế 5%", 6_453_500 * (1 - PIT_DIVIDEND_RATE), 6_130_825, tol=1)

    print("15) GHIM BẰNG CHỨNG THỰC NGHIỆM: ca chi trả THẬT duy nhất (MBB, SpaceX, 17/07/2026)")
    print("    — đây là thứ chứng minh `cashDividendReceiving` là GỘP và thuế trừ lúc CHI TRẢ.")
    # Số thật đọc từ data/execution_logs/dnse_raw_2026-07-1{6,7}.jsonl (đã lọc account §12).
    aC16, cd16, di16, tc16 = 302_111_136, 3_255_000, 22_501, 305_388_637
    aC17, cd17, di17, tc17 = 2_282_925, 855_000, 22_538, 3_160_463
    withdrawn = 302_108_211        # Trứng vàng, xác nhận bởi nav_snapshot_SpaceX_2026-07-17.json
    check("hằng đẳng thức totalCash 16/07", aC16 + cd16 + di16, tc16, tol=0)
    check("hằng đẳng thức totalCash 17/07", aC17 + cd17 + di17, tc17, tol=0)
    check("khoản phải thu xoá = GỘP 2400cp×1.000đ", cd16 - cd17, 2_400_000, tol=0)
    cash_in = (aC17 - aC16) + withdrawn
    check("tiền THẬT vào availableCash", cash_in, 2_280_000, tol=0)
    check("thuế suy ra từ tiền thật (%)", (1 - cash_in / (cd16 - cd17)) * 100, 5.00, tol=0.001)
    same("khớp đúng hằng số PIT_DIVIDEND_RATE", round(1 - cash_in / (cd16 - cd17), 6),
         round(PIT_DIVIDEND_RATE, 6))
    check("rút Trứng vàng == withdrawableCash 16/07 (không phải số ép cho khớp)",
          withdrawn, 302_108_211, tol=0)

    print(f"\n=== SELFCHECK: {passed} PASS / {failed} FAIL ===")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resolve", help="GIẢI CẢ RỔ (danh sách mã, phân tách bằng dấu phẩy) — bản "
                                      "dùng khi làm báo cáo")
    ap.add_argument("--ticker")
    ap.add_argument("--qty", type=int, default=1)
    ap.add_argument("--cost", type=float, help="giá vốn THÔ/cp (giá khớp thật đã trả)")
    ap.add_argument("--from", dest="start", help="ngày mua / đầu kỳ YYYY-MM-DD")
    ap.add_argument("--to", dest="end", help="cuối kỳ YYYY-MM-DD")
    ap.add_argument("--end-price", type=float, help="ghi đè giá cuối kỳ (mặc định lấy Price thô từ BQ)")
    ap.add_argument("--account-no", help="số tài khoản DNSE để xác minh cổ tức với broker")
    ap.add_argument("--account", help="nhãn tài khoản (SpaceX/ZaloPay) — tự tra số hiệu")
    ap.add_argument("--div-tax-rate", type=float, default=PIT_DIVIDEND_RATE,
                    help="thuế TNCN cổ tức tiền mặt (mặc định 0.05 = 5%% cho tài khoản CÁ NHÂN; "
                         "đặt 0 để xem số gộp, hoặc mức khác cho tài khoản tổ chức/quỹ)")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()

    if a.selfcheck:
        return _selfcheck()

    if a.resolve:
        if not (a.start and a.end):
            ap.error("--resolve cần thêm --from --to")
        adjs = resolve_dividends([t.strip().upper() for t in a.resolve.split(",")], a.start, a.end)
        print(f"Sự kiện {a.start} → {a.end} (giải từ tiền broker: {', '.join(ACCOUNTS)}):\n")
        rate = a.div_tax_rate
        print(f"  (thuế TNCN cổ tức {rate * 100:g}% — GỘP = sổ broker, RÒNG = tiền về túi)\n")
        for x in sorted(adjs, key=lambda z: (z.ex_date, z.ticker)):
            ps = (f"{x.per_share:,.0f} → {x.per_share * (1 - rate):,.1f}đ/cp"
                  if x.kind == "CASH_CONFIRMED" else "— (chưa xác minh)")
            print(f"  {x.ticker:5s} ex {x.ex_date}  {ps:>26s}  [{x.kind}/{x.source}]")
            print(f"        ước lượng tỉ số (chỉ để đối chiếu): {x.ratio_per_share:,.0f}đ/cp")
            print(f"        {x.note}")
            print(f"        Dividend_1Y: {x.fin_check} — {x.fin_note}")
        bad = [x for x in adjs if x.kind == "UNVERIFIED"]
        if bad:
            print(f"\n  ⚠️ {len(bad)} sự kiện CHƯA XÁC MINH — CẤM đưa vào báo cáo gửi nhà đầu tư.")
        return 0

    if not (a.ticker and a.cost and a.start and a.end):
        ap.error("cần --ticker --cost --from --to (hoặc --resolve, hoặc --selfcheck)")

    acc = a.account_no or ACCOUNTS.get(a.account or "")
    pr = position_total_return(a.ticker, a.qty, a.cost, a.start, a.end, a.end_price, acc,
                               tax_rate=a.div_tax_rate)

    print(f"{pr.ticker}  {pr.qty:,}cp · giá vốn {pr.cost_per_share:,.0f} · giá {a.end} {pr.end_price:,.0f}")
    for adj in pr.adjustments:
        print(f"  · ex-date {adj.ex_date}: {adj.per_share:,.0f}đ/cp  [{adj.kind}] {adj.note}")
    if not pr.adjustments:
        print("  · không có sự kiện điều chỉnh giá trong kỳ")
    print(f"  Lãi/lỗ do GIÁ        : {pr.pl_price:>15,.0f}  ({pr.pct_price_only:+.2f}%)")
    print(f"  Cổ tức GỘP           : {pr.dividend_total_gross:>15,.0f}  "
          f"({pr.dividend_per_share:,.0f}đ/cp danh nghĩa)")
    print(f"  − thuế TNCN {pr.tax_rate * 100:g}%      : {-pr.dividend_tax:>15,.0f}  "
          f"(khấu trừ tại nguồn lúc chi trả)")
    print(f"  = Cổ tức RÒNG        : {pr.dividend_total:>15,.0f}  "
          f"({pr.dividend_per_share * (1 - pr.tax_rate):,.1f}đ/cp thực nhận)")
    print(f"  Tổng (gộp, tham chiếu): {pr.pl_total_gross:>14,.0f}  ({pr.pct_total_return_gross:+.2f}%)")
    print(f"  TỔNG RÒNG (dùng báo cáo): {pr.pl_total:>12,.0f}  ({pr.pct_total_return:+.2f}%)")
    if pr.unverified:
        print("\n  ⚠️ CÓ SỰ KIỆN CHƯA XÁC MINH VỚI BROKER — không đưa số này vào báo cáo gửi nhà đầu tư"
              " trước khi đối soát cashDividendReceiving / số lượng cổ phiếu.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
