"""
Test suite for Scam Detection API
"""
import json
import requests
from datetime import datetime, timezone

# Configuration
BASE_URL = "http://localhost:5000"
API_KEY = "scam-detection-key-2026"

# Test data
TEST_MESSAGES = {
    "high_severity_prize": {
        "message": "Congratulations! You've won $1,000,000 in the lottery! Click here immediately to claim your prize: http://claim-prize-now.com. You must verify your bank account details and social security number within 24 hours!",
        "expected_severity": "high",
        "min_score": 0.75
    },
    "high_severity_banking": {
        "message": "URGENT: Your bank account has been compromised! Your account will be locked in 24 hours. Click here immediately to verify your account: https://verify-bank-details.com. Provide your credit card CVV and password.",
        "expected_severity": "high",
        "min_score": 0.75
    },
    "medium_severity_phishing": {
        "message": "Hello, we need to verify your email address. Please click this link to confirm your identity and password.",
        "expected_severity": "medium",
        "min_score": 0.5
    },
    "low_severity_suspicious": {
        "message": "Hi there, just checking in. How are you doing today? Everything seems normal.",
        "expected_severity": "low",
        "min_score": 0.0
    },
    "high_severity_romance": {
        "message": "My dear beloved, I have fallen in love with you. I am stuck overseas and need $5000 immediately. Please transfer money to this account: 1234567890. I love you so much and want to marry you.",
        "expected_severity": "high",
        "min_score": 0.75
    },
    "high_severity_tech_support": {
        "message": "WARNING: Your computer has a virus! Technical support needed immediately. Call 1-800-SCAMMER for help. Your system will be locked unless you pay $299 now!",
        "expected_severity": "high",
        "min_score": 0.75
    },
    "high_severity_crypto": {
        "message": "You've been selected to receive 10 Bitcoin! Send 1 BTC to 1A1z7agoat5powBZXvVBHtzmyQXotPUA immediately to receive 10 BTC. Limited time offer!",
        "expected_severity": "high",
        "min_score": 0.75
    }
}

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_section(text):
    """Print formatted section"""
    print(f"\n--- {text} ---")

def test_health_check():
    """Test health check endpoint"""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✓ Health check passed")
    except Exception as e:
        print(f"✗ Health check failed: {e}")

def test_home():
    """Test home endpoint"""
    print_header("TEST 2: Home/Documentation")
    
    try:
        response = requests.get(BASE_URL)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"API Name: {data['name']}")
        print(f"Version: {data['version']}")
        print(f"Endpoints Available: {len(data['endpoints'])}")
        assert response.status_code == 200
        print("✓ Home endpoint passed")
    except Exception as e:
        print(f"✗ Home endpoint failed: {e}")

def test_missing_api_key():
    """Test missing API key"""
    print_header("TEST 3: Missing API Key")
    
    try:
        headers = {"Content-Type": "application/json"}
        data = {"message": "Test message"}
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 401
        print("✓ Missing API key validation passed")
    except Exception as e:
        print(f"✗ Missing API key test failed: {e}")

def test_invalid_api_key():
    """Test invalid API key"""
    print_header("TEST 4: Invalid API Key")
    
    try:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": "invalid-key-xyz"
        }
        data = {"message": "Test message"}
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 401
        print("✓ Invalid API key validation passed")
    except Exception as e:
        print(f"✗ Invalid API key test failed: {e}")

def test_analyze_single_messages():
    """Test analyzing individual messages"""
    print_header("TEST 5: Analyze Single Messages")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    for test_name, test_data in TEST_MESSAGES.items():
        print_section(f"Testing: {test_name}")
        
        payload = {
            "message": test_data["message"],
            "message_id": f"test_{test_name}",
            "source": "email"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/analyze", json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                analysis = result["analysis"]
                
                print(f"Scam Score: {analysis['scam_score']}")
                print(f"Severity Level: {analysis['severity_level']}")
                print(f"Is Scam: {analysis['is_scam']}")
                print(f"Execution Time: {result['execution_time_ms']}ms")
                
                print(f"\nExtracted Data:")
                print(f"  - Emails: {len(analysis['extracted_data']['emails'])}")
                print(f"  - Phone Numbers: {len(analysis['extracted_data']['phone_numbers'])}")
                print(f"  - URLs: {len(analysis['extracted_data']['urls'])}")
                
                print(f"\nScam Categories Detected:")
                for category, keywords in analysis['scam_categories'].items():
                    print(f"  - {category}: {keywords}")
                
                # Validate expectations
                expected_severity = test_data["expected_severity"]
                actual_severity = analysis["severity_level"]
                
                if actual_severity == expected_severity:
                    print(f"✓ Severity level matches expected: {expected_severity}")
                else:
                    print(f"⚠ Severity mismatch - Expected: {expected_severity}, Got: {actual_severity}")
                
                if analysis["scam_score"] >= test_data["min_score"]:
                    print(f"✓ Scam score meets minimum: {analysis['scam_score']} >= {test_data['min_score']}")
                else:
                    print(f"⚠ Score below minimum: {analysis['scam_score']} < {test_data['min_score']}")
            else:
                print(f"Error: {response.json()}")
        except Exception as e:
            print(f"✗ Test failed: {e}")

def test_batch_analysis():
    """Test batch analysis"""
    print_header("TEST 6: Batch Analysis")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    # Prepare batch
    messages = [
        {
            "message": TEST_MESSAGES["high_severity_prize"]["message"],
            "message_id": "batch_msg_1",
            "source": "email"
        },
        {
            "message": TEST_MESSAGES["high_severity_banking"]["message"],
            "message_id": "batch_msg_2",
            "source": "sms"
        },
        {
            "message": TEST_MESSAGES["low_severity_suspicious"]["message"],
            "message_id": "batch_msg_3",
            "source": "email"
        }
    ]
    
    payload = {"messages": messages}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/batch", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nBatch Results:")
            print(f"Total Messages: {result['total_messages']}")
            print(f"Processed Messages: {result['processed_messages']}")
            print(f"Execution Time: {result['execution_time_ms']}ms")
            
            print(f"\nDetailed Results:")
            for idx, res in enumerate(result["results"], 1):
                print(f"\n  Message {idx}:")
                print(f"    - ID: {res['message_id']}")
                print(f"    - Score: {res['scam_score']}")
                print(f"    - Severity: {res['severity_level']}")
                print(f"    - Is Scam: {res['is_scam']}")
            
            print(f"\n✓ Batch analysis passed")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"✗ Batch analysis failed: {e}")

def test_scam_categories():
    """Test getting scam categories"""
    print_header("TEST 7: Get Scam Categories")
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/scam-categories", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Total Categories: {result['total_categories']}")
            print(f"Categories:")
            for cat in result['scam_categories']:
                print(f"  - {cat}")
            print(f"\n✓ Get scam categories passed")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"✗ Get scam categories failed: {e}")

def test_stats():
    """Test getting statistics"""
    print_header("TEST 8: Get Statistics")
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/stats", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Requests Processed: {result['requests_processed']}")
            print(f"Uptime Seconds: {result['uptime_seconds']}")
            print(f"\n✓ Get stats passed")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"✗ Get stats failed: {e}")

def test_edge_cases():
    """Test edge cases"""
    print_header("TEST 9: Edge Cases")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    # Test 1: Empty message
    print_section("Test: Empty Message")
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json={"message": ""},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"✓ Empty message rejected" if response.status_code == 400 else "✗ Failed")
    
    # Test 2: Missing message field
    print_section("Test: Missing Message Field")
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json={"message_id": "test"},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"✓ Missing field rejected" if response.status_code == 400 else "✗ Failed")
    
    # Test 3: Very long message
    print_section("Test: Message Too Long")
    long_message = "A" * 15000
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json={"message": long_message},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"✓ Long message rejected" if response.status_code == 400 else "✗ Failed")
    
    # Test 4: Invalid batch size
    print_section("Test: Batch Size Exceeded")
    large_batch = {"messages": [{"message": f"msg {i}"} for i in range(150)]}
    response = requests.post(
        f"{BASE_URL}/api/v1/batch",
        json=large_batch,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"✓ Large batch rejected" if response.status_code == 400 else "✗ Failed")

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("*" * 80)
    print("*  Agentic Honey-Pot Scam Detection API - Test Suite")
    print("*  " + datetime.now(timezone.utc).isoformat())
    print("*" * 80)
    
    try:
        test_health_check()
        test_home()
        test_missing_api_key()
        test_invalid_api_key()
        test_analyze_single_messages()
        test_batch_analysis()
        test_scam_categories()
        test_stats()
        test_edge_cases()
        
        print("\n" + "="*80)
        print("  ✓ All tests completed!")
        print("="*80 + "\n")
    except Exception as e:
        print(f"\n✗ Test suite error: {e}")

if __name__ == "__main__":
    print("\nMake sure the API is running on http://localhost:5000")
    print("Run: python app.py")
    print("\nStarting tests...\n")
    
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nTest suite failed: {e}")
