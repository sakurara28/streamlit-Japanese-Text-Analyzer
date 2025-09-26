from wordcloud import WordCloud
import pandas as pd
import numpy as np
from sudachipy import tokenizer, dictionary
import neologdn, re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib

# カラー一覧（単色 / カラーマップ）
def list_matplotlib_colors(): 
    colormap_list = [
        "limegreen / viridis（黄緑～青）",
        "mediumvioletred / plasma（黄～紫）",
        "orangered / inferno（黄～赤～黒）",
        "deeppink / magma（ピンク～黒）",
        "skyblue / cool（水色～ピンク）",
        "hotpink / spring（ピンク～黄緑）",
        "darkorange / autumn（赤～オレンジ）",
        "teal / winter（青～緑）",
        "royalblue / rainbow（虹色）",
    ]
    return colormap_list

# ===== 頻出単語&ワードクラウド用 形態素解析、データクレンジング =====
def morph_for_freq_wordcloud(df_wf: pd.DataFrame, selected_column: str, free_stopwords: list[str]):
    tokenizer_obj = dictionary.Dictionary(dict_type="full").create()
    mode = tokenizer.Tokenizer.SplitMode.C  # C：最も長い分割形式（A～C）

    stopwords = ["事","為","気","方","前","いう","こと","ため","ところ","ほう","とき","もの","思う","言う"]  # ストップワード
    keep_pos = ["名詞", "動詞", "形容詞"]  # 抽出したい品詞
    drop_pos = ["非自立可能"]  # 除外したい品詞（動詞の一部）
    
    all_tokens_flattened = []
    for i, text in enumerate(df_wf[selected_column]):
        norm_text = neologdn.normalize(text).lower()      # 正規化、小文字化
        tokens = tokenizer_obj.tokenize(norm_text, mode)  # トークンに分解

        dictionary_form_line = []
        for token in tokens:
            pos = token.part_of_speech()  # 品詞の抽出
            if pos[0] == "動詞" and pos[1] in drop_pos:  # 動詞でかつ品詞細分類1が非自立可能だったらスキップ
                continue
            if pos[0] in keep_pos:  # 必要な品詞かつ不要単語でなければ抽出
                dictionary_form = token.dictionary_form()  # 辞書に載ってる形（活用のない元の形）
                if not re.fullmatch(r"[ぁ-んァ-ヶー0-9a-z]", dictionary_form) and dictionary_form not in stopwords + free_stopwords:  # 平仮名、カナ、数字で1文字を除外
                    dictionary_form_line.append(dictionary_form)
        if dictionary_form_line:
            all_tokens_flattened.extend(dictionary_form_line)
    return all_tokens_flattened


# ===== 単語頻度グラフ =====
def plot_word_frequency(all_tokens_flattened: list[str], selected_color: str):
    counter = Counter(all_tokens_flattened)  # カウント
    top30 = counter.most_common(30)          # top30抽出
    df_top30 = pd.DataFrame(top30, columns=["words", "Frequency"])

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x="Frequency",
                y="words",
                data=df_top30,
                color=selected_color.split(" / ")[0]
    )
    ax.set_title("Word Frequency (Top30 Words)", fontsize=18)
    return fig

# ===== カウンタの表示 =====
def counter_df(all_tokens_flattened: list[str]) -> pd.DataFrame:
    counter = Counter(all_tokens_flattened)  # カウント
    top30 = counter.most_common(30)          # top30抽出
    df_top30 = pd.DataFrame(top30, columns=["words", "Frequency"])
    df_top30.index = df_top30.index + 1
    return df_top30

# ===== ワードクラウド生成 =====
def make_wordcloud(all_tokens_flattened: list[str], selected_color: str):
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

    counter = Counter(all_tokens_flattened)  # カウント
    dic_result = dict(counter)  # ワードクラウド取込用に辞書型ヘ変換
    mask_ellipse = make_ellipse_mask(1000, 600)  # 楕円マスク関数の呼び出し

    font_path = "C:/Windows/Fonts/msgothic.ttc"  # Windows用のフォントパス設定
    wordcloud = WordCloud(
        width=1000,
        height=600,
        mask=mask_ellipse,
        font_path=font_path,
        background_color="white",
        colormap=selected_color.split(" / ")[1].split("（")[0],
        max_words=100
    ).fit_words(dic_result)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(wordcloud)
    ax.axis("off")
    return fig