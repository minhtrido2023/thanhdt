#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""basket_price_basis_selfcheck.py — cổng bắt buộc của bản sửa "tách vai cơ sở giá" trong
`custom_basket.py` (job Taylor_20260802_141725, commit ebeacad).

Bốn câu hỏi, không hơn — theo đúng `.claude/skills/quant-research/SKILL.md` bước 9 (two-way
self-check) + bước 7 (control leg phải tái lập ĐÚNG số cũ):

  T1. ĐỒNG NHẤT THỨC (mạnh nhất): ép `mcapw == mcap` (pxw := Close) VÀ revert chuỗi return về
      `mcap` (`BASKET_RETURN_OSHARES=legacy`, thêm 2026-09-27) trong module MỚI → chuỗi
      level PHẢI trùng BIT-FOR-BIT với module TRƯỚC KHI SỬA. Chứng minh việc viết lại
      SUM(mcap_t)/SUM(mcap_{t-1})-1  →  SUM(w*r)/SUM(w) không hề đổi đại số.
      Nếu T1 fail = refactor sai, mọi số A/B sau đó vô nghĩa.
  T2. PARITY NGÀY GẦN ĐÂY (Price≈Close, hệ số điều chỉnh ~1,00): rổ + level MỚI vs CŨ phải
      gần như không đổi. Lệch lớn ở đây = đã làm hỏng thứ khác.
  T3. POSITIVE CONTROL NGÀY CŨ (hệ số điều chỉnh xa 1,00): PHẢI có khác biệt THẬT.
      0 diff ở đây = bản "sửa" không làm gì cả, chẩn đoán sai.
  T4. AN TOÀN CỔ TỨC: ngày chốt quyền KHÔNG được biến thành khoản lỗ giả — kiểm cơ sở giá
      ĐIỀU CHỈNH vẫn nằm đúng chỗ. ⚠️ Từ 2026-09-27 (job Taylor_20260927_022253) T4 KHÔNG còn
      đọc `mcap` như bằng chứng về chân return: chuỗi return đã chuyển sang `Close` THUẦN, nên
      đồng nhất thức `mcap/mcapw == Close/Price` chỉ còn nói về 2 CỘT EXPORT (vẫn đúng, vẫn phải
      giữ), không nói gì về chân return. Phần "chân return nằm trên Close" được kiểm TRỰC TIẾP
      trên chuỗi return ở T4c dưới đây, và đầy đủ ở
      `basket_return_leg_oshares_selfcheck.py` (R1/R3/R5). Đây chính là lỗi §28 mà luật fleet
      cấm: đừng suy ra trạng thái của A từ một kênh B đã thôi điều khiển A.

T2/T3 cùng nhau là điều kiện CẦN VÀ ĐỦ: một mình T2 không phân biệt "sửa đúng" với "no-op",
một mình T3 không phân biệt "sửa đúng" với "làm hỏng".

Chạy:  cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
       BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate $DNA_PYEXE basket_price_basis_selfcheck.py
"""
import os
import subprocess
import sys
import types

# WORKDIR = cay chua CHINH file selfcheck nay, KHONG hardcode canonical.
# Vi sao (Mike vá 2026-09-27 truoc khi merge): ban dau mac dinh la
# "/home/trido/thanhdt/WorkingClaude" + env override. Do thuc: chay tu worktree
# /home/trido/thanhdt/wt-faileg-proposal (da co ban va) thi T5 bao FAIL 2 vi pham vi no quet
# MAIN chua va; set BASKET_SELFCHECK_WORKDIR tro dung worktree moi PASS. Tuc mac dinh hardcode
# lam cong NAY VO HIEU o moi worktree — dung luc can nhat (luc review mot branch). Cung lop
# "bay duong dan selfcheck" da va o compute_active_nav_selfcheck.py (commit a56203f2).
# Env override GIU LAI cho sandbox, nhung mac dinh gio tu doi theo vi tri file.
WORKDIR = os.environ.get("BASKET_SELFCHECK_WORKDIR") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# Cấu hình PRODUCTION của rổ custom30V (= ETF_LIQ=custompitg + BASKET_WT=namecap của lệnh pin R3).
PROD_KW = dict(quality="none", rebal="q2m5", gate_rating=3, weight_scheme="namecap")
# Cửa sổ GẦN ĐÂY: hệ số Close/Price ~1,00 (trung vị 1,000 năm 2026) -> kỳ vọng parity.
RECENT = ("2025-01-02", "2026-06-19")
# Cửa sổ CŨ: hệ số Close/Price xa 1,00 (trung vị 0,448 năm 2014) -> kỳ vọng khác biệt THẬT.
# 2014 là mốc sớm nhất `universe_pit_q`/engine R3 phủ; pre-2014 ngoài tầm phủ của build_pit.
OLD = ("2014-01-02", "2016-12-30")
FAILS = []


def check(name, cond, detail=""):
    print(f"  [{'ok' if cond else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}", flush=True)
    if not cond:
        FAILS.append(name)


def _bq():
    """bq() của engine — tôn trọng BQ_LOCAL_CACHE (đường chạy của lệnh pin R3)."""
    import simulate_holistic_nav as shn
    return shn.bq


def _load(src, tag):
    m = types.ModuleType(f"custom_basket_{tag}")
    m.__file__ = os.path.join(WORKDIR, "custom_basket.py")
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


def load_pre_edit(ref="ebeacad^"):
    """Module TRƯỚC bản sửa tách vai (mcap = Close*OShares dùng cho CẢ return lẫn weight)."""
    src = subprocess.run(["git", "show", f"{ref}:./custom_basket.py"], cwd=WORKDIR,
                         capture_output=True, text=True, check=True).stdout
    return _load(src, "preedit")


def load_post_edit(force_close_basis=False):
    """Module SAU bản sửa. force_close_basis=True ép TOÀN BỘ cơ sở giá về `Close` — cả chân
    WEIGHT (pxw) LẪN chân SELECTION (liquidity) — nên module mới phải suy biến về ĐÚNG hành vi
    tiền-sửa. Phải revert CẢ HAI: bản control chỉ revert pxw vẫn đổi rổ (bài học lần chạy đầu:
    T1 fail vì control thiếu chân selection, KHÔNG phải vì code sai)."""
    src = open(os.path.join(WORKDIR, "custom_basket.py")).read()
    m = _load(src, "postedit_ctl" if force_close_basis else "postedit")
    # Dùng ĐÚNG knob production (`BASKET_PRICE_BASIS`) thay vì vá chuỗi SQL: control leg phải đi
    # qua CHÍNH đường code mà lệnh A/B của Bước 4 sẽ chạy, nếu không T1 chỉ chứng minh cho một
    # phiên bản không ai chạy. `pxw_sql()` đọc env tại thời điểm gọi nên set ở đây là đủ.
    m._SC_BASIS = "legacy" if force_close_basis else "split"
    # Chân return cũng phải revert trong control leg (thêm 2026-09-27, job Taylor_20260927_022253).
    # T1 đòi trùng BIT-FOR-BIT với `ebeacad^`, mà giữa `ebeacad^` và HÔM NAY có HAI thay đổi, không
    # một: (1) tách vai cơ sở GIÁ 2026-08-02, (2) bỏ số CP khỏi chuỗi RETURN 2026-09-27. Control leg
    # thiếu biến thứ hai sẽ fail T1 vì chính lý do docstring đã ghi một lần rồi ("T1 fail vì control
    # thiếu chân selection, KHÔNG phải vì code sai") — không phải vì code sai.
    m._SC_RETCHAIN = "legacy" if force_close_basis else "flat"
    # BIẾN THỨ BA (Mike thêm 2026-09-27, sau khi T1 FAIL trên main): giữa `ebeacad^` và HÔM NAY có
    # BA thay đổi, không hai — thay đổi thứ ba là "OShares bước tại EX-DATE thay vì mốc quý"
    # (ticket 1, merge 5c290848). Chính lần chạy phát hiện in ra bằng chứng: "[oshares-step]
    # exdate: 119 bước OShares, 80 bước ĐƯỢC DỜI (median 40 ngày)" — control leg không revert nó
    # nên KHÔNG THỂ trùng bit-for-bit, và T1 FAIL vì ĐÚNG lý do docstring đã ghi HAI lần rồi
    # ("T1 fail vì control thiếu <một chân>, KHÔNG phải vì code sai"). Knob production:
    # custom_basket.py:216 `BASKET_OSHARES_STEP` (mặc định "exdate", legacy "quarter").
    m._SC_OSTEP = "quarter" if force_close_basis else "exdate"
    return m


def adj_factor_line(tag, raw):
    """Đo THẬT hệ số điều chỉnh Close/Price trên chính panel rổ đã lấy (sức phân giải của phép
    thử) — không suy đoán 'gần đây thì ~1,00', và không cần thêm truy vấn.
    Tính bằng pandas, KHÔNG bằng APPROX_QUANTILES: cache production là DuckDB, hàm đó chỉ có
    trên BigQuery — selfcheck phải chạy được trên đúng đường dữ liệu của lệnh pin."""
    r = raw.dropna(subset=["Close", "pxw"])
    f = (r["Close"] / r["pxw"]).replace([np.inf, -np.inf], np.nan).dropna()
    return (f"      {tag:6s} p05 {f.quantile(0.05):.3f} / p50 {f.quantile(0.50):.3f} / "
            f"p95 {f.quantile(0.95):.3f} | |f-1|>5% ở {float((f.sub(1).abs()>0.05).mean())*100:.1f}% "
            f"dòng (n={len(f):,})")


def run(mod, bq, win):
    prev = os.environ.get("BASKET_PRICE_BASIS")
    prev_rc = os.environ.get("BASKET_RETURN_OSHARES")
    prev_os = os.environ.get("BASKET_OSHARES_STEP")
    basis = getattr(mod, "_SC_BASIS", None)
    retchain = getattr(mod, "_SC_RETCHAIN", None)
    ostep = getattr(mod, "_SC_OSTEP", None)
    if basis:
        os.environ["BASKET_PRICE_BASIS"] = basis
    if retchain:
        os.environ["BASKET_RETURN_OSHARES"] = retchain
    if ostep:
        os.environ["BASKET_OSHARES_STEP"] = ostep
    try:
        lvl, adv, mem, raw = mod.build_pit(bq, win[0], win[1], **PROD_KW)
    finally:
        os.environ.pop("BASKET_PRICE_BASIS", None)
        os.environ.pop("BASKET_RETURN_OSHARES", None)
        os.environ.pop("BASKET_OSHARES_STEP", None)
        if prev is not None:
            os.environ["BASKET_PRICE_BASIS"] = prev
        if prev_rc is not None:
            os.environ["BASKET_RETURN_OSHARES"] = prev_rc
        if prev_os is not None:
            os.environ["BASKET_OSHARES_STEP"] = prev_os
    s = pd.Series(lvl).sort_index()
    mem = mem.copy()
    mem["rebal_date"] = pd.to_datetime(mem["rebal_date"])
    members = {d: sorted(g["ticker"]) for d, g in mem.groupby("rebal_date")}
    return s, members, raw


def ret_of(level):
    return level.sort_index().pct_change().dropna()


def cmp_levels(a, b):
    """So 2 chuỗi level trên phần index chung -> (max |Δ return| theo ngày, CAGR-tương-đương)."""
    ra, rb = ret_of(a), ret_of(b)
    ix = ra.index.intersection(rb.index)
    d = (ra.loc[ix] - rb.loc[ix]).abs()
    tot_a = float(a.loc[a.index.intersection(b.index)].iloc[-1] / a.loc[a.index.intersection(b.index)].iloc[0])
    tot_b = float(b.loc[a.index.intersection(b.index)].iloc[-1] / b.loc[a.index.intersection(b.index)].iloc[0])
    return float(d.max()), len(ix), tot_a, tot_b


def member_diff(ma, mb):
    ds = sorted(set(ma) & set(mb))
    per = [len(set(ma[d]) ^ set(mb[d])) // 2 for d in ds]
    return ds, per



# ── T5. GREP-GATE CƠ SỞ GIÁ (thêm 2026-09-27, audit measurement-integrity FAIL-E) ─────────
# Vì sao T1-T4 KHÔNG thay được T5: T1-T4 chỉ chạy trên `custom_basket.py`. Lỗi trộn hệ quy chiếu
# là lỗi LẶP LẠI ở nhiều call-site (đã vá `LAG_ADV_BASIS` 2026-08-02 và `custom_basket` cùng
# ngày, vẫn sót `pt_v23_audit_2014.py:895` tới 2026-09-27). Một selfcheck hành vi chỉ canh được
# nơi nó đã cắn; phần LẶP LẠI phải là cổng CƠ HỌC (coding_guidelines §Enforcement policy).
#
# Luật: trong biểu thức TIỀN / ADV / mcap-weight, KHÔNG được nhân một SỐ LƯỢNG thô
# (`Volume*`, `OShares`) với một GIÁ ĐÃ ĐIỀU CHỈNH (`Close`, `Close_T1*`). Giá đúng = `Price`
# thô, hoặc `COALESCE(Price,Close)`, hoặc `pxw_sql()`.
#
# PHẠM VI CÓ CHỦ Ý = danh sách file được BẢO VỆ, KHÔNG quét cả repo. Đo thật 2026-09-27:
# regex này khớp 2.349 dòng / 1.010 file `.py` trong repo — gần như toàn bộ là script
# `backtest_*`/`test_*` legacy mà `data/results_registry.md` không trích. Một cổng 2.349 mục là
# một cổng không ai chạy. Muốn siết dần thì thêm file vào PROTECTED, đừng mở toàn repo.
#
# Phân biệt CODE với VĂN XUÔI bằng AST, không bằng "dòng có bắt đầu bằng #":
#   - chuỗi có chứa CẢ `SELECT` lẫn `FROM` = SQL thật  -> quét
#   - chuỗi khác (nhãn báo cáo, docstring)             -> BỎ QUA
#   - biểu thức code thường (pandas `df.Close*df.Volume`) -> quét
# Nếu không có bước này thì `pt_v23:2431`/`custom_basket.py:46` (văn xuôi mô tả chính cái bug)
# sẽ bị báo và cổng lập tức mất uy tín.
import ast as _ast  # noqa: E402
import re as _re  # noqa: E402

PROTECTED = [
    "pt_v23_audit_2014.py", "pt_v22_dt5g.py", "custom_basket.py",
    "simulate_holistic_nav.py", "signal_v11_sql.py", "edge_health_monitor.py",
    "rating_8l.py", "rating_8l_history.py", "custom30v_hybrid.py",
    "bootstrap_nav.py", "dsr_pbo_annex.py", "regime_size_overlay.py",
]
_QTY = r"(?:Volume[A-Za-z0-9_]*|OShares)"
_ADJ = r"(?:Close(?:_T1W?)?)"
_PFX = r"(?:[A-Za-z_][A-Za-z0-9_]*\.)?"
BAN_RE = _re.compile(
    rf"{_PFX}{_QTY}\s*\*\s*{_PFX}{_ADJ}\b|{_PFX}{_ADJ}\s*\*\s*{_PFX}{_QTY}\b")
# `COALESCE(Price,Close)` chứa `Close` nhưng là giá THÔ đã đúng -> gỡ khỏi văn bản trước khi khớp.
SAFE_RE = _re.compile(r"COALESCE\s*\(\s*[A-Za-z_0-9.]*Price\s*,\s*[A-Za-z_0-9.]*Close\s*\)",
                      _re.IGNORECASE)


# Điều kiện thứ HAI, bắt buộc: chính DÒNG vi phạm phải trông như SQL/biểu thức, không phải văn
# xuôi. Chỉ đòi "chuỗi bao quanh có SELECT+FROM" là KHÔNG đủ — docstring của `custom_basket.py`
# vừa mô tả chính cái bug này vừa trích SQL, nên 3 dòng VĂN XUÔI (`:35`, `:46`, `:58`) bị báo ở
# vòng thử đầu. Từ khoá cố ý phân biệt HOA/thường: SQL viết `AND`, văn xuôi viết `and`.
SQLLINE_RE = _re.compile(
    r"\b(SELECT|FROM|WHERE|GROUP BY|ORDER BY|HAVING|AND|OR|AVG|SUM|CAST|COALESCE|OVER)\b")


def _sql_string_hits(src):
    """Trả (lineno, text) cho mọi vi phạm nằm trong chuỗi TRÔNG NHƯ SQL."""
    hits = []
    tree = _ast.parse(src)
    for node in _ast.walk(tree):
        if not (isinstance(node, _ast.Constant) and isinstance(node.value, str)):
            continue
        v = node.value
        if not ("SELECT" in v.upper() and "FROM" in v.upper()):
            continue
        base = node.lineno
        for off, line in enumerate(v.splitlines()):
            clean = SAFE_RE.sub("__RAWPX__", line)
            if BAN_RE.search(clean) and SQLLINE_RE.search(line):
                hits.append((base + off, line.strip()))
    return hits


def _code_line_hits(src):
    """Vi phạm trên dòng CODE thật (không phải comment, không nằm trong chuỗi)."""
    import io as _io
    import tokenize as _tok
    # ⚠️ Python >= 3.12 (PEP 701) tách f-string thành FSTRING_START/MIDDLE/END, KHÔNG còn là
    # `STRING`. Chỉ liệt `_tok.STRING` thì mọi dòng f-string SQL bị coi là code ⇒ báo TRÙNG với
    # `_sql_string_hits`. Runner thật (`$DNA_PYEXE`) là 3.12 nên đây là đường chạy mặc định, không
    # phải trường hợp hiếm. Lọc theo TÊN token để chạy đúng trên cả 3.10 và 3.12.
    _SKIP_NAMES = {"COMMENT", "STRING", "FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"}
    skip = set()
    toks = list(_tok.generate_tokens(_io.StringIO(src).readline))
    for t in toks:
        if _tok.tok_name.get(t.type) in _SKIP_NAMES:
            for ln in range(t.start[0], t.end[0] + 1):
                skip.add(ln)
    hits = []
    for i, line in enumerate(src.splitlines(), 1):
        if i in skip:
            continue
        clean = SAFE_RE.sub("__RAWPX__", line)
        if BAN_RE.search(clean):
            hits.append((i, line.strip()))
    return hits


# Miễn trừ CÓ DANH DẤU, duy nhất một dạng: chân đối chứng A/B cố ý giữ hành vi cũ (rollback một
# từ). Viết bằng comment SQL `--` nên hợp lệ với BigQuery và nằm ĐÚNG trên dòng vi phạm.
# ⚠️ Kèm TRẦN: `EXEMPT_BUDGET` — miễn trừ không được nở âm thầm. Thêm một chân đối chứng mới thì
# phải nâng trần TRONG commit đó, tức phải có người đọc. Cùng triết lý ratchet với
# `mike/bin/tz_anchor_gate.py` (baseline per-file, chỉ hạ được).
EXEMPT_MARK = "pricebasis-gate:legacy-control"
EXEMPT_BUDGET = 1


def scan_price_basis(root=None, files=None, verbose=True, return_exempt=False):
    root = root or WORKDIR
    out = {}
    exempt = {}
    for fn in (files or PROTECTED):
        path = os.path.join(root, fn)
        if not os.path.exists(path):
            continue
        src = open(path, encoding="utf-8").read()
        hits = sorted(set(_sql_string_hits(src) + _code_line_hits(src)))
        keep = [(ln, txt) for ln, txt in hits if EXEMPT_MARK not in txt]
        ex = [(ln, txt) for ln, txt in hits if EXEMPT_MARK in txt]
        if keep:
            out[fn] = keep
        if ex:
            exempt[fn] = ex
    if verbose:
        for fn, hits in out.items():
            for ln, txt in hits:
                print(f"      {fn}:{ln}  {txt[:110]}")
        for fn, hits in exempt.items():
            for ln, _ in hits:
                print(f"      [miễn trừ có đánh dấu] {fn}:{ln}")
    return (out, exempt) if return_exempt else out


def t5():
    print("\nT5. Grep-gate cơ sở giá trên danh sách file BẢO VỆ "
          f"({len(PROTECTED)} file; SỐ LƯỢNG thô × GIÁ đã điều chỉnh)")
    hits, exempt = scan_price_basis(return_exempt=True)
    n = sum(len(v) for v in hits.values())
    n_ex = sum(len(v) for v in exempt.values())
    check("T5 không còn biểu thức tiền/ADV trộn số-lượng-thô × giá-đã-điều-chỉnh", n == 0,
          f"{n} vi phạm trên {len(hits)} file")
    check("T5b số miễn trừ có đánh dấu không vượt trần", n_ex <= EXEMPT_BUDGET,
          f"{n_ex} miễn trừ / trần {EXEMPT_BUDGET}")
    return n + max(0, n_ex - EXEMPT_BUDGET)

# ── PIN vintage corp-action cho T1-T4 (VIỆC 3 job Taylor_20260927_131720, 2026-09-27) ─────────
# Vì sao: `custom_basket._corp_action_share_events()` đọc `tav2_bq.corporate_action` từ LIVE BQ, và
# bảng đó được UPSERT TẠI CHỖ (`kb/data_registry/price-volume/corporate_action_bq.md` Bẫy 2b) ⇒ số
# dòng ISS+AIS ĐỔI giữa các lần chạy. Đo thật: Mike thấy 1706/1843 rồi 1736/1875 (hai con số/lần
# chạy = hai cửa sổ RECENT/OLD có member-union khác nhau), và đã có MỘT lần T1 FAIL rồi các lần sau
# PASS mà không giải thích được dứt điểm lần FAIL đó. Một selfcheck mà input đổi theo giờ thì
# "PASS" của nó không phải bằng chứng — nên ghim vintage.
#
# Dùng LẠI đúng vintage `data/snapshots/corp_action_share_20260927.parquet` (sinh 11:53 ICT
# 2026-09-27 bằng `corp_action_share_snapshot.py`) thay vì sinh một bản mới cùng ngày: nó đã là
# vintage mà lệnh pin `research/oshares_weight_exdate_20260927/run_publish_leg_v3.sh` chạy trên, nên
# ghim cùng file giữ selfcheck và kết quả đã pin nói về CÙNG một tập sự kiện. Sinh thêm một vintage
# 09-27 thứ hai là tự tạo ra hai nguồn sự thật cho cùng một ngày.
#
# FAIL-CLOSED nếu thiếu file: thà dừng còn hơn âm thầm rơi về LIVE BQ và lại bất tất định.
# Override: đặt sẵn `BASKET_CA_SNAPSHOT` (env thắng) — hoặc `BASKET_CA_SNAPSHOT=` rỗng thì
# `setdefault` không đè, nhưng `custom_basket` coi chuỗi rỗng là "đọc LIVE", nên đó là cách khai
# TƯỜNG MINH rằng mình muốn đọc live.
CA_SNAPSHOT_NAME = "corp_action_share_20260927.parquet"


def _ca_snapshot_candidates():
    """Nơi tìm vintage, theo thứ tự ưu tiên — KHÔNG hardcode đường dẫn canonical.

    Vì sao cần cây thứ hai: vintage nằm trong `data/`, là thư mục DỮ LIỆU không được git theo
    dõi. Đo thật trên worktree của chính commit này
    (`mike/agents/Taylor/wt-casnap-2709/WorkingClaude/data/snapshots/` chỉ có `latest_date.txt`)
    ⇒ nếu chỉ tìm theo `WORKDIR` thì cổng fail-closed ở ĐÚNG lúc cần nhất: lúc review một branch
    trong worktree. Đó là y hệt cái bẫy Mike vừa vá cho `WORKDIR`/T5 vài giờ trước
    ("mặc định hardcode làm cổng NÀY VÔ HIỆU ở mọi worktree"), chỉ đổi chỗ từ CODE sang DỮ LIỆU.
    Cây canonical suy ra bằng `git --git-common-dir` (worktree nào cũng trỏ về .git của repo
    chính) nên di chuyển repo không làm hỏng.
    """
    cands = [os.path.join(WORKDIR, "data", "snapshots", CA_SNAPSHOT_NAME)]
    try:
        common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=WORKDIR,
                                capture_output=True, text=True, check=True).stdout.strip()
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=WORKDIR,
                             capture_output=True, text=True, check=True).stdout.strip()
        canon = os.path.join(os.path.dirname(os.path.abspath(common)),
                             os.path.relpath(WORKDIR, top))
        cands.append(os.path.join(canon, "data", "snapshots", CA_SNAPSHOT_NAME))
    except Exception:
        pass  # không nằm trong git / git không có: chỉ còn cây của chính file này
    return [c for i, c in enumerate(cands) if c not in cands[:i]]


CA_SNAPSHOT = _ca_snapshot_candidates()[0]


def _pin_corp_action_vintage():
    """Ghim vintage corp-action và IN dấu vết để tất định kiểm được từ ngoài."""
    if "BASKET_CA_SNAPSHOT" in os.environ:
        snap = os.environ["BASKET_CA_SNAPSHOT"]
        print(f"BASKET_CA_SNAPSHOT = {snap or '(rỗng → LIVE BQ, khai tường minh)'} [env]")
        if not snap:
            return
    else:
        cands = _ca_snapshot_candidates()
        found = [c for c in cands if os.path.exists(c)]
        snap = found[0] if found else cands[0]
        os.environ["BASKET_CA_SNAPSHOT"] = snap
        tag = "pin mặc định" if snap == cands[0] else "pin mặc định · cây canonical"
        print(f"BASKET_CA_SNAPSHOT = {snap} [{tag}]")
    if not os.path.exists(snap):
        raise SystemExit(
            f"FAIL-CLOSED: thiếu snapshot corp-action. Đã tìm:\n"
            + "".join(f"    - {c}\n" for c in _ca_snapshot_candidates())
            + f"  Sinh lại: python3 corp_action_share_snapshot.py data/snapshots/{CA_SNAPSHOT_NAME}\n"
            f"  (KHÔNG rơi về LIVE BQ: bảng corporate_action upsert tại chỗ ⇒ selfcheck sẽ bất "
            f"tất định, đúng lý do cổng này được ghim.)")
    _ev = pd.read_parquet(snap)
    _dig = int(pd.util.hash_pandas_object(
        _ev[["ticker", "event_code", "share_date", "exercise_ratio"]].astype(str)).sum())
    print(f"  vintage: {len(_ev)} dòng ISS+AIS, {_ev['ticker'].nunique()} mã, "
          f"digest={_dig}")


def main():
    bq = _bq()
    print(f"BQ_LOCAL_CACHE = {os.environ.get('BQ_LOCAL_CACHE', '(live BQ)')}")
    _pin_corp_action_vintage()
    pre = load_pre_edit()
    post = load_post_edit()
    ctl = load_post_edit(force_close_basis=True)


    # ── T1. ĐỒNG NHẤT THỨC ────────────────────────────────────────────────────────────────
    print("\nT1. Đồng nhất thức (ép mcapw==mcap → phải trùng module tiền-sửa BIT-FOR-BIT)")
    for tag, win in (("recent", RECENT), ("old", OLD)):
        s_pre, m_pre, _ = run(pre, bq, win)
        s_ctl, m_ctl, _ = run(ctl, bq, win)
        ix = s_pre.index.intersection(s_ctl.index)
        dmax = float((s_pre.loc[ix] - s_ctl.loc[ix]).abs().max())
        check(f"T1[{tag}] level trùng khít", dmax == 0.0,
              f"max|Δlevel| = {dmax:.6e} trên {len(ix)} phiên")
        ds, per = member_diff(m_pre, m_ctl)
        check(f"T1[{tag}] rổ trùng khít", sum(per) == 0,
              f"{sum(per)} tên đổi trên {len(ds)} mốc rebal")

    # ── T2. PARITY MỐC REBAL MỚI NHẤT ─────────────────────────────────────────────────────
    # ⚠️ "Parity ngày gần đây" chỉ đúng ở MỐC REBAL MỚI NHẤT, nơi quý chọn rổ nằm sát ngày
    # snapshot nên Close/Price ~1,00. Trên cả CỬA SỔ 18 tháng hệ số KHÔNG ~1,00 (mỗi mã tích
    # luỹ cổ tức từ ngày t tới ngày snapshot) — đo bên dưới, không giả định.
    print("\nT2. Parity tại mốc rebal MỚI NHẤT (nơi Close/Price ~1,00)")
    s_pre_r, m_pre_r, _ = run(pre, bq, RECENT)
    s_new_r, m_new_r, raw_r = run(post, bq, RECENT)
    last = max(set(m_pre_r) & set(m_new_r))
    same_last = set(m_pre_r[last]) == set(m_new_r[last])
    check(f"T2 rổ tại rebal mới nhất ({last.date()}) KHÔNG đổi", same_last,
          f"{len(set(m_pre_r[last]) ^ set(m_new_r[last]))//2} tên đổi/30")
    dmax_r, n_r, ta, tb = cmp_levels(s_pre_r, s_new_r)
    ds_r, per_r = member_diff(m_pre_r, m_new_r)
    print("      sức phân giải (hệ số Close/Price đo trên chính panel này):")
    print(adj_factor_line("recent", raw_r))
    print(f"      [đo, KHÔNG phải gate] cả cửa sổ {RECENT[0]}..{RECENT[1]}: "
          f"{sum(per_r)} tên đổi / {len(ds_r)} rebal (TB {np.mean(per_r) if per_r else 0:.2f}/30); "
          f"tổng lợi suất cũ x{ta:.5f} vs mới x{tb:.5f} (Δ {(tb-ta)*100:+.2f}pp)")

    # ── T3. POSITIVE CONTROL NGÀY CŨ ──────────────────────────────────────────────────────
    print("\nT3. Positive control ngày cũ (Close/Price xa 1,00 → PHẢI có khác biệt thật)")
    s_pre_o, m_pre_o, _ = run(pre, bq, OLD)
    s_new_o, m_new_o, raw_o = run(post, bq, OLD)
    dmax_o, n_o, toa, tob = cmp_levels(s_pre_o, s_new_o)
    ds_o, per_o = member_diff(m_pre_o, m_new_o)
    print("      sức phân giải (hệ số Close/Price đo trên chính panel này):")
    print(adj_factor_line("old", raw_o))
    check("T3 rổ ĐỔI thật (>0 tên)", sum(per_o) > 0,
          f"{sum(per_o)} tên đổi / {len(ds_o)} mốc rebal (TB {np.mean(per_o) if per_o else 0:.2f}/30, "
          f"max {max(per_o) if per_o else 0})")
    check("T3 chuỗi return ĐỔI thật (>0)", dmax_o > 0,
          f"max|Δret| = {dmax_o*100:.4f}pp/phiên; tổng kỳ cũ x{toa:.5f} vs mới x{tob:.5f} "
          f"(Δ {(tob-toa)*100:+.2f}pp)")
    check("T3 khác biệt LỚN HƠN ngày gần đây (dose-response theo hệ số đ/c)",
          sum(per_o) / max(len(ds_o), 1) > sum(per_r) / max(len(ds_r), 1),
          f"cũ {sum(per_o)/max(len(ds_o),1):.2f} tên/rebal vs gần đây "
          f"{sum(per_r)/max(len(ds_r),1):.2f} tên/rebal")

    # ── T4. AN TOÀN CỔ TỨC ────────────────────────────────────────────────────────────────
    # T4/T4b: 2 cột EXPORT tách vai đúng — mcap/mcapw của cùng 1 mã-ngày lệch đúng bằng hệ số
    # Close/Price, và mcap vẫn tái lập Close*OShares (không phải Price*OShares). Vẫn là bất biến
    # thật và vẫn phải giữ, NHƯNG từ 2026-09-27 nó KHÔNG còn nói gì về chân return (chân return
    # đã rời `mcap`, sang `Close` thuần) — phần đó do T4c kiểm trực tiếp trên chuỗi return.
    print("\nT4. An toàn cổ tức (cơ sở điều chỉnh đúng chỗ; chân return kiểm riêng ở T4c)")
    r = raw_o.dropna(subset=["mcap", "mcapw", "Close", "pxw", "OShares"])
    lhs = (r["mcap"] / r["mcapw"]).values
    rhs = (r["Close"] / r["pxw"]).values
    ok_ratio = np.nanmax(np.abs(lhs - rhs)) < 1e-9
    check("T4 mcap/mcapw == Close/Price (2 CỘT EXPORT tách đúng — không phải chân return)",
          bool(ok_ratio),
          f"max|Δ| = {np.nanmax(np.abs(lhs - rhs)):.3e}, n={len(r):,}")
    adj = (r["Close"] / r["pxw"])
    n_far = int((adj.sub(1.0).abs() > 0.05).sum())
    check("T4 có mẫu hệ số đ/c XA 1,00 trong cửa sổ (phép thử có sức phân giải)", n_far > 0,
          f"{n_far:,}/{len(r):,} dòng có |Close/Price-1|>5% "
          f"(trung vị hệ số {float(adj.median()):.3f})")

    # T4c — KIỂM TRỰC TIẾP TRÊN CHUỖI RETURN (không qua cột `mcap`). Sau bản sửa 2026-09-27 chân
    # return chạy trên `Close` THUẦN, nên đảo `BASKET_RETURN_OSHARES` phải làm chuỗi ĐỔI: nếu
    # không đổi thì hoặc knob chết, hoặc ai đó đã âm thầm đưa số CP trở lại chân return.
    # ⚠️ Phải lật `_SC_RETCHAIN` của module, KHÔNG phải env trực tiếp: `run()` luôn GHI ĐÈ env
    # bằng `mod._SC_RETCHAIN` ngay trước khi gọi build_pit() (để control leg của T1 không bị môi
    # trường bên ngoài làm nhiễu). Bản đầu của T4c set env rồi gọi run() ⇒ bị đè về "flat" ⇒
    # d_ret = 0 ⇒ FAIL giả, đúng lớp lỗi §28 (so kênh HÀNH ĐỘNG thay vì giá trị thật sự có hiệu lực).
    _prev_rc = getattr(post, "_SC_RETCHAIN", None)
    post._SC_RETCHAIN = "legacy"
    try:
        s_leg_o, _, _ = run(post, bq, OLD)
    finally:
        post._SC_RETCHAIN = _prev_rc
    ix_o = s_new_o.index.intersection(s_leg_o.index)
    d_ret = float((ret_of(s_new_o).loc[ix_o[1:]] - ret_of(s_leg_o).loc[ix_o[1:]]).abs().max())
    check("T4c số CP ĐÃ ra khỏi chân return (đảo BASKET_RETURN_OSHARES làm chuỗi ĐỔI)",
          d_ret > 1e-9,
          f"max|Δret| flat vs legacy = {d_ret*100:.4f}pp/phiên trên {len(ix_o)} phiên "
          f"(0 = knob chết hoặc số CP đã quay lại chân return — xem "
          f"basket_return_leg_oshares_selfcheck.py)")

    t5()

    print("\n" + "=" * 78)
    if FAILS:
        print(f"KẾT QUẢ: FAIL {len(FAILS)} — {', '.join(FAILS)}")
        return 1
    print("KẾT QUẢ: PASS toàn bộ (T1 đồng nhất thức / T2 parity / T3 positive control / T4 cổ tức)")
    return 0


if __name__ == "__main__":
    # `--scan-only`: chạy RIÊNG T5, không đụng BigQuery/cache — để cổng cơ học này dùng được
    # trong pre-commit và trong CI nhẹ, không phải chờ cả selfcheck rổ (§23: chạy theo phạm vi).
    if "--scan-only" in sys.argv:
        sys.exit(1 if t5() else 0)
    sys.exit(main())
