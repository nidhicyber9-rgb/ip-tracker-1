# IP Tracker Pro - Flask-Based Phishing Simulation Tool

A Python/Flask web application for authorized penetration testing that captures IP addresses, GPS location, and photos from targets via phishing links.

## ⚠️ Legal Notice

**This tool is designed ONLY for authorized penetration testing within proper scope and with explicit written permission from the organization being tested. Unauthorized access to computer systems is illegal.**

## Features

### Three Tracking Modes

**Mode 1: IP Tracker**
- IP address and geolocation estimation
- Device type (Desktop, Mobile, Tablet)
- Browser and OS identification
- User-Agent string capture
- Referrer tracking
- Forward chain detection

**Mode 2: IP Tracker + GPS**
- Everything from Mode 1
- Precise GPS coordinates (requires user consent)
- GPS accuracy metrics
- Direct Google Maps links

**Mode 3: IP Tracker + GPS + Photos**
- Everything from Modes 1 & 2
- Captures 5 front-facing camera photos
- Camera access detection
- Base64 encoded image storage

### Dashboard Features
- Real-time statistics (total hits, unique IPs, GPS captures, photo captures)
- Detailed session view with all captured information
- Photo gallery for camera captures
- Forward detection (identifies when targets forward the link)
- JSON export for all captured data
- Auto-refreshing data (3-second interval)

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)
- OpenSSL (for HTTPS support)

### Setup Steps

1. **Clone and navigate to the tool:**
```bash
cd phishing_tool
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python app.py
```

The application will start on `https://localhost:5000`

## Usage

### Creating a Campaign

1. Navigate to `https://localhost:5000/`
2. Select your tracking level:
   - **IP Tracker** - Basic IP and device info
   - **IP Tracker + GPS** - Adds GPS location (with consent popup)
   - **IP Tracker + GPS + Photos** - Adds camera capture (5 photos)
3. Customize:
   - **Target Page Title** - What the page header displays
   - **Redirect URL** (optional) - Where to redirect after capture
   - **Loading Message** - Status message shown during capture
4. Click "Generate Phishing Link"
5. Copy the generated link and share with your target

### Monitoring Results

1. Navigate to `/dashboard`
2. View real-time statistics:
   - Total hits
   - Unique IP addresses
   - GPS captures
   - Photo captures
3. Click "View" on any entry to see detailed information:
   - Full IP data
   - GPS coordinates (if captured)
   - Camera photos (if captured)
4. Use "Export Data" to download all results as JSON

## Technical Architecture

```
phishing_tool/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html        # Campaign builder interface
│   ├── track.html        # Phishing page (target visits)
│   ├── dashboard.html    # Results dashboard
│   └── 404.html          # Error page
├── static/
│   ├── style.css         # Styling (gradient background, cards, forms)
│   └── script.js         # Frontend logic
└── data/
    ├── campaigns/        # Stores campaign configurations
    └── results/          # Stores captured data
        └── photos/       # Stores captured photos
```

## API Endpoints

### Campaign Management
- `POST /api/generate` - Create new campaign
- `GET /track?id=<id>&s=<secret>` - The phishing page

### Data Capture
- `POST /api/capture` - Handle IP, GPS, and photo data

### Dashboard
- `GET /dashboard` - View dashboard interface
- `GET /api/dashboard/stats` - Get statistics
- `GET /api/dashboard/session/<id>` - Get session details
- `GET /api/dashboard/export` - Export all data

## How It Works

### Step 1: IP & Device Capture
When target visits the phishing link:
1. JavaScript captures IP address (via request metadata)
2. User-Agent parsed for browser, OS, device type
3. Data sent to `/api/capture` endpoint
4. Progress bar shows 20% complete

### Step 2: GPS Capture (Mode 2+)
1. Browser's Geolocation API requests permission (via popup)
2. If granted, GPS coordinates and accuracy captured
3. Google Maps link generated for coordinates
4. Progress bar shows 50% complete

### Step 3: Camera Capture (Mode 3)
1. Camera permission requested via browser popup
2. 5 photos captured at 1-second intervals
3. Photos sent to server as base64-encoded images
4. Stored as JPEG files in `data/results/photos/<session_id>/`
5. Progress bar shows 100% complete

### Step 4: Redirect
- If redirect URL configured, user redirected to legitimate site
- Otherwise, simple "Verification Complete" message shown

## Data Storage

### Campaign Data (`data/campaigns/<id>.json`)
```json
{
  "id": "hex_campaign_id",
  "level": 1,
  "title": "Security Verification Required",
  "redirect": "https://example.com/login",
  "message": "Verifying your identity...",
  "created_at": "2024-01-15T10:30:00",
  "secret": "hex_secret_key"
}
```

### Session Data (`data/results/<session_id>_ip.json`)
```json
{
  "session_id": "hex_session_id",
  "timestamp": "2024-01-15T10:31:00",
  "ip_address": "203.0.113.42",
  "device": "Mobile",
  "browser": "Chrome 120.0",
  "os": "Android 13",
  "user_agent": "Mozilla/5.0...",
  "is_forwarded": false
}
```

### GPS Data (`data/results/<session_id>_gps.json`)
```json
{
  "session_id": "hex_session_id",
  "timestamp": "2024-01-15T10:31:05",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "accuracy": 15.5,
  "google_maps": "https://www.google.com/maps?q=40.7128,-74.0060"
}
```

### Photo Data (`data/results/<session_id>_photos.json`)
```json
{
  "session_id": "hex_session_id",
  "timestamp": "2024-01-15T10:31:10",
  "count": 5,
  "photos": ["photo_1.jpg", "photo_2.jpg", ...],
  "directory": "data/results/photos/session_id"
}
```

## Forward Detection

The tool detects when targets forward phishing links to others:

1. First visitor receives a cookie: `ipt_original_id=<campaign_id>`
2. If another user clicks link with that cookie, `is_forwarded` flag set to `true`
3. Dashboard shows forwarding chain
4. Useful for understanding link propagation

## Security Considerations

### HTTPS Requirement
- GPS and Camera APIs only work over HTTPS
- App uses ad-hoc SSL (for dev/testing)
- **For production:** Use proper SSL certificates via reverse proxy (nginx, Apache)

### Data Privacy
- All data stored locally on your server
- No third-party API calls
- No data sent to external services
- Photos stored as files, not in database

### Authorization
- **Always obtain written permission before testing**
- Clearly scope the engagement
- Document what data you're collecting
- Respect target's privacy laws (GDPR, CCPA, etc.)

## Deployment

### Development (Local Testing)
```bash
python app.py
```

### Production (WSGI Server)
```bash
# Install production server
pip install gunicorn pyopenssl

# Run with Gunicorn
gunicorn --certfile=cert.pem --keyfile=key.pem --bind 0.0.0.0:5000 app:app
```

### With Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl http2;
    server_name pentest.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass https://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Troubleshooting

### GPS Not Working
- Requires HTTPS (not HTTP)
- Browser may block geolocation on insecure contexts
- User must grant permission in popup
- Some devices/networks may have GPS disabled

### Camera Not Capturing
- Requires HTTPS
- Browser must have camera permission
- Mobile devices may require explicit app permission
- Some devices may have camera hardware issues

### Photos Not Saving
- Ensure `data/results/photos/` directory exists and is writable
- Check file permissions: `chmod 755 data/results/photos/`
- Verify disk space availability

### Port Already in Use
```bash
# Change port in app.py
app.run(port=5001)  # Use different port
```

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| IP Capture | ✓ | ✓ | ✓ | ✓ |
| GPS | ✓ | ✓ | ✓ | ✓ |
| Camera | ✓ | ✓ | ✓ | ✓ |

**Note:** All features require HTTPS on modern browsers (except localhost).

## Example Workflow

1. **Create Campaign:**
   - Mode 3 (IP + GPS + Photos)
   - Title: "Account Verification Required"
   - Redirect: `https://company.com/login`
   - Message: "Verifying your account..."

2. **Share Link:**
   - Send to target via email/SMS
   - Make it look legitimate

3. **Target Visits Link:**
   - Browser shows loading page
   - Captures IP, device, browser info
   - Asks for location permission
   - Requests camera access
   - Captures 5 photos
   - Redirects to legitimate login page

4. **Review Results:**
   - Dashboard shows new entry
   - Click "View" to see photos
   - Export data for reporting

## Contributing

This is a demonstration tool for authorized security testing. For improvements or bug reports, please follow responsible disclosure practices.

## License

Educational use only. Unauthorized use is illegal.

## Support

For issues or questions about legitimate penetration testing usage, refer to your authorized security provider or OWASP resources.
