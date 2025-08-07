# utils/pdf_processing.py

import pdfplumber
import pandas as pd
import re

def normalize_text(x):
    """清理字串：合併多重空格，去頭去尾"""
    return "" if x is None else re.sub(r"\s+", " ", str(x)).strip()

def standardize_columns(cols):
    """
    將原始欄位名稱映射到「科目名稱」「學分」「成績」三大欄位
    """
    mapping = {}
    for col in cols:
        lower = normalize_text(col).lower()
        if any(k in lower for k in ["課程", "名稱", "科目"]):
            mapping[col] = "科目名稱"
        elif "學分" in lower or re.match(r"credit", lower):
            mapping[col] = "學分"
        elif any(k in lower for k in ["成績", "gpa", "grade"]):
            mapping[col] = "成績"
        else:
            # 其他欄位留著原名
            mapping[col] = normalize_text(col)
    return mapping

def process_pdf_file(file) -> list[pd.DataFrame]:
    """
    讀取上傳的 PDF，提取所有表格並回傳 DataFrame 列表。
    每張表都會嘗試轉成 DataFrame，並標準化欄位名稱。
    """
    dfs = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                # 清理欄位名稱
                df.columns = [normalize_text(c) for c in df.columns]
                # 做欄位標準化映射
                col_map = standardize_columns(df.columns)
                df = df.rename(columns=col_map)
                dfs.append(df)
    return dfs
