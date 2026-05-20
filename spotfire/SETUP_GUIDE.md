# Spotfire 템플릿 설정 가이드

## 전체 흐름

```
[CSV 로드] → [릴레이션 설정] → [Document Property] → [리스트 박스]
                                                            ↓
                                              [분석 버튼 클릭]
                                                            ↓
                                  IronPython → analysis_core.py (Python 2)
                                                            ↓
                                              [결과 테이블 시각화]
```

---

## Step 1. 데이터 로드

1. **File > Add Data Tables** 선택
2. **A테이블** 추가
   - `sample_data/table_a.csv` 선택
   - 테이블 이름을 **`A테이블`** 로 지정
3. **B테이블** 추가 (같은 방법)
   - `sample_data/table_b.csv` 선택
   - 테이블 이름을 **`B테이블`** 로 지정

---

## Step 2. 테이블 간 릴레이션 설정

1. **Edit > Data Table Properties** 선택
2. **Relations** 탭 클릭 → **Add** 버튼
3. 아래와 같이 설정:

   | 항목 | 값 |
   |---|---|
   | Left table | A테이블 |
   | Left column | `apt_id` |
   | Right table | B테이블 |
   | Right column | `apt_id` |

4. **OK** 저장

---

## Step 3. Document Property 생성 (리스트 박스 값 저장소)

1. **Edit > Document Properties** 선택
2. **New** 클릭 후:

   | 항목 | 값 |
   |---|---|
   | Name | `SelectedXValue` |
   | Type | `String` |
   | Default | *(비워 둠)* |

3. 같은 방식으로 상태 메시지용 속성 추가:

   | Name | Type |
   |---|---|
   | `StatusMessage` | `String` |

---

## Step 4. 리스트 박스 컨트롤 생성

1. 텍스트 영역(Text Area) 시각화를 추가하고 **Edit HTML** 모드로 전환
2. 또는 **Insert > Property Control > List Box** 선택
3. 리스트 박스 설정:

   | 항목 | 값 |
   |---|---|
   | Property | `SelectedXValue` |
   | Data table | `A테이블` |
   | Column | `apartment_complex` (x컬럼) |
   | Display unique values | ✅ |

   > 리스트 박스를 선택하면 `Document.Properties["SelectedXValue"]` 에  
   > 선택된 단지명이 자동으로 기록됩니다.

---

## Step 5. 분석 스크립트 파일 배치

```
C:\spotfire_scripts\
    analysis_core.py        ← 이 저장소의 scripts/analysis_core.py
```

> **경로 변경 시** `button_analysis.py` 상단 설정 영역의  
> `ANALYSIS_SCRIPT` 와 `PYTHON_EXE` 를 수정하세요.

### Python 2 환경 확인

```bash
C:\Python27\python.exe --version
# Python 2.7.x
```

> subprocess 사용이 불가한 환경(샌드박스)이라면  
> `button_analysis_inline.py` 를 대신 사용하세요 (exec 방식).

---

## Step 6. 분석 버튼 생성 및 스크립트 연결

1. **Insert > Action Control > Button** 선택
2. 버튼 이름: **`분석`**
3. **Script** 탭 → **New** 클릭
4. `scripts/button_analysis.py` 내용을 전체 복사하여 붙여넣기
5. 스크립트 저장 후 버튼에 연결

### 버튼 스크립트 주요 설정값 확인

```python
TABLE_A_NAME    = "A테이블"
TABLE_B_NAME    = "B테이블"
X_COLUMN        = "apartment_complex"   # 리스트 박스 대상 컬럼
JOIN_KEY        = "apt_id"              # 릴레이션 키 컬럼
PROPERTY_NAME   = "SelectedXValue"      # Step 3 에서 만든 Property
PYTHON_EXE      = r"C:\Python27\python.exe"
ANALYSIS_SCRIPT = r"C:\spotfire_scripts\analysis_core.py"
```

---

## Step 7. 결과 테이블 시각화 추가

1. 분석 버튼을 한 번 클릭하여 **`분석결과`** DataTable 생성
2. **Insert > Visualization > Table** 선택
3. Data table: **`분석결과`** 선택
4. 표시할 컬럼 확인 (기본 전체 표시)

> 버튼을 클릭할 때마다 결과 테이블이 갱신됩니다.

### 상태 메시지 표시 (선택)

Text Area 에 다음 HTML 삽입:

```html
<SpotfireControl id="StatusControl"
  type="Property"
  propertyname="StatusMessage"
  displayname="상태" />
```

---

## 데이터 구조 요약

### A테이블 (`table_a.csv`)

| 컬럼 | 설명 |
|---|---|
| `apt_id` | 고유 ID (B테이블 조인 키) |
| `apartment_complex` | **리스트 박스 사용 컬럼 (x컬럼)** |
| `area` | 전용면적 (m²) |
| `floor` | 층수 |
| `rooms` | 방수 |
| `price_만원` | 매매가 |

### B테이블 (`table_b.csv`)

| 컬럼 | 설명 |
|---|---|
| `apt_id` | 조인 키 |
| `maintenance_fee_만원` | 관리비 |
| `management_score` | 관리 점수 |
| `year_built` | 준공연도 |
| `parking_ratio` | 주차 비율 |
| `amenity_count` | 편의시설 수 |
| `green_ratio_pct` | 녹지율 (%) |

---

## 분석 로직 커스터마이징

`analysis_core.py` 의 `compute_row()` 함수를 수정하세요.

```python
def compute_row(a_row, b_row):
    # a_row: A테이블 행 딕셔너리
    # b_row: B테이블 매칭 행 딕셔너리
    # 반환: 결과 행 딕셔너리 (원하는 컬럼 자유 추가)
    ...
```

- `a_data` / `b_data` 변수로 전체 리스트도 참조 가능
- 외부 라이브러리(numpy, pandas 등) 사용 시 `PYTHON_EXE` 환경에 설치 필요

---

## 파일 구조

```
spotfire/
├── scripts/
│   ├── button_analysis.py          # 분석 버튼 스크립트 (subprocess 방식)
│   ├── button_analysis_inline.py   # 분석 버튼 스크립트 (exec 방식, subprocess 불가 시)
│   └── analysis_core.py            # Python 2 분석 로직 (커스터마이징 대상)
├── sample_data/
│   ├── table_a.csv
│   └── table_b.csv
└── SETUP_GUIDE.md
```

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `KeyError: 'A테이블'` | 테이블 이름 불일치 | Spotfire 테이블 이름 ↔ 스크립트 `TABLE_A_NAME` 확인 |
| `분석 스크립트 오류` | Python 2 미설치 또는 경로 오류 | `PYTHON_EXE` 경로 확인, `button_analysis_inline.py` 사용 검토 |
| 결과 테이블 빈칸 | JSON 파싱 오류 | `analysis_core.py` 를 직접 실행하여 stdout 확인 |
| 리스트 박스 값 미반영 | Property 이름 불일치 | `PROPERTY_NAME` ↔ Document Property 이름 확인 |
