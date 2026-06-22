# Discord ⇄ Claude Code bridge

Talk to a Claude Code session on this server from Discord. Each Discord
channel / thread / DM is its own persistent Claude conversation, running
headless (`claude -p --resume`) in `work_dir`.

```
Discord msg ─▶ bot.py ─▶ claude -p --resume <sid> --add-dir <work_dir> ─▶ .result ─▶ Discord
```

## One-time setup

### 1. Create the Discord app + bot
1. https://discord.com/developers/applications → **New Application** → name it.
2. Left sidebar **Bot** → **Add Bot** → **Reset Token** → copy the token.
3. On the Bot page, enable **MESSAGE CONTENT INTENT** (required), and
   **SERVER MEMBERS INTENT** is optional. Save.
4. Left sidebar **OAuth2 → URL Generator**: scopes = `bot`; bot permissions =
   `View Channels`, `Send Messages`, `Read Message History`,
   `Add Reactions`, `Create Public Threads` (and `Send Messages in Threads`).
   Open the generated URL and invite the bot to your server.

### 2. Configure
Edit `config.json` (gitignored — holds the token):
- `discord_token`: the token from step 1.2.
- `allowed_user_ids`: **required**. Leave empty for now.

### 3. Install deps + run
```bash
cd /home/trido/thanhdt/discord_bot
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python bot.py            # foreground test
```

### 4. Lock it to you
In Discord, send **`!whoami`** in any channel the bot can see — it replies with
your `user_id` and `channel_id`. Put your `user_id` into `allowed_user_ids` in
`config.json` (restart the bot). Until then the bot serves **no one** (deny-all),
except `!whoami`.

### 5. Run as a service (auto-start, auto-restart)
```bash
sudo cp discord-claude-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now discord-claude-bot
journalctl -u discord-claude-bot -f      # live logs
```

## Usage
- Message the bot (in a channel it can see, a thread, or a DM). It runs Claude
  in `work_dir` and replies. **Use a thread per topic** — each thread keeps its
  own conversation/session.
- `!reset` — start a fresh Claude session in this channel/thread.
- `!whoami` — show your user/channel IDs.
- `!help` — quick help.

## Security
- Access is gated to `allowed_user_ids`. Empty = deny-all.
- `permission_mode: bypassPermissions` means Claude can read/edit/run anything
  as user `trido` (not root) inside `work_dir`. A Discord message from an
  allowlisted user therefore has full shell power on this box — keep the
  allowlist to yourself and the bot in a private channel.
- The bot token is a secret; `config.json` is gitignored.

## Config reference
See `config.example.json`. Notable: `permission_mode`
(`bypassPermissions|acceptEdits|auto|dontAsk|plan`), `model` (e.g.
`claude-opus-4-8`), `require_mention`, `allowed_channel_ids`, `timeout_seconds`.
