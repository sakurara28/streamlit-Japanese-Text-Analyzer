from huggingface_hub.utils.tqdm import progress_bar_states
from transformers import pipeline
import torch
import pandas as pd

# ===== ポジネガ分類 =====
def sentiment_analysis(input_texts: list[str]) -> pd.DataFrame:
    # progress_bar = st.progress(0) # forにするか否か…

    # 感情分析用のパイプラインをロード（事前学習済み日本語モデルを指定）
    classifier = pipeline(
        "sentiment-analysis",
        model="koheiduck/bert-japanese-finetuned-sentiment",  # Hugging Faceが自動でモデルに対応するトークナイザーをロード
        top_k=None  # top_k=Noneにするとすべてのクラスのスコアが返る（確率分布）
    )
    
    # 推論
    results = classifier(
        input_texts,
        truncation=True    # 長すぎる文章は強制的に512トークンに切り詰め。切り詰められた文章は情報が失われる
    )

    # 進捗を更新
    # progress_bar.progress((i+1)/len(input_texts))

    # 出力がリストのリストの辞書なので、dfにするため辞書に変換
    dict_list = []
    for row, t in zip(results, input_texts):
        row_dict = {}           # 空の辞書を用意
        row_dict["text"] = t    # textも格納しとく
        for d in row:           # rowの中には辞書が3つ入っているのでひとつずつ取り出す
            label = d['label']  # labelがキー、scoreが値になる
            score = d['score']
            row_dict[label] = score  # 1つずつ追加
        dict_list.append(row_dict)
        
    df_result = pd.DataFrame(dict_list)
    return df_result