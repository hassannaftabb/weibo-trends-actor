import asyncio
from apify import Actor
from .models import InputModel
from .auth import load_or_refresh_cookies
from .scraper import WeiboScraper
from .hot_trends import fetch_hot_hashtags
from .models import HashtagTrend, EngagementMetrics

import sys
sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        input_cfg = InputModel(**input_data)

        Actor.log.info("🚀 Starting Weibo Trending UGC Scraper")
        Actor.log.info(f"Max hashtags: {getattr(input_cfg, 'max_hashtags', 10)}")
        Actor.log.info(f"Max posts per hashtag: {getattr(input_cfg, 'max_posts_per_hashtag', 10)}")

        cookies = await load_or_refresh_cookies()
        scraper = WeiboScraper(cookies, input_cfg.max_pages, input_cfg.concurrency)

        # Step 1: Get trending hashtags
        Actor.log.info("Fetching hot trending hashtags from Weibo...")
        trending_tags = await fetch_hot_hashtags(limit=getattr(input_cfg, 'max_hashtags', 10))

        for t in trending_tags:
            Actor.log.info(f"#{t['rank']}: {t['hashtag']} (heat={t['heat']})")

        Actor.log.info(f"Found {len(trending_tags)} trending hashtags.")
        all_results = []

        # Step 2: Scrape posts for each hashtag
        for tag_info in trending_tags:
            tag = tag_info["hashtag"]
            Actor.log.info(f"🔥 Scraping posts for {tag} (rank {tag_info['rank']})")
            posts = await scraper.scrape_keyword(tag)

            Actor.log.info(f"✅ {len(posts)} posts collected for {tag}")

            engagement = EngagementMetrics(
                total_likes=sum(p.likes for p in posts),
                total_comments=sum(p.comments for p in posts),
                total_reposts=sum(p.reposts for p in posts),
                avg_engagement_rate=round(
                    sum(p.likes + p.comments + p.reposts for p in posts) / max(1, len(posts)), 2
                )
            )
            trend_data = HashtagTrend(
                hashtag=tag,
                rank=tag_info["rank"],
                heat=tag_info.get("heat"),
                total_posts=len(posts),
                engagement_metrics=engagement,
                posts=posts,
            )

            await Actor.push_data(trend_data.model_dump())
            all_results.append(trend_data.model_dump())

        Actor.log.info(f"🎯 Completed scraping {len(all_results)} trending hashtags successfully.")


if __name__ == "__main__":
    asyncio.run(main())
