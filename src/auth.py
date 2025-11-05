import asyncio
import time
from apify import Actor
from playwright.async_api import async_playwright
from fake_useragent import UserAgent

COOKIE_KEY = "weibo_cookies"
COOKIE_TTL_HOURS = 12


async def fetch_visitor_cookies():
    ua = UserAgent().random
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=ua)
        page = await context.new_page()
        try:
            await page.goto("https://m.weibo.cn", wait_until="networkidle", timeout=10000)
        except Exception:
            await page.goto("https://weibo.com", wait_until="networkidle", timeout=10000)
        await asyncio.sleep(5)
        cookies = await context.cookies()
        await browser.close()
        return cookies


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
