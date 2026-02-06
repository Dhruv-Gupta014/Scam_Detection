#!/usr/bin/env python3
"""Quick test of the API"""
import requests
import json
import time

print("🚀 Waiting for API to start...")
time.sleep(3)

BASE_URL = "http://127.0.0.1:5000"
API_KEY = "scam-detection-key-2026"

print("\n✅ Testing Scam Detection API\n")

# Test 1: Health check
print("1️⃣ Health Check:")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")

# Test 2: Analyze scam message
print("\n2️⃣ Analyzing Scam Message:")
try:
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "message": "URGENT! Your account is compromised. Click here to verify: http://scam.com",
        "message_id": "test_scam_001",
        "source": "email"
    }
    r = requests.post(f"{BASE_URL}/api/v1/analyze", json=data, headers=headers, timeout=5)
    print(f"Status: {r.status_code}")
    result = r.json()
    print(f"Scam Score: {result['analysis']['scam_score']}")
    print(f"Severity: {result['analysis']['severity_level']}")
    print(f"Is Scam: {result['analysis']['is_scam']}")
    print(f"URLs Found: {result['analysis']['extracted_data']['urls']}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Normal message
print("\n3️⃣ Analyzing Normal Message:")
try:
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "message": "Hi, how are you doing today?",
        "message_id": "test_normal_001",
        "source": "sms"
    }
    r = requests.post(f"{BASE_URL}/api/v1/analyze", json=data, headers=headers, timeout=5)
    print(f"Status: {r.status_code}")
    result = r.json()
    print(f"Scam Score: {result['analysis']['scam_score']}")
    print(f"Severity: {result['analysis']['severity_level']}")
    print(f"Is Scam: {result['analysis']['is_scam']}")
except Exception as e:
    print(f"Error: {e}")

print("\n✅ Tests completed!")
