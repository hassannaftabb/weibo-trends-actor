# Weibo UGC Lifestyle Trends Scraper

This Apify Actor scrapes **User-Generated Content (UGC)** from [Weibo](https://weibo.com), focusing on **lifestyle-related posts and hashtags**.  
It uses **Playwright + aiohttp + BeautifulSoup** to simulate real browser behavior, fetch visitor cookies, and collect trending posts safely and efficiently.

---

## Features

- Scrapes **Weibo posts** for a given query (keyword, trend, or hashtag).
- Automatically handles **authentication & session rotation** via Playwright visitor cookies.
- Extracts:
  - Post ID
  - Raw text content
  - Hashtags
  - Author details (ID, name, verification status, followers)
  - Post metrics (likes, comments, reposts)
  - Image URLs (if available)
- Concurrent asynchronous requests for **high-speed scraping**.
- Includes **session rotation & retry logic** for stability.
- Outputs data to your **Apify dataset** for further analysis or AI research.

---

## Tech Stack

- **Python 3.13 (Apify runtime)**
- **Playwright** – dynamic browser automation for cookies
- **aiohttp** – async HTTP client for scraping APIs
- **BeautifulSoup4** – HTML parsing
- **Pydantic** – strong schema validation
- **Tenacity** – automatic retry logic
- **Fake-UserAgent** – random user-agent rotation

---

## Setup

### Install dependencies & chromium

```bash
pip install -r requirements.txt
```

```bash
playwright install chromium
```

### Run locally

```bash
apify run
```

### Deploy to Apify platform

```bash
apify push
```

Apify will build your Docker image automatically using the included `Dockerfile`.

---

## Dockerfile (pre-installed Chromium)

The container uses `apify/actor-python:3.13` as the base image and installs Chromium with:

```dockerfile
RUN playwright install --with-deps chromium
```

This ensures browser-based authentication works inside the container.

---

## Input Configuration

You can pass inputs via `INPUT.json` or directly through Apify UI.

Example:

```json
{
  "query": "生活方式",
  "max_results": 20,
  "max_pages": 2,
  "concurrency": 5,
  "request_delay": 1.0
}
```

---

## Output Format

Each scraped post is stored in the Apify dataset with this structure:

```json
{
  "post_id": "5229026304069041",
  "text_raw": "最近在探索极简生活方式 #生活美学#",
  "created_at": "2025-11-03T22:34:44+08:00",
  "likes": 1240,
  "reposts": 8,
  "comments": 68,
  "pics": ["https://wx2.sinaimg.cn/orj360/...jpg"],
  "author_id": "1607260814",
  "author_name": "挥着翅膀的大尾巴螃蟹",
  "verified": false,
  "followers": 143000,
  "hashtags": ["生活美学", "极简生活"]
}
```

---

## AI / Research Use Case

The output is ideal for **training or analyzing lifestyle-related UGC trends**:

- Text-only data (no image download required)
- Ready for **topic modeling, hashtag analysis, sentiment classification**, or **semantic embedding**
- Follows a clean JSON schema for ingestion into LLM fine-tuning or retrieval pipelines

---

## Notes

- Some image URLs may be **403 Forbidden** due to Weibo CDN restrictions — they’re preserved only for metadata.
- Text content may occasionally be truncated if long-form text is behind a login wall.
- Avoid excessive scraping — follow Apify rate limits and respect Weibo’s robots.txt.

---
