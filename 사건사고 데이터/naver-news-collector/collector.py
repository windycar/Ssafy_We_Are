print("실행 파일:", __file__)

import hashlib
import html
import json
import os
import re
import time

from datetime import datetime
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


# =========================================================
# 1. 환경변수 및 네이버 API 설정
# =========================================================

load_dotenv()

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError(
        ".env 파일의 NAVER_CLIENT_ID와 "
        "NAVER_CLIENT_SECRET을 확인해주세요."
    )


API_URL = "https://openapi.naver.com/v1/search/news.json"

HEADERS = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET,
}


# =========================================================
# 2. 검색 대상 설정
# =========================================================

DISTRICTS = [
    "광주 동구",
    "광주 서구",
    "광주 남구",
    "광주 북구",
    "광주 광산구",
]

SEARCH_KEYWORDS = [
    "절도",
    "강도",
    "폭행",
    "상해",
    "살인",
    "살인미수",
    "스토킹",
    "교제폭력",
    "데이트폭력",
    "성범죄",
    "주거침입",
    "보이스피싱",
    "마약",
    "흉기",
    "실종",
]


# =========================================================
# 3. 범죄 유형 분류 규칙
# =========================================================

CRIME_RULES = {
    "절도": [
        "절도",
        "훔친",
        "훔쳐",
        "도난",
        "차량털이",
        "빈집털이",
        "소매치기",
    ],
    "강도": [
        "강도",
        "금품을 빼앗",
    ],
    "폭력": [
        "폭행",
        "상해",
        "난동",
        "집단폭행",
    ],
    "살인·살인미수": [
        "살인",
        "살해",
        "살인미수",
        "흉기로 찔러",
    ],
    "스토킹·교제폭력": [
        "스토킹",
        "교제폭력",
        "데이트폭력",
        "접근금지",
    ],
    "성범죄": [
        "성범죄",
        "성폭행",
        "성추행",
        "강제추행",
        "불법촬영",
        "몰카",
    ],
    "주거침입": [
        "주거침입",
        "무단침입",
        "침입",
    ],
    "보이스피싱": [
        "보이스피싱",
        "전화금융사기",
        "피싱",
    ],
    "마약": [
        "마약",
        "필로폰",
        "대마",
    ],
    "흉기": [
        "흉기",
        "칼부림",
    ],
    "실종": [
        "실종",
        "행방불명",
    ],
}


DISTRICT_RULES = {
    "동구": [
        "광주 동구",
        "광주광역시 동구",
    ],
    "서구": [
        "광주 서구",
        "광주광역시 서구",
    ],
    "남구": [
        "광주 남구",
        "광주광역시 남구",
    ],
    "북구": [
        "광주 북구",
        "광주광역시 북구",
    ],
    "광산구": [
        "광주 광산구",
        "광주광역시 광산구",
    ],
}


PLACE_TYPE_RULES = {
    "아파트": ["아파트", "공동주택"],
    "주택": ["주택", "빌라", "원룸"],
    "편의점": ["편의점"],
    "상가": ["상가", "점포", "매장"],
    "주차장": ["주차장"],
    "공원": ["공원"],
    "학교": [
        "학교",
        "초등학교",
        "중학교",
        "고등학교",
        "대학교",
    ],
    "도로": [
        "도로",
        "교차로",
        "횡단보도",
    ],
    "술집": [
        "술집",
        "주점",
        "유흥주점",
    ],
    "숙박시설": [
        "모텔",
        "호텔",
        "숙박업소",
    ],
    "대중교통": [
        "지하철역",
        "버스정류장",
        "기차역",
    ],
}


# =========================================================
# 4. 텍스트 정리 및 분류 함수
# =========================================================

def clean_text(text: str) -> str:
    """HTML 태그와 특수문자를 제거합니다."""

    cleaned = html.unescape(text or "")
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def normalize_title(title: str) -> str:
    """
    중복 판별을 위해 제목을 단순화합니다.
    특수문자와 불필요한 표현을 제거합니다.
    """

    normalized = clean_text(title).lower()

    removable_words = [
        "속보",
        "종합",
        "단독",
        "영상",
        "포토",
        "현장",
    ]

    for word in removable_words:
        normalized = normalized.replace(word, "")

    normalized = re.sub(
        r"\s*[-–—|]\s*[가-힣a-zA-Z0-9\s]+$",
        "",
        normalized,
    )

    normalized = re.sub(
        r"[^가-힣a-z0-9]",
        "",
        normalized,
    )

    return normalized


def classify_crime(text: str) -> str:
    """기사 제목과 요약에서 범죄 유형을 분류합니다."""

    for crime_type, keywords in CRIME_RULES.items():
        if any(keyword in text for keyword in keywords):
            return crime_type

    return "기타 사건·사고"


def classify_district(
    text: str,
    search_district: str,
) -> str:
    """기사 내용에서 광주 자치구를 분류합니다."""

    for district, keywords in DISTRICT_RULES.items():
        if any(keyword in text for keyword in keywords):
            return district

    return search_district.replace("광주 ", "")


def classify_place_type(text: str) -> str:
    """기사 내용에서 장소 유형을 분류합니다."""

    for place_type, keywords in PLACE_TYPE_RULES.items():
        if any(keyword in text for keyword in keywords):
            return place_type

    return "장소 미상"


def extract_neighborhood(text: str) -> str:
    """기사 제목과 요약에서 ○○동 표현을 추출합니다."""

    matches = re.findall(
        r"[가-힣]{2,8}동",
        text,
    )

    excluded_words = {
        "작동",
        "행동",
        "운동",
        "노동",
        "아동",
        "활동",
        "공동",
        "자동",
    }

    for match in matches:
        if match not in excluded_words:
            return match

    return ""


def normalize_published_date(
    pub_date: str,
) -> str:
    """네이버 날짜 형식을 YYYY-MM-DD로 변환합니다."""

    try:
        parsed = parsedate_to_datetime(pub_date)
        return parsed.strftime("%Y-%m-%d")

    except (TypeError, ValueError):
        return ""


def create_article_id(
    url: str,
    title: str,
) -> str:
    """URL 또는 제목으로 기사 고유 ID를 생성합니다."""

    raw_value = url or normalize_title(title)

    digest = hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()[:12]

    return f"GJ-{digest}"


# =========================================================
# 5. 광주 관련 여부 확인
# =========================================================

def is_relevant_to_gwangju(text: str) -> bool:
    """
    경기도 광주시 등 다른 지역의 기사가 섞이는 것을 줄입니다.
    """

    gwangju_keywords = [
        "광주광역시",
        "광주 동구",
        "광주 서구",
        "광주 남구",
        "광주 북구",
        "광주 광산구",
        "광주경찰청",
        "광주 경찰",
    ]

    return any(
        keyword in text
        for keyword in gwangju_keywords
    )


# =========================================================
# 6. 네이버 뉴스 API 호출
# =========================================================

def search_news(
    query: str,
    display: int = 30,
    start: int = 1,
) -> list[dict]:
    """네이버 뉴스 검색 API를 호출합니다."""

    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": "date",
    }

    response = requests.get(
        API_URL,
        headers=HEADERS,
        params=params,
        timeout=15,
    )

    if response.status_code != 200:
        print(
            f"[API 오류] {query} / "
            f"상태 코드: {response.status_code}"
        )
        print(response.text)

        return []

    return response.json().get("items", [])


# =========================================================
# 7. 기사 데이터 변환
# =========================================================

def normalize_article(
    item: dict,
    search_district: str,
    search_keyword: str,
) -> dict | None:
    """네이버 API 기사 한 건을 프로젝트 형식으로 변환합니다."""

    title = clean_text(
        item.get("title", "")
    )

    summary = clean_text(
        item.get("description", "")
    )

    original_url = item.get(
        "originallink",
        "",
    ).strip()

    naver_url = item.get(
        "link",
        "",
    ).strip()

    article_url = original_url or naver_url
    combined_text = f"{title} {summary}"

    if not title:
        return None

    if not is_relevant_to_gwangju(combined_text):
        return None

    district = classify_district(
        combined_text,
        search_district,
    )

    neighborhood = extract_neighborhood(
        combined_text
    )

    crime_type = classify_crime(
        combined_text
    )

    place_type = classify_place_type(
        combined_text
    )

    published_at = item.get(
        "pubDate",
        "",
    )

    location_parts = [
        "광주광역시",
        district,
    ]

    if neighborhood:
        location_parts.append(neighborhood)

    return {
        "id": create_article_id(
            article_url,
            title,
        ),
        "title": title,
        "normalizedTitle": normalize_title(title),
        "summary": summary,
        "crimeType": crime_type,
        "district": district,
        "neighborhood": neighborhood,
        "placeType": place_type,
        "locationText": " ".join(location_parts),
        "locationPrecision": (
            "neighborhood"
            if neighborhood
            else "district"
        ),
        "publishedAt": published_at,
        "publishedDate": normalize_published_date(
            published_at
        ),
        "sourceKeyword": search_keyword,
        "searchDistrict": search_district,
        "originalUrl": original_url,
        "naverUrl": naver_url,
        "collectedAt": datetime.now().isoformat(
            timespec="seconds"
        ),
    }


# =========================================================
# 8. 같은 실행 안에서 기사 수집
# =========================================================

def collect_all_articles() -> list[dict]:
    """광주 5개 구와 범죄 키워드를 조합해 검색합니다."""

    collected_by_id: dict[str, dict] = {}

    total_queries = (
        len(DISTRICTS)
        * len(SEARCH_KEYWORDS)
    )

    current_query = 0

    for district in DISTRICTS:
        for keyword in SEARCH_KEYWORDS:
            current_query += 1

            query = f"{district} {keyword}"

            print(
                f"[{current_query}/{total_queries}] "
                f"수집 중: {query}"
            )

            try:
                items = search_news(
                    query=query,
                    display=30,
                )

            except requests.RequestException as error:
                print(
                    f"[네트워크 오류] "
                    f"{query}: {error}"
                )
                continue

            for item in items:
                article = normalize_article(
                    item=item,
                    search_district=district,
                    search_keyword=keyword,
                )

                if article is None:
                    continue

                article_id = article["id"]

                if article_id not in collected_by_id:
                    collected_by_id[article_id] = article

            time.sleep(0.15)

    return list(
        collected_by_id.values()
    )


# =========================================================
# 9. 기존 JSON 파일 불러오기
# =========================================================

def load_existing_articles(
    file_path: Path,
) -> list[dict]:
    """기존 저장 기사를 읽어옵니다."""

    if not file_path.exists():
        return []

    try:
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        print(
            "[주의] 기존 JSON 파일이 "
            "리스트 형식이 아닙니다."
        )

        return []

    except (
        json.JSONDecodeError,
        OSError,
    ) as error:
        print(
            f"[주의] 기존 JSON 읽기 실패: {error}"
        )

        return []


# =========================================================
# 10. 중복 기사 판별
# =========================================================

def calculate_similarity(
    first_title: str,
    second_title: str,
) -> float:
    """두 기사 제목의 유사도를 계산합니다."""

    return SequenceMatcher(
        None,
        normalize_title(first_title),
        normalize_title(second_title),
    ).ratio()


def is_duplicate_article(
    new_article: dict,
    existing_article: dict,
) -> bool:
    """두 기사가 중복인지 판단합니다."""

    new_original_url = new_article.get(
        "originalUrl",
        "",
    )

    existing_original_url = existing_article.get(
        "originalUrl",
        "",
    )

    if (
        new_original_url
        and existing_original_url
        and new_original_url == existing_original_url
    ):
        return True

    new_naver_url = new_article.get(
        "naverUrl",
        "",
    )

    existing_naver_url = existing_article.get(
        "naverUrl",
        "",
    )

    if (
        new_naver_url
        and existing_naver_url
        and new_naver_url == existing_naver_url
    ):
        return True

    new_title = normalize_title(
        new_article.get("title", "")
    )

    existing_title = normalize_title(
        existing_article.get("title", "")
    )

    if (
        new_title
        and existing_title
        and new_title == existing_title
    ):
        return True

    same_date = (
        new_article.get("publishedDate")
        == existing_article.get("publishedDate")
    )

    same_district = (
        new_article.get("district")
        == existing_article.get("district")
    )

    same_crime_type = (
        new_article.get("crimeType")
        == existing_article.get("crimeType")
    )

    similarity = calculate_similarity(
        new_article.get("title", ""),
        existing_article.get("title", ""),
    )

    if (
        same_date
        and same_district
        and same_crime_type
        and similarity >= 0.82
    ):
        return True

    return False


# =========================================================
# 11. 기존 기사와 새 기사 병합
# =========================================================

def merge_articles(
    existing_articles: list[dict],
    new_articles: list[dict],
) -> tuple[list[dict], int]:
    """기존 데이터에 중복이 아닌 새 기사만 추가합니다."""

    merged = list(existing_articles)
    added_count = 0

    for new_article in new_articles:
        duplicated = any(
            is_duplicate_article(
                new_article,
                existing_article,
            )
            for existing_article in merged
        )

        if duplicated:
            continue

        merged.append(new_article)
        added_count += 1

    return merged, added_count


# =========================================================
# 12. 날짜 정렬
# =========================================================

def get_sort_datetime(
    article: dict,
) -> datetime:
    """기사 날짜를 정렬 가능한 값으로 변환합니다."""

    pub_date = article.get(
        "publishedAt",
        "",
    )

    try:
        parsed = parsedate_to_datetime(pub_date)

        # timezone 정보 제거
        return parsed.replace(
            tzinfo=None
        )

    except (
        TypeError,
        ValueError,
    ):
        return datetime.min


# =========================================================
# 13. JSON 파일 저장
# =========================================================

def save_articles(
    new_articles: list[dict],
) -> None:
    """기존 파일을 유지하면서 새 기사만 추가 저장합니다."""

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    article_path = (
        output_dir
        / "gwangju_crime_news.json"
    )

    existing_articles = load_existing_articles(
        article_path
    )

    print()
    print(
        f"기존 저장 기사: "
        f"{len(existing_articles)}건"
    )

    merged_articles, added_count = merge_articles(
        existing_articles,
        new_articles,
    )

    merged_articles.sort(
        key=get_sort_datetime,
        reverse=True,
    )

    with article_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            merged_articles,
            file,
            ensure_ascii=False,
            indent=2,
        )

    summary_data = {
        "updatedAt": datetime.now().isoformat(
            timespec="seconds"
        ),
        "previousCount": len(existing_articles),
        "newCollectedCount": len(new_articles),
        "newAddedCount": added_count,
        "duplicateCount": (
            len(new_articles) - added_count
        ),
        "totalCount": len(merged_articles),
        "districtCounts": {},
        "crimeTypeCounts": {},
    }

    for article in merged_articles:
        district = article.get(
            "district",
            "지역 미상",
        )

        crime_type = article.get(
            "crimeType",
            "기타 사건·사고",
        )

        summary_data["districtCounts"][district] = (
            summary_data["districtCounts"].get(
                district,
                0,
            )
            + 1
        )

        summary_data["crimeTypeCounts"][crime_type] = (
            summary_data["crimeTypeCounts"].get(
                crime_type,
                0,
            )
            + 1
        )

    summary_path = (
        output_dir
        / "gwangju_crime_news_summary.json"
    )

    with summary_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 55)
    print(
        f"이번 검색 결과: "
        f"{len(new_articles)}건"
    )
    print(
        f"중복 제외: "
        f"{len(new_articles) - added_count}건"
    )
    print(
        f"새로 추가: {added_count}건"
    )
    print(
        f"누적 저장: "
        f"{len(merged_articles)}건"
    )
    print(f"기사 파일: {article_path}")
    print(f"요약 파일: {summary_path}")
    print("=" * 55)


# =========================================================
# 14. 프로그램 실행
# =========================================================

def main() -> None:
    print(
        "광주 사건·사고 기사 수집을 시작합니다."
    )
    print()

    articles = collect_all_articles()

    if not articles:
        print(
            "이번 검색에서 수집된 기사가 없습니다."
        )
        return

    save_articles(articles)


if __name__ == "__main__":
    main()