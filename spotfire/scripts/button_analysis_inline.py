# -*- coding: utf-8 -*-
"""
Spotfire IronPython 스크립트 - "분석" 버튼 (인라인 exec 방식)
==============================================================
외부 Python 2 인터프리터 없이 IronPython 내에서 analysis_core.py 를
exec() 로 직접 실행합니다. subprocess 사용이 불가한 환경에 사용하세요.

[연결 방법] button_analysis.py 와 동일.
"""

import clr
import json

clr.AddReference('Spotfire.Dxp.Application')
clr.AddReference('Spotfire.Dxp.Data')

from Spotfire.Dxp.Data import DataValueCursor, IndexSet
from Spotfire.Dxp.Data.Import import TextFileDataSource, TextDataReaderSettings
from System.IO import MemoryStream, StreamWriter
from System.Text import Encoding

# ── 설정 ──────────────────────────────────────
TABLE_A_NAME    = "A테이블"
TABLE_B_NAME    = "B테이블"
X_COLUMN        = "apartment_complex"
JOIN_KEY        = "apt_id"
PROPERTY_NAME   = "SelectedXValue"
RESULT_TABLE    = "분석결과"
ANALYSIS_SCRIPT = r"C:\spotfire_scripts\analysis_core.py"
# ──────────────────────────────────────────────


def table_to_dicts(table, row_index_set=None):
    col_names = [col.Name for col in table.Columns]
    cursors   = [DataValueCursor.CreateFormatted(table.Columns[c]) for c in col_names]
    rows = []
    it = table.GetRows(row_index_set, *cursors) if row_index_set is not None \
         else table.GetRows(*cursors)
    for _row in it:
        rows.append({col_names[i]: cursors[i].CurrentValue for i in range(len(col_names))})
    return rows


def dicts_to_datatable(document, table_name, columns, rows):
    def escape(v):
        s = u"" if v is None else unicode(v)
        if u"," in s or u'"' in s or u"\n" in s:
            s = u'"' + s.replace(u'"', u'""') + u'"'
        return s

    lines = [u",".join(escape(c) for c in columns)]
    for r in rows:
        lines.append(u",".join(escape(r.get(c, u"")) for c in columns))

    stream = MemoryStream()
    writer = StreamWriter(stream, Encoding.UTF8)
    writer.Write(u"\n".join(lines))
    writer.Flush()
    stream.Position = 0

    rd = TextDataReaderSettings()
    rd.Separator = ","
    rd.HasColumnHeaders = True

    src = TextFileDataSource(stream, rd)
    if document.Data.Tables.Contains(table_name):
        document.Data.Tables.Remove(document.Data.Tables[table_name])
    document.Data.Tables.Add(table_name, src)


def run_analysis():
    selected_x = Document.Properties[PROPERTY_NAME]
    if not selected_x or not selected_x.strip():
        Document.Properties["StatusMessage"] = u"리스트 박스에서 항목을 선택하세요."
        return

    # A 필터링
    table_a = Document.Data.Tables[TABLE_A_NAME]
    idx_a   = IndexSet(table_a.RowCount, False)
    cur     = DataValueCursor.CreateFormatted(table_a.Columns[X_COLUMN])
    for row in table_a.GetRows(cur):
        if cur.CurrentValue == selected_x:
            idx_a.AddIndex(row.Index)

    if idx_a.Count == 0:
        Document.Properties["StatusMessage"] = u"해당 데이터 없음."
        return

    a_data = table_to_dicts(table_a, idx_a)
    a_keys = set(r.get(JOIN_KEY, "") for r in a_data)

    # B 필터링
    table_b = Document.Data.Tables[TABLE_B_NAME]
    idx_b   = IndexSet(table_b.RowCount, False)
    cur_b   = DataValueCursor.CreateFormatted(table_b.Columns[JOIN_KEY])
    for row in table_b.GetRows(cur_b):
        if cur_b.CurrentValue in a_keys:
            idx_b.AddIndex(row.Index)

    b_data = table_to_dicts(table_b, idx_b)

    # analysis_core.py 를 exec 으로 실행
    try:
        with open(ANALYSIS_SCRIPT, "r") as f:
            script_code = f.read()
    except IOError as e:
        Document.Properties["StatusMessage"] = u"스크립트 파일 읽기 실패: " + unicode(e)
        return

    exec_ns = {
        "selected_x": selected_x,
        "a_data":     a_data,
        "b_data":     b_data,
        "__result__": None,
    }

    # analysis_core.py 의 analyze() 를 호출하는 래퍼를 주입
    wrapper = (
        script_code
        + "\n__result__ = analyze(selected_x, a_data, b_data)\n"
    )

    try:
        exec(wrapper, exec_ns)  # noqa: S102
    except Exception as e:
        Document.Properties["StatusMessage"] = u"분석 실행 오류: " + unicode(e)
        return

    result  = exec_ns.get("__result__", {}) or {}
    columns = result.get("columns", [])
    rows    = result.get("data",    [])

    if not rows:
        Document.Properties["StatusMessage"] = u"분석 결과 없음."
        return

    dicts_to_datatable(Document, RESULT_TABLE, columns, rows)
    Document.Properties["StatusMessage"] = u"분석 완료 ▸ " + selected_x


run_analysis()
