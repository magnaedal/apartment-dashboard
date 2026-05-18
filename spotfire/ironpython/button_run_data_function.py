# =============================================================================
# [Spotfire IronPython] 버튼 액션 – 팝업 사이에서 Data Function 실행
# =============================================================================
# 설정 방법:
#   1. Spotfire → Insert → Button
#   2. 버튼 우클릭 → Edit Script
#   3. Script Language: IronPython
#   4. 아래 코드를 붙여넣기
#   5. DATA_FUNCTION_NAME 값을 실제 Data Function 이름으로 변경
# =============================================================================

from System.Windows.Forms import (
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult
)
from Spotfire.Dxp.Data.DataFunctions import DataFunctionExecutorService

# ── 설정: Data Function 이름 ──────────────────────────────────────────────────
DATA_FUNCTION_NAME = "IrisRowCount"   # Data Function 등록 시 사용한 이름

# ── 시작 팝업 ────────────────────────────────────────────────────────────────
start_result = MessageBox.Show(
    "Iris 데이터셋 분석을 시작합니다.\n\n"
    "데이터의 행 수를 계산하여 새 테이블에 저장합니다.\n\n"
    "계속하려면 [확인]을 클릭하세요.",
    "분석 시작",
    MessageBoxButtons.OKCancel,
    MessageBoxIcon.Information
)

if start_result == DialogResult.Cancel:
    MessageBox.Show(
        "분석이 취소되었습니다.",
        "취소",
        MessageBoxButtons.OK,
        MessageBoxIcon.Warning
    )
else:
    # ── Data Function 실행 ────────────────────────────────────────────────────
    executed = False
    error_msg = ""

    try:
        executor = Application.GetService[DataFunctionExecutorService]()

        for data_function in Document.Data.DataFunctions:
            if data_function.Name == DATA_FUNCTION_NAME:
                executor.ExecuteDataFunction(data_function)
                executed = True
                break

        if not executed:
            error_msg = (
                "Data Function '{0}'을(를) 찾을 수 없습니다.\n\n"
                "Spotfire에 Data Function이 등록되어 있는지 확인하세요."
            ).format(DATA_FUNCTION_NAME)

    except Exception as e:
        error_msg = "Data Function 실행 중 오류가 발생했습니다:\n\n{0}".format(str(e))

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
            "Iris 데이터셋의 행 수가 계산되어\n새 테이블에 저장되었습니다.",
            "분석 완료",
            MessageBoxButtons.OK,
            MessageBoxIcon.Information
        )
