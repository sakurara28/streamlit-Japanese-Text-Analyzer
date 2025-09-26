from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup  # HTMLやXMLをきれいに解析してデータを取り出すためのライブラリ
import pandas as pd
from selenium.common.exceptions import TimeoutException     # 要素が待機時間内に見つからなかった場合だすエラー
from selenium.webdriver.support.ui import WebDriverWait     # 「何かの状態になるまで」明示的に待機するためのクラス
from selenium.webdriver.support import expected_conditions  # 「どんな状態を待つか」を指定するための関数群
import requests, json, time, urllib.parse
from sudachipy import tokenizer, dictionary
import neologdn, re, itertools
from collections import Counter
from matplotlib import rcParams
import networkx as nx
import matplotlib.pyplot as plt

# ===== 検索KWをエンコードして一覧結果のURL作成 =====
def make_search_url(keyword: str):
    kw_encode = urllib.parse.quote(keyword)
    search_url = "https://prtimes.jp/main/action.php?run=html&page=searchkey&search_word=" + kw_encode
    return search_url


# ===== 検索結果一覧から会社名と記事URLを取得 =====
def get_search_results(search_url: str):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))  # Chromeを自動操作するためのWebDriverを起動
    driver.get(search_url)  # URLにアクセス

    for i in range(1):  # もっと見るを1回だけ押下（重いから2ページ分だけ/1ページ40記事）
        try:
            wait = WebDriverWait(driver, 10)  # 最長10秒まで「クリックできる状態になる」のを待つ
            more_button = wait.until(
                expected_conditions.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='もっと見る']]"))
            )
            more_button.click()
            time.sleep(3)  # 3秒待つ
        except TimeoutException:  # 10秒たってもボタンが見つからないときにだすエラー
            break  # もう押せないからループ終了

    page_source = driver.page_source  # ソースコードをまるごと取得
    soup = BeautifulSoup(page_source, "html.parser")  # HTMLをPythonで扱いやすい形に変換
    driver.quit()  # ブラウザを閉じる

    search_results = []
    for article in soup.find_all("article", class_="release-card_article__No7uQ"):  # <article>タグの中にある情報を全部取得
        title_tag = article.find("h3")  # タイトル。<h3>タグは一個しかないからクラス名は省略
        company_tag = article.find("a", class_="release-card_companyLink__jRgSJ")  # 会社名
        link_tag = article.find("a", href=True)  # 記事リンク

        if title_tag and company_tag and link_tag:  # 3つともそろったら
            url = "https://prtimes.jp" + link_tag["href"]
            company_name = company_tag.text.strip()
            search_results.append((company_name, url))
    articles_list_df = pd.DataFrame(search_results, columns=["company_name", "url"])
    return articles_list_df

# ===== 検索結果一覧から取得したlinkから記事本文を取得 =====
def get_article_data(articles_list_df: pd.DataFrame):
    headers = {"User-Agent": "Mozilla/5.0"}  # サーバーに「ブラウザですよ」と伝える。（requestsの時に必要）
    url_list = articles_list_df["url"].tolist()

    titles = []
    main_texts = []
    for url in url_list:
        response = requests.get(url, headers=headers)       # 静的だから記事の取得はrequestsでいく
        soup = BeautifulSoup(response.text, "html.parser")  # response.text:記事を文字列として取得して、HTMLをPythonで扱いやすい形に変換
        script_tag = soup.select("script#__NEXT_DATA__")[0]     # <script>タグをselectで取得（リストで返るので[0]つける → 中身JSON…
        json_string = script_tag.string         # <script>タグの中身の文字列だけを取り出す
        parsed_json = json.loads(json_string)   # JSON文字列をPythonの辞書に変換

        title = parsed_json["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["title"]
        main_text = parsed_json["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["text"]  # 中身がhtml…
        
        body_soup = BeautifulSoup(main_text, "html.parser")  # 本文がHTMLなのでテキストだけを取得
        clean_text = body_soup.get_text(strip=False)  # get_text:タグ内の文字列だけを取得。改行を削除したくないのであえてstripしないでいく
        titles.append(title)
        main_texts.append(clean_text)
        time.sleep(3)  # 3秒間待つ

    articles_detail_df = articles_list_df.copy()  # 上書き回避のためにコピー
    articles_detail_df["title"] = titles
    articles_detail_df["main_text"] = main_texts
    articles_detail_df = articles_detail_df[["company_name", "title", "main_text", "url"]]  # 列並び替え
    return articles_detail_df

# ===== 共起ネットワーク用 形態素解析 =====
def morph_for_cooccurrence(articles_detail_df: pd.DataFrame):
    data = articles_detail_df["main_text"].tolist()
    tokenizer_obj = dictionary.Dictionary(dict_type="full").create()
    mode = tokenizer.Tokenizer.SplitMode.C  # C：最も長い分割形式（A～C）

    keep_pos = ["名詞"]  # 抽出したい品詞
    stopwords = ["事", "こと", "年", "月", "時", "分", "日", "以下", "所在地", "円", "ため", "為", "URL", "url", 
                "内容", "詳細", "もの", "物", "概要", "HTTPS", "開始", "対象","代表者", "JP", "jp", "株式会社",
                "今後", "%", "皆", "兼", "他", "階", "もと", "以上", "以下","前", "後", "中"]  # ストップワード

    all_tokens = []
    for i, text in enumerate(data):
        text = neologdn.normalize(text).lower()      # 正規化、小文字化
        tokens = tokenizer_obj.tokenize(text, mode)  # トークンに分解
        dictionary_form_line = []
        for token in tokens:
            pos = token.part_of_speech()  # 品詞の抽出
            if pos[0] in keep_pos:  # 必要な品詞かつ不要単語でなければ抽出
                dictionary_form = token.dictionary_form()  # 辞書に載ってる形（活用のない元の形）
                if not re.fullmatch(r"[ぁ-んァ-ヶー0-9a-z]", dictionary_form) and dictionary_form not in stopwords:  # 平仮名、カナ、数字で1文字を除外
                    dictionary_form_line.append(dictionary_form)
        if dictionary_form_line:
            all_tokens.append(dictionary_form_line)
    return all_tokens

# ===== 単語同士のペアを作成してTOP200を抽出 =====
def make_word_pairs(all_tokens: list):
    combi_list = []
    for sentence in all_tokens:
        unique_sentence = list(set(sentence))  # 気になったとこ。文書内の重複はどのくらい影響する？set()で重複削除できるらしい。
        combi = list(itertools.combinations(unique_sentence, 2))  # itertools.combinations( ,2)でペアが作れるらしい、そしてリストに戻す
        combi_list.append(combi)  # リストのリストのタプル…

    combi_flat_list = list(itertools.chain.from_iterable(combi_list))  # リストのリストを1つのリストに結合する
    counter = Counter(combi_flat_list)  # リストのタプルのタプル…

    top200 = counter.most_common(200)  # 上位200組抽出
    return top200

# ===== 共起ネットワーク描画 =====
def plot_cooccurrence_network(top200: list[tuple[tuple[str, str], int]]):
    G = nx.Graph()  # グラフの初期化。無向グラフ（A-BとB-Aは同じとみなす）

    # ノードとエッジを追加
    for (word1, word2), count in top200:
        G.add_edge(word1, word2, weight=count)  # グラフGにノードword1とword2をつなぐエッジを追加。weight属性に共起回数を入れる

    # 独立したサブネットワークを除外（孤立しちゃうやつ）
    components = list(nx.connected_components(G))  # 無向グラフGを分解してお互いに繋がっているノードの集まりを返す。リストのセット…

    small_components = []
    for c in components:
        if len(c) == 2:  # ノード数が2しかないやつを探す（=孤立）
            small_components.append(c)

    for s_c in small_components:  # そのノードをすべて削除
        G.remove_nodes_from(s_c)  # 既存のグラフからノード数2を直接削除。appendは不要

    # 重み付き次数（strength）でノードサイズを決める
    node_sizes = []
    for node in G.nodes():  # グラフにある全ノードを順番に取り出す
        strength = 0  # このノードの強さ（エッジ重み合計）を入れる変数を初期化
        for u, v, d in G.edges(node, data=True):  # G.edges(node, data=True):そのノードにつながっているエッジ全部を返す。u, v, d:JAL ANA {'weight': 10}
            strength = strength + d['weight']  # dは属性の辞書、d['weight']が共起回数
        size = strength * 0.5  # 見やすいようにスケーリングしてリストに追加（数値変更でノードサイズかわる）
        node_sizes.append(size)
    print(f'node_sizes:{node_sizes}')

    # NetworkX のノード配置（レイアウト）を設定
    pos = nx.spring_layout(G, k=0.5, seed=42)  # ノードとエッジをちょうどいい位置に散らばるように計算してくれる関数。Kの値で密集具合が調整できる

    # 描画サイズ
    fig, ax = plt.subplots(figsize=(10, 8))

    # ノード描画
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='lightblue')

    # エッジ描画（weightに応じて太さ変える）
    nx.draw_networkx_edges(
        G,
        pos,
        width=[G[u][v]['weight'] * 0.008 for u, v in G.edges()],  # width=[G[u][v]['weight'] * 0.002 の数値部分でエッジの太さ調整
        edge_color='black',
        alpha=0.4  # 透明度
    )

    # ラベル描画（ノード名）
    nx.draw_networkx_labels(
        G,
        pos,
        font_family='Meiryo',
        font_size=8
    )

    # # エッジラベル（共起回数）も表示するなら：
    # edge_labels = nx.get_edge_attributes(G, 'weight')
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

    ax.set_title("Co-occurrence network")
    ax.axis('off')  # 軸線・目盛り全部消す
    return fig      # streamlitでエラーになるからplt.show()はしない