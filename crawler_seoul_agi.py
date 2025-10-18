# seoulBaby-site-crawler/crawler_seoul_agi.py

import time
from datetime import datetime
from bs4 import BeautifulSoup
from common import get_chrome_driver  # import 경로 수정


def crawl_seoul_agi_education():
    """
    서울 임신/출산 정보센터 (seoul-agi.seoul.go.kr)의 보건소 교육 정보를 크롤링합니다.
    [최적화] '신청마감', '접수완료' 등 이미 종료된 항목은 수집에서 제외합니다.
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
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            card_items = soup.select("div.card-item")
            if not card_items:
                print("INFO: No more items found. Finishing crawl.")
                break

            for card in card_items:
                program = {}

                # --- [최적화 1단계] 상태(status) 먼저 확인하기 ---
                status_tag = card.select_one(".item-button span, .item-button a")
                status = status_tag.text.strip() if status_tag else ""

                # 제외할 상태 목록 정의
                statuses_to_exclude = ["신청마감", "접수완료", "접수마감"]

                # 상태가 제외 목록에 포함되면, 이 항목은 건너뛰고 다음 항목으로 넘어감
                if status in statuses_to_exclude:
                    title_for_log = (
                        card.select_one(".item-name a").text.strip()
                        if card.select_one(".item-name a")
                        else "N/A"
                    )
                    print(
                        f"INFO: Skipping item '{title_for_log}' with status '{status}'."
                    )
                    continue  # --- 이 continue가 핵심입니다 ---

                # --- [최적화 2단계] 수집할 가치가 있는 항목만 나머지 정보 수집 ---
                program["status"] = status

                labels = card.select(".item-label .label")
                program["district"] = labels[0].text.strip() if labels else ""
                program["categories"] = [label.text.strip() for label in labels[1:]]

                name_tag = card.select_one(".item-name a")
                if name_tag:
                    program["title"] = name_tag.text.strip()
                    detail_path = name_tag.get("href")
                    if detail_path:
                        program["details_url"] = f"{base_url}{detail_path}"

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

                programs.append(program)

            paging = soup.select_one(".paging")
            if paging and not paging.find("a", title=f"{current_page + 1} 페이지"):
                print("INFO: Reached the last page.")
                break

            current_page += 1

        for i, program in enumerate(programs):
            if "details_url" in program:
                print(
                    f"INFO: Scraping details for item {i+1}/{len(programs)}: {program['title']}"
                )
                driver.get(program["details_url"])
                time.sleep(1)
                detail_soup = BeautifulSoup(driver.page_source, "html.parser")
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
        f"INFO: Successfully crawled {len(programs)} ACTIVE programs from seoul-agi.seoul.go.kr."
    )
    return programs
