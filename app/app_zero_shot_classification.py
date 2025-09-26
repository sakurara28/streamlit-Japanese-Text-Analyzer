import streamlit as st
import pandas as pd
from zero_shot_classification import zero_shot_classification
import re
 
# ページタイトル
st.title("Sentiment Analysis")
st.write("CSVファイルからトピック分類データを生成します。")

# ===== データ読み込み & プレビュー =====
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください。", type=["csv"])
if uploaded_file is not None:
    df_topic = pd.read_csv(uploaded_file)
    st.success(f"ファイルが正常にアップロードされました。データ行数: {len(df_topic)}")
    
    # データのプレビュー
    st.subheader("データプレビュー")
    st.dataframe(df_topic.head())
    
    # ファイルの対象column名取得 
    st.subheader("テキスト設定")
    selected_col = st.selectbox("分析する.csvの列名を選択", df_topic.columns)

    # カテゴリ名の入力
    input_colcategories = st.text_input("トピック分類したいキーワードをカンマ（,）区切りで入力")
    colcategories = re.split(r"[, 　]+", input_colcategories)  # カンマ、半角/全角スペースで分割してリストに変換

else:
    st.warning("CSVファイルをアップロードしてください。")
    st.stop()

# ===== ゼロショット分類 =====
if st.button("実行"):
    with st.spinner("作成中..."):
        # 選択された列をリスト化（欠損値行削除、文字列に）
        input_texts = df_topic[selected_col].dropna().astype(str).tolist()
        # 推論
        topic_classification_data = zero_shot_classification(input_texts, colcategories)
        # 画面にデータフレームを表示
        st.dataframe(topic_classification_data.head())
        
        # CSVファイル出力
        st.download_button(
            label = "CSVファイルをダウンロード",
            data= topic_classification_data.to_csv().encode(),  # CSV形式の文字列に変換しバイト列にエンコード
            file_name="output_topic_classification.csv", # ダウンロードされるファイル名
            mime="text/csv" # ファイルのMIMEタイプを指定
        )
    st.snow()
    st.success("完了しました！")