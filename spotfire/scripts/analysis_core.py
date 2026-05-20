# -*- coding: utf-8 -*-
"""
분석 코어 스크립트 (Python 2)
==============================
[실행 방법]
  표준 입력(stdin)으로 JSON 데이터를 받아 분석 후 JSON을 표준 출력(stdout)으로 반환.

[입력 JSON 스키마]
  {
    "selected_x"  : "선택된 단지명",
    "a_data"      : [ {컬럼명: 값, ...}, ... ],  # A테이블 필터링 결과
    "b_data"      : [ {컬럼명: 값, ...}, ... ]   # B테이블 관련 데이터
  }

[출력 JSON 스키마]
  {
    "columns" : ["컬럼1", "컬럼2", ...],
    "data"    : [ {"컬럼1": 값, ...}, ... ]
  }
"""

import sys
import json
import math
reload(sys)
sys.setdefaultencoding('utf-8')


# ─────────────────────────────────────────────
# 유틸리티
# ─────────────────────────────────────────────

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ─────────────────────────────────────────────
# 분석 함수
# ─────────────────────────────────────────────

def analyze(selected_x, a_data, b_data):
    """
    A테이블과 B테이블을 apt_id 기준으로 조인한 뒤 단지별 통계를 산출.

    커스터마이징 포인트:
      - JOIN_KEY: 두 테이블을 연결하는 키 컬럼명
      - 아래 compute_row() 함수에 원하는 계산 로직 추가
    """
    JOIN_KEY = "apt_id"

    # B 데이터를 키 기준으로 인덱싱
    b_index = {}
    for row in b_data:
        key = row.get(JOIN_KEY, "")
        b_index[key] = row

    # ── 행별 계산 ──────────────────────────────
    def compute_row(a_row, b_row):
        price     = safe_float(a_row.get("price_만원"))
        area      = safe_float(a_row.get("area"))
        floor     = safe_int(a_row.get("floor"))
        rooms     = safe_int(a_row.get("rooms"))
        maint     = safe_float(b_row.get("maintenance_fee_만원"))
        score     = safe_float(b_row.get("management_score"))
        year      = safe_int(b_row.get("year_built"))
        parking   = safe_float(b_row.get("parking_ratio"))
        amenity   = safe_int(b_row.get("amenity_count"))
        green     = safe_float(b_row.get("green_ratio_pct"))

        price_per_m2 = round(price / area, 1) if area > 0 else 0.0
        age          = 2026 - year if year > 0 else 0

        # 종합 점수 (0~100 스케일 임의 가중치)
        score_total = round(
            score * 0.40
            + min(parking / 2.0, 1.0) * 15.0
            + min(amenity / 15.0, 1.0) * 15.0
            + min(green / 40.0, 1.0) * 15.0
            + max(0, (20 - age) / 20.0) * 15.0,
            2
        )

        return {
            u"단지명"         : a_row.get("apartment_complex", ""),
            u"apt_id"        : a_row.get(JOIN_KEY, ""),
            u"면적(m2)"      : area,
            u"층"            : floor,
            u"방수"          : rooms,
            u"매매가(만원)"   : price,
            u"m2당가격(만원)" : price_per_m2,
            u"관리비(만원)"   : maint,
            u"관리점수"       : score,
            u"준공연도"       : year,
            u"건물나이(년)"   : age,
            u"주차비율"       : parking,
            u"편의시설수"     : amenity,
            u"녹지율(%)"     : green,
            u"종합점수"       : score_total,
        }

    result_rows = []
    for a_row in a_data:
        key   = a_row.get(JOIN_KEY, "")
        b_row = b_index.get(key, {})
        result_rows.append(compute_row(a_row, b_row))

    # ── 요약 통계 행 추가 ──────────────────────
    if result_rows:
        num_cols = [u"면적(m2)", u"매매가(만원)", u"m2당가격(만원)",
                    u"관리비(만원)", u"관리점수", u"종합점수"]

        def avg(col):
            vals = [r[col] for r in result_rows if isinstance(r[col], (int, float))]
            return round(sum(vals) / len(vals), 2) if vals else 0.0

        summary = {k: u"" for k in result_rows[0].keys()}
        summary[u"단지명"]       = u"[평균]"
        summary[u"apt_id"]      = u"-"
        for col in num_cols:
            summary[col] = avg(col)
        result_rows.append(summary)

    columns = [
        u"단지명", u"apt_id", u"면적(m2)", u"층", u"방수",
        u"매매가(만원)", u"m2당가격(만원)", u"관리비(만원)",
        u"관리점수", u"준공연도", u"건물나이(년)", u"주차비율",
        u"편의시설수", u"녹지율(%)", u"종합점수",
    ]

    return {"columns": columns, "data": result_rows}


# ─────────────────────────────────────────────
# 진입점
# ─────────────────────────────────────────────

if __name__ == "__main__":
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)

        result = analyze(
            payload.get("selected_x", ""),
            payload.get("a_data", []),
            payload.get("b_data", []),
        )

        sys.stdout.write(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        sys.stderr.write(u"[analysis_core ERROR] " + unicode(e) + u"\n")
        sys.exit(1)
