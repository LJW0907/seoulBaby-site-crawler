# seoulBaby-site-crawler/crawler_childcare_go_kr.py

import time
from datetime import datetime
from bs4 import BeautifulSoup
from common import get_chrome_driver

# [핵심] 서울시 자치구 목록을 정의하여, 서울 관련 정보만 필터링합니다.
SEOUL_GU_LIST = [
    "강남구",
    "강동구",
    "강북구",
    "강서구",
    "관악구",
    "광진구",
    "구로구",
    "금천구",
    "노원구",
    "도봉구",
    "동대문구",
    "동작구",
    "마포구",
    "서대문구",
    "서초구",
    "성동구",
    "성북구",
    "송파구",
    "양천구",
    "영등포구",
    "용산구",
    "은평구",
    "종로구",
    "중구",
    "중랑구",
]


def crawl_childcare_support_fund():
    """
    아이사랑(childcare.go.kr)의 출산지원금 정보를 크롤링합니다.
    [최적화] 전국 정보 중 '서울시' 및 25개 자치구 관련 게시물만 필터링하여 수집합니다.
    """
    driver = get_chrome_driver()
    base_url = "https://www.childcare.go.kr"
    support_funds = []

    try:
        page_num = 1
        while True:
            list_url = f"{base_url}/?menuno=279&pageNo={page_num}"
            print(f"INFO: Scraping i-sarang page {page_num}: {list_url}")
            driver.get(list_url)
            time.sleep(3)  # F12 방지 사이트는 로딩이 느릴 수 있어 넉넉하게 대기

            soup = BeautifulSoup(driver.page_source, "html.parser")

            table_rows = soup.select("tbody > tr")
            if not table_rows:
                print("INFO: No more table rows found. Finishing crawl.")
                break

            for row in table_rows:
                cells = row.select("td")
                if len(cells) < 4:
                    continue

                title = cells[1].text.strip()

                # --- [핵심 필터링 로직] ---
                # 제목에 '서울' 또는 서울시 자치구 이름이 포함된 경우에만 수집
                is_seoul_data = "서울" in title or any(
                    gu in title for gu in SEOUL_GU_LIST
                )

                if not is_seoul_data:
                    # print(f"INFO: Skipping non-Seoul item: {title}")
                    continue
                # -------------------------

                post = {}
                post["number"] = cells[0].text.strip()
                post["title"] = title
                post["views"] = cells[2].text.strip()
                post["date"] = cells[3].text.strip()

                link_tag = cells[1].select_one("a")
                if link_tag and link_tag.get("href"):
                    # 자바스크립트 링크를 실제 URL로 변환
                    onclick_attr = link_tag.get("onclick", "")
                    post_id = "".join(filter(str.isdigit, onclick_attr))
                    if post_id:
                        post["details_url"] = (
                            f"{base_url}/?menuno=279&boardno={post_id}&pageNo={page_num}&brd_id=&search_key=&search_word=&cate_id="
                        )

                support_funds.append(post)

            # 다음 페이지 버튼이 비활성화되면 마지막 페이지로 간주
            next_button = soup.select_one("a.next_page")
            if next_button and "disabled" in next_button.get("class", []):
                print("INFO: Reached the last page of i-sarang.")
                break
            page_num += 1

        # 상세 페이지 방문
        for i, post in enumerate(support_funds):
            if "details_url" in post:
                print(
                    f"INFO: Scraping details for i-sarang post {i+1}/{len(support_funds)}: {post['title']}"
                )
                driver.get(post["details_url"])
                time.sleep(2)

                detail_soup = BeautifulSoup(driver.page_source, "html.parser")
                content_area = detail_soup.select_one(".board_view_cont")
                if content_area:
                    post["content"] = content_area.get_text(separator="\n", strip=True)

            post["crawled_at"] = datetime.now().isoformat()

    except Exception as e:
        print(f"ERROR during crawling childcare.go.kr: {e}")
    finally:
        driver.quit()

    print(
        f"INFO: Successfully crawled {len(support_funds)} SEOUL-related posts from childcare.go.kr."
    )
    return support_funds
