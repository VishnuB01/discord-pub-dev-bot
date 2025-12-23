import os
import json
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

PACKAGES = [
    "liquid_glass_container_plus",
    "radar_chart_plus"
]

STATS_FILE = "stats.json"


def load_previous_stats():
    if not os.path.exists(STATS_FILE):
        return {}
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_current_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)


def get_downloads(pkg):
    url = f"https://pub.dev/api/packages/{pkg}/metrics"
    r = requests.get(url, timeout=15)

    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch metrics for {pkg}")

    data = r.json()
    return data["score"]["downloadCount30Days"]


def format_delta(today, yesterday):
    if yesterday is None:
        return "🆕 first run"
    diff = today - yesterday
    if diff > 0:
        return f"📈 +{diff}"
    if diff < 0:
        return f"📉 {diff}"
    return "➖ no change"


def send_message(message):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    requests.post(url, headers=headers, json={"content": message}, timeout=10)


def main():
    previous_stats = load_previous_stats()
    current_stats = {}

    msg = "📊 **Daily pub.dev Stats**\n"
    msg += f"🗓 {datetime.now().strftime('%d %b %Y')}\n\n"

    for pkg in PACKAGES:
        today = get_downloads(pkg)
        yesterday = previous_stats.get(pkg)

        delta_text = format_delta(today, yesterday)

        msg += f"📦 `{pkg}` → {today:,} ({delta_text})\n"
        current_stats[pkg] = today

    send_message(msg)
    save_current_stats(current_stats)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        send_message(f"❌ **Daily Stats Error**\n```\n{str(e)}\n```")
        raise
