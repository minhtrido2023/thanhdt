# -*- coding: utf-8 -*-
"""Selfcheck: due_diligence._bq_client cache cả lỗi dựng client (job Taylor_20261120_154910).

Chạy (từ thư mục chứa trading_bot/):  /home/trido/thanhdt/wc_venv/bin/python dd_bqclient_failcache_selfcheck.py
  --live   thêm ca CÓ credential thật: _in_universe trên mã thật phải ra kết quả y hệt bản
           không cache lỗi (cần `source wc_env.sh`; thiếu cred ⇒ SKIP, nói rõ).

Ca mất cred mô phỏng bằng patch google.auth.default ném DefaultCredentialsError (có sleep để
lộ race) — đếm số lần dò. Ca "mutant" chạy lại đúng kịch bản với logic CŨ (chỉ cache khi thành
công) để chứng minh test thật sự phân biệt được (cũ: N lần dò; mới: 1 lần).
"""
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import google.auth                                      # noqa: E402
from google.auth.exceptions import DefaultCredentialsError  # noqa: E402

import trading_bot.due_diligence as DD                  # noqa: E402

FAILS = []
N_TICKERS = 11
ASOF = "2026-11-20"


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


class _Probe:
    """Thay google.auth.default: đếm lần gọi, chậm 0.3s (đủ để 8 luồng chồng lên nhau)."""
    def __init__(self):
        self.n = 0
        self.lock = threading.Lock()

    def __call__(self, *a, **k):
        with self.lock:
            self.n += 1
        time.sleep(0.3)
        raise DefaultCredentialsError("mo phong: khong tim thay ADC (selfcheck)")


def _reset():
    for k in ("_bqclient", "_bqclient_fail"):
        DD._CACHE.pop(k, None)


def _old_bq_client():
    """Logic TRƯỚC fix (dòng 127-131 cũ) — chỉ cache khi thành công."""
    from google.cloud import bigquery
    client = DD._CACHE.get("_bqclient")
    if client is None:
        client = bigquery.Client(project="lithe-record-440915-m9", location="asia-southeast1")
        DD._CACHE["_bqclient"] = client
    return client


def run_offline():
    orig_default, orig_prune, orig_warn = google.auth.default, DD._in_prune, DD._log.warning
    orig_adc = DD._adc_missing_reason
    DD._adc_missing_reason = lambda: None      # ca 1-5: ép đi đường google.auth (precheck test riêng ở 6-8)
    prune_calls, warns = [], []
    DD._in_prune = lambda *a, **k: prune_calls.append(a) or (True, "x", None)
    DD._log.warning = lambda fmt, *a: warns.append(fmt % a)
    tks = [f"T{i:02d}" for i in range(N_TICKERS)]
    try:
        # 1) tuần tự, mất cred: 1 lần dò cho N mã, mọi mã None
        _reset(); p = _Probe(); google.auth.default = p
        res = [DD._in_universe(t, ASOF) for t in tks]
        check("seq: so lan do credential = 1", p.n == 1, f"n={p.n} / {N_TICKERS} ma")
        check("seq: moi ma (None,None,None) = 'n/a'", all(r == (None, None, None) for r in res), str(set(res)))
        check("seq: khong goi _in_prune (cam fallback §4.3)", not prune_calls, str(len(prune_calls)))
        check("seq: canh bao ma dau mang loi goc", "DefaultCredentialsError" in warns[0] or "khong tim thay ADC" in warns[0], warns[0][:160])
        check("seq: canh bao ma sau van mang loi goc (§29)",
              all("khong tim thay ADC" in w for w in warns[1:]) and len(warns) == N_TICKERS, warns[-1][:160])

        # 2) song song 8 luồng như dd_flag_map (KHÔNG có mã tuần tự mồi trước): vẫn 1 lần dò
        _reset(); p = _Probe(); google.auth.default = p
        with ThreadPoolExecutor(max_workers=8) as ex:
            res = list(ex.map(lambda t: DD._in_universe(t, ASOF), tks * 3))
        check("par8: so lan do = 1 (lock, khong race)", p.n == 1, f"n={p.n} / {len(tks) * 3} loi goi")
        check("par8: moi ket qua None", all(r == (None, None, None) for r in res))

        # 3) hết TTL ⇒ dò lại đúng 1 lần nữa (credential có thể vừa được cấp)
        ts, msg = DD._CACHE["_bqclient_fail"]
        DD._CACHE["_bqclient_fail"] = (ts - DD._BQCLIENT_FAIL_TTL_S - 1, msg)
        for t in tks:
            DD._in_universe(t, ASOF)
        check("ttl: het han -> do lai dung 1 lan", p.n == 2, f"n={p.n}")

        # 4) dò lại THÀNH CÔNG sau lỗi ⇒ xoá cache lỗi, cache client
        _reset(); p = _Probe(); google.auth.default = p
        DD._in_universe("A", ASOF)
        DD._CACHE["_bqclient_fail"] = (time.monotonic() - DD._BQCLIENT_FAIL_TTL_S - 1, "x")
        from google.auth.credentials import AnonymousCredentials
        google.auth.default = lambda *a, **k: (AnonymousCredentials(), "lithe-record-440915-m9")
        c = DD._bq_client()
        check("recover: client duoc cache, loi bi xoa",
              DD._CACHE.get("_bqclient") is c and "_bqclient_fail" not in DD._CACHE)

        # 5) mutant = logic cũ: phải dò N lần (chứng minh test 1 phân biệt được)
        _reset(); p = _Probe(); google.auth.default = p
        new = DD._bq_client
        DD._bq_client = _old_bq_client
        try:
            for t in tks:
                DD._in_universe(t, ASOF)
        finally:
            DD._bq_client = new
        check("mutant(logic cu): do N lan -> test seq bat duoc", p.n == N_TICKERS, f"n={p.n}")
    finally:
        google.auth.default, DD._in_prune, DD._log.warning = orig_default, orig_prune, orig_warn
        DD._adc_missing_reason = orig_adc
        _reset()


def run_precheck():
    """_adc_missing_reason: chỉ 'chắc chắn không có ADC' mới bỏ dò; mọi nguồn cred ⇒ None."""
    import tempfile
    keys = ("GOOGLE_APPLICATION_CREDENTIALS", "CLOUDSDK_CONFIG", "GCE_METADATA_HOST", "GCE_METADATA_ROOT")
    saved = {k: os.environ.get(k) for k in keys}
    orig_default, orig_warn = google.auth.default, DD._log.warning
    try:
        for k in keys:
            os.environ.pop(k, None)
        empty = tempfile.mkdtemp(prefix="ddfix_noadc_")
        os.environ["CLOUDSDK_CONFIG"] = empty
        try:
            prod = open("/sys/class/dmi/id/product_name").read().strip()
        except OSError:
            prod = None
        why = DD._adc_missing_reason()
        if prod is None or "google" in prod.lower():
            check("pre6: DMI khong doc duoc/Google -> None (khong doan)", why is None, str(prod))
        else:
            check("pre6: khong env, khong file ADC, DMI khac Google -> co ly do", bool(why) and empty in why, str(why))
            # end-to-end: precheck chặn ⇒ google.auth.default KHÔNG được gọi lần nào, 11 mã vẫn None
            _reset(); p = _Probe(); google.auth.default = p
            warns = []; DD._log.warning = lambda fmt, *a: warns.append(fmt % a)
            res = [DD._in_universe(f"T{i}", ASOF) for i in range(N_TICKERS)]
            check("pre6: 0 lan do metadata, moi ma None",
                  p.n == 0 and all(r == (None, None, None) for r in res), f"n={p.n}")
            check("pre6: canh bao noi ro ly do (§29)", all("khong co nguon credential ADC" in w for w in warns), warns[0][:200])
            google.auth.default, DD._log.warning = orig_default, orig_warn
        open(os.path.join(empty, "application_default_credentials.json"), "w").write("{}")
        check("pre7: co file ADC theo CLOUDSDK_CONFIG -> None", DD._adc_missing_reason() is None)
        os.remove(os.path.join(empty, "application_default_credentials.json"))
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/x/sa.json"
        check("pre8: co GOOGLE_APPLICATION_CREDENTIALS -> None", DD._adc_missing_reason() is None)
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["GCE_METADATA_HOST"] = "127.0.0.1:1"
        check("pre8b: co GCE_METADATA_HOST -> None", DD._adc_missing_reason() is None)
    finally:
        google.auth.default, DD._log.warning = orig_default, orig_warn
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        _reset()


def run_live():
    """Có cred: kết quả _in_universe (logic mới) == logic cũ trên mã thật."""
    _reset()
    try:
        google.auth.default()
    except Exception as e:  # noqa: BLE001
        print(f"SKIP live: khong co credential ({type(e).__name__}) — source wc_env.sh roi chay --live")
        return
    tks = ["FPT", "HPG", "VCB", "MWG", "QTP", "ZZZZ"]
    new = [DD._in_universe(t, ASOF) for t in tks]
    newfn = DD._bq_client
    _reset(); DD._bq_client = _old_bq_client
    try:
        old = [DD._in_universe(t, ASOF) for t in tks]
    finally:
        DD._bq_client = newfn; _reset()
    for t, a, b in zip(tks, new, old):
        print(f"  {t}: moi={a} cu={b}")
    check("live: ket qua moi == cu tren ma that", new == old)
    check("live: co it nhat 1 ma doc duoc (khong phai toan None)", any(r[0] is not None for r in new))


if __name__ == "__main__":
    run_offline()
    run_precheck()
    if "--live" in sys.argv:
        run_live()
    print(f"\n{'OK' if not FAILS else 'FAILED'}: {len(FAILS)} fail")
    sys.exit(1 if FAILS else 0)
