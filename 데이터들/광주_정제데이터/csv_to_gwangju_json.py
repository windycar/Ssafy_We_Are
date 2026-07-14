"""전국 CCTV·경찰관서 CSV에서 광주광역시 데이터만 JSON으로 생성한다.

실행: python csv_to_gwangju_json.py
출력: cctv_gwangju.json, police_gwangju.json
"""

import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / "데이터셋"
CCTV_CSV = DATASET_DIR / "CCTV정보.csv"
POLICE_CSV = DATASET_DIR / "경찰청_전국 지구대 파출소 주소 현황_20251231.csv"

# 광주광역시 행정구역을 포함하는 좌표 범위
GWANGJU_BOUNDS = {"min_lat": 35.0, "max_lat": 35.3, "min_lng": 126.6, "max_lng": 127.1}


def is_gwangju_coordinate(lat: float, lng: float) -> bool:
    """좌표가 광주광역시 범위 안에 있는지 확인한다."""
    return (
        GWANGJU_BOUNDS["min_lat"] <= lat <= GWANGJU_BOUNDS["max_lat"]
        and GWANGJU_BOUNDS["min_lng"] <= lng <= GWANGJU_BOUNDS["max_lng"]
    )


def read_cctv() -> list[dict]:
    """광주광역시 관리 CCTV를 id, lat, lng 형태로 정제한다."""
    result = []
    with CCTV_CSV.open("r", encoding="cp949", newline="") as file:
        for index, row in enumerate(csv.DictReader(file), start=1):
            if "광주광역시" not in (row.get("관리기관명") or ""):
                continue

            try:
                lat = float(row["WGS84위도"])
                lng = float(row["WGS84경도"])
            except (KeyError, TypeError, ValueError):
                continue

            # 관리기관은 광주이나 좌표가 다른 지역인 오류 데이터를 제외한다.
            if not is_gwangju_coordinate(lat, lng):
                continue

            result.append({"id": str(row.get("관리번호") or f"cctv-{index}"), "lat": lat, "lng": lng})
    return result


def read_police() -> list[dict]:
    """광주청 관할 지구대·파출소를 관서 정보 형태로 정제한다."""
    result = []
    with POLICE_CSV.open("r", encoding="cp949", newline="") as file:
        for index, row in enumerate(csv.DictReader(file), start=1):
            if row.get("시도청") != "광주청":
                continue

            result.append(
                {
                    "id": f"police-{index}",
                    "name": f"{row.get('관서명', '')}{row.get('구분', '')}",
                    "district": row.get("경찰서", ""),
                    "type": row.get("구분", ""),
                    "address": row.get("주소", ""),
                }
            )
    return result


def save_json(filename: str, data: list[dict]) -> None:
    """한글이 유지되는 UTF-8 JSON 파일로 저장한다."""
    with (BASE_DIR / filename).open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def main() -> None:
    cctv = read_cctv()
    police = read_police()
    save_json("cctv_gwangju.json", cctv)
    save_json("police_gwangju.json", police)
    print(f"완료: CCTV {len(cctv)}건, 경찰관서 {len(police)}건")


if __name__ == "__main__":
    main()
