# =============================================================================
# [Spotfire 14.0 Data Function] Iris 데이터셋 행 수 계산
# =============================================================================
# 설정 방법 (Spotfire Analyst 14.0):
#
#  [Step 1] 스크립트 등록 — Tools → Register Data Functions
#   1. Tools → Register Data Functions → [New] 클릭
#   2. Name: IrisRowCount
#   3. Script Engine: Python 3.x
#   4. 아래 코드를 Script 영역에 붙여넣기
#   5. [Input Parameters] → Add:
#      - Name: iris_data  /  Type: Table
#   6. [Output Parameters] → Add:
#      - Name: result_table  /  Type: Table
#   7. [OK] 저장
#
#  [Step 2] 파라미터 매핑 — Data → Data Function Properties
#   1. Data → Data Function Properties → IrisRowCount 선택
#   2. Input  iris_data   → Iris 데이터 테이블 선택
#   3. Output result_table → "New table" 선택, 이름: Iris_Summary
#   4. [OK] → 함수 자동 실행되어 Iris_Summary 테이블 생성됨
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
