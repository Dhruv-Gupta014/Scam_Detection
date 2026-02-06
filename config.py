"""
Configuration for the Agentic Honey-Pot Scam Detection System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_PORT = int(os.getenv("API_PORT", 5000))
API_HOST = os.getenv("API_HOST", "0.0.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
API_KEY = os.getenv("API_KEY", "scam-detection-key-2026")

# Scam Detection Models and Patterns
SCAM_KEYWORDS = {
    "urgent_action": ["urgent", "immediately", "asap", "right now", "quick action"],
    "financial_threat": ["account", "bank", "money", "transfer", "payment", "wire", "cryptocurrency", "bitcoin"],
    "verification": ["verify", "confirm", "validate", "authenticate", "login", "password", "otp", "code"],
    "trust_appeal": ["trusted", "official", "government", "police", "officer", "authority"],
    "personal_info": ["name", "ssn", "social security", "credit card", "cvv", "pin", "address", "email"],
    "phishing": ["click here", "link", "download", "attachment", "update", "confirm your identity"],
    "prize_scam": ["congratulations", "winner", "claim", "prize", "reward", "lottery", "jackpot"],
    "romance_scam": ["love", "relationship", "meet", "marry", "darling", "sweetheart"],
    "tech_support": ["error", "virus", "malware", "technical support", "computer repair"],
    "impersonation": ["we are", "behalf of", "authorized", "representing"]
}

# Response Templates
SCAM_SEVERITY_LEVELS = {
    "high": "Likely scam with immediate threat",
    "medium": "Potential scam with moderate risk",
    "low": "Suspicious but lower confidence",
    "none": "No scam indicators detected"
}

# Rate limiting
RATE_LIMIT_PER_MINUTE = 60
CACHE_TIMEOUT = 3600  # 1 hour

# Maximum request size
MAX_REQUEST_SIZE = 10000  # characters

# Response timeout
RESPONSE_TIMEOUT = 30  # seconds
