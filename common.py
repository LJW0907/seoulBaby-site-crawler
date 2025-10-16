# crawlers/common.py

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_chrome_driver():
    """
    실행 환경(로컬/GitHub Actions)에 맞춰 headless Chrome WebDriver를 생성하고 반환합니다.
    이 함수 덕분에 각 크롤러는 드라이버 설정에 신경 쓸 필요가 없습니다.
    """
    options = Options()
    options.add_argument("--headless")  # UI 없이 백그라운드에서 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # GITHUB_ACTIONS 환경 변수가 true이면 GitHub Actions 환경으로 간주
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("INFO: Running in GitHub Actions environment.")
        driver = webdriver.Chrome(options=options)
    else:
        print("INFO: Running in local environment.")
        from webdriver_manager.chrome import ChromeDriverManager

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    return driver
