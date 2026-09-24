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
# Ngưỡng coi hai nguồn ĐỘC LẬP (tiền broker thật vs `tav2_bq.corporate_action`) là LỆCH.
# Giữ nguyên giá trị đã chạy từ 2026-08-13 (1% tương đối, sàn 1đ/cp). ĐÃ ĐO trước khi chốt, trên
# 39 mã hai tài khoản từng nắm giữ, cửa sổ 2026-03-24→09-24: 62 sự kiện, trong đó 6 sự kiện đủ
# điều kiện đối soát (CASH_CONFIRMED + vendor có số tiền) và CẢ 6 khớp ĐÚNG TỪNG ĐỒNG (MBB 09/07
# 1.000 · CTG+VCB 23/07 450 · NCT 27/07 8.000 · SAB 28/07 3.000 · DGC 14/09 8.000) ⇒ **0 ca
# mismatch**, 0 cảnh báo nhiễu. Vì cổng này chưa từng kêu một lần nào nên KHÔNG có cơ sở để nới —
# nới bây giờ là nới mù. Số đo tái lập bằng `agents/Taylor/exp_vendor_mismatch/measure_k1.py`.
VENDOR_MISMATCH_REL, VENDOR_MISMATCH_ABS = 0.01, 1.0


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
    vendor_check: str = "unavailable"   # match | mismatch | vendor_only | broker_only |
                                        # unavailable | lookup_failed
    # unavailable    = vendor XÁC NHẬN 0 dòng ở (mã, ex-date) — truy vấn CHẠY THÀNH CÔNG.
    # lookup_failed  = KHÔNG tra được vendor (BQ lỗi mạng/auth/quota) — KHÔNG được suy ra "vendor
    #                  không có sự kiện" từ đây (vá 2026-09-24, §28/§29 — hai trạng thái khác nhau
    #                  không được gộp một nhãn). Xem `bq_corp_action`/`resolve_dividends`.
    vendor_note: str = ""
    # KHI `vendor_check == "mismatch"`: mã lý do đã CHUẨN HOÁ để tầng ngoài rẽ nhánh thông điệp
    # theo bằng chứng thay vì đoán (§28 — so giá trị, không so câu văn xuôi; §29).
    #   cash_mismatch     = hai nguồn CÙNG khai chân tiền nhưng SỐ lệch quá ngưỡng
    #   stock_leg_ignored = vendor khai THUẦN CỔ PHIẾU, solver lại giải ra tiền mà không biết
    #                       chân cổ phiếu (share_multiplier = 1,0)
    vendor_mismatch_reason: str = ""
    # hệ số tăng KL của chân CỔ PHIẾU cùng ex-date (1,0 = không có chân cổ phiếu). Đặt bởi
    # `solve_from_broker` khi `credit_frame` chứng minh được bằng KL.
    share_multiplier: float = 1.0

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

    Trả None khi vendor XÁC NHẬN không có sự kiện nào ở (mã, ex-date) — 0 dòng, truy vấn CHẠY
    THÀNH CÔNG. NÉM LẠI exception của `_bq()` khi tự BQ không tra được (mạng/auth/quota lỗi) —
    KHÔNG còn nuốt exception ở đây (vá 2026-09-24, arch-review: nuốt lỗi làm "vendor không có
    sự kiện" và "không tra được vendor" trộn chung một nhãn `unavailable`, khiến CẢ HAI lá chắn
    vendor-mismatch ở `resolve_dividends` — D1 stock_leg_ignored + cash_mismatch — TẮT IM LẶNG mỗi
    khi BQ hỏng, quay lại đúng hành vi trước khi có chính sách 2026-09-24). Người gọi
    (`resolve_dividends`) là nơi PHẢI bắt exception này và quyết định chính sách fail-closed —
    hàm ở đây chỉ có nhiệm vụ KHÔNG che giấu sự khác biệt giữa hai trường hợp.
    """
    rows = _bq(f"""
        SELECT event_code, value_per_share, exercise_ratio,
               issue_method_name_vi, event_title_vi
        FROM `{BQ_PROJECT}.tav2_bq.corporate_action`
        WHERE ticker = '{ticker}' AND exright_date = DATE '{ex_date}'
          AND event_status IN {"('executed', 'announced')" if include_announced
                               else "('executed')"}
          AND event_code IN ('DIV', 'ISS')
    """)
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
    """{(mã, ngày): TỔNG KL các lô cùng mã trong bản ghi CUỐI NGÀY} (đã lọc account, §12).

    Bug đã sửa 2026-09-24 (đo thật, xem `_selfcheck` mục 25): bản cũ khoá theo `(symbol, ngày)`
    rồi OVERWRITE — nhiều lô cùng mã trong CÙNG một bản ghi (gói vay margin khác nhau,
    `loanPackageId` khác nhau) chỉ lô đứng CUỐI mảng `positions[]` sống sót, các lô trước bị
    ghi đè vì so `ts >= ts` của chính bản ghi đó luôn đúng. Đo trên dữ liệu thật ZaloPay:
    135 cặp (mã, ngày) lệch (BID/MBB/VCB, đều có ≥2 gói vay), lệch 25,0%–66,7% — ca cụ thể BID
    14/08 báo 320 (chỉ lô `loanPackageId=1258`) trong khi tổng thật 2 lô là 427
    (107 `loanPackageId=1826` + 320 `loanPackageId=1258`). SpaceX cùng kỳ 0 cặp lệch (không có
    mã nào tách ≥2 gói vay) — bug LATENT ở đó, không phải không tồn tại.

    Cùng quy ước GỘP LÔ với `daily_nav_snapshot.raw_positions` (`row["qty"] += qty`) — hàm đó
    cũng đọc positions của CÙNG loại bản ghi DNSE và cũng phải gộp nhiều `loanPackageId` của một
    mã. Khác biệt CÓ CHỦ Ý duy nhất: `raw_positions` nhận 1 `date` cụ thể (đọc đúng 1 file), còn
    hàm này quét NHIỀU ngày (nhiều file `dnse_raw_*.jsonl`) nên cần chọn bản ghi MỚI NHẤT của
    TỪNG ngày trước khi gộp — không được gộp CHÉO giữa hai bản ghi khác thời điểm của cùng
    ngày (sẽ cộng hai lần), và cũng không được lấy nhầm bản ghi CŨ hơn nếu file chứa nhiều
    snapshot trong ngày mà không theo đúng thứ tự thời gian.
    """
    day_last_ts = {}   # ngày -> ts bản ghi mới nhất đã thấy cho ngày đó
    day_last_rec = {}  # ngày -> bản ghi positions ứng với ts mới nhất đó
    for rec in _broker_records("positions", account_no):
        ts = rec.get("ts") or ""
        day = ts[:10]
        if day in day_last_ts and ts < day_last_ts[day]:
            continue                                  # bản ghi cũ hơn bản đã thấy — bỏ
        day_last_ts[day] = ts
        day_last_rec[day] = rec

    out = {}
    for day, rec in day_last_rec.items():
        for it in rec.get("payload", {}).get("positions", []):
            if str(it.get("accountNo")) != str(account_no):
                continue
            key = (it["symbol"], day)
            out[key] = out.get(key, 0.0) + float(it.get("openQuantity") or 0)
    return out


# ======================================================================================
# KHUNG QUY CHIẾU KHỐI LƯỢNG HƯỞNG QUYỀN  (vá 2026-09-24 — call-site thứ 3 của lớp lỗi
# "hai số từ hai nguồn, ranh giới corp-action nằm giữa"; hai cái trước: daily_nav_snapshot
# `corp_action_gate_v2` 4dcc3643, compute_active_nav/park_holdings `exdate_frame` 508bb607)
# ======================================================================================
# VẤN ĐỀ. `broker_qty()` trả bản ghi positions CUỐI NGÀY. Nhưng DNSE credit cổ phiếu mới
# ngay TỐI T-1 — đo thật trên 6/7 sự kiện có trong `data/corp_actions.json`:
#
#     VHM 05/08  SpaceX   500 → 1.000   (×2,0)        BID 14/08  SpaceX 1.100 → 1.175
#     VIX 19/08  SpaceX   400 →   420   (×1,05)       MSB 27/08  SpaceX   500 →   600
#     VIB 09/09  SpaceX   500 →   547   (×1,095)      VPB 23/09  SpaceX 1.100 → 1.386
#
# Nên ở `last_cum_date` con số đọc được là KL SAU sự kiện, trong khi ngữ nghĩa cần là KL
# HƯỞNG QUYỀN (trước). Hệ phương trình tầng 2 (`delta = Σ qty × per_share`) do đó mang hệ số
# lớn hơn sự thật đúng bằng hệ số sự kiện ⇒ `per_share` giải ra THẤP hơn đúng bấy nhiêu lần.
#
# TỆ HƠN: lá chắn cũ (`qtys[last_cum] != qtys[ex_date]` ⇒ STOCK_SUSPECTED) bị CHÍNH tình huống
# này vô hiệu hoá — sau credit sớm thì hai ngày BẰNG NHAU (1.386 = 1.386) nên cờ không bao giờ
# bật. Lá chắn sinh ra cho đúng ca này lại bị đúng ca đó tắt đi.
#
# KHÔNG NEO THEO `broker_effective_ts`. Trường đó CÓ ĐỦ ở cả 7 sự kiện nhưng KHÔNG dùng neo
# được, hai lý do đo được:
#   · MBB 11/08 khai `broker_effective_ts=2026-08-10T19:32:49`, nhưng bản ghi positions cuối
#     cùng của 10/08 là 19:12:13 (KL 1.100, CHƯA credit) — credit thật chỉ xuất hiện trong bản
#     ghi ngày 11/08. Neo theo mốc này trả về đúng số, nhưng vì lý do SAI.
#   · VIX/MSB/VIB/VPB: bản ghi cuối cùng TRƯỚC mốc nằm ở ~04:47–04:51 sáng, tức TRƯỚC phiên.
#     Neo ở đó sẽ bỏ mất mọi lệnh khớp trong chính phiên cum — mà cổ phiếu mua ngày cum VẪN
#     hưởng quyền (SpaceX bán 1.500→1.100 MBB lúc 09:15 ngày 10/08 là ca thật cùng dạng).
# Neo bằng BẰNG CHỨNG KHỐI LƯỢNG thay vì bằng MỐC THỜI GIAN: `classify_qty_residual` trừ lệnh
# khớp thật rồi đối chiếu phần dư với tỉ lệ thực hiện — `qty_now − residual` chính là KL hưởng
# quyền, đã gồm lệnh khớp trong phiên cum.

_CORP_ACTIONS_PATH = "/home/trido/thanhdt/WorkingClaude/data/corp_actions.json"


def _ledger_event(ticker: str, ex_date: str):
    """Sự kiện CỔ PHIẾU từ sổ `data/corp_actions.json` (user đã ký duyệt), ở ĐÚNG hình dạng mà
    `classify_qty_residual` nhận — nguồn lịch THỨ HAI, độc lập với `corp_action_daily_*.json`.

    Vì sao cần nguồn thứ hai: snapshot lịch hằng ngày có ngày KHÔNG TỒN TẠI (đo thật — VHM
    05/08/2026 không có `corp_action_daily_2026-08-05.json`), và khi đó nhánh gán tỉ lệ của
    `classify_qty_residual` TẮT ⇒ một cú credit đúng tỉ lệ rơi xuống `qty_unexplained`. Sổ
    `corp_actions.json` phủ đúng ca đó: VHM ×2,0 giải thích trọn vẹn phần dư +500.

    Chỉ nhận dòng `_status` CONFIRMED — `REVOKED ...` là cách thu hồi một xác nhận (xem chính
    `_status` của VHM), nhận nhầm là khôi phục một sự kiện đã bị rút lại.
    """
    try:
        with open(_CORP_ACTIONS_PATH, encoding="utf-8") as f:
            actions = json.load(f).get("actions") or []
    except (OSError, ValueError):
        return None
    return _pick_ledger_action(actions, ticker, ex_date)


def _pick_ledger_action(actions, ticker: str, ex_date: str):
    """PURE — phần chọn dòng của `_ledger_event`, tách ra để test được cả nhánh REVOKED."""
    for a in actions:
        if a.get("ticker") != ticker or a.get("ex_date") != ex_date:
            continue
        if not str(a.get("_status", "")).upper().startswith("CONFIRMED"):
            continue
        try:
            mult = float(a.get("qty_multiplier"))
        except (TypeError, ValueError):
            continue
        if mult <= 1.0:          # sự kiện không làm tăng KL ⇒ không phải cái ta đang neo
            continue
        return {"date": ex_date, "event_code": a.get("event_type") or "ISS",
                "price_adjusting": True, "exercise_ratio": mult - 1.0,
                "_source": "corp_actions.json"}
    return None


def credit_frame(account_label: str, account_no: str, adjustments: list) -> dict:
    """{(mã, last_cum_date): bằng chứng} — KL ở `last_cum_date` đang ở hệ TRƯỚC hay SAU sự kiện.

    Trả bản ghi `{"status", "entitled", "multiplier", "note"}`:
      status="pre_credit" — broker ĐÃ credit trong ngày cum; `entitled` = KL hưởng quyền thật.
      status="eod"        — KL cuối ngày cum ĐÚNG là KL hưởng quyền (không có credit sớm).
      status="unknown"    — KHÔNG chứng minh được đang ở hệ nào ⇒ người gọi PHẢI fail-closed.

    TÁI DÙNG `daily_nav_snapshot.classify_qty_residual` + plumbing của nó (đã qua 5 vòng
    arch-review, đo trên 104 cặp phiên của cả 2 account: 12 phần dư, 12/12 là corp-action thật).
    Viết lại phép phân loại ở đây là nhân đôi rủi ro, không phải nhân đôi bảo vệ.

    Hai kênh bằng chứng, cố ý KHÁC NHAU về cơ chế:
      1. KHỐI LƯỢNG — phần dư sau khi trừ lệnh khớp thật, khớp tỉ lệ thực hiện.
      2. GIÁ — `exdate_frame.verify_post_event_price`: khi KL KHÔNG đổi mà lịch lại có sự kiện
         cổ phiếu phiên kế tiếp, `marketPrice` tái tạo được `last_cum_price / hệ số` nghĩa là
         giá ĐÃ sang hệ mới trong khi KL chưa — không kết luận được KL thuộc hệ nào ⇒ unknown.
         Kênh này bắt ca credit rơi TRƯỚC cả bản ghi vị thế gần nhất, thứ mà kênh 1 mù.

    §12 — mọi bản ghi đọc ở đây đều đã lọc `account_no` bên trong `raw_positions`/
    `previous_raw_qty`; hàm nhận account_no nên không có đường nào gộp nhầm 2 tài khoản.
    """
    import daily_nav_snapshot as _dns

    out, fill_cache = {}, {}
    by_day = {}
    for adj in adjustments:
        by_day.setdefault(adj.last_cum_date, []).append(adj)

    for day, adjs in sorted(by_day.items()):
        snap = _dns._corp_action_daily_snapshot(day)
        pos, _ts = _dns.raw_positions(account_no, day)
        if pos is None:
            continue                      # không có bản ghi ngày đó ⇒ để người gọi xử như cũ
        for adj in adjs:
            tk = adj.ticker
            qty_now = (pos.get(tk) or {}).get("qty")
            if qty_now is None:
                continue                  # không nắm giữ ⇒ không có gì để neo
            qty_prev, prev_d = _dns.previous_raw_qty(account_no, tk, day)
            if prev_d is not None and qty_prev is None:
                qty_prev = 0.0            # [B2] bản ghi ngày trước CÓ mà vắng mã ⇒ "chưa giữ"
            gaps = []
            net_fill = (_dns.net_fills_between(account_label, prev_d, day, fill_cache,
                                               missing_out=gaps).get(tk)
                        if prev_d else None)
            ev = (_dns.held_event_next_session(snap, day, tk)
                  or _ledger_event(tk, adj.ex_date))
            verdict, detail = _dns.classify_qty_residual(ev, qty_now, qty_prev, net_fill, prev_d)

            if verdict == "share_event_credit":
                ratio = float(detail["exercise_ratio"])
                out[(tk, day)] = {
                    "status": "pre_credit",
                    "entitled": float(detail["qty_now"]) - float(detail["residual"]),
                    "multiplier": 1.0 + ratio,
                    "note": (f"{account_label}: broker credit sớm trong ngày cum "
                             f"({detail['qty_prev']:,.0f}→{detail['qty_now']:,.0f}, lệnh khớp "
                             f"thật {detail['net_fill']:+,.0f}, phần dư {detail['residual']:+,.0f} "
                             f"= tỉ lệ {ratio:g}) ⇒ KL hưởng quyền "
                             f"{float(detail['qty_now']) - float(detail['residual']):,.0f}"),
                }
                continue

            if verdict == "qty_unexplained":
                out[(tk, day)] = {
                    "status": "unknown", "entitled": None, "multiplier": 1.0,
                    "note": (f"{account_label}: KL {detail['qty_prev']:,.0f}→"
                             f"{detail['qty_now']:,.0f} (so với {detail['prev_qty_date']}), lệnh "
                             f"khớp thật {detail['net_fill']:+,.0f} ⇒ phần dư "
                             f"{detail['residual']:+,.0f} CHƯA GIẢI THÍCH ĐƯỢC — không biết KL "
                             f"đang ở hệ TRƯỚC hay SAU sự kiện"
                             + (f" [⚠️ journal thiếu {len(set(gaps))} ngày giao dịch]"
                                if gaps else "")),
                }
                continue

            # verdict == "ok": KL không đổi (hoặc đổi đúng bằng lệnh khớp). Kênh GIÁ nói gì?
            status, why = _frame_from_price(
                adj.last_cum_price, (pos.get(tk) or {}).get("marketPrice"), _event_multiplier(ev))
            out[(tk, day)] = {"status": status, "multiplier": _event_multiplier(ev),
                              "entitled": None if status == "unknown" else float(qty_now),
                              "note": f"{account_label}: {why}"}
    return out


def _event_multiplier(ev) -> float:
    """Hệ số tăng KL của sự kiện CỔ PHIẾU. 1,0 nếu không phải sự kiện cổ phiếu / không đọc được.

    Sự kiện DIV cũng mang `exercise_ratio` nhưng đó là tỉ lệ cổ tức trên MỆNH GIÁ (DRI
    2026-09-22: 0,1 = 1.000đ/10.000đ), KHÔNG phải tỉ lệ cổ phiếu — cùng cái bẫy mà
    `classify_qty_residual` đã ghi.
    """
    if not (ev and ev.get("price_adjusting") and ev.get("event_code") != "DIV"):
        return 1.0
    try:
        return 1.0 + float(ev.get("exercise_ratio") or 0.0)
    except (TypeError, ValueError):
        return 1.0


def _frame_from_price(last_cum_price, market_price, multiplier):
    """(status, lý do) cho ca KL KHÔNG đổi — PURE, không đọc file, không phụ thuộc TZ.

    Kênh KHỐI LƯỢNG mù đúng một ca: credit rơi TRƯỚC cả bản ghi vị thế gần nhất mà ta so sánh,
    nên `qty_now == qty_prev` và phần dư = 0. Khi đó `marketPrice` là nhân chứng còn lại: nếu nó
    tái tạo được `last_cum_price / hệ số` thì GIÁ đã ở hệ sau sự kiện, và ta KHÔNG biết KL đang
    ở hệ nào ⇒ fail-closed. Đây chính là phép kiểm `exdate_frame.verify_post_event_price` — tái
    dùng, không viết lại, vì nó đã có dung sai theo bước giá và ca DNSE điều chỉnh theo GÓI VAY.
    """
    if multiplier <= 1.0:
        return "eod", "KL cuối ngày cum = KL hưởng quyền (không có sự kiện cổ phiếu)"
    import exdate_frame as _ef
    px, why = _ef.verify_post_event_price(last_cum_price, market_price, multiplier)
    if px is not None:
        return "unknown", (f"KL KHÔNG đổi nhưng GIÁ đã sang hệ SAU sự kiện ({why}) — credit có "
                           f"thể đã rơi trước bản ghi vị thế gần nhất; không kết luận được KL "
                           f"thuộc hệ nào")
    return "eod", f"KL cuối ngày cum = KL hưởng quyền; giá vẫn ở hệ TRƯỚC sự kiện ({why})"


def qty_entitled(qmap: dict, adj, frame: dict = None):
    """(KL hưởng quyền, status, ghi chú). `frame` = `credit_frame()` của CHÍNH tài khoản đó.

    `status="unknown"` ⇒ hệ số của ẩn này KHÔNG biết ⇒ người gọi phải BỎ phương trình chứa nó,
    KHÔNG được coi như 0 (coi như 0 là lặng lẽ giải hệ thiếu một ẩn có thật).
    """
    ev = (frame or {}).get((adj.ticker, adj.last_cum_date))
    q = qmap.get((adj.ticker, adj.last_cum_date))
    if q is None:
        q = qmap.get((adj.ticker, adj.ex_date))
        if q is None:
            return 0.0, "eod", ""                     # không nắm giữ ở cả hai ngày
        if ev and float(ev.get("multiplier") or 1.0) > 1.0:
            return 0.0, "unknown", ("chỉ có bản ghi vị thế của CHÍNH ex-date, mà mã này có sự "
                                    "kiện cổ phiếu ⇒ số đó đã ở hệ SAU sự kiện, không suy ngược "
                                    "ra KL hưởng quyền")
        return float(q), "eod", ""
    if ev is None:
        return float(q or 0.0), "eod", ""
    if ev["status"] == "unknown":
        return 0.0, "unknown", ev["note"]
    if ev["status"] == "pre_credit":
        return float(ev["entitled"]), "pre_credit", ev["note"]
    return float(q or 0.0), "eod", ev.get("note", "")


def _qty_at(qmap: dict, adj, frame: dict = None) -> float:
    """KL hưởng quyền (tương thích ngược: gọi 2 tham số = hành vi cũ, KL cuối ngày cum)."""
    return qty_entitled(qmap, adj, frame)[0]


def _connected(equations: list, n: int) -> list:
    """Gom (phương trình, ẩn) thành thành phần liên thông. equations = [(cols, rhs, label)]."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for cols, *_ in equations:
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


def _cash_ratio_ref(adj) -> float:
    """Ước lượng TẦNG 1 của riêng CHÂN TIỀN MẶT — đã trừ phần giá tụt do chân CỔ PHIẾU.

    `ratio_per_share` của `_scan_jumps` là `P(1 − 1/jump)`, mà `jump` gộp CẢ HAI chân:

        jump = ratio_ex / ratio_cum = P_cum × m / (P_cum − cash)   (m = hệ số tăng KL)
        ⇒ cash = P_cum × (1 − m / jump)

    Với m = 1 (thuần tiền mặt) công thức thu về đúng bản cũ, nên mọi ca cũ KHÔNG đổi một đồng.
    Với sự kiện CÓ chân cổ phiếu, bản cũ trả một con số lớn gấp nhiều lần chân tiền thật (VPB
    23/09: P=27.800, m=1,2604 ⇒ bản cũ 5.744đ/cp cho một sự kiện KHÔNG có đồng tiền mặt nào),
    và lưới an toàn `SANITY_REL` so với con số đó sẽ bác đúng nghiệm ĐÚNG.

    Trả 0 khi không dựng được — người gọi coi đó là "không có chân tiền" và từ chối mọi nghiệm
    dương (fail-closed), thay vì bỏ qua lưới an toàn.
    """
    est = float(getattr(adj, "ratio_per_share", adj.per_share) or 0.0)
    m = float(getattr(adj, "share_multiplier", 1.0) or 1.0)
    p = float(adj.last_cum_price or 0.0)
    if m == 1.0:
        return est
    if p <= 0 or est >= p:
        return 0.0
    jump = p / (p - est)
    return p * (1.0 - m / jump)


def solve_from_broker(adjustments: list, accounts: dict, deltas=None, qtys=None,
                      frames=None) -> list:
    """Giải `per_share` của từng sự kiện TỪ TIỀN BROKER THẬT.

    Đặt `kind=CASH_CONFIRMED` + `source='broker_solved'` khi giải được; ngược lại giữ
    `kind='UNVERIFIED'` (giá trị `per_share` ước lượng từ tỉ số vẫn nằm đó cho mục đích chẩn đoán,
    nhưng `.cash_per_share` trả 0 nên KHÔNG thể lọt vào báo cáo).

    `deltas`/`qtys`/`frames` cho phép tiêm dữ liệu giả lập trong selfcheck (chạy offline).
    `frames` = {nhãn tài khoản: `credit_frame()`} — bằng chứng KL hưởng quyền; None ⇒ tự dựng
    từ dnse_raw + lịch corp-action.
    """
    import numpy as np

    deltas = deltas or {lb: broker_cash_deltas(no) for lb, no in accounts.items()}
    qtys = qtys or {lb: broker_qty(no) for lb, no in accounts.items()}
    if frames is None:
        frames = {lb: credit_frame(lb, no, adjustments) for lb, no in accounts.items()}
    for adj in adjustments:
        adj.source = getattr(adj, "source", "unresolved")

    # (a) Sự kiện có chân CỔ PHIẾU ⇒ gắn STOCK_SUSPECTED. Hai nhánh, KHÁC NHAU về hệ quả:
    live = []
    for adj in adjustments:
        # (a1) BẰNG CHỨNG CƠ KHÍ: broker credit sớm, phần dư KL khớp đúng tỉ lệ thực hiện.
        # Lá chắn CŨ (so KL ngày cum với KL ex-date) KHÔNG bắt được ca này — credit sớm làm hai
        # ngày BẰNG NHAU. Khác lá chắn cũ, nhánh này KHÔNG loại sự kiện khỏi hệ: đã biết chắc KL
        # hưởng quyền (`credit_frame`) và hệ số sự kiện thì CHÂN TIỀN của một sự kiện vừa-tiền-
        # vừa-cổ-phiếu vẫn giải được; solver chỉ nâng lên CASH_CONFIRMED khi nghiệm dương và
        # khớp ước lượng tỉ số ĐÃ TRỪ phần cổ phiếu (xem `_cash_ratio_ref`).
        proven = [frames[lb][(adj.ticker, adj.last_cum_date)] for lb in accounts
                  if frames.get(lb, {}).get((adj.ticker, adj.last_cum_date), {}).get("status")
                  == "pre_credit"]
        if proven:
            adj.share_multiplier = max(float(p["multiplier"]) for p in proven)
            adj.kind = "STOCK_SUSPECTED"
            adj.note = ("sự kiện CỔ PHIẾU đã chứng minh bằng KL (" + "; ".join(
                p["note"] for p in proven) + ")")
            live.append(adj)
            continue

        # (a2) LÁ CHẮN CŨ, giữ nguyên nguyên văn: KL cuối ngày cum ≠ KL ex-date.
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
    # KL hưởng quyền phải là KL TRƯỚC credit (xem khối "KHUNG QUY CHIẾU" ở trên). Ẩn nào KHÔNG
    # chứng minh được đang ở hệ nào thì hệ số của nó KHÔNG BIẾT ⇒ BỎ CẢ PHƯƠNG TRÌNH chứa nó,
    # không được coi như 0: coi như 0 là lặng lẽ giải một hệ thiếu đúng cái ẩn đang gây lệch.
    equations = []
    for lb in accounts:
        by_day, poisoned = {}, {}
        for i, adj in enumerate(live):
            qty, status, why = qty_entitled(qtys[lb], adj, frames.get(lb))
            if status == "unknown":
                adj.note = adj.note or f"KL hưởng quyền KHÔNG xác định được — {why}"
                for day in (adj.last_cum_date, adj.ex_date):
                    if deltas[lb].get(day, 0) > 0:
                        poisoned.setdefault(day, []).append(f"{adj.ticker}: {why}")
                continue
            if qty <= 0:
                continue
            for day in (adj.last_cum_date, adj.ex_date):
                if deltas[lb].get(day, 0) > 0:
                    by_day.setdefault(day, []).append((i, qty))
                    break
        for day, cols in sorted(by_day.items()):
            if day in poisoned:
                for i, _ in cols:
                    live[i].note = (f"phương trình {lb} {day} BỊ BỎ — có ẩn không xác định được "
                                    f"KL hưởng quyền (" + "; ".join(poisoned[day]) + ")")
                continue
            equations.append(([i for i, _ in cols], float(deltas[lb][day]), (lb, day),
                              {i: q for i, q in cols}))

    # (c) Giải từng thành phần liên thông độc lập.
    for eqs, cols in _connected(equations, len(live)):
        pos = {c: j for j, c in enumerate(cols)}
        A = np.zeros((len(eqs), len(cols)))
        b = np.zeros(len(eqs))
        for i, (ecols, rhs, (lb, _), qmap_eq) in enumerate(eqs):
            b[i] = rhs
            for c in ecols:
                A[i, pos[c]] = qmap_eq[c]

        names = ", ".join(f"{live[c].ticker}@{live[c].ex_date}" for c in cols)
        shape = f"{len(eqs)} phương trình / {len(cols)} ẩn: {names}"
        if np.linalg.matrix_rank(A) < len(cols):
            for c in cols:
                live[c].note = (f"hệ VÔ ĐỊNH ({shape}) — nhiều mã cùng ngày chốt quyền mà không đủ "
                                "tài khoản có tỉ lệ nắm giữ khác nhau để tách")
            continue

        x = np.round(np.linalg.lstsq(A, b, rcond=None)[0])
        resid = A @ x - b
        bad = [f"{lb} {d}" for i, (_, _, (lb, d), _) in enumerate(eqs)
               if abs(resid[i]) > max(EQ_TOL_ABS, EQ_TOL_REL * abs(b[i]))]
        if bad:
            for c in cols:
                live[c].note = ("nghiệm KHÔNG khớp tiền broker tại " + ", ".join(bad)
                                + " — có thể còn mã khác cùng ngày chưa phát hiện")
            continue

        for c in cols:
            adj, val = live[c], float(x[pos[c]])
            ref = _cash_ratio_ref(adj)
            if val <= 0 or ref <= 0 or abs(val - ref) > SANITY_REL * ref:
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
        try:
            row = bq_corp_action(adj.ticker, adj.ex_date)
        except Exception as e:
            # FAIL-CLOSED có chủ đích (arch-review 2026-09-24, xem docstring `bq_corp_action`):
            # KHÔNG tra được vendor ⇒ không chạy được 2 lá chắn D1 (stock_leg_ignored/
            # cash_mismatch) cho ĐÚNG mã này. Vẫn hạ CHỈ sự kiện này (không crash cả
            # resolve_dividends — các mã khác mà BQ tra được vẫn được xử lý bình thường; một
            # đợt BQ hỏng thật sẽ khiến NHIỀU/mọi mã trong rổ cùng rơi vào nhánh này, tự làm báo
            # cáo hiện rõ "toàn UNVERIFIED" thay vì âm thầm công bố số chưa được lưới an toàn xác
            # nhận — lỗi hạ tầng thấy được LỚN HƠN để buộc chạy lại, so với công bố sai mà im lặng).
            adj.vendor_check = "lookup_failed"
            err = str(e)[:300]
            adj.vendor_note = (f"KHÔNG TRA ĐƯỢC nguồn vendor corporate_action (lỗi hạ tầng, KHÔNG "
                               f"phải vendor không có sự kiện): {err} — 2 lá chắn D1 "
                               f"(stock_leg_ignored/cash_mismatch) KHÔNG chạy được cho mã này, thử "
                               f"lại khi BQ khoẻ")
            if adj.kind == "CASH_CONFIRMED":
                adj.kind = "UNVERIFIED"
                adj.note = (adj.note + " | " if adj.note else "") + adj.vendor_note
            continue
        if not row:
            adj.vendor_check = "unavailable"
            adj.vendor_note = "không có sự kiện executed nào ở (mã, ex-date) trong corporate_action"
            continue
        adj.vendor_cash = float(row.get("cash") or 0.0)
        adj.vendor_stock = float(row.get("stock") or 0.0)
        adj.vendor_note = row.get("titles", "")

        if adj.kind == "CASH_CONFIRMED":
            # broker đã cho số chính thức — vendor chỉ được phép XÁC NHẬN hoặc BÁO ĐỘNG
            if adj.vendor_cash <= 0 and adj.vendor_stock > 0 and adj.share_multiplier == 1.0:
                # BẤT NHẤT NỘI BỘ (arch-review vòng 2, D1). Ba mảnh bằng chứng đang cầm trong tay,
                # KHÔNG phải hạ cấp mù (§29):
                #   · vendor NÓI THẲNG đây là sự kiện CỔ PHIẾU (`ISS`, exercise_ratio > 0) và
                #     KHÔNG có chân tiền (`value_per_share` rỗng ⇒ vendor_cash = 0);
                #   · solver vẫn trả `CASH_CONFIRMED` với một số tiền dương;
                #   · `share_multiplier == 1,0` ⇒ solver CHƯA HỀ biết đến chân cổ phiếu đó, nên
                #     con số nó giải ra là giá rơi của chia tách bị đọc thành tiền cổ tức.
                # Không có bản vá này thì nhánh `vendor_cash <= 0` gán nhãn LÀNH TÍNH `broker_only`
                # (không consumer nào đọc), GIỮ CASH_CONFIRMED, và CÔNG BỐ một khoản cổ tức KHÔNG
                # TỒN TẠI — y hệt lỗ hổng mà chính sách 2026-09-24 ra đời để đóng, chỉ khác nhánh
                # con. Trước đây nó LATENT nhờ hai lá chắn ở `solve_from_broker` (a1 `credit_frame`
                # pre_credit, a2 KL đổi tại ex-date) hạ sự kiện xuống STOCK_SUSPECTED trước; nhưng
                # đó là phòng thủ ở HÀM KHÁC và lá chắn TRƯỢT được (credit muộn + thiếu bản ghi
                # `dnse_raw` ⇒ cả hai dấu hiệu im lặng). Phòng thủ phải ĐỐI XỨNG.
                # Đo trên dữ liệu thật (K1, 39 mã × 6 tháng): MẪU SỐ ĐÚNG không phải 62 sự kiện —
                # nhánh này chỉ CÓ THỂ chạy khi `adj.kind == "CASH_CONFIRMED"` (dòng if ở trên), và
                # chỉ 6/62 sự kiện đạt điều kiện đó (MBB 09/07, CTG+VCB 23/07, NCT 27/07, SAB
                # 28/07, DGC 14/09) ⇒ ô rủi ro thật = 6, và 0/6 khớp hình dạng này ⇒ 0 DƯƠNG TÍNH
                # GIẢ. 12/62 sự kiện có `vendor_cash=0 ∧ vendor_stock>0` nhưng tất cả đã là
                # STOCK_CONFIRMED (broker không giải được) nên KHÔNG đi vào nhánh CASH_CONFIRMED
                # này — không phải mẫu số của phép đo này (arch-review D1b, R3).
                adj.vendor_check = "mismatch"
                adj.vendor_mismatch_reason = "stock_leg_ignored"
                ly_do = (
                    f"LỆCH NGUỒN (chân cổ phiếu bị bỏ qua): vendor `corporate_action` khai đây là "
                    f"sự kiện CỔ PHIẾU tỉ lệ {adj.vendor_stock:.4f} và KHÔNG có chân tiền, nhưng "
                    f"solver giải ra {adj.per_share:,.0f}đ/cp TIỀN MẶT với share_multiplier=1,0 "
                    f"(tức chưa hề biết đến chân cổ phiếu) ⇒ con số đó gần như chắc chắn là giá "
                    f"rơi của chia tách bị đọc thành cổ tức ⇒ HẠ VỀ UNVERIFIED, KHÔNG công bố tỉ "
                    f"suất cho mã này — cần Winston (data-ops) đối soát nguồn vendor với sổ broker")
                adj.vendor_note = ly_do
                adj.kind = "UNVERIFIED"
                adj.note = (adj.note + " | " if adj.note else "") + ly_do
            elif adj.vendor_cash <= 0:
                # vendor thiếu hẳn chân tiền mà cũng không khai chân cổ phiếu nào (hoặc solver ĐÃ
                # biết chân cổ phiếu): vendor thiếu dòng DIV là chuyện thường (K1 thực tế
                # 2026-09-24: 0/62 sự kiện rơi vào nhánh này — CHƯA gặp ca thật, nhưng lý do vẫn
                # đứng: một mã có tiền cổ tức thật về tài khoản mà `corporate_action` chưa kịp có
                # dòng DIV cho đúng (ticker, ex-date) đó) ⇒ CỐ Ý không hạ cấp, tránh mất số oan.
                # (VNM 2026-06-25 KHÔNG phải ví dụ của nhánh này — `row` không tồn tại ⇒ nó rơi
                # vào `if not row: vendor_check = "unavailable"` ở TRÊN, arch-review D1b, R3.)
                adj.vendor_check = "broker_only"
            elif abs(adj.vendor_cash - adj.per_share) <= max(VENDOR_MISMATCH_ABS,
                                                              VENDOR_MISMATCH_REL * adj.per_share):
                adj.vendor_check = "match"
            else:
                # HẠ VỀ UNVERIFIED (chính sách user chốt 2026-09-24). Trước bản vá này nhãn
                # `mismatch` chỉ là GHI CHÚ: `kind` vẫn CASH_CONFIRMED ⇒ `cash_per_share` vẫn cho
                # số qua cổng ⇒ hai nguồn độc lập lệch 50% vẫn ra một tỉ suất CÔNG BỐ, và
                # `PositionReturn.unverified` rỗng nên không một cảnh báo nào nổi lên. Không
                # consumer nào trong repo đọc `vendor_check`, nên nhãn đó KHÔNG chặn được gì.
                adj.vendor_check = "mismatch"
                adj.vendor_mismatch_reason = "cash_mismatch"
                lech_pct = (abs(adj.vendor_cash - adj.per_share) / adj.per_share * 100.0
                            if adj.per_share > 0 else float("inf"))
                ly_do = (f"LỆCH NGUỒN: broker giải {adj.per_share:,.0f}đ/cp, vendor "
                         f"`corporate_action` khai {adj.vendor_cash:,.0f}đ/cp (lệch {lech_pct:.1f}%) "
                         f"⇒ HẠ VỀ UNVERIFIED, KHÔNG công bố tỉ suất cho mã này — cần Winston "
                         f"(data-ops) đối soát nguồn vendor với sổ broker")
                adj.vendor_note = ly_do
                adj.kind = "UNVERIFIED"
                adj.note = (adj.note + " | " if adj.note else "") + ly_do
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


def _solve_offline(adjs, accounts, qty=None, delta=None, frame=None):
    """`frame={}` (mặc định) = KHÔNG có bằng chứng credit ⇒ hành vi y hệt bản trước bản vá."""
    return solve_from_broker(
        adjs, accounts,
        deltas={lb: (delta or _DELTA).get(lb, {}) for lb in accounts},
        qtys={lb: (qty or _QTY).get(lb, {}) for lb in accounts},
        frames={lb: (frame or {}).get(lb, {}) for lb in accounts})


def _selfcheck() -> int:
    # §5b — selfcheck này import `daily_nav_snapshot` (qua `credit_frame`), mà cây import đó
    # chạm `trading_bot`. Chặn mọi side-effect ra BUS trước khi có gì được dựng.
    os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
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

    # ==================================================================================
    # KHUNG QUY CHIẾU KL HƯỞNG QUYỀN (vá 2026-09-24) — mục 16→20
    # Số của fixture lấy nguyên hình dạng ca THẬT VPB 24/09/2026 (m = 1,2604104; SpaceX
    # 1.100→1.386, ZaloPay 1.200→1.512), thêm một chân TIỀN MẶT 1.000đ/cp mà VPB không có —
    # đó chính là cấu trúc "cổ tức tiền + cổ phiếu cùng ex-date" rất phổ thông ở VN.
    # ==================================================================================
    _M = 1.2604104
    _P = 27800.0
    _CASH = 1000.0
    _JUMP = _P * _M / (_P - _CASH)              # tỉ số Close/Price nhảy vì CẢ HAI chân
    _EST = _P * (1.0 - 1.0 / _JUMP)             # ước lượng tầng 1 (gộp cả hai chân)

    def _combined_adj():
        return _mk("ZZZ", "2026-09-24", "2026-09-23", _P, _EST)

    def _frame_credited(entitled_by_lb):
        return {lb: {("ZZZ", "2026-09-23"): {
            "status": "pre_credit", "entitled": float(q), "multiplier": _M,
            "note": f"{lb}: fixture credit sớm"}} for lb, q in entitled_by_lb.items()}

    _QTY_CREDITED = {"SpaceX": {("ZZZ", "2026-09-23"): 1386, ("ZZZ", "2026-09-24"): 1386},
                     "ZaloPay": {("ZZZ", "2026-09-23"): 1512, ("ZZZ", "2026-09-24"): 1512}}
    _DELTA_COMBINED = {"SpaceX": {"2026-09-23": 1100 * _CASH},
                       "ZaloPay": {"2026-09-23": 1200 * _CASH}}

    print("16) CỔ TỨC TIỀN + CỔ PHIẾU CÙNG EX-DATE, broker credit sớm ⇒ per_share vẫn ĐÚNG:")
    print(f"     KL cuối ngày cum ĐÃ credit (1.386/1.512) nhưng KL hưởng quyền là 1.100/1.200;"
          f" tiền thật {1100 * _CASH:,.0f} / {1200 * _CASH:,.0f}")
    a16 = _combined_adj()
    _solve_offline([a16], ACCOUNTS, qty=_QTY_CREDITED, delta=_DELTA_COMBINED,
                   frame=_frame_credited({"SpaceX": 1100, "ZaloPay": 1200}))
    check("ZZZ per_share (chân TIỀN MẶT)", a16.per_share, _CASH)
    same("ZZZ kind/source", (a16.kind, a16.source), ("CASH_CONFIRMED", "broker_solved"))
    check("ZZZ cash_per_share được phép vào báo cáo", a16.cash_per_share, _CASH)
    print("     MUTATION — đảo bản vá (dùng KL cuối ngày 1.386/1.512 như trước):")
    a16b = _combined_adj()
    _solve_offline([a16b], ACCOUNTS, qty=_QTY_CREDITED, delta=_DELTA_COMBINED)   # frame rỗng
    check("→ per_share KHÔNG còn bằng 1.000 (bản cũ giải ra thấp hơn ~hệ số sự kiện)",
          abs(a16b.cash_per_share - _CASH) > 1.0, True, tol=0)
    check("→ và fail-closed về 0 (lưới SANITY bắt được, không ra số sai)",
          a16b.cash_per_share, 0.0, tol=1e-9)

    print("17) LÁ CHẮN: credit sớm làm KL hai ngày BẰNG NHAU ⇒ lá chắn CŨ mù, lá chắn MỚI bật:")
    same("KL ngày cum == KL ex-date (điều kiện làm lá chắn cũ câm)",
         _QTY_CREDITED["SpaceX"][("ZZZ", "2026-09-23")]
         == _QTY_CREDITED["SpaceX"][("ZZZ", "2026-09-24")], True)
    a17 = _combined_adj()
    _solve_offline([a17], ACCOUNTS, qty=_QTY_CREDITED,
                   delta={"SpaceX": {}, "ZaloPay": {}},          # không có dòng tiền nào
                   frame=_frame_credited({"SpaceX": 1100, "ZaloPay": 1200}))
    same("ZZZ kind (thuần cổ phiếu, không có tiền) = STOCK_SUSPECTED", a17.kind,
         "STOCK_SUSPECTED")
    check("ZZZ cash_per_share", a17.cash_per_share, 0.0, tol=1e-9)
    check("ZZZ share_multiplier ghi lại đúng hệ số sự kiện", a17.share_multiplier, _M, tol=1e-9)

    print("18) KHÔNG chứng minh được KL ở hệ nào ⇒ FAIL-CLOSED, và BỎ luôn phương trình đó:")
    # Bộ số CỐ Ý dựng để "bỏ qua ẩn không biết" KHÔNG lộ ra dưới dạng dư số: tỉ lệ nắm giữ
    # ZZZ/YYY giống hệt nhau ở cả hai tài khoản (1.100/1.000 = 440/400 = 1,1) nên phần nhiễm
    # là một phép NHÂN đều — hệ vẫn "khớp tiền" hoàn hảo và lưới SANITY cũng cho qua (502 lệch
    # 0,4% < 1%). Đây chính là ca mà coi ẩn-không-biết như 0 sẽ công bố một số SAI mà không có
    # cảnh báo nào; chỉ việc BỎ phương trình mới chặn được.
    a18 = _combined_adj()
    other = _mk("YYY", "2026-09-24", "2026-09-23", 20000.0, 500.0)
    unknown_frame = {lb: {("ZZZ", "2026-09-23"): {
        "status": "unknown", "entitled": None, "multiplier": _M,
        "note": f"{lb}: fixture không đọc được lịch"}} for lb in ACCOUNTS}
    _solve_offline([a18, other], ACCOUNTS,
                   qty={"SpaceX": {("ZZZ", "2026-09-23"): 1386, ("YYY", "2026-09-23"): 1000},
                        "ZaloPay": {("ZZZ", "2026-09-23"): 555, ("YYY", "2026-09-23"): 400}},
                   delta={"SpaceX": {"2026-09-23": 1100 * 2.0 + 1000 * 500.0},
                          "ZaloPay": {"2026-09-23": 440 * 2.0 + 400 * 500.0}},
                   frame=unknown_frame)
    same("ZZZ kind", a18.kind, "UNVERIFIED")
    check("ZZZ cash_per_share", a18.cash_per_share, 0.0, tol=1e-9)
    same("YYY (mã LÀNH cùng ngày) cũng KHÔNG được giải — hệ số ẩn kia không biết",
         other.kind, "UNVERIFIED")
    check("YYY cash_per_share", other.cash_per_share, 0.0, tol=1e-9)
    check("→ nếu coi ẩn-không-biết như 0 thì YYY sẽ được công bố 502đ/cp thay vì 500 "
          "(sai 0,4%, lọt cả dư số lẫn SANITY)", other.per_share != 502.0, True, tol=0)
    print(f"     lý do ghi lại: {other.note[:90]}…")

    print("19) `_cash_ratio_ref` — ước lượng tỉ số phải TRỪ phần giá tụt do chân cổ phiếu:")
    a19 = _combined_adj()
    a19.share_multiplier = _M
    check("sự kiện TIỀN+CỔ PHIẾU: ref ≈ đúng chân tiền 1.000đ/cp", _cash_ratio_ref(a19), _CASH,
          tol=1.0)
    pure_stock = _mk("VPB", "2026-09-24", "2026-09-23", _P, _P * (1.0 - 1.0 / _M))
    pure_stock.share_multiplier = _M
    check("sự kiện THUẦN cổ phiếu: ref = 0 ⇒ mọi nghiệm dương bị từ chối",
          _cash_ratio_ref(pure_stock), 0.0, tol=1.0)
    pure_cash = _mk("MBB", "2026-07-09", "2026-07-08", 26000.0, 1000.0)
    check("sự kiện THUẦN tiền mặt: ref KHÔNG đổi một đồng so với bản cũ",
          _cash_ratio_ref(pure_cash), 1000.0, tol=1e-9)

    print("20) DỮ LIỆU THẬT — `credit_frame` trên dnse_raw của CẢ 2 tài khoản (§12):")
    print("    7 sự kiện trong data/corp_actions.json; KL hưởng quyền phải KHÁC nhau giữa 2 TK.")
    _REAL = {   # (mã, ngày cum): {tài khoản: KL hưởng quyền đã đối soát tay}
        ("VHM", "2026-08-05"): {"SpaceX": 500.0, "ZaloPay": 300.0},
        ("BID", "2026-08-14"): {"SpaceX": 1100.0, "ZaloPay": 400.0},
        ("VIX", "2026-08-19"): {"SpaceX": 400.0, "ZaloPay": 100.0},
        ("MSB", "2026-08-27"): {"SpaceX": 500.0, "ZaloPay": 200.0},
        ("VIB", "2026-09-09"): {"SpaceX": 500.0, "ZaloPay": 200.0},
        ("VPB", "2026-09-23"): {"SpaceX": 1100.0, "ZaloPay": 1200.0},
    }
    real_adjs = [_mk(tk, next_ex, cum, 0.0, 0.0) for (tk, cum), next_ex in [
        (("VHM", "2026-08-05"), "2026-08-06"), (("BID", "2026-08-14"), "2026-08-17"),
        (("VIX", "2026-08-19"), "2026-08-20"), (("MSB", "2026-08-27"), "2026-08-28"),
        (("VIB", "2026-09-09"), "2026-09-10"), (("VPB", "2026-09-23"), "2026-09-24")]]
    frames_real = {lb: credit_frame(lb, no, real_adjs) for lb, no in ACCOUNTS.items()}
    for key, want in sorted(_REAL.items()):
        for lb in ACCOUNTS:
            got = frames_real[lb].get(key)
            same(f"{key[0]} {key[1]} {lb} status", (got or {}).get("status"), "pre_credit")
            check(f"{key[0]} {key[1]} {lb} KL hưởng quyền", (got or {}).get("entitled") or -1.0,
                  want[lb])
    diff = sum(1 for key in _REAL
               if frames_real["SpaceX"][key]["entitled"] != frames_real["ZaloPay"][key]["entitled"])
    check("§12: số sự kiện mà 2 tài khoản cho KL KHÁC nhau (phải > 0)", diff >= 5, True, tol=0)
    mbb = [_mk("MBB", "2026-08-11", "2026-08-10", 24150.0, 0.0)]
    f_mbb = {lb: credit_frame(lb, no, mbb) for lb, no in ACCOUNTS.items()}
    same("MBB 10/08 SpaceX: broker CHƯA credit trong ngày cum ⇒ KL cuối ngày là đúng",
         f_mbb["SpaceX"][("MBB", "2026-08-10")]["status"], "eod")
    check("MBB 10/08 SpaceX KL hưởng quyền = 1.100 (đã trừ lệnh BÁN 400 trong phiên cum)",
          f_mbb["SpaceX"][("MBB", "2026-08-10")]["entitled"], 1100.0)

    print("21) KÊNH GIÁ — bắt ca kênh KHỐI LƯỢNG mù (credit rơi trước bản ghi vị thế gần nhất).")
    print("    Số THẬT: Price(BQ, hệ cum) và marketPrice(broker) đọc từ dnse_raw cùng ngày.")
    for name, px_cum, mp, mult, want in [
        # BID 14/08: BQ Price 38.250 (cum) — broker đã hạ marketPrice về 35.800 = 38.250/1,068433
        ("BID 14/08 giá ĐÃ sang hệ mới", 38250.0, 35800.0, 1.068433, "unknown"),
        # VPB 23/09: 27.800 / 1,2604104 = 22.056 ≈ 22.050 (lệch 6đ, trong 1 bước giá)
        ("VPB 23/09 giá ĐÃ sang hệ mới", 27800.0, 22050.0, 1.2604104, "unknown"),
        # VHM 05/08: 153.000 / 2,0 = 76.500 đúng từng đồng
        ("VHM 05/08 giá ĐÃ sang hệ mới", 153000.0, 76500.0, 2.0, "unknown"),
        # MBB 10/08: broker vẫn để 24.150, cách xa 24.250/1,15 = 21.087 ⇒ còn ở hệ cum
        ("MBB 10/08 giá CÒN ở hệ cum", 24250.0, 24150.0, 1.15, "eod"),
        # không có chân cổ phiếu ⇒ không có gì để nghi, KL cuối ngày là đúng
        ("thuần tiền mặt (m=1)", 26000.0, 25000.0, 1.0, "eod"),
        # broker không trả giá ⇒ KHÔNG có nhân chứng ⇒ không được suy là "an toàn"
        ("broker không trả marketPrice", 27800.0, None, 1.2604104, "eod"),
    ]:
        same(name, _frame_from_price(px_cum, mp, mult)[0], want)
    print("     ⚠️ ca cuối: thiếu marketPrice ⇒ kênh giá CÂM, chỉ còn kênh khối lượng bảo vệ —")
    print("        ghi lại để không ai tưởng 'eod' ở đó là một kết luận dương tính.")

    print("22) `_event_multiplier` — sự kiện DIV cũng mang `exercise_ratio` nhưng đó là tỉ lệ")
    print("    cổ tức trên MỆNH GIÁ, KHÔNG phải tỉ lệ cổ phiếu (ca thật DRI 22/09: 0,1 = 1.000đ):")
    for name, ev, want in [
        ("DIV ratio 0,1 (DRI 22/09) ⇒ KHÔNG được thành hệ số 1,1",
         {"event_code": "DIV", "price_adjusting": True, "exercise_ratio": 0.1}, 1.0),
        ("ISS ratio 0,2604104 (VPB 24/09) ⇒ hệ số 1,2604104",
         {"event_code": "ISS", "price_adjusting": True, "exercise_ratio": 0.2604104}, 1.2604104),
        ("sự kiện KHÔNG điều chỉnh giá ⇒ 1,0",
         {"event_code": "ISS", "price_adjusting": False, "exercise_ratio": 0.5}, 1.0),
        ("không có sự kiện ⇒ 1,0", None, 1.0),
        ("ratio hỏng kiểu ⇒ 1,0 (không ném lỗi giữa đường dựng báo cáo)",
         {"event_code": "ISS", "price_adjusting": True, "exercise_ratio": "x"}, 1.0),
    ]:
        check(name, _event_multiplier(ev), want, tol=1e-9)
    print("23) `_ledger_event` — chỉ nhận dòng CONFIRMED, bỏ REVOKED, bỏ sự kiện không tăng KL:")
    check("VPB 24/09 (CONFIRMED trong data/corp_actions.json) ⇒ hệ số 1,2604104",
          _event_multiplier(_ledger_event("VPB", "2026-09-24")), 1.2604104, tol=1e-9)
    same("mã không có trong sổ ⇒ None", _ledger_event("ZZZ", "2026-09-24"), None)
    same("đúng mã nhưng SAI ex-date ⇒ None", _ledger_event("VPB", "2026-09-23"), None)
    _LEDGER_FIXTURE = [
        {"ticker": "AAA", "ex_date": "2026-10-01", "qty_multiplier": 1.5,
         "event_type": "BONUS_ISSUE", "_status": "REVOKED — user rút xác nhận 2026-09-30"},
        {"ticker": "BBB", "ex_date": "2026-10-01", "qty_multiplier": 1.0,
         "event_type": "STOCK_DIVIDEND", "_status": "CONFIRMED — user ký duyệt"},
        {"ticker": "CCC", "ex_date": "2026-10-01", "qty_multiplier": "hỏng",
         "event_type": "BONUS_ISSUE", "_status": "CONFIRMED — user ký duyệt"},
        {"ticker": "DDD", "ex_date": "2026-10-01", "qty_multiplier": 1.5,
         "event_type": "BONUS_ISSUE", "_status": "CONFIRMED — user ký duyệt"},
    ]
    same("_status REVOKED ⇒ KHÔNG khôi phục sự kiện đã bị rút lại",
         _pick_ledger_action(_LEDGER_FIXTURE, "AAA", "2026-10-01"), None)
    same("hệ số 1,0 (không tăng KL) ⇒ None", _pick_ledger_action(_LEDGER_FIXTURE, "BBB",
                                                                 "2026-10-01"), None)
    same("hệ số hỏng kiểu ⇒ None (không ném lỗi)",
         _pick_ledger_action(_LEDGER_FIXTURE, "CCC", "2026-10-01"), None)
    check("dòng CONFIRMED hợp lệ ⇒ tỉ lệ 0,5",
          (_pick_ledger_action(_LEDGER_FIXTURE, "DDD", "2026-10-01") or {})
          .get("exercise_ratio", -1), 0.5, tol=1e-9)

    print("24) CHÍNH SÁCH vendor mismatch (user chốt 2026-09-24): LỆCH NGUỒN ⇒ HẠ VỀ UNVERIFIED.")
    print("    Ca gốc do arch-review dựng: sự kiện VỪA-TIỀN-VỪA-CỔ-PHIẾU, broker giải ra 1.000đ/cp,")
    print("    vendor khai 1.500đ/cp (lệch 50%) — trước bản vá vẫn ra số CÔNG BỐ, 0 cảnh báo.")

    def _resolve_offline(ex_date, broker_ps, vendor_cash, vendor_stock, solved=True, mult=1.0):
        """Chạy `resolve_dividends` KHÔNG chạm BQ/broker: thay 3 cửa I/O bằng hằng số.

        `mult` = `share_multiplier` mà solver để lại (1,0 = solver KHÔNG biết chân cổ phiếu nào).
        """
        g = globals()
        keep = {k: g[k] for k in ("detect_adjustments", "solve_from_broker", "bq_corp_action")}
        made = _mk("ZZZ", ex_date, "2026-09-23", 27_800.0, broker_ps)

        def _detect(tk, start, end):
            return [made]

        def _solve(todo, accounts, *a, **kw):
            for t in todo:
                t.share_multiplier = mult
                if solved:
                    t.per_share, t.kind, t.source = broker_ps, "CASH_CONFIRMED", "broker_solved"
            return todo

        def _vendor(tk, ex, include_announced=False):
            return {"cash": vendor_cash, "stock": vendor_stock, "titles": "DIV+ISS (fixture)"}

        g["detect_adjustments"], g["solve_from_broker"], g["bq_corp_action"] = (
            _detect, _solve, _vendor)
        try:
            return resolve_dividends(["ZZZ"], "2026-09-01", "2026-09-30", with_crosscheck=False)[0]
        finally:
            g.update(keep)

    a24 = _resolve_offline("2026-09-24", 1_000.0, 1_500.0, 0.2604104)
    same("mismatch ⇒ vendor_check", a24.vendor_check, "mismatch")
    same("mismatch ⇒ kind HẠ VỀ UNVERIFIED (KHÔNG còn CASH_CONFIRMED)", a24.kind, "UNVERIFIED")
    check("mismatch ⇒ cash_per_share = 0 (không qua cổng công bố)", a24.cash_per_share, 0.0,
          tol=1e-9)
    # ASSERTION có tên — mutation "giữ CASH_CONFIRMED khi mismatch" phải CHẾT ở đây, không chỉ
    # đếm FAIL rồi chạy tiếp (đúng yêu cầu dispatch 2026-09-24).
    assert a24.kind == "UNVERIFIED", (
        "MUTATION-GUARD vendor_mismatch_downgrade: vendor lệch 50% với tiền broker mà `kind` vẫn "
        f"{a24.kind!r} ⇒ tỉ suất mã này VẪN được công bố. Đây chính là lỗ hổng chính sách "
        "2026-09-24.")
    assert a24.cash_per_share == 0.0, (
        "MUTATION-GUARD vendor_mismatch_cash_blocked: mismatch mà cash_per_share vẫn > 0.")
    for tu in ("1,000", "1,500", "50.0%", "Winston"):
        same(f"lý do có '{tu}'", tu in a24.note, True)
    assert "Winston" in a24.note and "1,500" in a24.note and "1,000" in a24.note, (
        "MUTATION-GUARD vendor_mismatch_reason: lý do phải có SỐ của cả hai nguồn + chỉ đích danh "
        f"Winston (data-ops) — §29. Đang là: {a24.note!r}")
    pr24 = PositionReturn("ZZZ", 100, 27_800.0, 24_464.0, 0.0, [a24])
    check("mã lệch nguồn nổi lên PositionReturn.unverified", len(pr24.unverified), 1, tol=0)
    assert pr24.unverified, ("MUTATION-GUARD vendor_mismatch_surfaced: PositionReturn.unverified "
                             "rỗng ⇒ báo cáo công bố số mà không một cảnh báo nào nổi lên.")

    print("    Chống hồi quy — vendor KHỚP thì vẫn công bố BÌNH THƯỜNG (kể cả có chân cổ phiếu):")
    a24b = _resolve_offline("2026-09-24", 1_000.0, 1_000.0, 0.2604104)
    same("vendor khớp ⇒ vendor_check", a24b.vendor_check, "match")
    same("vendor khớp ⇒ kind giữ CASH_CONFIRMED", a24b.kind, "CASH_CONFIRMED")
    check("vendor khớp ⇒ vẫn công bố 1.000đ/cp", a24b.cash_per_share, 1_000.0, tol=1e-9)
    assert a24b.cash_per_share == 1_000.0, (
        "MUTATION-GUARD vendor_match_still_published: vá mismatch KHÔNG được làm mất số công bố "
        "của sự kiện hai nguồn ĐỒNG THUẬN.")

    print("    Ngưỡng (VENDOR_MISMATCH_REL=1%, sàn 1đ/cp) — hai bên sát ngưỡng:")
    a24c = _resolve_offline("2026-09-24", 1_000.0, 1_009.0, 0.0)     # lệch 0,9% < 1%
    same("lệch 0,9% ⇒ match, vẫn công bố", (a24c.vendor_check, a24c.kind),
         ("match", "CASH_CONFIRMED"))
    a24d = _resolve_offline("2026-09-24", 1_000.0, 1_011.0, 0.0)     # lệch 1,1% > 1%
    same("lệch 1,1% ⇒ mismatch, hạ UNVERIFIED", (a24d.vendor_check, a24d.kind),
         ("mismatch", "UNVERIFIED"))

    print("    24b) NHÁNH CON ANH EM (arch-review vòng 2, D1): vendor khai THUẦN CỔ PHIẾU mà")
    print("         solver vẫn giải ra tiền với share_multiplier=1,0 ⇒ BẤT NHẤT NỘI BỘ.")
    # Ca G1 do reviewer dựng: trước bản vá D1 nó ra (broker_only, CASH_CONFIRMED, 1.000đ/cp CÔNG BỐ).
    a24h = _resolve_offline("2026-09-24", 1_000.0, 0.0, 0.2604104, mult=1.0)
    same("vendor thuần CP + mult=1,0 ⇒ vendor_check",
         (a24h.vendor_check, a24h.vendor_mismatch_reason), ("mismatch", "stock_leg_ignored"))
    same("vendor thuần CP + mult=1,0 ⇒ vendor_check ĐƠN LẺ đúng 'mismatch' (không phải "
         "'broker_only' — nhãn mà entitled_gross lọc, arch-review D1b R3)",
         a24h.vendor_check, "mismatch")
    # ASSERTION CÓ TÊN (arch-review D1b, R3) — trước bản vá này mutant "mismatch -> broker_only"
    # chỉ chết bằng dòng got/want của `same()` ở trên (đếm FAIL, không dừng), vì `kind`/
    # `cash_per_share` vẫn HẠ ĐÚNG dù `vendor_check` sai. Hậu quả của mutant đó KHÔNG PHẢI vô hại:
    # `report_return_gate.entitled_gross` chỉ vào nhánh cảnh báo khi
    # `a.vendor_check == "mismatch"` — "broker_only" là nhãn LÀNH TÍNH không consumer nào chặn, nên
    # cảnh báo biến mất TRONG IM LẶNG dù `kind` bên dưới đã đúng.
    assert a24h.vendor_check == "mismatch", (
        "MUTATION-GUARD vendor_stock_leg_check_label: `vendor_check` phải là 'mismatch' để "
        "`report_return_gate.entitled_gross` (lọc theo đúng nhãn này) đưa sự kiện vào danh sách "
        f"cảnh báo — đang là {a24h.vendor_check!r}. Nhãn khác 'mismatch' (vd 'broker_only') làm "
        "cảnh báo biến mất TRONG IM LẶNG dù kind/cash_per_share bên dưới vẫn hạ đúng.")
    same("vendor thuần CP + mult=1,0 ⇒ kind HẠ VỀ UNVERIFIED", a24h.kind, "UNVERIFIED")
    check("vendor thuần CP + mult=1,0 ⇒ cash_per_share = 0", a24h.cash_per_share, 0.0, tol=1e-9)
    assert a24h.kind == "UNVERIFIED" and a24h.cash_per_share == 0.0, (
        "MUTATION-GUARD vendor_stock_leg_ignored: vendor khai ISS tỉ lệ 0,26 và KHÔNG có chân tiền, "
        "solver giải 1.000đ/cp với share_multiplier=1,0 (chưa biết chân cổ phiếu), mà `kind` vẫn "
        f"{a24h.kind!r} / cash_per_share = {a24h.cash_per_share} ⇒ báo cáo CÔNG BỐ một khoản cổ tức "
        "KHÔNG TỒN TẠI, không một cảnh báo nào. Đây là nhánh con D1 của lỗ hổng 2026-09-24.")
    for tu in ("0.2604", "1,000", "Winston", "share_multiplier"):
        same(f"lý do D1 có '{tu}'", tu in a24h.note, True)
    assert "Winston" in a24h.note and "0.2604" in a24h.note, (
        "MUTATION-GUARD vendor_stock_leg_reason: lý do phải TRÍCH tỉ lệ ISS mà vendor khai + chỉ "
        f"đích danh Winston, không phát câu chung (§29). Đang là: {a24h.note!r}")
    pr24h = PositionReturn("ZZZ", 100, 27_800.0, 24_464.0, 0.0, [a24h])
    check("mã D1 nổi lên PositionReturn.unverified", len(pr24h.unverified), 1, tol=0)

    print("         CHỐNG QUÁ-HẠ-CẤP: solver ĐÃ biết chân cổ phiếu (mult > 1) ⇒ VẪN QUA.")
    # Ở đây `share_multiplier > 1` là bằng chứng cơ khí rằng `credit_frame` đã chứng minh chân cổ
    # phiếu và `_cash_ratio_ref` đã TRỪ nó ra trước khi nhận nghiệm ⇒ chân tiền dương là hợp lệ,
    # vendor chỉ thiếu dòng DIV (chuyện thường). Hạ cấp ở đây là MẤT SỐ OAN.
    a24i = _resolve_offline("2026-09-24", 1_000.0, 0.0, 0.2604104, mult=1.2604104)
    same("vendor thuần CP nhưng mult>1 ⇒ broker_only, giữ CASH_CONFIRMED",
         (a24i.vendor_check, a24i.kind), ("broker_only", "CASH_CONFIRMED"))
    check("vendor thuần CP nhưng mult>1 ⇒ vẫn công bố 1.000đ/cp", a24i.cash_per_share, 1_000.0,
          tol=1e-9)
    assert a24i.cash_per_share == 1_000.0, (
        "MUTATION-GUARD vendor_stock_leg_no_overreach: vá D1 KHÔNG được hạ cấp sự kiện mà solver ĐÃ "
        "chứng minh chân cổ phiếu bằng KL (share_multiplier > 1) — đó là ca vừa-tiền-vừa-cổ-phiếu "
        "giải ĐÚNG, hạ cấp là mất số oan.")

    print("    Ba nhánh CÒN LẠI không được đổi hành vi:")
    a24e = _resolve_offline("2026-09-24", 1_000.0, 0.0, 0.0)
    same("vendor không có số tiền ⇒ broker_only, giữ CASH_CONFIRMED",
         (a24e.vendor_check, a24e.kind), ("broker_only", "CASH_CONFIRMED"))
    # ASSERTION CÓ TÊN, không chỉ đếm FAIL: đây là ca vendor THIẾU HẲN dòng DIV (`row` CÓ tồn tại
    # nhưng cash=0 ∧ stock=0 — KHÔNG phải VNM 2026-06-25: mã đó `row` không tồn tại nên rơi vào
    # nhánh `unavailable`, không phải `broker_only`; K1 thực tế 0/62 sự kiện có ca `broker_only`
    # thật, arch-review D1b R3). Nới điều kiện của vá D1 cho trùm cả ca này (bỏ `vendor_stock > 0`)
    # là MẤT SỐ OAN trên một sự kiện đã đối soát được với tiền thật.
    assert a24e.kind == "CASH_CONFIRMED" and a24e.cash_per_share == 1_000.0, (
        "MUTATION-GUARD vendor_missing_div_row_still_published: vendor không khai gì (cash=0, "
        "stock=0) là chuyện THƯỜNG và KHÔNG phải bằng chứng chống lại nghiệm broker — hạ cấp ở đây "
        f"làm mất tỉ suất của mã đã có tiền thật về tài khoản. Đang là kind={a24e.kind!r}, "
        f"cash_per_share={a24e.cash_per_share}.")
    a24f = _resolve_offline("2026-09-24", 0.0, 1_200.0, 0.0, solved=False)
    same("broker chưa giải + vendor thuần tiền ⇒ CASH_VENDOR (vẫn bị chặn ở cash_per_share)",
         (a24f.vendor_check, a24f.kind), ("vendor_only", "CASH_VENDOR"))
    check("CASH_VENDOR vẫn không được công bố", a24f.cash_per_share, 0.0, tol=1e-9)
    a24g = _resolve_offline("2026-09-24", 0.0, 0.0, 0.2604104, solved=False)
    same("broker chưa giải + vendor có chân cổ phiếu ⇒ STOCK_CONFIRMED",
         (a24g.vendor_check, a24g.kind), ("vendor_only", "STOCK_CONFIRMED"))

    print("25) `broker_qty()` — GỘP TỔNG các lô cùng mã/ngày, KHÔNG lấy lô CUỐI (vá 2026-09-24).")
    print("    Fixture hình dạng THẬT ZaloPay BID 14/08 (2 gói vay margin, loanPackageId khác nhau,")
    print("    107 + 320 = 427; bản cũ chỉ giữ lô đứng CUỐI mảng positions[] = 320):")
    import tempfile as _tempfile
    global EXEC_LOG_DIR
    _orig_exec_log_dir = EXEC_LOG_DIR
    _tmpdir = _tempfile.mkdtemp(prefix="dividend_selfcheck_")
    try:
        _acct = "9999999999"
        _rec_day1 = {
            "kind": "positions", "account_no": _acct, "ts": "2026-09-01T09:00:00Z",
            "payload": {"positions": [
                {"symbol": "MULTI", "accountNo": _acct, "openQuantity": 107, "loanPackageId": 1826},
                {"symbol": "MULTI", "accountNo": _acct, "openQuantity": 320, "loanPackageId": 1258},
                {"symbol": "SOLO", "accountNo": _acct, "openQuantity": 500, "loanPackageId": 1},
            ]},
        }
        # bản ghi THỨ HAI trong CÙNG ngày, ts SỚM HƠN (rớt về sau trong iteration) — phải bị bỏ,
        # không được cộng chéo vào bản ghi mới nhất (nếu không sẽ nhân đôi KL của MULTI).
        _rec_day1_earlier = {
            "kind": "positions", "account_no": _acct, "ts": "2026-09-01T08:00:00Z",
            "payload": {"positions": [
                {"symbol": "MULTI", "accountNo": _acct, "openQuantity": 999, "loanPackageId": 1826},
            ]},
        }
        _rec_day2 = {
            "kind": "positions", "account_no": _acct, "ts": "2026-09-02T09:00:00Z",
            "payload": {"positions": [
                {"symbol": "MULTI", "accountNo": _acct, "openQuantity": 200, "loanPackageId": 1826},
            ]},
        }
        with open(os.path.join(_tmpdir, "dnse_raw_2026-09-01.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(_rec_day1_earlier) + "\n")
            f.write(json.dumps(_rec_day1) + "\n")
        with open(os.path.join(_tmpdir, "dnse_raw_2026-09-02.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(_rec_day2) + "\n")
        EXEC_LOG_DIR = _tmpdir
        _q25 = broker_qty(_acct)
    finally:
        EXEC_LOG_DIR = _orig_exec_log_dir
        shutil.rmtree(_tmpdir, ignore_errors=True)

    check("nhiều lô cùng mã/ngày ⇒ TỔNG (107+320)", _q25.get(("MULTI", "2026-09-01")), 427.0,
          tol=1e-9)
    check("một lô duy nhất ⇒ KHÔNG đổi so với trước", _q25.get(("SOLO", "2026-09-01")), 500.0,
          tol=1e-9)
    check("ngày khác của CÙNG mã không bị cộng chéo", _q25.get(("MULTI", "2026-09-02")), 200.0,
          tol=1e-9)
    assert _q25.get(("MULTI", "2026-09-01")) == 427.0, (
        "MUTATION-GUARD broker_qty_last_lot_wins: broker_qty() phải GỘP TỔNG các lô cùng "
        "(mã, ngày) trong bản ghi CUỐI NGÀY, không lấy lô đứng cuối mảng positions[]. Ca thật "
        "ZaloPay BID 14/08: 2 lô margin (loanPackageId 1826=107, 1258=320) tổng 427; bản cũ chỉ "
        f"giữ lô cuối = 320. Đang trả về {_q25.get(('MULTI', '2026-09-01'))!r} cho fixture 107+320."
    )
    assert _q25.get(("MULTI", "2026-09-01")) != 999 + 320 + 107, (
        "MUTATION-GUARD broker_qty_cross_record_double_count: broker_qty() ĐANG cộng chéo giữa "
        "hai bản ghi khác thời điểm của CÙNG một ngày (999 từ bản ghi 08:00 cộng nhầm vào bản ghi "
        "09:00) thay vì chỉ lấy bản ghi MỚI NHẤT của ngày đó rồi gộp lô bên trong bản ghi đó."
    )

    print("26) `bq_corp_action` KHÔNG TRA ĐƯỢC (lỗi hạ tầng) ⇒ nhãn `lookup_failed`, KHÔNG lẫn với")
    print("    `unavailable` (vendor XÁC NHẬN 0 dòng) — arch-review 2026-09-24: nuốt exception làm")
    print("    CẢ HAI lá chắn D1 (stock_leg_ignored/cash_mismatch) tắt IM LẶNG khi BQ hỏng, quay lại")
    print("    đúng hành vi trước chính sách vendor-mismatch (§28/§29).")

    def _resolve_offline_raising(ex_date, broker_ps, exc, solved=True):
        g = globals()
        keep = {k: g[k] for k in ("detect_adjustments", "solve_from_broker", "bq_corp_action")}
        made = _mk("ZZZ", ex_date, "2026-09-23", 27_800.0, broker_ps)

        def _detect(tk, start, end):
            return [made]

        def _solve(todo, accounts, *a, **kw):
            for t in todo:
                t.share_multiplier = 1.0
                if solved:
                    t.per_share, t.kind, t.source = broker_ps, "CASH_CONFIRMED", "broker_solved"
            return todo

        def _vendor(tk, ex, include_announced=False):
            raise exc

        g["detect_adjustments"], g["solve_from_broker"], g["bq_corp_action"] = (
            _detect, _solve, _vendor)
        try:
            return resolve_dividends(["ZZZ"], "2026-09-01", "2026-09-30", with_crosscheck=False)[0]
        finally:
            g.update(keep)

    _ERR26 = RuntimeError("BQ 403 PERMISSION_DENIED: quota exceeded for project lithe-record (fixture)")
    a26 = _resolve_offline_raising("2026-09-24", 1_000.0, _ERR26)
    same("BQ ném lỗi ⇒ vendor_check = lookup_failed (KHÔNG phải 'unavailable')",
         a26.vendor_check, "lookup_failed")
    same("BQ ném lỗi khi ĐÃ CASH_CONFIRMED ⇒ hạ về UNVERIFIED (fail-closed)", a26.kind, "UNVERIFIED")
    check("⇒ cash_per_share = 0 (không qua cổng công bố)", a26.cash_per_share, 0.0, tol=1e-9)
    assert a26.kind == "UNVERIFIED" and a26.cash_per_share == 0.0, (
        "MUTATION-GUARD lookup_failed_downgrade: BQ ném lỗi (không tra được vendor) mà `kind` vẫn "
        f"{a26.kind!r}/cash_per_share={a26.cash_per_share} ⇒ báo cáo công bố số CHƯA qua lưới an "
        "toàn D1/mismatch — quay lại đúng hành vi trước bản vá 2026-09-24 (nuốt exception).")
    assert a26.vendor_check == "lookup_failed", (
        "MUTATION-GUARD lookup_failed_label: BQ ném lỗi phải gắn nhãn 'lookup_failed', KHÔNG được "
        "lẫn vào 'unavailable' (vendor XÁC NHẬN 0 dòng, truy vấn CHẠY THÀNH CÔNG) — hai trạng thái "
        f"khác nhau, §28. Đang là {a26.vendor_check!r}.")
    assert "PERMISSION_DENIED" in a26.vendor_note and "quota exceeded" in a26.vendor_note, (
        "MUTATION-GUARD lookup_failed_real_error: vendor_note phải in LỖI THẬT của exception "
        f"(§29 — không đoán nguyên nhân). Đang là: {a26.vendor_note!r}")

    print("    Chống hồi quy — BQ ném lỗi mà broker CHƯA giải (kind chưa từng đạt CASH_CONFIRMED):")
    print("    KHÔNG được ép giá trị nào khác, chỉ đơn thuần KHÔNG promote lên CASH_VENDOR/")
    print("    STOCK_CONFIRMED (những nhãn đó chỉ hợp lệ khi vendor THỰC SỰ tra được):")
    a26b = _resolve_offline_raising("2026-09-24", 0.0, _ERR26, solved=False)
    same("BQ lỗi + broker chưa giải ⇒ vendor_check = lookup_failed", a26b.vendor_check,
         "lookup_failed")
    same("BQ lỗi + broker chưa giải ⇒ kind vẫn UNVERIFIED (KHÔNG bị promote)", a26b.kind,
         "UNVERIFIED")
    assert a26b.kind != "CASH_VENDOR" and a26b.kind != "STOCK_CONFIRMED", (
        "MUTATION-GUARD lookup_failed_no_promote: BQ ném lỗi (không tra được gì) mà `kind` lại "
        f"{a26b.kind!r} — CASH_VENDOR/STOCK_CONFIRMED chỉ hợp lệ khi vendor THỰC SỰ trả về dữ liệu, "
        "không phải khi truy vấn thất bại.")

    print("    Chống hồi quy — vendor XÁC NHẬN 0 dòng (`bq_corp_action` trả về None, KHÔNG ném lỗi)")
    print("    VẪN là 'unavailable', KHÔNG bị lẫn sang 'lookup_failed':")

    def _resolve_offline_none(ex_date, broker_ps):
        g = globals()
        keep = {k: g[k] for k in ("detect_adjustments", "solve_from_broker", "bq_corp_action")}
        made = _mk("ZZZ", ex_date, "2026-09-23", 27_800.0, broker_ps)

        def _detect(tk, start, end):
            return [made]

        def _solve(todo, accounts, *a, **kw):
            for t in todo:
                t.share_multiplier, t.per_share, t.kind, t.source = (
                    1.0, broker_ps, "CASH_CONFIRMED", "broker_solved")
            return todo

        def _vendor(tk, ex, include_announced=False):
            return None   # ĐÚNG mô phỏng: truy vấn CHẠY THÀNH CÔNG, 0 dòng khớp (mã, ex-date)

        g["detect_adjustments"], g["solve_from_broker"], g["bq_corp_action"] = (
            _detect, _solve, _vendor)
        try:
            return resolve_dividends(["ZZZ"], "2026-09-01", "2026-09-30", with_crosscheck=False)[0]
        finally:
            g.update(keep)

    a26c = _resolve_offline_none("2026-09-24", 1_000.0)
    same("vendor 0 dòng (thành công) ⇒ vendor_check = unavailable", a26c.vendor_check,
         "unavailable")
    same("vendor 0 dòng ⇒ kind GIỮ CASH_CONFIRMED (không bị hạ oan)", a26c.kind, "CASH_CONFIRMED")
    check("vendor 0 dòng ⇒ vẫn công bố 1.000đ/cp", a26c.cash_per_share, 1_000.0, tol=1e-9)
    assert a26c.vendor_check != "lookup_failed", (
        "MUTATION-GUARD lookup_failed_not_over_eager: vendor trả về 0 dòng THÀNH CÔNG (không phải "
        f"exception) bị gắn nhầm 'lookup_failed' — đang là {a26c.vendor_check!r}. Sẽ làm MỌI sự "
        "kiện không có dòng vendor (25/62 đo thật K1) bị coi nhầm là lỗi hạ tầng, kéo theo cảnh báo "
        "giả tràn lan mỗi lần chạy resolve_dividends.")
    assert a26c.kind == "CASH_CONFIRMED" and a26c.cash_per_share == 1_000.0, (
        "MUTATION-GUARD unavailable_still_published: vendor 0 dòng là chuyện THƯỜNG (K1 đo 25/62) "
        f"và KHÔNG được hạ cấp sự kiện đã đối soát broker — đang kind={a26c.kind!r}, "
        f"cash_per_share={a26c.cash_per_share}.")

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
