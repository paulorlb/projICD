
import spacy

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"]) 
import re
from typing import List

# simple helper: remove weird control chars
_whitespace_re = re.compile(r"\s+")

def spacy_tokenize_abstract(text: str, allowed_pos=("NOUN", "PROPN", "ADJ")) -> List[str]:
    """
    Process an abstract with spaCy and return a list of clean, lemmatized tokens.
    - keeps only alphabetic tokens
    - removes stopwords and very short tokens
    - filters by part-of-speech
    """
    if not isinstance(text, str):
        return []

    # basic normalization
    text = text.strip()
    if not text:
        return []

    doc = nlp(text)

    tokens = []
    for token in doc:
        # 1) Skip stopwords, punctuation, spaces
        if token.is_stop or token.is_punct or token.is_space:
            continue

        # 2) Keep only alphabetic tokens (no numbers, no mixed)
        if not token.is_alpha:
            continue

        # 3) POS filter
        if token.pos_ not in allowed_pos:
            continue

        # 4) Use lemma, lowercased
        lemma = token.lemma_.lower().strip()

        # 5) Remove very short lemmas
        if len(lemma) < 3:
            continue

        tokens.append(lemma)

    return tokens
