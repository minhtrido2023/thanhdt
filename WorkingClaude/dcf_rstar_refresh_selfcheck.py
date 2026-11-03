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


def fake_build_checks(mod, d):
    """Tiêm engine/oshares_pit/oshares_live/dcf_valuation/level giả vào sys.modules; gọi mod.build_panel thật."""
    import types
    real_cal = mod.CAL
    snap = sorted(os.listdir(os.path.join(real_cal, "data")))
    tmp = tempfile.mkdtemp(dir=d)
    st = {"months": [pd.Timestamp("2026-09-30"), pd.Timestamp("2026-10-30"), pd.Timestamp("2026-11-30")], "writes": []}
    under = lambda path: os.path.abspath(path).startswith(os.path.abspath(tmp) + os.sep)
    E = types.ModuleType("engine"); E.DATA = "/nonexistent/REAL_DATA_MUST_NOT_BE_WRITTEN"
    def build():
        st["writes"].append(E.DATA)
        rows = [(t, tk, 1e9) for t in st["months"] for tk in ("AAA", "BBB")]
        pd.DataFrame(rows, columns=["t", "ticker", "OShares"]).to_parquet(os.path.join(E.DATA, "panel_monthly.parquet"))
    E.build = build
    OP = types.ModuleType("oshares_pit")
    OP.oshares_pit = lambda tks, date, fb, cache=None: {k: {"value": fb[k], "source": "fallback", "method": None, "live_value": None} for k in tks}
    OL = types.ModuleType("oshares_live"); OL._fetch = lambda tks, until: ([1, 2], [3])
    D = types.ModuleType("dcf_valuation"); D.LIVE_BELOW_FIN_TOL = 0.005
    LV = types.ModuleType("level"); LV.OLD = LV.DATA = "/nonexistent/REAL_LEVEL"
    def load():
        st["writes"] += [LV.OLD, LV.DATA]
        p = pd.read_parquet(os.path.join(LV.DATA, "os_live.parquet"))
        p["rt"] = 0
        return p
    LV.load = load
    fakes = {"engine": E, "oshares_pit": OP, "oshares_live": OL, "dcf_valuation": D, "level": LV}
    saved = {k: sys.modules.get(k) for k in fakes}
    sys.modules.update(fakes)
    env0 = os.environ.get("DCF_RATE_FRAME"); sp0 = list(sys.path)
    try:
        p = mod.build_panel(tmp, "2026-10-31")
        assert p.t.max() == pd.Timestamp("2026-10-30"), "cutoff phải loại t > cutoff (11-30): " + str(p.t.max())
        assert all(under(w) for w in st["writes"]), "ghi ngoài tmp: " + str(st["writes"])
        assert sorted(os.listdir(os.path.join(real_cal, "data"))) == snap, "thư mục nghiên cứu thật bị đổi"
        st["months"] = [pd.Timestamp("2026-09-30"), pd.Timestamp("2026-10-20")]     # dữ liệu dừng giữa tháng 10
        try:
            mod.build_panel(tempfile.mkdtemp(dir=d), "2026-10-31"); raise AssertionError("tháng dở phải rc3")
        except mod.RefreshError as e:
            assert e.rc == mod.RC_BUILD and "2026-10-20" in str(e), "tháng dở -> rc3 + bằng chứng: " + str(e)
    finally:
        for k, v in saved.items():
            if v is None: sys.modules.pop(k, None)
            else: sys.modules[k] = v
        sys.path[:] = sp0
        if env0 is None: os.environ.pop("DCF_RATE_FRAME", None)
        else: os.environ["DCF_RATE_FRAME"] = env0
    return True


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
    # --- expiry: báo khi tuổi cache > ALERT_AGE_DAYS (38), hết hạn khi > max_age (45)
    C = lambda pa: [{"panel_asof": pa}]
    A0 = dt.date(2026, 10, 30)
    ok(mod.ALERT_AGE_DAYS == 38, "ngưỡng báo 38 ngày")
    ok(mod.expiry_status(C("2026-10-30"), A0 + dt.timedelta(days=38), 45)[0] == 0, "tuổi đúng 38 -> chưa báo (biên)")
    rc, msg = mod.expiry_status(C("2026-10-30"), A0 + dt.timedelta(days=39), 45)
    ok(rc == mod.RC_EXPIRY and "bị lỡ" in msg and "còn 6 ngày" in msg, "tuổi 39 -> báo lần làm mới lỡ: " + msg)
    ok(mod.expiry_status(C("2026-10-30"), A0 + dt.timedelta(days=45), 45)[0] == mod.RC_EXPIRY, "tuổi 45 vẫn báo (lỡ), chưa hết hạn")
    rc, msg = mod.expiry_status(C("2026-10-30"), A0 + dt.timedelta(days=46), 45)
    ok(rc == mod.RC_EXPIRY and "HẾT HẠN 1 ngày" in msg, "quá hạn: " + msg)
    ok(mod.expiry_status(C("2026-10-30"), dt.date(2026, 11, 20), 45)[0] == 0, "cache tháng trước, giữa tháng sau -> im lặng")
    ok(mod.expiry_status([], dt.date(2026, 12, 1), 45)[0] == mod.RC_EXPIRY, "không có cache -> cảnh báo")
    rc, _ = mod.expiry_status([{"panel_asof": "2026-06-30"}, {"panel_asof": "2026-10-30"}], dt.date(2026, 11, 20), 45)
    ok(rc == 0, "lấy cache MỚI NHẤT, không phải cái đầu")
    # --- phiên giao dịch cuối ≤ mốc cắt + kiểm tháng đóng
    ok(mod.last_trading_day(dt.date(2026, 10, 31)) == dt.date(2026, 10, 30), "31/10/2026 là T7 -> 30/10")
    ok(mod.last_trading_day(dt.date(2026, 10, 30)) == dt.date(2026, 10, 30), "30/10 là T6 giao dịch")
    ok(mod.last_trading_day(dt.date(2026, 9, 2)) == dt.date(2026, 8, 28), "2/9, 1/9, 31/8 nghỉ lễ + cuối tuần -> 28/8")
    mod.check_month_closed(dt.date(2026, 10, 30), dt.date(2026, 10, 31))
    try:
        mod.check_month_closed(dt.date(2026, 10, 20), dt.date(2026, 10, 31)); ok(False, "lẽ ra rc3")
    except mod.RefreshError as e:
        ok(e.rc == mod.RC_BUILD and "2026-10-20" in str(e) and "2026-10-30" in str(e), "tháng dở -> rc3 + bằng chứng: " + str(e))
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
    # --- cache nền cũ nhưng còn tươi: panel không mới hơn -> IM LẶNG (rc0, không ghi); quá 38 ngày -> rc2
    ms09 = ms + [pd.Timestamp("2026-09-30")]
    c09 = mod.refresh(out, builder=mk(ms09), **kw); json.dump(c09, open(tr, "w"), sort_keys=True); os.remove(out)
    kw2 = dict(baseline_paths=[tr, out], tmp_root=d)
    ok(mod.refresh(out, builder=mk(ms09), today=dt.date(2026, 11, 7), **kw2) is None and not os.path.exists(out),
       "tuổi cache 38 ngày (09-30 -> 11-07): im lặng, không ghi")
    try:
        mod.refresh(out, builder=mk(ms09), today=dt.date(2026, 11, 8), **kw2); ok(False, "lẽ ra rc2")
    except mod.RefreshError as e:
        ok(e.rc == mod.RC_NOT_NEWER and "LỠ" in str(e) and not os.path.exists(out), "tuổi 39 ngày -> rc2 lần làm mới lỡ")
    # --- cache nền đã tới tháng đóng gần nhất: thoát rc0 NGAY, KHÔNG gọi builder; --force / --until thì dựng
    c10 = mod.refresh(out, builder=mk(ms09 + [pd.Timestamp("2026-10-30")]), **kw); json.dump(c10, open(tr, "w"), sort_keys=True); os.remove(out)
    def never(tmp, cutoff): raise AssertionError("builder không được gọi khi cache đã tới tháng đóng")
    ok(mod.refresh(out, builder=never, **kw) is None and not os.path.exists(out), "đã đủ tháng -> rc0, không dựng")
    called = []
    def spy(tmp, cutoff): called.append(cutoff); return synth(ms09 + [pd.Timestamp("2026-10-30")])
    mod.refresh(out, builder=spy, force=True, **kw); os.remove(out)
    mod.refresh(out, builder=spy, until="2026-10-30", **kw)   # tuổi 3 ngày: im lặng nhưng ĐÃ dựng (builder được gọi)
    ok(len(called) == 2, "--force và --until đều bỏ qua lối tắt 'đã đủ tháng'")
    # --- control lệch + --accept-control-drift: mặc định rc4; có cờ thì ghi, log từng tháng, đánh dấu trong cache
    def drift2(tmp, cutoff):
        p = synth(ms09 + [pd.Timestamp("2026-10-30")]); k = p.t == pd.Timestamp("2025-03-31"); p.loc[k, "Price"] *= 1.5; return p
    def drift3(tmp, cutoff):
        p = synth(ms09 + [pd.Timestamp("2026-10-30"), pd.Timestamp("2026-11-30")]); k = p.t == pd.Timestamp("2025-03-31"); p.loc[k, "Price"] *= 1.5; return p
    for bld, fr, un in ((drift2, True, "2026-10-30"), (drift3, False, "2026-11-30")):   # --force KHÔNG bỏ control
        try:
            mod.refresh(out, builder=bld, force=fr, until=un, **kw); ok(False, "lẽ ra rc4")
        except mod.RefreshError as e:
            ok(e.rc == mod.RC_CONTROL and "--accept-control-drift" in str(e) and not os.path.exists(out), f"drift không cờ -> rc4 (force={fr})")
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cd = mod.refresh(out, builder=drift2, force=True, accept_drift=True, **kw)
    lg = buf.getvalue()
    ok(os.path.exists(out) and json.load(open(out))["control_drift_accepted"]["month"] == "2025-03", "accept -> ghi + đánh dấu trong cache")
    ok(cd["control_drift_accepted"]["n_months"] >= 1 and "2025-03:" in lg and "CHẤP NHẬN" in lg, "accept -> log diff từng tháng: " + lg[-300:])
    os.remove(out)
    # --- traceback thật gắn vào RefreshError (rc3) để main() in ra stderr
    try:
        mod.refresh(out, builder=boom, force=True, **kw); ok(False, "lẽ ra rc3")
    except mod.RefreshError as e:
        ok(e.tb and "Traceback" in e.tb and "bq timeout 30s" in e.tb, "rc3 mang traceback đầy đủ")
    # --- main(): mặc định ghi RSTAR_CACHE_LIVE (untracked), không bao giờ RSTAR_CACHE (tracked); --out tương đối -> tuyệt đối
    seen = []
    real_refresh = mod.refresh
    mod.refresh = lambda o, **k: seen.append((o, k)) or None
    try:
        cwd0 = os.getcwd(); os.chdir(d)
        mod.main([]); mod.main(["--out", "rel/x.json", "--accept-control-drift"])
        os.chdir(cwd0)
    finally:
        mod.refresh = real_refresh; os.chdir(cwd0)
    ok(seen[0][0] == DISP.RSTAR_CACHE_LIVE and seen[0][0] != DISP.RSTAR_CACHE, "main mặc định ghi RSTAR_CACHE_LIVE, không phải tracked")
    ok(seen[1][0] == os.path.join(os.path.realpath(d), "rel", "x.json") or seen[1][0] == os.path.join(d, "rel", "x.json"), "--out tương đối -> tuyệt đối theo cwd gọi: " + seen[1][0])
    ok(seen[1][1]["accept_drift"] is True and seen[0][1]["accept_drift"] is False, "cờ accept chuyển xuống refresh")
    # --- build_panel với engine/oshares/level GIẢ: mọi ghi nằm dưới tmp, cắt cutoff, kiểm tháng đóng
    ok(fake_build_checks(mod, d), "build_panel giả")
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
                ("if not accept_drift:", "if True:"),
                ("if not accept_drift:", "if False:"),
                ("new_asof <= base[\"panel_asof\"] and not force", "new_asof < base[\"panel_asof\"] and not force"),
                ("new_asof <= base[\"panel_asof\"] and not force", "False"),
                ("os.replace(tmpo, out_path)", "shutil.copyfile(stage, out_path)"),
                ("shutil.rmtree(tmp, ignore_errors=True)", "pass"),
                ("if age > alert_age:", "if age >= alert_age:"),
                ("if age > alert_age:", "if age > max_age:"),
                ("if age > max_age:\n        return RC_EXPIRY, f\"cache r* ĐÃ HẾT HẠN", "if age > max_age + 9999:\n        return RC_EXPIRY, f\"cache r* ĐÃ HẾT HẠN"),
                ("if age <= ALERT_AGE_DAYS:", "if age < ALERT_AGE_DAYS:"),
                ("if age <= ALERT_AGE_DAYS:", "if True:"),
                ("max(caches, key=lambda c: c[\"panel_asof\"])", "caches[0]"),
                ("first - _dt.timedelta(days=1)", "first"),
                ("raise RefreshError(RC_BUILD, f\"dựng panel lỗi: {type(e).__name__}: {e}\", traceback.format_exc())", "raise RefreshError(RC_BUILD, 'dựng panel lỗi')"),
                ("if d > worst:", "if d < worst:"),
                ("if m not in new_series:", "if False:"),
                ("base[\"panel_asof\"][:7] >= cutoff.isoformat()[:7]", "False"),
                ("if base and until is None and not force and", "if base and"),
                # vòng 2 (arch-review): 3 mutation sống theo yêu cầu + kiểm tháng đóng + abspath
                ("out = os.path.abspath(a.out or DISP.RSTAR_CACHE_LIVE)", "out = os.path.abspath(a.out or DISP.RSTAR_CACHE)"),
                ("out = os.path.abspath(a.out or DISP.RSTAR_CACHE_LIVE)", "out = a.out or DISP.RSTAR_CACHE_LIVE"),
                ("E.DATA = os.path.join(cal, \"data\")", "pass"),
                ("LV.OLD, LV.DATA = cal, os.path.join(lv, \"data\")", "pass"),
                ("pan = pan[pan.t <= pd.Timestamp(cutoff)]", "pan = pan"),
                ("check_month_closed(pan.t.max().date(), _dt.date.fromisoformat(str(cutoff)[:10]))", "pass"),
                ("if tmax != exp:", "if False:"),
                ("while d.weekday() >= 5 or is_holiday(d):", "while d.weekday() >= 5:")]
        for a, b in muts:
            assert src.count(a) == 1, "mutation target mất/đúp: " + a[:50]
            try:
                run_checks(load(src.replace(a, b))); print("SURVIVED (xấu):", a); sys.exit(1)
            except Exception as e:
                print("killed:", a[:50].replace("\n", " "), "->", str(e)[:60])
        print("MUTATION: %d/%d killed" % (len(muts), len(muts)))
