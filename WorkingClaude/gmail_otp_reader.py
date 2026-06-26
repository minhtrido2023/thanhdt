"""Read DNSE email OTP from Gmail via Gmail API (readonly OAuth2).

One public function:
    fetch_dnse_otp(timeout=90, poll_interval=5) -> str

Requires one-time setup: run setup_gmail_oauth.py to create
secrets/gmail_oauth_token.json (gmail.readonly scope).
"""

import base64
import json
import os
import re
import time

WORKDIR = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
SECRETS_DIR = os.path.join(WORKDIR, "secrets")
TOKEN_FILE = os.path.join(SECRETS_DIR, "gmail_oauth_token.json")
LAST_ID_FILE = os.path.join(WORKDIR, "data", "gmail_otp_last_id.txt")

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# DNSE OTP email: from noreply@mail.dnse.com.vn, subject "Xác thực với Email OTP"
# OTP digits rendered as large individual characters (e.g. "1 9 4 9 5 8")
_GMAIL_QUERY = 'from:noreply@mail.dnse.com.vn subject:"Xác thực với Email OTP" newer_than:3m'
_OTP_RE = re.compile(r"\b(\d{6})\b")
_OTP_SPACED_RE = re.compile(r"(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)")


def _build_gmail_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            f"Gmail OAuth token not found at {TOKEN_FILE} — "
            f"run setup_gmail_oauth.py first"
        )
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _read_last_id():
    try:
        with open(LAST_ID_FILE) as f:
            return f.read().strip()
    except OSError:
        return None


def _save_last_id(msg_id):
    os.makedirs(os.path.dirname(LAST_ID_FILE), exist_ok=True)
    with open(LAST_ID_FILE, "w") as f:
        f.write(msg_id)


def _decode_body(payload):
    """Extract text from Gmail message payload (handles multipart)."""
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode(
            "utf-8", errors="replace"
        )
    parts = payload.get("parts", [])
    for part in parts:
        mime = part.get("mimeType", "")
        if mime == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode(
                "utf-8", errors="replace"
            )
    for part in parts:
        mime = part.get("mimeType", "")
        if mime == "text/html" and part.get("body", {}).get("data"):
            raw = base64.urlsafe_b64decode(part["body"]["data"]).decode(
                "utf-8", errors="replace"
            )
            return re.sub(r"<[^>]+>", " ", raw)
    for part in parts:
        if part.get("parts"):
            result = _decode_body(part)
            if result:
                return result
    return ""


def _extract_otp(text):
    """Find a 6-digit OTP code in text (handles spaced digits like '1 9 4 9 5 8')."""
    m = _OTP_RE.search(text)
    if m:
        return m.group(1)
    m = _OTP_SPACED_RE.search(text)
    if m:
        return "".join(m.groups())
    return None


def fetch_dnse_otp(timeout=90, poll_interval=5, sent_after=None):
    """Poll Gmail for the most recent DNSE OTP email, return the 6-digit code.

    sent_after: unix timestamp (seconds). Only accept emails with internalDate
    >= sent_after. Defaults to (time.time() - 60) so only emails from the last
    60s are accepted. Pass time.time() before calling send_email_otp() for
    precise filtering.

    NOTE: Gmail API ignores the newer_than:Xm query parameter — we filter
    by internalDate in Python instead.

    Raises TimeoutError if no OTP found within `timeout` seconds.
    """
    if sent_after is None:
        sent_after = time.time() - 60
    service = _build_gmail_service()
    last_seen = _read_last_id()
    deadline = time.monotonic() + timeout
    attempt = 0

    print(f"[gmail-otp] polling Gmail for DNSE OTP (sent_after={sent_after:.0f})...",
          flush=True)

    # Use a broad query without newer_than (it's ignored by the API anyway).
    # We filter by internalDate in Python.
    base_query = 'from:noreply@mail.dnse.com.vn subject:"Xác thực với Email OTP"'

    while time.monotonic() < deadline:
        attempt += 1
        try:
            resp = (
                service.users()
                .messages()
                .list(userId="me", q=base_query, maxResults=10)
                .execute()
            )
        except Exception as e:
            print(f"[gmail-otp] API error (attempt {attempt}): {e}", flush=True)
            time.sleep(poll_interval)
            continue

        messages = resp.get("messages", [])
        for msg_meta in messages:
            msg_id = msg_meta["id"]
            if msg_id == last_seen:
                continue
            try:
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=msg_id, format="full")
                    .execute()
                )
            except Exception as e:
                print(f"[gmail-otp] failed to read message {msg_id}: {e}", flush=True)
                continue

            # Filter by internalDate (ms since epoch)
            internal_ts = int(msg.get("internalDate", 0)) / 1000
            if internal_ts < sent_after:
                continue  # email too old

            body_text = _decode_body(msg.get("payload", {}))
            code = _extract_otp(body_text)
            if code:
                _save_last_id(msg_id)
                age_s = time.time() - internal_ts
                print(
                    f"[gmail-otp] OTP extracted (len={len(code)}, age={age_s:.0f}s) "
                    f"after {attempt} poll(s)",
                    flush=True,
                )
                return code

        if time.monotonic() + poll_interval >= deadline:
            break
        time.sleep(poll_interval)

    # Save debug info on failure
    debug_path = os.path.join(WORKDIR, "data", "gmail_otp_debug.txt")
    try:
        os.makedirs(os.path.dirname(debug_path), exist_ok=True)
        with open(debug_path, "w") as f:
            f.write(f"timeout after {attempt} attempts\n")
            f.write(f"query: {_GMAIL_QUERY}\n")
            f.write(f"last_seen: {last_seen}\n")
    except OSError:
        pass

    raise TimeoutError(
        f"No DNSE OTP found in Gmail after {timeout}s ({attempt} polls). "
        f"Check data/gmail_otp_debug.txt"
    )


if __name__ == "__main__":
    import sys

    t = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    try:
        code = fetch_dnse_otp(timeout=t)
        print(f"OTP: {code}")
    except TimeoutError as e:
        print(f"TIMEOUT: {e}", file=sys.stderr)
        sys.exit(1)
