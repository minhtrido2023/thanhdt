"""One-time setup: authorize Gmail readonly access and save the OAuth2 refresh token.

Usage:
    python setup_gmail_oauth.py                  # opens browser on local machine
    python setup_gmail_oauth.py --port 8080      # fixed port (for SSH tunnel)

Prerequisites:
    1. Enable Gmail API in GCP Console (project lithe-record-440915-m9)
    2. Create OAuth2 client ID (Desktop app) → download JSON
    3. Save as secrets/gmail_client_secret.json
"""

import argparse
import json
import os
import stat
import sys

WORKDIR = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
SECRETS_DIR = os.path.join(WORKDIR, "secrets")
CLIENT_SECRET_FILE = os.path.join(SECRETS_DIR, "gmail_client_secret.json")
TOKEN_FILE = os.path.join(SECRETS_DIR, "gmail_oauth_token.json")

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    ap = argparse.ArgumentParser(description="Setup Gmail OAuth2 for DNSE OTP reader")
    ap.add_argument(
        "--port",
        type=int,
        default=0,
        help="local server port for OAuth callback (0=random; use fixed port for SSH tunnel)",
    )
    args = ap.parse_args()

    if not os.path.exists(CLIENT_SECRET_FILE):
        print(
            f"ERROR: {CLIENT_SECRET_FILE} not found.\n\n"
            f"Steps:\n"
            f"  1. Go to https://console.cloud.google.com/apis/credentials"
            f"?project=lithe-record-440915-m9\n"
            f"  2. Create Credentials → OAuth client ID → Desktop app\n"
            f"  3. Download JSON → save as {CLIENT_SECRET_FILE}\n"
        )
        return 1

    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=args.port, open_browser=False)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 600
    print(f"\nToken saved to {TOKEN_FILE} (chmod 600)")

    # Quick test — list 1 recent email
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    resp = service.users().messages().list(userId="me", maxResults=1).execute()
    msgs = resp.get("messages", [])
    if msgs:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msgs[0]["id"], format="metadata")
            .execute()
        )
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        print(f"Test OK — latest email: {headers.get('Subject', '(no subject)')}")
    else:
        print("Test OK — inbox empty (access works)")

    print("\nSetup complete. gmail_otp_reader.py is ready to use.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
