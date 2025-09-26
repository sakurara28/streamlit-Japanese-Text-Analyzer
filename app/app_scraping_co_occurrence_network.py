import streamlit as st
from scraping_co_occurrence_network import (make_search_url, get_search_results, get_article_data,
morph_for_cooccurrence, make_word_pairs, plot_cooccurrence_network)

# ページタイトル
st.title("Co-occurrence Network")
st.write("PR TIMESの記事から共起ネットワークを生成します。")

# ===== PR TIMESの検索KW入力 =====
keyword = st.text_input("キーワードを半角スペース区切りで入力")

# ===== スクレイピング =====
if st.button("実行"):
    with st.spinner("作成中..."):
        # 一覧結果のURL作成
        search_url = make_search_url(keyword)

        # 検索結果一覧から会社名と記事URLを取得
        articles_list_df = get_search_results(search_url)

        # 検索結果一覧から取得したlinkから記事本文を取得してデータフレームで表示
        articles_detail_df = get_article_data(articles_list_df)
        st.dataframe(articles_detail_df, use_container_width=True)

        # 形態素解析
        all_tokens = morph_for_cooccurrence(articles_detail_df)

        # 単語同士のペアを作成してTOP200を抽出
        top200 = make_word_pairs(all_tokens)

        # 共起ネットワーク描画
        fig = plot_cooccurrence_network(top200)
        st.pyplot(fig)
    st.success("完了しました！")