# =============================================================================
# [Spotfire 14.0 Data Function] Iris 데이터셋 행 수 계산
# =============================================================================
# 설정 방법 (Spotfire Analyst 14.0):
#   1. 메뉴 → Insert → Data Function → New Data Function
#   2. Name: IrisRowCount
#   3. Script Engine: Python 3.x  ← 14.0에서의 표기 (Python 3 선택)
#   4. [Input Parameters] Add Parameter
#      - Name: iris_data
#      - Type: Table
#      - Display name (선택): Iris Dataset
#   5. [Output Parameters] Add Parameter
#      - Name: result_table
#      - Type: Table
#   6. 아래 코드를 Script 영역에 붙여넣기 → OK
#   7. 상단 메뉴 → Data → Data Function Properties 에서 매핑 확인:
#      - iris_data  : Iris 테이블 선택
#      - result_table: "Create new table" 선택 후 이름 지정 (예: Iris_Summary)
# =============================================================================
# 참고 (Spotfire 14.0 Python 타입 매핑):
#   pandas dtype int64   → Spotfire Integer
#   pandas dtype float64 → Spotfire Real
#   pandas dtype object  → Spotfire String
# =============================================================================

import pandas as pd
from datetime import datetime

# iris_data : Spotfire가 자동 주입하는 pandas DataFrame (Iris 테이블 전체)
row_count  = int(len(iris_data))           # int64 → Spotfire Integer
col_count  = int(len(iris_data.columns))   # int64 → Spotfire Integer
col_names  = ", ".join(str(c) for c in iris_data.columns)

# result_table : Spotfire가 새 테이블로 저장할 출력 DataFrame
result_table = pd.DataFrame({
    "Dataset":       pd.array(["Iris"],                                  dtype="object"),
    "Row_Count":     pd.array([row_count],                               dtype="int64"),
    "Column_Count":  pd.array([col_count],                               dtype="int64"),
    "Columns":       pd.array([col_names],                               dtype="object"),
    "Calculated_At": pd.array([datetime.now().strftime("%Y-%m-%d %H:%M:%S")], dtype="object"),
})
