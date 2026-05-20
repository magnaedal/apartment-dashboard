# -*- coding: utf-8 -*-
"""
Spotfire IronPython 스크립트 - "분석" 버튼 클릭 핸들러
========================================================
[연결 방법]
  Spotfire > Edit > Script Manager > New Script 에서 이 파일 내용을 붙여 넣고
  "분석" 버튼(Action Control)의 Click 이벤트에 연결합니다.

[사전 설정 필수]
  1. Document Property "SelectedXValue" (String 타입) 생성
     - 리스트 박스 컨트롤이 이 속성에 선택값을 기록하도록 설정
  2. 아래 ── 설정 영역 ── 의 값을 실제 환경에 맞게 수정
"""

import clr
import json
import subprocess

clr.AddReference('Spotfire.Dxp.Application')
clr.AddReference('Spotfire.Dxp.Data')

from Spotfire.Dxp.Data import (
    DataValueCursor, IndexSet,
    DataTableSaveSettings,
)
from Spotfire.Dxp.Data.Import import TextFileDataSource, TextDataReaderSettings
from System.IO import MemoryStream, StreamWriter
from System.Text import Encoding

# ══════════════════════════════════════════════════════════
# ── 설정 영역 (환경에 맞게 수정) ──────────────────────────
TABLE_A_NAME    = "A테이블"          # Spotfire에 로드된 A테이블 이름
TABLE_B_NAME    = "B테이블"          # Spotfire에 로드된 B테이블 이름
X_COLUMN        = "apartment_complex" # 리스트 박스에 사용할 A테이블 컬럼
JOIN_KEY        = "apt_id"            # A↔B 조인 키 컬럼 (두 테이블 공통)
PROPERTY_NAME   = "SelectedXValue"    # 리스트 박스와 연결된 Document Property
RESULT_TABLE    = "분석결과"
PYTHON_EXE      = r"C:\Python27\python.exe"           # Python 2 실행 파일 경로
ANALYSIS_SCRIPT = r"C:\spotfire_scripts\analysis_core.py"  # 분석 스크립트 경로
# ── 설정 끝 ───────────────────────────────────────────────
# ══════════════════════════════════════════════════════════


# ─────────────────────────────────────────────
# 헬퍼: 테이블 → 딕셔너리 리스트 변환
# ─────────────────────────────────────────────

def table_to_dicts(table, row_index_set=None):
    """DataTable 전체(또는 지정 행)를 [{col: val, ...}, ...] 로 변환."""
    col_names = [col.Name for col in table.Columns]
    cursors   = [DataValueCursor.CreateFormatted(table.Columns[c]) for c in col_names]

    rows = []
    iterator = table.GetRows(row_index_set, *cursors) if row_index_set is not None \
               else table.GetRows(*cursors)

    for _row in iterator:
        rows.append({col_names[i]: cursors[i].CurrentValue for i in range(len(col_names))})
    return rows


def filter_index_set(table, column_name, match_value):
    """column_name == match_value 인 행의 IndexSet 반환."""
    idx_set = IndexSet(table.RowCount, False)
    cursor  = DataValueCursor.CreateFormatted(table.Columns[column_name])
    for row in table.GetRows(cursor):
        if cursor.CurrentValue == match_value:
            idx_set.AddIndex(row.Index)
    return idx_set


# ─────────────────────────────────────────────
# 헬퍼: 딕셔너리 리스트 → Spotfire DataTable
# ─────────────────────────────────────────────

def dicts_to_datatable(document, table_name, columns, rows):
    """
    결과 데이터를 CSV MemoryStream 으로 변환 후 Spotfire DataTable 에 반영.
    기존 테이블이 있으면 삭제 후 재생성(Replace).
    """
    # CSV 직렬화
    def escape(v):
        s = u"" if v is None else unicode(v)
        if u"," in s or u'"' in s or u"\n" in s:
            s = u'"' + s.replace(u'"', u'""') + u'"'
        return s

    lines = [u",".join(escape(c) for c in columns)]
    for r in rows:
        lines.append(u",".join(escape(r.get(c, u"")) for c in columns))
    csv_text = u"\n".join(lines)

    # MemoryStream 생성
    stream = MemoryStream()
    writer = StreamWriter(stream, Encoding.UTF8)
    writer.Write(csv_text)
    writer.Flush()
    stream.Position = 0

    # TextDataReaderSettings
    rd_settings = TextDataReaderSettings()
    rd_settings.Separator = ","
    rd_settings.HasColumnHeaders = True

    data_source = TextFileDataSource(stream, rd_settings)

    # 기존 테이블 제거
    if document.Data.Tables.Contains(table_name):
        document.Data.Tables.Remove(document.Data.Tables[table_name])

    document.Data.Tables.Add(table_name, data_source)


# ─────────────────────────────────────────────
# 메인 로직
# ─────────────────────────────────────────────

def run_analysis():
    # 1. 리스트 박스 선택값 읽기
    selected_x = Document.Properties[PROPERTY_NAME]
    if not selected_x or not selected_x.strip():
        Document.Properties["StatusMessage"] = u"리스트 박스에서 항목을 선택하세요."
        return

    # 2. A테이블 필터링
    table_a  = Document.Data.Tables[TABLE_A_NAME]
    idx_a    = filter_index_set(table_a, X_COLUMN, selected_x)

    if idx_a.Count == 0:
        Document.Properties["StatusMessage"] = u"선택값에 해당하는 A테이블 데이터 없음."
        return

    a_data = table_to_dicts(table_a, idx_a)

    # 3. B테이블: A에서 추출한 JOIN_KEY 값과 일치하는 행만
    a_keys  = set(r.get(JOIN_KEY, "") for r in a_data)
    table_b = Document.Data.Tables[TABLE_B_NAME]
    idx_b   = filter_index_set(table_b, JOIN_KEY, None)   # 임시 빈 셋 대신 직접 구성

    idx_b = IndexSet(table_b.RowCount, False)
    b_key_cursor = DataValueCursor.CreateFormatted(table_b.Columns[JOIN_KEY])
    for row in table_b.GetRows(b_key_cursor):
        if b_key_cursor.CurrentValue in a_keys:
            idx_b.AddIndex(row.Index)

    b_data = table_to_dicts(table_b, idx_b)

    # 4. 분석 스크립트(Python 2) 실행
    payload = json.dumps(
        {"selected_x": selected_x, "a_data": a_data, "b_data": b_data},
        ensure_ascii=False,
    ).encode("utf-8")

    try:
        proc = subprocess.Popen(
            [PYTHON_EXE, ANALYSIS_SCRIPT],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = proc.communicate(input=payload)
    except Exception as e:
        Document.Properties["StatusMessage"] = u"프로세스 실행 오류: " + unicode(e)
        return

    if proc.returncode != 0:
        err = stderr_bytes.decode("utf-8") if stderr_bytes else u"알 수 없는 오류"
        Document.Properties["StatusMessage"] = u"분석 스크립트 오류: " + err
        return

    # 5. 결과 파싱 및 DataTable 생성
    try:
        result  = json.loads(stdout_bytes.decode("utf-8"))
        columns = result.get("columns", [])
        rows    = result.get("data", [])
    except Exception as e:
        Document.Properties["StatusMessage"] = u"결과 파싱 오류: " + unicode(e)
        return

    if not rows:
        Document.Properties["StatusMessage"] = u"분석 결과 데이터 없음."
        return

    dicts_to_datatable(Document, RESULT_TABLE, columns, rows)
    Document.Properties["StatusMessage"] = u"분석 완료 ▸ " + selected_x


# 실행
run_analysis()
