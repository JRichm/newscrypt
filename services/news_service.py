import requests
import random
from typing import Optional, Dict, Any
from config import (
    NEWS_API_KEY,
    NEWS_PAGE_SIZE,
    NEWS_COUNTRY,
    NEWS_LANGUAGE
)


class NewsService:
    """Service for fetching trending news articles"""

    def __init__(self):
        self.api_key = NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"

    
    def get_trending_topic(self) -> Optional[Dict[str, Any]]:
        """Fetch trending news articles from News API"""
        
        if not NEWS_API_KEY:
            print("NEWS_API_KEY not found in environment variables")
            return None
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "language": NEWS_LANGUAGE,
                "pageSize": NEWS_PAGE_SIZE,
                "country": NEWS_COUNTRY
            }
            headers = {"X-API-Key": self.api_key}

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            articles = response.json().get("articles", [])

            valid_articles = [
                article for article in articles
                if article.get("description") and article.get("title")
            ]

            return random.choice(valid_articles) if valid_articles else None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in get_trending_topic: {e}")
            return None


    def search_news(self, query: str, page_size: int = 5) -> Optional[list]:
        """Search for specific news topics"""

        if not self.api_key:
            return None
            
        try:
            url = f"{self.base_url}/everything"
            params = {
                "q": query,
                "language": NEWS_LANGUAGE,
                "pageSize": page_size,
                "sortBy": "popularity"
            }
            headers = {"X-API-Key": self.api_key}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            return response.json().get("articles", [])
            
        except Exception as e:
            print(f"Error searching news: {e}")
            return None
        
