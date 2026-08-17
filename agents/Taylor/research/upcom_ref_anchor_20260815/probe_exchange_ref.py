"""Đo THẬT: exchange + q.ref + ohlc close cho toàn bộ mã đã/đang dùng cơ chế Rule A."""
import datetime as dt, json, sys
import os, sys as _s; _s.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from zoneinfo import ZoneInfo
from trading_bot.brokers import DNSEBroker

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
TK = ("ACB BID CSV CTG DCM DRI EVF FPT HAH HDB HPG LPB MBB MBS MSB NCT POW PVT SAB SCL SHB "
      "SHS SIP SSI TCB TPB TV1 VCB VGC VHC VHM VIB VIX VND VNM VPB VRE DGC PNJ SGP ACV QNS TMG").split()
b = DNSEBroker(quote_only=True).connect()
to_ts = int(dt.datetime(2026, 8, 15, 20, 0, tzinfo=ICT).timestamp())
fr = to_ts - 40 * 86400
out = []
for t in TK:
    r = {"ticker": t}
    try:
        q = b.get_quote(t)
        raw = q.raw if isinstance(q.raw, dict) else {}
        # in RA MỌI key có mùi sàn — không tin field đã chuẩn hoá (Quote.exchange default='HOSE')
        r["raw_keys_exch"] = {k: v for k, v in raw.items()
                              if any(s in k.lower() for s in
                                     ("exchange", "market", "floor", "board", "listed"))}
        r["q_exchange"] = q.exchange
        r["ref"] = q.ref; r["ce"] = q.ceiling; r["fl"] = q.floor; r["last"] = q.last
        if q.ref and q.ceiling:
            r["band_up_pct"] = round((q.ceiling / q.ref - 1) * 100, 3)
        if q.ref and q.floor:
            r["band_dn_pct"] = round((q.floor / q.ref - 1) * 100, 3)
        o = b.client.ohlc(t, resolution="1D", **{"from": fr, "to": to_ts})
        c, ts = o.get("c") or [], o.get("t") or []
        if c:
            r["close"] = float(c[-1]) * 1000.0
            r["close_date"] = dt.datetime.fromtimestamp(int(ts[-1]), ICT).date().isoformat()
            if q.ref:
                r["dev_pct"] = round((q.ref / r["close"] - 1) * 100, 4)
    except Exception as e:
        r["err"] = f"{type(e).__name__}: {e}"
    out.append(r)
json.dump(out, open("/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/upcom_ref_anchor_20260815/probe_exchange_ref.json", "w"), ensure_ascii=False, indent=1)
for r in out:
    print(f"{r['ticker']:<5} exch={str(r.get('q_exchange')):<8} ref={r.get('ref')} "
          f"close={r.get('close')} dev={r.get('dev_pct')} bandUp={r.get('band_up_pct')} "
          f"rawexch={r.get('raw_keys_exch')} {r.get('err','')}")
