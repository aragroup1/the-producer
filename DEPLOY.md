# Deploy to Railway

## 1. Create GitHub Repo (if not exists)
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/the-producer.git
git push -u origin main
```

## 2. Railway Setup
1. Go to https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Choose your `the-producer` repo
4. Railway auto-detects `nixpacks.toml`

## 3. Add Environment Variables
In Railway Dashboard → Variables:
```
DATABASE_URL=                  # Railway Postgres (auto-provisioned)
REDIS_URL=                     # Railway Redis (auto-provisioned)
SECRET_KEY=your-secret-key
ENVIRONMENT=production
YOUTUBE_API_KEY=               # Get from Google Cloud Console
```

## 4. Services Railway Will Create
| Service | Type | Purpose |
|---------|------|---------|
| Web | API Gateway | FastAPI on port $PORT |
| Worker | Celery | Background task processing |
| Beat | Celery Beat | Scheduled tasks (hourly scans) |
| Postgres | Database | Beat storage, analytics |
| Redis | Cache/Queue | Celery broker |

## 5. Cost
- ~$5-10/month for basic tier
- Scales automatically if traffic grows

## 6. Dashboard Access
Frontend deploys separately as static site (Vercel/Netlify) or run locally:
```bash
cd frontend/admin-dashboard
npm run dev
# Set NEXT_PUBLIC_API_URL to your Railway URL
```
