import streamlit as st
import pandas as pd

from utils.grade_analysis import calculate_total_credits
from utils.docx_processing import process_docx_file
from utils.pdf_processing import process_pdf_file  # 仍保留，若你想同時支援 PDF

def main():
    st.set_page_config(page_title="成績單學分計算工具", layout="wide")
    st.title("📄 成績單學分計算工具（DOCX 版）")

    # 上傳（預設只開 .docx；若要同時支援 PDF，把 type 改成 ["docx","pdf"]）
    uploaded_file = st.file_uploader("請上傳成績單（Word .docx）", type=["docx"])
    if not uploaded_file:
        st.info("請先上傳 DOCX 檔案。")
        return

    # 解析 DOCX（若你要同時支援 PDF，可依副檔名分支）
    name_lower = uploaded_file.name.lower()
    if name_lower.endswith(".docx"):
        dfs = process_docx_file(uploaded_file)
    elif name_lower.endswith(".pdf"):
        dfs = process_pdf_file(uploaded_file)
    else:
        st.error("不支援的檔案格式。")
        return

    if not dfs:
        st.error("讀不到表格資料，請確認檔案內容。")
        return

    # 計算學分
    stats = calculate_total_credits(dfs)
    total           = stats["total"]
    required        = stats["required"]
    i_elective      = stats["i_elective"]
    ii_elective     = stats["ii_elective"]
    other_elective  = stats["other_elective"]
    passed          = stats["passed"]
    failed          = stats["failed"]
    elective_total  = i_elective + ii_elective + other_elective

    # 顯示結果
    st.markdown("## ✅ 查詢結果")
    st.markdown(f"- **必修學分**：{required:.0f} 學分")
    st.markdown(f"- **一類選修學分**：{i_elective:.0f} 學分")
    st.markdown(f"- **二類選修學分**：{ii_elective:.0f} 學分")
    st.markdown(f"- **總選修學分**：{elective_total:.0f} 學分")
    st.markdown(
        f"<p style='font-size:32px; margin:8px 0;'>📊 **總學分**：<strong>{total:.2f}</strong></p>",
        unsafe_allow_html=True
    )

    # 通過課程列表
    st.markdown("### 📚 通過的課程列表")
    if passed:
        df_passed = pd.DataFrame(passed)
        st.dataframe(df_passed, use_container_width=True)
        st.download_button(
            "下載通過課程 CSV",
            df_passed.to_csv(index=False, encoding="utf-8-sig"),
            file_name="通過課程列表.csv",
            mime="text/csv",
        )
    else:
        st.info("未偵測到任何通過的課程。")

    # 不及格課程列表
    st.markdown("### ⚠️ 不及格的課程列表")
    if failed:
        df_failed = pd.DataFrame(failed)
        st.dataframe(df_failed, use_container_width=True)
        st.download_button(
            "下載不及格課程 CSV",
            df_failed.to_csv(index=False, encoding="utf-8-sig"),
            file_name="不及格課程列表.csv",
            mime="text/csv",
        )
    else:
        st.info("未偵測到任何不及格的課程。")

if __name__ == "__main__":
    main()
