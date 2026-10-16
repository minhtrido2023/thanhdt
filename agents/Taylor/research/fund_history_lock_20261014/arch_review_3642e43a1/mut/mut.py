import os, shutil, subprocess, sys, tempfile
SRC="/tmp/arch_fl/wt/bin"; EMPTY="/tmp/arch_fl/empty"
L,F,S="nav_unit_ledger.py","fund_restatement.py","daily_nav_snapshot.py"
V,R,U,FR="nav_ledger_vault_selfcheck.py","fund_restatement_selfcheck.py","nav_unit_ledger_selfcheck.py","daily_nav_snapshot_from_raw_selfcheck.py"
M=[
("N1",L,"fcntl.flock(lock, fcntl.LOCK_EX)\n        try:\n            if immutable:","pass\n        try:\n            if immutable:","seal: bỏ khoá flock",(V,U)),
("N2",L,"        fcntl.flock(lock, fcntl.LOCK_EX)\n        try:\n            old, sealed, manifest, resumed","        pass\n        try:\n            old, sealed, manifest, resumed","restate: bỏ khoá flock",(V,)),
("N3",L,'for key in ("seq", "kind", "md5", "md5_before", "rows_total", "last_date"):','for key in ():',"manifest: không kiểm khoá bắt buộc",(V,)),
("N6",L,"want = d if session else _acf._last_session_closed_by(","want = d if True else _acf._last_session_closed_by(","cổng: dòng ngày không phiên phải chụp đúng ngày đó",(V,)),
("N8",L,'if row["balance_ts"] is None and d == ledger[0]["date"]:','if row["balance_ts"] is None:',"cổng: mọi dòng thiếu balance_ts bỏ qua",(V,)),
("N10",L,'if not any(p.startswith(f"--accept-preclose {k}:") for k in carried\n                                   if k not in (accept_preclose or {}))]','if True]',"restate: không lọc lời nhận cũ hết hiệu lực",(V,)),
("N12",L,"n_diffs=len(diffs), diffs=diffs[:200],","n_diffs=len(diffs), diffs=[],","restate: manifest không ghi chi tiết dòng lệch",(V,)),
("N13",L,"impact_report_md5=_md5(report_bytes),","impact_report_md5=None,","restate: manifest không ghi md5 báo cáo tác động",(V,)),
("N14",L,"return (os.path.realpath(os.path.dirname(os.path.abspath(path)))\n            == os.path.realpath(NAV_HISTORY_DIR))","return (os.path.dirname(path) == NAV_HISTORY_DIR)","thư mục thật: bỏ realpath (symlink/../ lách)",(V,U)),
("N16",L,"immutable=True if args.immutable else None,","immutable=None,","CLI: --immutable bị bỏ qua",(V,)),
("N17",L,"    except SealRefused as e:\n        print(f\"nav_unit_ledger ({args.account}): {e}\", file=sys.stderr)\n        return 3","    except SealRefused as e:\n        print(f\"nav_unit_ledger ({args.account}): {e}\", file=sys.stderr)\n        return 2","CLI: SealRefused rc 3→2",(V,U)),
("N18",L,'meta = {"account": args.account, "tool": "nav_unit_ledger.py",','meta = {"account": None, "tool": "nav_unit_ledger.py",',"CLI: meta không mang tài khoản (restate CLI luôn từ chối)",(V,)),
("N20",L,"upto = asof or cutoff","upto = asof or ledger[-1][\"date\"]","seal không --asof: chốt cả dòng hôm nay",(V,)),
("N21",L,"problems, accepted = seal_gate(ledger, last if last is not None else new[0][\"date\"],","problems, accepted = seal_gate(ledger, new[0][\"date\"],","cổng: không kiểm thiếu phiên ngay sau dòng đã chốt cuối",(V,)),
("N22",L,'base = old if old is not None else (",".join(LEDGER_FIELDS) + "\\n").encode("utf-8")','base = (",".join(LEDGER_FIELDS) + "\\n").encode("utf-8")',"seal lần 2 ghi đè mất dòng cũ",(V,)),
("N23",L,'if rec["kind"] == "restate":\n        return _content(ledger, upto)','if False:\n        return _content(ledger, upto)',"hoàn tất restate dở bằng công thức seal",(V,)),
("N24",L,'rows_added=len(new), rows_total=len(sealed) + len(new),','rows_added=len(new), rows_total=len(new),',"manifest rows_total sai",(V,)),
("G1",F,'return [whole.replace(",", "."), whole, whole.replace(",", "")]','return [whole]',"literal: chỉ tìm dạng 1,234,567",(R,V)),
("G5",F,"        if nav_dev or ret_dev:\n","        if nav_dev:\n","window: ngày chỉ đổi tỉ suất không được kể",(R,V)),
("G7",F,'look = [r for r in affected if r["needs_human_look"] and r["tier_headline"] < 3]','look = [r for r in affected if r["needs_human_look"]]',"hàng đợi user trùng bậc 3",(R,V)),
("G9",F,"end = datetime.date(year, month, calendar.monthrange(year, month)[1])","end = start","báo cáo tháng YYYY-MM: kỳ chỉ ngày 1",(R,V)),
("G10",F,"                start = end.replace(day=1)","                start = end","báo cáo tháng tên 1 ngày: kỳ chỉ 1 ngày",(R,V)),
("G11",F,'if _md5(cur_bytes) == bound[3] and all(c.get("already") for c in changes):','if all(c.get("already") for c in changes):',"apply: 'đã áp' không kiểm md5",(R,V)),
("G14",F,"    if not pending:\n        with open(log, \"a\", encoding=\"utf-8\") as f:","    if False:\n        with open(log, \"a\", encoding=\"utf-8\") as f:","apply: không ghi nhật ký",(R,V)),
("G15",F,'"approved_by": args.approved_by.strip(), "correction_md5": correction_md5,','"approved_by": "", "correction_md5": correction_md5,',"apply: nhật ký mất người duyệt",(R,V)),
("G16",F,'"changes": [dict(c, reason=i["reason"], evidence=i["evidence"])','"changes": [dict(c, reason="", evidence="")',"apply: nhật ký mất lý do/bằng chứng",(R,V)),
("G17",F,"        datetime.datetime.fromisoformat(row[\"balance_ts\"])\n    except ValueError as exc:\n        raise RestatementError(f\"{where}: balance_ts","        pass\n    except ValueError as exc:\n        raise RestatementError(f\"{where}: balance_ts","_check_row: balance_ts rác được nhận",(R,V)),
("G19",F,'if item["op"] in ("replace", "delete") and not isinstance(item.get("expect"), dict):','if item["op"] in ("replace",) and not isinstance(item.get("expect"), dict):',"delete không cần expect",(R,V)),
("G20",F,"                if out[idx] == row:","                if True:","insert đè ngày đã có (khác giá trị) coi như đã áp",(R,V)),
("G21",F,'if unknown or "date" in item["set"]:','if unknown:',"replace được đổi cột date",(R,V)),
("G24",F,'"weekly": ("wtd", "mtd", "inception"),','"weekly": ("wtd",),',"báo cáo tuần không đo MTD/từ đầu",(R,V)),
("G25",F,"            if a[key] is None or b[key] is None:\n                out[\"headline\"][key] = {\"old\": a[key], \"new\": b[key], \"dev_pp\": None}\n                devs.append(float(\"inf\"))","            if a[key] is None or b[key] is None:\n                out[\"headline\"][key] = {\"old\": a[key], \"new\": b[key], \"dev_pp\": None}\n                devs.append(0.0)","số chính có/mất kỳ ⇒ bậc 0",(R,V)),
("G26",F,"            pending = all(last.get(k) == record[k] for k in key)","            pending = all(last.get(k) == record[k] for k in key[:1])","apply: nhận nhầm bản ghi nhật ký của đính chính khác là 'dở'",(R,V)),
("Sa",S,"            if t in cash_div_confirmed:\n                d = cash_div_confirmed[t]","            if t in price_overrides:\n                continue\n            if t in cash_div_confirmed:\n                d = cash_div_confirmed[t]","giá thay KHÔNG qua cổng lệch 5%",(V,FR)),
("Sb",S,'f"({args.raw_price_evidence.strip()})")','f"")',"ghi chú giá thay mất bằng chứng",(V,FR)),
("Sc",S,"        if unknown:\n            print(f\"❌ [{args.date}] --raw-price-override","        if False:\n            print(f\"❌ [{args.date}] --raw-price-override","mã không giữ không bị chặn (giữ chuỗi)",(V,FR)),
("Sd",S,"sorted(price_overrides.items())))","[]))","nav_source không ghi giá thay",(V,FR)),
("Se",S,"            prices[t] = p_new\n","            prices[t] = p_new\n            prices[t] = prev_prices.get(t, p_new)\n","giá thay bị ghi đè bằng giá phiên trước",(V,FR)),
("Sf",S,"            return 2\n        price_override_notes = []","            pass\n        price_override_notes = []","mã không giữ: in lỗi nhưng vẫn chạy tiếp",(V,FR)),
("Sg",S,'if out and not str(evidence or "").strip():','if out and evidence is None:',"bằng chứng chỉ khoảng trắng được nhận",(V,FR)),
("Sh",S,"            prices[t] = p_new\n","            prices[t] = p_new if t not in prices else prices[t]\n","giá thay bị bỏ qua khi BQ có giá (luôn)",(V,FR)),
]
only=set(sys.argv[1:])
res=[]
for mid,fn,old,new,desc,scs in M:
    if only and mid not in only: continue
    d=tempfile.mkdtemp(prefix="mut_",dir="/tmp/arch_fl/mut")
    shutil.copytree(SRC,d+"/bin")
    p=d+"/bin/"+fn; s=open(p,encoding="utf-8").read()
    n=s.count(old)
    if n!=1:
        res.append((mid,"LỖI-DỰNG(%d)"%n,fn,desc,"")); shutil.rmtree(d); continue
    open(p,"w",encoding="utf-8").write(s.replace(old,new))
    dead=None
    for sc in scs:
        env=dict(os.environ,WC_ROOT=EMPTY); env.pop("TZ",None)
        r=subprocess.run([sys.executable,d+"/bin/"+sc],cwd="/tmp",env=env,capture_output=True,text=True,timeout=300)
        if r.returncode!=0:
            fl=[l for l in (r.stdout+r.stderr).splitlines() if "FAIL" in l or "Error" in l]
            dead=f"{sc} rc={r.returncode}: {(fl[0] if fl else (r.stdout+r.stderr).strip().splitlines()[-1:] )}"[:220]; break
    res.append((mid,"chết" if dead else "SỐNG",fn,desc,dead or ""))
    shutil.rmtree(d)
    print(res[-1],flush=True)
print("\nTỔNG", len(res), "chết", sum(r[1]=="chết" for r in res), "SỐNG", sum(r[1]=="SỐNG" for r in res), "lỗi", sum(r[1].startswith("LỖI") for r in res))
for r in res:
    if r[1]!="chết": print(r[0],r[1],r[2],r[3])
