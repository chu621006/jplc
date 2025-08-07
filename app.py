# app.py

import streamlit as st
import pandas as pd
from utils.pdf_processing import process_pdf_file
from utils.grade_analysis import calculate_total_credits

def main():
    st.set_page_config(page_title="成績單學分計算工具 (Debug 模式)", layout="wide")
    st.title("🐞 成績單學分計算工具 (Debug 模式)")

    # 上傳 PDF
    uploaded_file = st.file_uploader("請上傳成績單（PDF）", type=["pdf"])
    if not uploaded_file:
        st.info("請先上傳 PDF 檔案。")
        return

    # 處理 PDF
    dfs = process_pdf_file(uploaded_file)

    # 計算學分
    stats = calculate_total_credits(dfs)

    # 顯示統計
    st.markdown("---")
    st.markdown("## ✅ 分類結果")
    st.markdown(f"- **必修學分**：{stats['required']:.0f}")
    st.markdown(f"- **一類選修**：{stats['i_elective']:.0f}")
    st.markdown(f"- **二類選修**：{stats['ii_elective']:.0f}")
    st.markdown(f"- **其他選修**：{stats['other_elective']:.0f}")
    st.markdown(f"- **總學分**：{stats['total']:.2f}")

    # 列表
    st.markdown("### 📚 通過課程明細 (前5筆)")
    df_passed = pd.DataFrame(stats["passed"])
    st.dataframe(df_passed.head(), use_container_width=True)

    st.markdown("### ⚠️ 未通過課程 (前5筆)")
    df_failed = pd.DataFrame(stats["failed"])
    st.dataframe(df_failed.head(), use_container_width=True)

if __name__ == "__main__":
    main()
