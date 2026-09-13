"""aria-F: tai TOAN BO email 'Bao cao giao dich khop lenh' DNSE (phan trang, khong gioi han 20
nhu fetch_dnse_khoplenh_email.py) -> 1 CSV/ngay trong emails/ + all_fills.csv. Tai dung parser cua
tool canonical (header 'STT' dong, 'Tong cong')."""
import base64, io, os, re, sys
import pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
from gmail_otp_reader import _build_gmail_service
from fetch_dnse_khoplenh_email import _find_attachment, _SUBJECT_PREFIX
OUT = os.path.dirname(os.path.abspath(__file__))
svc = _build_gmail_service()
q = f'from:dnse.com.vn subject:"{_SUBJECT_PREFIX}" after:2026/06/28'
ids, tok = [], None
while True:
    r = svc.users().messages().list(userId="me", q=q, maxResults=100, pageToken=tok).execute()
    ids += [m["id"] for m in r.get("messages", [])]
    tok = r.get("nextPageToken")
    if not tok:
        break
print("messages:", len(ids))
frames, seen = [], {}
for mid in ids:
    msg = svc.users().messages().get(userId="me", id=mid, format="full").execute()
    subj = next(h["value"] for h in msg["payload"]["headers"] if h["name"] == "Subject")
    m = re.search(r"ngày (\d{2}/\d{2}/\d{4})", subj)
    if not m:
        print("skip subj", subj); continue
    d = m.group(1)
    part = _find_attachment(msg["payload"])
    if part is None:
        print("no attach", d); continue
    att = svc.users().messages().attachments().get(userId="me", messageId=mid, id=part["body"]["attachmentId"]).execute()
    raw = pd.read_excel(io.BytesIO(base64.urlsafe_b64decode(att["data"])), sheet_name=0, header=None)
    hr = raw[raw[0] == "STT"].index; tr = raw[raw[0] == "Tổng cộng"].index
    if len(hr) == 0 or len(tr) == 0:
        print("layout?", d, raw.head(12).to_string()); continue
    # luu header 2 dong de kiem cot
    hdr = " | ".join(str(x) for x in raw.iloc[hr[0]].tolist()) + " || " + " | ".join(str(x) for x in raw.iloc[hr[0]+1].tolist())
    data = raw.iloc[hr[0] + 2: tr[0]].copy()
    if data.shape[1] != 12:
        print("ncol", d, data.shape[1], hdr); continue
    data.columns = ["stt","ngay_gd","loai_lenh","ma","tieu_khoan","khoi_luong","gia_khop","gia_tri_khop","ty_le_phi","phi_tra_so","phi_dnse","thue"]
    data["email_date"] = d; data["msg_id"] = mid; data["hdr"] = hdr
    if d in seen:
        print("DUP email for", d, mid, seen[d]); 
    seen[d] = mid
    data.to_csv(os.path.join(OUT, "emails", f"khoplenh_{d.replace('/','-')}_{mid}.csv"), index=False)
    frames.append(data)
df = pd.concat(frames, ignore_index=True)
df.to_csv(os.path.join(OUT, "all_fills_raw.csv"), index=False)
print("rows", len(df), "dates", df.email_date.nunique()); print(df.hdr.unique())
