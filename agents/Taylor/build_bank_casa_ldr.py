#!/usr/bin/env python3
"""
build_bank_casa_ldr.py — nguồn CASA + LDR cho rổ ngân hàng đang nắm giữ (13 mã)
==============================================================================
Đóng [GAP] §1a của `research/sbv_meeting_note_impact_20260813.md`: BigQuery
`ticker_financial` KHÔNG có cột nào về CASA / LDR / deposit / loan cho ngân hàng
(schema doanh nghiệp phi tài chính; StLiab/LtLiab/StDebt/LtDebt/CR/FinLev = 0).

HAI CHÂN, KHÁC HẲN NHAU VỀ ĐỘ TIN CẬY — đọc kỹ trước khi trích số:

  LDR  = Cho vay khách hàng (GỘP, trước dự phòng) / Tiền gửi của khách hàng
         → TỰ TÍNH từ 2 dòng BẢNG CÂN ĐỐI (vnstock/VCI `balance_sheet`).
         Kỳ hiện hành (community edition trả 4 quý GẦN NHẤT). Tái lập được.

  CASA = tiền gửi không kỳ hạn / tổng tiền gửi khách hàng
         → KHÔNG có trong bảng cân đối. Nằm ở THUYẾT MINH BCTC ("Tiền gửi của
         khách hàng — phân theo loại tiền gửi"). Script này KHÔNG bịa ra nó:
         cột `casa` để trống, `casa_source="MISSING_NEEDS_FOOTNOTE"`.

⚠️ BẪY ĐÃ ĐO (2026-08-14) — vì sao KHÔNG lấy CASA từ vnstock `ratio()`:
   endpoint `finance.ratio()` CÓ đúng 2 chỉ tiêu `CASA Ratio` và `LDR (%)`, nhưng
   dưới community edition nó trả về **4 quý của năm 2018** — không phải 4 quý gần
   nhất (khác hẳn `balance_sheet`, vốn trả đúng kỳ mới). `period="year"` chỉ lặp
   lại đúng 4 quý 2018 đó 4 lần. Nhãn cột còn hỏng (mọi cột đều tên "2018").
   Kỳ THẬT chỉ đọc được ở 2 dòng dữ liệu `Năm` / `Quý`, không đọc được ở header.
   ⇒ Ai lấy `CASA Ratio` từ đó cho phân tích hôm nay đang dùng số **8 năm trước**
   mà không có gì báo lỗi. `bank_lens_v3.py` / `bank_lens_v2.py` đọc đúng cột này
   (biến `C_CASA`) — nay chúng crash trước ở `lengthReport` (vnstock đổi shape),
   nên chưa từng in ra số 2018; "sửa" chúng một cách ngây thơ sẽ TẠO RA bug đó.

Output: data/bank_casa_ldr_<asof>.csv (tên KHÔNG canonical — §8 coding_guidelines)
Chạy:   python3 mike/agents/Taylor/build_bank_casa_ldr.py
"""
import warnings; warnings.filterwarnings("ignore")
import logging; logging.disable(logging.CRITICAL)
import os, sys, time, json
import pandas as pd
from vnstock import Vnstock

WORKDIR = "/home/trido/thanhdt/WorkingClaude"

# Rổ ngân hàng đang nắm giữ THẬT — đọc từ positions dnse_raw_2026-08-13.jsonl
# (SpaceX + ZaloPay hợp nhất). KHÔNG phải universe ngân hàng VN nói chung.
BANKS = ["ACB", "BID", "CTG", "HDB", "LPB", "MBB", "MSB",
         "SHB", "TCB", "TPB", "VCB", "VIB", "VPB"]

# Nhãn dòng bảng cân đối ngân hàng (lang="vi"). Dòng "Cho vay khách hàng" xuất
# hiện HAI LẦN: bản RÒNG (đã trừ dự phòng, nằm ngay trước dòng dự phòng) và bản
# GỘP. Lấy MAX = bản gộp — chuẩn quốc tế của LDR dùng dư nợ gộp.
IT_LOAN = "Cho vay khách hàng"
IT_PROV = "Dự phòng rủi ro cho vay khách hàng"
IT_DEP = "Tiền gửi của khách hàng"
IT_ASSET = "TỔNG TÀI SẢN"
IT_CDGTCG = "Phát hành giấy tờ có giá"
IT_INTERBANK = "Tiền gửi và vay các Tổ chức tín dụng khác"

# ---------------------------------------------------------------------------
# CASA — chân YẾU. Đọc kỹ trước khi trích.
# ---------------------------------------------------------------------------
# KHÔNG phải số tự tính. Đây là số BÁO CHÍ tổng hợp từ BCTC Q2/2026, chép tay
# 2026-08-14 từ 2 bài (vietnambiz + mekongasean). Hai bài khớp nhau tới 2 chữ số
# — NHƯNG đó KHÔNG phải 2 nguồn độc lập: nhiều khả năng cùng một bảng tổng hợp
# gốc. Coi như MỘT nguồn, chưa đối soát với thuyết minh gốc.
#
# ⚠️ HAI BÀI ĐỊNH NGHĨA KHÁC NHAU cho cùng con số:
#     vietnambiz  : CASA = (tiền gửi KHÔNG kỳ hạn + tiền KÝ QUỸ) / tiền gửi KH
#     mekongasean : CASA = tiền gửi KHÔNG kỳ hạn / tiền gửi KH
#   Số giống nhau ⇒ ít nhất một trong hai mô tả SAI. Chưa xác định được cái nào.
#   Ảnh hưởng: tiền ký quỹ ở NH lớn có thể là 1-3pp ⇒ sai số cỡ đó.
#
# ⚠️ Mức bình quân hệ thống cũng KHÔNG khớp giữa các nguồn: 14,7% (vietnambiz)
#   vs 17,19% (nguoiquansat). Chênh 2,5pp ⇒ rổ mẫu/định nghĩa khác nhau.
#
# CHỈ có tại 30/6/2026, KHÔNG có chuỗi lịch sử. 3/13 mã KHÔNG có số: HDB, SHB, VPB.
CASA_PRESS_2026Q2 = {
    "TCB": 0.3502, "MBB": 0.3443, "VCB": 0.3278, "CTG": 0.2317,
    "MSB": 0.2283, "TPB": 0.2097, "ACB": 0.2052, "BID": 0.2037,
    "VIB": 0.1189, "LPB": 0.0637,
    # HDB, SHB, VPB: không tìm thấy trong nguồn nào đã quét — để trống, KHÔNG suy đoán.
}
CASA_PRESS_PERIOD = "2026-Q2"
CASA_PRESS_SRC = "PRESS_UNVERIFIED_2026Q2"

# Số ĐÃ CÔNG BỐ (báo chí đọc thẳng BCTC gốc, đường dữ liệu KHÁC hẳn VCI) —
# dùng để đối soát chéo chân LDR. Đây là cái làm nên khác biệt giữa "trông hợp lý"
# và "đã verify": mẫu số/tử số của LDR được xác nhận bởi nguồn không liên quan.
# (ticker, cột, giá trị VND đã công bố, nguồn)
CROSSCHECK_2026Q2 = [
    ("CTG", "cust_deposit_vnd", 1.89e15, "tinnhanhchungkhoan: 1,89 trieu ty"),
    ("CTG", "loan_gross_vnd", 2.09e15, "tinnhanhchungkhoan: 2,09 trieu ty"),
    ("MBB", "cust_deposit_vnd", 963.815e12, "BCTC HN Q2/2026: 963.815 ty"),
    ("TCB", "cust_deposit_vnd", 662.447e12, "BCTC HN Q2/2026: 662.447 ty"),
    ("VPB", "cust_deposit_vnd", 733.0e12, "nguoiquansat: gan 733.000 ty"),
]


def pull(tk, retries=3):
    """Trả về dict theo từng kỳ, hoặc None nếu không lấy được."""
    for attempt in range(retries):
        try:
            fin = Vnstock().stock(symbol=tk, source="VCI").finance
            bs = fin.balance_sheet(period="quarter", lang="vi", dropna=False)
            break
        except Exception as e:
            if attempt == retries - 1:
                print(f"  [skip {tk}] {repr(e)[:70]}", flush=True)
                return None
            time.sleep(5)

    periods = [c for c in bs.columns if isinstance(c, str) and "-Q" in c]
    if not periods:
        print(f"  [skip {tk}] khong co cot ky", flush=True)
        return None

    def get(item, period, agg="max"):
        rows = bs.loc[bs["item"] == item, period].dropna()
        if len(rows) == 0:
            return float("nan")
        return float(rows.max() if agg == "max" else rows.min())

    out = []
    for p in periods:
        loan_gross = get(IT_LOAN, p, "max")
        loan_net = get(IT_LOAN, p, "min")
        prov = get(IT_PROV, p, "min")
        dep = get(IT_DEP, p, "max")
        row = {
            "ticker": tk, "period": p,
            "loan_gross_vnd": loan_gross,
            "loan_net_vnd": loan_net,
            "provision_vnd": prov,
            "cust_deposit_vnd": dep,
            "total_asset_vnd": get(IT_ASSET, p, "max"),
            "cds_issued_vnd": get(IT_CDGTCG, p, "max"),
            "interbank_funding_vnd": get(IT_INTERBANK, p, "max"),
            "ldr_pure": loan_gross / dep if dep else float("nan"),
            "ldr_source": "COMPUTED_FROM_VCI_BALANCE_SHEET",
        }
        # CASA không suy ra được từ bảng cân đối — chỉ gắn số báo chí ở ĐÚNG kỳ
        # nó nói tới, các kỳ khác để trống thay vì kéo ngang (kéo ngang = bịa).
        if p == CASA_PRESS_PERIOD and tk in CASA_PRESS_2026Q2:
            row["casa"] = CASA_PRESS_2026Q2[tk]
            row["casa_source"] = CASA_PRESS_SRC
        else:
            row["casa"] = float("nan")
            row["casa_source"] = "MISSING_NEEDS_FOOTNOTE"
        out.append(row)
    return out


def main():
    rows = []
    for i, tk in enumerate(BANKS):
        r = pull(tk)
        if r:
            rows.extend(r)
            last = r[-1]
            print(f"  {tk}: {last['period']} LDR={last['ldr_pure']*100:6.2f}% "
                  f"loan={last['loan_gross_vnd']/1e12:8.1f}k ty  "
                  f"dep={last['cust_deposit_vnd']/1e12:8.1f}k ty", flush=True)
        if i < len(BANKS) - 1:
            time.sleep(3)

    if not rows:
        print("NO DATA (network / vnstock).")
        sys.exit(1)

    df = pd.DataFrame(rows).sort_values(["ticker", "period"])
    # SELF-CHECK bắt buộc: bất biến kế toán gộp = ròng + dự phòng (dự phòng âm).
    df["selfcheck_loan_resid_vnd"] = (
        df["loan_gross_vnd"] + df["provision_vnd"] - df["loan_net_vnd"]).abs()
    bad = df[df["selfcheck_loan_resid_vnd"] > 1e6]
    asof = pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").strftime("%Y%m%d")
    out = os.path.join(WORKDIR, "data", f"bank_casa_ldr_{asof}.csv")
    df.to_csv(out, index=False)

    print(f"\nSELF-CHECK 1 — bat bien ke toan gop==rong+duphong: "
          f"{len(df)-len(bad)}/{len(df)} ky khop (sai lech >1tr VND: {len(bad)})")
    if len(bad):
        print(bad[["ticker", "period", "selfcheck_loan_resid_vnd"]].to_string())

    # SELF-CHECK 2 — doi soat cheo voi so DA CONG BO tren bao chi (duong du lieu
    # HOAN TOAN KHAC: bao chi doc BCTC goc, khong qua VCI). Bat sai lech >1%.
    print("\nSELF-CHECK 2 — doi soat cheo nguon doc lap (bao chi doc BCTC goc):")
    q2 = df[df["period"] == "2026-Q2"].set_index("ticker")
    for tk, field, published, src in CROSSCHECK_2026Q2:
        if tk not in q2.index:
            continue
        ours = float(q2.loc[tk, field])
        dev = (ours - published) / published
        flag = "OK " if abs(dev) <= 0.01 else "LECH"
        print(f"  [{flag}] {tk:4s} {field:18s} ta={ours/1e12:8.1f}k ty  "
              f"cong bo={published/1e12:8.1f}k ty  lech={dev*100:+.2f}%  ({src})")

    print(f"\nSaved {out}  ({df['ticker'].nunique()} ma, {len(df)} ky)")
    n_casa = int(df["casa"].notna().sum())
    print(f"CASA: {n_casa}/13 ma co so (chi ky {CASA_PRESS_PERIOD}), "
          f"status {CASA_PRESS_SRC} — CHUA doi soat thuyet minh goc.")


if __name__ == "__main__":
    main()
