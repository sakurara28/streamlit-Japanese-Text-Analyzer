from huggingface_hub.utils.tqdm import progress_bar_states
from transformers import pipeline
import pandas as pd
import torch
import streamlit as st



def zero_shot_classification(input_texts: list[str], categories: list[str]) -> pd.DataFrame:
    progress_bar = st.progress(0)

    # ゼロショット分類モデルを読み込む
    zero_shot_classifier = pipeline(
        "zero-shot-classification",
        model="MoritzLaurer/bge-m3-zeroshot-v2.0-c"
    )

    # モデルに渡すプロンプトテンプレート。ラベル名をこのテンプレートに埋め込む。精度が向上する可能性があるらしい。
    template = "このテキストは {} について書かれています。"

    results = []
    for i, input_text in enumerate(input_texts):
        output = zero_shot_classifier(
            input_text,
            categories,
            hypothesis_template=template,  # テンプレート
            multi_label=True  # True:複数のカテゴリにまたがっている可能性がある場合。スコアの合計は1.0にはならない（Sigmoidでスコア化される）
        )                     # False:1つのカテゴリだけに属するとみなせる場合。スコアの合計は1.0（Softmax関数で正規化）
        #print(output,"\n")   # 辞書で返る（sequenc, labels, scores）
        results.append(output)

        progress_bar.progress((i+1)/len(input_texts))
    
    # スコアが降順に返ってくるので、元のラベル順に並べ替える
    rows = []
    for r in results:
        row = {"text": r["sequence"]}
        for c in categories:
            idx = r["labels"].index(c)  # cが何番目か調べる
            score = r["scores"][idx]    # idx番目のスコアを格納
            row[c] = score              # このラベルの列にスコアを入れる
        rows.append(row)

    df_results = pd.DataFrame(rows)
    # print(df_results.columns)

    # 各行からスコア最大値のラベル名を取得
    top_labels = []
    for idx, df_row in df_results.iterrows():  # rowが1行分のデータ（Series）でとれる。iterrowsは(インデックス,行のデータ)をタプルで返す
        scores = df_row.drop("text").astype(float)  # なぜかスコアが文字列だから、text列を除いてfloatに変換
        # print(scores)
        top = scores.idxmax()  # スコア最大値のラベル名を取得
        # print(f"top:{top}")
        # print(f"type(top):{type(top)}")
        top_labels.append(top)
        # print(top_labels)
    df_results["top_label"] = top_labels
    progress_bar.empty()
    return df_results