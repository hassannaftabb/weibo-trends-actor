from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from html import unescape
import asyncio
import re

HOT_SEARCH_URL = "https://s.weibo.com/top/summary"


async def fetch_hot_hashtags(limit=20):
    """Fetch trending hashtags with fallback and timeout recovery."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(HOT_SEARCH_URL, wait_until="domcontentloaded", timeout=20000)
        except Exception:
            print("[WARN] networkidle wait failed, retrying with plain load...")
            try:
                await page.goto(HOT_SEARCH_URL, wait_until="load", timeout=20000)
            except Exception as e:
                print(f"[ERROR] Could not load Weibo hot search page: {e}")
                await browser.close()
                return []

        await asyncio.sleep(3)

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tbody tr")

    if not rows:
        print("[WARN] Hot search table not found (possibly visitor system).")
        return []

    trends = []
    for i, row in enumerate(rows[:limit]):
        link = row.select_one("td.td-02 a")
        heat_span = row.select_one("td.td-02 span")

        if link and link.text.strip():
            tag = unescape(link.text.strip())
            tag = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9#]+", "", tag)
            try:
                tag = tag.encode("latin1", "ignore").decode("gbk", "ignore")
            except Exception:
                try:
                    tag = tag.encode("latin1", "ignore").decode("utf-8", "ignore")
                except Exception:
                    pass
            if not tag or len(tag) < 2:
                continue

            heat = None
            if heat_span:
                text = heat_span.text.strip()
                try:
                    if "万" in text:
                        heat = int(float(text.replace("万", "")) * 10000)
                    else:
                        heat = int(text)
                except ValueError:
                    pass

            trends.append({"rank": i + 1, "hashtag": tag, "heat": heat})

    print(f"[INFO] Extracted {len(trends)} trending hashtags.")
    for t in trends:
        print(f"#{t['rank']}: {t['hashtag']} ({t['heat']})")

    return trends
