import pandas as pd
import re

def normalize_text(x):
    return "" if x is None else re.sub(r"\s+", " ", str(x)).strip()

def is_passing_gpa(gpa_str):
    s = normalize_text(gpa_str).upper()
    if not s: return False
    if s in ["PASS", "通過", "抵免"]: return True
    if re.match(r"^[A-C][+\-]?$", s): return True
    if s in ["D","D-","E","F","X"]: return False
    return False

def parse_credit_and_gpa(txt):
    s = normalize_text(txt)
    # e.g. "2 A+" / "A+ 2"
    m1 = re.match(r"([A-Fa-f][+\-]?)\s*(\d+(\.\d+)?)", s)
    if m1:
        return float(m1.group(2)), m1.group(1).upper()
    m2 = re.match(r"(\d+(\.\d+)?)\s*([A-Fa-f][+\-]?)", s)
    if m2:
        return float(m2.group(1)), m2.group(3).upper()
    # 單純學分
    m3 = re.match(r"(\d+(\.\d+)?)", s)
    if m3:
        return float(m3.group(1)), ""
    # 單純 GPA
    m4 = re.match(r"([A-Fa-f][+\-]?)", s)
    if m4:
        return 0.0, m4.group(1).upper()
    return 0.0, ""

def calculate_total_credits(df_list):
    # 初始化
    total_credits = 0.0
    required_credits = 0.0
    i_credits = 0.0
    ii_credits = 0.0
    other_credits = 0.0
    passed = []
    failed = []

    from utils.credit_rules import categorize_course

    for df in df_list:
        for _, row in df.iterrows():
            name = row.get("科目名稱", "")
            credit = row.get("學分", 0.0)
            gpa = row.get("GPA", "") or row.get("成績","") or row.get("gpa","")
            if is_passing_gpa(gpa):
                passed.append(row.to_dict())
                total_credits += credit
                cat = categorize_course(name)
                if cat == "Required":
                    required_credits += credit
                elif cat == "I":
                    i_credits += credit
                elif cat == "II":
                    ii_credits += credit
                else:
                    other_credits += credit
            else:
                failed.append(row.to_dict())

    return {
        "total": total_credits,
        "required": required_credits,
        "i_elective": i_credits,
        "ii_elective": ii_credits,
        "other_elective": other_credits,
        "passed": passed,
        "failed": failed
    }
