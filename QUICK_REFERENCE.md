# 📋 IP Tracker Pro - Supabase Integration Quick Reference

**Complete setup in 3 main steps**

---

## ⚡ TL;DR - Quick Setup (15 Minutes)

### 1️⃣ Supabase Setup (5 min)

```bash
# 1. Go to https://supabase.com → Sign up (free)
# 2. Create new project
# 3. Wait for project to initialize (~2 min)
# 4. Go to SQL Editor → New Query
# 5. Paste content from database_schema.sql
# 6. Click Run
# 7. Settings → API → Copy:
#    - Project URL → SUPABASE_URL
#    - anon key → SUPABASE_KEY
#    - service_role secret → SUPABASE_SERVICE_ROLE_KEY
```

### 2️⃣ Local Configuration (5 min)

```bash
cd /workspaces/IPTracer/phishing_tool

# Create .env.local
cat > .env.local << 'EOF'
SUPABASE_URL=YOUR_PROJECT_URL_HERE
SUPABASE_KEY=YOUR_ANON_KEY_HERE
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY_HERE
FLASK_ENV=development
EOF

# Edit with your actual credentials
nano .env.local
```

### 3️⃣ Run Application (5 min)

```bash
# Install dependencies
pip install -r requirements.txt

# Use Supabase version
cp app_supabase.py app.py

# Run
python app.py

# Visit: https://localhost:5000/
```

---

## 📊 File Structure

```
phishing_tool/
│
├── 📄 Original Files (File-Based)
│   ├── app.py                    # Original (or renamed to app_file_based.py)
│   ├── data/campaigns/           # Campaign JSON files
│   └── data/results/             # Session JSON files
│
├── 🆕 New Files (Supabase)
│   ├── app_supabase.py           # ⭐ Use this version
│   ├── app_file_based.py         # Backup of original
│   ├── .env.example              # Template for credentials
│   ├── database_schema.sql       # SQL schema (run in Supabase)
│   ├── migrate_to_supabase.py   # Migrate old data
│   ├── SUPABASE_SETUP.md         # Detailed guide
│   └── INTEGRATION.md            # Migration guide
│
└── 📚 Documentation
    ├── README.md                 # Overview
    ├── QUICKSTART.md             # Quick start
    ├── INSTALL.md                # Installation
    └── This file                 # Quick reference
```

---

## 🔑 Environment Variables

### `.env.local` (Never commit to git)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
FLASK_ENV=development
FLASK_DEBUG=0
```

### Vercel Environment Variables

Set in Vercel Dashboard → Settings → Environment Variables:

```
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
FLASK_ENV=production
FLASK_DEBUG=0
```

---

## 🔄 Switch Between Versions

### Use Supabase Version
```bash
cp app_supabase.py app.py
python app.py  # Must have .env.local with credentials
```

### Use File-Based Version
```bash
cp app_file_based.py app.py
python app.py  # No credentials needed (uses local data/)
```

---

## 📊 Database Tables

| Table | Purpose | Records |
|-------|---------|---------|
| `campaigns` | Campaign configs | 1 per campaign |
| `sessions` | IP & device data | 1 per visit |
| `gps_data` | GPS coordinates | 1 per mode 2+ visit |
| `photos` | Photo records | 5 per mode 3 visit |
| `photos` (storage) | Photo files | Cloud storage |

---

## ✅ Verify Installation

### Check Dependencies
```bash
python -c "import supabase; print('✓ Supabase installed')"
```

### Check Connection
```bash
curl https://localhost:5000/api/health
# Should return: {"status":"ok","database":"connected"}
```

### Check Database
1. Go to https://app.supabase.com
2. Select your project
3. Go to Table Editor
4. Should see: campaigns, sessions, gps_data, photos tables

---

## 🧪 Test the Setup

```bash
# 1. Start app
python app.py

# 2. Open browser
# https://localhost:5000/

# 3. Create campaign (Mode 1 for quick test)

# 4. Copy the generated link

# 5. Open link in new tab (may need to accept cert warning)

# 6. Check Supabase dashboard:
# Go to Table Editor → campaigns (should see your campaign)
# Go to Table Editor → sessions (should see your visit)

# 7. Go to https://localhost:5000/dashboard
# Should show: 1 total hit, 1 unique IP
```

---

## 📈 Performance Tips

### Database Queries
```python
# ✓ Good: Limit results
supabase.table('sessions').select('*').limit(100).execute()

# ✗ Bad: Fetch all
supabase.table('sessions').select('*').execute()
```

### Batch Inserts
```python
# Insert multiple at once (faster)
records = [
    {'session_id': '1', ...},
    {'session_id': '2', ...},
]
supabase.table('sessions').insert(records).execute()
```

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_stats():
    return supabase.table('sessions').select('count', count='exact').execute()
```

---

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| "SUPABASE_URL not set" | Check `.env.local` exists and has credentials |
| "Connection refused" | Verify Supabase project is running (check dashboard) |
| "Invalid credentials" | Copy exact values from Supabase Settings → API |
| "No data showing" | Check Supabase Table Editor for records |
| "Photos not uploading" | Verify `photos` storage bucket exists and is public |
| "Migration fails" | Run `database_schema.sql` first in Supabase SQL Editor |

---

## 🚀 Deployment Checklist

### Before Deploying

- [ ] `.env.local` configured with Supabase credentials
- [ ] Database schema created in Supabase (`database_schema.sql` run)
- [ ] Storage bucket `photos` created and set to public
- [ ] App tested locally: `python app.py`
- [ ] Health check works: `curl .../api/health`

### Deploy to Vercel

```bash
# 1. Commit and push
git add phishing_tool/
git commit -m "feat: Add Supabase integration"
git push origin main

# 2. Go to https://vercel.com
# 3. Connect GitHub repository
# 4. Add environment variables (same as .env.local)
# 5. Deploy

# Or use CLI
vercel --prod
```

### Post-Deployment

- [ ] Visit deployed URL
- [ ] Create test campaign
- [ ] Verify data in Supabase
- [ ] Check Vercel logs for errors
- [ ] Monitor dashboard activity

---

## 📚 Documentation Guide

| Document | Purpose | Time |
|----------|---------|------|
| **QUICKSTART.md** | 5-minute setup | 5 min |
| **SUPABASE_SETUP.md** | Detailed Supabase guide | 20 min |
| **INSTALL.md** | Installation methods | 15 min |
| **INTEGRATION.md** | Migration from file-based | 30 min |
| **README.md** | Complete reference | 30 min |
| **This file** | Quick lookup | 5 min |

---

## 🎯 Next Steps

1. **Complete Quick Setup** (above) - 15 min
2. **Read SUPABASE_SETUP.md** - 20 min
3. **Deploy to Vercel** - 10 min
4. **Test in production** - 5 min

**Total Time: ~50 minutes**

---

## 💡 Pro Tips

```bash
# View Supabase logs
# Supabase Dashboard → Logs

# Monitor Vercel deployment
# Vercel Dashboard → Analytics

# Check database queries
# Supabase Dashboard → Query Performance

# Export your data
# Dashboard → Export Data button

# Scale your deployment
# Supabase Pro plan ($25/mo)
```

---

## 🔐 Security Notes

- ✅ API keys stored in `.env.local` (not in git)
- ✅ Vercel secrets private (not accessible via URL)
- ✅ Database credentials not in code
- ✅ HTTPS required (enforced in production)
- ⚠️ Never paste credentials in code/comments
- ⚠️ Rotate keys if exposed

---

## 📞 Quick Help

**Q: Where do I get SUPABASE_URL?**  
A: https://app.supabase.com → Select project → Settings → API → Project URL

**Q: My photos aren't uploading?**  
A: Create storage bucket: Supabase Dashboard → Storage → New Bucket → Name: `photos` → Public

**Q: Can I use both file-based and Supabase?**  
A: Yes! Keep both versions:
- `app.py` → Supabase version
- `app_file_based.py` → File-based version

**Q: How do I rollback?**  
A: `cp app_file_based.py app.py` and restart

**Q: What if I forget .env.local?**  
A: App will fail silently. Check Flask logs for "SUPABASE_URL not set"

---

## 📊 Pricing

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **Supabase** | Included | Up to 500MB storage |
| **Vercel** | Included | Up to 5 deployments/month |
| **Flask** | Free | Open source |
| **Total** | **$0** | Production ready! |

---

## ✨ Key Benefits

✓ **Scalable** - PostgreSQL backend  
✓ **Real-time** - Live database sync  
✓ **Automatic** - Backups included  
✓ **Free** - Generous free tier  
✓ **Global** - CDN for photos  
✓ **Secure** - Encryption at rest/transit  
✓ **Easy** - SQL editor for queries  

---

## 🎓 Learning Resources

- **Supabase Docs:** https://supabase.com/docs
- **Flask Guide:** https://flask.palletsprojects.com/
- **Vercel Deploy:** https://vercel.com/docs
- **PostgreSQL Basics:** https://www.postgresql.org/docs/

---

**Ready?** → Start with Quick Setup above or read SUPABASE_SETUP.md for details.

**Questions?** → Check the troubleshooting section in INTEGRATION.md

**Status:** ✅ Complete and Ready to Use

---

*Last updated: 2024 | Version 2.0*
