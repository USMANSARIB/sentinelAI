from playwright.sync_api import sync_playwright
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

def test_launch():
    print(f"Testing launch with SESSION_DIR: {config.SESSION_DIR}")
    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=config.SESSION_DIR,
                headless=True
            )
            print("Launch Successful!")
            page = context.new_page()
            page.goto("https://x.com")
            print(f"Title: {page.title()}")
            context.close()
        except Exception as e:
            print(f"Launch Failed: {e}")

if __name__ == "__main__":
    test_launch()
