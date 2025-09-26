import streamlit as st

st.title("Japanese Text Analysis")
st.subheader("体験できる機能一覧")
st.markdown("""
    <h4>🔠 **Word Frequency & Word Cloud**</h4>
    <p>&emsp;&emsp;&emsp;テキストを形態素解析して単語出現頻度を集計し、ワードクラウドで可視化します</p>
    <h4>😊 **Sentiment Analysis**</h4>
    <p>&emsp;&emsp;&emsp;テキストを感情分析し、Positive/Neutral/Negative の確率分布を出力します</p>
    <h4>🏷️ **Topic Classification**</h4>
    <p>&emsp;&emsp;&emsp;テキストをZero-shot分類し、指定したトピックごとの関連度（確率）を算出します</p>
    <h4>🕸️ **Co-occurrence Network**</h4>
    <p>&emsp;&emsp;&emsp;テキストから単語の共起関係を抽出し、ネットワークグラフで可視化します</p>""",
    unsafe_allow_html=True
)