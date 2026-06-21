#!/usr/bin/env python3
"""telegram_8l_bot.py — interactive 8L query bot. User texts a ticker (e.g. "BMP", "BMP 8L", "/dna VCS")
and the bot replies with its current 8L ranking + concise read. Long-polls Telegram getUpdates.
In-universe (≈125 names) → instant from cached rank_8l.csv + unified_screener.csv.
Any other ticker → on-demand dna_card.py <ticker> (100% coverage via ICB-fallback).
Run persistently (Task Scheduler ONLOGON or a console). Stop with Ctrl-C.
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os, re, time, subprocess
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, requests
WORKDIR=os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
PYEXE=os.environ.get("DNA_PYEXE", (r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe" if os.name=="nt" else "python3"))
sys.path.insert(0,WORKDIR)
from telegram_recommend import load_config, send_telegram_text
CFG=load_config(); TOKEN=CFG["bot_token"]; API=f"https://api.telegram.org/bot{TOKEN}"
KW={"8L","DNA","HELP","BOT","RANK","CARD","START","NEW","TOP","MOI","VN30","RO"}
# list commands (top-N table, new-this-week) — see bot_8l_commands.py
try: import bot_8l_commands as CMD
except Exception as e: CMD=None; print("bot_8l_commands unavailable:",e)
# 2-block DNA+NOW renderer (dna_report.build_report). Falls back to the legacy reply if unavailable.
try: from dna_report import build_report as _build_report
except Exception: _build_report=None

def extract_ticker(text):
    toks=re.findall(r"[A-Za-z]{3}[A-Za-z0-9]?", text.upper())
    c=[x for x in toks if x not in KW]
    return c[0] if c else None

def fmt_components(row):
    parts=[]
    for k,v in row.items():
        if k.startswith("_") and pd.notna(v) and v!=0: parts.append(f"{k[1:]}{v:+.0f}")
    return " ".join(parts)

def reply_for(tk):
    # preferred: 2-block DNA+NOW report (live NOW query at message time)
    if _build_report is not None:
        try:
            msg=_build_report(tk)
            if msg and "🧬" in msg: return msg
        except Exception as e: print("dna_report err, fallback:",e)
    try: rank=pd.read_csv(os.path.join(WORKDIR,"data","rank_8l.csv"))
    except Exception: rank=pd.DataFrame()
    try: scr=pd.read_csv(os.path.join(WORKDIR,"data","unified_screener.csv")).set_index("ticker")
    except Exception: scr=pd.DataFrame()
    N=len(rank)
    if len(scr) and tk in scr.index:
        s=scr.loc[tk]; route=s["route"]; verdict=s["verdict"]; action=s["action"]; eng=str(s.get("engine","") or "")
        det=str(s["detail"]); det=det if len(det)<320 else det[:317]+"..."
        rrow=rank[rank["ticker"]==tk]
        if len(rrow):
            rr=rrow.iloc[0]; rk=f"#{int(rr['rank'])}/{N}  score {rr['score']:.1f}"; comps=fmt_components(rr)
        else:
            rk="GATED (AVOID/distressed — not ranked)"; comps=""
        msg=(f"<b>📊 {tk} — 8L</b>\n"
             f"Route: <b>{route}</b> | Rank: <b>{rk}</b>\n"
             f"Verdict: <b>{verdict}</b> | Action: {action}\n"
             + (f"Engine: {eng}\n" if eng and eng!='nan' else "")
             + (f"<i>{comps}</i>\n" if comps else "")
             + f"\n{det}")
        return msg
    # fallback — any ticker via dna_card.py
    try:
        env=dict(os.environ); env["CLOUDSDK_PYTHON"]=PYEXE
        env["PATH"]=env.get("PATH","")+r";C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
        r=subprocess.run([PYEXE,os.path.join(WORKDIR,"dna_card.py"),tk],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=120,cwd=WORKDIR,env=env)
        out=r.stdout
        block=[]; grab=False
        for ln in out.splitlines():
            if ln.startswith("━━"):
                if grab: break
                if tk in ln.split("[")[0]: grab=True
            if grab and ln.strip() and not ln.startswith("[") and not ln.startswith("Saved"): block.append(ln.strip())
        if block:
            return f"<b>📊 {tk} — 8L (DNA card, ngoài universe ranking)</b>\n"+"\n".join(block[:8])
    except Exception as e:
        return f"{tk}: lỗi tra cứu ({e})"
    return f"Không tìm thấy <b>{tk}</b> trong dữ liệu 8L. Gõ mã 3 ký tự, vd: <code>BMP</code> hoặc <code>BMP 8L</code>."

HELP=("<b>🤖 8L Bot</b>\n"
      "• Gõ <b>số</b> (vd <code>10</code>, <code>20</code>, <code>30</code>) → bảng <b>Top N</b> của 8L.\n"
      "• Gõ <code>vn30</code> → <b>rổ 8L-VN30</b> (30 mã chất lượng thanh khoản) + cổng thị trường DT5G.\n"
      "• Gõ <code>new</code> (hoặc <code>mới</code>) → mã <b>mới vào Top 30 trong tuần</b>.\n"
      "• Gõ <b>mã CP</b> (vd <code>BMP</code>, <code>BMP 8L</code>, <code>/dna VCS</code>) → ranking + nhận xét chi tiết.\n"
      "In-universe → trả lời tức thì; mã khác → dựng DNA card on-demand (vài giây).")

def handle_command(text):
    """Return a reply for the list-commands (top-N / new / vn30), or None if not a command."""
    if CMD is None: return None
    low=text.strip().lower().lstrip("/")
    if low in ("vn30","ro","rổ","basket","8lvn30"):
        return CMD.format_vn30()
    m=re.fullmatch(r"(?:top\s*)?(\d{1,3})", low)
    if m:
        return CMD.format_topn(int(m.group(1)))
    if low in ("new","mới","moi","new30","whatsnew","top","topnew") or low.startswith("new "):
        return CMD.format_new()
    return None

def main():
    print("8L bot started, polling…")
    off=None
    # skip backlog on start
    try:
        u=requests.get(f"{API}/getUpdates",params={"timeout":0},timeout=20).json()
        if u.get("result"): off=u["result"][-1]["update_id"]+1
    except Exception: pass
    while True:
        try:
            u=requests.get(f"{API}/getUpdates",params={"timeout":30,"offset":off},timeout=40).json()
            for upd in u.get("result",[]):
                off=upd["update_id"]+1
                m=upd.get("message") or upd.get("edited_message")
                if not m: continue
                chat=m["chat"]["id"]; text=(m.get("text") or "").strip()
                if not text: continue
                if text.lower() in ("/start","/help","help"):
                    send_telegram_text(TOKEN,str(chat),HELP); continue
                cmd=handle_command(text)
                if cmd is not None:
                    print(f"cmd: {text!r}")
                    send_telegram_text(TOKEN,str(chat),cmd); continue
                tk=extract_ticker(text)
                if not tk: send_telegram_text(TOKEN,str(chat),HELP); continue
                print(f"query: {text} → {tk}")
                send_telegram_text(TOKEN,str(chat),reply_for(tk))
        except KeyboardInterrupt: print("stopped"); break
        except Exception as e: print("loop err:",e); time.sleep(5)

if __name__=="__main__": main()
