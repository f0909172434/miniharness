"""詞頻契約的參考解；先嘗試作業再閱讀。"""
def word_counts(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return sorted(counts.items(), key=lambda row: (-row[1], row[0]))
