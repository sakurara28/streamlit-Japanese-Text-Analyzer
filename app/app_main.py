import streamlit as st

pages = {
    "Japanese Text Analyzer": [
        st.Page("app_home.py", title="Top Page"),
        st.Page("app_wordfrequency_wordcloud.py", title="Word Frequency & Word Cloud"),
        st.Page("app_sentiment_analysis.py", title="Sentiment Analysis"),
        st.Page("app_zero_shot_classification.py", title="Topic Classification"),
        st.Page("app_scraping_co_occurrence_network.py", title="Co-occurrence_Network"),
    ]
}

pg = st.navigation(pages)
pg.run()