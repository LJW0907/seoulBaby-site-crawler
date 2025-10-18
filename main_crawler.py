# main_crawler.py

import json
from datetime import datetime
import boto3
import os

# --- 설정(Configuration) 영역 ---

from crawler_seoul_agi import crawl_seoul_agi_education
from crawler_seoul_agi_notice import crawl_seoul_agi_notices
from crawler_childcare_go_kr import crawl_childcare_support_fund

# [핵심] 3개의 크롤러를 모두 실행하도록 설정
CRAWLER_CONFIGS = [
    {
        "name": "서울 임신출산 정보센터 (보건소 교육)",
        "crawler_func": crawl_seoul_agi_education,
        "s3_key": "dynamic_programs/seoul_agi_education.json",
        "enabled": True,
    },
    {
        "name": "서울 임신출산 정보센터 (공지사항)",
        "crawler_func": crawl_seoul_agi_notices,
        "s3_key": "dynamic_programs/seoul_agi_notices.json",
        "enabled": True,
    },
    {
        "name": "아이사랑 (출산지원금-서울시)",
        "crawler_func": crawl_childcare_support_fund,
        "s3_key": "dynamic_programs/childcare_support_fund.json",
        "enabled": True,
    },
]

# --- 로직(Logic) 영역 (수정 불필요) ---


def upload_to_s3(data, key):
    # (이전과 동일한 코드)
    bucket_name = os.environ.get("S3_BUCKET_NAME", "seoul-baby")
    s3_client = boto3.client("s3", region_name="ap-northeast-2")
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(data, ensure_ascii=False, indent=4).encode("utf-8"),
            ContentType="application/json; charset=utf-8",
        )
        print(f"✅ S3 Upload Success: s3://{bucket_name}/{key}")
        return True
    except Exception as e:
        print(f"❌ S3 Upload Failed ({key}): {e}")
        return False


def main():
    # (이전과 동일한 코드)
    print("=" * 60)
    print("👶 서울시 임신/출산/육아 정보 통합 크롤링을 시작합니다.")
    print(f"   시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    summary = {}
    total_crawled_count = 0
    for config in CRAWLER_CONFIGS:
        if not config["enabled"]:
            print(f"\n⏩ Skipping '{config['name']}' (disabled).")
            continue
        print(f"\n🚀 [{config['name']}] 크롤링을 시작합니다...")
        crawled_data = []
        try:
            crawled_data = config["crawler_func"]()
            count = len(crawled_data)
            total_crawled_count += count
            print(f"✓ '{config['name']}' 크롤링 완료. 수집된 데이터: {count}개")
            summary[config["name"]] = {"status": "success", "count": count}
        except Exception as e:
            print(f"🔥 '{config['name']}' 크롤링 중 심각한 오류 발생: {e}")
            summary[config["name"]] = {"status": "failed", "error": str(e)}
        upload_data = {
            "source": config["name"],
            "data": crawled_data,
            "count": len(crawled_data),
            "updated_at": datetime.now().isoformat(),
        }
        upload_to_s3(upload_data, config["s3_key"])
    print("\n" + "=" * 60)
    print("✨ 크롤링 완료 요약")
    print("=" * 60)
    for name, result in summary.items():
        if result["status"] == "success":
            print(f"  ✅ {name}: {result['count']}개")
        else:
            print(f"  ❌ {name}: 실패 - {result['error']}")
    print(f"\n총 {total_crawled_count}개의 동적 데이터를 수집했습니다.")
    print(f"   완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
