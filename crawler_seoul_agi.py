# seoulBaby_crawlers/crawlers/crawler_seoul_agi.py

import time
from datetime import datetime
from bs4 import BeautifulSoup
from common import get_chrome_driver


def crawl_seoul_agi_education():
    """
    서울 임신/출산 정보센터 (seoul-agi.seoul.go.kr)의 보건소 교육 정보를 크롤링합니다.
    목록 페이지와 상세 페이지를 모두 크롤링하여 종합적인 정보를 수집합니다.
    """
    driver = get_chrome_driver()
    base_url = "https://seoul-agi.seoul.go.kr"
    programs = []

    try:
        current_page = 1
        while True:
            list_url = f"{base_url}/health-center-education?curPage={current_page}"
            print(f"INFO: Scraping page {current_page}: {list_url}")
            driver.get(list_url)
            time.sleep(2)  # 페이지 로딩을 위한 대기 시간

            soup = BeautifulSoup(driver.page_source, "html.parser")

            # --- 1. 목록 페이지에서 기본 정보와 상세 링크 수집 ---
            card_items = soup.select("div.card-item")

            # 현재 페이지에 더 이상 게시물이 없으면 루프 종료
            if not card_items:
                print("INFO: No more items found. Finishing crawl.")
                break

            for card in card_items:
                program = {}

                # 자치구, 분류
                labels = card.select(".item-label .label")
                program["district"] = labels[0].text.strip() if labels else ""
                program["categories"] = [label.text.strip() for label in labels[1:]]

                # 제목, 상세보기 링크
                name_tag = card.select_one(".item-name a")
                if name_tag:
                    program["title"] = name_tag.text.strip()
                    detail_path = name_tag.get("href")
                    if detail_path:
                        program["details_url"] = f"{base_url}{detail_path}"

                # 기간 정보
                info_dls = card.select(".item-info dl")
                for dl in info_dls:
                    dt = dl.dt.text.strip()
                    dd = dl.dd.text.strip().replace("\n", "").replace("\t", "")
                    if "신청기간" in dt:
                        program["apply_period"] = dd
                    elif "교육기간" in dt:
                        program["education_period"] = dd
                    elif "신청/정원" in dt:
                        program["capacity"] = dd

                # 상태
                status_tag = card.select_one(".item-button span, .item-button a")
                program["status"] = status_tag.text.strip() if status_tag else ""

                programs.append(program)

            # 다음 페이지가 있는지 확인 (현재 페이지 번호가 paging 영역에 없으면 마지막 페이지)
            paging = soup.select_one(".paging")
            if paging and not paging.find("a", title=f"{current_page + 1} 페이지"):
                print("INFO: Reached the last page.")
                break

            current_page += 1

        # --- 2. 각 프로그램의 상세 페이지에 접속하여 추가 정보 수집 ---
        for i, program in enumerate(programs):
            if "details_url" in program:
                print(
                    f"INFO: Scraping details for item {i+1}/{len(programs)}: {program['title']}"
                )
                driver.get(program["details_url"])
                time.sleep(1)

                detail_soup = BeautifulSoup(driver.page_source, "html.parser")

                # 상세 정보 테이블에서 데이터 추출
                detail_table = detail_soup.select(".article-body .table dl")
                for dl in detail_table:
                    dt_text = dl.dt.text.strip()
                    dd_text = dl.dd.text.strip()

                    if "교육내용" in dt_text:
                        program["content"] = dd_text
                    elif "교육장소" in dt_text:
                        program["location"] = dd_text
                    elif "교육대상" in dt_text:
                        program["target_audience"] = dd_text
                    elif "준비물" in dt_text:
                        program["materials"] = dd_text
                    elif "문의처" in dt_text:
                        program["contact"] = dd_text

            program["crawled_at"] = datetime.now().isoformat()

    except Exception as e:
        print(f"ERROR during crawling seoul-agi.seoul.go.kr: {e}")
    finally:
        driver.quit()

    print(
        f"INFO: Successfully crawled {len(programs)} programs from seoul-agi.seoul.go.kr."
    )
    return programs
