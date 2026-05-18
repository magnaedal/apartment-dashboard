# =============================================================================
# [Spotfire Data Function] Iris 데이터셋 행 수 계산
# =============================================================================
# 설정 방법:
#   1. Spotfire → Insert → Data Function → New
#   2. Script Engine: Python 3
#   3. [Parameters 탭]
#      - Input  파라미터 추가: 이름 = iris_data,   Type = Table
#      - Output 파라미터 추가: 이름 = result_table, Type = Table
#   4. 아래 코드를 Script 영역에 붙여넣기
#   5. Input 파라미터 iris_data → Iris 데이터 테이블 매핑
#   6. Output 파라미터 result_table → "새 테이블 생성" 선택
# =============================================================================

import pandas as pd
from datetime import datetime

# iris_data: Spotfire가 주입하는 입력 DataFrame (Iris 테이블 전체)
row_count = len(iris_data)
col_count = len(iris_data.columns)
col_names = ", ".join(iris_data.columns.tolist())

# 결과 테이블 생성 (새 테이블로 저장됨)
result_table = pd.DataFrame({
    "Dataset":       ["Iris"],
    "Row_Count":     [row_count],
    "Column_Count":  [col_count],
    "Columns":       [col_names],
    "Calculated_At": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
})
