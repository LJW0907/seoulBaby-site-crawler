# seoulBaby-site-crawler/crawler_seoul_agi_notice.py

import time
from datetime import datetime
from bs4 import BeautifulSoup
from common import get_chrome_driver  # import 경로 수정


def crawl_seoul_agi_notices():
    """
    서울 임신/출산 정보센터 (seoul-agi.seoul.go.kr)의 공지사항을 크롤링합니다.
    목록 페이지와 상세 페이지를 모두 방문하여 종합 정보를 수집합니다.
    """
    driver = get_chrome_driver()
    base_url = "https://seoul-agi.seoul.go.kr"
    notices = []

    try:
        current_page = 1
        while True:
            list_url = f"{base_url}/notice?curPage={current_page}"
            print(f"INFO: Scraping notice page {current_page}: {list_url}")
            driver.get(list_url)
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            # 목록에서 각 공지사항 아이템 수집
            list_items = soup.select("a.list-item")
            if not list_items:
                print("INFO: No more notice items found. Finishing crawl.")
                break

            for item in list_items:
                notice = {}

                # 게시물 번호
                notice["post_id"] = item.select_one(".item-number").text.strip()

                # 제목
                notice["title"] = item.select_one(".item-name").text.strip()

                # 상세보기 링크
                detail_path = item.get("href")
                if detail_path:
                    notice["details_url"] = f"{base_url}{detail_path}"

                # 등록일, 조회수
                info_tags = item.select(".item-info p")
                if len(info_tags) >= 2:
                    notice["date"] = info_tags[0].text.replace("등록일 :", "").strip()
                    notice["views"] = info_tags[1].text.replace("조회수 :", "").strip()

                notices.append(notice)

            # 다음 페이지 확인
            paging = soup.select_one(".paging")
            if paging and not paging.find("a", title=f"{current_page + 1} 페이지"):
                print("INFO: Reached the last page of notices.")
                break
            current_page += 1

        # 상세 페이지 방문하여 본문 내용 수집
        for i, notice in enumerate(notices):
            if "details_url" in notice:
                print(
                    f"INFO: Scraping details for notice {i+1}/{len(notices)}: {notice['title']}"
                )
                driver.get(notice["details_url"])
                time.sleep(1)

                detail_soup = BeautifulSoup(driver.page_source, "html.parser")

                # 본문 내용이 있는 영역 선택
                content_area = detail_soup.select_one(".article-body")
                if content_area:
                    # 줄바꿈을 유지하면서 텍스트 전체를 가져옴
                    notice["content"] = content_area.get_text(
                        separator="\n", strip=True
                    )

            notice["crawled_at"] = datetime.now().isoformat()

    except Exception as e:
        print(f"ERROR during crawling seoul-agi notices: {e}")
    finally:
        driver.quit()

    print(
        f"INFO: Successfully crawled {len(notices)} notices from seoul-agi.seoul.go.kr."
    )
    return notices
