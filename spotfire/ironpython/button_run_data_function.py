# =============================================================================
# [Spotfire 14.0 IronPython] 버튼 액션 – 팝업 사이에서 Data Function 실행
# =============================================================================
# 설정 방법 (Spotfire Analyst 14.0):
#   버튼 추가:
#     1. 메뉴 → Insert → Text Area
#     2. 텍스트 영역 우클릭 → Edit Text Area
#     3. 상단 도구모음 → Insert Action Control → Button
#     4. 버튼 우클릭 → Properties → [Actions 탭] → Add → Script
#     5. Script Language: IronPython
#     6. 아래 코드를 붙여넣기 → OK
#
#   사전 조건:
#     - iris_row_count.py 의 Data Function이 이미 등록되어 있어야 함
#     - DATA_FUNCTION_NAME 을 등록된 Data Function 이름과 동일하게 설정
#
# 주의 (Spotfire 14.0):
#   - DataFunctionExecutorService 는 Spotfire.Dxp.Data.DataFunctions 네임스페이스
#   - Application.GetService[T]() 제네릭 패턴 사용 (IronPython 2.7 문법)
#   - Document.Data.DataFunctions 로 등록된 Data Function 목록 조회
# =============================================================================

import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import (
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult
)

# ── 설정: 등록된 Data Function 이름 ──────────────────────────────────────────
DATA_FUNCTION_NAME = "IrisRowCount"

# ── 시작 팝업 ────────────────────────────────────────────────────────────────
start_result = MessageBox.Show(
    "Iris 데이터셋 분석을 시작합니다.\n\n"
    "데이터의 행 수를 계산하여 새 테이블에 저장합니다.\n\n"
    "계속하려면 [확인]을 클릭하세요.",
    "분석 시작",
    MessageBoxButtons.OKCancel,
    MessageBoxIcon.Information
)

# ── 취소 처리 ────────────────────────────────────────────────────────────────
if start_result == DialogResult.Cancel:
    MessageBox.Show(
        "분석이 취소되었습니다.",
        "취소",
        MessageBoxButtons.OK,
        MessageBoxIcon.Warning
    )

# ── Data Function 실행 (확인 클릭 시) ────────────────────────────────────────
else:
    executed  = False
    error_msg = ""

    try:
        # Spotfire 14.0: DataFunctionExecutorService import를 실행 시점에 수행
        # (모듈 로드 실패 시 try 블록 안에서 처리하기 위함)
        from Spotfire.Dxp.Data.DataFunctions import DataFunctionExecutorService

        executor = Application.GetService[DataFunctionExecutorService]()

        for data_function in Document.Data.DataFunctions:
            if data_function.Name == DATA_FUNCTION_NAME:
                executor.ExecuteDataFunction(data_function)
                executed = True
                break

        if not executed:
            error_msg = (
                "Data Function '{0}'을(를) 찾을 수 없습니다.\n\n"
                "확인 사항:\n"
                "  1. Insert → Data Function 에서 함수가 등록되어 있는지 확인\n"
                "  2. DATA_FUNCTION_NAME 변수 값이 등록명과 일치하는지 확인"
            ).format(DATA_FUNCTION_NAME)

    except Exception as e:
        error_msg = (
            "Data Function 실행 중 오류가 발생했습니다.\n\n{0}"
        ).format(str(e))

    # ── 결과 팝업 ─────────────────────────────────────────────────────────────
    if error_msg:
        MessageBox.Show(
            error_msg,
            "오류",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error
        )
    else:
        MessageBox.Show(
            "분석이 완료되었습니다.\n\n"
            "Iris 데이터셋의 행 수가 계산되어\n"
            "새 테이블(Iris_Summary)에 저장되었습니다.",
            "분석 완료",
            MessageBoxButtons.OK,
            MessageBoxIcon.Information
        )
