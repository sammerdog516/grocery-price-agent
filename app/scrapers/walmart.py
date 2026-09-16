from urllib.parse import quote_plus
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path(".playwright/walmart-profile")


def fetch_walmart_search_page(query: str) -> str:
    encoded_query = quote_plus(query)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=False,
        )

        page = context.pages[0] if context.pages else  context.new_page()

        page.goto(
            f"https://www.walmart.ca/en/search?q={encoded_query}",
            wait_until="domcontentloaded",
            timeout=30000,
        )

        print("Complete any Walmart verification if it appears")

        try:
            page.wait_for_selector(
                "script#__NEXT_DATA__",
                timeout=120000,
            )
        except:
            print("Timed out waiting for Walmart search page.")
            print("Final URL:", page.url)
            print("Title", page.title())
            context.close()

        html = page.content()
        context.close()

        return html

import json
from bs4 import BeautifulSoup


def extract_next_data(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    script = soup.find("script", id="__NEXT_DATA__")

    if script is None or script.string is None:
        raise ValueError("__NEXT_DATA__ not found")

    return json.loads(script.string)


def find_product_dicts(obj) -> list[dict]:
    products = []

    if isinstance(obj, dict):
        if (
            "priceInfo" in obj
            and "name" in obj
            and ("usItemId" in obj or "canonicalUrl" in obj)
        ):
            products.append(obj)

        for value in obj.values():
            products.extend(find_product_dicts(value))

    elif isinstance(obj, list):
        for item in obj:
            products.extend(find_product_dicts(item))

    return products

def find_paths_to_products(obj, path="root"):
    if isinstance(obj, dict):
        if (
            "priceInfo" in obj
            and "name" in obj
            and ("usItemId" in obj or "canonicalUrl" in obj)
        ):
            print(path)
        
        for key, value in obj.items():
            find_paths_to_products(value, f"{path}.{key}")
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_paths_to_products(item, f"{path}[{i}]")