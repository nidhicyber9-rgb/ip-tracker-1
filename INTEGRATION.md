# 🔄 Integration Summary: File-Based vs Supabase

Complete guide for transitioning your IP Tracker Pro from file-based storage to Supabase.

---

## 📊 Comparison

| Feature | File-Based | Supabase |
|---------|-----------|----------|
| **Storage** | Local JSON files | PostgreSQL database |
| **Scalability** | Up to ~10K records | Unlimited (cloud) |
| **Deployment** | Heroku, local | Vercel, AWS, any host |
| **Real-time Sync** | No | Yes |
| **Backups** | Manual | Automatic |
| **Cost** | Free (local) | Free tier included |
| **Photos** | Local files | Cloud storage |
| **Setup Time** | 5 min | 15 min |

---

## 🚀 Quick Switch Guide

### Option 1: Use Supabase from Start (Recommended)

```bash
cd phishing_tool

# 1. Set up .env
cp .env.example .env.local

# 2. Edit .env.local with your Supabase credentials
# Get from: https://app.supabase.com → Settings → API

# 3. Use Supabase version
cp app_supabase.py app.py

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run
python app.py
```

### Option 2: Migrate Existing Data

If you have data from the file-based version:

```bash
cd phishing_tool

# 1. Set up .env (with Supabase credentials)
cp .env.example .env.local

# 2. Run migration script
python migrate_to_supabase.py

# 3. Switch to Supabase version
cp app_supabase.py app.py

# 4. Start application
python app.py
```

### Option 3: Keep Both Versions

```bash
cd phishing_tool

# Rename original
mv app.py app_file_based.py

# Use Supabase version
cp app_supabase.py app.py

# Create .env for Supabase
cp .env.example .env.local
# Edit .env.local with credentials

# Now you can switch by changing which app.py is used
# For file-based: cp app_file_based.py app.py
# For Supabase: cp app_supabase.py app.py
```

---

## 📁 File Reference

### Original Version (File-Based)
```
app.py                          # Main file-based Flask app
data/
├── campaigns/                  # Campaign configs (JSON)
└── results/                    # Session data (JSON)
    ├── *_ip.json              # IP & device data
    ├── *_gps.json             # GPS coordinates
    └── photos/                # Camera photos
```

### New Version (Supabase)
```
app_supabase.py                 # New Supabase-based app
app_file_based.py               # Backup of original
.env.local                       # Local credentials (not committed)
.env.example                     # Template for .env
database_schema.sql             # SQL to set up Supabase
migrate_to_supabase.py          # Migration script
SUPABASE_SETUP.md               # Detailed setup guide
```

---

## 🔐 Environment Variables

### `.env.local` (Local Development)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
FLASK_ENV=development
FLASK_DEBUG=0
SECRET_KEY=your-random-secret
```

### Vercel Secrets

Set these in Vercel dashboard → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `SUPABASE_URL` | From Supabase dashboard |
| `SUPABASE_KEY` | From Supabase dashboard |
| `SUPABASE_SERVICE_ROLE_KEY` | From Supabase dashboard |
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `0` |

---

## 🧪 Testing

### Test Locally

```bash
# 1. Start app
python app.py

# 2. Visit https://localhost:5000/
# 3. Create campaign
# 4. Check Supabase Table Editor:
#    - campaigns table
#    - sessions table
#    - gps_data table
#    - photos table

# 5. Verify health check
curl https://localhost:5000/api/health
# Should return: {"status":"ok","database":"connected"}
```

### Test on Vercel

```bash
# 1. Deploy
vercel --prod

# 2. Visit https://your-app.vercel.app/
# 3. Create campaign
# 4. Verify in Supabase dashboard
# 5. Check logs
vercel logs --tail
```

---

## 🔗 Data Flow Comparison

### File-Based Flow
```
Browser
  ↓
Flask App
  ↓
JSON Files (data/results/)
  ↓
Dashboard reads files
  ↓
Display results
```

### Supabase Flow
```
Browser
  ↓
Flask App (app_supabase.py)
  ↓
Supabase API
  ↓
PostgreSQL Database
  ↓
Dashboard queries database
  ↓
Display results (real-time)
```

---

## 📊 Database Schema

### Campaigns Table
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| campaign_id | VARCHAR | Unique campaign identifier |
| secret | VARCHAR | Secret token for link validation |
| level | INTEGER | 1, 2, or 3 (tracking level) |
| title | TEXT | Page title shown to user |
| redirect_url | TEXT | Where to redirect after capture |
| message | TEXT | Loading message |
| created_at | TIMESTAMP | Creation time |

### Sessions Table
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| session_id | VARCHAR | Unique session identifier |
| campaign_id | VARCHAR | Foreign key to campaigns |
| ip_address | VARCHAR | Client's IP address |
| device | VARCHAR | Desktop, Mobile, Tablet |
| browser | VARCHAR | Chrome, Firefox, etc. |
| os | VARCHAR | Windows, macOS, Android, etc. |
| user_agent | TEXT | Full browser user agent |
| is_forwarded | BOOLEAN | Was link forwarded? |
| timestamp | TIMESTAMP | When capture occurred |

### GPS Data Table
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| session_id | VARCHAR | Foreign key to sessions |
| latitude | DECIMAL | GPS latitude |
| longitude | DECIMAL | GPS longitude |
| accuracy | DECIMAL | Accuracy in meters |
| timestamp | TIMESTAMP | When captured |

### Photos Table
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| session_id | VARCHAR | Foreign key to sessions |
| photo_number | INTEGER | 1-5 for photo sequence |
| photo_url | TEXT | URL to photo in storage |
| timestamp | TIMESTAMP | When uploaded |

---

## 🐛 Troubleshooting

### Issue: "Cannot find .env variables"

```bash
# Solution: Make sure .env.local exists
ls -la .env.local

# And is in root of phishing_tool
cd phishing_tool && pwd
```

### Issue: "Supabase API key invalid"

```bash
# Solution: Verify credentials
# 1. Go to https://app.supabase.com
# 2. Select your project
# 3. Settings → API
# 4. Copy exact values (no extra spaces)
```

### Issue: Migration fails

```bash
# Solution: Check prerequisites
python migrate_to_supabase.py -v  # Verbose mode

# If migration fails:
# 1. Verify Supabase connection
# 2. Ensure database_schema.sql ran successfully
# 3. Check .env.local credentials
```

### Issue: Photos not uploading to Supabase

```bash
# Solution: Verify storage bucket
# 1. Supabase Dashboard → Storage
# 2. Click "photos" bucket
# 3. Check bucket is Public
# 4. Verify policies exist
```

---

## 🔄 Rollback to File-Based

If you need to revert:

```bash
cd phishing_tool

# Restore original
cp app_file_based.py app.py

# Comment out .env loading if not needed
python app.py
```

Old file-based data remains in `data/` directory.

---

## 📈 Scaling Considerations

### File-Based Limits
- ✓ Good for: < 1000 records, local testing
- ✗ Bad for: Large deployments, concurrent access
- ✗ Issue: Slow file I/O, no real-time sync

### Supabase Strengths
- ✓ Scales to millions of records
- ✓ Real-time database sync
- ✓ Built-in backups and recovery
- ✓ Global CDN for photos
- ✓ Automatic indexing and optimization

### Performance Optimization

```python
# Add caching
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=256)
def get_stats(ttl=300):
    # Results cached for 5 minutes
    return supabase.table('sessions').select('count', count='exact').execute()
```

---

## 🎯 Next Steps

1. **Set up Supabase account** (5 min)
   - https://supabase.com
   
2. **Create database schema** (5 min)
   - Paste `database_schema.sql` in Supabase SQL Editor
   
3. **Configure environment** (5 min)
   - Create `.env.local` with credentials
   
4. **Test locally** (5 min)
   - Run `python app.py`
   - Create campaign and verify data in Supabase
   
5. **Deploy to Vercel** (5 min)
   - Add environment variables
   - Push to GitHub
   - Vercel auto-deploys

6. **Monitor and optimize** (ongoing)
   - Supabase Dashboard
   - Vercel Analytics
   - Database Performance

---

## 📚 Documentation Index

- **README.md** - Overview of all features
- **QUICKSTART.md** - 5-minute getting started
- **INSTALL.md** - Installation and deployment
- **SUPABASE_SETUP.md** - Detailed Supabase guide
- **INTEGRATION.md** - This file (migration guide)

---

## ✅ Checklist for Migration

- [ ] Created Supabase account
- [ ] Set up database schema
- [ ] Copied API credentials
- [ ] Created `.env.local` file
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Tested locally: `python app.py`
- [ ] Verified data in Supabase dashboard
- [ ] Added secrets to Vercel
- [ ] Deployed to Vercel
- [ ] Tested production deployment
- [ ] Backed up old data (optional)

---

**Ready to migrate?** Start with [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

**Need help?** Check the troubleshooting section or create an issue on GitHub.

---

**Status:** ✅ Complete  
**Version:** 2.0 (Supabase Backend)  
**Last Updated:** 2024
