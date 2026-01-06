import time
from config import MAX_ORG_PAGES, TARGET_DOMAIN, BUSINESS_NAME_SNIPPET
from browser_utils import clean_domain, extract_real_url, safe_goto

def get_organic_rank(page, keyword, target_url):
    target_domain = clean_domain(target_url)
    rank = 0
    for page_no in range(MAX_ORG_PAGES):
        url = f"https://www.google.com/search?q={keyword}&start={page_no * 10}"
        if not safe_goto(page, url): return "Network Error"
        if "sorry" in page.url: return "Captcha"
        try:
            page.wait_for_selector("a", timeout=10000)
        except: continue
        
        results = page.query_selector_all("div.g, div.MjjYud, div.tF2Cxc")
        for result in results:
            link = result.query_selector("a[href^='http']")
            if not link: continue
            href = link.get_attribute("href") or ""
            real_url = extract_real_url(href)
            if not real_url.startswith("http") or "google.com" in real_url: continue
            rank += 1
            if target_domain in clean_domain(real_url): return rank
    return "Not Found"

def get_local_pack_rank(page, keyword):
    search_url = f"https://www.google.com/search?q={keyword}"
    if not safe_goto(page, search_url): return "Network Error"
    time.sleep(1.5)
    try:
        initial_listings = page.query_selector_all("div.u3M9ce, div.VkpGBb, [data-lp]")
        for i, listing in enumerate(initial_listings[:3], start=1):
            if BUSINESS_NAME_SNIPPET.lower() in listing.inner_text().lower(): return i

        more_places_btn = page.locator("div[data-async-context] >> text=/More places|More businesses/i").first
        if not more_places_btn.is_visible():
            more_places_btn = page.locator("text=/More places/i").first

        if more_places_btn.is_visible():
            more_places_btn.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            for _ in range(3): 
                page.mouse.wheel(0, 1500)
                time.sleep(0.8)
            listings = page.locator("div[role='article'], .VkpGBb").all()
            for i, listing in enumerate(listings, start=1):
                if BUSINESS_NAME_SNIPPET.lower() in listing.inner_text().lower(): return i
    except Exception as e:
        print(f"     Local Pack Error: {e}")
    return "Not Found"