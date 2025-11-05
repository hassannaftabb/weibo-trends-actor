import asyncio
import aiohttp
import random
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from apify import Actor
from fake_useragent import UserAgent
from .models import PostModel
from .auth import cookies_to_header
from bs4 import BeautifulSoup
import re


class WeiboScraper:
    BASE_URL = "https://m.weibo.cn/api/container/getIndex"

    def __init__(self, cookies, max_pages=3, concurrency=5):
        self.cookies = cookies
        self.cookie_header = cookies_to_header(cookies)
        self.max_pages = max_pages
        self.concurrency = concurrency
        self.ua = UserAgent().random

    @staticmethod
    def _extract_text_and_hashtags(html_text: str):
        """Clean HTML text and extract hashtags like #护肤#."""
        if not html_text:
            return "", []
        soup = BeautifulSoup(html_text, "html.parser")
        cleaned = soup.get_text().strip()
        hashtags = re.findall(r"#(.*?)#", cleaned)
        return cleaned, hashtags

    @staticmethod
    def _parse_followers(val):
        """Convert follower count strings like '264.4万' or '1.2亿' to integers."""
        if isinstance(val, int):
            return val
        if isinstance(val, str):
            val = val.replace(",", "").strip()
            if val.endswith("万"):
                try:
                    return int(float(val[:-1]) * 10000)
                except ValueError:
                    return 0
            if val.endswith("亿"):
                try:
                    return int(float(val[:-1]) * 100000000)
                except ValueError:
                    return 0
            try:
                return int(float(val))
            except ValueError:
                return 0
        return 0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def _fetch_page(self, session, keyword: str, since_id: Optional[str] = None):
        params = {
            "containerid": f"100103type=1&q={keyword}&t=2",
        }
        if since_id:
            params["since_id"] = since_id

        headers = {
            "User-Agent": self.ua,
            "Cookie": self.cookie_header,
            "Referer": "https://m.weibo.cn/",
            "Accept": "application/json, text/plain, */*",
        }

        async with session.get(self.BASE_URL, headers=headers, params=params) as resp:
            if resp.status != 200:
                Actor.log.warning(f"HTTP {resp.status} for keyword {keyword}")
                return {}
            return await resp.json()

    async def scrape_keyword(self, keyword: str) -> List[PostModel]:
        results = []
        since_id = None
        page = 1

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while page <= self.max_pages:
                data = await self._fetch_page(session, keyword, since_id)
                if not data or data.get("ok") != 1:
                    break

                cards = data["data"].get("cards", [])
                if not cards:
                    break

                for card in cards:
                    m = card.get("mblog")
                    if not m:
                        continue                    

                    clean_text, hashtags = self._extract_text_and_hashtags(m.get("text", ""))

                    post = PostModel(
                        post_id=m["id"],
                        text_raw=clean_text,
                        created_at=m.get("created_at", ""),
                        likes=m.get("attitudes_count", 0),
                        reposts=m.get("reposts_count", 0),
                        comments=m.get("comments_count", 0),
                        pics=[p["url"] for p in m.get("pics", [])],
                        author_id=str(m["user"]["id"]),
                        author_name=m["user"]["screen_name"],
                        verified=m["user"].get("verified", False),
                        followers=self._parse_followers(m["user"].get("followers_count", 0)),
                        hashtags=hashtags,
                    )
                    results.append(post)

                since_id = data["data"].get("since_id")
                if not since_id:
                    break
                page += 1
                await asyncio.sleep(random.uniform(1, 2))

        return results

