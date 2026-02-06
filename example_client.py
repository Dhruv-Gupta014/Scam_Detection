#!/usr/bin/env python3
"""
Example client for the Scam Detection API
Demonstrates how to use the API with various scam examples
"""

import requests
import json
from typing import Dict, List

class ScamDetectionClient:
    """Client for interacting with the Scam Detection API"""
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: str = "scam-detection-key-2026"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
    
    def analyze(self, message: str, message_id: str = None, source: str = "unknown") -> Dict:
        """Analyze a single scam message"""
        if message_id is None:
            import time
            message_id = f"msg_{int(time.time())}"
        
        payload = {
            "message": message,
            "message_id": message_id,
            "source": source
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/analyze",
            json=payload,
            headers=self.headers
        )
        return response.json()
    
    def analyze_batch(self, messages: List[Dict]) -> Dict:
        """Analyze multiple messages"""
        payload = {"messages": messages}
        response = requests.post(
            f"{self.base_url}/api/v1/batch",
            json=payload,
            headers=self.headers
        )
        return response.json()
    
    def get_categories(self) -> Dict:
        """Get list of scam categories"""
        response = requests.get(
            f"{self.base_url}/api/v1/scam-categories",
            headers=self.headers
        )
        return response.json()
    
    def get_stats(self) -> Dict:
        """Get API statistics"""
        response = requests.get(
            f"{self.base_url}/api/v1/stats",
            headers=self.headers
        )
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()


def print_analysis(result: Dict):
    """Pretty print analysis results"""
    if not result.get("success"):
        print(f"Error: {result.get('error')}")
        return
    
    analysis = result.get("analysis", {})
    
    print(f"\n📊 Analysis Results for: {result.get('message_id')}")
    print(f"{'='*60}")
    print(f"Scam Score: {analysis.get('scam_score')} (0-1)")
    print(f"Severity: {analysis.get('severity_level').upper()}")
    print(f"Is Scam: {'🚨 YES' if analysis.get('is_scam') else '✓ No'}")
    print(f"Processing Time: {result.get('execution_time_ms')}ms")
    
    print(f"\n📧 Extracted Data:")
    extracted = analysis.get("extracted_data", {})
    print(f"  Emails: {extracted.get('emails', [])}")
    print(f"  Phone Numbers: {extracted.get('phone_numbers', [])}")
    print(f"  URLs: {extracted.get('urls', [])}")
    if extracted.get('cryptocurrency_addresses'):
        crypto = extracted.get('cryptocurrency_addresses', {})
        if crypto.get('bitcoin'):
            print(f"  Bitcoin Addresses: {crypto.get('bitcoin', [])}")
        if crypto.get('ethereum'):
            print(f"  Ethereum Addresses: {crypto.get('ethereum', [])}")
    
    print(f"\n⚠️  Indicators:")
    indicators = analysis.get("indicators", {})
    personal = indicators.get("personal_info_requests", {})
    urgency = indicators.get("urgency_indicators", {})
    
    print(f"  Personal Info Requests:")
    for key, value in personal.items():
        icon = "🔴" if value else "🟢"
        print(f"    {icon} {key.replace('_', ' ').title()}: {value}")
    
    print(f"  Urgency Indicators:")
    for key, value in urgency.items():
        icon = "🔴" if value else "🟢"
        print(f"    {icon} {key.replace('_', ' ').title()}: {value}")
    
    categories = analysis.get("scam_categories", {})
    if categories:
        print(f"\n🏷️  Scam Categories Detected:")
        for category, keywords in categories.items():
            print(f"  - {category.replace('_', ' ').title()}: {keywords}")
    else:
        print(f"\n🏷️  No scam categories detected")
    
    print(f"{'='*60}\n")


def main():
    """Main demonstration"""
    print("\n" + "="*60)
    print("  Agentic Honey-Pot Scam Detection API - Example Client")
    print("="*60 + "\n")
    
    # Initialize client
    client = ScamDetectionClient()
    
    # Check API health
    print("1️⃣  Checking API health...")
    try:
        health = client.health_check()
        print(f"✓ API Status: {health.get('status')}\n")
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        print("Make sure the API is running: python app.py\n")
        return
    
    # Example scam messages
    scam_examples = [
        {
            "name": "Prize Scam",
            "message": "Congratulations! You've won $1,000,000 in the lottery! Click here to claim your prize: http://claim-now.com. Verify immediately with your SSN and credit card.",
            "source": "email"
        },
        {
            "name": "Banking Scam",
            "message": "URGENT: Your bank account has been compromised! Your account will be locked in 24 hours. Click to verify: https://verify-account-details.com",
            "source": "sms"
        },
        {
            "name": "Romance Scam",
            "message": "My darling, I have fallen in love with you. I need $5000 immediately for an emergency. Please transfer to my account.",
            "source": "email"
        },
        {
            "name": "Tech Support Scam",
            "message": "WARNING: Your computer has a critical virus! Call our technical support immediately at 1-800-SCAMMER. Pay $299 for removal.",
            "source": "popup"
        },
        {
            "name": "Normal Message",
            "message": "Hi, how are you doing today? Would you like to grab coffee this weekend?",
            "source": "sms"
        }
    ]
    
    # Analyze individual messages
    print("2️⃣  Analyzing individual messages...")
    print("="*60)
    
    for i, example in enumerate(scam_examples[:3], 1):
        print(f"\n📨 Example {i}: {example['name']}")
        print(f"Message: {example['message'][:80]}...")
        
        result = client.analyze(
            message=example['message'],
            source=example['source']
        )
        print_analysis(result)
    
    # Batch analysis
    print("\n3️⃣  Running batch analysis...")
    print("="*60)
    
    batch_messages = [
        {
            "message": scam_examples[0]['message'],
            "message_id": "batch_1",
            "source": "email"
        },
        {
            "message": scam_examples[1]['message'],
            "message_id": "batch_2",
            "source": "sms"
        },
        {
            "message": scam_examples[4]['message'],
            "message_id": "batch_3",
            "source": "sms"
        }
    ]
    
    try:
        batch_result = client.analyze_batch(batch_messages)
        if batch_result.get('success'):
            print(f"\n✓ Batch Analysis Complete")
            print(f"  Processed: {batch_result.get('processed_messages')} messages")
            print(f"  Time: {batch_result.get('execution_time_ms')}ms")
            print(f"\n  Results:")
            for result in batch_result.get('results', []):
                severity_icon = "🚨" if result.get('is_scam') else "✓"
                print(f"    {severity_icon} {result.get('message_id')}: {result.get('scam_score')} ({result.get('severity_level')})")
    except Exception as e:
        print(f"✗ Batch analysis failed: {e}")
    
    # Get scam categories
    print("\n4️⃣  Available scam categories:")
    print("="*60)
    try:
        categories = client.get_categories()
        if 'scam_categories' in categories:
            for i, cat in enumerate(categories['scam_categories'], 1):
                print(f"  {i:2}. {cat.replace('_', ' ').title()}")
    except Exception as e:
        print(f"✗ Failed to get categories: {e}")
    
    # Get statistics
    print("\n5️⃣  API Statistics:")
    print("="*60)
    try:
        stats = client.get_stats()
        print(f"  Requests Processed: {stats.get('requests_processed')}")
        print(f"  Uptime: {stats.get('uptime_seconds')} seconds")
    except Exception as e:
        print(f"✗ Failed to get stats: {e}")
    
    print("\n" + "="*60)
    print("✓ Example client demo completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
