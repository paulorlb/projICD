# utils_textmining.py

from pathlib import Path
import sys
import pandas as pd
import numpy as np
from scipy.sparse import load_npz
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# Find the project root (assuming marker-based or script-relative path)
def find_project_root(marker="README.md"):
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:  # Traverse up until root
        if (current_dir / marker).exists():
            return current_dir
        current_dir = current_dir.parent
    raise FileNotFoundError(f"Marker '{marker}' not found in any parent directory.")

project_root = find_project_root()
sys.path.append(str(project_root)) 


BASE_DIR = project_root
DATA_DIR = BASE_DIR / "data"
DATA_FOR_VIS_DIR = DATA_DIR / "dashboard_data"
MODELS_DIR = BASE_DIR / "models"

MODEL_FILE = MODELS_DIR / "abstract_topic_classifier.joblib"
TFIDF_FILE = DATA_FOR_VIS_DIR / "tfidf_matrix.npz"
DOC_INDEX_FILE = DATA_FOR_VIS_DIR / "doc_index.csv"


def load_corpus():
    df = pd.read_csv(DATA_DIR / "scopus_corpus_with_topics.csv")
    return df


def load_dashboard_tables():
    topic_counts = pd.read_csv(DATA_FOR_VIS_DIR / "topic_counts.csv")
    topics_over_time = pd.read_csv(DATA_FOR_VIS_DIR / "topics_over_time.csv")
    journals_per_topic = pd.read_csv(DATA_FOR_VIS_DIR / "journals_per_topic.csv")
    return topic_counts, topics_over_time, journals_per_topic


def load_model():
    return joblib.load(MODEL_FILE)


def load_interpretability():
    interp_file = DATA_FOR_VIS_DIR / "top_terms_per_topic.csv"
    if interp_file.exists():
        return pd.read_csv(interp_file)
    return None


def load_topic_comparison():
    comp_file = DATA_FOR_VIS_DIR / "topic_classifier_vs_model_sample.csv"
    if comp_file.exists():
        return pd.read_csv(comp_file)
    return None


def load_semantic_search_data():
    if TFIDF_FILE.exists() and DOC_INDEX_FILE.exists():
        X = load_npz(TFIDF_FILE)
        doc_index = pd.read_csv(DOC_INDEX_FILE)
        return X, doc_index
    return None, None


def semantic_search(query_text, model_pipeline, X, doc_index, top_n=10):
    """
    query_text: string
    model_pipeline: the same Pipeline used for classification, to reuse its vectorizer
    X: sparse matrix of tf-idf document representations
    doc_index: dataframe with doc_id and metadata
    """
    vectorizer = model_pipeline.named_steps["tfidf"]
    q_vec = vectorizer.transform([query_text])
    sims = cosine_similarity(q_vec, X)[0]
    top_idx = np.argsort(sims)[::-1][:top_n]
    results = doc_index.iloc[top_idx].copy()
    results["similarity"] = sims[top_idx]
    return results
