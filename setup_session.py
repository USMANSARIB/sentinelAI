from playwright.sync_api import sync_playwright
import time
import config
import os

def setup_login_session():
    print("🔐 Launching Browser for Manual Login...")
    print("   1. A browser window will open.")
    print("   2. Log in to X (Twitter) manually.")
    print("   3. Solve any CAPTCHAs if they appear.")
    print("   4. Once you are on the home timeline, simply CLOSE the browser window.")
    
    # Ensure session dir exists
    if not os.path.exists(config.SESSION_DIR):
        os.makedirs(config.SESSION_DIR)

    with sync_playwright() as p:
        # Launch with images ENABLED and NO blocking
        context = p.chromium.launch_persistent_context(
            user_data_dir=config.SESSION_DIR,
            headless=False,
            viewport={'width': 1280, 'height': 800},
            args=["--disable-blink-features=AutomationControlled", "--disable-infobars"]
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        print("🌍 Going to login page...")
        page.goto("https://x.com/login")
        
        print("⏳ Waiting for login success (checking multiple indicators)...")
        max_retries = 60 # 5 minutes (5s sleep * 60)
        logged_in = False

        for i in range(max_retries):
            try:
                # Check for Home Link OR New Tweet Button OR Account Menu
                if page.query_selector("a[href='/home']") or \
                   page.query_selector("div[data-testid='SideNav_NewTweet_Button']") or \
                   page.query_selector("div[data-testid='SideNav_AccountSwitcher_Button']"):
                    print("[OK] Login indicators found!")
                    logged_in = True
                    break
            except:
                pass
            
            if i % 5 == 0:
                 print(f"   ... waiting for you to login ({i*5}s elapsed)")
            time.sleep(5)

        if logged_in:
            print("[OK] saving session cookies...")
            time.sleep(3)
        else:
            print("[WARN] Timed out waiting for login detection.")

        print("[OK] Session data saved to:", config.SESSION_DIR)
        context.close()

if __name__ == "__main__":
    setup_login_session()
