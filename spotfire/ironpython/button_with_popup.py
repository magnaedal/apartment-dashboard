# =============================================================================
# [Spotfire 14.0 IronPython] 버튼 액션 스크립트 – 시작/종료 팝업
# =============================================================================
# 설정 방법 (Spotfire Analyst 14.0):
#   버튼 추가:
#     1. 메뉴 → Insert → Text Area  (새 텍스트 영역 생성)
#     2. 텍스트 영역 우클릭 → Edit Text Area
#     3. 텍스트 영역 편집 창 상단 도구모음 → Insert Action Control → Button
#     4. 버튼 우클릭 → Properties
#     5. [Actions 탭] → Add → Script
#     6. Script Language: IronPython
#     7. 아래 코드를 붙여넣기 → OK
#
# 주의 (Spotfire 14.0):
#   - Script Language는 반드시 "IronPython" 선택 (Python 3.x 와 다름)
#   - Application / Document 전역 객체는 import 없이 바로 사용 가능
# =============================================================================

import clr
clr.AddReference("System.Windows.Forms")
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

# ── 취소 시 안내 팝업 ────────────────────────────────────────────────────────
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
