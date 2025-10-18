# seoulBaby-site-crawler/common.py

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth  # <-- selenium-stealth import


def get_chrome_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    # User-Agent 설정은 selenium-stealth가 더 잘 처리해주므로 주석 처리하거나 삭제 가능
    # options.add_argument("user-agent=...")

    # excludeSwitches 옵션도 selenium-stealth가 처리해줌
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("INFO: Running in GitHub Actions with selenium-stealth.")
        driver = webdriver.Chrome(options=options)
    else:
        print("INFO: Running in local environment with selenium-stealth.")
        from webdriver_manager.chrome import ChromeDriverManager

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    # --- [핵심] selenium-stealth를 드라이버에 적용 ---
    stealth(
        driver,
        languages=["ko-KR", "ko"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    # -----------------------------------------------

    return driver
