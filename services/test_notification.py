"""Test notification manager functionality"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from utils.notification_manager import notify, get_notification_manager

def test_basic_notification():
    """Test basic notification without email/webhook configured"""
    print("Testing notification manager...")
    
    # Test with no email/webhook configured (should just log)
    notify(
        subject="Test Notification",
        message="This is a test notification from the payment system",
        level="info",
        metadata={
            "test": True,
            "user_id": 123,
            "amount": 29.99
        }
    )
    
    print("✓ Basic notification test passed")

def test_payment_notification():
    """Test payment-related notification"""
    notify(
        subject="Payment Successful",
        message="User john.doe completed payment for Researcher plan ($29/mo)",
        level="info",
        metadata={
            "user_id": 1,
            "plan": "researcher",
            "amount": 29.00,
            "payment_method": "card",
            "last4": "1234"
        }
    )
    
    print("✓ Payment notification test passed")

def test_notification_levels():
    """Test different notification levels"""
    levels = ["info", "warning", "error", "critical"]
    
    for level in levels:
        notify(
            subject=f"Test {level.upper()} Notification",
            message=f"Testing {level} level notification",
            level=level,
            metadata={"level_test": True}
        )
    
    print(f"✓ Tested {len(levels)} notification levels")

if __name__ == "__main__":
    print("\n=== Notification Manager Tests ===\n")
    
    test_basic_notification()
    test_payment_notification()
    test_notification_levels()
    
    print("\n=== All Tests Passed ===\n")
    
    print("Configuration Status:")
    nm = get_notification_manager()
    print(f"  - SMTP Server: {'✓ Configured' if nm.smtp_server else '✗ Not configured (notifications will be logged only)'}")
    print(f"  - Webhook URL: {'✓ Configured' if nm.webhook_url else '✗ Not configured'}")
    print(f"  - Database: {'✓ Configured' if nm.engine else '✗ Not configured'}")
    print(f"  - Default Email: {nm.default_email}")
    
    print("\nTo enable email notifications, set these environment variables:")
    print("  - SMTP_SERVER=smtp.gmail.com")
    print("  - SMTP_PORT=587")
    print("  - SMTP_USERNAME=your-email@gmail.com")
    print("  - SMTP_PASSWORD=your-app-password")
    print("  - DEFAULT_NOTIFICATION_EMAIL=recipient@example.com")
    
    print("\nTo enable webhook notifications, set:")
    print("  - GLOBAL_WEBHOOK_URL=https://your-webhook-endpoint.com/notifications")
