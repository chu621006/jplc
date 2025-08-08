import re
import pandas as pd

# ---------- 名稱正規化 ----------
def _normalize_name(name: str) -> str:
    """
    將課名做『只比對符號前中文字』的強化版正規化：
    - 去掉各式括號含內容（（）、()、〈〉、【】等）
    - 去掉「上學期/下學期」
    - 移除所有標點與空白（包含全/半形、破折號、斜線）
    """
    s = str(name or "")
    s = re.sub(r'（.*?）|\(.*?\)|〈.*?〉|【.*?】', '', s)
    s = re.sub(r'上學期|下學期', '', s)
    s = re.sub(r'[：:、，,。．\.\-/／—–\s]+', '', s)
    return s.strip()

# ---------- 判定是否通過 ----------
def is_passing_gpa(gpa: str) -> bool:
    # C- 以上、或包含「通過」「抵免」
    return bool(re.search(r'抵免|通過|[ABC][\+\-]?|C-', str(gpa)))

# ---------- 字典：先用原始寫法建立，之後一律正規化後比對 ----------
_REQ_LIST = [
    # 系必修/通識必修/共同必修（用前綴+關鍵詞）
    "綜合日語", "專題研究",
    "多元文化導論", "表象文化概論",
    "語言溝通概論", "社會文化概論",
    "日語語法",                  # 任何版本的語法都視為必修
    "中文：文學欣賞與實用", "大一英文", "大二英文",
    "AI思維與程式設計",
    "全民國防教育",              # 前綴比對
    "大一體育", "大二體育"
]
_I_LIST = [
    "日語語音學演練","日語討論與表達","日語新聞聽解","日劇聽解",
    "專題論證寫作","學習方法論","日語戲劇實踐","類義表現",
    "台日社會語言分析","多元文化社會與語言","華日語言對比分析",
    "中日語言對比分析","辭典學日語","日語分科教學法",
    "日本資訊傳播導論","媒體素養論","歷史與敘事","台日區域專題",
    "不可思議的日本","台日報導製作","台日報導實踐","台日報導寫作",
    "日本古代中世史","日本史","日本近世近代史",
    "台日交流實踐-農食育中的語言實踐"
]
_II_LIST = [
    "華日翻譯","翻譯-中翻日","日語口譯入門","日語口譯實務",
    "職場日語","商務日語","日本上古中古表象文化論","日本古典表象文化論",
    "日本中世近世表象文化論","日語專書導讀","日語精讀與專書探討",
    "日本近代表象文化論","日本現代表象文化論","日本殖民時期台灣日語文學",
    "現代台灣日語文學","文化與敘事","越境文化論","跨文化敘事",
    "日本國際關係","行走·探索·思考-台灣裡的東亞"
]

# 轉為正規化集合（移除標點/括號差異）
_REQ_SET = {_normalize_name(x) for x in _REQ_LIST}
_I_SET   = {_normalize_name(x) for x in _I_LIST}
_II_SET  = {_normalize_name(x) for x in _II_LIST}

# ---------- 課程分類 ----------
def categorize_course(name: str) -> str:
    """
    回傳 'Required' / 'I' / 'II' / 'Other'
    規則：
    - 通識（人文/社會/自然）前綴 => Required
    - 必修：名稱正規化後以 required 任何 token 作「前綴」比對
      （含 綜合日語*, 日語語法*, 大一/二英文*, 大一/二體育*, 全民國防教育*）
    - I/II 類：同樣採用前綴比對
    """
    raw = str(name or "").strip()
    # 通識前綴（不強制冒號）
    if re.match(r'^\s*(人文|社會|自然)', raw):
        return "Required"

    base = _normalize_name(raw)

    if any(base.startswith(tok) for tok in _REQ_SET):
        return "Required"
    if any(base.startswith(tok) for tok in _I_SET):
        return "I"
    if any(base.startswith(tok) for tok in _II_SET):
        return "II"
    return "Other"

# ---------- 主計算 ----------
def calculate_total_credits(df_list: list[pd.DataFrame]) -> dict:
    """
    接受多個 DataFrame（來自 DOCX 解析），回傳：
      total/required/i_elective/ii_elective/other_elective/passed/failed
    需要欄位：『科目名稱』『學分』『成績』（大小寫/別名由 docx_processing 標準化）
    """
    total_credits    = 0.0
    required_credits = 0.0
    i_credits        = 0.0
    ii_credits       = 0.0
    other_credits    = 0.0
    passed           = []
    failed           = []

    for df in df_list:
        # 安全處理：欄位名不同時嘗試別名
        name_col   = "科目名稱" if "科目名稱" in df.columns else ( "課程名稱" if "課程名稱" in df.columns else df.columns[0] )
        credit_col = "學分"     if "學分"     in df.columns else ( "credit" if "credit" in df.columns else df.columns[-2] )
        grade_col  = "成績"     if "成績"     in df.columns else ( "GPA"    if "GPA"    in df.columns else df.columns[-1] )

        for _, row in df.iterrows():
            raw_name = row.get(name_col, "")
            base_name = raw_name  # 保留原名給明細
            name = raw_name

            # 學分
            raw_credit = row.get(credit_col, 0)
            try:
                credit = float(raw_credit)
            except Exception:
                credit = 0.0

            # 成績
            gpa = row.get(grade_col, "")

            if is_passing_gpa(gpa):
                passed.append({"科目名稱": base_name, "學分": credit, "成績": gpa})
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
                failed.append({"科目名稱": base_name, "學分": credit, "成績": gpa})

    return {
        "total":          total_credits,
        "required":       required_credits,
        "i_elective":     i_credits,
        "ii_elective":    ii_credits,
        "other_elective": other_credits,
        "passed":         passed,
        "failed":         failed
    }
