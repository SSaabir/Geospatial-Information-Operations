"""
Test script for historical data access limits by tier.

This script demonstrates the tier-based historical data access enforcement:
- Free: Last 30 days only
- Researcher: Last 1 year (365 days)
- Professional: Full archive (28 years from 1997)
"""

from datetime import date, timedelta
from utils.tier import (
    historical_access_limits,
    get_historical_days_for_tier,
    enforce_historical_access
)

print("=" * 60)
print("HISTORICAL DATA ACCESS LIMITS BY TIER")
print("=" * 60)

# Display tier limits
limits = historical_access_limits()
print("\n📊 Tier Limits:")
for tier, days in limits.items():
    days_str = f"{days} days" if days != float('inf') else "Unlimited (all 28 years)"
    print(f"  • {tier.capitalize()}: {days_str}")

print("\n" + "=" * 60)
print("ACCESS BOUNDARY DATES (from today)")
print("=" * 60)

today = date.today()
print(f"\n📅 Today: {today.isoformat()}")

for tier in ['free', 'researcher', 'professional']:
    days = get_historical_days_for_tier(tier)
    if days == float('inf'):
        oldest = date(1997, 1, 1)  # Earliest data in database
        print(f"\n🔑 {tier.capitalize()} tier:")
        print(f"  Oldest accessible: {oldest.isoformat()} (Full archive)")
    else:
        oldest = today - timedelta(days=int(days))
        print(f"\n🔑 {tier.capitalize()} tier:")
        print(f"  Oldest accessible: {oldest.isoformat()} ({int(days)} days ago)")

print("\n" + "=" * 60)
print("TESTING ACCESS ENFORCEMENT")
print("=" * 60)

# Test cases
test_cases = [
    # Free tier tests
    ("free", today - timedelta(days=15), True),  # 15 days ago - OK
    ("free", today - timedelta(days=30), True),  # 30 days ago - OK
    ("free", today - timedelta(days=31), False), # 31 days ago - DENIED
    ("free", today - timedelta(days=100), False), # 100 days ago - DENIED
    
    # Researcher tier tests
    ("researcher", today - timedelta(days=30), True),  # 30 days ago - OK
    ("researcher", today - timedelta(days=180), True), # 6 months ago - OK
    ("researcher", today - timedelta(days=365), True), # 1 year ago - OK
    ("researcher", today - timedelta(days=366), False), # >1 year - DENIED
    ("researcher", today - timedelta(days=730), False), # 2 years ago - DENIED
    
    # Professional tier tests
    ("professional", today - timedelta(days=30), True),   # 30 days ago - OK
    ("professional", today - timedelta(days=365), True),  # 1 year ago - OK
    ("professional", today - timedelta(days=3650), True), # 10 years ago - OK
    ("professional", date(1997, 1, 31), True),  # Earliest data - OK
]

for tier, test_date, should_pass in test_cases:
    try:
        enforce_historical_access(test_date, tier)
        result = "✅ GRANTED"
        if not should_pass:
            result = "❌ UNEXPECTED: Should have been denied"
    except Exception as e:
        result = "🚫 DENIED"
        if should_pass:
            result = "❌ UNEXPECTED: Should have been granted"
    
    days_ago = (today - test_date).days
    print(f"\n{tier.upper():12} | {test_date.isoformat()} ({days_ago:4} days ago) | {result}")

print("\n" + "=" * 60)
print("✅ Historical data access enforcement test complete!")
print("=" * 60)
