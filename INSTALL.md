# IP Tracker Pro - Installation & Deployment Guide

## 🎯 Project Overview

**IP Tracker Pro** is a Python/Flask web application for authorized penetration testing. It generates phishing simulation links that capture:

- **Mode 1:** IP address, device type, browser, OS
- **Mode 2:** Everything above + GPS coordinates  
- **Mode 3:** Everything above + 5 camera photos

All data is collected in a real-time dashboard with photo gallery and export functionality.

---

## 📋 What's Included

```
phishing_tool/
├── Core Application
│   ├── app.py                 # Main Flask application (450+ lines)
│   ├── requirements.txt       # Python dependencies
│   └── setup.sh              # Automated setup script
│
├── Frontend Templates
│   ├── templates/
│   │   ├── index.html        # Campaign builder UI
│   │   ├── track.html        # Phishing page (target sees this)
│   │   ├── dashboard.html    # Results dashboard
│   │   └── 404.html          # Error pages
│   │
│   └── static/
│       ├── style.css         # Styling & animations
│       └── script.js         # Client-side logic
│
├── Data Storage
│   └── data/
│       ├── campaigns/        # Campaign configurations
│       └── results/          # Captured IP, GPS, photos
│
├── Deployment
│   ├── Dockerfile            # Docker containerization
│   ├── docker-compose.yml    # Docker Compose setup
│   └── .gitignore            # Git ignore rules
│
└── Documentation
    ├── README.md             # Full documentation (400+ lines)
    ├── QUICKSTART.md         # Quick start guide
    └── INSTALL.md            # This file
```

---

## ⚡ Quick Start (5 Minutes)

### 1. Navigate to Project
```bash
cd /workspaces/IPTracer/phishing_tool
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```

You should see:
```
 * Running on https://127.0.0.1:5000
 * Running on https://0.0.0.0:5000
 * Press CTRL+C to quit
```

### 4. Access in Browser
- **Home:** https://localhost:5000/
- **Dashboard:** https://localhost:5000/dashboard

⚠️ **Browser Warning:** Click "Advanced" → "Proceed to localhost" for the self-signed certificate.

---

## 📦 Installation Methods

### Method 1: Manual Installation (Recommended for Testing)

```bash
# Navigate to project
cd phishing_tool

# Install Python packages
pip install -r requirements.txt

# Run application
python app.py
```

### Method 2: Virtual Environment (Recommended for Production)

```bash
cd phishing_tool

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

### Method 3: Automated Setup Script

```bash
cd phishing_tool
bash setup.sh
source venv/bin/activate
python app.py
```

### Method 4: Docker (Container Deployment)

```bash
cd phishing_tool

# Build image
docker build -t iptracker-pro .

# Run container
docker run -p 5000:5000 -v $(pwd)/data:/app/data iptracker-pro

# OR use Docker Compose
docker-compose up -d
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in `phishing_tool/` directory:

```env
FLASK_ENV=production          # or 'development'
FLASK_DEBUG=0                # 1 for development, 0 for production
SECRET_KEY=your-secret-key   # Generate one: python -c "import secrets; print(secrets.token_hex(16))"
```

### Port Configuration

Edit `app.py` to change port:

```python
if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001,  # Change this
        ssl_context='adhoc'
    )
```

### Data Directories

Data is stored in `phishing_tool/data/`:
- `campaigns/` - Campaign configurations (JSON)
- `results/` - Captured data
  - `*_ip.json` - IP & device info
  - `*_gps.json` - GPS coordinates
  - `photos/` - Camera photos

---

## 🔐 Security Considerations

### HTTPS/SSL

**Required Features:**
- GPS API only works over HTTPS
- Camera API only works over HTTPS
- Development: Self-signed certificate (included via `ssl_context='adhoc'`)
- Production: Use proper certificates

### Generate Self-Signed Certificate

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365 \
  -subj "/C=US/ST=State/L=City/O=Org/CN=localhost"
```

### Production Deployment

Use a proper reverse proxy (Nginx/Apache) with real SSL certificates:

```nginx
server {
    listen 443 ssl http2;
    server_name pentest.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass https://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Data Protection

- No data sent to external services
- All data stored locally
- Database: File-based JSON (no SQL)
- Photos: Stored as JPEG files
- Access control: Implement in reverse proxy

---

## 🚀 Deployment Scenarios

### Scenario 1: Local Testing
```bash
python app.py
# Access: https://localhost:5000/
# Self-signed cert warning is OK
```

### Scenario 2: LAN Testing
```bash
# Get local IP
hostname -I  # Linux/Mac
ipconfig     # Windows

# Access: https://<your-lan-ip>:5000/
python app.py
```

### Scenario 3: Cloud/VPS Deployment

1. **Prepare server (Ubuntu 20.04+):**
```bash
apt update && apt upgrade
apt install python3 python3-pip nginx
```

2. **Clone and setup:**
```bash
cd /opt
git clone https://github.com/username/IPTracer.git
cd IPTracer/phishing_tool
pip install -r requirements.txt
```

3. **Create Systemd service** (`/etc/systemd/system/iptracker.service`):
```ini
[Unit]
Description=IP Tracker Pro
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/IPTracer/phishing_tool
ExecStart=/usr/bin/python3 /opt/IPTracer/phishing_tool/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Enable service:**
```bash
systemctl enable iptracker
systemctl start iptracker
```

5. **Configure Nginx reverse proxy:**
```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/iptracker
sudo ln -s /etc/nginx/sites-available/iptracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📊 Database Structure

### Campaign Config (`data/campaigns/<id>.json`)
```json
{
  "id": "a1b2c3d4e5f6...",
  "level": 3,
  "title": "Security Verification",
  "redirect": "https://example.com",
  "message": "Verifying your identity...",
  "created_at": "2024-01-15T10:30:00",
  "secret": "secret_token"
}
```

### IP Data (`data/results/<id>_ip.json`)
```json
{
  "session_id": "xyz...",
  "timestamp": "2024-01-15T10:31:00",
  "ip_address": "203.0.113.42",
  "device": "Mobile",
  "browser": "Chrome 120",
  "os": "Android 13",
  "user_agent": "Mozilla/5.0...",
  "is_forwarded": false
}
```

### GPS Data (`data/results/<id>_gps.json`)
```json
{
  "session_id": "xyz...",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "accuracy": 15.5,
  "google_maps": "https://www.google.com/maps?q=40.7128,-74.0060"
}
```

---

## 🐛 Troubleshooting

### Port 5000 Already in Use
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port in app.py
app.run(port=5001)
```

### SSL Certificate Error
```bash
# Install pyopenssl
pip install pyopenssl

# Generate self-signed cert
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365
```

### GPS Not Working
- ✓ Using HTTPS (not HTTP)
- ✓ Browser permission granted
- ✓ Not using VPN/proxy that blocks location
- ✓ Device has GPS hardware

### Camera Not Capturing
- ✓ Using HTTPS
- ✓ Browser permission granted
- ✓ Device has camera
- ✓ Another app isn't using camera

### Photos Not Saving
```bash
# Check directory permissions
ls -la phishing_tool/data/results/

# Fix permissions
chmod 755 phishing_tool/data/results/
mkdir -p phishing_tool/data/results/photos
```

---

## 📈 Performance & Scaling

### Optimization Tips

1. **Caching:**
   - Dashboard auto-refreshes every 3 seconds
   - Static files served directly

2. **Scalability:**
   - File-based storage scales to thousands of records
   - For millions: Use database (PostgreSQL/MongoDB)

3. **API Rate Limiting:**
   - Consider adding Flask-Limiter for production

### Typical Specs
- **Users:** Single to moderate (< 100 concurrent)
- **Data Storage:** ~1MB per session with photos
- **Processing:** Sub-100ms per capture
- **Memory:** ~50-100MB baseline

---

## ⚠️ Legal & Ethical Notice

This tool is **ONLY** for authorized security testing:

✓ Get written authorization from organization owner
✓ Define clear scope of engagement
✓ Document all activities
✓ Respect privacy laws (GDPR, CCPA, etc.)
✓ Don't use on systems you don't own/have permission for

❌ **Illegal uses will result in prosecution**

---

## 📚 Additional Resources

- **OWASP:** https://owasp.org/
- **Penetration Testing Standards:** https://nist.gov/
- **Web Security:** https://portswigger.net/web-security
- **Flask Documentation:** https://flask.palletsprojects.com/

---

## ✨ Features Summary

| Feature | Status | Details |
|---------|--------|---------|
| IP Tracking | ✅ | Country, city, ISP, user agent |
| Device Detection | ✅ | Desktop/Mobile/Tablet |
| Browser ID | ✅ | Chrome, Firefox, Safari, Edge, etc. |
| OS Detection | ✅ | Windows, macOS, Linux, iOS, Android |
| GPS Capture | ✅ | Latitude, longitude, accuracy |
| Google Maps Link | ✅ | Direct link to coordinates |
| Camera Capture | ✅ | 5 photos at 1-second intervals |
| Dashboard | ✅ | Real-time results with photos |
| Export | ✅ | JSON export of all data |
| Forward Detection | ✅ | Detect link forwarding/sharing |
| Data Visualization | ✅ | Stats cards, tables, photo gallery |
| Mobile Responsive | ✅ | Works on phones/tablets |

---

## 🎓 Getting Started

1. **Read:** [README.md](README.md) - Full documentation
2. **Quick Start:** [QUICKSTART.md](QUICKSTART.md) - 5-minute test
3. **Deploy:** Use instructions above
4. **Test:** Create campaign and test the link
5. **Monitor:** Watch dashboard for real-time data

---

## 📞 Support

For installation issues:
1. Check Python version: `python3 --version` (need 3.7+)
2. Verify dependencies: `pip list | grep -i flask`
3. Test import: `python3 -c "import flask; print(flask.__version__)"`
4. Check logs: Look at terminal output for errors

For security questions, consult with your organization's security team or a professional penetration testing firm.

---

**Version:** 1.0  
**Last Updated:** 2024  
**Status:** Ready for Testing ✓
