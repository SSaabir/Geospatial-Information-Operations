"""
Seed news database with initial articles
"""
from db_config import DatabaseConfig
from agents.news_collector import NewsCollectorAgent

def seed_news():
    """Collect initial news articles"""
    db = DatabaseConfig().get_session()
    collector = NewsCollectorAgent(db)
    
    print("🗞️ Collecting news articles...")
    result = collector.collect_news(days_back=7, max_articles=50)
    
    if result["success"]:
        print(f"✅ Collected {result['collected']} new articles")
        print(f"⏭️  Skipped {result['skipped']} existing articles")
    else:
        print(f"❌ News collection failed: {result.get('error')}")

if __name__ == "__main__":
    seed_news()
