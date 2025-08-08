import streamlit as st
import pandas as pd

from utils.docx_processing import process_docx_file
from utils.grade_analysis import calculate_total_credits

def main():
    st.set_page_config(page_title="成績單學分計算工具（DOCX）", layout="wide")
    st.title("📄 成績單學分計算工具（DOCX）")

    # 使用說明下載按鈕
    with open("usage_guide.pdf", "rb") as f:
        pdf_bytes = f.read()
    st.download_button(
        label="📖 使用說明 (PDF)",
        data=pdf_bytes,
        file_name="使用說明.pdf",
        mime="application/pdf"
    )

    uploaded_file = st.file_uploader("請上傳成績單（Word .docx）", type=["docx"])
    if not uploaded_file:
        st.info("請先上傳 DOCX 檔案。")
        return

    # 解析 DOCX -> DataFrame 列表
    dfs = process_docx_file(uploaded_file)
    if not dfs:
        st.error("讀不到表格資料，請確認檔案內容。")
        return

    # 統計
    stats = calculate_total_credits(dfs)
    total           = stats["total"]
    required        = stats["required"]
    i_elective      = stats["i_elective"]
    ii_elective     = stats["ii_elective"]
    other_elective  = stats["other_elective"]
    elective_total  = i_elective + ii_elective + other_elective

    st.markdown("## ✅ 查詢結果")
    st.markdown(f"- **必修學分**：{required:.0f} 學分")
    st.markdown(f"- **一類選修學分**：{i_elective:.0f} 學分")
    st.markdown(f"- **二類選修學分**：{ii_elective:.0f} 學分")
    st.markdown(f"- **總選修學分**：{elective_total:.0f} 學分")
    st.markdown(
        f"<p style='font-size:32px; margin:8px 0;'>📊 **總學分**：<strong>{total:.2f}</strong></p>",
        unsafe_allow_html=True
    )

    # 各分類通過清單（分開顯示）
    st.markdown("### 🧩 分類清單（通過）")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("必修（通過）")
        req_df = pd.DataFrame(stats["passed_required"])
        st.dataframe(req_df if not req_df.empty else pd.DataFrame(columns=["科目名稱","學分","成績"]),
                     use_container_width=True)
        if not req_df.empty:
            st.download_button("下載必修清單 CSV",
                               req_df.to_csv(index=False, encoding="utf-8-sig"),
                               "必修_通過.csv", "text/csv")

    with col2:
        st.subheader("一類選修（通過）")
        i_df = pd.DataFrame(stats["passed_i"])
        st.dataframe(i_df if not i_df.empty else pd.DataFrame(columns=["科目名稱","學分","成績"]),
                     use_container_width=True)
        if not i_df.empty:
            st.download_button("下載一類清單 CSV",
                               i_df.to_csv(index=False, encoding="utf-8-sig"),
                               "一類選修_通過.csv", "text/csv")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("二類選修（通過）")
        ii_df = pd.DataFrame(stats["passed_ii"])
        st.dataframe(ii_df if not ii_df.empty else pd.DataFrame(columns=["科目名稱","學分","成績"]),
                     use_container_width=True)
        if not ii_df.empty:
            st.download_button("下載二類清單 CSV",
                               ii_df.to_csv(index=False, encoding="utf-8-sig"),
                               "二類選修_通過.csv", "text/csv")

    with col4:
        st.subheader("其他選修（通過）")
        other_df = pd.DataFrame(stats["passed_other"])
        st.dataframe(other_df if not other_df.empty else pd.DataFrame(columns=["科目名稱","學分","成績"]),
                     use_container_width=True)
        if not other_df.empty:
            st.download_button("下載其他選修清單 CSV",
                               other_df.to_csv(index=False, encoding="utf-8-sig"),
                               "其他選修_通過.csv", "text/csv")

    # 全部通過/未通過清單（原本的）
    st.markdown("### 📚 所有通過課程（彙整）")
    all_passed_df = pd.DataFrame(stats["passed"])
    st.dataframe(all_passed_df, use_container_width=True)

    st.markdown("### ⚠️ 未通過課程")
    failed_df = pd.DataFrame(stats["failed"])
    st.dataframe(failed_df, use_container_width=True)

# 回饋連結
    st.markdown(
        '<p style="text-align:center;">'
        '感謝您的使用，若您有相關修改建議或發生其他類型錯誤，'
        '<a href="https://forms.gle/Bu95Pt74d1oGVCev5" target="_blank">請點此提出</a>'
        '</p>',
        unsafe_allow_html=True
    )
    # 開發者資訊
    st.markdown(
        '<p style="text-align:center;">'
        '開發者：<a href="https://www.instagram.com/chiuuuuu11.7?igsh=MWRlc21zYW55dWZ5Yw==" target="_blank">Chu</a>'
        '</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()


