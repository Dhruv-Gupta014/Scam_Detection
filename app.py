"""
Main Flask API for Agentic Honey-Pot Scam Detection System
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
from typing import Dict
from config import API_PORT, API_HOST, DEBUG, API_KEY
from intelligence_extractor import IntelligenceExtractor
from auth_middleware import check_api_key, check_rate_limit, validate_json_request
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize intelligence extractor
intelligence_extractor = IntelligenceExtractor()

# Health check counter
app.request_count = 0
app.start_time = datetime.now(timezone.utc)

# ==================== API Routes ====================

@app.route("/", methods=["GET", "OPTIONS"])
def root():
    """Root endpoint - API info"""
    if request.method == "OPTIONS":
        return "", 200
    return jsonify({
        "service": "Agentic Honey-Pot Scam Detection API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "health": "GET /health",
            "analyze": "POST /api/v1/analyze",
            "batch": "POST /api/v1/batch",
            "stats": "GET /api/v1/stats",
            "categories": "GET /api/v1/scam-categories"
        },
        "authentication": {
            "method": "Header",
            "header": "X-API-Key",
            "example": "scam-detection-key-2026"
        },
        "rate_limit": "60 requests/minute"
    }), 200

@app.route("/health", methods=["GET", "OPTIONS"])
def health_check():
    """Health check endpoint"""
    if request.method == "OPTIONS":
        return "", 200
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": (datetime.now(timezone.utc) - app.start_time).total_seconds(),
        "requests_processed": app.request_count
    }), 200

@app.route("/api/v1/analyze", methods=["POST", "OPTIONS"])
def analyze_scam():
    """
    Main endpoint to analyze scam messages
    
    Request JSON:
    {
        "message": "The scam message text",
        "message_id": "optional unique identifier",
        "source": "optional source (email, sms, call, etc)"
    }
    
    Response JSON:
    {
        "success": true,
        "message_id": "unique identifier",
        "analysis": {
            "scam_score": 0.85,
            "severity_level": "high",
            "is_scam": true,
            "extracted_data": {...},
            "indicators": {...},
            "scam_categories": {...}
        },
        "timestamp": "ISO timestamp",
        "execution_time_ms": 45
    }
    """
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return "", 200
    
    # Now check auth and other decorators
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({
            "error": "Missing API key",
            "message": "Please provide X-API-Key header",
            "code": "AUTH_MISSING_KEY"
        }), 401
    
    if api_key != API_KEY:
        return jsonify({
            "error": "Invalid API key",
            "code": "AUTH_INVALID_KEY"
        }), 401
    
    try:
        start_time = datetime.now(timezone.utc)
        data = request.get_json()
        
        # Validate required fields
        if not data or "message" not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: message",
                "code": "MISSING_FIELD"
            }), 400
        
        message = data.get("message", "").strip()
        message_id = data.get("message_id", f"msg_{datetime.now(timezone.utc).timestamp()}")
        source = data.get("source", "unknown")
        
        # Validate message
        if not message or len(message) == 0:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty",
                "code": "EMPTY_MESSAGE"
            }), 400
        
        if len(message) > 10000:
            return jsonify({
                "success": False,
                "error": "Message exceeds maximum length of 10000 characters",
                "code": "MESSAGE_TOO_LONG"
            }), 400
        
        # Extract intelligence
        intelligence = intelligence_extractor.extract_all_intelligence(message)
        
        # Prepare response
        response = {
            "success": True,
            "message_id": message_id,
            "source": source,
            "analysis": {
                "scam_score": round(intelligence["scam_score"], 3),
                "severity_level": intelligence["severity_level"],
                "is_scam": intelligence["severity_level"] in ["high", "medium"],
                "extracted_data": {
                    "emails": intelligence["extracted_data"]["emails"],
                    "phone_numbers": intelligence["extracted_data"]["phone_numbers"],
                    "urls": intelligence["extracted_data"]["urls"],
                    "cryptocurrency_addresses": intelligence["extracted_data"]["cryptocurrency"],
                },
                "indicators": {
                    "personal_info_requests": intelligence["indicators"]["personal_info_requests"],
                    "urgency_indicators": intelligence["indicators"]["urgency_indicators"],
                },
                "scam_categories": intelligence["scam_categories"],
            },
            "timestamp": intelligence["timestamp"],
            "execution_time_ms": int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        }
        
        app.request_count += 1
        logger.info(f"Analyzed message {message_id} with score {intelligence['scam_score']}")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error analyzing scam: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "details": str(e) if DEBUG else None
        }), 500

@app.route("/api/v1/batch", methods=["POST", "OPTIONS"])
def analyze_batch():
    """
    Batch analysis endpoint for multiple messages
    
    Request JSON:
    {
        "messages": [
            {
                "message": "scam text 1",
                "message_id": "id1",
                "source": "email"
            },
            ...
        ]
    }
    """
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return "", 200
    
    # Check auth
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({
            "error": "Missing API key",
            "message": "Please provide X-API-Key header",
            "code": "AUTH_MISSING_KEY"
        }), 401
    
    if api_key != API_KEY:
        return jsonify({
            "error": "Invalid API key",
            "code": "AUTH_INVALID_KEY"
        }), 401
    
    try:
        start_time = datetime.now(timezone.utc)
        data = request.get_json()
        
        if not data or "messages" not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: messages",
                "code": "MISSING_FIELD"
            }), 400
        
        messages = data.get("messages", [])
        
        if not isinstance(messages, list):
            return jsonify({
                "success": False,
                "error": "messages must be an array",
                "code": "INVALID_FORMAT"
            }), 400
        
        if len(messages) > 100:
            return jsonify({
                "success": False,
                "error": "Batch size cannot exceed 100 messages",
                "code": "BATCH_SIZE_EXCEEDED"
            }), 400
        
        # Analyze each message
        results = []
        for idx, msg_data in enumerate(messages):
            if isinstance(msg_data, str):
                message = msg_data
                message_id = f"msg_{idx}_{datetime.now(timezone.utc).timestamp()}"
                source = "unknown"
            elif isinstance(msg_data, dict):
                message = msg_data.get("message", "")
                message_id = msg_data.get("message_id", f"msg_{idx}_{datetime.now(timezone.utc).timestamp()}")
                source = msg_data.get("source", "unknown")
            else:
                continue
            
            if message and len(message) > 0:
                intelligence = intelligence_extractor.extract_all_intelligence(message)
                results.append({
                    "message_id": message_id,
                    "source": source,
                    "scam_score": round(intelligence["scam_score"], 3),
                    "severity_level": intelligence["severity_level"],
                    "is_scam": intelligence["severity_level"] in ["high", "medium"],
                })
        
        response = {
            "success": True,
            "total_messages": len(messages),
            "processed_messages": len(results),
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_time_ms": int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        }
        
        app.request_count += 1
        logger.info(f"Batch analyzed {len(results)} messages")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "details": str(e) if DEBUG else None
        }), 500

@app.route("/api/v1/stats", methods=["GET", "OPTIONS"])
def get_stats():
    """Get API statistics"""
    if request.method == "OPTIONS":
        return "", 200
    
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({
            "error": "Missing API key",
            "message": "Please provide X-API-Key header",
            "code": "AUTH_MISSING_KEY"
        }), 401
    
    if api_key != API_KEY:
        return jsonify({
            "error": "Invalid API key",
            "code": "AUTH_INVALID_KEY"
        }), 401
    
    return jsonify({
        "requests_processed": app.request_count,
        "uptime_seconds": int((datetime.now(timezone.utc) - app.start_time).total_seconds()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route("/api/v1/scam-categories", methods=["GET", "OPTIONS"])
def get_scam_categories():
    """Get list of recognized scam categories"""
    if request.method == "OPTIONS":
        return "", 200
    
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({
            "error": "Missing API key",
            "message": "Please provide X-API-Key header",
            "code": "AUTH_MISSING_KEY"
        }), 401
    
    if api_key != API_KEY:
        return jsonify({
            "error": "Invalid API key",
            "code": "AUTH_INVALID_KEY"
        }), 401
    
    from config import SCAM_KEYWORDS
    return jsonify({
        "scam_categories": list(SCAM_KEYWORDS.keys()),
        "total_categories": len(SCAM_KEYWORDS),
        "description": "List of scam categories used for classification"
    }), 200



@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist",
        "code": "NOT_FOUND"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "code": "INTERNAL_ERROR"
    }), 500

# ==================== Main ====================

if __name__ == "__main__":
    logger.info(f"Starting Agentic Honey-Pot API on {API_HOST}:{API_PORT}")
    logger.info(f"API Key: {API_KEY}")
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG)
