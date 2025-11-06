import asyncio
import time
from apify import Actor
from playwright.async_api import async_playwright
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_fixed

COOKIE_KEY = "weibo_cookies"
COOKIE_TTL_HOURS = 12

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
async def fetch_visitor_cookies():
    ua = UserAgent().random
    Actor.log.info("Launching Playwright to fetch visitor cookies...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = await browser.new_context(user_agent=ua)
        page = await context.new_page()

        urls = [
            "https://m.weibo.cn/",
            "https://weibo.com/",
            "https://s.weibo.com/top/summary"
        ]

        for url in urls:
            try:
                Actor.log.info(f"Trying to load {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(5)
                cookies = await context.cookies()
                if cookies:
                    await browser.close()
                    Actor.log.info(" Successfully fetched cookies.")
                    return cookies
            except Exception as e:
                Actor.log.warning(f"Failed to load {url}: {str(e)}")
                continue

        await browser.close()
        raise RuntimeError("All attempts to fetch Weibo cookies failed.")


async def load_or_refresh_cookies():
    store = await Actor.get_value(COOKIE_KEY)
    if store:
        age_hours = (time.time() - store["_created"]) / 3600
        if age_hours < COOKIE_TTL_HOURS:
            Actor.log.info("Using cached visitor cookies.")
            return store["cookies"]

    Actor.log.info("Fetching new visitor cookies...")
    cookies = await fetch_visitor_cookies()
    await Actor.set_value(COOKIE_KEY, {"cookies": cookies, "_created": time.time()})
    return cookies


def cookies_to_header(cookies):
    return "; ".join(f"{c['name']}={c['value']}" for c in cookies)
