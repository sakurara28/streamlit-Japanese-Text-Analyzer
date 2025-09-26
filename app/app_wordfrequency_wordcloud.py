import streamlit as st
import re
import pandas as pd
from wordfrequency_wordcloud import list_matplotlib_colors, morph_for_freq_wordcloud, plot_word_frequency, counter_df, make_wordcloud

# ページタイトル
st.title("Word Frequency & Word Cloud")
st.write("CSV内のテキストを形態素解析して単語頻度を集計し、ワードクラウドを生成します。")

# ===== データ読み込み & プレビュー =====
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください。", type=["csv"])
if uploaded_file is not None:
    df_wf = pd.read_csv(uploaded_file)
    st.success(f"ファイルが正常にアップロードされました。データ行数: {len(df_wf)}")
    
    # データのプレビュー
    st.subheader("データプレビュー")
    st.dataframe(df_wf.head())
    
    # ファイルの対象column名取得 
    st.subheader("テキスト設定")
    selected_col = st.selectbox("分析する.csvの列名を選択", df_wf.columns)

    # 形態素解析フリー設定
    input_stopwords = st.text_input("ストップワードをカンマ（,）区切りで入力（※入力語と完全一致する単語のみ除外）")
    free_stopwords = re.split(r"[, 　]+", input_stopwords)  # カンマ、半角/全角スペースで分割してリストに変換

    # 棒グラフ / ワードクラウドのカラー選択
    st.subheader("グラフ設定")
    colormap_list = list_matplotlib_colors()
    selected_color = st.selectbox("棒グラフ / ワードクラウドのカラーマップを選択", colormap_list)
else:
    st.warning("CSVファイルをアップロードしてください。")
    st.stop()

# ===== 分析処理 =====
if st.button("実行"):
    with st.spinner("作成中..."):
        # データクレンジング,、形態素解析
        all_tokens_flattened = morph_for_freq_wordcloud(df_wf, selected_col, free_stopwords)

        # 単語頻度グラフ
        st.subheader("単語頻度グラフ")
        fig = plot_word_frequency(all_tokens_flattened, selected_color)
        st.pyplot(fig)

        # データフレームの表示
        df_top30 = counter_df(all_tokens_flattened)
        st.dataframe(df_top30, use_container_width=True)

        # ワードクラウド生成
        st.subheader("ワードクラウド")
        fig_wc = make_wordcloud(all_tokens_flattened, selected_color)
        st.pyplot(fig_wc)
    st.success("完了しました！")