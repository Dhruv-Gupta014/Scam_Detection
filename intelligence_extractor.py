"""
Intelligence Extraction Engine for Scam Detection
Extracts key information from scam messages
"""
from typing import Dict, List, Set
import re
from datetime import datetime, timezone
from config import SCAM_KEYWORDS

class IntelligenceExtractor:
    """Extract intelligence from scam messages"""
    
    def __init__(self):
        self.scam_patterns = SCAM_KEYWORDS
        
    def extract_email_addresses(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(pattern, text)))
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        patterns = [
            r'\+?1?\s*[-.\s]?[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'\+[0-9]{1,3}\s?[0-9]{6,14}',
            r'\b[0-9]{10}\b'
        ]
        numbers = []
        for pattern in patterns:
            numbers.extend(re.findall(pattern, text))
        return list(set(numbers))
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        pattern = r'https?://[^\s]+'
        return list(set(re.findall(pattern, text)))
    
    def extract_crypto_addresses(self, text: str) -> Dict[str, List[str]]:
        """Extract cryptocurrency addresses"""
        crypto_addresses = {
            "bitcoin": [],
            "ethereum": [],
            "other": []
        }
        
        # Bitcoin address pattern (simplified)
        bitcoin_pattern = r'\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}\b'
        crypto_addresses["bitcoin"] = list(set(re.findall(bitcoin_pattern, text)))
        
        # Ethereum address pattern
        eth_pattern = r'\b0x[a-fA-F0-9]{40}\b'
        crypto_addresses["ethereum"] = list(set(re.findall(eth_pattern, text)))
        
        return crypto_addresses
    
    def extract_account_info(self, text: str) -> Dict[str, List[str]]:
        """Extract account-related information"""
        account_info = {
            "account_numbers": [],
            "card_numbers": [],
            "bank_references": []
        }
        
        # Account numbers (16 digits)
        account_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        account_info["account_numbers"] = list(set(re.findall(account_pattern, text)))
        
        return account_info
    
    def extract_personal_info_indicators(self, text: str) -> Dict[str, bool]:
        """Check for personal information requests"""
        text_lower = text.lower()
        indicators = {
            "requests_ssn": bool(re.search(r'\b(ssn|social security|social.{0,5}security)\b', text_lower)),
            "requests_credit_card": bool(re.search(r'\b(credit.?card|cvv|card.?number)\b', text_lower)),
            "requests_password": bool(re.search(r'\b(password|pin|passcode)\b', text_lower)),
            "requests_otp": bool(re.search(r'\b(otp|one.?time.?password|verification.?code)\b', text_lower)),
            "requests_dob": bool(re.search(r'\b(date.?of.?birth|dob|birthday)\b', text_lower)),
        }
        return indicators
    
    def extract_urgency_indicators(self, text: str) -> Dict[str, bool]:
        """Check for urgency/threat language"""
        text_lower = text.lower()
        indicators = {
            "immediate_action": bool(re.search(r'\b(urgent|immediately|asap|right now|quick action)\b', text_lower)),
            "threat_language": bool(re.search(r'\b(shut down|freeze|block|suspend|close|lock)\b', text_lower)),
            "time_pressure": bool(re.search(r'\b(today|24 hours|48 hours|deadline|expires)\b', text_lower)),
            "emotional_appeal": bool(re.search(r'\b(beloved|dear|urgent need|help|emergency)\b', text_lower)),
        }
        return indicators
    
    def extract_scam_category(self, text: str) -> Dict[str, List[str]]:
        """Identify scam category based on keywords"""
        text_lower = text.lower()
        categories = {}
        
        for category, keywords in self.scam_patterns.items():
            matched = []
            for keyword in keywords:
                if keyword in text_lower:
                    matched.append(keyword)
            if matched:
                categories[category] = matched
        
        return categories
    
    def calculate_scam_score(self, text: str) -> float:
        """Calculate scam likelihood score (0-1)"""
        score = 0.0
        max_score = 0.0
        
        # Check for scam categories (weight: 0.3)
        categories = self.extract_scam_category(text)
        category_weight = 0.3
        max_score += category_weight
        score += min(len(categories) * 0.08, category_weight)
        
        # Check for personal info requests (weight: 0.25)
        personal_info = self.extract_personal_info_indicators(text)
        personal_weight = 0.25
        max_score += personal_weight
        score += (sum(personal_info.values()) / len(personal_info)) * personal_weight if personal_info else 0
        
        # Check for urgency (weight: 0.2)
        urgency = self.extract_urgency_indicators(text)
        urgency_weight = 0.2
        max_score += urgency_weight
        score += (sum(urgency.values()) / len(urgency)) * urgency_weight if urgency else 0
        
        # Check for suspicious links/attachments (weight: 0.15)
        urls = self.extract_urls(text)
        links_weight = 0.15
        max_score += links_weight
        if urls:
            score += links_weight * min(len(urls) * 0.15, 1.0)
        
        # Check for contact info (weight: 0.1)
        emails = self.extract_email_addresses(text)
        phones = self.extract_phone_numbers(text)
        contact_weight = 0.1
        max_score += contact_weight
        contact_count = len(emails) + len(phones)
        if contact_count > 0:
            score += min(contact_count * 0.05, contact_weight)
        
        # Normalize score
        if max_score > 0:
            normalized_score = score / max_score
        else:
            normalized_score = 0.0
        
        return min(normalized_score, 1.0)
    
    def get_severity_level(self, score: float) -> str:
        """Determine severity level based on score"""
        if score >= 0.75:
            return "high"
        elif score >= 0.5:
            return "medium"
        elif score >= 0.25:
            return "low"
        else:
            return "none"
    
    def extract_all_intelligence(self, text: str) -> Dict:
        """Extract all intelligence from the message"""
        intelligence = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "text_length": len(text),
            "scam_score": self.calculate_scam_score(text),
            "severity_level": None,
            "extracted_data": {
                "emails": self.extract_email_addresses(text),
                "phone_numbers": self.extract_phone_numbers(text),
                "urls": self.extract_urls(text),
                "cryptocurrency": self.extract_crypto_addresses(text),
                "account_info": self.extract_account_info(text),
            },
            "indicators": {
                "personal_info_requests": self.extract_personal_info_indicators(text),
                "urgency_indicators": self.extract_urgency_indicators(text),
            },
            "scam_categories": self.extract_scam_category(text),
        }
        
        intelligence["severity_level"] = self.get_severity_level(intelligence["scam_score"])
        
        return intelligence
