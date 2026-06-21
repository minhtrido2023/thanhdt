"""
wifeed_coverage_audit.py
========================
Đối chiếu schema dữ liệu WiFeed (WiGroup API) với các cột mà hệ thống 8L đang
dùng trong BigQuery `tav2_bq.ticker_financial` (và vài cột thô của `ticker`),
để TRẢ LỜI 1 câu hỏi trước khi trả tiền:

    "WiFeed có cung cấp đủ các NGUỒN THÔ để tôi dựng lại toàn bộ ~190 cột
     tài chính mà 8L đang dùng không? Cột nào THIẾU?"

Hai chế độ:
  1) OFFLINE (mặc định, KHÔNG cần API key) — in bảng ánh xạ cột-8L -> nguồn-WiFeed
     + phân loại RAW / DERIVABLE / GAP, và xuất wifeed_coverage_report.csv.
  2) LIVE PROBE (khi đã có WIFEED_APIKEY) — gọi thật WiFeed cho 1 mã mẫu,
     làm phẳng JSON trả về, và xác nhận từng "raw field" đã ánh xạ có TỒN TẠI
     trong response không (CONFIRMED / MISSING). Đây là bước "thử trước khi mua".

Cách dùng:
    # Offline audit (chạy được ngay):
    python wifeed_coverage_audit.py

    # Live probe sau khi WiFeed cấp key (đăng ký thử free tại wifeed.vn):
    set WIFEED_APIKEY=xxxxxxxx        # Windows CMD
    $env:WIFEED_APIKEY="xxxxxxxx"     # PowerShell
    python wifeed_coverage_audit.py --probe --ticker VNM

LƯU Ý: đường dẫn endpoint WiFeed bên dưới là BEST-GUESS theo WiFeed API v3.
Khi có tài khoản, mở dashboard "Tài liệu API" của bạn và CHỈNH lại CONFIG cho
khớp path/param thật — phần ánh xạ cột (COVERAGE_MAP) thì không phụ thuộc path.
"""

import os
import sys
import csv
import json
import argparse

# Windows console mặc định cp1252 -> ép UTF-8 để in tiếng Việt/emoji
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
OUT_CSV = os.path.join(WORKDIR, "data/wifeed_coverage_report.csv")

# ---------------------------------------------------------------------------
# CONFIG — endpoint WiFeed (chỉnh lại cho khớp tài liệu API của bạn khi có key)
# ---------------------------------------------------------------------------
WIFEED_BASE = "https://wifeed.vn/api"
WIFEED_APIKEY = os.environ.get("WIFEED_APIKEY", "")

# Mỗi "dataset logic" -> (path template, mô tả). {code}=mã CK, {key}=apikey.
# Các path dưới đây theo cấu trúc WiFeed v3 phổ biến; VERIFY lại trên dashboard.
WIFEED_ENDPOINTS = {
    "income":   ("/du-lieu-co-ban/bctc/ket-qua-kinh-doanh",   "Báo cáo KQKD (quý)"),
    "balance":  ("/du-lieu-co-ban/bctc/can-doi-ke-toan",      "Bảng cân đối kế toán (quý)"),
    "cashflow": ("/du-lieu-co-ban/bctc/luu-chuyen-tien-te-gt", "Lưu chuyển tiền tệ (gián tiếp)"),
    "ratios":   ("/du-lieu-co-ban/chi-so-tai-chinh",          "Chỉ số tài chính tính sẵn"),
    "price":    ("/thong-tin-co-phieu/lich-su-gia",           "Lịch sử giá OHLCV"),
    "dividend": ("/thong-tin-co-phieu/lich-su-co-tuc",        "Lịch sử cổ tức"),
    "list":     ("/thong-tin-co-phieu/danh-sach-ma-chung-khoan", "Danh sách mã + ngành ICB"),
}

# ---------------------------------------------------------------------------
# COVERAGE_MAP — trái tim của script.
# Mỗi entry mô tả MỘT NHÓM cột 8L (dùng prefix để gom các _P0.._P7 / _MA / _SD):
#   prefixes : list prefix khớp tên cột ticker_financial
#   dataset  : nguồn WiFeed cần ('income'/'balance'/'cashflow'/'ratios'/'price'/'dividend'/'list'/'internal')
#   raw      : các trường THÔ WiFeed cần có (best-guess key tiếng Việt WiFeed)
#   status   : RAW (WiFeed trả thẳng) | DERIVABLE (8L tự tính từ raw) | GAP (rủi ro thiếu)
#   note     : công thức / ghi chú
# ---------------------------------------------------------------------------
COVERAGE_MAP = [
    # ---- META / identity --------------------------------------------------
    dict(prefixes=["ticker", "time", "quarter", "ID_Release", "Release_Date"],
         dataset="list", raw=["ma_ck", "ngay_cap_nhat"], status="RAW",
         note="Định danh & ngày phát hành BCTC"),

    # ---- NGÀNH (ICB) — cột ticker table, KHÔNG ở ticker_financial ---------
    # 8L dùng ICB_Code = mã FTSE-ICB 4 chữ số (2357/8633/...). RỦI RO LỆCH
    # TAXONOMY: WiFeed có thể trả mã ngành HỆ RIÊNG -> cần crosswalk.
    dict(prefixes=["ICB_Code", "ICB", "Sector", "Industry"],
         dataset="list", raw=["nganh_icb", "ma_nganh_icb", "icb_code",
                               "nganh_cap_4", "ma_nganh"],
         status="GAP", note="VERIFY: WiFeed có trả ĐÚNG mã ICB 4 chữ số FTSE? Nếu hệ riêng -> cần bảng map sang ICB_Code"),
    # Nhóm 8L (bank/cyclical/compounder/power) = TỰ DỰNG từ ICB+moat_tags,
    # KHÔNG vendor nào có. Để minh bạch, đưa vào như cột nội bộ.
    dict(prefixes=["Group_8L", "Moat", "Rating_8L"],
         dataset="internal", raw=["(moat_tags.csv tự dựng)"],
         status="DERIVABLE", note="Nhóm 8L derive từ ICB + business model; KHÔNG mua được từ vendor"),

    # ---- Risk/Beta — cột ticker table, dựng từ giá -----------------------
    dict(prefixes=["Risk_Rating", "Beta", "Dev"],
         dataset="price", raw=["gia_dong_cua_dieu_chinh", "vnindex"],
         status="DERIVABLE", note="Beta/Dev tự tính từ chuỗi giá mã vs VNINDEX"),

    # ---- KQKD (income statement) -----------------------------------------
    dict(prefixes=["NP_P", "NP_R", "NP_Q_Min5Y"],
         dataset="income", raw=["loi_nhuan_sau_thue_cong_ty_me", "loi_nhuan_sau_thue"],
         status="DERIVABLE", note="LN ròng 8 quý -> NP_P0..P7; NP_R=NP_P0/NP_P4-1; Min5Y=min 20 quý"),
    dict(prefixes=["Revenue_P", "Revenue_YoY"],
         dataset="income", raw=["doanh_thu_thuan"],
         status="DERIVABLE", note="Doanh thu thuần 8 quý; YoY = P0/P4-1"),
    dict(prefixes=["GPM_P"],
         dataset="income", raw=["loi_nhuan_gop", "doanh_thu_thuan"],
         status="DERIVABLE", note="GPM = loi_nhuan_gop / doanh_thu_thuan"),
    dict(prefixes=["NPM_P", "EBITM_P", "EBITDA_P", "IntCov_P"],
         dataset="income", raw=["loi_nhuan_sau_thue", "loi_nhuan_truoc_thue",
                                 "chi_phi_lai_vay", "khau_hao", "doanh_thu_thuan"],
         status="DERIVABLE", note="Biên LN & độ phủ lãi vay (EBIT/chi phí lãi vay)"),
    dict(prefixes=["EPS", "EPS_P0", "PEG"],
         dataset="income", raw=["eps", "loi_nhuan_sau_thue_cong_ty_me", "so_luong_cp_luu_hanh"],
         status="DERIVABLE", note="EPS từ report hoặc NP/shares; PEG = PE / growth"),

    # ---- CĐKT (balance sheet) --------------------------------------------
    dict(prefixes=["Inventory_P", "InvTurn", "DIO", "RE_Inventory"],
         dataset="balance", raw=["hang_ton_kho", "gia_von_hang_ban"],
         status="DERIVABLE", note="Tồn kho 8 quý; vòng quay/DIO cần giá vốn"),
    dict(prefixes=["totalAsset_P", "StLiab_P", "LtLiab_P", "AR_P",
                   "StDebt_P", "LtDebt_P", "LtInvest_P", "Cash_P", "EBITDA_P"],
         dataset="balance", raw=["tong_tai_san", "no_ngan_han", "no_dai_han",
                                  "phai_thu_ngan_han", "vay_ngan_han", "vay_dai_han",
                                  "dau_tu_dai_han", "tien_va_tuong_duong_tien",
                                  "dau_tu_tai_chinh_ngan_han"],
         status="DERIVABLE", note="Các dòng CĐKT thô; Cash_P0 = tiền + ĐTTC ngắn hạn"),
    dict(prefixes=["BVPS", "OShares"],
         dataset="balance", raw=["von_chu_so_huu", "so_luong_cp_luu_hanh"],
         status="DERIVABLE", note="BVPS = VCSH / số CP lưu hành"),
    dict(prefixes=["AdvCust_P", "UnearnRev_P"],
         dataset="balance", raw=["nguoi_mua_tra_tien_truoc", "doanh_thu_chua_thuc_hien"],
         status="GAP", note="Dòng CĐKT CHI TIẾT — WiFeed có thể KHÔNG tách (cần xác minh khi probe)"),

    # ---- Tỷ số thanh khoản/đòn bẩy/hiệu quả (ratios) ---------------------
    dict(prefixes=["CR_P", "QuickR_P", "CashR_P"],
         dataset="ratios", raw=["he_so_thanh_toan_hien_hanh", "he_so_thanh_toan_nhanh",
                                 "he_so_thanh_toan_tien_mat"],
         status="RAW", note="WiFeed thường trả sẵn nhóm thanh khoản"),
    dict(prefixes=["Debt_Eq_P", "STLTDebt_Eq_P", "FinLev_P", "FAsset_Eq_P", "OwnEq_Cap_P"],
         dataset="ratios", raw=["no_tren_vcsh", "don_bay_tai_chinh"],
         status="DERIVABLE", note="Đòn bẩy; nếu ratios không đủ -> tính từ CĐKT"),
    dict(prefixes=["AssetTurn_P", "FAssetTurn_P", "DSO_P", "DPO_P", "CashCycle_P", "ROA_P"],
         dataset="ratios", raw=["vong_quay_tai_san", "roa"],
         status="DERIVABLE", note="Hiệu quả hoạt động & ROA; cash cycle = DSO+DIO-DPO"),

    # ---- Định giá (ratios, RAW) ------------------------------------------
    dict(prefixes=["PE", "PB", "PS", "PCF", "EVEB", "DY"],
         dataset="ratios", raw=["pe", "pb", "ps", "pcf", "ev_ebitda", "ty_suat_co_tuc"],
         status="RAW", note="WiFeed chi-so-tai-chinh trả sẵn nhóm định giá"),

    # ---- Chất lượng đa năm (DERIVABLE từ lịch sử dài) --------------------
    dict(prefixes=["ROE3Y", "ROE5Y", "ROE10Y", "ROE_Min3Y", "ROE_Min5Y", "ROE_Min10Y",
                   "ROE_Trailing"],
         dataset="ratios", raw=["roe"],
         status="DERIVABLE", note="Cần chuỗi ROE quý 10 năm -> avg/min/TTM (WiFeed có ~20y)"),
    dict(prefixes=["ROIC3Y", "ROIC5Y", "ROIC10Y", "ROIC_Min3Y", "ROIC_Min5Y",
                   "ROIC_Min10Y", "ROIC_Trailing"],
         dataset="ratios", raw=["roic", "loi_nhuan_truoc_thue", "chi_phi_lai_vay",
                                 "tong_tai_san", "no_ngan_han"],
         status="DERIVABLE", note="ROIC tự tính = NOPAT/(VCSH+nợ vay); avg/min đa năm"),
    dict(prefixes=["FSCORE", "FSCORE_P1"],
         dataset="ratios", raw=["roa", "luu_chuyen_tien_thuan_hdkd", "tong_tai_san",
                                 "no_dai_han", "he_so_thanh_toan_hien_hanh",
                                 "so_luong_cp_luu_hanh", "bien_loi_nhuan_gop",
                                 "vong_quay_tai_san"],
         status="DERIVABLE", note="Piotroski 9 cấu phần từ IS/BS/CF — tự tính"),

    # ---- Lưu chuyển tiền tệ (cashflow) -----------------------------------
    dict(prefixes=["CF_OA_P", "CF_OA_3Y", "CF_OA_5Y"],
         dataset="cashflow", raw=["luu_chuyen_tien_thuan_tu_hdkd"],
         status="DERIVABLE", note="CF_OA = CFO/tổng tài sản; 3Y/5Y = tổng dồn"),
    dict(prefixes=["CF_Invest_P", "CF_Invest_3Y", "CF_Invest_5Y"],
         dataset="cashflow", raw=["luu_chuyen_tien_thuan_tu_hdtt"],
         status="DERIVABLE", note="CF từ hoạt động đầu tư (capex); 3Y/5Y tổng dồn"),

    # ---- Cổ tức (dividend) -----------------------------------------------
    dict(prefixes=["Dividend_Min3Y", "Dividend_1Y", "Dividend_3Y"],
         dataset="dividend", raw=["co_tuc_tien_mat", "ngay_chot_quyen"],
         status="GAP", note="Cần lịch sử cổ tức tiền mặt — xác minh endpoint dividend khi probe"),

    # ---- Giá & lịch sử định giá (price + derived) ------------------------
    dict(prefixes=["Close", "Price"],
         dataset="price", raw=["gia_dong_cua", "gia_dong_cua_dieu_chinh"],
         status="DERIVABLE", note="Giá tại thời điểm BCTC từ lịch sử giá"),
    dict(prefixes=["PE_MA", "PE_SD", "PB_MA", "PB_SD", "EVEB_MA", "EVEB_SD"],
         dataset="internal", raw=["(chuỗi PE/PB/EVEB lịch sử)"],
         status="DERIVABLE", note="MA/SD 3M/1Y/5Y dựng từ chuỗi PE/PB hằng ngày = price x EPS/BVPS"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_8l_columns():
    """Danh sách đầy đủ cột ticker_financial (snapshot từ BQ 2026-06-14).
    Nếu muốn lấy LIVE: bq show --schema ... ticker_financial."""
    return [
        "ticker","time","quarter","ID_Release","Release_Date","Close","Price","NP_R",
        "NP_P0","NP_P1","NP_P2","NP_P3","NP_P4","NP_P5","NP_P6","NP_P7",
        "Revenue_P0","Revenue_P1","Revenue_P2","Revenue_P3","Revenue_P4","Revenue_P5","Revenue_P6","Revenue_P7",
        "GPM_P0","GPM_P1","GPM_P2","GPM_P3","GPM_P4","GPM_P5","GPM_P6","GPM_P7",
        "Inventory_P0","Inventory_P1","Inventory_P2","Inventory_P3","Inventory_P4","Inventory_P5","Inventory_P6","Inventory_P7",
        "AdvCust_P0","AdvCust_P1","AdvCust_P2","AdvCust_P3","AdvCust_P4","AdvCust_P5","AdvCust_P6","AdvCust_P7",
        "UnearnRev_P0","UnearnRev_P1","UnearnRev_P2","UnearnRev_P3","UnearnRev_P4","UnearnRev_P5","UnearnRev_P6","UnearnRev_P7",
        "CR_P0","CR_P4","ROA_P0","ROA_P4","EBITM_P0","EBITM_P4","NPM_P0","NPM_P4",
        "CashR_P0","CashR_P4","QuickR_P0","QuickR_P4","FinLev_P0","FinLev_P4",
        "AssetTurn_P0","AssetTurn_P4","FAssetTurn_P0","FAssetTurn_P4","DSO_P0","DSO_P4",
        "DIO_P0","DIO_P4","DPO_P0","DPO_P4","CashCycle_P0","CashCycle_P4","InvTurn_P0","InvTurn_P4",
        "STLTDebt_Eq_P0","STLTDebt_Eq_P4","Debt_Eq_P0","Debt_Eq_P4","FAsset_Eq_P0","FAsset_Eq_P4",
        "OwnEq_Cap_P0","OwnEq_Cap_P4","Revenue_YoY_P0","Revenue_YoY_P4","IntCov_P0","IntCov_P4",
        "DY","EPS_P0","BVPS","OShares","totalAsset_P0","StLiab_P0","LtLiab_P0","AR_P0",
        "StDebt_P0","LtDebt_P0","EBITDA_P0","LtInvest_P0","Cash_P0","RE_Inventory",
        "PB","PE","PS","PCF","EVEB","ROE3Y","ROE5Y","ROE10Y","ROE_Min3Y","ROE_Min5Y","ROE_Min10Y",
        "ROIC3Y","ROIC5Y","ROIC10Y","ROIC_Min3Y","ROIC_Min5Y","ROIC_Min10Y",
        "CF_OA_3Y","CF_OA_5Y","CF_Invest_3Y","CF_Invest_5Y","NP_Q_Min5Y",
        "Dividend_Min3Y","Dividend_1Y","Dividend_3Y",
        "CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3","CF_OA_P4",
        "CF_Invest_P0","CF_Invest_P1","CF_Invest_P2","CF_Invest_P3","CF_Invest_P4",
        "FSCORE","FSCORE_P1","ROE_Trailing","ROIC_Trailing","ROIC_Trailing_v1","EPS","PEG",
        "PE_MA5Y","PE_MA1Y","PE_MA3M","PE_SD5Y","PE_SD1Y","PE_SD3M",
        "PB_MA5Y","PB_MA1Y","PB_MA3M","PB_SD5Y","PB_SD1Y","PB_SD3M",
        "EVEB_MA5Y","EVEB_MA1Y","EVEB_MA3M","EVEB_SD5Y","EVEB_SD1Y","EVEB_SD3M",
        # --- cột thuộc bảng `ticker` (8L dùng nhưng KHÔNG ở ticker_financial) ---
        "ICB_Code", "Risk_Rating",
    ]


def match_column(col, prefixes):
    return any(col == p or col.startswith(p) for p in prefixes)


def build_coverage():
    """Gán mỗi cột 8L vào 1 entry COVERAGE_MAP. Trả về (rows, unmatched)."""
    cols = load_8l_columns()
    rows = []
    matched = set()
    for col in cols:
        hit = None
        for entry in COVERAGE_MAP:
            if match_column(col, entry["prefixes"]):
                hit = entry
                break
        if hit:
            matched.add(col)
            rows.append(dict(column=col, dataset=hit["dataset"], status=hit["status"],
                             raw_fields="; ".join(hit["raw"]), note=hit["note"]))
        else:
            rows.append(dict(column=col, dataset="?", status="UNMAPPED",
                             raw_fields="", note="Chưa ánh xạ — kiểm tra thủ công"))
    unmatched = [c for c in cols if c not in matched]
    return rows, unmatched


# ---------------------------------------------------------------------------
# LIVE PROBE (chỉ chạy khi có WIFEED_APIKEY)
# ---------------------------------------------------------------------------

def flatten_keys(obj, prefix=""):
    """Lấy mọi key (đệ quy) trong JSON trả về để dò sự tồn tại của raw field."""
    keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.add(str(k).lower())
            keys |= flatten_keys(v, prefix)
    elif isinstance(obj, list):
        for it in obj[:3]:  # đủ 3 phần tử mẫu
            keys |= flatten_keys(it, prefix)
    return keys


def flatten_pairs(obj, out=None):
    """Lấy mọi cặp (key_lower, value) phẳng — để soi GIÁ TRỊ ngành trả về."""
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                flatten_pairs(v, out)
            else:
                out.append((str(k).lower(), v))
    elif isinstance(obj, list):
        for it in obj[:3]:
            flatten_pairs(it, out)
    return out


def check_industry_taxonomy(list_pairs, expect_icb):
    """So trường ngành WiFeed trả về với ICB_Code thật của 8L.
    Phát hiện: (a) WiFeed có trường ngành không, (b) có khớp mã ICB 4 chữ số không."""
    print("\n=== KIỂM TRA TAXONOMY NGÀNH (quan trọng nhất) ===")
    if not list_pairs:
        print("  [!] Endpoint 'list' không trả dữ liệu — không kiểm tra được.")
        return
    # các key nghi là ngành
    ind_keys = [(k, v) for k, v in list_pairs
                if any(t in k for t in ["nganh", "icb", "sector", "industry", "phan_loai"])]
    if not ind_keys:
        print("  [MISSING] Không thấy trường ngành nào trong response 'list'.")
        print("            -> WiFeed có thể để ngành ở endpoint riêng (vd /phan-nganh-icb). VERIFY.")
        return
    print("  Trường ngành WiFeed trả về (key = value mẫu):")
    for k, v in ind_keys:
        print(f"     {k:24s} = {v}")
    # so khớp ICB 4 chữ số
    if expect_icb:
        exp = str(int(float(expect_icb))) if str(expect_icb).replace('.', '').isdigit() else str(expect_icb)
        hit = any(exp in str(v) for k, v in ind_keys)
        if hit:
            print(f"  [MATCH]    Có giá trị chứa ICB '{exp}' của bạn -> taxonomy KHỚP, dùng trực tiếp.")
        else:
            print(f"  [MISMATCH] KHÔNG thấy mã ICB '{exp}'. WiFeed nhiều khả năng dùng HỆ NGÀNH RIÊNG")
            print(f"             -> CẦN BẢNG CROSSWALK (WiFeed-sector -> ICB_Code) trước khi thay nguồn.")


def probe_wifeed(ticker):
    try:
        import requests
    except ImportError:
        print("  [!] Cần `pip install requests` để chạy live probe.")
        return {}
    if not WIFEED_APIKEY:
        print("  [!] Chưa set WIFEED_APIKEY -> bỏ qua live probe.")
        return {}

    found_keys = {}
    raw_pairs = {}
    for name, (path, desc) in WIFEED_ENDPOINTS.items():
        url = WIFEED_BASE + path
        params = {"code": ticker, "apikey": WIFEED_APIKEY}
        try:
            r = requests.get(url, params=params, timeout=20)
            print(f"  [{name:9s}] {r.status_code}  {url}")
            if r.status_code == 200:
                try:
                    data = r.json()
                except Exception:
                    data = {}
                found_keys[name] = flatten_keys(data)
                raw_pairs[name] = flatten_pairs(data)
            else:
                found_keys[name] = set()
                raw_pairs[name] = []
        except Exception as e:
            print(f"  [{name:9s}] ERROR {e}")
            found_keys[name] = set()
            raw_pairs[name] = []
    return found_keys, raw_pairs


def confirm_raw_fields(found_keys):
    """So các raw field đã ánh xạ với key thực tế WiFeed trả về."""
    print("\n=== XÁC NHẬN RAW FIELD (live) ===")
    for entry in COVERAGE_MAP:
        ds = entry["dataset"]
        if ds in ("internal", "list"):
            continue
        present = found_keys.get(ds, set())
        if not present:
            continue
        for raw in entry["raw"]:
            token = raw.lower().split("(")[0].strip()
            # so khớp lỏng: raw field xuất hiện như substring của 1 key trả về
            ok = any(token in k or k in token for k in present) if token else False
            flag = "CONFIRMED" if ok else "MISSING  "
            print(f"  [{flag}] {ds:9s} :: {raw}")


# ---------------------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="Gọi WiFeed thật (cần WIFEED_APIKEY)")
    ap.add_argument("--ticker", default="VNM", help="Mã mẫu để probe")
    ap.add_argument("--expect-icb", default="", help="ICB_Code thật của mã (lấy từ BQ) để so taxonomy, vd 2357")
    args = ap.parse_args()

    rows, unmatched = build_coverage()

    # Xuất CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["column", "dataset", "status", "raw_fields", "note"])
        w.writeheader()
        w.writerows(rows)

    # Tổng hợp
    from collections import Counter
    by_status = Counter(r["status"] for r in rows)
    by_dataset = Counter(r["dataset"] for r in rows)
    total = len(rows)

    print("=" * 72)
    print(" ĐỘ PHỦ WIFEED vs CỘT 8L (ticker_financial)")
    print("=" * 72)
    print(f" Tổng số cột 8L kiểm tra : {total}")
    print("\n Phân loại khả năng dựng lại từ WiFeed:")
    for st in ["RAW", "DERIVABLE", "GAP", "UNMAPPED"]:
        n = by_status.get(st, 0)
        bar = "#" * int(40 * n / total)
        print(f"   {st:10s} {n:4d} ({100*n/total:4.1f}%)  {bar}")

    print("\n Theo nguồn dữ liệu WiFeed cần mua:")
    for ds, n in by_dataset.most_common():
        desc = WIFEED_ENDPOINTS.get(ds, (None, "(nội bộ tính)"))[1] if ds in WIFEED_ENDPOINTS else "(nội bộ/khác)"
        print(f"   {ds:9s} {n:4d} cột   <- {desc}")

    # Liệt kê các GAP — đây là thứ user cần quan tâm nhất
    gaps = [r for r in rows if r["status"] in ("GAP", "UNMAPPED")]
    print("\n" + "-" * 72)
    print(f" ⚠️  CỘT RỦI RO THIẾU NGUỒN ({len(gaps)} cột) — cần xác minh/khác nguồn:")
    print("-" * 72)
    for r in gaps:
        print(f"   {r['column']:18s} [{r['status']}] {r['note']}")

    print(f"\n Báo cáo chi tiết -> {OUT_CSV}")

    # Live probe
    if args.probe:
        print("\n" + "=" * 72)
        print(f" LIVE PROBE WiFeed — ticker={args.ticker}")
        print("=" * 72)
        result = probe_wifeed(args.ticker)
        if result:
            found, raw_pairs = result
            confirm_raw_fields(found)
            check_industry_taxonomy(raw_pairs.get("list", []), args.expect_icb)
    else:
        print("\n (Thêm --probe + WIFEED_APIKEY để gọi WiFeed thật và xác nhận raw field.)")


if __name__ == "__main__":
    main()
