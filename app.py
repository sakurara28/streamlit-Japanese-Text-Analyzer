import streamlit as st
from wordcloud import WordCloud
import pandas as pd
import numpy as np
from sudachipy import tokenizer, dictionary
import neologdn
from collections import Counter
import re
import matplotlib.pyplot as plt
import japanize_matplotlib

# ページタイトル
st.title("日本語テキスト分析アプリ")
st.write("CSVファイルから単語頻度分析とワードクラウドを生成します。")

# ファイルアップロード機能
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください。", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.success(f"ファイルが正常にアップロードされました。データ行数: {len(data)}")
    
    # データのプレビュー
    st.subheader("データプレビュー")
    st.dataframe(data.head())
else:
    st.warning("CSVファイルをアップロードしてください。")
    st.stop()

# 形態素解析の設定
st.subheader("テキスト分析設定")
selected_col = st.selectbox("解析する列を選択", data.columns)
colormap_list = [
    "viridis:（黄緑～青）",
    "plasma:（黄～紫）",
    "inferno:（黄～赤～黒）",
    "magma:（ピンク～黒）",
    "cool:（水色～ピンク）",
    "spring:（ピンク～黄緑）",
    "autumn:（赤～オレンジ）",
    "winter:（青～緑）",
    "rainbow:（虹色）",
]
selected_color = st.selectbox("ワードクラウドのカラーマップを選択", colormap_list)

# 処理開始
if st.button("実行"):
    with st.spinner("作成中..."):
        tokenizer_obj = dictionary.Dictionary(dict_type="full").create()
        mode = tokenizer.Tokenizer.SplitMode.C  # C：最も長い分割形式（A～C）

        keep_pos = ["名詞", "動詞", "形容詞"]  # 抽出したい品詞
        drop_pos = ["非自立可能"]  # 除外したい品詞（動詞の一部）
        stopwords = ["事","為","気","方","前","いう","こと","ため","ところ","ほう","とき","もの","思う","言う"]  # ストップワード
        all_tokens_flattened  = []  # 結果を入れるリスト（棒グラフ・ワードクラウド用）
        all_tokens_by_review = []  # 結果を入れるリスト（トピック分類用）

        # 形態素解析の実行
        # progress_bar = st.progress(0)

        for i, text in enumerate(data[selected_col]):
            text = neologdn.normalize(text).lower()  # 正規化、小文字化
            tokens = tokenizer_obj.tokenize(text, mode)  # トークンに分解
            dictionary_form_line = []
            for token in tokens:
                pos = token.part_of_speech()  # 品詞の抽出
                if pos[0] == "動詞" and pos[1] in drop_pos:  # 動詞でかつ品詞細分類1が非自立可能だったらスキップ
                    continue
                if pos[0] in keep_pos:  # 必要な品詞かつ不要単語でなければ抽出
                    dictionary_form = token.dictionary_form()  # 辞書に載ってる形（活用のない元の形）
                    if not re.fullmatch(r"[ぁ-んァ-ヶー0-9a-z]", dictionary_form) and dictionary_form not in stopwords:  # 平仮名、カナ、数字で1文字を除外
                        dictionary_form_line.append(dictionary_form)
            if dictionary_form_line:
                all_tokens_flattened.extend(dictionary_form_line)  # 棒グラフ・ワードクラウド用
                all_tokens_by_review.append(dictionary_form_line)  # トピック分類用
            

        # ===== 単語頻度分析 =====
        st.subheader("単語頻度グラフ")

        counter = Counter(all_tokens_flattened)  # カウント

        top30 = counter.most_common(30)[::-1]  # 出現数上位30語（逆順で下から上へ）

        words, counts = zip(*top30)  # 単語と出現回数を別々のリストに分解
        words = list(words)
        counts = list(counts)

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(words, counts, color="skyblue")
        ax.set_xlabel("出現回数", fontsize=12)
        ax.set_ylabel("単語", fontsize=12)
        ax.set_ylim(-1, len(words))  # y軸の上下の余白詰め
        ax.set_title("単語頻度分析（上位30語）", fontsize=18)
        plt.tight_layout()

        st.pyplot(fig)

        # 頻度データの表示
        st.write("頻度データ（上位10語）")
        common_words =counter.most_common(10)
        df_common = pd.DataFrame(common_words, columns=["単語", "出現回数"])
        df_common.index = df_common.index + 1
        st.dataframe(df_common, use_container_width=True)

        # ===== ワードクラウド生成 =====
        st.subheader("ワードクラウド生成")

        # 楕円マスクの生成関数
        def make_ellipse_mask(width, height):
            y, x = np.ogrid[:height, :width]
            center_x = (width - 1) / 2
            center_y = (height - 1) / 2
            a = center_x  # 横半径
            b = center_y  # 縦半径

            # 楕円の方程式：(x - cx)^2/a^2 + (y - cy)^2/b^2 <= 1
            mask = ((x - center_x)**2) / (a**2) + ((y - center_y)**2) / (b**2) > 1
            mask = 255 * mask.astype(int)  # 白（255）＝単語を置かない
            return mask

        dic_result = dict(counter)  # ワードクラウド取込用に辞書型ヘ変換
        mask_ellipse = make_ellipse_mask(1000, 600)  # 楕円マスク関数の呼び出し

        # Windows用のフォントパス設定
        font_path = "C:/Windows/Fonts/msgothic.ttc"
        wordcloud = WordCloud(
            width=1000,
            height=600,
            mask=mask_ellipse,
            font_path=font_path,
            background_color="white",
            colormap=selected_color.split(":")[0],
            max_words=100
        ).fit_words(dic_result)

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(wordcloud)
        ax.axis("off")
        plt.tight_layout()

        st.pyplot(fig)
    st.success("完了しました！")
