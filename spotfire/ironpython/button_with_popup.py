# =============================================================================
# [Spotfire IronPython] 버튼 액션 스크립트 – 시작/종료 팝업
# =============================================================================
# 설정 방법:
#   1. Spotfire → Insert → Button
#   2. 버튼 우클릭 → Edit Script
#   3. Script Language: IronPython
#   4. 아래 코드를 붙여넣기
# =============================================================================

from System.Windows.Forms import (
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult
)

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
# ── 종료 팝업 (확인 클릭 시) ─────────────────────────────────────────────────
else:
    MessageBox.Show(
        "분석이 완료되었습니다.\n\n"
        "결과가 새 테이블에 저장되었습니다.",
        "분석 완료",
        MessageBoxButtons.OK,
        MessageBoxIcon.Information
    )
