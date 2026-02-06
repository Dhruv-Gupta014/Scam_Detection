# API Usage Examples

## 📌 Base URL
```
http://localhost:5000
```

## 🔑 Authentication
All endpoints (except `/health` and `/`) require:
```
Header: X-API-Key: scam-detection-key-2026
```

---

## 1️⃣ Health Check

### cURL
```bash
curl http://localhost:5000/health
```

### Python
```python
import requests

response = requests.get('http://localhost:5000/health')
print(response.json())
```

### JavaScript
```javascript
fetch('http://localhost:5000/health')
  .then(r => r.json())
  .then(data => console.log(data))
```

### Response
```json
{
  "status": "healthy",
  "timestamp": "2026-02-06T12:00:00.000000",
  "uptime_seconds": 3600,
  "requests_processed": 150
}
```

---

## 2️⃣ Analyze Single Message

### cURL
```bash
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: scam-detection-key-2026" \
  -d '{
    "message": "Congratulations! You have won $1,000,000. Click here to claim: http://claim-prize.com. Verify your account immediately!",
    "message_id": "prize_scam_001",
    "source": "email"
  }'
```

### Python
```python
import requests
import json

url = "http://localhost:5000/api/v1/analyze"
headers = {
    "X-API-Key": "scam-detection-key-2026",
    "Content-Type": "application/json"
}

payload = {
    "message": "Your account will be closed in 24 hours. Verify now at https://verify-account.com",
    "message_id": "bank_scam_001",
    "source": "email"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

print(f"Scam Score: {result['analysis']['scam_score']}")
print(f"Severity: {result['analysis']['severity_level']}")
print(f"Is Scam: {result['analysis']['is_scam']}")
```

### JavaScript
```javascript
const headers = {
  'X-API-Key': 'scam-detection-key-2026',
  'Content-Type': 'application/json'
};

const payload = {
  message: "URGENT: Send $5000 to 1A1z7agoat5powBZXvVBHtzmyQXotPUA immediately",
  message_id: "crypto_scam_001",
  source: "email"
};

fetch('http://localhost:5000/api/v1/analyze', {
  method: 'POST',
  headers,
  body: JSON.stringify(payload)
})
.then(r => r.json())
.then(data => {
  console.log(`Score: ${data.analysis.scam_score}`);
  console.log(`Severity: ${data.analysis.severity_level}`);
})
```

### Response
```json
{
  "success": true,
  "message_id": "prize_scam_001",
  "source": "email",
  "analysis": {
    "scam_score": 0.87,
    "severity_level": "high",
    "is_scam": true,
    "extracted_data": {
      "emails": [],
      "phone_numbers": [],
      "urls": ["http://claim-prize.com"],
      "cryptocurrency_addresses": {
        "bitcoin": [],
        "ethereum": [],
        "other": []
      }
    },
    "indicators": {
      "personal_info_requests": {
        "requests_ssn": false,
        "requests_credit_card": false,
        "requests_password": false,
        "requests_otp": false,
        "requests_dob": false
      },
      "urgency_indicators": {
        "immediate_action": true,
        "threat_language": false,
        "time_pressure": false,
        "emotional_appeal": false
      }
    },
    "scam_categories": {
      "urgent_action": ["immediately"],
      "prize_scam": ["won", "congratulations"],
      "phishing": ["click here"]
    }
  },
  "timestamp": "2026-02-06T12:34:56.789123",
  "execution_time_ms": 42
}
```

---

## 3️⃣ Batch Analysis

### cURL
```bash
curl -X POST http://localhost:5000/api/v1/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: scam-detection-key-2026" \
  -d '{
    "messages": [
      {
        "message": "Click here to verify your account: http://verify.com",
        "message_id": "phishing_001",
        "source": "email"
      },
      {
        "message": "I love you darling, I need $500 urgently",
        "message_id": "romance_001",
        "source": "sms"
      },
      {
        "message": "How are you doing today?",
        "message_id": "normal_001",
        "source": "sms"
      }
    ]
  }'
```

### Python
```python
import requests

url = "http://localhost:5000/api/v1/batch"
headers = {
    "X-API-Key": "scam-detection-key-2026",
    "Content-Type": "application/json"
}

messages = [
    {
        "message": "Your computer has a virus. Call 1-800-SCAMMER",
        "message_id": "tech_001"
    },
    {
        "message": "Bank account suspended. Verify SSN immediately.",
        "message_id": "bank_001"
    },
    {
        "message": "Meeting at 3 PM today?",
        "message_id": "normal_001"
    }
]

payload = {"messages": messages}
response = requests.post(url, json=payload, headers=headers)
result = response.json()

for res in result['results']:
    print(f"{res['message_id']}: {res['scam_score']} ({res['severity_level']})")
```

### Response
```json
{
  "success": true,
  "total_messages": 3,
  "processed_messages": 3,
  "results": [
    {
      "message_id": "phishing_001",
      "source": "email",
      "scam_score": 0.75,
      "severity_level": "high",
      "is_scam": true
    },
    {
      "message_id": "romance_001",
      "source": "sms",
      "scam_score": 0.68,
      "severity_level": "medium",
      "is_scam": true
    },
    {
      "message_id": "normal_001",
      "source": "sms",
      "scam_score": 0.08,
      "severity_level": "none",
      "is_scam": false
    }
  ],
  "timestamp": "2026-02-06T12:34:56.789123",
  "execution_time_ms": 78
}
```

---

## 4️⃣ Get Scam Categories

### cURL
```bash
curl -H "X-API-Key: scam-detection-key-2026" \
  http://localhost:5000/api/v1/scam-categories
```

### Python
```python
import requests

headers = {"X-API-Key": "scam-detection-key-2026"}
response = requests.get(
    "http://localhost:5000/api/v1/scam-categories",
    headers=headers
)

categories = response.json()['scam_categories']
for cat in categories:
    print(f"- {cat}")
```

### Response
```json
{
  "scam_categories": [
    "urgent_action",
    "financial_threat",
    "verification",
    "trust_appeal",
    "personal_info",
    "phishing",
    "prize_scam",
    "romance_scam",
    "tech_support",
    "impersonation"
  ],
  "total_categories": 10,
  "description": "List of scam categories used for classification"
}
```

---

## 5️⃣ Get API Statistics

### cURL
```bash
curl -H "X-API-Key: scam-detection-key-2026" \
  http://localhost:5000/api/v1/stats
```

### Python
```python
import requests

headers = {"X-API-Key": "scam-detection-key-2026"}
response = requests.get(
    "http://localhost:5000/api/v1/stats",
    headers=headers
)
print(response.json())
```

### Response
```json
{
  "requests_processed": 1250,
  "uptime_seconds": 86400,
  "timestamp": "2026-02-06T12:34:56.789123"
}
```

---

## ❌ Error Examples

### Missing API Key
```bash
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

Response (401):
```json
{
  "error": "Missing API key",
  "message": "Please provide X-API-Key header",
  "code": "AUTH_MISSING_KEY"
}
```

### Invalid API Key
```bash
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "X-API-Key: wrong-key" \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

Response (401):
```json
{
  "error": "Invalid API key",
  "message": "The provided API key is invalid",
  "code": "AUTH_INVALID_KEY"
}
```

### Missing Required Field
```bash
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "X-API-Key: scam-detection-key-2026" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response (400):
```json
{
  "success": false,
  "error": "Missing required field: message",
  "code": "MISSING_FIELD"
}
```

### Empty Message
```bash
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "X-API-Key: scam-detection-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"message":""}'
```

Response (400):
```json
{
  "success": false,
  "error": "Message cannot be empty",
  "code": "EMPTY_MESSAGE"
}
```

### Message Too Long
```bash
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "X-API-Key: scam-detection-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"message":"AAAA...AAAA"}'  # > 10,000 characters
```

Response (400):
```json
{
  "success": false,
  "error": "Message exceeds maximum length of 10000 characters",
  "code": "MESSAGE_TOO_LONG"
}
```

### Rate Limit Exceeded
```bash
# Make 61 requests within 1 minute
```

Response (429):
```json
{
  "error": "Rate limit exceeded",
  "message": "You have exceeded the rate limit of 60 requests per minute",
  "code": "RATE_LIMIT_EXCEEDED",
  "rate_limit": {
    "limit": 60,
    "current": 61,
    "reset_in_seconds": 45
  }
}
```

### Batch Size Exceeded
```bash
curl -X POST http://localhost:5000/api/v1/batch \
  -H "X-API-Key: scam-detection-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"messages": [...]}'  # > 100 messages
```

Response (400):
```json
{
  "success": false,
  "error": "Batch size cannot exceed 100 messages",
  "code": "BATCH_SIZE_EXCEEDED"
}
```

---

## 🎯 Real-World Scam Examples

### Example 1: Prize Scam
```json
{
  "message": "🎉 CONGRATULATIONS! You've been randomly selected to WIN $1,000,000 USD! To claim your prize, click here immediately: http://claim-mega-prize.com. You must verify your information within 24 hours or the prize will be forfeited! Enter your full name, address, social security number, and bank account details.",
  "message_id": "prize_scam_2026",
  "source": "email"
}
```

**Expected Response:**
- Scam Score: 0.89+
- Severity: HIGH
- Categories: prize_scam, phishing, urgent_action, personal_info, verification

### Example 2: Banking Scam
```json
{
  "message": "⚠️ URGENT: Your bank account has been COMPROMISED! Unauthorized transactions detected. Your account will be FROZEN in 24 hours. ACT NOW: https://verify-bank-account-emergency.com to prevent account closure. Provide your account number, PIN, and credit card CVV immediately.",
  "message_id": "bank_scam_2026",
  "source": "sms"
}
```

**Expected Response:**
- Scam Score: 0.92+
- Severity: HIGH
- Categories: financial_threat, urgent_action, verification, personal_info, threat_language

### Example 3: Romance Scam
```json
{
  "message": "My beloved darling, I have fallen deeply in love with you. I want to marry you and spend the rest of my life with you. Unfortunately, I am stuck overseas and need $5000 for emergency travel expenses. Please wire transfer the money to this account: 1A1z7agoat5powBZXvVBHtzmyQXotPUA. I love you so much.",
  "message_id": "romance_scam_2026",
  "source": "email"
}
```

**Expected Response:**
- Scam Score: 0.78+
- Severity: MEDIUM/HIGH
- Categories: romance_scam, financial_threat, emotional_appeal, impersonation

### Example 4: Tech Support Scam
```json
{
  "message": "🚨 CRITICAL ALERT: Your computer has detected 5 critical viruses! Your system is at risk. DO NOT TURN OFF YOUR COMPUTER. Call our emergency technical support immediately: 1-800-TECH-FIX. Our technicians will provide immediate remote assistance. Payment of $299 required for professional virus removal service.",
  "message_id": "tech_scam_2026",
  "source": "popup"
}
```

**Expected Response:**
- Scam Score: 0.82+
- Severity: HIGH
- Categories: tech_support, urgent_action, threat_language, financial_threat

### Example 5: Normal Message (Not a Scam)
```json
{
  "message": "Hi Sarah, how are you doing today? Would you like to grab coffee this weekend? Let me know your availability.",
  "message_id": "normal_msg_2026",
  "source": "sms"
}
```

**Expected Response:**
- Scam Score: 0.05-0.15
- Severity: NONE
- Categories: {} (empty)

---

## 📊 Integration Example

Complete Python integration:

```python
import requests
from typing import Dict, List

class ScamDetector:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def analyze(self, message: str) -> Dict:
        """Analyze single message"""
        response = requests.post(
            f"{self.api_url}/api/v1/analyze",
            json={"message": message},
            headers=self.headers
        )
        return response.json()
    
    def is_scam(self, message: str) -> bool:
        """Quick scam check"""
        result = self.analyze(message)
        return result.get('analysis', {}).get('is_scam', False)
    
    def get_confidence(self, message: str) -> float:
        """Get scam confidence score"""
        result = self.analyze(message)
        return result.get('analysis', {}).get('scam_score', 0.0)
    
    def batch_analyze(self, messages: List[str]) -> List[Dict]:
        """Analyze multiple messages"""
        response = requests.post(
            f"{self.api_url}/api/v1/batch",
            json={"messages": [{"message": m} for m in messages]},
            headers=self.headers
        )
        return response.json().get('results', [])

# Usage
detector = ScamDetector('http://localhost:5000', 'scam-detection-key-2026')

# Check if message is scam
message = "Click here to claim your prize!"
if detector.is_scam(message):
    print("🚨 SCAM DETECTED!")
else:
    print("✓ Legitimate message")

# Get confidence
confidence = detector.get_confidence(message)
print(f"Confidence: {confidence:.0%}")

# Batch process
messages = [
    "You won a million dollars!",
    "Let's meet for coffee",
    "Your account is compromised"
]
results = detector.batch_analyze(messages)
```

---

## 🔗 Summary

- **Single Message**: `POST /api/v1/analyze`
- **Batch Processing**: `POST /api/v1/batch`
- **Categories**: `GET /api/v1/scam-categories`
- **Statistics**: `GET /api/v1/stats`
- **Health**: `GET /health`

All requests require `X-API-Key` header (except `/health` and `/`).

Responses are always JSON with success/error status.
