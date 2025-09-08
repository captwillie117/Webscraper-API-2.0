# Webscraper API 2.0

Flask-based API for scraping emails, phone numbers, and social media links.

## Deploy on Render

1. Upload repo to GitHub
2. Create new Web Service on Render
3. Add env vars:
   - `API_KEY`
   - `LOGTAIL_SOURCE_TOKEN` (optional)
   - `CORS_ORIGIN` (optional)
4. Deploy 🎉

## Example Usage

```bash
curl -H "x-api-key: your-secret-key" "https://<your-app>.onrender.com/scrape?url=https://example.com"
```
