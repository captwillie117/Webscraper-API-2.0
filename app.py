from flask import Flask, request, jsonify, abort
import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import os

# Try importing Logtail safely
try:
    from logtail import LogtailHandler
except ImportError:
    LogtailHandler = None

app = Flask(__name__)

# Enable CORS
CORS(app, origins=[os.getenv("CORS_ORIGIN", "*")])

# 🔐 API Keys
API_KEY = os.getenv("API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# 🚫 Rate Limiting (Flask-Limiter v3.x syntax)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)
limiter.init_app(app)

# 📋 Logging Setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Console logs
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Logtail logs (only if available)
logtail_token = os.getenv("LOGTAIL_SOURCE_TOKEN")
if logtail_token and LogtailHandler:
    logtail_handler = LogtailHandler(source_token=logtail_token)
    logger.addHandler(logtail_handler)

# Regex patterns
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"\+?\d[\d\-\(\) ]{7,}\d"

SOCIALS = {
    'facebook': r"(https?:\/\/(www\.)?facebook\.com\/[^\s\"\'<>]*)",
    'twitter': r"(https?:\/\/(www\.)?(twitter|x)\.com\/[^\s\"\'<>]*)",
    'instagram': r"(https?:\/\/(www\.)?instagram\.com\/[^\s\"\'<>]*)",
}

def save_to_file(data, url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '_')
    data_dir = os.getenv("DATA_DIR", ".")
    os.makedirs(data_dir, exist_ok=True)
    filename = os.path.join(data_dir, f"scrape_results_{domain}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return filename

def extract_data_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()

    emails = re.findall(EMAIL_REGEX, text)
    phones = [re.sub(r'\s+', '', p) for p in re.findall(PHONE_REGEX, text)]

    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if href.startswith('mailto:'):
            emails.append(href.replace('mailto:', ''))
        elif href.startswith('tel:'):
            phones.append(href.replace('tel:', ''))

    socials = {}
    for name, pattern in SOCIALS.items():
        links = re.findall(pattern, html, re.IGNORECASE)
        socials[name] = list(set([match[0] for match in links]))

    return {
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "socials": socials
    }

def get_internal_links(base_url, html, max_links=5):
    soup = BeautifulSoup(html, 'html.parser')
    base_domain = urlparse(base_url).netloc
    links = set()

    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.netloc == base_domain and full_url.startswith(base_url):
            links.add(full_url)
        if len(links) >= max_links:
            break

    return list(links)

def check_api_key():
    key = request.headers.get("x-api-key")
    if API_KEY and key == API_KEY:
        return
    if RAPIDAPI_KEY and key == RAPIDAPI_KEY:
        return
    logger.warning(f"Unauthorized access attempt from IP {request.remote_addr}")
    abort(401, description="Invalid or missing API key")

@app.route('/scrape', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def scrape():
    check_api_key()

    if request.method == 'GET':
        url = request.args.get("url")
    else:
        data = request.get_json(silent=True)
        url = data.get("url") if data else None

    if not url:
        logger.error("No URL provided")
        return jsonify({"error": "URL is required"}), 400

    logger.info(f"Received scrape request from {request.remote_addr} for {url}")

    try:
        visited = set()
        to_visit = [url]
        all_emails = set()
        all_phones = set()
        all_socials = {k: set() for k in SOCIALS}

        while to_visit:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue

            visited.add(current_url)
            try:
                resp = requests.get(current_url, timeout=10)
                resp.raise_for_status()
                data = extract_data_from_html(resp.text)

                all_emails.update(data["emails"])
                all_phones.update(data["phones"])
                for k in all_socials:
                    all_socials[k].update(data["socials"].get(k, []))

                if current_url == url:
                    to_visit.extend(get_internal_links(url, resp.text))

            except requests.RequestException as e:
                logger.warning(f"Failed to fetch {current_url}: {e}")
                continue

        result = {
            "url": url,
            "emails": list(all_emails),
            "phone_numbers": list(all_phones),
            "socials": {k: list(v) for k, v in all_socials.items()}
        }

        filename = save_to_file(result, url)
        result["saved_to_file"] = filename

        logger.info(f"Scrape completed for {url}")
        return jsonify(result)

    except Exception as e:
        logger.exception("Unhandled exception during scraping")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
