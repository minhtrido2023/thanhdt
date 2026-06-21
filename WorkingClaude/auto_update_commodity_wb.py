#!/usr/bin/env python3
"""auto_update_commodity_wb.py — TỰ ĐỘNG cập nhật 6 file commodity từ World Bank "Pink Sheet"
================================================================================================
Thay cho quy trình NHẬP TAY (tải xlsx thủ công rồi chạy rebuild_commodity_wb.py).
Script này tự: (1) DÒ link xlsx Pink Sheet mới nhất từ trang World Bank (hash đổi theo
tháng) -> (2) TẢI về cache -> (3) PARSE -> (4) KIỂM TRA tính hợp lệ -> (5) GHI an toàn
(atomic + .bak) 6 file data/*_monthly.csv.

KHÔNG đụng tới caustic_soda (World Bank không có series xút — vẫn là ước lượng, low-confidence).

Nguồn: World Bank Commodity Markets, file CMO-Historical-Data-Monthly.xlsx, sheet "Monthly Prices".
Trang: https://www.worldbank.org/en/research/commodity-markets

Cách dùng:
    python auto_update_commodity_wb.py                 # tự dò link + tải + cập nhật
    python auto_update_commodity_wb.py --dry-run       # chỉ báo cáo, KHÔNG ghi
    python auto_update_commodity_wb.py --url <URL>     # ép dùng URL xlsx cụ thể
    python auto_update_commodity_wb.py --xlsx <PATH>   # dùng file xlsx đã tải sẵn (offline)

Cài phụ thuộc (nếu thiếu): pip install requests pandas openpyxl

Tự động hóa định kỳ (Windows Task Scheduler, chạy đầu mỗi tháng):
    schtasks /Create /SC MONTHLY /D 3 /TN "8L_CommodityWB" /TR ^
      "python C:\\...\\auto_update_commodity_wb.py" /ST 08:00
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, re, argparse, shutil, tempfile
from datetime import datetime
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd

W = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
DATA_DIR = os.path.join(W, "data")
CACHE_DIR = os.path.join(DATA_DIR, "_wb_cache")
START = "2006-04"  # giữ đúng cửa sổ file hiện có

WB_PAGE = "https://www.worldbank.org/en/research/commodity-markets"
# Fallback nếu dò link thất bại (bản tháng 6/2026 — cập nhật khi cần):
FALLBACK_URL = ("https://thedocs.worldbank.org/en/doc/"
                "74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/"
                "CMO-Historical-Data-Monthly.xlsx")

# 8L file -> (cột Pink Sheet, số thập phân, dải hợp lệ để bắt lỗi parse)
# (mirror rebuild_commodity_wb.py:MAP + thêm sanity band)
MAP = {
    "iron_ore": ("Iron ore, cfr spot", 2, (20, 400)),    # $/dmtu
    "urea":     ("Urea ",              2, (50, 1500)),    # $/mt (lưu ý dấu cách cuối header WB)
    "dap":      ("DAP",                2, (100, 1500)),   # $/mt
    "rubber":   ("Rubber, RSS3",       3, (0.5, 12)),     # $/kg (8L dùng RSS3)
    "sugar":    ("Sugar, world",       3, (0.05, 1.5)),   # $/kg
    "brent":    ("Crude oil, Brent",   2, (10, 300)),     # $/bbl
}

UA = {"User-Agent": "Mozilla/5.0 (8L-commodity-updater)"}


# ---------------------------------------------------------------------------
def discover_url():
    """Dò link xlsx Pink Sheet hiện hành từ trang World Bank (hash đổi theo tháng)."""
    try:
        import requests
        r = requests.get(WB_PAGE, headers=UA, timeout=30)
        if r.status_code == 200:
            m = re.findall(
                r'https://thedocs\.worldbank\.org/[^"\'\s]*CMO-Historical-Data-Monthly\.xlsx',
                r.text)
            if m:
                print(f"  [dò] tìm thấy link Pink Sheet: {m[0]}")
                return m[0]
            print("  [dò] không thấy link trong HTML (trang có thể render JS) -> dùng fallback.")
        else:
            print(f"  [dò] trang WB trả {r.status_code} -> dùng fallback.")
    except Exception as e:
        print(f"  [dò] lỗi {e} -> dùng fallback.")
    return FALLBACK_URL


def download_xlsx(url):
    """Tải xlsx về cache. Trả về đường dẫn file."""
    import requests
    os.makedirs(CACHE_DIR, exist_ok=True)
    dst = os.path.join(CACHE_DIR, "CMO-Historical-Data-Monthly.xlsx")
    print(f"  [tải] {url}")
    r = requests.get(url, headers=UA, timeout=120, stream=True)
    r.raise_for_status()
    tmp = dst + ".part"
    with open(tmp, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    size = os.path.getsize(tmp)
    if size < 50_000:  # file thật ~vài trăm KB; quá nhỏ = trang lỗi/HTML
        os.remove(tmp)
        raise RuntimeError(f"file tải về quá nhỏ ({size} bytes) — có thể là trang lỗi, không phải xlsx.")
    os.replace(tmp, dst)
    print(f"  [tải] OK {size//1024} KB -> {dst}")
    return dst


def parse_pink_sheet(xlsx):
    """Đọc xlsx -> dict {name: DataFrame[month,price]} đã round + cắt từ START."""
    df = pd.read_excel(xlsx, sheet_name="Monthly Prices", skiprows=4, header=0)
    mcol = df.columns[0]
    data = df.iloc[1:].copy()                          # bỏ dòng đơn vị
    data["ym"] = data[mcol].astype(str).str.replace("M", "-", regex=False)  # 2006M04 -> 2006-04
    src_first, src_last = data["ym"].dropna().iloc[0], data["ym"].dropna().iloc[-1]
    print(f"  [parse] Pink Sheet phủ {src_first} -> {src_last}")
    frames = {}
    for name, (col, dp, _band) in MAP.items():
        if col not in df.columns:
            print(f"  [!] {name}: KHÔNG thấy cột WB '{col}' — bỏ qua (header WB có thể đổi).")
            continue
        s = data[["ym", col]].copy()
        s[col] = pd.to_numeric(s[col], errors="coerce")
        s = s.dropna()
        s = s[s["ym"] >= START]
        out = s.rename(columns={"ym": "month", col: "price"})
        out["price"] = out["price"].round(dp)
        frames[name] = out.reset_index(drop=True)
    return frames, (src_first, src_last)


def validate(name, new_df):
    """Kiểm tra hợp lệ trước khi ghi đè. Trả (ok, [lỗi])."""
    errs = []
    band = MAP[name][2]
    if new_df.empty:
        return False, ["rỗng"]
    if not new_df["month"].str.match(r"^\d{4}-\d{2}$").all():
        errs.append("định dạng month sai")
    months = new_df["month"].tolist()
    if months != sorted(months):
        errs.append("month không tăng dần")
    if new_df["month"].duplicated().any():
        errs.append("month trùng")
    p = pd.to_numeric(new_df["price"], errors="coerce")
    if p.isna().any():
        errs.append("có price NaN")
    elif (p <= 0).any():
        errs.append("có price <= 0")
    elif p.min() < band[0] or p.max() > band[1]:
        errs.append(f"price ngoài dải hợp lệ {band} (min={p.min()}, max={p.max()}) — nghi sai cột")
    return (len(errs) == 0), errs


def existing_last(path):
    """(last_month, n_rows) của file hiện có, hoặc (None,0)."""
    if not os.path.exists(path):
        return None, 0
    try:
        d = pd.read_csv(path)
        return str(d["month"].iloc[-1]), len(d)
    except Exception:
        return None, 0


def write_atomic(path, df):
    """Ghi an toàn: backup .bak rồi atomic replace."""
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")
    fd, tmp = tempfile.mkstemp(suffix=".csv", dir=os.path.dirname(path))
    os.close(fd)
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Chỉ báo cáo, không ghi file")
    ap.add_argument("--url", default="", help="Ép dùng URL xlsx cụ thể")
    ap.add_argument("--xlsx", default="", help="Dùng file xlsx đã tải sẵn (bỏ qua bước tải)")
    args = ap.parse_args()

    print("=" * 74)
    print(f" AUTO-UPDATE COMMODITY (World Bank Pink Sheet)  {datetime.now():%Y-%m-%d %H:%M}")
    print("=" * 74)

    # 1) Lấy xlsx
    try:
        if args.xlsx:
            xlsx = args.xlsx
            print(f"  [xlsx] dùng file offline: {xlsx}")
            if not os.path.exists(xlsx):
                print("  [LỖI] file xlsx không tồn tại."); sys.exit(2)
        else:
            url = args.url or discover_url()
            xlsx = download_xlsx(url)
    except Exception as e:
        print(f"\n  [LỖI] không lấy được xlsx: {e}")
        print("        -> giữ nguyên file cũ (không ghi đè). Có thể tải tay rồi chạy --xlsx <path>.")
        sys.exit(1)

    # 2) Parse
    try:
        frames, _cov = parse_pink_sheet(xlsx)
    except Exception as e:
        print(f"\n  [LỖI] parse xlsx thất bại: {e} -> giữ nguyên file cũ.")
        sys.exit(1)

    # 3) Validate + so sánh + ghi
    print("\n" + "-" * 74)
    updated, skipped, unchanged = [], [], []
    for name in MAP:
        path = os.path.join(DATA_DIR, f"{name}_monthly.csv")
        if name not in frames:
            print(f"  {name:<10} [BỎ QUA] không có dữ liệu từ WB"); skipped.append(name); continue
        new_df = frames[name]
        ok, errs = validate(name, new_df)
        if not ok:
            print(f"  {name:<10} [TỪ CHỐI] {', '.join(errs)} -> giữ file cũ"); skipped.append(name); continue

        old_last, old_n = existing_last(path)
        new_last, new_n = str(new_df["month"].iloc[-1]), len(new_df)

        # bảo vệ: không lùi tháng, không thu nhỏ chuỗi
        if old_last and new_last < old_last:
            print(f"  {name:<10} [TỪ CHỐI] WB last {new_last} < file cũ {old_last} (lùi tháng) -> giữ cũ")
            skipped.append(name); continue
        if old_n and new_n < old_n - 1:
            print(f"  {name:<10} [TỪ CHỐI] chuỗi mới ngắn hơn nhiều ({new_n} < {old_n}) -> giữ cũ")
            skipped.append(name); continue

        delta = f"{old_last or '∅'} -> {new_last}"
        new_val = new_df["price"].iloc[-1]
        if old_last == new_last:
            # cùng tháng cuối: chỉ ghi nếu WB ĐÃ REVISE giá trị (lệch ngoài làm tròn)
            old_val = None
            try:
                old_val = float(pd.read_csv(path)["price"].iloc[-1])
            except Exception:
                pass
            if old_val is not None and abs(old_val - float(new_val)) < 10 ** (-MAP[name][1]):
                print(f"  {name:<10} [=]  đã mới nhất ({new_last}={new_val})"); unchanged.append(name)
                continue
            # giá tháng cuối bị revise -> rơi xuống nhánh ghi bên dưới
            delta = f"{new_last} (revise {old_val}->{new_val})"

        if args.dry_run:
            print(f"  {name:<10} [DRY] sẽ cập nhật {delta}  last={new_val}")
        else:
            write_atomic(path, new_df)
            print(f"  {name:<10} [OK] {delta}  last={new_val}  ({new_n} tháng)")
        updated.append(name)

    # 4) Tổng kết
    print("-" * 74)
    print(f"  Cập nhật: {len(updated)} {updated}")
    print(f"  Đã mới  : {len(unchanged)} {unchanged}")
    if skipped:
        print(f"  Bỏ qua  : {len(skipped)} {skipped}")
    print("  ⚠️  caustic_soda KHÔNG cập nhật (World Bank không có series xút — vẫn ước lượng, low-confidence).")
    if args.dry_run:
        print("\n  (DRY-RUN: chưa ghi file nào. Bỏ --dry-run để cập nhật thật.)")
    elif updated:
        print("\n  Gợi ý: chạy lại cyclical_structural.py để refresh verdict ngành theo giá mới.")


if __name__ == "__main__":
    main()
