import streamlit as st
import pandas as pd
from sentiment_analysis import sentiment_analysis
 
# ページタイトル
st.title("Sentiment Analysis")
st.write("CSV内のテキストを感情分析し、Positive/Neutral/Negative の確率分布を出力します。")

# ===== データ読み込み & プレビュー =====
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください。", type=["csv"])
if uploaded_file is not None:
    df_sentiment = pd.read_csv(uploaded_file)
    st.success(f"ファイルが正常にアップロードされました。データ行数: {len(df_sentiment)}")
    
    # データのプレビュー
    st.subheader("データプレビュー")
    st.dataframe(df_sentiment.head())
    
    # ファイルの対象column名取得 
    st.subheader("テキスト設定")
    selected_col = st.selectbox("分析する.csvの列名を選択", df_sentiment.columns)

else:
    st.warning("CSVファイルをアップロードしてください。")
    st.stop()

# ===== ポジネガ分類 =====
if st.button("実行"):
    with st.spinner("作成中..."):
        # 選択された列をリスト化（欠損値行削除、文字列に）
        input_texts = df_sentiment[selected_col].dropna().astype(str).tolist()
        # 推論
        sentiment_analysis_data = sentiment_analysis(input_texts)
        # 画面にデータフレームを表示
        st.dataframe(sentiment_analysis_data.head())
        
        # CSVファイル出力
        st.download_button(
            label = "CSVファイルをダウンロード",
            data= sentiment_analysis_data.to_csv().encode(),  # CSV形式の文字列に変換しバイト列にエンコード
            file_name="output_sentiment_analysis.csv", # ダウンロードされるファイル名
            mime="text/csv" # ファイルのMIMEタイプを指定
        )
    st.success("完了しました！")