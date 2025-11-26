import argparse
import json
import os
import re
from itertools import combinations

import matplotlib.pyplot as plt
import pandas as pd


#Func for loading cleaned book in json
def load_book_json(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for ch_idx, chapter in enumerate(data["chapters"], start = 1):
        for seg_idx, seg_text in enumerate(chapter):
            rows.append({
                "chapter": ch_idx,
                "segment": seg_idx,
                "text": seg_text,
            })

    df = pd.DataFrame(rows)
    return df


#Splitting each segment into sentences

def split_to_sentences(df: pd.DataFrame) -> pd.DataFrame:
    sent_rows = []

    for _, row in df.iterrows():
        sentences = re.split(r"(?<=[.!?])\s+", row["text"].strip())
        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if not sent:
                continue
            sent_rows.append({
                "chapter": row["chapter"],
                "segment": row["segment"],
                "sent_in_segment": i,
                "sentence": sent, 
            })

    return pd.DataFrame(sent_rows)


#Mention counts per sentence
def add_character_columns(df_sent: pd.DataFrame, characters: dict) -> pd.DataFrame:
    def count_mentions(sentence: str, aliases: list) -> int:
        s = sentence.lower()
        return sum(s.count(alias.lower()) for alias in aliases)
    
    df_sent = df_sent.copy()
    for char, aliases in characters.items():
        df_sent[char] = df_sent["sentence"].apply(lambda s: count_mentions(s, aliases))

    return df_sent



#co-occurence table and raw pairs
def build_cooccurence(df_sent: pd.DataFrame, characters: dict):
    df_sent = df_sent.copy()
    df_sent["present_characters"] = df_sent.apply(
        lambda row: [c for c in characters.keys() if row[c] > 0],
        axis = 1
    )

    co_pairs = []

    for chars in df_sent["present_characters"]:
        if len(chars) > 1:
            for pair in combinations(sorted(chars), 2):
                co_pairs.append(pair)

    if not co_pairs:
        co_df = pd.DataFrame(columns=["char1", "char2"])
        co_matrix = pd.DataFrame(columns=["char1", "char2", "weight"])
        return co_matrix, co_df
    
    co_df = pd.DataFrame(co_pairs, columns=["char1", "char2"])
    co_matrix = co_df.groupby(["char1", "char2"]).size().reset_index(name="weight")
    return co_matrix, co_df


#plot heatmap
def cooccurence_heatmap(co_df: pd.DataFrame, characters: dict, title: str, out_path: str):
    if co_df.empty:
        print("No co-occurences found")
        return
    
    adj = co_df.groupby(["char1", "char2"]).size().unstack(fill_value=0)

    for c in characters.keys():
        if c not in adj.index:
            adj.loc[c] = 0

        if c not in adj.columns:
            adj[c] = 0

    adj = adj.sort_index().sort_index(axis = 1)
    adj_sym = adj + adj.T

    plt.figure(figsize=(8, 6))
    plt.imshow(adj_sym, cmap="Blues")

    plt.xticks(
        range(len(adj_sym.columns)),
        adj_sym.columns,
        rotation=45,
        ha="right"
    )
    plt.yticks(range(len(adj_sym.index)), adj_sym.index)

    plt.colorbar(label="Co-occurence freq")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


# Sum the mentions for each character
def character_mentions_barplot(df_sent: pd.DataFrame, characters: dict, title: str, out_path: str):

    mention_counts = (
        df_sent[list(characters.keys())]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.bar(mention_counts.index, mention_counts.values)

    ax.set_title(title)
    ax.set_ylabel("Number of mentions")
    ax.set_xlabel("Characters")

    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()

    fig.savefig(str(out_path), dpi=300, bbox_inches="tight")
    plt.close(fig)
