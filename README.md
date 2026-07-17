# Book Highlights

Webpage that displays highlights saved from KOReader via Telegram bot.

## Setup (GitHub Pages)

1. Push this repo to GitHub
2. Enable **GitHub Pages** in Settings → Pages → Source: **Deploy from a branch**, Branch: `main`, folder: `/` (root)

---

## Getting your highlights in

### One-time import (already done)

Export your Telegram chat with @bookshotsbot as JSON (Telegram Desktop → Settings → Advanced → Export Telegram data), place `result.json` here, and run:

```
python3 parse_export.js
```

---

### Automatic sync via GitHub Actions (recommended)

The repo includes a workflow (`.github/workflows/sync.yml`) that runs every 6 hours. It uses [Telethon](https://github.com/LonamiWebs/Telethon) to log into your Telegram account, read new messages from @bookshotsbot, and commit them to `highlights.json`.

#### Step 1: Get Telegram API credentials

Go to https://my.telegram.org → **API Development tools** → create an app. You'll get:

- **API ID** (a number)
- **API Hash** (a string)

#### Step 2: Authenticate locally (creates the session)

Run this on your computer (one time only):

```
pip install telethon
TG_API_ID=<your-api-id> TG_API_HASH=<your-api-hash> python3 sync.py --phone <your-phone>
```

Example with real values:

```
TG_API_ID=1234567 TG_API_HASH=a1b2c3d4e5f6g7h8i9j0 python3 sync.py --phone +34123456789
```

You'll be prompted for the OTP code sent to your Telegram app. After success, a file called `telegram_session.session` is created locally.

#### Step 3: Encode the session for GitHub

```
base64 telegram_session.session
```

Copy the output (a long base64 string).

#### Step 4: Add secrets to your GitHub repo

Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

Add these three secrets:

| Secret | Value |
|---|---|
| `TG_API_ID` | The number from my.telegram.org |
| `TG_API_HASH` | The string from my.telegram.org |
| `TG_SESSION_B64` | The base64 output from Step 3 |

#### Step 5: Push the repo

After pushing, the workflow runs automatically every 6 hours. You can also trigger it manually: **Actions** → **Sync highlights from Telegram** → **Run workflow**.

Each run fetches new messages from @bookshotsbot, deduplicates, and commits to `highlights.json`. GitHub Pages picks up the changes automatically.

> **Note:** The Telegram session expires after a while (weeks to months). When the workflow starts failing, re-run Step 2 and Step 3 locally, then update the `TG_SESSION_B64` secret.

---

### Manual local sync

If you prefer not to set up GitHub Actions, run the script manually whenever you want:

```
TG_API_ID=<api-id> TG_API_HASH=<api-hash> python3 sync.py
```

It deduplicates and updates `highlights.json`. Then commit and push.

---

### Modify KOReader plugin (alternative)

Edit `telegramhighlights.koplugin/main.lua` on your device and add a second HTTP POST to your own endpoint after it sends to the bot. Quickest path if you're comfortable editing Lua.

---

## File structure

```
├── index.html                    # GitHub Pages webpage
├── highlights.json               # JSON array of highlights
├── parse_export.js               # One-time import from Telegram export
├── sync.py                       # Telethon-based sync script
├── .github/workflows/sync.yml    # GitHub Action for auto-sync
└── README.md
```

## JSON format

```json
{
  "text": "The highlighted text content",
  "title": "Book title",
  "author": "Book author",
  "timestamp": "2025-11-15T10:30:00.000Z"
}
```
