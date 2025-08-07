# utils/pdf_processing.py

import pdfplumber
import pandas as pd
import re

def normalize_text(x):
    """清理字串：合併多重空格"""
    return "" if x is None else re.sub(r"\s+", " ", str(x)).strip()

def process_pdf_file(file) -> list[pd.DataFrame]:
    """
    讀取上傳的 PDF，提取所有表格並回傳 DataFrame 列表。
    每張表都會嘗試轉成 DataFrame。
    """
    dfs = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                # 轉 DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])
                # 清理欄位名稱
                df.columns = [normalize_text(c) for c in df.columns]
                dfs.append(df)
    return dfs
