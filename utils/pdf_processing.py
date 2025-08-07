# utils/pdf_processing.py

import pdfplumber
import pandas as pd
import re

def normalize_text(x):
    """清理字串：合併多重空格，去頭去尾"""
    return "" if x is None else re.sub(r"\s+", " ", str(x)).strip()

def standardize_columns(cols):
    """
    印出原始欄位清單並映射到科目名稱/學分/成績
    """
    print("📝 調試: 原始欄位列表：", cols)
    mapping = {}
    for col in cols:
        lower = normalize_text(col).lower()
        if any(k in lower for k in ["課程", "名稱", "科目"]):
            mapping[col] = "科目名稱"
        elif "學分" in lower or "credit" in lower:
            mapping[col] = "學分"
        elif any(k in lower for k in ["成績", "gpa", "grade"]):
            mapping[col] = "成績"
        else:
            mapping[col] = normalize_text(col)
    print("📝 調試: 標準化後欄位映射：", mapping)
    return mapping

def process_pdf_file(file) -> list[pd.DataFrame]:
    """
    讀 PDF，提取所有表格，標準化欄位名稱，並回傳 DataFrame list
    """
    dfs = []
    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            for j, table in enumerate(tables, start=1):
                df = pd.DataFrame(table[1:], columns=table[0])
                # 清理欄位名
                df.columns = [normalize_text(c) for c in df.columns]
                # 標準化映射
                col_map = standardize_columns(df.columns)
                df = df.rename(columns=col_map)
                print(f"📝 調試: page {i} table {j} 處理後欄位：", df.columns.tolist())
                dfs.append(df)
    return dfs
