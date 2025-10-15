"""
Test script to collect real news from NewsAPI.org
"""
import os
from dotenv import load_dotenv
from agents.news_collector import NewsCollectorAgent
from db_config import DatabaseConfig

# Load environment variables
load_dotenv()

def test_real_news_collection():
    """Test collecting real news articles"""
    
    # Check API key
    api_key = os.getenv("NEWS_API_KEY")
    print(f"📋 NEWS_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    
    if not api_key or api_key == "your_newsapi_key_here":
        print("⚠️  Using mock data (no API key configured)")
    else:
        print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
    
    # Initialize database
    db_config = DatabaseConfig()
    db = db_config.get_session()
    
    # Initialize news collector
    collector = NewsCollectorAgent(db)
    
    print("\n🗞️  Starting real news collection...")
    print(f"📅 Looking back: 7 days")
    print(f"📊 Max articles: 20")
    print(f"🔍 Keywords: {', '.join(collector.keywords)}")
    print(f"📰 Sources: {', '.join(collector.sources)}")
    print("\n" + "="*60)
    
    # Collect news
    result = collector.collect_news(days_back=7, max_articles=20)
    
    print("\n" + "="*60)
    print("📊 COLLECTION RESULTS:")
    print(f"✅ Success: {result['success']}")
    print(f"📰 Collected: {result['collected']} new articles")
    print(f"⏭️  Skipped: {result['skipped']} existing articles")
    
    if result['success'] and result['collected'] > 0:
        print("\n📑 Sample Articles:")
        for i, article in enumerate(result['articles'][:5], 1):
            print(f"\n{i}. {article.title}")
            print(f"   📅 {article.published_at}")
            print(f"   📰 {article.source}")
            print(f"   🏷️  {article.category} | ⭐ Relevance: {article.relevance_score}")
            print(f"   🔗 {article.url}")
    
    db.close()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_real_news_collection()
