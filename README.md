# Webscraper API 2.0

Flask-based API for scraping emails, phone numbers, and social media links from websites.

## Deploy on Render

1. Upload this repo to GitHub.
2. Create a new **Web Service** on Render.
3. Connect your GitHub repo.
4. Add environment variables:
   - `API_KEY`
   - `LOGTAIL_SOURCE_TOKEN` (optional)
   - `CORS_ORIGIN` (optional)
5. Deploy 🎉

## Example Usage

```bash
curl -H "x-api-key: your-secret-key" "https://<your-app>.onrender.com/scrape?url=https://example.com"
```

Response:

```json
{
  "url": "https://example.com",
  "emails": ["info@example.com"],
  "phone_numbers": ["+123456789"],
  "socials": {
    "facebook": ["https://facebook.com/example"],
    "twitter": [],
    "instagram": []
  },
  "saved_to_file": "scrape_results_example_com.json"
}
```
