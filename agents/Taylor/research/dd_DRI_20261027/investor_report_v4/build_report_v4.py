"""Báo cáo DD nhà đầu tư DRI — dữ liệu đến 03/11/2026. Khuôn PDF/HTML + hình không-định-giá dùng lại từ
../investor_report_v3/build_report.py (import, không sửa). Hình định giá dựng lại từ số đã khoá md5:
../r5/calc/dri_model_r5_out.json, grid_r5.csv, liquidity_r5_out.json (LOCK_md5_r5.txt).
Chạy:  python3 build_report_v4.py [figs|pdf|all]
"""
import os, sys, json, importlib.util, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
CALC = os.path.abspath(os.path.join(HERE, "../r5/calc"))
spec = importlib.util.spec_from_file_location("b3", os.path.join(HERE, "../investor_report_v3/build_report.py"))
b3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b3)
b3.HERE, b3.FIGS = HERE, FIGS
# trang PDF: thay dòng đầu trang của khuôn cũ bằng ngày dữ liệu của bản này
import inspect, textwrap as _tw
_src = _tw.dedent(inspect.getsource(b3.pdf)).replace("Báo cáo Due Diligence · 30/10/2026 (v3)", "Báo cáo Due Diligence · dữ liệu đến 03/11/2026")
assert "dữ liệu đến 03/11/2026" in _src
exec(compile(_src, "b3_pdf_v4", "exec"), b3.__dict__)
NAVY, ACCENT, GREY, LIGHT, vn, save = b3.NAVY, b3.ACCENT, b3.GREY, b3.LIGHT, b3.vn, b3.save

M = json.load(open(os.path.join(CALC, "dri_model_r5_out.json")))
LQ = json.load(open(os.path.join(CALC, "liquidity_r5_out.json")))
F5 = 1 - LQ["pos"]["5"]["disc"]["Y1.0"]
CLOSE_0311 = LQ["price"]       # 13.400 đóng cửa 03/11/2026, DNSE ohlc 1D (dd_audit_newproject_20261103/close_20261103.md) — CHỈ dùng sau khoá
SC = M["scale"]; C = M["center"]; FORCED = M["forced"]
# kịch bản (trình bày): hỗn hợp 80% lưới cơ sở NPV-0 + 20% tái canh bị buộc (xác suất = nhận định); dải = P25–P75 từng lưới
import csv
grid = list(csv.DictReader(open(os.path.join(CALC, "grid_r5.csv"))))
SF, SL = M["scale_forced"], M["scale_liqread"]
SCEN = [("Cơ sở", 0.80, SC["P25"], SC["P75"], "vườn hiện hữu + tiền ròng; tái canh/dự án mới ở giá vốn"),
        ("Tái canh bị buộc", 0.20, SF["P25"], SF["P75"], "thanh lý + trồng lại với kinh tế dự án thận trọng")]
EXPW = M["expected"]["0.2"]     # (1-0,2) x TB lưới cơ sở + 0,2 x TB lưới bị buộc


def engine_paths():
    ENG = os.path.abspath(os.path.join(HERE, "../../dri_val_supply_adj_r4_20261027/model.py"))
    import builtins
    WC = "/home/trido/thanhdt/WorkingClaude/data"
    RD = {f"{WC}/rubber_monthly.csv": os.path.join(CALC, "data/rubber_monthly_snapshot_20261103.csv"),
          f"{WC}/macro_usdvnd.csv": os.path.join(CALC, "data/macro_usdvnd_snapshot_20261103.csv")}
    ns = {"__file__": ENG, "__name__": "eng", "open": lambda p, *a, **k: builtins.open(RD.get(os.path.abspath(str(p)), p), *a, **k)}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(open(ENG, encoding="utf-8").read(), ENG, "exec"), ns)
    yrs = list(range(2026, 2055))
    out = {}
    for L in (22, 27, 32):
        v, _ = ns["build3"](2029, L, R_on=False, new_on=False); out[f"hien_huu_L{L}"] = [v[y][0] for y in yrs]
    v, _ = ns["build3"](2029, 27); out["co_tai_canh_TB_L27"] = [v[y][0] for y in yrs]
    return yrs, out


def figs_new():
    import numpy as np, pandas as pd
    import matplotlib.patches as mp
    plt = b3.setup_mpl()
    # 7. sản lượng
    yrs, P = engine_paths()
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.fill_between(yrs, P["hien_huu_L22"], P["hien_huu_L32"], color=LIGHT, alpha=0.8, label="Vườn hiện hữu, đời cạo 22–32 năm")
    ax.plot(yrs, P["hien_huu_L27"], color=NAVY, lw=2.0, label="Vườn hiện hữu, đời cạo 27 năm (đường định giá)")
    ax.plot(yrs, P["co_tai_canh_TB_L27"], color=ACCENT, lw=1.4, ls="--", label="Nếu tái canh 4.082 ha (2029–36): sản lượng cây mới từ năm 7")
    ax.set_ylim(0, 15500); ax.set_ylabel("tấn mủ tự khai thác/năm"); ax.yaxis.set_major_formatter(lambda v, p: vn(v, 0))
    ax.legend(fontsize=6.9, frameon=False, loc="lower left")
    ax.set_title("Định giá dựa trên vườn đang cạo: sản lượng giảm dần khi các lớp tuổi hết đời cạo")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_07_production_paths", "Nguồn: mô hình của nhóm (ước lượng) dựng từ 8.166 ha đang cạo (KH 2026: 13.800 t / 1,69 t/ha, BCTN 2025), "
         "phân bố năm mở cạo suy từ mốc '2015: 80% diện tích đã khai thác'. Đường tái canh chỉ minh hoạ; giá trị dự án tái canh tính ở giá vốn.",
         pd.DataFrame({"nam": yrs, **P}))
    plt.close(fig)

    # 8. giá 12 tháng tới 03/11
    px = pd.read_csv(os.path.join(CALC, "bq_liq_dri_20261103.csv"), parse_dates=["time"])
    px = px[(px["time"] >= "2025-11-03") & (px["time"] <= "2026-11-02")].reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.7), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    a1.plot(px["time"], px["Close"], color=NAVY, lw=1.3)
    a1.plot(pd.Timestamp("2026-11-03"), CLOSE_0311, "o", color=ACCENT, ms=5)
    a1.annotate("03/11: 13.400", (pd.Timestamp("2026-11-03"), CLOSE_0311), xytext=(pd.Timestamp("2026-06-01"), 11500),
                fontsize=7, color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.6))
    a1.set_ylabel("đ/cp (điều chỉnh)"); a1.yaxis.set_major_formatter(lambda v, p: vn(v, 0))
    a2.bar(px["time"], px["Volume"]/1e6, color=GREY, width=1.0); a2.set_ylabel("KL, triệu cp")
    a1.set_title("Giá 12 tháng: đỉnh 16.900 (09/10/2026), 13.400 ngày 03/11")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_price_12m", "Nguồn: dữ liệu giao dịch (Close điều chỉnh cổ tức, Volume) 03/11/2025–02/11/2026; điểm 03/11: đóng cửa DNSE.",
         px[["time", "Close", "Price", "Volume"]])
    plt.close(fig)

    # 19. RSS3 thực
    rs = pd.read_csv(os.path.join(CALC, "data/rubber_monthly_snapshot_20261103.csv"))
    cpi = pd.read_csv(os.path.join(CALC, "data/fred_cpiaucsl_20261103.csv"))
    cpi["month"] = cpi["observation_date"].str[:7]; cpi = cpi[cpi["CPIAUCSL"].astype(str).str.len() > 0]
    cpi["CPIAUCSL"] = pd.to_numeric(cpi["CPIAUCSL"], errors="coerce")
    d = rs.merge(cpi[["month", "CPIAUCSL"]], on="month", how="left")
    d["CPIAUCSL"] = d["CPIAUCSL"].interpolate()
    c25 = d.loc[d["month"].str.startswith("2025"), "CPIAUCSL"].mean()
    d["real_2025usd"] = d["price"] * c25 / d["CPIAUCSL"]
    d["t"] = pd.to_datetime(d["month"])
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.plot(d["t"], d["price"], color=GREY, lw=1.0, label="RSS3 danh nghĩa")
    ax.plot(d["t"], d["real_2025usd"], color=NAVY, lw=1.5, label="RSS3 theo sức mua USD 2025")
    for k, lab, c, ls in (("P25", "phân vị 25% thực 2014–26", "#7A8A9A", ":"), ("TB", "TB thực 2014–26 (mức giữa chu kỳ)", ACCENT, "-"),
                          ("P75", "phân vị 75% thực 2014–26", "#2E7D5B", "--")):
        ax.axhline(M["mids"][k], color=c, ls=ls, lw=1.2, label=f"{lab}: {M['mids'][k]:.2f} $/kg".replace(".", ","))
    ax.set_ylabel("USD/kg"); ax.legend(fontsize=6.7, frameon=False, loc="upper right")
    ax.set_title(f"Giá cao su quý 3/2026 (2,75 $/kg) cao hơn mức giữa chu kỳ thực {vn(M['mids']['TB'], 2)} $/kg khoảng {(M['rssq3']/M['mids']['TB']-1)*100:.0f}%")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_19_rss3_10y", "Nguồn: World Bank Pink Sheet (RSS3 tháng, 04/2006–09/2026); CPI-U Mỹ (FRED CPIAUCSL; 10/2025 không công bố, nội suy).",
         d[["month", "price", "real_2025usd"]])
    plt.close(fig)

    # 9. football field (sau chiết khấu thanh khoản 5 tỷ)
    gv = {k: float(v) for k, v in [(f'{g["mid"]}|{g["L"]}|{g["r"]}', g["v"]) for g in grid]}
    rows = [("Thang giá trị (lưới 27 bộ giả định) P10–P90", SC["P10"]*F5, SC["P90"]*F5, C*F5),
            ("Giá cao su giữa chu kỳ: P25 → P75 (2014–26)", gv["P25|27|0.135"]*F5, gv["P75|27|0.135"]*F5, C*F5),
            ("Đời cạo vườn hiện hữu 22 → 32 năm (giả định)", gv["TB|22|0.135"]*F5, gv["TB|32|0.135"]*F5, C*F5),
            ("Chi phí vốn 11,5% → 15,5%", gv["TB|27|0.155"]*F5, gv["TB|27|0.115"]*F5, C*F5),
            ("Cách đọc khác: thanh lý 2029–36 không trồng lại", SL["P25"]*F5, SL["P75"]*F5, M["center_liqread"]*F5),
            ("Tái canh bị buộc, kinh tế thận trọng (P25–P75)", SF["P25"]*F5, SF["P75"]*F5, None),
            ("Giá cao su 2027–28 về 1,60 $/kg", M["trough_stress"]*F5, M["trough_stress"]*F5 + 1, None)]
    ff = pd.DataFrame(rows, columns=["phuong_phap", "thap", "cao", "diem_giua"])
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    for i, r in ff.iterrows():
        yy = len(ff) - 1 - i
        c = ACCENT if i == 0 else (GREY if i >= 5 else ("#7A8A9A" if i == 4 else NAVY))
        ax.barh(yy, max(r["cao"] - r["thap"], 120), left=r["thap"], color=c, height=0.5, alpha=0.85)
        ax.text(r["thap"] - 250, yy, vn(r["thap"]/1e3), ha="right", va="center", fontsize=7.5)
        if r["cao"] - r["thap"] > 200:
            ax.text(r["cao"] + 250, yy, vn(r["cao"]/1e3), ha="left", va="center", fontsize=7.5)
        if r["diem_giua"] is not None and r["diem_giua"] == r["diem_giua"]:
            ax.plot(r["diem_giua"], yy, "|", color="white", ms=14, mew=2)
    ax.set_yticks(range(len(ff)), ff["phuong_phap"][::-1], fontsize=7.4)
    ax.axvline(CLOSE_0311, color=NAVY, ls="--", lw=1.1, label="Đóng cửa 03/11: 13,4k")
    ax.legend(fontsize=7, frameon=True, framealpha=0.95, loc="lower right")
    ax.set_xlim(6000, 22000); ax.set_xlabel("đồng/cổ phiếu, sau chiết khấu thanh khoản 2,0% (vị thế 5 tỷ đ)")
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title(f"Giá 13,4k sát cận dưới vùng hợp lý ({vn(SC['P25']*F5/1e3)}k); trung tâm {vn(C*F5/1e3)}k")
    ax.set_xticks(range(6000, 22001, 2000))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_09_football_field", f"Nguồn: mô hình của nhóm (ước lượng), khoá trước khi so với giá. Vạch trắng = giá trị trung tâm {vn(C*F5/1e3)}k. "
         "Mỗi dòng đổi MỘT giả định quanh trung tâm; hai dòng xám là kịch bản/cách đọc khác, không thuộc thang.", ff)
    plt.close(fig)

    # 21. kịch bản
    df = pd.DataFrame([(a, p, lo*F5, hi*F5, g) for a, p, lo, hi, g in SCEN], columns=["kich_ban", "xac_suat", "thap", "cao", "gia_dinh"])
    fig, ax = plt.subplots(figsize=(7.2, 2.0))
    cols = [NAVY, ACCENT]
    for i, r in df.iterrows():
        yy = len(df) - 1 - i
        ax.barh(yy, r["cao"] - r["thap"], left=r["thap"], color=cols[i], height=0.5, alpha=0.85)
        ax.text(r["thap"] - 200, yy, vn(r["thap"]/1e3), ha="right", va="center", fontsize=7.5)
        ax.text(r["cao"] + 200, yy, vn(r["cao"]/1e3), ha="left", va="center", fontsize=7.5)
    ax.set_yticks(range(len(df)), [f"{k} · {int(p*100)}%" for k, p in zip(df["kich_ban"][::-1], df["xac_suat"][::-1])], fontsize=8)
    ax.axvline(CLOSE_0311, color=NAVY, ls="--", lw=1.1, label="Đóng cửa 03/11: 13,4k")
    ax.axvline(EXPW*F5, color="#999", lw=1.0, label=f"Bình quân theo xác suất ~{vn(EXPW*F5/1e3)}k")
    ax.legend(fontsize=6.8, frameon=True, framealpha=0.95, loc="lower right")
    ax.set_xlim(8000, 20000); ax.set_xticks(range(8000, 20001, 2000)); ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); ax.set_xlabel("đồng/cổ phiếu, sau chiết khấu thanh khoản")
    ax.set_title("Giá hiện tại nằm giữa kịch bản tái canh bị buộc và kịch bản cơ sở")
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    df["binh_quan"] = EXPW*F5
    save(fig, "fig_21_scenarios", "Nguồn: mô hình của nhóm (ước lượng). Dải = P25–P75 của lưới 27 bộ giả định mỗi kịch bản. Xác suất 80/20 là nhận định của nhóm, "
         "không ước lượng từ dữ liệu; bình quân = 0,8 × TB lưới cơ sở + 0,2 × TB lưới tái canh bị buộc.", df)
    plt.close(fig)

    # 22. lãi huy động + thanh khoản
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.7))
    s1 = M["dep_sens"]["1.0"]; xs = [-100, -50, 0, 50, 100]
    a1.bar([str(x) for x in xs], [s1[str(x)]*F5/1e3 for x in xs], color=[("#2E7D5B" if x < 0 else (NAVY if x == 0 else ACCENT)) for x in xs])
    for i, x in enumerate(xs):
        a1.text(i, s1[str(x)]*F5/1e3 + 0.1, vn(s1[str(x)]*F5/1e3), ha="center", fontsize=7)
    a1.set_ylim(14, 18.5); a1.set_xlabel("thay đổi lãi huy động 12T (điểm cơ bản)"); a1.set_ylabel("nghìn đ/cp")
    a1.set_title("Lãi huy động ±100bp ⇒ giá trị ∓3%", fontsize=8.4)
    qs = ["1", "5", "10"]
    a2.bar([f"{q} tỷ" for q in qs], [LQ["pos"][q]["disc"]["Y1.0"]*100 for q in qs], color=NAVY)
    for i, q in enumerate(qs):
        a2.text(i, LQ["pos"][q]["disc"]["Y1.0"]*100 + 0.05, f'{LQ["pos"][q]["disc"]["Y1.0"]*100:.1f}% · {LQ["pos"][q]["days15"]:.0f} phiên'.replace(".", ","), ha="center", fontsize=6.8)
    a2.set_ylabel("chiết khấu thanh khoản, %"); a2.set_title("Chiết khấu theo quy mô vị thế", fontsize=8.4); a2.set_ylim(0, 3.6)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, "fig_22_rate_liquidity", "Nguồn: mô hình của nhóm; lãi huy động 12T neo 7,40% (02/11/2026), r = 13,5% + 1 × thay đổi. Thanh khoản: "
         "dữ liệu giao dịch 250 phiên tới 02/11/2026, giá trị khớp trung vị 8,33 tỷ đ/phiên, biến động ngày 2,58%; số phiên thoát ở 15% khối lượng.",
         pd.DataFrame({"bp": xs, "gia_tri_sau_ck": [s1[str(x)]*F5 for x in xs]}))
    plt.close(fig)

    # 0. hero
    fig = plt.figure(figsize=(7.2, 3.15)); fig.patch.set_facecolor("white")
    band = fig.add_axes([0, 0.86, 1, 0.14]); band.axis("off")
    band.add_patch(mp.Rectangle((0, 0), 1, 1, fc=NAVY, transform=band.transAxes))
    band.text(0.015, 0.5, "DRI · Cao su thiên nhiên tại Nam Lào", color="white", fontsize=10.5, fontweight="bold", va="center")
    band.text(0.985, 0.5, "Giá 13,4k: sát cận dưới vùng hợp lý", color="white", fontsize=10, fontweight="bold", va="center", ha="right",
              bbox=dict(boxstyle="round,pad=0.3", fc=ACCENT, ec="none"))
    a = fig.add_axes([0.0, 0.17, 0.27, 0.68]); a.axis("off"); a.set_xlim(0, 3); a.set_ylim(0, 3.2)
    for (x, s) in ((0.55, 0.85), (1.45, 1.05), (2.4, 0.85)):
        b3._tree(a, x, 0.75, s)
    a.plot([0.05, 2.95], [0.75, 0.75], color="#B9C3CE", lw=1.2)
    a.text(1.5, 0.42, "8.592 ha cao su", ha="center", fontsize=9.2, fontweight="bold", color=NAVY)
    a.text(1.5, 0.2, "Champasak & Salavan (Lào)\nnhà máy 18.000 t/năm", ha="center", va="top", fontsize=6.8, color="#333")
    a.text(0.05, 3.1, "1 · NGÀNH NGHỀ", fontsize=7.6, fontweight="bold", color=ACCENT)
    bb = fig.add_axes([0.335, 0.2, 0.31, 0.50])
    bb.bar([2025], [15152.83], color=NAVY, width=1.6)
    bb.plot(yrs, P["hien_huu_L27"], color=ACCENT, lw=2.0); bb.fill_between(yrs, 0, P["hien_huu_L27"], color=ACCENT, alpha=0.10)
    bb.set_ylim(0, 17500); bb.set_xlim(2023.5, 2055); bb.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    bb.tick_params(labelsize=6.5); bb.set_ylabel("tấn mủ/năm", fontsize=6.8)
    fig.text(0.335, 0.83, "2 · TĂNG TRƯỞNG", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.335, 0.81, "LNST 9T/26 +43,6%, tiền ròng 237 tỷ;\nvườn hiện hữu giảm dần theo tuổi", fontsize=6.4, color="#333", va="top")
    c = fig.add_axes([0.70, 0.14, 0.24, 0.55]); c.set_xlim(0, 1); c.set_ylim(9000, 21000); c.grid(False)
    for sp in ("left", "bottom"):
        c.spines[sp].set_visible(False)
    c.set_xticks([]); c.yaxis.tick_right(); c.tick_params(labelsize=6.5); c.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    c.add_patch(mp.Rectangle((0.15, SC["P10"]*F5), 0.5, (SC["P90"]-SC["P10"])*F5, fc=ACCENT, alpha=0.18, ec="none"))
    c.add_patch(mp.Rectangle((0.15, SC["P25"]*F5), 0.5, (SC["P75"]-SC["P25"])*F5, fc=ACCENT, alpha=0.85, ec="none"))
    c.text(0.4, (SC["P25"]+SC["P75"])/2*F5, f"giá trị\nhợp lý\n{vn(SC['P25']*F5/1e3)}–{vn(SC['P75']*F5/1e3)}k", ha="center", va="center", fontsize=6.4, color="white", fontweight="bold")
    c.axhline(CLOSE_0311, xmin=0.02, xmax=0.98, color=NAVY, lw=1.6)
    c.text(0.02, CLOSE_0311 - 900, "Giá 13,4k (03/11)", fontsize=6.6, color=NAVY, fontweight="bold")
    fig.text(0.69, 0.83, "3 · ĐỊNH GIÁ", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.69, 0.81, f"sau chiết khấu thanh khoản;\ntâm {vn(C*F5/1e3)}k", fontsize=6.4, color="#333", va="top")
    b3.foot(fig, "Nguồn: BCTN 2025; BCTC HN Q3/2026; mô hình của nhóm (ước lượng; vườn hiện hữu, giá cao su giữa chu kỳ thực " + vn(M["mids"]["TB"], 2) + " $/kg, r 13,5%); "
               "vùng đậm = P25–P75, nhạt = P10–P90 sau chiết khấu thanh khoản 2,0%; giá: đóng cửa DNSE 03/11/2026.")
    fig.savefig(os.path.join(FIGS, "fig_00_hero.png"), dpi=200)
    pd.DataFrame([("tam_sau_ck", C*F5), ("p10_sau_ck", SC["P10"]*F5), ("p25_sau_ck", SC["P25"]*F5), ("p75_sau_ck", SC["P75"]*F5),
                  ("p90_sau_ck", SC["P90"]*F5), ("dong_cua_0311", CLOSE_0311)], columns=["chi_tieu", "gia_tri"]).to_csv(os.path.join(FIGS, "fig_00_hero.csv"), index=False)
    plt.close(fig)
    json.dump(dict(F5=F5, EXPW=EXPW, EXPW_after=EXPW*F5, scen=[(a, p, lo, hi) for a, p, lo, hi, _ in SCEN]),
              open(os.path.join(HERE, "scenarios_v4.json"), "w"), indent=1)
    print(f"EXPW {EXPW:,.0f} -> sau CK {EXPW*F5:,.0f}; tam sau CK {C*F5:,.0f}; P10..P90 sau CK " + " / ".join(f"{SC[k]*F5:,.0f}" for k in SC))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("figs", "all"):
        figs_new()
    if mode in ("pdf", "all"):
        b3.pdf(os.path.join(HERE, "DRI_DD_investor_report_20261103.md"), os.path.join(HERE, "DRI_DD_investor_report_20261103.pdf"))
