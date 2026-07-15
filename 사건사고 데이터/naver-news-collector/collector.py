import hashlib
import html
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError(".env 파일의 네이버 API 키를 확인해주세요.")


API_URL = "https://openapi.naver.com/v1/search/news.json"

HEADERS = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET,
}


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
        "동구",
    ],
    "서구": [
        "광주 서구",
        "서구",
    ],
    "남구": [
        "광주 남구",
        "남구",
    ],
    "북구": [
        "광주 북구",
        "북구",
    ],
    "광산구": [
        "광주 광산구",
        "광산구",
    ],
}


PLACE_TYPE_RULES = {
    "아파트": ["아파트", "공동주택"],
    "주택": ["주택", "빌라", "원룸"],
    "편의점": ["편의점"],
    "상가": ["상가", "점포", "매장"],
    "주차장": ["주차장"],
    "공원": ["공원"],
    "학교": ["학교", "초등학교", "중학교", "고등학교", "대학교"],
    "도로": ["도로", "교차로", "횡단보도"],
    "술집": ["술집", "주점", "유흥주점"],
    "숙박시설": ["모텔", "호텔", "숙박업소"],
    "대중교통": ["지하철역", "버스정류장", "역"],
}


def clean_text(text: str) -> str:
    """HTML 태그와 특수문자를 제거합니다."""
    cleaned = html.unescape(text or "")
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def classify_crime(text: str) -> str:
    """제목과 설명에서 범죄 유형을 분류합니다."""
    for crime_type, keywords in CRIME_RULES.items():
        if any(keyword in text for keyword in keywords):
            return crime_type

    return "기타 사건·사고"


def classify_district(text: str, search_district: str) -> str:
    """기사 내용에서 광주 자치구를 분류합니다."""
    for district, keywords in DISTRICT_RULES.items():
        if any(keyword in text for keyword in keywords):
            return district

    return search_district.replace("광주 ", "")


def classify_place_type(text: str) -> str:
    """기사 내용에 등장하는 장소 유형을 분류합니다."""
    for place_type, keywords in PLACE_TYPE_RULES.items():
        if any(keyword in text for keyword in keywords):
            return place_type

    return "장소 미상"


def extract_neighborhood(text: str) -> str:
    """
    광주 기사에서 '용봉동', '치평동' 같은 동 이름을 단순 추출합니다.
    정확한 행정동 검증은 하지 않는 목업용 방식입니다.
    """
    matches = re.findall(r"[가-힣]{2,8}동", text)

    excluded_words = {
        "작동",
        "행동",
        "운동",
        "노동",
        "아동",
        "중동",
    }

    for match in matches:
        if match not in excluded_words:
            return match

    return ""


def create_article_id(url: str, title: str) -> str:
    """링크 또는 제목을 기준으로 고유 ID를 생성합니다."""
    raw_value = url or title
    digest = hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()[:12]

    return f"GJ-{digest}"


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
            f"[오류] {query} / "
            f"상태 코드: {response.status_code}"
        )
        print(response.text)
        return []

    return response.json().get("items", [])


def is_relevant_to_gwangju(text: str) -> bool:
    """
    다른 지역의 '광주' 기사 유입을 줄입니다.
    광주광역시 또는 광주 5개 구 표현이 있는 기사만 통과시킵니다.
    """
    keywords = [
        "광주광역시",
        "광주 동구",
        "광주 서구",
        "광주 남구",
        "광주 북구",
        "광주 광산구",
        "광주경찰",
        "광주 경찰",
    ]

    return any(keyword in text for keyword in keywords)


def normalize_article(
    item: dict,
    search_district: str,
    search_keyword: str,
) -> dict | None:
    """API 응답 기사 한 건을 프로젝트용 구조로 변환합니다."""
    title = clean_text(item.get("title", ""))
    summary = clean_text(item.get("description", ""))

    original_url = item.get("originallink", "").strip()
    naver_url = item.get("link", "").strip()
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

    neighborhood = extract_neighborhood(combined_text)
    place_type = classify_place_type(combined_text)
    crime_type = classify_crime(combined_text)

    location_text_parts = ["광주광역시", district]

    if neighborhood:
        location_text_parts.append(neighborhood)

    location_text = " ".join(location_text_parts)

    return {
        "id": create_article_id(
            article_url,
            title,
        ),
        "title": title,
        "summary": summary,
        "crimeType": crime_type,
        "district": district,
        "neighborhood": neighborhood,
        "placeType": place_type,
        "locationText": location_text,
        "locationPrecision": (
            "neighborhood"
            if neighborhood
            else "district"
        ),
        "publishedAt": item.get("pubDate", ""),
        "sourceKeyword": search_keyword,
        "searchDistrict": search_district,
        "originalUrl": original_url,
        "naverUrl": naver_url,
        "collectedAt": datetime.now().isoformat(
            timespec="seconds"
        ),
    }


def collect_all_articles() -> list[dict]:
    """광주 5개 구와 범죄 키워드를 조합해 기사를 수집합니다."""
    collected_by_id: dict[str, dict] = {}

    total_queries = len(DISTRICTS) * len(SEARCH_KEYWORDS)
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
                    f"[네트워크 오류] {query}: {error}"
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

                # 같은 링크나 제목의 중복 기사 제거
                if article_id not in collected_by_id:
                    collected_by_id[article_id] = article

            # 짧은 간격을 두어 요청
            time.sleep(0.15)

    return list(collected_by_id.values())


def save_articles(articles: list[dict]) -> None:
    """기사 데이터를 JSON으로 저장합니다."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    articles.sort(
        key=lambda article: article["publishedAt"],
        reverse=True,
    )

    article_path = (
        output_dir
        / "gwangju_crime_news.json"
    )

    with article_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            articles,
            file,
            ensure_ascii=False,
            indent=2,
        )

    summary_data = {
        "collectedAt": datetime.now().isoformat(
            timespec="seconds"
        ),
        "totalCount": len(articles),
        "districtCounts": {},
        "crimeTypeCounts": {},
    }

    for article in articles:
        district = article["district"]
        crime_type = article["crimeType"]

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
    print("=" * 50)
    print(f"수집 완료: {len(articles)}건")
    print(f"기사 파일: {article_path}")
    print(f"요약 파일: {summary_path}")
    print("=" * 50)


def main() -> None:
    print("광주 사건·사고 기사 수집을 시작합니다.")
    print()

    articles = collect_all_articles()

    if not articles:
        print("수집된 기사가 없습니다.")
        return

    save_articles(articles)


if __name__ == "__main__":
    main()