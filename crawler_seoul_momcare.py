# seoulBaby-site-crawler/crawler_seoul_momcare.py

import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from common import get_chrome_driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def crawl_seoul_momcare_notices():
    """
    서울 맘케어 시스템 (seoulmomcare.com)의 공지사항을 크롤링합니다.
    JavaScript 기반의 페이지 이동과 상세 페이지 링크를 처리합니다.
    """
    driver = get_chrome_driver()
    base_url = "https://www.seoulmomcare.com"
    list_url = f"{base_url}/notice/userNoticeList.do"
    notices = []

    try:
        driver.get(list_url)
        page_num = 1

        while True:
            print(f"INFO: Scraping Seoul Mom Care page {page_num}")
            time.sleep(random.uniform(2.5, 4.5))
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # tbody의 tr 중에서 goDetail 클래스를 가진 것만 선택
            rows = soup.select("tbody#listAppend > tr.goDetail")
            if not rows and page_num > 1:
                print("INFO: No more notice rows found on this page.")
                break

            for row in rows:
                notice = {}
                cells = row.select("td")
                if len(cells) < 3:
                    continue

                notice["post_id"] = cells[0].text.strip()
                notice["title"] = cells[1].text.strip()
                notice["date"] = cells[
                    3
                ].text.strip()  # 모바일용 td를 건너뛰고 4번째 td

                # [핵심] 숨겨진 input에서 상세 페이지 ID(nttId) 추출
                hidden_input = row.find_next_sibling("input", {"type": "hidden"})
                if hidden_input and hidden_input.get("value"):
                    ntt_id = hidden_input.get("value")
                    notice["details_url"] = (
                        f"{base_url}/notice/userNoticeView.do?nttId={ntt_id}"
                    )

                notices.append(notice)

            # [핵심] JavaScript 기반 페이지 이동 처리
            try:
                # 다음 페이지 번호(예: 2, 3, ...)에 해당하는 링크를 찾음
                next_page_link = driver.find_element(
                    By.CSS_SELECTOR, f"a.pg_page[link='{page_num + 1}']"
                )
                print(f"INFO: Clicking next page link for page {page_num + 1}")
                driver.execute_script("arguments[0].click();", next_page_link)
                page_num += 1
            except NoSuchElementException:
                # 더 이상 다음 페이지 링크가 없으면 루프 종료
                print("INFO: Reached the last page of Seoul Mom Care.")
                break

        # 상세 페이지 방문하여 본문 내용 수집
        for i, notice in enumerate(notices):
            if "details_url" in notice:
                print(
                    f"INFO: Scraping details for Mom Care notice {i+1}/{len(notices)}: {notice['title']}"
                )
                driver.get(notice["details_url"])
                time.sleep(1)

                detail_soup = BeautifulSoup(driver.page_source, "html.parser")
                content_area = detail_soup.select_one(".view_content")
                if content_area:
                    notice["content"] = content_area.get_text(
                        separator="\n", strip=True
                    )
            notice["crawled_at"] = datetime.now().isoformat()

    except Exception as e:
        print(f"ERROR during crawling seoulmomcare.com: {e}")
    finally:
        driver.quit()

    print(f"INFO: Successfully crawled {len(notices)} notices from seoulmomcare.com.")
    return notices
