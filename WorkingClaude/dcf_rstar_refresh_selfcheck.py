# -*- coding: utf-8 -*-
"""Selfcheck dcf_rstar_refresh (job Taylor_20261102_034815). Không chạm BQ / engine thật: builder được tiêm.
Chạy: python3 dcf_rstar_refresh_selfcheck.py [--mutate]   (nên chạy dưới `env -u TZ` và TZ=America/Los_Angeles)"""
import datetime as dt
import json, os, sys, tempfile
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
SRC = os.path.join(HERE, "dcf_rstar_refresh.py")


def load(src):
    m = type(sys)("rr"); m.__file__ = SRC
    exec(compile(src, SRC, "exec"), m.__dict__)
    return m


def synth(months):
    """panel_live tổng hợp: mỗi tháng 60 mã, Price/FV có r* xác định (g_T_raw hằng)."""
    rng = np.random.default_rng(7); rows = []
    for t in months:
        for i in range(60):
            rows.append((pd.Timestamp(t), f"T{i}", float(rng.uniform(10, 90)), 0.055, 0.08, float(rng.uniform(2, 9)), 1.0))
    p = pd.DataFrame(rows, columns=["t", "ticker", "Price", "g_T_raw", "g_raw", "base", "os_live"])
    p["base"] = p.base * 1e9; p["os_live"] = p.base * 60.0 / p.Price * p.os_live / 5.5
    return p


def run_checks(mod):
    n = 0
    def ok(c, m):
        nonlocal n
        assert c, "FAIL: " + m; n += 1
    # --- cutoff tháng đóng
    ok(mod.closed_months_cutoff(dt.date(2026, 11, 2)) == dt.date(2026, 10, 31), "cutoff = cuối tháng trước")
    ok(mod.closed_months_cutoff(dt.date(2026, 1, 15)) == dt.date(2025, 12, 31), "cutoff qua năm")
    ok(mod.closed_months_cutoff(dt.date(2026, 11, 2), "2026-10-30") == dt.date(2026, 10, 30), "--until thắng")
    # --- control_compare
    base = {"2026-08": 14.0, "2026-09": 14.5}
    w, wm, miss = mod.control_compare({"2026-08": 14.04, "2026-09": 14.52, "2026-10": 15}, base)
    ok(abs(w - 0.04) < 1e-9 and wm == "2026-08" and not miss, "control: max|Δ| đúng, tháng mới thừa không phạt")
    w, wm, miss = mod.control_compare({"2026-08": 14.0}, base)
    ok(miss == ["2026-09"], "control: thiếu tháng bị báo")
    w, wm, miss = mod.control_compare({"2026-08": 14.0, "2026-09": 14.5 + 0.0501}, base)
    ok(w > mod.TOL_PP, "control: 0,0501pp > dung sai 0,05")
    # --- expiry
    T = dt.date(2026, 12, 1); C = lambda pa: [{"panel_asof": pa}]
    ok(mod.expiry_status(C("2026-10-30"), T, 45)[0] == 0, "còn 14 ngày -> ok (10-30+45=12-14; 12-01 còn 13)")
    ok(mod.expiry_status(C("2026-10-30"), dt.date(2026, 12, 5), 45)[0] == mod.RC_EXPIRY, "còn 9 ngày (<10) -> cảnh báo")
    ok(mod.expiry_status(C("2026-10-30"), dt.date(2026, 12, 4), 45)[0] == 0, "còn đúng 10 ngày -> chưa cảnh báo (biên)")
    rc, msg = mod.expiry_status(C("2026-10-30"), dt.date(2026, 12, 20), 45)
    ok(rc == mod.RC_EXPIRY and "HẾT HẠN" in msg, "quá hạn: " + msg)
    ok(mod.expiry_status([], T, 45)[0] == mod.RC_EXPIRY, "không có cache -> cảnh báo")
    rc, _ = mod.expiry_status([{"panel_asof": "2026-06-30"}, {"panel_asof": "2026-10-30"}], T, 45)
    ok(rc == 0, "lấy cache MỚI NHẤT, không phải cái đầu")
    # --- refresh() với builder tiêm
    import dcf_rate_display as DISP
    d = tempfile.mkdtemp(); out = os.path.join(d, "u", "c.json"); tr = os.path.join(d, "tracked.json")
    ms = [m.to_timestamp(how="end").normalize() for m in pd.period_range("2025-01", "2026-08", freq="M")]
    mk = lambda months: (lambda tmp, cutoff: synth(months))
    kw = dict(baseline_paths=[tr, out], tmp_root=d, today=dt.date(2026, 11, 2))
    tmps = lambda: [x for x in os.listdir(d) if x.startswith("rstar_refresh_")]
    c1 = mod.refresh(out, builder=mk(ms), **kw)                      # không baseline -> ghi
    ok(os.path.exists(out) and not os.path.exists(out + ".tmp") and not tmps(), "ghi nguyên tử, dọn tmp")
    ok(json.load(open(out))["series"] == c1["series"] and c1["panel_asof"] == "2026-08-31", "cache = nội dung trả về")
    json.dump(c1, open(tr, "w"), sort_keys=True); os.remove(out)      # tracked = bản vừa dựng
    # panel không mới hơn -> rc2, không ghi
    try:
        mod.refresh(out, builder=mk(ms), **kw); ok(False, "lẽ ra rc2")
    except mod.RefreshError as e:
        ok(e.rc == mod.RC_NOT_NEWER and not os.path.exists(out), "panel không mới hơn -> rc2 + không ghi")
    # --force cho phép dựng lại cùng asof (control tự khớp)
    mod.refresh(out, builder=mk(ms), force=True, **kw); ok(os.path.exists(out), "--force ghi"); os.remove(out)
    # panel mới thêm tháng, nền khớp -> ghi, có tháng mới
    c3 = mod.refresh(out, builder=mk(ms + [pd.Timestamp("2026-09-30")]), **kw)
    ok(c3["panel_asof"] == "2026-09-30" and "2026-09" in c3["series"], "tháng mới vào cache"); os.remove(out)
    # control lệch: đổi giá 1 tháng cũ -> r* tháng đó lệch > 0,05pp -> rc4, KHÔNG ghi
    def drift(tmp, cutoff):
        p = synth(ms + [pd.Timestamp("2026-09-30")]); k = p.t == pd.Timestamp("2025-03-31"); p.loc[k, "Price"] *= 1.5; return p
    try:
        mod.refresh(out, builder=drift, **kw); ok(False, "lẽ ra rc4")
    except mod.RefreshError as e:
        ok(e.rc == mod.RC_CONTROL and not os.path.exists(out) and not tmps(), "control lệch -> rc4, không ghi, dọn tmp: " + str(e))
    # control: tháng nền biến mất -> rc4
    try:
        mod.refresh(out, builder=mk(ms[3:] + [pd.Timestamp("2026-09-30")]), **kw); ok(False, "lẽ ra rc4 (thiếu tháng)")
    except mod.RefreshError as e:
        ok(e.rc == mod.RC_CONTROL, "thiếu tháng nền -> rc4")
    # builder lỗi (BQ down) -> rc3, thông điệp có lỗi thật (§29), không ghi
    def boom(tmp, cutoff): raise ConnectionError("bq timeout 30s")
    try:
        mod.refresh(out, builder=boom, **kw); ok(False, "lẽ ra rc3")
    except mod.RefreshError as e:
        ok(e.rc == mod.RC_BUILD and "ConnectionError" in str(e) and "bq timeout 30s" in str(e) and not os.path.exists(out), "builder lỗi -> rc3 + trích lỗi thật: " + str(e))
    # đích đã có (bản cũ) không bị phá khi thất bại
    open(out, "w").write(json.dumps(c1))
    before = open(out).read()
    try:
        mod.refresh(out, builder=boom, **kw)
    except mod.RefreshError:
        pass
    ok(open(out).read() == before, "thất bại không đụng cache đích đang có")
    # main(): --check-expiry không dựng gì
    ok(mod.main(["--check-expiry"]) in (0, mod.RC_EXPIRY), "--check-expiry chạy được")
    return n


if __name__ == "__main__":
    src = open(SRC).read()
    print("PASS", run_checks(load(src)), "assertions")
    if "--mutate" in sys.argv:
        muts = [("TOL_PP = 0.05", "TOL_PP = 5.0"),
                ("if worst > TOL_PP or missing:", "if worst > TOL_PP:"),
                ("if worst > TOL_PP or missing:", "if False:"),
                ("new_asof <= base[\"panel_asof\"] and not force", "new_asof < base[\"panel_asof\"] and not force"),
                ("new_asof <= base[\"panel_asof\"] and not force", "False"),
                ("os.replace(tmpo, out_path)", "shutil.copyfile(stage, out_path)"),
                ("shutil.rmtree(tmp, ignore_errors=True)", "pass"),
                ("if left < warn_days:", "if left <= warn_days:"),
                ("if left < warn_days:", "if left < 0:"),
                ("if left < 0:\n        return RC_EXPIRY, f\"cache r* ĐÃ HẾT HẠN", "if left < -9999:\n        return RC_EXPIRY, f\"cache r* ĐÃ HẾT HẠN"),
                ("max(caches, key=lambda c: c[\"panel_asof\"])", "caches[0]"),
                ("first - _dt.timedelta(days=1)", "first"),
                ("raise RefreshError(RC_BUILD, f\"dựng panel lỗi: {type(e).__name__}: {e}\")", "raise RefreshError(RC_BUILD, 'dựng panel lỗi')"),
                ("if d > worst:", "if d < worst:"),
                ("if m not in new_series:", "if False:")]
        for a, b in muts:
            assert src.count(a) == 1, "mutation target mất/đúp: " + a[:50]
            try:
                run_checks(load(src.replace(a, b))); print("SURVIVED (xấu):", a); sys.exit(1)
            except Exception as e:
                print("killed:", a[:50].replace("\n", " "), "->", str(e)[:60])
        print("MUTATION: %d/%d killed" % (len(muts), len(muts)))
