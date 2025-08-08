import re
import pandas as pd
from utils.pdf_processing import normalize_text  # 借用同名函式；或改成從 docx_processing 匯入也可

def categorize_course(name: str) -> str:
    """只比對符號前的中文字，回傳 'Required' / 'I' / 'II' / 'Other'"""
    base = re.sub(
        r'（.*?）|\(.*?\)|上學期|下學期|[、:：「」【】\[\]–—]',
        '',
        name
    ).strip()

    REQUIRED = {
        "綜合日語一A","綜合日語一B","綜合日語一C",
        "綜合日語二A","綜合日語二B","綜合日語二C",
        "綜合日語三","專題研究","多元文化導論","表象文化概論",
        "語言溝通概論","社會文化概論","日語語法一",
        "中文：文學欣賞與實用","大一英文","大二英文",
        "AI思維與程式設計","全民國防教育軍事訓練–國防政策",
        "大一體育：體適能／桌球","大二體育：體操與瑜珈理論與實作"
    }

    I_SET = {
        "日語語音學演練","日語討論與表達","日語新聞聽解","日劇聽解",
        "專題論證寫作","學習方法論","日語戲劇實踐","類義表現",
        "台日社會語言分析","多元文化社會與語言","華日語言對比分析",
        "中日語言對比分析","辭典學日語","日語分科教學法",
        "日本資訊傳播導論","媒體素養論","歷史與敘事","台日區域專題",
        "不可思議的日本","台日報導製作","台日報導實踐","台日報導寫作",
        "日本古代中世史","日本史","日本近世近代史",
        "台日交流實踐-農食育中的語言實踐"
    }

    II_SET = {
        "華日翻譯","翻譯-中翻日","日語口譯入門","日語口譯實務",
        "職場日語","商務日語","日本上古中古表象文化論","日本古典表象文化論",
        "日本中世近世表象文化論","日語專書導讀","日語精讀與專書探討",
        "日本近代表象文化論","日本現代表象文化論","日本殖民時期台灣日語文學",
        "現代台灣日語文學","文化與敘事","越境文化論","跨文化敘事",
        "日本國際關係","行走·探索·思考-台灣裡的東亞"
    }

    if base in REQUIRED or base.startswith(("人文：","社會：","自然：")):
        return "Required"
    if base in I_SET:
        return "I"
    if base in II_SET:
        return "II"
    return "Other"

def is_passing_gpa(gpa: str) -> bool:
    """C-以上（含 C-）、通過、抵免視為通過"""
    return bool(re.search(r'抵免|通過|[ABC][\+\-]?|C-', str(gpa)))

def calculate_total_credits(df_list: list[pd.DataFrame]) -> dict:
    total_credits    = 0.0
    required_credits = 0.0
    i_credits        = 0.0
    ii_credits       = 0.0
    other_credits    = 0.0
    passed           = []
    failed           = []

    for df in df_list:
        for _, row in df.iterrows():
            raw_name = row.get("科目名稱") or row.get("name") or ""
            name = normalize_text(raw_name)

            raw_credit = row.get("學分") or row.get("credit") or 0.0
            try:
                credit = float(raw_credit)
            except Exception:
                credit = 0.0

            gpa = row.get("成績") or row.get("GPA") or row.get("gpa") or ""

            if is_passing_gpa(gpa):
                passed.append({"科目名稱": name, "學分": credit, "成績": gpa})
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
                failed.append({"科目名稱": name, "學分": credit, "成績": gpa})

    return {
        "total":          total_credits,
        "required":       required_credits,
        "i_elective":     i_credits,
        "ii_elective":    ii_credits,
        "other_elective": other_credits,
        "passed":         passed,
        "failed":         failed
    }
