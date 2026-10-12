#!/usr/bin/env python3
"""Mục B (CHỈ ĐỌC, OAuth gmail.readonly dùng chung với auto-OTP): DNSE có gửi email xác nhận nạp/rút
không? Liệt kê mẫu tiêu đề của MỌI email từ dnse.com.vn + vài truy vấn nhắm đích. Không tải thân thư."""
import collections, re, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from gmail_otp_reader import _build_gmail_service
svc = _build_gmail_service()

def ids(query, cap=2000):
    out, token = [], None
    while len(out) < cap:
        resp = svc.users().messages().list(userId="me", q=query, maxResults=500, pageToken=token).execute()
        out += [m["id"] for m in resp.get("messages", [])]
        token = resp.get("nextPageToken")
        if not token:
            break
    return out

def head(mid):
    msg = svc.users().messages().get(userId="me", id=mid, format="metadata",
                                     metadataHeaders=["Subject", "From", "Date"]).execute()
    h = {x["name"]: x["value"] for x in msg["payload"]["headers"]}
    return h.get("Subject", ""), h.get("From", ""), h.get("Date", "")

def norm(subject):
    s = re.sub(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", "<ngày>", subject)
    return re.sub(r"\d{3,}", "<số>", s)

all_ids = ids("from:dnse.com.vn after:2026/06/01")
print(f"== email từ dnse.com.vn sau 2026-06-01: {len(all_ids)}")
pat = collections.Counter(); sample = {}; senders = collections.Counter()
for mid in all_ids:
    subj, frm, date = head(mid)
    key = norm(subj); pat[key] += 1; sample.setdefault(key, (date, subj)); senders[re.sub(r".*<|>.*", "", frm)] += 1
print("người gửi:", dict(senders))
for key, n in pat.most_common():
    print(f"{n:5d}  {key}   | vd {sample[key][0][:16]}")
print("\n== truy vấn nhắm đích (mọi người gửi, sau 2026-06-01)")
for q in ('"nạp tiền"', '"rút tiền"', '"nộp tiền"', '"chuyển tiền"', '"biến động số dư"', '"sao kê"',
          'DNSE nạp', 'DNSE rút', '"chuyển khoản" DNSE', '"Trứng vàng"', 'subject:(nạp OR rút OR "chuyển tiền" OR "số dư")'):
    found = ids(f"{q} after:2026/06/01", cap=50)
    print(f"-- {q}: {len(found)} thư")
    for mid in found[:6]:
        subj, frm, date = head(mid)
        print(f"     {date[:16]} | {re.sub(r'.*<|>.*', '', frm)} | {subj[:110]}")
