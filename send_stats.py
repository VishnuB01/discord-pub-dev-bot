import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

PACKAGES = [
    "liquid_glass_container_plus",
    "radar_chart_plus"
]

def get_downloads(pkg):
    url = f"https://pub.dev/api/packages/{pkg}"
    r = requests.get(url, timeout=15)

    if r.status_code != 200:
        return "N/A"

    data = r.json()

    downloads = data.get("downloads", {})
    last_30_days = downloads.get("last30Days")

    if last_30_days is None:
        return "N/A"

    return f"{last_30_days:,} downloads (last 30 days)"


def send_message(message):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    requests.post(url, headers=headers, json={"content": message}, timeout=10)

def main():
    msg = "📊 **Daily pub.dev Stats**\n\n"
    for pkg in PACKAGES:
        msg += f"📦 `{pkg}` → {get_downloads(pkg)}\n"
    send_message(msg)

if __name__ == "__main__":
    main()
