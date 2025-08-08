import re
import pandas as pd
from io import BytesIO
import docx  # python-docx

def normalize_text(x):
    """清理字串：合併多重空格、去頭去尾"""
    return "" if x is None else re.sub(r"\s+", " ", str(x)).strip()

def standardize_columns(cols):
    """
    將原始欄位名稱映射到『科目名稱』『學分』『成績』
    其餘欄位保留原名（清理後）
    """
    mapping = {}
    for col in cols:
        raw = normalize_text(col)
        low = raw.lower()
        if any(k in low for k in ["科目", "課程", "名稱", "subject", "course"]):
            mapping[col] = "科目名稱"
        elif ("學分" in low) or ("credit" in low):
            mapping[col] = "學分"
        elif any(k in low for k in ["成績", "gpa", "grade", "score"]):
            mapping[col] = "成績"
        else:
            mapping[col] = raw
    return mapping

def _table_to_dataframe(tbl) -> pd.DataFrame:
    """把 python-docx 的 table 轉成 DataFrame（第一列當表頭）"""
    rows = tbl.rows
    if len(rows) < 2:
        return pd.DataFrame()  # 沒資料就略過

    header = [normalize_text(cell.text) for cell in rows[0].cells]
    data = []
    for r in rows[1:]:
        cells = [normalize_text(c.text) for c in r.cells]
        # 對齊欄數
        if len(cells) < len(header):
            cells = cells + [""] * (len(header) - len(cells))
        elif len(cells) > len(header):
            cells = cells[:len(header)]
        # 空白列略過
        if any(cells):
            data.append(cells)

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=header)
    # 欄位標準化
    col_map = standardize_columns(df.columns)
    df = df.rename(columns=col_map)
    return df

def process_docx_file(file) -> list[pd.DataFrame]:
    """
    讀取上傳的 DOCX，提取所有表格並回傳 DataFrame 列表。
    - 走遍所有 tables（不只第二個）
    - 標準化欄位名稱：『科目名稱』『學分』『成績』
    """
    content = file.read()  # Streamlit 上傳物件 -> bytes
    doc = docx.Document(BytesIO(content))
    dfs = []
    for tbl in doc.tables:
        df = _table_to_dataframe(tbl)
        if not df.empty:
            dfs.append(df)
    return dfs
