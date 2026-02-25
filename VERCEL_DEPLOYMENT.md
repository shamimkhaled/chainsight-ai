# Deploying ChainSight AI Backend to Vercel

This guide covers deploying the Django REST API to Vercel.

## Prerequisites

- Vercel account
- Supabase PostgreSQL database (pooler connection recommended)
- All environment variables configured in Vercel

## Quick Deploy

1. **Connect your repo** to Vercel (GitHub, GitLab, or Bitbucket).

2. **Set environment variables** in Vercel Project → Settings → Environment Variables:

   | Variable | Required | Description |
   |----------|----------|-------------|
   | `SECRET_KEY` | Yes | Django secret key |
   | `DJANGO_SETTINGS_MODULE` | Yes | `config.settings.vercel` |
   | `DB_ENGINE` | Yes | `django.db.backends.postgresql` |
   | `DB_NAME` | Yes | Supabase: `postgres` |
   | `DB_USER` | Yes | Supabase: `postgres.<project-ref>` |
   | `DB_PASSWORD` | Yes | Your Supabase password |
   | `DB_HOST` | Yes | Supabase pooler: `aws-1-us-east-1.pooler.supabase.com` |
   | `DB_PORT` | Yes | `6543` (pooler) |
   | `ALLOWED_HOSTS` | No | Comma-separated, e.g. `.vercel.app,your-domain.com` |
   | `OPENAI_API_KEY` | Yes* | For AI features |
   | `REDIS_URL` | No | Not used on Vercel (in-memory cache) |
   | `CORS_ALLOWED_ORIGINS` | No | Comma-separated frontend URLs |

3. **Deploy**:
   ```bash
   npm i -g vercel
   vercel login
   vercel --prod
   ```

   Or push to your connected Git branch for automatic deploys.

## Project Structure for Vercel

- `api/wsgi.py` - Vercel entry point (exposes `app`)
- `config/settings/vercel.py` - Serverless-optimized settings
- `vercel.json` - Routing and build config

## Limitations

| Feature | Vercel | Notes |
|---------|--------|-------|
| Celery | ❌ | Background tasks won't run. Use external worker (Railway, Render) or offload to frontend |
| Redis | ❌ | Uses in-memory cache per function instance |
| WebSockets | ❌ | Not supported |
| File uploads | ⚠️ | `/tmp` only; use S3 for persistent storage |
| Request timeout | 10s (Hobby) / 60s (Pro) | Long-running requests may fail |
| Bundle size | ~250MB | Heavy deps (WeasyPrint, pytesseract) may need trimming |

## Run Migrations Manually

If the build migration fails (e.g. network), run locally:

```bash
export DJANGO_SETTINGS_MODULE=config.settings.vercel
python manage.py migrate --noinput
```

Ensure your local `.env` has the same Supabase credentials as Vercel.

## Troubleshooting

- **502 Bad Gateway**: Check Vercel function logs; often DB connection or import errors
- **Static files 404**: Ensure `buildCommand` runs `collectstatic`; WhiteNoise serves from `staticfiles/`
- **Database connection refused**: Use Supabase **pooler** URL (port 6543), not direct (5432)
- **Module not found**: Some packages may not work on Vercel's Python runtime; consider `vercel-requirements.txt` with fewer deps
