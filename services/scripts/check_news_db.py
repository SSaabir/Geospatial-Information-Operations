"""
Quick script to check news articles in database
"""
from db_config import DatabaseConfig
from models.news import NewsArticleDB
from datetime import datetime

db = DatabaseConfig().get_session()

# Count total articles
total = db.query(NewsArticleDB).count()
print(f"📊 Total articles in database: {total}")

# Get latest articles
print("\n📰 Latest 10 articles:")
print("="*80)

articles = db.query(NewsArticleDB).order_by(NewsArticleDB.published_at.desc()).limit(10).all()

for i, article in enumerate(articles, 1):
    print(f"\n{i}. {article.title}")
    print(f"   📅 Published: {article.published_at}")
    print(f"   📰 Source: {article.source}")
    print(f"   🏷️  Category: {article.category} | ⭐ Relevance: {article.relevance_score}")
    print(f"   🔗 {article.url[:80]}...")

# Check categories
print("\n" + "="*80)
print("📊 Articles by category:")
from sqlalchemy import func
categories = db.query(
    NewsArticleDB.category, 
    func.count(NewsArticleDB.id)
).group_by(NewsArticleDB.category).all()

for cat, count in categories:
    print(f"   {cat}: {count} articles")

# Check date range
oldest = db.query(NewsArticleDB).order_by(NewsArticleDB.published_at.asc()).first()
newest = db.query(NewsArticleDB).order_by(NewsArticleDB.published_at.desc()).first()

if oldest and newest:
    print("\n📅 Date range:")
    print(f"   Oldest: {oldest.published_at}")
    print(f"   Newest: {newest.published_at}")

db.close()
print("\n✅ Database check complete!")
