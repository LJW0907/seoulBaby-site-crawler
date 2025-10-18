# seoulBaby-site-crawler/common.py

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_chrome_driver():
    """
    실행 환경(로컬/GitHub Actions)에 맞춰 headless Chrome WebDriver를 생성하고 반환합니다.
    """
    options = Options()

    # --- [핵심 수정] 로봇 탐지를 우회하기 위한 옵션 추가 ---
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # ----------------------------------------------------

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
    # options.add_experimental_option('excludeSwitches', ['enable-logging']) # 이 줄은 위와 중복될 수 있으므로 주석 처리하거나 삭제합니다.

    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("INFO: Running in GitHub Actions environment with anti-detection.")
        driver = webdriver.Chrome(options=options)
    else:
        print("INFO: Running in local environment with anti-detection.")
        from webdriver_manager.chrome import ChromeDriverManager

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    return driver
