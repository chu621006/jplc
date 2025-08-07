import streamlit as st
import pandas as pd
from utils.docx_processing import process_docx_file
from utils.grade_analysis import calculate_total_credits

def main():
    st.set_page_config(page_title="成績單學分計算工具", layout="wide")

    # 標題
    st.title("📄 成績單學分計算工具")

    # 使用說明下載按鈕
    with open("usage_guide.pdf", "rb") as f:
        pdf_bytes = f.read()
    st.download_button(
        label="📖 使用說明 (PDF)",
        data=pdf_bytes,
        file_name="使用說明.pdf",
        mime="application/pdf"
    )

    # 上傳成績單區（僅限 .docx）
    st.write("請上傳 Word (.docx) 格式的成績單檔案。")
    uploaded_file = st.file_uploader(
        "選擇一個成績單檔案（支援 DOCX）",
        type=["docx"]
    )

    if not uploaded_file:
        st.info("請先上傳檔案，以開始學分計算。")
        return

    # 單一路徑：Docx 解析
    dfs = process_docx_file(uploaded_file)
    total_credits, passed, failed = calculate_total_credits(dfs)

    # --- 分隔線 & 查詢結果 ---
    st.markdown("---")
    st.markdown("## ✅ 查詢結果")

    # 總學分顯示
    st.markdown(
        f"<p style='font-size:32px; margin:4px 0;'>目前總學分：<strong>{total_credits:.2f}</strong></p>",
        unsafe_allow_html=True
    )

    # 目標與差額
    target = st.number_input("目標學分（例如：128）", min_value=0.0, value=128.0, step=1.0)
    diff = target - total_credits
    if diff > 0:
        st.markdown(
            f"<p style='font-size:24px;'>還需 <span style='color:red;'>{diff:.2f}</span> 學分</p>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<p style='font-size:24px;'>已超出畢業學分 <span style='color:red;'>{abs(diff):.2f}</span> 學分</p>",
            unsafe_allow_html=True
        )

    # 通過課程列表
    st.markdown("### 📚 通過的課程列表")
    if passed:
        df_passed = pd.DataFrame(passed)
        st.dataframe(df_passed, use_container_width=True)
        csv_pass = df_passed.to_csv(index=False, encoding='utf-8-sig')
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
        csv_fail = df_failed.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="下載不及格課程 CSV",
            data=csv_fail,
            file_name="不及格課程列表.csv",
            mime="text/csv"
        )
    else:
        st.info("未偵測到任何不及格的課程。")

    # （可保留後續通識 Word 單獨上傳功能）
    st.markdown("---")
    st.markdown("## 🎓 通識學分計算 (Word 單獨功能)")
    with open("caculate.pdf", "rb") as f:
        pdf_bytes = f.read()
    st.download_button(
        label="‼️ 通識學分計算使用說明 (PDF) ‼️",
        data=pdf_bytes,
        file_name="通識學分計算使用說明處理.pdf",
        mime="application/pdf"
    )
    gen_docx = st.file_uploader(
        "請上傳 Word 檔 (.docx) 以計算通識學分", type=["docx"], key="gened_word"
    )
    if gen_docx:
        dfs_gen = process_docx_file(gen_docx)
        _, passed_gen, _ = calculate_total_credits(dfs_gen)
        df_gen = pd.DataFrame(passed_gen)
        if df_gen.empty:
            st.info("未偵測到任何通識課程。")
        else:
            prefixes = ("人文：", "自然：", "社會：")
            df_selected = df_gen[df_gen["科目名稱"].str.startswith(prefixes)].reset_index(drop=True)
            if df_selected.empty:
                st.info("未偵測到任何符合通識前綴的課程。")
            else:
                total_gen = df_selected["學分"].sum()
                st.markdown(
                    f"<p style='font-size:28px; font-weight:bold;'>通識總學分：{total_gen:.0f}</p>",
                    unsafe_allow_html=True
                )
                df_selected["領域"] = df_selected["科目名稱"].str.extract(r"^(人文：|自然：|社會：)")[0].str[:-1]
                gen_by_area = df_selected.groupby("領域")["學分"].sum().reindex(["人文","自然","社會"], fill_value=0)
                st.markdown("**各領域學分**：")
                for area, credits in gen_by_area.items():
                    st.markdown(f"- {area}：{credits:.0f} 學分")
                st.dataframe(df_selected[["領域", "科目名稱", "學分"]], use_container_width=True)

    # 回饋 & 開發者資訊
    st.markdown(
        '<p style="text-align:center;">'
        '感謝您的使用，若有建議或錯誤回報，'
        '<a href="https://forms.gle/Bu95Pt74d1oGVCev5" target="_blank">點此提出</a>'
        '</p>', unsafe_allow_html=True
    )
    st.markdown(
        '<p style="text-align:center;">'
        '開發者：<a href="https://www.instagram.com/chiuuuuu11.7" target="_blank">Chu</a>'
        '</p>', unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
