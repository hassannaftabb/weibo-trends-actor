from pydantic import BaseModel, Field
from typing import List, Optional

class InputModel(BaseModel):
    max_hashtags: int = Field(default=10, ge=1, le=50, description="How many trending hashtags to fetch")
    max_posts_per_hashtag: int = Field(default=10, ge=1, le=50, description="How many posts to scrape per hashtag")
    max_pages: int = Field(default=3, ge=1, le=10, description="How many pages per hashtag to scrape")
    concurrency: int = Field(default=5, ge=1, le=20, description="Concurrent scraping threads")

class EngagementMetrics(BaseModel):
    total_likes: int = Field(..., description="Total likes across all posts for a hashtag")
    total_comments: int = Field(..., description="Total comments across all posts for a hashtag")
    total_reposts: int = Field(..., description="Total reposts across all posts for a hashtag")
    avg_engagement_rate: float = Field(..., description="Average engagement rate per post")


class PostModel(BaseModel):
    post_id: str
    text_raw: str
    created_at: str
    likes: int
    reposts: int
    comments: int
    pics: List[str]
    author_id: str
    author_name: str
    verified: bool
    followers: int
    hashtags: Optional[List[str]] = []


class HashtagTrend(BaseModel):
    hashtag: str
    rank: int
    heat: Optional[int]
    total_posts: int
    engagement_metrics: EngagementMetrics
    posts: List[PostModel]