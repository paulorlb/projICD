from pathlib import Path
import sys

import streamlit as st
import pandas as pd
import numpy as np

import joblib
import altair as alt



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

SCOPUS_FILE = DATA_DIR / "scopus_corpus_with_topics.csv"
TOPIC_COUNTS_FILE = DATA_FOR_VIS_DIR / "topic_counts.csv"
TOPICS_OVER_TIME_FILE = DATA_FOR_VIS_DIR / "topics_over_time.csv"
JOURNALS_PER_TOPIC_FILE = DATA_FOR_VIS_DIR / "journals_per_topic.csv"


from scripts.auxDashboard.utils_dashboard import (
    load_corpus,
    load_dashboard_tables,
    load_model,
    load_interpretability,
    load_topic_comparison,
    load_semantic_search_data,
    semantic_search,
    spacy_analyzer,
)



@st.cache_data
def _load_corpus_cached():
    return load_corpus()


@st.cache_data
def _load_tables_cached():
    return load_dashboard_tables()


@st.cache_resource
def _load_model_cached():
    return load_model()


@st.cache_data
def _load_interpretability_cached():
    return load_interpretability()


@st.cache_data
def _load_topic_comparison_cached():
    return load_topic_comparison()


@st.cache_resource
def _load_semantic_data_cached():
    return load_semantic_search_data()

# Main Streamlit app
def main():
    st.set_page_config(
        page_title="Scopus Text Mining Dashboard",
        layout="wide"
    )

    st.title("📚 Scopus Text Mining Dashboard")

    df = _load_corpus_cached()
    topic_counts, topics_over_time, journals_per_topic = _load_tables_cached()
    model = _load_model_cached()
    interp_df = _load_interpretability_cached()
    comp_df = _load_topic_comparison_cached()
    X_sem, doc_index = _load_semantic_data_cached()

    st.sidebar.header("Filters")
    min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
    year_range = st.sidebar.slider(
        "Publication year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    df_filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

    tabs = st.tabs([
        "Overview",
        "Topics over time",
        "Journals by topic",
        "Abstract classifier",
        "Interpretability",
        "Topic model comparison",
        "Semantic search"
    ])

    with tabs[0]:
        show_overview(df_filtered)

    with tabs[1]:
        show_topics_over_time(df_filtered, topics_over_time, year_range)

    with tabs[2]:
        show_journals_by_topic(df_filtered, journals_per_topic)

    with tabs[3]:
        show_classifier(model)

    with tabs[4]:
        show_interpretability(interp_df)

    with tabs[5]:
        show_topic_comparison(comp_df, model)

    with tabs[6]:
        show_semantic_search(model, X_sem, doc_index)


def show_overview(df):
    st.subheader("📊 Corpus overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Documents", f"{len(df):,}")
    with col2:
        st.metric("Journals", df["Journal"].nunique())
    with col3:
        st.metric("Years", df["Year"].nunique())
    with col4:
        st.metric("Topics", df["dominant_topic_nmf"].nunique())
    # topic distribution in filtered df
    tc = (
        df["dominant_topic_nmf"]
        .value_counts()
        .rename_axis("dominant_topic_nmf")
        .reset_index(name="n_docs")
    )

    chart = (
        alt.Chart(tc)
        .mark_bar()
        .encode(
            x=alt.X("dominant_topic_nmf:N", title="Topic"),
            y=alt.Y("n_docs:Q", title="Number of documents"),
            tooltip=["dominant_topic_nmf", "n_docs"]
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show table"):
        st.dataframe(tc, use_container_width=True)


def show_topics_over_time(df, topics_over_time, year_range):
    st.subheader("⏱ Topics over time")

    tot = topics_over_time[
        (topics_over_time["Year"] >= year_range[0]) &
        (topics_over_time["Year"] <= year_range[1])
    ].copy()

    topics_available = sorted(df["dominant_topic_nmf"].unique())
    selected_topics = st.multiselect(
        "Select topics",
        options=topics_available,
        default=topics_available[: min(5, len(topics_available))]
    )

    if not selected_topics:
        st.info("Select at least one topic.")
        return

    tot = tot[tot["dominant_topic_nmf"].isin(selected_topics)]

    chart = (
        alt.Chart(tot)
        .mark_line(point=True)
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("n_docs:Q", title="Number of documents"),
            color="dominant_topic_nmf:N",
            tooltip=["Year", "dominant_topic_nmf", "n_docs"]
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show data"):
        st.dataframe(tot.sort_values(["dominant_topic_nmf", "Year"]), use_container_width=True)


def show_journals_by_topic(df, journals_per_topic):
    st.subheader("📖 Journals by topic")

    topics_available = sorted(df["dominant_topic_nmf"].unique())
    selected_topic = st.selectbox(
        "Select a topic (journals view)",
        options=topics_available,
        key="journals_topic_select",
    )

    jpt = journals_per_topic[journals_per_topic["dominant_topic_nmf"] == selected_topic].copy()
    if jpt.empty:
        st.info("No journal data for this topic.")
        return

    top_n = st.slider("Number of journals to display", 5, 40, 15)
    jpt_top = jpt.nlargest(top_n, "n_docs")

    chart = (
        alt.Chart(jpt_top)
        .mark_bar()
        .encode(
            x=alt.X("n_docs:Q", title="Number of documents"),
            y=alt.Y("Journal:N", sort="-x", title="Journal"),
            tooltip=["Journal", "n_docs"]
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show data"):
        st.dataframe(jpt_top, use_container_width=True)


def show_classifier(model):
    st.subheader("🔮 Abstract topic classifier")

    example_text = (
        "This paper explores the relationship between urban form and energy "
        "consumption using spatial econometric models and remote sensing data."
    )
    text = st.text_area(
        "Abstract",
        value=example_text,
        height=200,
        help="Paste an abstract to classify."
    )

    if st.button("Classify"):
        if not text.strip():
            st.warning("Please enter some text.")
            return

        predicted_topic = model.predict([text])[0]
        st.success(f"Predicted topic: **{predicted_topic}**")


def show_interpretability(interp_df):
    st.subheader("🧩 Model interpretability – influential terms per topic")

    if interp_df is None:
        st.info("Interpretability table not found. Generate 'top_terms_per_topic.csv' from the notebook.")
        return

    topics = sorted(interp_df["dominant_topic_nmf"].unique())
    selected_topic = st.selectbox("Select a topic", topics)

    top_n = st.slider("Number of terms to show", 5, 40, 20)

    df_topic = (
        interp_df[interp_df["dominant_topic_nmf"] == selected_topic]
        .sort_values("weight", ascending=False)
        .head(top_n)
    )

    chart = (
        alt.Chart(df_topic)
        .mark_bar()
        .encode(
            x=alt.X("weight:Q", title="Weight (importance)"),
            y=alt.Y("term:N", sort="-x", title="Term"),
            tooltip=["term", "weight"]
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show table"):
        st.dataframe(df_topic, use_container_width=True)


def show_topic_comparison(comp_df, model):
    st.subheader("⚖️ Topic model vs. classifier comparison")

    if comp_df is None:
        st.info("No comparison file found. Generate 'topic_classifier_vs_model_sample.csv' in the notebook.")
        return

    st.markdown(
        "This table shows topic labels from the original topic model "
        "and the labels predicted by the classifier."
    )

    # Optionally recompute classifier predictions for the sample
    sample = comp_df.copy()
    if "Abstract" in sample.columns:
        sample["classifier_pred"] = model.predict(sample["Abstract"].astype(str))
    else:
        st.warning("No 'Abstract' column in comparison file. Showing static labels only.")

    st.dataframe(sample.head(100), use_container_width=True)

    if "topic_model_label" in sample.columns and "classifier_pred" in sample.columns:
        ctab = pd.crosstab(sample["topic_model_label"], sample["classifier_pred"])
        st.markdown("### Cross-tabulation: topic model vs. classifier")
        st.dataframe(ctab, use_container_width=True)


def show_semantic_search(model, X, doc_index):
    st.subheader("🔍 Semantic search on the corpus")

    if X is None or doc_index is None:
        st.info(
            "Semantic search data not available. "
            "Generate 'tfidf_matrix.npz' and 'doc_index.csv' in the notebook."
        )
        return

    query = st.text_area(
        "Enter a query text (abstract, question, paragraph)",
        height=150,
        value="How do cities adapt energy systems for climate change?"
    )
    top_n = st.slider("Number of results", 3, 30, 10)

    if st.button("Search"):
        if not query.strip():
            st.warning("Please enter a query text.")
            return

        results = semantic_search(query, model, X, doc_index, top_n=top_n)
        st.markdown("### Most similar documents")
        st.dataframe(results, use_container_width=True)


if __name__ == "__main__":
    main()
