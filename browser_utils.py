import time
from urllib.parse import urlparse, parse_qs

def clean_domain(url):
    return urlparse(str(url)).netloc.replace("www.", "").strip()

def extract_real_url(href):
    if href and href.startswith("/url?"):
        parsed = urlparse(href)
        return parse_qs(parsed.query).get("q", [""])[0]
    return href

def safe_goto(page, url, retries=2):
    for i in range(retries + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            return True
        except Exception as e:
            if i < retries:
                print(f"     Connection issue, retrying in 10s... ({i+1}/{retries})")
                time.sleep(10)
            else:
                return False

def create_browser(p):
    browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled", "--start-maximized"])
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="en-IN",
        geolocation={"latitude": 28.5355, "longitude": 77.3910},
        permissions=["geolocation"],
        viewport=None
    )
    return browser, context.new_page()