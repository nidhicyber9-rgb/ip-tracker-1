# Quick Start Guide - IP Tracker Pro

## Installation & Running

### 1. Install Dependencies
```bash
cd phishing_tool
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

You should see:
```
 * Running on https://127.0.0.1:5000
 * Press CTRL+C to quit
```

### 3. Access the Application
- **Campaign Builder:** https://localhost:5000/
- **Dashboard:** https://localhost:5000/dashboard

## First Test Run

### Step 1: Create a Campaign
1. Open https://localhost:5000/
2. Select "IP Tracker + GPS + Photos"
3. Enter a title: "Test Campaign"
4. Leave redirect URL empty (optional)
5. Click "Generate Phishing Link"
6. Copy the generated link

### Step 2: Test the Link
1. Open the link in a new browser window
2. You'll see a loading page
3. The tool will:
   - Capture your IP and device info (immediate)
   - Ask for GPS permission (after ~2 seconds)
   - Ask for camera permission
   - Capture 5 photos at 1-second intervals
   - Show "Verification complete"

### Step 3: View Results
1. Go to https://localhost:5000/dashboard
2. You should see:
   - Stats: 1 total hit, 1 unique IP, 1 GPS capture, 1 photo capture
   - Your entry in the table with IP, device, browser, OS
   - Badges showing: IP, GPS, 📸
3. Click "View" to see detailed information including photos

## Common Issues

### "Connection not private" Warning
- This is normal for self-signed certificates
- Click "Advanced" → "Proceed to localhost"
- In production, use proper SSL certificates

### GPS Not Working
- Make sure you allow location access when prompted
- GPS requires HTTPS (it won't work on HTTP)
- Some networks block geolocation

### Camera Not Capturing
- Allow camera access when prompted
- Some browsers may require https and explicit permissions
- Mobile devices may have additional permission prompts

### Port Already in Use
If port 5000 is already in use, edit `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

## File Structure

```
phishing_tool/
├── app.py                 # Main Flask app
├── requirements.txt       # Python packages
├── README.md             # Full documentation
├── QUICKSTART.md         # This file
├── templates/
│   ├── index.html        # Home page
│   ├── track.html        # Phishing page
│   ├── dashboard.html    # Results dashboard
│   └── 404.html          # Error page
├── static/
│   ├── style.css         # Styling
│   └── script.js         # JavaScript
└── data/
    ├── campaigns/        # Campaign configs
    └── results/          # Captured data
        └── photos/       # Photos directory
```

## Data Locations

- **Campaign configs:** `phishing_tool/data/campaigns/`
- **IP & device data:** `phishing_tool/data/results/*_ip.json`
- **GPS data:** `phishing_tool/data/results/*_gps.json`
- **Photos:** `phishing_tool/data/results/photos/<session_id>/`
- **Export:** Dashboard → "Export Data" button

## API Quick Reference

```
GET  /                          # Home page
POST /api/generate              # Create campaign
GET  /track?id=<id>&s=<secret> # Phishing page
POST /api/capture               # Capture endpoint
GET  /dashboard                 # Results dashboard
GET  /api/dashboard/stats       # Get statistics
GET  /api/dashboard/session/<id># Get session details
GET  /api/dashboard/export      # Export all data
```

## Tips for Testing

### Localhost Testing
- Self-signed cert is fine for testing
- GPS/Camera work on localhost (special case)
- Dashboard auto-refreshes every 3 seconds

### Real Domain Testing
- You need proper SSL certificates
- Use Let's Encrypt (free) for production
- Point DNS to your server
- Deploy behind nginx/apache

### Troubleshooting Captures
- Open browser DevTools (F12)
- Check Console tab for JavaScript errors
- Check Network tab to see API calls
- Look for 200 status on `/api/capture` requests

## Legal Reminder

⚠️ **This tool is ONLY for authorized security testing.**
- Get written permission before any testing
- Clearly define the scope of testing
- Document all activities
- Follow local laws and regulations
- Respect user privacy

## Next Steps

1. **Learn More:** Read the full [README.md](README.md)
2. **Deploy:** Set up on a test server with proper SSL
3. **Customize:** Modify templates/styling as needed
4. **Secure:** Use strong authentication in production
5. **Test Safely:** Always test in controlled environments first

## Support

For questions about penetration testing methodology, refer to:
- OWASP: https://owasp.org/
- NIST: https://www.nist.gov/
- Your security provider
