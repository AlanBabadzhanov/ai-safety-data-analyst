import streamlit as st
import pandas as pd


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Safety Data Analyst",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ AI Safety Data Analyst")

st.caption(
    "Human-in-the-loop analytics and quality control "
    "for AI safety datasets"
)

st.divider()


# ============================================================
# FILE UPLOAD
# ============================================================

st.subheader("📁 Dataset")

uploaded_file = st.file_uploader(
    "Upload a CSV dataset",
    type=["csv"]
)


# ============================================================
# LOAD DATA
# ============================================================

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success(
        f"Successfully loaded {len(df):,} records."
    )

else:

    df = pd.read_csv("safety_dataset.csv")

    st.info(
        "Using the built-in demonstration dataset. "
        "Upload a CSV above to analyze your own data."
    )


# ============================================================
# DATASET QUALITY AUDIT
# ============================================================

st.subheader("🔍 Dataset Quality Audit")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Rows",
        len(df)
    )

with col2:
    st.metric(
        "Columns",
        len(df.columns)
    )

with col3:
    missing_values = int(
        df.isna().sum().sum()
    )

    st.metric(
        "Missing Values",
        missing_values
    )

with col4:
    duplicate_rows = int(
        df.duplicated().sum()
    )

    st.metric(
        "Duplicate Rows",
        duplicate_rows
    )


# ============================================================
# DATA PREVIEW
# ============================================================

with st.expander("View Dataset"):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# CHECK FOR ANALYTICS COLUMNS
# ============================================================

required_columns = [
    "classification",
    "confidence",
    "human_review"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.warning(
        "This dataset does not contain all of the fields "
        "needed for the safety analytics dashboard."
    )

    st.write("Missing fields:")

    for column in missing_columns:
        st.write(f"• `{column}`")

    st.stop()


# ============================================================
# KEY METRICS
# ============================================================

st.divider()

st.subheader("📊 Safety Analytics")

total_items = len(df)

average_confidence = df["confidence"].mean()

review_items = df[
    df["human_review"]
    .astype(str)
    .str.upper()
    .eq("YES")
]

review_count = len(review_items)

review_rate = (
    review_count / total_items * 100
)


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Items Analyzed",
        total_items
    )

with col2:

    st.metric(
        "Avg. Confidence",
        f"{average_confidence:.1f}%"
    )

with col3:

    st.metric(
        "Human Review",
        review_count
    )

with col4:

    st.metric(
        "Review Rate",
        f"{review_rate:.1f}%"
    )


# ============================================================
# CATEGORY ANALYSIS
# ============================================================

st.subheader("📊 Category Analysis")

category_stats = (
    df.groupby("classification")
    .agg(
        Items=("id", "count"),
        Average_Confidence=(
            "confidence",
            "mean"
        ),
        Human_Reviews=(
            "human_review",
            lambda x:
            x.astype(str)
            .str.upper()
            .eq("YES")
            .sum()
        )
    )
    .reset_index()
)

category_stats["Average_Confidence"] = (
    category_stats[
        "Average_Confidence"
    ].round(1)
)

st.dataframe(
    category_stats,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CONFIDENCE CHART
# ============================================================

st.subheader("📈 Confidence by Category")

chart_data = (
    category_stats
    .set_index("classification")
    ["Average_Confidence"]
)

st.bar_chart(chart_data)


# ============================================================
# HUMAN REVIEW QUEUE
# ============================================================

st.subheader("⚠️ Human Review Queue")

review_queue = (
    df[
        df["confidence"] < 70
    ]
    .sort_values("confidence")
)

if len(review_queue) > 0:

    st.warning(
        f"{len(review_queue)} items have confidence "
        "below 70%."
    )

    st.dataframe(
        review_queue,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No low-confidence cases detected."
    )


# ============================================================
# AUTOMATED FINDINGS
# ============================================================

st.subheader("🔎 Automated Findings")

lowest_category = (
    category_stats
    .sort_values(
        "Average_Confidence"
    )
    .iloc[0]
)

highest_review_category = (
    category_stats
    .sort_values(
        "Human_Reviews",
        ascending=False
    )
    .iloc[0]
)

lowest_item = (
    df
    .sort_values("confidence")
    .iloc[0]
)


st.info(
    f"""
### Key Findings

**Lowest-confidence category:**  
{lowest_category["classification"]} 
({lowest_category["Average_Confidence"]:.1f}% average confidence)

**Most human-review cases:**  
{highest_review_category["classification"]} 
({int(highest_review_category["Human_Reviews"])} cases)

**Highest-priority item:**  
ID {lowest_item["id"]} 
({lowest_item["confidence"]}% confidence)

### Recommended Action

Prioritize low-confidence items for human review,
then investigate whether similar items are receiving
inconsistent classifications.
"""
)


# ============================================================
# CONTENT EXPLORER
# ============================================================

st.subheader("🔍 Content Explorer")

selected_id = st.selectbox(
    "Select an item:",
    df["id"].tolist()
)

selected_item = (
    df[
        df["id"] == selected_id
    ]
    .iloc[0]
)

st.write(
    f"**Classification:** "
    f"{selected_item['classification']}"
)

st.write(
    f"**Confidence:** "
    f"{selected_item['confidence']}%"
)

st.write(
    f"**Human Review:** "
    f"{selected_item['human_review']}"
)

if "content" in df.columns:

    st.write("**Content:**")

    st.write(
        selected_item["content"]
    )


# ============================================================
# EXPORT
# ============================================================

st.subheader("📥 Export Analysis")

csv_export = review_queue.to_csv(
    index=False
)

st.download_button(
    label="Download Human Review Queue",
    data=csv_export,
    file_name="human_review_queue.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Safety Data Analyst — Prototype"
)