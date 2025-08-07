# utils/grade_analysis.py

import re
import pandas as pd
from utils.pdf_processing import normalize_text

# 課程分類函式
def categorize_course(name: str) -> str:
    base = re.sub(
        r'（.*?）|\(.*?\)|上學期|下學期|[、:：「」【】\[\]–—]',
        '',
        name
    ).strip()
    # 必修
    REQUIRED = { ... }   # 同前面提供完整集合
    # I 類
    I_SET = { ... }
    # II 類
    II_SET = { ... }

    if base in REQUIRED or base.startswith(("人文：","社會：","自然：")):
        return "Required"
    if base in I_SET:
        return "I"
    if base in II_SET:
        return "II"
    return "Other"

def is_passing_gpa(gpa: str) -> bool:
    return bool(re.search(r'抵免|通過|[ABC][\+\-]?|C-', str(gpa)))

def calculate_total_credits(df_list: list[pd.DataFrame]) -> dict:
    total = req = i_cr = ii_cr = other = 0.0
    passed, failed = [], []

    for df in df_list:
        # 印出前 5 個 raw 名稱，做調試
        sample_names = df.get("科目名稱", df.columns.tolist())[0:5]
        print("🧐 調試: 取到的科目名稱範例：", sample_names)

        for _, row in df.iterrows():
            raw_name = row.get("科目名稱") or row.get("name") or ""
            name = normalize_text(raw_name)
            # Debug
            print("🔍 調試: 處理後名稱：", name)

            # 學分
            raw_credit = row.get("學分") or row.get("credit") or 0
            try:
                credit = float(raw_credit)
            except:
                credit = 0.0

            # 成績
            gpa = row.get("成績") or row.get("GPA") or row.get("gpa") or ""

            if is_passing_gpa(gpa):
                passed.append({"科目名稱": name, "學分": credit, "成績": gpa})
                total += credit
                cat = categorize_course(name)
                if cat == "Required":
                    req += credit
                elif cat == "I":
                    i_cr += credit
                elif cat == "II":
                    ii_cr += credit
                else:
                    other += credit
            else:
                failed.append({"科目名稱": name, "學分": credit, "成績": gpa})

    return {
        "total":          total,
        "required":       req,
        "i_elective":     i_cr,
        "ii_elective":    ii_cr,
        "other_elective": other,
        "passed":         passed,
        "failed":         failed
    }
