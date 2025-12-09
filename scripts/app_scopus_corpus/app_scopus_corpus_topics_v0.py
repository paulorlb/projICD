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
MODELS_DIR = BASE_DIR / "models"

MODEL_FILE = MODELS_DIR / "abstract_topic_classifier.joblib"

SCOPUS_FILE = DATA_DIR / "scopus_corpus_with_topics.csv"
TOPIC_COUNTS_FILE = DATA_DIR / "topic_counts.csv"
TOPICS_OVER_TIME_FILE = DATA_DIR / "topics_over_time.csv"
JOURNALS_PER_TOPIC_FILE = DATA_DIR / "journals_per_topic.csv"

# -----------------------------------------------------
# Helper functions (cached)
@st.cache_data
def load_data():
    df = pd.read_csv(SCOPUS_FILE)
    # Ensure basic types
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df

@st.cache_data
def load_dashboard_tables():
    topic_counts = pd.read_csv(TOPIC_COUNTS_FILE)
    topics_over_time = pd.read_csv(TOPICS_OVER_TIME_FILE)
    journals_per_topic = pd.read_csv(JOURNALS_PER_TOPIC_FILE)
    return topic_counts, topics_over_time, journals_per_topic

@st.cache_resource
def load_model():
    clf = joblib.load(MODEL_FILE)
    return clf


# -----------------------------------------------------
# Layout and navigation
def main():
    st.set_page_config(
        page_title="Scopus Text Mining Dashboard",
        layout="wide"
    )

    st.title("📚 Scopus Text Mining Dashboard")
    st.markdown(
        """
        This dashboard explores a Scopus corpus and allows you to classify new abstracts
        into the topics identified in your text mining project.
        """
    )

    # Load data & model
    df = load_data()
    topic_counts, topics_over_time, journals_per_topic = load_dashboard_tables()
    model = load_model()

    # Sidebar filters
    st.sidebar.header("Filters")
    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    year_range = st.sidebar.slider(
        "Publication year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    # Filter df by year
    df_filtered = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    # Tabs (or pages)
    tab_overview, tab_topics_time, tab_journals, tab_classifier = st.tabs(
        ["Overview", "Topics over time", "Journals by topic", "Abstract classifier"]
    )

    with tab_overview:
        show_overview(df_filtered, topic_counts)

    with tab_topics_time:
        show_topics_over_time(df_filtered, topics_over_time, year_range)

    with tab_journals:
        show_journals_by_topic(df_filtered, journals_per_topic)

    with tab_classifier:
        show_classifier(model)

if __name__ == "__main__":
    main()

# -----------------------------------------------------
# Specific visualization functions for each tab
# -----------------------------------------------------

# --------------
# Overview tab

def show_overview(df, topic_counts):
    st.subheader("📊 Corpus overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Documents", f"{len(df):,}")
    with col2:
        st.metric("Journals", df["journal"].nunique())
    with col3:
        st.metric("Years", df["year"].nunique())
    with col4:
        st.metric("Topics", df["topic_label"].nunique())

    # Topic distribution (bar chart)
    st.markdown("### Topic distribution")

    topic_counts_filtered = (
        df["topic_label"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "topic_label", "topic_label": "n_docs"})
    )

    chart = (
        alt.Chart(topic_counts_filtered)
        .mark_bar()
        .encode(
            x=alt.X("topic_label:N", title="Topic"),
            y=alt.Y("n_docs:Q", title="Number of documents"),
            tooltip=["topic_label", "n_docs"]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)

    # Optional: show table
    with st.expander("Show topic frequency table"):
        st.dataframe(topic_counts_filtered, use_container_width=True)
        
# --------------
# Topic counts by year tab

def show_overview(df, topic_counts):
    st.subheader("📊 Corpus overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Documents", f"{len(df):,}")
    with col2:
        st.metric("Journals", df["journal"].nunique())
    with col3:
        st.metric("Years", df["year"].nunique())
    with col4:
        st.metric("Topics", df["topic_label"].nunique())

    # Topic distribution (bar chart)
    st.markdown("### Topic distribution")

    topic_counts_filtered = (
        df["topic_label"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "topic_label", "topic_label": "n_docs"})
    )

    chart = (
        alt.Chart(topic_counts_filtered)
        .mark_bar()
        .encode(
            x=alt.X("topic_label:N", title="Topic"),
            y=alt.Y("n_docs:Q", title="Number of documents"),
            tooltip=["topic_label", "n_docs"]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)

    # Optional: show table
    with st.expander("Show topic frequency table"):
        st.dataframe(topic_counts_filtered, use_container_width=True)

# --------------
# Journals by topics tab

def show_journals_by_topic(df, journals_per_topic):
    st.subheader("📖 Journals by topic")

    topics_available = sorted(df["topic_label"].unique())
    selected_topic = st.selectbox("Select a topic", options=topics_available)

    jpt = journals_per_topic[journals_per_topic["topic_label"] == selected_topic].copy()
    jpt = jpt.sort_values("n_docs", ascending=False)

    # limit to top N journals
    top_n = st.slider("How many journals to show?", 5, 40, 15)
    jpt_top = jpt.head(top_n)

    chart = (
        alt.Chart(jpt_top)
        .mark_bar()
        .encode(
            x=alt.X("n_docs:Q", title="Number of documents"),
            y=alt.Y("journal:N", sort="-x", title="Journal"),
            tooltip=["journal", "n_docs"]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show journal-topic table"):
        st.dataframe(jpt_top, use_container_width=True)
