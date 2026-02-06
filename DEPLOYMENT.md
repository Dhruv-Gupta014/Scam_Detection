# Agentic Honey-Pot - Deployment Guide

## Quick Start

### Local Development

```bash
# 1. Navigate to project directory
cd c:\Users\91798\OneDrive\Desktop\Scam_Detection

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py

# 4. Test the API
python test_api.py

# 5. Try the example client
python example_client.py
```

---

## Running the API

### Option 1: Direct Python (Development)
```bash
python app.py
```
- Single-threaded
- Good for development and testing
- Auto-reloads on code changes with DEBUG=True

### Option 2: Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
- Multi-worker (4 workers by default)
- Production-ready
- Better performance
- Handles multiple concurrent requests

### Option 3: Uvicorn (Async Alternative)
```bash
pip install uvicorn
uvicorn app:app --host 0.0.0.0 --port 5000 --workers 4
```
- Async support
- Better for I/O operations
- Modern ASGI server

---

## Configuration

Edit `.env` file to configure:

```
API_PORT=5000              # Port to run API on
API_HOST=0.0.0.0           # Host to bind to
DEBUG=False                # Debug mode (True for development)
API_KEY=your-secret-key    # Change this to your own key!
```

---

## Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run application
ENV API_PORT=5000
ENV API_HOST=0.0.0.0
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Build and Run

```bash
# Build image
docker build -t scam-detection-api:latest .

# Run container
docker run -p 5000:5000 \
  -e API_KEY=your-secret-key \
  -e API_PORT=5000 \
  -e DEBUG=False \
  scam-detection-api:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: scam-detection-api
    ports:
      - "5000:5000"
    environment:
      - API_PORT=5000
      - API_HOST=0.0.0.0
      - API_KEY=your-secret-key-change-this
      - DEBUG=False
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

---

## Cloud Deployment

### AWS EC2

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - Security group: Allow port 5000 (or 80/443 with reverse proxy)

2. **SSH into instance**
   ```bash
   ssh -i key.pem ubuntu@your-instance-ip
   ```

3. **Install Python and dependencies**
   ```bash
   sudo apt update
   sudo apt install python3.10 python3-pip git
   ```

4. **Clone and setup**
   ```bash
   git clone <your-repo>
   cd Scam_Detection
   pip install -r requirements.txt
   ```

5. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

6. **Use systemd for auto-restart**
   Create `/etc/systemd/system/scam-detection.service`:
   ```ini
   [Unit]
   Description=Scam Detection API
   After=network.target

   [Service]
   Type=notify
   User=ubuntu
   WorkingDirectory=/home/ubuntu/Scam_Detection
   ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Enable service:
   ```bash
   sudo systemctl enable scam-detection
   sudo systemctl start scam-detection
   ```

### Heroku

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Create Procfile**
   ```
   web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables**
   ```bash
   heroku config:set API_KEY=your-secret-key
   heroku config:set DEBUG=False
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **View logs**
   ```bash
   heroku logs --tail
   ```

### Google Cloud Run

1. **Create `cloudbuild.yaml`**
   ```yaml
   steps:
     - name: 'gcr.io/cloud-builders/docker'
       args: ['build', '-t', 'gcr.io/$PROJECT_ID/scam-detection-api', '.']
     - name: 'gcr.io/cloud-builders/docker'
       args: ['push', 'gcr.io/$PROJECT_ID/scam-detection-api']
     - name: 'gcr.io/cloud-builders/run'
       args:
         - 'deploy'
         - 'scam-detection-api'
         - '--image'
         - 'gcr.io/$PROJECT_ID/scam-detection-api'
         - '--region'
         - 'us-central1'
         - '--allow-unauthenticated'
         - '--set-env-vars'
         - 'API_KEY=your-secret-key'
   ```

2. **Deploy**
   ```bash
   gcloud builds submit
   ```

### Vercel/Netlify

Vercel doesn't natively support Flask, but you can use Vercel Functions:

Create `vercel.json`:
```json
{
  "buildCommand": "pip install -r requirements.txt",
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.10"
    }
  },
  "env": {
    "API_KEY": "@api_key"
  }
}
```

---

## HTTPS Setup with Nginx (Reverse Proxy)

Install Nginx:
```bash
sudo apt install nginx certbot python3-certbot-nginx
```

Configure `/etc/nginx/sites-available/default`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable HTTPS:
```bash
sudo certbot --nginx -d your-domain.com
```

---

## Performance Tuning

### Gunicorn Settings
```bash
# More workers for CPU-bound tasks
gunicorn -w 8 --threads 4 -b 0.0.0.0:5000 app:app

# For high concurrency
gunicorn -w 4 --worker-class gevent -b 0.0.0.0:5000 app:app

# With timeout and graceful shutdown
gunicorn -w 4 --timeout 30 --graceful-timeout 10 -b 0.0.0.0:5000 app:app
```

### Rate Limiting
Adjust in `config.py`:
```python
RATE_LIMIT_PER_MINUTE = 100  # Increase from 60 for higher throughput
```

### Caching
Consider adding Redis for caching:
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=3600)
def expensive_operation():
    pass
```

---

## Monitoring & Logging

### Application Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Uptime Monitoring
- Use tools like UptimeRobot
- Monitor `/health` endpoint every 5 minutes
- Get alerts if endpoint is down

### Log Aggregation
- Use ELK Stack (Elasticsearch, Logstash, Kibana)
- Use Datadog or New Relic
- Use CloudWatch (for AWS)

---

## API Key Management

### Generate Strong API Keys
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Rotate API Keys
1. Generate new key
2. Add to environment: `NEW_API_KEY=...`
3. Update code to accept both keys temporarily
4. Inform clients of new key
5. Deprecate old key

---

## Testing Before Deployment

```bash
# Health check
curl http://localhost:5000/health

# Analyze message
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"message":"test scam message"}'

# Load testing with Apache Bench
ab -n 1000 -c 10 -H "X-API-Key: your-api-key" http://localhost:5000/health

# Load testing with wrk
wrk -t4 -c100 -d30s --script=api_load_test.lua http://localhost:5000/api/v1/analyze
```

---

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux
lsof -i :5000
kill -9 <PID>
```

### Memory Issues
- Reduce worker count in Gunicorn
- Use Uvicorn with async workers
- Monitor with: `htop` or `docker stats`

### Slow Requests
- Check network latency
- Increase worker count
- Profile with: `py-spy` or `cProfile`

---

## Backup & Recovery

### Database Backups (if added)
```bash
# PostgreSQL
pg_dump -h localhost -U user -d db_name > backup.sql

# MongoDB
mongodump --db scam_detection --out backup/
```

### Configuration Backups
```bash
# Backup .env
cp .env .env.backup

# Backup configuration
cp config.py config.py.backup
```

---

## Checklist for Production

- [ ] Change API key in `.env`
- [ ] Set `DEBUG=False`
- [ ] Use HTTPS with valid SSL certificate
- [ ] Setup rate limiting appropriately
- [ ] Configure logging and monitoring
- [ ] Setup automated backups
- [ ] Document API endpoint and key
- [ ] Setup health monitoring
- [ ] Load test before launch
- [ ] Create incident response plan
- [ ] Document rollback procedure
- [ ] Setup error alerting

---

## Support

For deployment issues, check:
- Application logs: `python app.py` or `gunicorn` output
- API health: `curl http://your-api/health`
- Network connectivity
- Firewall rules
- Environment variables
