# Weibo UGC Trends Scraper

This Apify Actor scrapes **User-Generated Content (UGC)** from [Weibo](https://weibo.com) to uncover **lifestyle trends, topics, and engagement metrics** across China’s most popular social platform.
It leverages **Playwright**, **aiohttp**, and **BeautifulSoup** for dynamic page rendering, session handling, and structured data extraction.

---

## Features

- Collects **real-time Weibo UGC** by trending topic, hashtag, or keyword.
- Automatically handles **session creation and rotation** via Playwright visitor cookies.
- Extracts detailed **post-level data**, including:

  - Post ID, raw text, creation time
  - Hashtags and attached images
  - Author metadata (ID, name, verification, follower count)
  - Engagement metrics (likes, reposts, comments, engagement score)

- Built-in **asynchronous concurrency** for fast, parallel scraping.
- **Retry & cookie refresh logic** for resilience against anti-bot measures.
- Saves output to your **Apify dataset** in a clean, analysis-ready JSON schema.

---

## Tech Stack

| Component                       | Purpose                                |
| ------------------------------- | -------------------------------------- |
| **Python 3.13 (Apify runtime)** | Base environment                       |
| **Playwright**                  | Browser automation & cookie generation |
| **aiohttp**                     | Asynchronous HTTP requests             |
| **BeautifulSoup4**              | DOM parsing and data extraction        |
| **Pydantic**                    | Schema validation and data integrity   |
| **Tenacity**                    | Automatic retry policy                 |
| **Fake-UserAgent**              | User-agent randomization               |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Chromium (required by Playwright)

```bash
playwright install --with-deps chromium
```

### 3. Run locally

```bash
apify run
```

### 4. Deploy to Apify

```bash
apify push
```

Apify will automatically build your Docker image and run the scraper in the cloud.

---

## Dockerfile (pre-installed Chromium)

Your container already includes:

```dockerfile
FROM apify/actor-python:3.13
RUN playwright install --with-deps chromium
```

This ensures cookie generation and dynamic page rendering work inside Apify’s sandbox.

---

## Input Configuration

Pass configuration in `INPUT.json` or via the Apify UI:

```json
{
  "query": "生活方式",
  "max_hashtags": 10,
  "max_posts_per_hashtag": 10,
  "concurrency": 5,
  "request_delay": 1.0
}
```

| Field                   | Description                          | Default      |
| ----------------------- | ------------------------------------ | ------------ |
| `query`                 | Keyword or hashtag to search for     | `"生活方式"` |
| `max_hashtags`          | Number of trending hashtags to fetch | 10           |
| `max_posts_per_hashtag` | Max posts to scrape per tag          | 10           |
| `concurrency`           | Parallel request limit               | 5            |
| `request_delay`         | Delay between requests (seconds)     | 1.0          |

---

## Output Format

Each dataset record follows this schema:

```json
{
  "post_id": "5229026304069041",
  "text_raw": "最近在探索极简生活方式 #生活美学#",
  "created_at": "2025-11-03T22:34:44+08:00",
  "likes": 1240,
  "reposts": 8,
  "comments": 68,
  "engagement_score": 1392,
  "pics": ["https://wx2.sinaimg.cn/orj360/...jpg"],
  "author_id": "1607260814",
  "author_name": "挥着翅膀的大尾巴螃蟹",
  "verified": false,
  "followers": 143000,
  "hashtags": ["生活美学", "极简生活"],
  "source_hashtag": "生活方式",
  "collected_at": "2025-11-05T16:14:12Z"
}
```

---

## Output Views

After the run, Apify provides multiple dataset views:

| View                 | Description                                             |
| -------------------- | ------------------------------------------------------- |
| `overview`           | Summary of authors, text snippets, and engagement stats |
| `lifestyle_trends`   | Lifestyle-focused posts (护肤, 健身, 旅行, 穿搭, 美食)  |
| `engagement_summary` | Aggregated engagement metrics by trend                  |
| `raw_data`           | Complete raw dataset                                    |

---

## Research & AI Use Cases

Perfect for **data scientists, brand analysts, and AI researchers** studying social trends or building datasets for fine-tuning.

Use cases:

- Topic modeling & semantic clustering
- Hashtag co-occurrence graphs
- Sentiment and lifestyle category classification
- Engagement analysis & influencer scoring
- Cross-domain LLM training data (Chinese social corpus)

---

## Notes

- Image URLs may occasionally return `403` due to CDN restrictions — metadata is preserved for reference.
- Some posts with long-form text or media may require login and can be truncated.
- Respect Weibo’s usage policies and Apify’s rate limits — this actor is optimized for **non-intrusive research scraping**.
