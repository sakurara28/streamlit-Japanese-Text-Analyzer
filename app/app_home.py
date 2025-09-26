import streamlit as st

st.title("Japanese Text Analysis")
st.subheader("体験できる機能一覧")
st.markdown("""
    <h4>🔠 **Word Frequency & Word Cloud**</h4>
    <p>&emsp;&emsp;&emsp;文章を形態素解析して頻出単語を可視化します</p>
    <h4>😊 **Sentiment Analysis**</h4>
    <p>&emsp;&emsp;&emsp;文章をポジティブ／ネガティブに分類します</p>
    <h4>🏷️ **Topic Classification**</h4>
    <p>&emsp;&emsp;&emsp;文章の内容から自動的にトピックを推定します</p>
    <h4>🕸️ **Co-occurrence Network**</h4>
    <p>&emsp;&emsp;&emsp;単語のつながりをネットワーク図で表示します</p>""",
    unsafe_allow_html=True
)