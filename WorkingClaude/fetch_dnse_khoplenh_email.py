"""fetch_dnse_khoplenh_email.py [--date DD/MM/YYYY] — tải + parse email "Báo cáo giao dịch khớp
lệnh" DNSE (broker-issued, gửi ~16:30 ICT mỗi phiên) thành CSV sạch: khớp lệnh THẬT theo từng dòng
(mã, tiểu khoản, khối lượng, giá khớp, phí sở/DNSE, thuế) — nguồn ĐỘC LẬP với dnse_raw_*.jsonl
(API positions/orders), dùng để đối soát fill THẬT ≠ lệnh ĐẶT (coding_guidelines §6).

Dùng chung OAuth readonly đã có cho auto-OTP (secrets/gmail_oauth_token.json) — không cần
credential mới. Đọc file trước khi wire vào pipeline báo cáo: kb/data_registry/trading-bot/
dnse_khoplenh_broker_email.md.

Output: data/execution_logs/dnse_khoplenh_broker_confirm_<DD-MM-YYYY>.csv (idempotent — chạy lại
ghi đè, không tạo trùng).

Usage:
    python3 fetch_dnse_khoplenh_email.py                  # email của HÔM NAY (giờ hệ thống)
    python3 fetch_dnse_khoplenh_email.py --date 10/08/2026 # email của 1 ngày cụ thể (dd/mm/yyyy)
"""
import argparse
import base64
import io
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

WORKDIR = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, WORKDIR)

_SUBJECT_PREFIX = "DNSE_Báo cáo giao dịch khớp lệnh tài khoản"


def _find_attachment(payload):
    for part in payload.get("parts", []) or []:
        if part.get("filename") and part.get("body", {}).get("attachmentId"):
            return part
        found = _find_attachment(part)
        if found:
            return found
    return None


def fetch_and_parse(date_str=None):
    """date_str: 'DD/MM/YYYY'. None = hôm nay (Asia/Ho_Chi_Minh). Returns (df, msg_id, xlsx_path)."""
    import pandas as pd
    from gmail_otp_reader import _build_gmail_service

    if date_str is None:
        date_str = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%d/%m/%Y")

    service = _build_gmail_service()
    query = f'from:dnse.com.vn subject:"{_SUBJECT_PREFIX}"'
    resp = service.users().messages().list(userId="me", q=query, maxResults=20).execute()
    msgs = resp.get("messages", [])

    target_msg_id = None
    for m in msgs:
        meta = service.users().messages().get(
            userId="me", id=m["id"], format="metadata", metadataHeaders=["Subject"]
        ).execute()
        subject = next(
            (h["value"] for h in meta["payload"]["headers"] if h["name"] == "Subject"), ""
        )
        if subject.strip().endswith(f"ngày {date_str}"):
            target_msg_id = m["id"]
            break

    if target_msg_id is None:
        raise FileNotFoundError(
            f"Không tìm thấy email '{_SUBJECT_PREFIX} ... ngày {date_str}' trong {len(msgs)} kết "
            f"quả gần nhất — có thể email chưa gửi (phiên chưa đóng) hoặc ngày sai định dạng."
        )

    msg = service.users().messages().get(userId="me", id=target_msg_id, format="full").execute()
    part = _find_attachment(msg["payload"])
    if part is None:
        raise ValueError(f"Email {target_msg_id} không có file đính kèm xlsx.")

    att_id = part["body"]["attachmentId"]
    att = service.users().messages().attachments().get(
        userId="me", messageId=target_msg_id, id=att_id
    ).execute()
    xlsx_bytes = base64.urlsafe_b64decode(att["data"])

    df_raw = pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name=0, header=None)
    # Hàng dữ liệu bắt đầu ngay sau 2 dòng header ("STT|Ngày GD|..." rồi "|Khối lượng|Giá khớp|...")
    # và kết thúc trước dòng "Tổng cộng" — tìm động, không hardcode chỉ số dòng (file có thể dài/ngắn
    # khác nhau tuỳ số lệnh khớp trong ngày).
    header_row = df_raw[df_raw[0] == "STT"].index
    total_row = df_raw[df_raw[0] == "Tổng cộng"].index
    if len(header_row) == 0 or len(total_row) == 0:
        raise ValueError("Không tìm thấy hàng header 'STT' hoặc hàng 'Tổng cộng' — layout đổi?")
    start = header_row[0] + 2
    end = total_row[0]

    data = df_raw.iloc[start:end].copy()
    data.columns = [
        "stt", "ngay_gd", "loai_lenh", "ma", "tieu_khoan", "khoi_luong", "gia_khop",
        "gia_tri_khop", "ty_le_phi", "phi_tra_so", "phi_dnse", "thue",
    ]
    data = data.drop(columns=["stt"]).reset_index(drop=True)
    for col in ("khoi_luong", "gia_khop", "gia_tri_khop", "ty_le_phi", "phi_tra_so",
                "phi_dnse", "thue"):
        data[col] = pd.to_numeric(data[col], errors="coerce")

    out_date = datetime.strptime(date_str, "%d/%m/%Y").strftime("%d-%m-%Y")
    out_path = os.path.join(
        WORKDIR, "data", "execution_logs", f"dnse_khoplenh_broker_confirm_{out_date}.csv"
    )
    data.to_csv(out_path, index=False)
    return data, target_msg_id, out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="DD/MM/YYYY, mặc định hôm nay (Asia/Ho_Chi_Minh)")
    args = ap.parse_args()

    try:
        df, msg_id, out_path = fetch_and_parse(args.date)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Đã lưu {len(df)} dòng khớp lệnh (email {msg_id}) → {out_path}")
    summary = (
        df.groupby(["tieu_khoan", "ma"])
        .agg(qty=("khoi_luong", "sum"), value=("gia_tri_khop", "sum"))
        .reset_index()
    )
    print(summary.to_string(index=False))
    total_qty = df["khoi_luong"].sum()
    total_value = df["gia_tri_khop"].sum()
    total_fee = df["phi_tra_so"].sum() + df["phi_dnse"].sum()
    total_tax = df["thue"].sum()
    print(f"\nTổng: {total_qty:,.0f}cp · {total_value:,.0f}đ · phí {total_fee:,.0f}đ · thuế {total_tax:,.0f}đ")


if __name__ == "__main__":
    main()
