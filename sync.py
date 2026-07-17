"""
Sync highlights from @bookshotsbot to highlights.json.

First run (authenticate):
  python sync.py --phone <your-number>

Subsequent runs reuse the session file automatically.
Commit highlights.json to GitHub after each run.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

HIGHLIGHTS_FILE = Path(__file__).parent / "highlights.json"
SESSION_FILE = Path(__file__).parent / "telegram_session"

async def main():
    from telethon import TelegramClient, events

    api_id = int(os.environ["TG_API_ID"])
    api_hash = os.environ["TG_API_HASH"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--phone")
    args = parser.parse_args()

    phone = args.phone or os.environ.get("TG_PHONE")
    bot_token = os.environ.get("TG_BOT_TOKEN")

    client = TelegramClient(str(SESSION_FILE), api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        if not phone and not bot_token:
            print("No valid session and no credentials provided. To fix:")
            print("  - Set TG_SESSION_B64 secret (session file)")
            print("  - Or pass --phone <number> / TG_PHONE")
            print("  - Or set TG_BOT_TOKEN")
            sys.exit(1)
        await client.start(phone=phone, bot_token=bot_token)

    bot = await client.get_entity("@bookshotsbot")

    # Load existing highlights for dedup
    existing = []
    if HIGHLIGHTS_FILE.exists():
        existing = json.loads(HIGHLIGHTS_FILE.read_text())
    seen = {h["text"] + "|" + (h.get("title") or "") for h in existing}

    new_highlights = []
    async for msg in client.iter_messages(bot, limit=200):
        if not msg.text or not msg.text.strip():
            continue

        text_entities = getattr(msg, "entities", None) or []
        parsed = parse_highlight(msg.text, text_entities)
        if not parsed:
            continue

        key = parsed["text"] + "|" + (parsed.get("title") or "")
        if key in seen:
            continue
        seen.add(key)
        parsed["timestamp"] = msg.date.isoformat()
        new_highlights.append(parsed)

    if not new_highlights:
        print("No new highlights found.")
        return

    all_h = new_highlights + existing
    all_h.sort(key=lambda h: h.get("timestamp", ""), reverse=True)
    HIGHLIGHTS_FILE.write_text(json.dumps(all_h, indent=2, ensure_ascii=False))
    print(f"Added {len(new_highlights)} new highlight(s). Total: {len(all_h)}")


def parse_highlight(text, entities):
    """Parse a Telegram message from @bookshotsbot into {text, title, author}."""
    parts = {"blockquote": "", "italic": "", "bold": ""}
    for e in entities:
        t = type(e).__name__
        chunk = text[e.offset : e.offset + e.length].strip()
        if "Blockquote" in t:
            parts["blockquote"] += chunk + "\n"
        elif "Bold" in t:
            parts["bold"] = chunk
        elif "Italic" in t:
            parts["italic"] = chunk

    text = parts["blockquote"].strip()
    if not text:
        return None

    return {
        "text": text,
        "title": parts["italic"],
        "author": parts["bold"],
    }


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
