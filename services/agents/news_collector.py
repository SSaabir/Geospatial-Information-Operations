"""
News Collector Agent
Collects weather and climate-related news from various sources and stores in database.
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models.news import NewsArticleDB, NewsArticleCreate
import os

logger = logging.getLogger(__name__)

class NewsCollectorAgent:
    """Collects and stores weather/climate news from various sources"""
    
    def __init__(self, db: Session):
        self.db = db
        self.news_api_key = os.getenv("NEWS_API_KEY", "")  # Get from .env
        self.sources = [
            "bbc-news",
            "cnn",
            "the-weather-channel",
            "national-geographic",
            "reuters"
        ]
        self.keywords = [
            "weather",
            "climate change",
            "global warming",
            "temperature",
            "rainfall",
            "storm",
            "hurricane",
            "drought",
            "flood",
            "monsoon",
            "environmental"
        ]
    
    def collect_news(self, days_back: int = 7, max_articles: int = 50) -> Dict[str, any]:
        """
        Collect news articles from the past N days
        
        Args:
            days_back: Number of days to look back
            max_articles: Maximum number of articles to collect
            
        Returns:
            Dict with collection results
        """
        try:
            logger.info(f"🗞️ Starting news collection (last {days_back} days)")
            
            # Calculate date range
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            collected_articles = []
            skipped_count = 0
            
            # Collect from NewsAPI.org
            if self.news_api_key:
                articles = self._fetch_from_newsapi(from_date, to_date, max_articles)
                for article_data in articles:
                    if self._article_exists(article_data['url']):
                        skipped_count += 1
                        continue
                    
                    saved_article = self._save_article(article_data)
                    if saved_article:
                        collected_articles.append(saved_article)
            else:
                logger.warning("NEWS_API_KEY not set, using mock data")
                # Generate mock articles for testing
                articles = self._generate_mock_articles(max_articles // 5)
                for article_data in articles:
                    if self._article_exists(article_data['url']):
                        skipped_count += 1
                        continue
                    
                    saved_article = self._save_article(article_data)
                    if saved_article:
                        collected_articles.append(saved_article)
            
            logger.info(f"✅ Collected {len(collected_articles)} new articles, skipped {skipped_count} existing")
            
            return {
                "success": True,
                "collected": len(collected_articles),
                "skipped": skipped_count,
                "articles": collected_articles
            }
            
        except Exception as e:
            logger.error(f"❌ News collection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "collected": 0,
                "skipped": 0
            }
    
    def _fetch_from_newsapi(self, from_date: str, to_date: str, max_results: int) -> List[Dict]:
        """Fetch articles from NewsAPI.org"""
        try:
            url = "https://newsapi.org/v2/everything"
            
            # Join keywords with OR
            query = " OR ".join(self.keywords)
            
            params = {
                "q": query,
                "from": from_date,
                "to": to_date,
                "language": "en",
                "sortBy": "relevancy",
                "pageSize": min(max_results, 100),
                "apiKey": self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("articles", [])
            
            # Convert to our format
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    "title": article.get("title", "Untitled"),
                    "description": article.get("description"),
                    "content": article.get("content"),
                    "url": article.get("url"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "author": article.get("author"),
                    "published_at": self._parse_datetime(article.get("publishedAt")),
                    "image_url": article.get("urlToImage"),
                    "category": self._categorize_article(article.get("title", "") + " " + article.get("description", "")),
                    "keywords": self._extract_keywords(article.get("title", "") + " " + article.get("description", "")),
                    "relevance_score": self._calculate_relevance(article.get("title", "") + " " + article.get("description", ""))
                })
            
            return formatted_articles
            
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
            return []
    
    def _generate_mock_articles(self, count: int = 10) -> List[Dict]:
        """Generate mock news articles for testing"""
        mock_articles = []
        base_time = datetime.now()
        
        templates = [
            ("Extreme Weather Alert: Temperature Records Shattered Across Multiple Regions", "weather", 
             "Recent temperature measurements have broken previous records, with meteorologists reporting unprecedented readings."),
            ("Climate Scientists Issue Urgent Warning on Global Temperature Rise", "climate",
             "Leading climate researchers have published new data showing accelerated global warming trends."),
            ("Monsoon Season Brings Heavy Rainfall to South Asia", "weather",
             "The annual monsoon season has arrived with intense rainfall affecting millions across the region."),
            ("New Study Links Rising Temperatures to Extreme Weather Events", "climate",
             "A comprehensive study reveals strong correlations between global temperature increases and severe weather patterns."),
            ("Drought Conditions Persist in Multiple Agricultural Regions", "environmental",
             "Extended dry periods continue to impact farming communities and water resources worldwide."),
            ("Hurricane Season Forecast: Above-Average Activity Expected", "weather",
             "Meteorological agencies predict an active hurricane season with above-normal storm formation."),
            ("Antarctic Ice Sheet Shows Accelerated Melting Patterns", "climate",
             "Satellite data reveals concerning trends in Antarctic ice loss over recent observation periods."),
            ("Urban Areas Face Increased Heat Island Effect", "environmental",
             "Cities worldwide are experiencing elevated temperatures due to infrastructure and reduced vegetation."),
            ("Global Carbon Emissions Reach New High Despite Climate Goals", "climate",
             "Latest reports show greenhouse gas emissions continue to rise, challenging international climate targets."),
            ("Severe Flooding Displaces Thousands in Coastal Communities", "weather",
             "Heavy rainfall and storm surges have caused widespread flooding, forcing evacuations in low-lying areas."),
        ]
        
        for i in range(min(count, len(templates))):
            title, category, description = templates[i]
            mock_articles.append({
                "title": title,
                "description": description,
                "content": f"{description} Full article content would be available at the source website.",
                "url": f"https://example-news-source.com/article-{datetime.now().timestamp()}-{i}",
                "source": ["BBC News", "CNN", "Reuters", "National Geographic", "The Guardian"][i % 5],
                "author": ["John Smith", "Jane Doe", "Climate Desk", "Weather Team", "Environment Reporter"][i % 5],
                "published_at": base_time - timedelta(hours=i * 6),
                "image_url": f"https://via.placeholder.com/800x400?text={category.replace(' ', '+')}+News",
                "category": category,
                "keywords": self._extract_keywords(title + " " + description),
                "relevance_score": 85 - (i * 3)
            })
        
        return mock_articles
    
    def _article_exists(self, url: str) -> bool:
        """Check if article already exists in database"""
        return self.db.query(NewsArticleDB).filter(NewsArticleDB.url == url).first() is not None
    
    def _save_article(self, article_data: Dict) -> Optional[NewsArticleDB]:
        """Save article to database"""
        try:
            article = NewsArticleDB(**article_data)
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            return article
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            self.db.rollback()
            return None
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _categorize_article(self, text: str) -> str:
        """Categorize article based on content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["climate change", "global warming", "emissions", "carbon"]):
            return "climate"
        elif any(word in text_lower for word in ["weather", "temperature", "rainfall", "storm", "hurricane"]):
            return "weather"
        else:
            return "environmental"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:5]  # Limit to 5 keywords
    
    def _calculate_relevance(self, text: str) -> int:
        """Calculate relevance score (0-100) based on keyword matches"""
        text_lower = text.lower()
        matches = sum(1 for keyword in self.keywords if keyword.lower() in text_lower)
        
        # Score based on number of matching keywords
        score = min(100, (matches * 15) + 40)  # Base score 40, +15 per keyword
        return score
    
    def get_recent_news(self, limit: int = 20, category: Optional[str] = None) -> List[NewsArticleDB]:
        """Get recent news articles from database"""
        query = self.db.query(NewsArticleDB).filter(NewsArticleDB.is_active == True)
        
        if category:
            query = query.filter(NewsArticleDB.category == category)
        
        return query.order_by(NewsArticleDB.published_at.desc()).limit(limit).all()
    
    def get_relevant_alerts(self, threshold: int = 70) -> List[NewsArticleDB]:
        """Get high-relevance articles for dashboard alerts"""
        return (
            self.db.query(NewsArticleDB)
            .filter(
                NewsArticleDB.is_active == True,
                NewsArticleDB.relevance_score >= threshold,
                NewsArticleDB.published_at >= datetime.now() - timedelta(days=3)
            )
            .order_by(NewsArticleDB.relevance_score.desc())
            .limit(10)
            .all()
        )
