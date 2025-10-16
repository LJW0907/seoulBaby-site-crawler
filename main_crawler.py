# main_crawler.py

import json
from datetime import datetime
import boto3
import os

# --- 설정(Configuration) 영역 ---

# 앞으로 만들 크롤러 함수들을 여기서 import 합니다.
from crawlers.sample_parenting_crawler import crawl_seoul_parenting_programs

# from crawlers.another_crawler import crawl_another_site # 새로운 크롤러 추가 시 import

# [핵심] 실행할 크롤러 목록을 설정합니다.
# 새로운 크롤러를 추가하거나 비활성화할 때 이 리스트만 수정하면 됩니다.
CRAWLER_CONFIGS = [
    {
        "name": "서울시 육아종합지원센터",
        "crawler_func": crawl_seoul_parenting_programs,  # 실행할 함수
        "s3_key": "dynamic_programs/parenting_classes.json",  # S3에 저장될 파일 경로
        "enabled": True,  # 이 크롤러를 실행할지 여부
    },
    # {
    #     "name": "강남구청 육아 이벤트",
    #     "crawler_func": crawl_gangnam_events, # 나중에 만들 함수
    #     "s3_key": "dynamic_programs/gangnam_events.json",
    #     "enabled": True
    # }
]

# --- 로직(Logic) 영역 ---


def upload_to_s3(data, key):
    """주어진 데이터를 JSON 형태로 S3에 업로드합니다."""
    bucket_name = os.environ.get("S3_BUCKET_NAME", "seoul-baby")
    s3_client = boto3.client("s3")

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
    """설정에 정의된 모든 크롤러를 순차적으로 실행하고 결과를 S3에 업로드합니다."""
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
            # 설정에 명시된 크롤러 함수를 실행
            crawled_data = config["crawler_func"]()
            count = len(crawled_data)
            total_crawled_count += count

            print(f"✓ '{config['name']}' 크롤링 완료. 수집된 데이터: {count}개")
            summary[config["name"]] = {"status": "success", "count": count}

        except Exception as e:
            print(f"🔥 '{config['name']}' 크롤링 중 심각한 오류 발생: {e}")
            summary[config["name"]] = {"status": "failed", "error": str(e)}

        # 크롤링 결과(오류 발생 시 빈 데이터)를 S3에 업로드
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
    # 이 스크립트가 직접 실행될 때 main 함수를 호출
    # (로컬 테스트 및 GitHub Actions에서 실행하기 위함)
    main()
