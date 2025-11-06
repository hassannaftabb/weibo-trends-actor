import aiohttp
import re
from bs4 import BeautifulSoup
from .auth import load_or_refresh_cookies, cookies_to_header

MOBILE_API_URL = (
    "https://m.weibo.cn/api/container/getIndex?"
    "containerid=102803_ctg1_9999_-_ctg1_9999_home"
)


async def fetch_hot_hashtags(limit: int = 20):
    """Fetch trending hashtags from Weibo's mobile JSON API (stable global method)."""
    print("[apify] INFO  Fetching trending hashtags via Weibo mobile API...")

    cookies = await load_or_refresh_cookies()
    cookie_header = cookies_to_header(cookies)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Mobile Safari/537.36"
        ),
        "Referer": "https://m.weibo.cn/",
        "Cookie": cookie_header,
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(MOBILE_API_URL, timeout=25) as resp:
                text = await resp.text()
                if "Sina Visitor System" in text:
                    print("[WARN] Got redirected to visitor page, retrying with fresh cookies...")
                    cookies = await load_or_refresh_cookies()
                    headers["Cookie"] = cookies_to_header(cookies)
                    async with aiohttp.ClientSession(headers=headers) as s2:
                        async with s2.get(MOBILE_API_URL, timeout=25) as r2:
                            data = await r2.json(content_type=None)
                else:
                    data = await resp.json(content_type=None)
    except Exception as e:
        print(f"[ERROR] Failed to fetch from Weibo mobile API: {e}")
        return []

    cards = data.get("data", {}).get("cards", [])
    if not cards:
        print("[WARN] No cards returned from mobile API.")
        return []

    trends = []
    for card in cards:
        mblog = card.get("mblog", {})
        html_text = mblog.get("text", "")
        if not html_text:
            continue

        soup = BeautifulSoup(html_text, "html.parser")
        clean_text = soup.get_text()
        hashtags = re.findall(r"#(.*?)#", clean_text)
        for tag in hashtags:
            tag = tag.strip()
            if tag and len(tag) > 1:
                trends.append({"hashtag": tag, "heat": None})

        if len(trends) >= limit:
            break

    # hashtags dedup
    seen = set()
    unique_trends = []
    for t in trends:
        tag = t["hashtag"]
        if tag not in seen:
            unique_trends.append(t)
            seen.add(tag)

    print(f"[INFO] Extracted {len(unique_trends)} trending hashtags from mobile API.")
    for i, t in enumerate(unique_trends[:limit], start=1):
        print(f"#{i}: {t['hashtag']}")

    return unique_trends[:limit]
