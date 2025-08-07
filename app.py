import streamlit as st
import pandas as pd
from utils.pdf_processing import process_pdf_file
from utils.grade_analysis import calculate_total_credits

def main():
    st.set_page_config(page_title="成績單學分計算工具", layout="wide")
    st.title("📄 成績單學分計算工具")

    # 使用說明下載按鈕
    try:
        with open("usage_guide.pdf", "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="📖 使用說明 (PDF)",
            data=pdf_bytes,
            file_name="使用說明.pdf",
            mime="application/pdf"
        )
    except FileNotFoundError:
        st.warning("使用說明檔案 usage_guide.pdf 不存在。")

    # 上傳成績單區（僅限 PDF）
    st.write("請上傳成績單（PDF 純表格）。")
    uploaded_file = st.file_uploader(
        "選擇一個成績單檔案（支援 PDF）",
        type=["pdf"]
    )

    if not uploaded_file:
        st.info("請先上傳 PDF 檔案，以開始學分計算。")
        return

    # 處理 PDF
    dfs = process_pdf_file(uploaded_file)
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
    st.markdown("---")
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
        csv_pass = df_passed.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="下載通過課程 CSV",
            data=csv_pass,
            file_name="通過課程列表.csv",
            mime="text/csv"
        )
    else:
        st.info("未偵測到任何通過的課程。")

    # 不及格課程列表
    st.markdown("### ⚠️ 不及格的課程列表")
    if failed:
        df_failed = pd.DataFrame(failed)
        st.dataframe(df_failed, use_container_width=True)
        csv_fail = df_failed.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="下載不及格課程 CSV",
            data=csv_fail,
            file_name="不及格課程列表.csv",
            mime="text/csv"
        )
    else:
        st.info("未偵測到任何不及格的課程。")

    # 回饋 & 開發者資訊
    st.markdown(
        '<p style="text-align:center;">'
        '感謝您的使用，若有建議或錯誤回報，'
        '<a href="https://forms.gle/Bu95Pt74d1oGVCev5" target="_blank">點此提出</a>'
        '</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p style="text-align:center;">'
        '開發者：<a href="https://www.instagram.com/chiuuuuu11.7" target="_blank">Chu</a>'
        '</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
